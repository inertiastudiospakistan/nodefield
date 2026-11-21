"""Nodefield inference worker — runs a real model and serves jobs from the API.

Standalone worker: polls the Nodefield API for pending jobs, runs them
through a local GGUF model with llama-cpp-python, and posts the result
back. Works on CPU (no GPU) and on a GPU worker (e.g. a Colab T4) with
no code changes — GPU offload is decided at runtime from hardware
detection.

Dependencies: llama-cpp-python only (plus the Python standard library).
Install it in a venv — the system Python on Ubuntu refuses pip installs
(PEP 668):

    python3 -m venv .venv
    .venv/bin/pip install llama-cpp-python

Usage:
    .venv/bin/python agent/worker.py [--api URL] [--model qwen3-4b]
    .venv/bin/python agent/worker.py --once        # one job, then exit
    .venv/bin/python agent/worker.py --help

Model download: on first run the worker downloads the GGUF file from
Hugging Face (Qwen3-4B Q4_K_M by default, ~2.6 GB) into agent/models/
using plain urllib — no huggingface_hub dependency. Override with
--repo/--file or the NODEFIELD_HF_REPO / NODEFIELD_HF_FILE env vars.

Honesty rules (hard):
- The worker only claims jobs for models it has actually loaded. If the
  model fails to load, the worker exits instead of claiming anything.
- A reply is labelled real only when this model generated it. Token
  counts come from the model's own tokenizer; tok/s and TTFT are
  measured wall-clock, never estimated.
- The worker never executes arbitrary code from the network: it accepts
  only a prompt (chat messages) and returns generated text.

Clean stop: Ctrl+C / SIGTERM stops polling after the current job; the
server re-queues any job left running past its timeout.
"""

import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_MODEL_DIR = os.path.join(BASE_DIR, "models")

DEFAULT_API_URL = "http://localhost:8787"
DEFAULT_MODEL = "qwen3-4b"
DEFAULT_REPO = "Qwen/Qwen3-4B-GGUF"
DEFAULT_FILE = "Qwen3-4B-Q4_K_M.gguf"
HEARTBEAT_SECONDS = 30
CLAIM_POLL_SECONDS = 2
MAX_TOKENS_DEFAULT = 256
MAX_TOKENS_CAP = 512

# Stop tokens for the ChatML prompt format below. Qwen3 emits
# <|im_end|> at the end of its reply; <|endoftext|> is a safety net.
STOP_TOKENS = ["<|im_end|>", "<|endoftext|>"]


def log(msg):
    print("[%s] %s" % (time.strftime("%H:%M:%S"), msg), flush=True)


# --- HTTP helpers (stdlib only) -------------------------------------------

def http_json(method, url, payload=None, timeout=10):
    """POST/GET JSON; returns (status, parsed dict) or raises URLError."""
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.status, json.loads(resp.read().decode("utf-8"))


# --- hardware detection ----------------------------------------------------

def detect_gpu():
    """Return (device, gpu_model, vram_gb). device is 'gpu' or 'cpu'.
    Never invents a GPU: no nvidia-smi match means CPU."""
    if shutil.which("nvidia-smi"):
        try:
            out = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,memory.total",
                 "--format=csv,noheader"],
                capture_output=True, text=True, timeout=10)
            if out.returncode == 0 and out.stdout.strip():
                name, mem = out.stdout.strip().split(",")[0:2]
                vram = None
                try:
                    vram = float(mem.strip().split()[0]) / 1024
                except (ValueError, IndexError):
                    pass
                return "gpu", name.strip(), round(vram, 1) if vram else None
        except (subprocess.SubprocessError, OSError):
            pass
    return "cpu", None, None


# --- model download ---------------------------------------------------------

def download_model(repo, filename, model_dir):
    """Download a GGUF file from Hugging Face with plain urllib.
    Writes to a .part file and renames on success, so a partial
    download is never mistaken for a complete model."""
    os.makedirs(model_dir, exist_ok=True)
    dest = os.path.join(model_dir, filename)
    if os.path.exists(dest) and os.path.getsize(dest) > 0:
        log("Model file already present: %s (%.1f MB)"
            % (dest, os.path.getsize(dest) / 1024 / 1024))
        return dest
    url = "https://huggingface.co/%s/resolve/main/%s" % (repo, filename)
    tmp = dest + ".part"
    log("Downloading %s (this is ~2.6 GB for Qwen3-4B Q4_K_M) ..." % url)
    req = urllib.request.Request(url, headers={"User-Agent": "nodefield-worker/0.1"})
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            total = int(resp.headers.get("Content-Length") or 0)
            downloaded = 0
            with open(tmp, "wb") as f:
                while True:
                    chunk = resp.read(1024 * 1024)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total and downloaded % (256 * 1024 * 1024) < 1024 * 1024:
                        log("  ... %.0f%% (%.0f MB of %.0f MB)"
                            % (100.0 * downloaded / total,
                               downloaded / 1024 / 1024, total / 1024 / 1024))
        os.rename(tmp, dest)
    except Exception as e:
        try:
            os.remove(tmp)
        except OSError:
            pass
        raise RuntimeError("model download failed: %s" % e)
    log("Downloaded in %.0fs -> %s (%.1f MB)"
        % (time.time() - t0, dest, os.path.getsize(dest) / 1024 / 1024))
    return dest


# --- prompt formatting ------------------------------------------------------

def format_chatml(messages, model_id=""):
    """Render chat messages into the ChatML prompt Qwen3 was trained on.
    Built by hand (not the model's chat template) so the output format
    is deterministic and no <think> reasoning block is requested.

    Qwen3 note: the model thinks by default. The official way to turn
    thinking off (what the chat template does with enable_thinking=False)
    is to open the assistant turn with an *empty* think block — the model
    then continues straight into the answer. Only Qwen3 models get it;
    other model families must not see this token."""
    parts = []
    for m in messages:
        if not isinstance(m, dict):
            continue
        role = m.get("role") or "user"
        if role not in ("system", "user", "assistant"):
            role = "user"
        content = str(m.get("content") or "")
        parts.append("<|im_start|>%s\n%s<|im_end|>\n" % (role, content))
    parts.append("<|im_start|>assistant\n")
    if model_id.startswith("qwen3"):
        parts.append("<think>\n\n</think>\n\n")
    return "".join(parts)


# --- worker -----------------------------------------------------------------

class Worker:
    def __init__(self, args):
        self.api_url = args.api.rstrip("/")
        self.model_id = args.model
        self.worker_id = args.worker_id
        self.n_ctx = args.n_ctx
        self.max_tokens_default = args.max_tokens
        self.model_dir = args.model_dir
        self.repo = args.repo
        self.file = args.file
        self.once = args.once
        self.no_download = args.no_download
        self.device, self.gpu_model, self.vram_gb = detect_gpu()
        if args.n_gpu_layers is not None:
            self.n_gpu_layers = args.n_gpu_layers
        else:
            # GPU present -> offload all layers; CPU-only -> 0 layers.
            self.n_gpu_layers = -1 if self.device == "gpu" else 0
        self.llm = None
        self.n_threads = args.n_threads
        self.stop = False
        self.jobs_done = 0
        self.jobs_failed = 0
        self.started_at = time.time()

    # -- model --
    def load_model(self):
        try:
            from llama_cpp import Llama
        except ImportError:
            log("ERROR: llama-cpp-python is not installed.")
            log("Install it in a venv: .venv/bin/pip install llama-cpp-python")
            return False
        model_path = os.path.join(self.model_dir, self.file)
        if not os.path.exists(model_path):
            if self.no_download:
                log("ERROR: model file not found and --no-download given: %s"
                    % model_path)
                return False
            try:
                model_path = download_model(self.repo, self.file, self.model_dir)
            except RuntimeError as e:
                log("ERROR: %s" % e)
                return False
        log("Loading model %s (device=%s, n_gpu_layers=%d, n_ctx=%d) ..."
            % (model_path, self.device, self.n_gpu_layers, self.n_ctx))
        t0 = time.time()
        try:
            self.llm = Llama(model_path=model_path,
                             n_gpu_layers=self.n_gpu_layers,
                             n_ctx=self.n_ctx,
                             n_threads=self.n_threads,
                             verbose=False)
        except Exception as e:
            log("ERROR: failed to load model: %s" % e)
            return False
        log("Model loaded in %.1fs: %s (device=%s)"
            % (time.time() - t0, self.model_id, self.device))
        return True

    # -- coordinator API --
    def heartbeat(self):
        """Register / refresh this worker. Only ever lists the model that
        is actually loaded — that list is what the API routes on."""
        payload = {
            "id": self.worker_id,
            "gpu_model": self.gpu_model or ("CPU (no GPU)" if self.device == "cpu" else None),
            "vram_gb": self.vram_gb,
            "device": self.device,
            "models": [self.model_id] if self.llm is not None else [],
            "region": "unknown",
            "latency_ms": None,
            "uptime_hours": round((time.time() - self.started_at) / 3600, 2),
        }
        try:
            status, _ = http_json("POST", self.api_url + "/api/workers",
                                  payload, timeout=10)
            return status == 200
        except Exception as e:
            log("heartbeat failed: %s" % e)
            return False

    def claim_job(self):
        """Ask the API for one pending job this worker can serve.
        Returns the job dict, or None when there is nothing to do."""
        try:
            status, body = http_json(
                "POST", self.api_url + "/api/workers/claim",
                {"worker_id": self.worker_id, "models": [self.model_id]},
                timeout=10)
        except Exception as e:
            log("claim failed (API unreachable?): %s" % e)
            return None
        if status != 200:
            log("claim rejected (%s): %s" % (status, body))
            return None
        return body.get("job")

    def post_result(self, job_id, result):
        try:
            status, _ = http_json(
                "POST", self.api_url + "/api/jobs/%s/result" % job_id,
                result, timeout=15)
            return status == 200
        except Exception as e:
            log("result post failed for job %s: %s" % (job_id, e))
            return False

    # -- inference --
    def run_job(self, job):
        """Run one claimed job through the loaded model. Returns True on
        success. Never returns fake text: on any failure the job is
        reported failed with the error, not completed with invented
        output."""
        job_id = job["id"]
        model = job.get("model")
        if model != self.model_id or self.llm is None:
            # Refuse work this worker cannot serve (defensive: the API
            # should never assign it, but never generate blindly).
            log("Refusing job %s: model %s not loaded here" % (job_id, model))
            self.post_result(job_id, {
                "worker_id": self.worker_id,
                "error": "model %s not loaded on this worker" % model})
            self.jobs_failed += 1
            return False
        messages = job.get("messages")
        if messages:
            prompt = format_chatml(messages, self.model_id)
        else:
            prompt = format_chatml(
                [{"role": "user", "content": job.get("prompt") or ""}],
                self.model_id)
        max_tokens = job.get("max_tokens") or self.max_tokens_default
        max_tokens = max(1, min(int(max_tokens), MAX_TOKENS_CAP))
        log("Job %s: model=%s max_tokens=%d" % (job_id, model, max_tokens))
        t_start = time.time()
        first_token_at = None
        text = ""
        try:
            stream = self.llm.create_completion(
                prompt, max_tokens=max_tokens, temperature=0.0,
                stop=STOP_TOKENS, stream=True)
            for chunk in stream:
                if first_token_at is None:
                    first_token_at = time.time()
                text += chunk["choices"][0].get("text") or ""
            total_s = time.time() - t_start
        except Exception as e:
            log("Job %s failed during inference: %s" % (job_id, e))
            self.post_result(job_id, {
                "worker_id": self.worker_id,
                "error": "inference failed: %s" % e})
            self.jobs_failed += 1
            return False
        ttft_s = (first_token_at - t_start) if first_token_at else None
        decode_s = total_s - ttft_s if ttft_s else total_s
        prompt_tokens = len(self.llm.tokenize(prompt.encode("utf-8")))
        completion_tokens = len(self.llm.tokenize(text.encode("utf-8")))
        tok_per_s = (completion_tokens / decode_s) if decode_s > 0 else None
        log("Job %s done: %d output tokens in %.1fs (TTFT %.3fs, %.2f tok/s)"
            % (job_id, completion_tokens, total_s,
               ttft_s if ttft_s is not None else -1,
               tok_per_s if tok_per_s is not None else -1))
        ok = self.post_result(job_id, {
            "worker_id": self.worker_id,
            "text": text,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "tokens_per_second": round(tok_per_s, 2) if tok_per_s else None,
            "ttft_ms": round(ttft_s * 1000, 1) if ttft_s is not None else None,
            "total_ms": round(total_s * 1000, 1),
        })
        if ok:
            self.jobs_done += 1
        else:
            self.jobs_failed += 1
        return ok

    # -- main loop --
    def _heartbeat_loop(self):
        while not self.stop:
            self.heartbeat()
            for _ in range(HEARTBEAT_SECONDS):
                if self.stop:
                    return
                time.sleep(1)

    def run(self):
        if not self.load_model():
            return 1
        log("Worker %s ready: model=%s device=%s api=%s"
            % (self.worker_id, self.model_id, self.device, self.api_url))
        if not self.heartbeat():
            log("WARNING: first heartbeat failed — is the API running at %s?"
                % self.api_url)
        hb = threading.Thread(target=self._heartbeat_loop, daemon=True)
        hb.start()
        try:
            while not self.stop:
                job = self.claim_job()
                if job is None:
                    time.sleep(CLAIM_POLL_SECONDS)
                    continue
                self.run_job(job)
                if self.once:
                    break
        except KeyboardInterrupt:
            log("Interrupted.")
        self.stop = True
        log("Worker stopped. jobs done: %d, failed: %d"
            % (self.jobs_done, self.jobs_failed))
        return 0


def main():
    parser = argparse.ArgumentParser(
        description="Nodefield inference worker (llama.cpp, CPU or GPU)")
    parser.add_argument("--api", default=os.environ.get(
        "NODEFIELD_API_URL", DEFAULT_API_URL),
        help="API base URL (default: %(default)s)")
    parser.add_argument("--model", default=os.environ.get(
        "NODEFIELD_MODEL", DEFAULT_MODEL),
        help="model id served, e.g. qwen3-4b (default: %(default)s)")
    parser.add_argument("--worker-id", default=os.environ.get(
        "NODEFIELD_WORKER_ID", "worker-" + os.uname().nodename.lower()),
        help="worker id announced to the API")
    parser.add_argument("--model-dir", default=os.environ.get(
        "NODEFIELD_MODEL_DIR", DEFAULT_MODEL_DIR),
        help="directory holding the GGUF file (default: %(default)s)")
    parser.add_argument("--repo", default=os.environ.get(
        "NODEFIELD_HF_REPO", DEFAULT_REPO),
        help="Hugging Face repo for the model (default: %(default)s)")
    parser.add_argument("--file", default=os.environ.get(
        "NODEFIELD_HF_FILE", DEFAULT_FILE),
        help="GGUF filename (default: %(default)s)")
    parser.add_argument("--n-gpu-layers", type=int, default=None,
                        help="layers offloaded to GPU (-1 = all, 0 = CPU only; "
                             "default: -1 when a GPU is detected, else 0)")
    parser.add_argument("--n-ctx", type=int, default=1024,
                        help="context window in tokens (default: %(default)s; "
                             "smaller = less RAM on CPU)")
    parser.add_argument("--n-threads", type=int, default=os.cpu_count() or 4,
                        help="CPU threads for inference (default: CPU count; "
                             "lower it if the machine has a small CPU quota)")
    parser.add_argument("--max-tokens", type=int, default=MAX_TOKENS_DEFAULT,
                        help="default max output tokens per job (default: %(default)s)")
    parser.add_argument("--once", action="store_true",
                        help="process one claimed job, then exit")
    parser.add_argument("--no-download", action="store_true",
                        help="fail instead of downloading a missing model file")
    args = parser.parse_args()

    worker = Worker(args)

    def _stop(signum, frame):
        worker.stop = True

    signal.signal(signal.SIGINT, _stop)
    signal.signal(signal.SIGTERM, _stop)
    try:
        return worker.run()
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
