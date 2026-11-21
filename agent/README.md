# Nodefield Contributor Agent (prototype)

A lightweight contributor agent. Python standard library only — no
dependencies. Run it with `python3 agent.py`.

## What it does

- Detects OS, CPU count, RAM, and GPU (via `nvidia-smi`, then `lspci`).
  If no GPU is found it says so honestly: "no GPU detected on this machine".
- Runs a CPU-only sanity-check timing loop and reports only the measured
  wall-time. It does **not** invent GPU benchmark numbers.
- Sends a heartbeat to the coordinator (`http://localhost:8787/api/workers`)
  — but only when a GPU was actually detected. A machine with no GPU is
  not registered as a worker (that would falsely inflate the worker count).
  If the server is not running it reports that clearly instead of crashing.
- Reads resource limits from `config.json` (`max_gpu_percent`,
  `max_vram_gb`, `allowed_hours`, `paused`).

## Usage

```bash
python3 agent.py --report   # print a JSON status report, do not connect
python3 agent.py --once     # detect + benchmark + one heartbeat, then exit
python3 agent.py            # heartbeat every 60s until Ctrl+C
python3 agent.py --pause    # pause participation
python3 agent.py --resume   # resume participation
```

## Security rules

- **Never executes arbitrary customer code.** Inference workloads run
  only through a fixed, sandboxed runtime; the agent accepts no code,
  scripts, or shell commands from the network.
- **Sandboxed workloads only.** Any future model execution must run
  inside a sandbox with strict resource limits (CPU, VRAM, memory,
  network) and no access to the user's files.
- **Least privilege.** The agent runs as a normal user process, reads
  only hardware information, and writes only its own `config.json`.
- **No hidden activity.** Everything the agent does is visible: the
  status report, the heartbeat log, and the coordinator dashboard show
  what is running. It never uses the GPU silently.
- **No personal files.** The agent never reads, uploads, or accesses
  personal files, documents, or browsing data.
- **User control.** Pause at any time (`python3 agent.py --pause`) or
  uninstall by deleting this folder. Pausing stops all heartbeats and
  all participation.
- **No earnings claims.** Being connected does **not** mean money is
  being earned. Earnings exist only when real paid workloads complete,
  and no payments exist in this pre-launch prototype.
- **Encrypted communications and signed updates** are required before
  any production release; this prototype talks plain HTTP to localhost
  only and has no auto-update mechanism.

## Honest limits

- This machine (the dev VM) has no GPU, so detection reports no GPU.
- No model is loaded and no inference runs in this prototype.
- The benchmark is a CPU timing loop only — not a GPU benchmark.
