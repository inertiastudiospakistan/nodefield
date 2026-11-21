"""Nodefield contributor agent prototype — Python standard library only.

Runs on a contributor's machine, detects hardware honestly, and reports
capacity to the coordinator. It NEVER executes arbitrary customer code,
never accesses personal files, and never hides activity: the user can
pause it or uninstall it at any time (see README.md).

Usage:
  python3 agent.py --report    # print a JSON status report, do not connect
  python3 agent.py --once      # detect hardware, benchmark stub, one heartbeat
  python3 agent.py             # loop heartbeats every 60s until stopped
"""

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
COORDINATOR_URL = "http://localhost:8787/api/workers"

DEFAULT_CONFIG = {
    "max_gpu_percent": 80,
    "max_vram_gb": 0,          # 0 = no explicit VRAM cap set
    "allowed_hours": "00:00-23:59",
    "paused": False,
    "worker_id": "local-worker-1",
    "gpu_model": None,
    "vram_gb": None,
}


def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, encoding="utf-8") as f:
            cfg = json.load(f)
        merged = dict(DEFAULT_CONFIG)
        merged.update(cfg)
        return merged
    return dict(DEFAULT_CONFIG)


def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
        f.write("\n")


def detect_os():
    return {"system": platform.system(), "release": platform.release(),
            "version": platform.version(), "machine": platform.machine(),
            "python": platform.python_version()}


def detect_cpu_ram():
    cpu_count = os.cpu_count() or 1
    ram_gb = None
    # Linux: read /proc/meminfo.
    try:
        with open("/proc/meminfo", encoding="utf-8") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    kb = int(line.split()[1])
                    ram_gb = round(kb / 1024 / 1024, 2)
                    break
    except (OSError, ValueError):
        pass
    if ram_gb is None:
        # Fallback: no reliable stdlib cross-platform RAM query; say so.
        ram_gb = None
    return {"cpu_count": cpu_count, "ram_gb": ram_gb}


def detect_gpu():
    """Try nvidia-smi, then lspci, then report honestly that no GPU
    was detected. Never invents a GPU."""
    # 1. nvidia-smi (NVIDIA GPUs).
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
                return {"detected": True, "source": "nvidia-smi",
                        "gpu_model": name.strip(),
                        "vram_gb": round(vram, 1) if vram else None}
        except (subprocess.SubprocessError, OSError):
            pass
    # 2. lspci (Linux PCI listing — catches AMD/Intel GPUs too).
    if shutil.which("lspci"):
        try:
            out = subprocess.run(["lspci"], capture_output=True,
                                 text=True, timeout=10)
            if out.returncode == 0:
                for line in out.stdout.splitlines():
                    low = line.lower()
                    if "vga" in low or "3d controller" in low:
                        model = line.split(":", 2)[-1].strip()
                        return {"detected": True, "source": "lspci",
                                "gpu_model": model, "vram_gb": None}
        except (subprocess.SubprocessError, OSError):
            pass
    return {"detected": False, "source": None, "gpu_model": None,
            "vram_gb": None,
            "note": "no GPU detected on this machine"}


def benchmark_stub():
    """CPU sanity check ONLY. Runs a tiny timing loop and reports only
    the measured wall-time. This is NOT a GPU benchmark and no GPU
    performance numbers are claimed: no GPU / no model is loaded here."""
    n = 200_000
    start = time.perf_counter()
    total = 0
    for i in range(n):
        total += i * i
    elapsed = time.perf_counter() - start
    return {"type": "CPU sanity check only — GPU benchmark not run "
                    "(no GPU / no model loaded)",
            "loop_iterations": n, "checksum": total,
            "wall_time_seconds": round(elapsed, 4)}


def status_report():
    cfg = load_config()
    gpu = detect_gpu()
    # Prefer configured GPU details only if detection found nothing and
    # the user explicitly set them; detection always wins when present.
    if not gpu["detected"] and cfg.get("gpu_model"):
        gpu = {"detected": False, "source": "config (user-set)",
               "gpu_model": cfg["gpu_model"], "vram_gb": cfg.get("vram_gb"),
               "note": "GPU from config, not detected by this machine"}
    return {
        "worker_id": cfg.get("worker_id"),
        "paused": bool(cfg.get("paused")),
        "os": detect_os(),
        "cpu_ram": detect_cpu_ram(),
        "gpu": gpu,
        "resource_limits": {
            "max_gpu_percent": cfg.get("max_gpu_percent"),
            "max_vram_gb": cfg.get("max_vram_gb"),
            "allowed_hours": cfg.get("allowed_hours"),
        },
        "benchmark": benchmark_stub(),
        "coordinator_url": COORDINATOR_URL,
        "timestamp": int(time.time()),
    }


def heartbeat(report):
    """POST worker status to the coordinator. Connection refused (no
    server running) is handled gracefully with a clear message."""
    if report["paused"]:
        return {"ok": False, "error": "paused by user (config paused=true)"}
    gpu = report["gpu"]
    if not gpu.get("detected"):
        # A machine with no detected GPU is not a GPU worker. Registering
        # it would mislead the coordinator (and /api/health) into
        # reporting a live worker where there is none.
        return {"ok": False,
                "error": "no GPU detected on this machine — not registering "
                         "as a GPU worker (see --report)"}
    payload = {
        "id": report["worker_id"],
        "gpu_model": gpu.get("gpu_model"),
        "vram_gb": gpu.get("vram_gb"),
        "models": [],  # no model loaded in this prototype
        "region": "unknown",
        "latency_ms": None,
        "uptime_hours": 0,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(COORDINATOR_URL, data=data, method="POST",
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return {"ok": True, "status": resp.status,
                    "body": json.loads(resp.read().decode("utf-8"))}
    except urllib.error.URLError as e:
        return {"ok": False,
                "error": "coordinator unreachable at %s: %s "
                         "(is the API server running? Start it with "
                         "`cd backend/api && python3 server.py`)"
                         % (COORDINATOR_URL, e.reason)}
    except OSError as e:
        return {"ok": False, "error": "coordinator unreachable: %s" % e}


def main():
    parser = argparse.ArgumentParser(description="Nodefield contributor agent")
    parser.add_argument("--report", action="store_true",
                        help="print a JSON status report and exit")
    parser.add_argument("--once", action="store_true",
                        help="detect, benchmark, send one heartbeat, exit")
    parser.add_argument("--pause", action="store_true",
                        help="set paused=true in config and exit")
    parser.add_argument("--resume", action="store_true",
                        help="set paused=false in config and exit")
    args = parser.parse_args()

    if args.pause or args.resume:
        cfg = load_config()
        cfg["paused"] = bool(args.pause)
        save_config(cfg)
        print("Agent %s." % ("paused" if args.pause else "resumed"))
        return 0

    if args.report:
        print(json.dumps(status_report(), indent=2))
        return 0

    if args.once:
        report = status_report()
        print(json.dumps(report, indent=2))
        print("Heartbeat:", json.dumps(heartbeat(report), indent=2))
        return 0

    print("Nodefield agent running. Heartbeat every 60s. Ctrl+C to stop.")
    print("Pause with: python3 agent.py --pause")
    try:
        while True:
            report = status_report()
            result = heartbeat(report)
            print("[%s] heartbeat: %s"
                  % (time.strftime("%H:%M:%S"), json.dumps(result)))
            sys.stdout.flush()
            time.sleep(60)
    except KeyboardInterrupt:
        print("\nAgent stopped by user.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
