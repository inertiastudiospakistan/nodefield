"""Nodefield API prototype — Python standard library only, zero dependencies.

Run:  cd backend/api && python3 server.py [--port 8787]

Honest limits: this is a PRE-LAUNCH DEMO. No live GPU worker is
connected and no model is actually loaded. POST /v1/chat/completions
returns a clearly-labelled demo response; it never pretends a model ran.
Token counts are word-count approximations, stated as such.
"""

import argparse
import hashlib
import json
import os
import secrets
import sqlite3
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

# Scheduler lives in ../scheduler — import it for job assignment.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "scheduler"))
try:
    import scheduler as sched
except ImportError:  # pragma: no cover - scheduler is shipped alongside
    sched = None

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "nodefield.db")
VERSION = "0.1.0"

MODELS = [
    {"id": "qwen3-4b", "params": "4B", "license": "Apache 2.0",
     "vram_gb_q4": 4, "context": 32768, "status": "planned"},
    {"id": "qwen3-8b", "params": "8B", "license": "Apache 2.0",
     "vram_gb_q4": 8, "context": 32768, "status": "planned"},
    {"id": "qwen3-14b", "params": "14B", "license": "Apache 2.0",
     "vram_gb_q4": 14, "context": 32768, "status": "planned"},
    {"id": "llama-3.1-8b", "params": "8B", "license": "Llama 3.1 Community",
     "vram_gb_q4": 8, "context": 131072, "status": "planned"},
    {"id": "mistral-7b", "params": "7B", "license": "Apache 2.0",
     "vram_gb_q4": 7, "context": 32768, "status": "planned"},
]
MODEL_IDS = {m["id"] for m in MODELS}

# Rate limit: 60 requests/minute per key (or per IP without a key).
RATE_LIMIT = 60
RATE_WINDOW_SECONDS = 60
_rate_lock = threading.Lock()
_rate_hits = {}  # key -> [timestamps]


# --- Database ------------------------------------------------------------

def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS waitlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kind TEXT NOT NULL,
            name TEXT, email TEXT NOT NULL, country TEXT,
            gpu_manufacturer TEXT, gpu_model TEXT, gpu_vram_gb REAL,
            system_ram_gb REAL, os TEXT, internet TEXT,
            available_hours TEXT, beta_interest INTEGER,
            application TEXT, monthly_tokens INTEGER,
            preferred_models TEXT, desired_features TEXT,
            created_at INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL, label TEXT,
            key_hash TEXT NOT NULL UNIQUE, prefix TEXT NOT NULL,
            created_at INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS workers (
            id TEXT PRIMARY KEY, gpu_model TEXT, vram_gb REAL,
            models TEXT, region TEXT, latency_ms REAL,
            reliability REAL, cost_per_mtok REAL, uptime_hours REAL,
            online INTEGER, last_heartbeat INTEGER
        );
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model TEXT NOT NULL, prompt TEXT NOT NULL,
            priority TEXT, state TEXT NOT NULL,
            worker_id TEXT, retries INTEGER DEFAULT 0,
            created_at INTEGER NOT NULL, updated_at INTEGER NOT NULL
        );
    """)
    conn.commit()
    return conn


def count(table):
    conn = get_db()
    try:
        return conn.execute("SELECT COUNT(*) FROM %s" % table).fetchone()[0]
    finally:
        conn.close()


def workers_online():
    conn = get_db()
    try:
        return conn.execute(
            "SELECT COUNT(*) FROM workers WHERE online = 1").fetchone()[0]
    finally:
        conn.close()


# --- Helpers -------------------------------------------------------------

def approx_tokens(text):
    """Approximate token count by word count. Stated as approximate
    in every response that uses it — it is NOT a tokenizer."""
    if not text:
        return 0
    return len(str(text).split())


def check_rate_limit(bucket):
    """True if the request is allowed, False if the 60/min limit is hit."""
    now = time.time()
    with _rate_lock:
        hits = [t for t in _rate_hits.get(bucket, [])
                if now - t < RATE_WINDOW_SECONDS]
        if len(hits) >= RATE_LIMIT:
            _rate_hits[bucket] = hits
            return False
        hits.append(now)
        _rate_hits[bucket] = hits
        return True


def verify_bearer(auth_header):
    """Return (ok, error). No header -> demo allowed (ok, demo=True).
    Header present -> SHA-256 must match a stored key hash."""
    if not auth_header:
        return True, None, True  # allowed, no error, demo (unauthenticated)
    parts = auth_header.split(None, 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return False, "invalid Authorization header", False
    digest = hashlib.sha256(parts[1].encode("utf-8")).hexdigest()
    conn = get_db()
    try:
        row = conn.execute("SELECT id FROM api_keys WHERE key_hash = ?",
                           (digest,)).fetchone()
    finally:
        conn.close()
    if row is None:
        return False, "invalid API key", False
    return True, None, False


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    # -- plumbing ---------------------------------------------------------
    def log_message(self, fmt, *args):
        sys.stdout.write("%s - %s\n" % (self.address_string(), fmt % args))
        sys.stdout.flush()

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers",
                         "Content-Type, Authorization")

    def _send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, status, message, err_type="error"):
        self._send_json(status, {"error": {"message": message, "type": err_type}})

    def _read_json(self):
        length = int(self.headers.get("Content-Length") or 0)
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        try:
            data = json.loads(raw.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return None
        return data if isinstance(data, dict) else None

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.send_header("Content-Length", "0")
        self.end_headers()

    # -- routing ----------------------------------------------------------
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        query = parse_qs(parsed.query)
        if path == "/api/health":
            self._send_json(200, {
                "status": "ok", "service": "nodefield-api", "mode": "demo",
                "gpu_workers_online": workers_online(), "version": VERSION})
        elif path == "/api/stats":
            conn = get_db()
            try:
                providers = conn.execute(
                    "SELECT COUNT(*) FROM waitlist WHERE kind='provider'"
                ).fetchone()[0]
                developers = conn.execute(
                    "SELECT COUNT(*) FROM waitlist WHERE kind='developer'"
                ).fetchone()[0]
            finally:
                conn.close()
            self._send_json(200, {
                "providers": providers,
                "developers": developers,
                "keys": count("api_keys"),
                "jobs": count("jobs"),
                "demo": True, "live_workers": workers_online(),
                "note": "Pre-launch demo. No live GPU workers connected."})
        elif path == "/api/models":
            self._send_json(200, {"models": MODELS})
        elif path == "/api/keys":
            email = (query.get("email") or [None])[0]
            if not email:
                self._send_error(400, "email query parameter is required")
                return
            conn = get_db()
            try:
                rows = conn.execute(
                    "SELECT prefix, label, created_at FROM api_keys "
                    "WHERE email = ? ORDER BY created_at DESC", (email,)).fetchall()
            finally:
                conn.close()
            self._send_json(200, {"keys": [dict(r) for r in rows]})
        elif path == "/api/jobs":
            conn = get_db()
            try:
                rows = conn.execute(
                    "SELECT * FROM jobs ORDER BY created_at DESC").fetchall()
            finally:
                conn.close()
            self._send_json(200, {"jobs": [dict(r) for r in rows]})
        elif path == "/api/workers":
            conn = get_db()
            try:
                rows = conn.execute("SELECT * FROM workers").fetchall()
            finally:
                conn.close()
            self._send_json(200, {"workers": [dict(r) for r in rows]})
        else:
            self._send_error(404, "not found: %s" % path)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/") or "/"
        body = self._read_json()
        if body is None:
            self._send_error(400, "request body must be a JSON object")
            return
        if path == "/api/waitlist":
            self._handle_waitlist(body)
        elif path == "/api/keys":
            self._handle_create_key(body)
        elif path == "/api/jobs":
            self._handle_create_job(body)
        elif path == "/api/workers":
            self._handle_worker_heartbeat(body)
        elif path == "/v1/chat/completions":
            self._handle_chat(body)
        else:
            self._send_error(404, "not found: %s" % path)

    # -- handlers ---------------------------------------------------------
    def _handle_waitlist(self, body):
        kind = body.get("kind")
        email = (body.get("email") or "").strip()
        if kind not in ("provider", "developer"):
            self._send_error(400, "kind must be 'provider' or 'developer'")
            return
        if not email or "@" not in email:
            self._send_error(400, "a valid email is required")
            return
        now = int(time.time())
        conn = get_db()
        try:
            cur = conn.execute(
                """INSERT INTO waitlist
                   (kind, name, email, country, gpu_manufacturer, gpu_model,
                    gpu_vram_gb, system_ram_gb, os, internet, available_hours,
                    beta_interest, application, monthly_tokens,
                    preferred_models, desired_features, created_at)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (kind, body.get("name"), email, body.get("country"),
                 body.get("gpu_manufacturer"), body.get("gpu_model"),
                 body.get("gpu_vram_gb"), body.get("system_ram_gb"),
                 body.get("os"), body.get("internet"),
                 body.get("available_hours"),
                 1 if body.get("beta_interest") else 0,
                 body.get("application"), body.get("monthly_tokens"),
                 json.dumps(body.get("preferred_models"))
                 if isinstance(body.get("preferred_models"), list) else body.get("preferred_models"),
                 json.dumps(body.get("desired_features"))
                 if isinstance(body.get("desired_features"), list) else body.get("desired_features"),
                 now))
            conn.commit()
            row_id = cur.lastrowid
        finally:
            conn.close()
        self._send_json(201, {"ok": True, "id": row_id, "kind": kind})

    def _handle_create_key(self, body):
        email = (body.get("email") or "").strip()
        if not email or "@" not in email:
            self._send_error(400, "a valid email is required")
            return
        label = body.get("label") or "default"
        full_key = "nf_live_" + secrets.token_hex(16)  # 32 hex chars
        digest = hashlib.sha256(full_key.encode("utf-8")).hexdigest()
        prefix = full_key[:16]  # "nf_live_" + first 8 hex chars
        now = int(time.time())
        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO api_keys (email, label, key_hash, prefix, created_at) "
                "VALUES (?,?,?,?,?)", (email, label, digest, prefix, now))
            conn.commit()
        finally:
            conn.close()
        # The full key is returned ONLY here, never stored in cleartext.
        self._send_json(201, {
            "key": full_key, "prefix": prefix,
            "warning": "Copy now — the full key is never shown again."})

    def _handle_create_job(self, body):
        model = body.get("model")
        prompt = body.get("prompt")
        if not model or not prompt:
            self._send_error(400, "model and prompt are required")
            return
        if model not in MODEL_IDS:
            self._send_error(404, "unknown model: %s" % model)
            return
        priority = body.get("priority") or "standard"
        now = int(time.time())
        conn = get_db()
        try:
            cur = conn.execute(
                "INSERT INTO jobs (model, prompt, priority, state, retries, "
                "created_at, updated_at) VALUES (?,?,?,?,0,?,?)",
                (model, prompt, priority, "pending", now, now))
            job_id = cur.lastrowid
            conn.commit()
        finally:
            conn.close()
        job = {"id": job_id, "model": model, "prompt": prompt,
               "priority": priority, "state": "pending", "worker_id": None,
               "retries": 0}
        # Delegate assignment to the scheduler module (no live workers yet,
        # so this will honestly report that no worker is available).
        assignment = None
        if sched is not None:
            workers = []
            conn = get_db()
            try:
                for r in conn.execute(
                        "SELECT * FROM workers WHERE online = 1").fetchall():
                    workers.append(sched.Worker(
                        id=r["id"], gpu_model=r["gpu_model"] or "",
                        vram_gb=r["vram_gb"] or 0,
                        models=json.loads(r["models"] or "[]"),
                        region=r["region"] or "unknown",
                        latency_ms=r["latency_ms"] or 100,
                        reliability=r["reliability"] or 0.9,
                        cost_per_mtok=r["cost_per_mtok"] or 0.30,
                        uptime_hours=r["uptime_hours"] or 0, online=True))
            finally:
                conn.close()
            sched_job = sched.Job(id=str(job_id), model=model, prompt=prompt,
                                  priority=priority)
            worker, _score, info = sched.assign_job(sched_job, workers)
            if worker is not None:
                job["state"] = "assigned"
                job["worker_id"] = worker.id
                conn = get_db()
                try:
                    conn.execute("UPDATE jobs SET state='assigned', worker_id=?, "
                                 "updated_at=? WHERE id=?",
                                 (worker.id, int(time.time()), job_id))
                    conn.commit()
                finally:
                    conn.close()
                assignment = {"worker_id": worker.id}
            else:
                assignment = {"reason": info.get("reason", "no suitable worker")}
        self._send_json(201, {"job": job, "assignment": assignment})

    def _handle_worker_heartbeat(self, body):
        worker_id = body.get("id") or body.get("worker_id")
        if not worker_id:
            self._send_error(400, "worker id is required")
            return
        now = int(time.time())
        conn = get_db()
        try:
            conn.execute(
                """INSERT INTO workers
                   (id, gpu_model, vram_gb, models, region, latency_ms,
                    reliability, cost_per_mtok, uptime_hours, online, last_heartbeat)
                   VALUES (?,?,?,?,?,?,?,?,?,?,?)
                   ON CONFLICT(id) DO UPDATE SET
                     gpu_model=excluded.gpu_model, vram_gb=excluded.vram_gb,
                     models=excluded.models, region=excluded.region,
                     latency_ms=excluded.latency_ms, uptime_hours=excluded.uptime_hours,
                     online=1, last_heartbeat=excluded.last_heartbeat""",
                (worker_id, body.get("gpu_model"), body.get("vram_gb"),
                 json.dumps(body.get("models") or []), body.get("region"),
                 body.get("latency_ms"), 0.9,
                 body.get("cost_per_mtok") or 0.30,
                 body.get("uptime_hours") or 0, 1, now))
            conn.commit()
        finally:
            conn.close()
        self._send_json(200, {"ok": True, "worker_id": worker_id})

    def _handle_chat(self, body):
        # Auth: Bearer key verified when present; demo mode without one.
        ok, err, demo = verify_bearer(self.headers.get("Authorization"))
        if not ok:
            self._send_error(401, err, "authentication_error")
            return
        # Rate limit per key (or per IP without a key).
        bucket = self.headers.get("Authorization") or self.client_address[0]
        if not check_rate_limit(bucket):
            self._send_json(429, {"error": {
                "message": "rate limit exceeded (demo: 60/min)",
                "type": "rate_limit"}})
            return
        model = body.get("model")
        messages = body.get("messages")
        if not messages or not isinstance(messages, list):
            self._send_error(400, "messages is required and must be a list")
            return
        if not model:
            self._send_error(400, "model is required")
            return
        if model not in MODEL_IDS:
            self._send_error(404, "unknown model: %s" % model)
            return
        prompt_text = " ".join(
            str(m.get("content", "")) for m in messages
            if isinstance(m, dict))
        prompt_tokens = approx_tokens(prompt_text)
        max_tokens = body.get("max_tokens")
        demo_text = (
            "[Nodefield demo — no live model ran] Nodefield is in pre-launch "
            "demo mode: no live GPU worker is connected, so the requested model "
            "(%s) is not actually loaded and no inference was performed. "
            "Your prompt was %d words (approx. %d tokens by word count). "
            "When workers connect, this endpoint will return real model output."
            % (model, len(prompt_text.split()), prompt_tokens))
        completion_tokens = approx_tokens(demo_text)
        if max_tokens is not None:
            try:
                completion_tokens = min(completion_tokens, int(max_tokens))
            except (TypeError, ValueError):
                pass
        usage = {"prompt_tokens": prompt_tokens,
                 "completion_tokens": completion_tokens,
                 "total_tokens": prompt_tokens + completion_tokens}
        chat_id = "chatcmpl-demo-" + secrets.token_hex(8)
        created = int(time.time())
        if body.get("stream"):
            self._send_stream(chat_id, created, model, demo_text, usage)
        else:
            self._send_json(200, {
                "id": chat_id, "object": "chat.completion", "created": created,
                "model": model,
                "choices": [{"index": 0,
                             "message": {"role": "assistant", "content": demo_text},
                             "finish_reason": "stop"}],
                "usage": usage})

    def _send_stream(self, chat_id, created, model, text, usage):
        """SSE stream: demo text split into word chunks, then [DONE]."""
        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        words = text.split(" ")
        chunk_size = 8
        for i in range(0, len(words), chunk_size):
            piece = " ".join(words[i:i + chunk_size])
            if i + chunk_size < len(words):
                piece += " "
            payload = {"id": chat_id, "object": "chat.completion.chunk",
                       "created": created, "model": model,
                       "choices": [{"index": 0, "delta": {"content": piece},
                                    "finish_reason": None}]}
            self.wfile.write(("data: %s\n\n" % json.dumps(payload)).encode("utf-8"))
            self.wfile.flush()
        payload = {"id": chat_id, "object": "chat.completion.chunk",
                   "created": created, "model": model,
                   "choices": [{"index": 0, "delta": {},
                                "finish_reason": "stop"}],
                   "usage": usage}
        self.wfile.write(("data: %s\n\ndata: [DONE]\n\n" % json.dumps(payload)).encode("utf-8"))
        self.wfile.flush()


def main():
    parser = argparse.ArgumentParser(description="Nodefield API prototype")
    parser.add_argument("--port", type=int, default=8787)
    args = parser.parse_args()
    get_db()  # create DB/tables on first run
    server = ThreadingHTTPServer(("0.0.0.0", args.port), Handler)
    print("Nodefield API (demo) listening on 0.0.0.0:%d" % args.port)
    print("DB: %s" % DB_PATH)
    sys.stdout.flush()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
