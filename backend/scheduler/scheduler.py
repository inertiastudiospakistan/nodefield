"""Nodefield distributed compute scheduler (stdlib only, importable module).

Assigns independent inference requests to suitable GPU workers. It does
NOT split one model across distributed GPUs — one request goes to one
worker. No live workers exist yet; the self-test below uses DEMO workers
only, clearly labelled as such.
"""

import time
from dataclasses import dataclass, field

# Model -> minimum VRAM (GB) needed to host it in Q4 quantisation.
# Provisional planning figures, not measured benchmarks.
MODEL_VRAM_GB = {
    "qwen3-4b": 4,
    "qwen3-8b": 8,
    "qwen3-14b": 14,
    "llama-3.1-8b": 8,
    "mistral-7b": 8,
}

JOB_STATES = ("pending", "assigned", "running", "completed", "failed", "cancelled")
JOB_TIMEOUT_SECONDS = 120
MAX_RETRIES = 2


@dataclass
class Worker:
    id: str
    gpu_model: str
    vram_gb: float
    models: list = field(default_factory=list)
    region: str = "unknown"
    latency_ms: float = 100.0
    reliability: float = 0.9  # 0-1, fraction of past jobs completed
    cost_per_mtok: float = 0.30
    uptime_hours: float = 0.0
    online: bool = True
    last_heartbeat: float = field(default_factory=time.time)


@dataclass
class Job:
    id: str
    model: str
    prompt: str
    priority: str = "standard"
    state: str = "pending"
    worker_id: str = None
    retries: int = 0
    created_at: float = field(default_factory=time.time)
    assigned_at: float = None
    timeout_seconds: int = JOB_TIMEOUT_SECONDS


def score_worker(worker, job):
    """Score a worker for a job. Returns (score, breakdown) or (None, reason).

    Hard filters (return None): worker offline, model not offered,
    VRAM below the model's minimum. Otherwise a 0-1 weighted score from
    reliability (50%), cost (30%, cheaper is better) and latency (20%).
    """
    if not worker.online:
        return None, {"reason": "worker offline"}
    if job.model not in worker.models:
        return None, {"reason": "model %s not offered by worker" % job.model}
    required_vram = MODEL_VRAM_GB.get(job.model)
    if required_vram is None:
        return None, {"reason": "unknown model %s" % job.model}
    if worker.vram_gb < required_vram:
        return None, {
            "reason": "VRAM %.1fGB < %.1fGB required for %s"
                      % (worker.vram_gb, required_vram, job.model)}
    reliability = max(0.0, min(1.0, worker.reliability))
    # Cost: normalise against a $1.00/MTok reference; cheaper scores higher.
    cost_score = max(0.0, 1.0 - (worker.cost_per_mtok / 1.0))
    # Latency: 0ms -> 1.0, >=500ms -> 0.0.
    latency_score = max(0.0, 1.0 - (worker.latency_ms / 500.0))
    score = 0.5 * reliability + 0.3 * cost_score + 0.2 * latency_score
    breakdown = {
        "reliability": round(reliability, 3),
        "cost_score": round(cost_score, 3),
        "latency_score": round(latency_score, 3),
        "score": round(score, 4),
    }
    return round(score, 4), breakdown


def assign_job(job, workers):
    """Return (worker, score, breakdown) for the best worker, or (None, None, reason).

    The job object is NOT mutated here; the caller records the assignment.
    """
    best = None
    best_score = None
    best_breakdown = None
    reasons = []
    for worker in workers:
        score, info = score_worker(worker, job)
        if score is None:
            reasons.append("%s: %s" % (worker.id, info["reason"]))
        elif best_score is None or score > best_score:
            best, best_score, best_breakdown = worker, score, info
    if best is None:
        return None, None, {"reason": "no suitable worker", "details": reasons}
    return best, best_score, best_breakdown


def check_timeout(job, now=None):
    """Return True if an assigned/running job has exceeded its timeout."""
    if job.state not in ("assigned", "running") or job.assigned_at is None:
        return False
    now = time.time() if now is None else now
    return (now - job.assigned_at) > job.timeout_seconds


def handle_timeout(job):
    """Apply timeout/retry policy: retry up to MAX_RETRIES, then fail."""
    if job.retries < MAX_RETRIES:
        job.retries += 1
        job.state = "pending"
        job.worker_id = None
        job.assigned_at = None
        return "retry %d/%d" % (job.retries, MAX_RETRIES)
    job.state = "failed"
    return "failed after %d retries" % MAX_RETRIES


# --- In-memory worker registry -------------------------------------------

class Registry:
    """Small in-memory registry of workers, keyed by worker id."""

    def __init__(self):
        self.workers = {}

    def register_worker(self, worker):
        self.workers[worker.id] = worker
        return worker

    def heartbeat(self, worker_id, now=None):
        worker = self.workers.get(worker_id)
        if worker is None:
            return None
        worker.last_heartbeat = time.time() if now is None else now
        worker.online = True
        return worker

    def online_workers(self):
        return [w for w in self.workers.values() if w.online]

    def get(self, worker_id):
        return self.workers.get(worker_id)


if __name__ == "__main__":
    # Self-test with DEMO workers only — no real hardware is involved.
    registry = Registry()
    demo_workers = [
        # DEMO worker: high-end, reliable, pricier.
        Worker(id="demo-worker-rtx4090", gpu_model="RTX 4090 24GB", vram_gb=24,
               models=["qwen3-4b", "qwen3-8b", "qwen3-14b", "llama-3.1-8b", "mistral-7b"],
               region="EU", latency_ms=45, reliability=0.98, cost_per_mtok=0.40,
               uptime_hours=120.0),
        # DEMO worker: mid-range, cheap, slower.
        Worker(id="demo-worker-rtx3060", gpu_model="RTX 3060 12GB", vram_gb=12,
               models=["qwen3-4b", "qwen3-8b", "llama-3.1-8b", "mistral-7b"],
               region="EU", latency_ms=120, reliability=0.90, cost_per_mtok=0.20,
               uptime_hours=48.0),
        # DEMO worker: low VRAM — must be rejected for 14B models.
        # (It lists qwen3-14b as offered so the VRAM filter, not the
        # model filter, is what rejects it.)
        Worker(id="demo-worker-gtx1660", gpu_model="GTX 1660 6GB", vram_gb=6,
               models=["qwen3-4b", "qwen3-14b"],
               region="EU", latency_ms=200, reliability=0.75, cost_per_mtok=0.15,
               uptime_hours=10.0),
    ]
    for w in demo_workers:
        registry.register_worker(w)

    job = Job(id="demo-job-1", model="qwen3-8b", prompt="Hello, demo job.")
    worker, score, breakdown = assign_job(job, registry.online_workers())
    print("Job %s (%s) assigned to: %s" % (job.id, job.model, worker.id if worker else None))
    print("Score: %s  breakdown: %s" % (score, breakdown))
    assert worker is not None, "expected a worker for qwen3-8b"

    # VRAM filter: the 4GB-class / 6GB worker must be rejected for a 14B model.
    big_job = Job(id="demo-job-2", model="qwen3-14b", prompt="Large model job.")
    small = registry.get("demo-worker-gtx1660")
    s, info = score_worker(small, big_job)
    print("VRAM filter check — GTX 1660 6GB for qwen3-14b: score=%s info=%s" % (s, info))
    assert s is None, "6GB worker must be rejected for a 14B model"
    assert "VRAM" in info["reason"]

    # Timeout / retry: 2 retries then failed.
    job2 = Job(id="demo-job-3", model="qwen3-8b", prompt="Timeout test.")
    job2.state, job2.assigned_at = "running", time.time() - 200
    assert check_timeout(job2) is True
    assert handle_timeout(job2) == "retry 1/2" and job2.state == "pending"
    job2.state, job2.assigned_at = "running", time.time() - 200
    handle_timeout(job2)
    job2.state, job2.assigned_at = "running", time.time() - 200
    assert handle_timeout(job2) == "failed after 2 retries" and job2.state == "failed"

    print("Scheduler self-test passed (all DEMO workers).")
