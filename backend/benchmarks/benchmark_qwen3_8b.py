# Nodefield benchmark 1 — Qwen3-8B (Q4_K_M) on a free Kaggle GPU.
# Records ONLY measured values. If any step fails, it prints the failure
# and stops — no invented numbers, ever.
# Run in a Kaggle notebook with: GPU accelerator ON, Internet ON.
import json, subprocess, sys, time

def sh(cmd):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return (r.stdout + r.stderr).strip()

def gpu_info():
    out = sh("nvidia-smi --query-gpu=name,memory.total,memory.used --format=csv,noheader")
    return out or "NO GPU DETECTED"

print("== environment ==", flush=True)
print("GPU:", gpu_info(), flush=True)
print("Python:", sys.version.split()[0], flush=True)

print("== install llama-cpp-python (CUDA wheel) ==", flush=True)
r = subprocess.run([sys.executable, "-m", "pip", "install", "-q",
    "llama-cpp-python", "huggingface_hub",
    "--extra-index-url", "https://abetlen.github.io/llama-cpp-python/whl/cu124"],
    capture_output=True, text=True)
print(r.stdout[-2000:], flush=True)
print(r.stderr[-2000:], flush=True)
if r.returncode != 0:
    print("BENCHMARK FAILED: llama-cpp-python install failed", flush=True)
    raise SystemExit(1)

print("== download Qwen3-8B Q4_K_M (~5 GB) ==", flush=True)
from huggingface_hub import hf_hub_download
t0 = time.time()
path = hf_hub_download(repo_id="Qwen/Qwen3-8B-GGUF",
                       filename="Qwen3-8B-Q4_K_M.gguf")
print("downloaded in %.1fs -> %s" % (time.time() - t0, path), flush=True)

print("== load model on GPU ==", flush=True)
from llama_cpp import Llama
t0 = time.time()
llm = Llama(model_path=path, n_gpu_layers=-1, n_ctx=2048, verbose=False)
print("loaded in %.1fs" % (time.time() - t0), flush=True)
print("VRAM after load:", gpu_info(), flush=True)

PROMPTS = [
    "Explain photosynthesis in two sentences.",
    "Write a Python function that returns the nth Fibonacci number.",
    "What is the capital of France and one fact about it?",
    "Summarise the plot of Hamlet in three sentences.",
    "Give three tips for saving money on groceries.",
]

print("== run 5 fixed prompts, 128 max tokens, temp 0 ==", flush=True)
results = []
for i, prompt in enumerate(PROMPTS):
    t_start = time.time()
    first_token_at = None
    text = ""
    for chunk in llm.create_completion(prompt, max_tokens=128, temperature=0.0, stream=True):
        if first_token_at is None:
            first_token_at = time.time()
        text += chunk["choices"][0]["text"]
    total_s = time.time() - t_start
    ttft_s = (first_token_at - t_start) if first_token_at else None
    # Count generated tokens by re-tokenising the output.
    n_tokens = len(llm.tokenize(text.encode("utf-8")))
    results.append({
        "prompt": prompt, "output": text.strip(),
        "ttft_s": round(ttft_s, 3) if ttft_s else None,
        "total_s": round(total_s, 3),
        "completion_tokens": n_tokens,
        "tok_per_s": round(n_tokens / total_s, 2) if total_s > 0 else None,
    })
    print("prompt %d: ttft=%.3fs total=%.3fs tokens=%d tok/s=%.2f" % (
        i + 1, ttft_s or -1, total_s, n_tokens, n_tokens / total_s), flush=True)

summary = {
    "project": "nodefield", "benchmark": "qwen3-8b-q4_k_m",
    "gpu": gpu_info(), "vram_after_load": gpu_info(),
    "model": "Qwen/Qwen3-8B-GGUF Qwen3-8B-Q4_K_M.gguf",
    "runtime": "llama-cpp-python (llama.cpp, CUDA)",
    "date": time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()),
    "results": results,
    "mean_tok_per_s": round(sum(r["tok_per_s"] for r in results) / len(results), 2),
    "mean_ttft_s": round(sum(r["ttft_s"] for r in results if r["ttft_s"]) / len(results), 3),
}
with open("benchmark_qwen3_8b.json", "w") as f:
    json.dump(summary, f, indent=2)
print("== SUMMARY (copy into BENCHMARKS.md) ==", flush=True)
print(json.dumps(summary, indent=2), flush=True)
print("BENCHMARK COMPLETE — results saved to benchmark_qwen3_8b.json", flush=True)
