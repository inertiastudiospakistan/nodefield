"""Nodefield pricing engine — pure functions, no I/O.

Prices are USD per 1,000,000 tokens. These are PROVISIONAL launch
targets for the pricing page, not measured costs: no live inference has
been run yet, so no real cost-per-token has been established. The
economics must be validated against real benchmarks before any paid
billing is activated (see backend README).
"""

# USD per 1M tokens: (input, output)
PRICES = {
    "economy":  {"input_per_mtok": 0.15, "output_per_mtok": 0.60},
    "standard": {"input_per_mtok": 0.30, "output_per_mtok": 1.20},
    "priority": {"input_per_mtok": 0.60, "output_per_mtok": 2.40},
    # Batch = 50% of standard.
    "batch":    {"input_per_mtok": 0.15, "output_per_mtok": 0.60},
}

PROVIDER_SPLIT = 0.80  # 80% of request revenue goes to the GPU provider.


def price_request(tier, input_tokens, output_tokens):
    """Cost breakdown for one request. Returns a dict of USD amounts."""
    if tier not in PRICES:
        raise ValueError("unknown pricing tier: %r (expected one of %s)"
                         % (tier, ", ".join(sorted(PRICES))))
    if input_tokens < 0 or output_tokens < 0:
        raise ValueError("token counts must be >= 0")
    rate = PRICES[tier]
    input_cost = input_tokens / 1_000_000 * rate["input_per_mtok"]
    output_cost = output_tokens / 1_000_000 * rate["output_per_mtok"]
    total = input_cost + output_cost
    return {
        "tier": tier,
        "input_tokens": int(input_tokens),
        "output_tokens": int(output_tokens),
        "input_cost_usd": round(input_cost, 6),
        "output_cost_usd": round(output_cost, 6),
        "total_cost_usd": round(total, 6),
        "input_per_mtok_usd": rate["input_per_mtok"],
        "output_per_mtok_usd": rate["output_per_mtok"],
    }


def provider_payout(cost, split=PROVIDER_SPLIT):
    """USD paid to the GPU provider from a request costing `cost`."""
    if not 0 <= split <= 1:
        raise ValueError("split must be between 0 and 1")
    return round(float(cost) * split, 6)


def platform_fee(cost, split=PROVIDER_SPLIT):
    """USD retained by the platform from a request costing `cost`."""
    if not 0 <= split <= 1:
        raise ValueError("split must be between 0 and 1")
    return round(float(cost) * (1 - split), 6)


def estimate_electricity_cost(power_watts, hours, kwh_price_usd):
    """Electricity cost (USD) for running hardware.

    power_watts: average draw in watts; hours: run time;
    kwh_price_usd: local electricity price per kWh.
    """
    if power_watts < 0 or hours < 0 or kwh_price_usd < 0:
        raise ValueError("power, hours and kWh price must be >= 0")
    kwh = (power_watts / 1000.0) * hours
    return {"kwh": round(kwh, 4), "cost_usd": round(kwh * kwh_price_usd, 4)}


if __name__ == "__main__":
    # Worked example: 1,000 input + 500 output tokens, standard tier.
    example = price_request("standard", 1000, 500)
    print("Worked example — standard tier, 1000 in / 500 out tokens:")
    print("  input cost:  $%.6f" % example["input_cost_usd"])
    print("  output cost: $%.6f" % example["output_cost_usd"])
    print("  total cost:  $%.6f" % example["total_cost_usd"])
    print("  provider payout (80%%): $%.6f"
          % provider_payout(example["total_cost_usd"]))
    print("  platform fee (20%%):    $%.6f"
          % platform_fee(example["total_cost_usd"]))
    elec = estimate_electricity_cost(300, 1, 0.15)
    print("  electricity: 300W for 1h at $0.15/kWh = %.4f kWh, $%.4f"
          % (elec["kwh"], elec["cost_usd"]))
    print("  1M in / 1M out tokens at standard: $%.2f"
          % price_request("standard", 1_000_000, 1_000_000)["total_cost_usd"])
