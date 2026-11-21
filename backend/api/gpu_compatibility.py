"""Nodefield GPU compatibility database (stdlib only, pure data + function).

Honest limits: statuses are based on VRAM size and known consumer/pro
hardware capability for running small quantized open-weight LLMs locally
(e.g. via llama.cpp). They are NOT measured benchmarks — no benchmark
numbers are claimed anywhere in this prototype.
"""

import json
import os

# status: "compatible" | "experimental" | "unsupported"
# max_model: largest model tier the GPU can plausibly host in Q4 quantisation.
COMPATIBILITY = {
    "RTX 3060 12GB": {
        "status": "compatible", "vram_gb": 12, "max_model": "medium (7B-8B)",
        "notes": "12GB VRAM comfortably hosts 7B-8B Q4 models; 14B is tight.",
    },
    "RTX 3070 8GB": {
        "status": "experimental", "vram_gb": 8, "max_model": "small (1B-4B)",
        "notes": "8GB VRAM: small models only; 7B-8B Q4 is borderline and may OOM.",
    },
    "RTX 3080 10GB": {
        "status": "compatible", "vram_gb": 10, "max_model": "small (1B-4B)",
        "notes": "10GB VRAM: small models comfortably; medium models experimental.",
    },
    "RTX 3090 24GB": {
        "status": "compatible", "vram_gb": 24, "max_model": "large (12B-14B)",
        "notes": "24GB VRAM hosts 12B-14B Q4 models.",
    },
    "RTX 4060 8GB": {
        "status": "experimental", "vram_gb": 8, "max_model": "small (1B-4B)",
        "notes": "8GB VRAM: small models only; 7B-8B Q4 is borderline and may OOM.",
    },
    "RTX 4070 12GB": {
        "status": "compatible", "vram_gb": 12, "max_model": "medium (7B-8B)",
        "notes": "12GB VRAM comfortably hosts 7B-8B Q4 models; 14B is tight.",
    },
    "RTX 4090 24GB": {
        "status": "compatible", "vram_gb": 24, "max_model": "large (12B-14B)",
        "notes": "24GB VRAM hosts 12B-14B Q4 models.",
    },
    "RTX 5090 32GB": {
        "status": "compatible", "vram_gb": 32, "max_model": "large (12B-14B)",
        "notes": "32GB VRAM hosts 12B-14B Q4 models with headroom.",
    },
    "GTX 1660 6GB": {
        "status": "experimental", "vram_gb": 6, "max_model": "small (1B-4B)",
        "notes": "6GB VRAM and older architecture: small Q4 models only, expect low throughput.",
    },
    "RX 6700 XT 12GB": {
        "status": "experimental", "vram_gb": 12, "max_model": "medium (7B-8B)",
        "notes": "AMD support is experimental in this prototype; ROCm/vulkan path untested here.",
    },
    "RX 6800 16GB": {
        "status": "experimental", "vram_gb": 16, "max_model": "medium (7B-8B)",
        "notes": "AMD support is experimental in this prototype; ROCm/vulkan path untested here.",
    },
    "RX 7900 XTX 24GB": {
        "status": "experimental", "vram_gb": 24, "max_model": "large (12B-14B)",
        "notes": "AMD support is experimental in this prototype; ROCm/vulkan path untested here.",
    },
    "Tesla T4 16GB": {
        "status": "compatible", "vram_gb": 16, "max_model": "medium (7B-8B)",
        "notes": "16GB datacentre GPU: medium models; efficient for inference.",
    },
    "A100 40GB": {
        "status": "compatible", "vram_gb": 40, "max_model": "large (12B-14B)",
        "notes": "40GB datacentre GPU: large models with headroom.",
    },
    "H100 80GB": {
        "status": "compatible", "vram_gb": 80, "max_model": "large (12B-14B)",
        "notes": "80GB datacentre GPU: large models with ample headroom.",
    },
}

# VRAM thresholds used by classify() for GPUs not in the table.
# <6GB unsupported; 6-8GB experimental (small only);
# >=8GB compatible for small, >=12GB medium, >=24GB large.
def _tier_for_vram(vram_gb):
    if vram_gb is None:
        return None
    if vram_gb < 6:
        return ("unsupported", None)
    if vram_gb < 8:
        return ("experimental", "small (1B-4B)")
    if vram_gb < 12:
        return ("compatible", "small (1B-4B)")
    if vram_gb < 24:
        return ("compatible", "medium (7B-8B)")
    return ("compatible", "large (12B-14B)")


def classify(gpu_model, vram_gb=None):
    """Classify a GPU for LLM inference.

    Returns {"status", "max_model", "notes"}.
    Known models come from the table above; unknown models fall back to
    the VRAM rules. VRAM below 6GB is always unsupported.
    """
    name = (gpu_model or "").strip()
    # Case-insensitive lookup against the table keys.
    entry = None
    for key, value in COMPATIBILITY.items():
        if key.lower() == name.lower():
            entry = value
            break
    if vram_gb is not None:
        try:
            vram_gb = float(vram_gb)
        except (TypeError, ValueError):
            vram_gb = None
    if vram_gb is not None and vram_gb < 6:
        return {
            "status": "unsupported",
            "max_model": None,
            "notes": "Under 6GB VRAM is unsupported for LLM inference in this prototype.",
        }
    if entry is not None:
        # If a VRAM figure was supplied and is lower than the table's,
        # the VRAM rule wins (a 3060 reported with 6GB is not a 12GB card).
        if vram_gb is not None and vram_gb < entry["vram_gb"]:
            status, max_model = _tier_for_vram(vram_gb)
            return {
                "status": status,
                "max_model": max_model,
                "notes": "VRAM reported (%sGB) is below the listed %sGB for %s; classified by VRAM."
                % (vram_gb, entry["vram_gb"], name),
            }
        return {
            "status": entry["status"],
            "max_model": entry["max_model"],
            "notes": entry["notes"],
        }
    if vram_gb is None:
        return {
            "status": "experimental",
            "max_model": "small (1B-4B)",
            "notes": "Unknown GPU model and no VRAM reported; treated as experimental "
                     "(small models only) until verified.",
        }
    status, max_model = _tier_for_vram(vram_gb)
    notes = {
        "unsupported": "Under 6GB VRAM is unsupported for LLM inference in this prototype.",
        "experimental": "Unknown GPU model; classified by VRAM only — small models, untested.",
        "compatible": "Unknown GPU model; classified by VRAM only — not yet verified on this hardware.",
    }[status]
    return {"status": status, "max_model": max_model, "notes": notes}


def export_json(path=None):
    """Write the compatibility table to JSON (for the frontend)."""
    if path is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "gpu_compatibility.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(COMPATIBILITY, f, indent=2, sort_keys=True)
        f.write("\n")
    return path


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--export":
        print("Wrote", export_json())
    else:
        for gpu, vram in [("RTX 4090 24GB", 24), ("RTX 4060 8GB", 8),
                          ("GTX 1660 6GB", 6), ("Unknown GPU", 3),
                          ("Unknown GPU", 16), ("Unknown GPU", None)]:
            print(gpu, vram, "->", classify(gpu, vram))
        print("Wrote", export_json())
