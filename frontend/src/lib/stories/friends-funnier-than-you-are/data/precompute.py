#!/usr/bin/env python3
"""
Pre-compute trimmed cascade data for LogLogPlot.svelte.

The plot does three things at runtime that we can do once at build time:
  1. Slice each dataset's data to the first 10000 values.
  2. Filter values outside (1e-10, 1e5).
  3. Subsample: keep first 50, every 3rd from 50-499, every 5th after.

Additionally we:
  - Drop unused metadata fields (keep only p, pc, model).
  - Store as parallel `i` (index) and `v` (value) arrays, which is ~2x
    more compact than arrays of {index, value} objects in JSON.
  - Round values to 6 significant figures (plenty for a log-log plot).

Regenerate with:
    python3 precompute.py
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
SRC = HERE / "cascades.json"
OUT = HERE / "cascades.trimmed.json"


def round_sig(x: float, sig: int = 6) -> float:
    if x == 0:
        return 0.0
    from math import floor, log10
    return round(x, -int(floor(log10(abs(x)))) + (sig - 1))


def subsample(pairs):
    """Match the JS logic in LogLogPlot.svelte getData()."""
    out = []
    for i, (idx, value) in enumerate(pairs):
        s = i + 1
        if s < 50:
            out.append((idx, value))
        elif s < 500:
            if i % 3 == 0:
                out.append((idx, value))
        else:
            if i % 5 == 0:
                out.append((idx, value))
    return out


def process(dataset):
    meta = dataset["metadata"]
    raw = dataset["data"][:10000]
    # Preserve original indices through the filter.
    filtered = [
        (idx, v) for idx, v in enumerate(raw) if 1e-10 < v < 1e5
    ]
    sampled = subsample(filtered)
    return {
        "metadata": {
            "p": meta["p"],
            "pc": meta["pc"],
            "model": meta.get("model", "Unknown Model"),
        },
        "i": [idx for idx, _ in sampled],
        "v": [round_sig(v) for _, v in sampled],
    }


def main():
    with SRC.open() as f:
        raw = json.load(f)
    trimmed = {"datasets": {key: process(ds) for key, ds in raw["datasets"].items()}}
    # Compact JSON (no indentation) for smaller bundle size.
    with OUT.open("w") as f:
        json.dump(trimmed, f, separators=(",", ":"))
    print(f"Wrote {OUT}")
    print(f"  Source:  {SRC.stat().st_size / 1024 / 1024:.2f} MB")
    print(f"  Trimmed: {OUT.stat().st_size / 1024 / 1024:.2f} MB")
    total_points = sum(len(d["i"]) for d in trimmed["datasets"].values())
    print(f"  Datasets: {len(trimmed['datasets'])}, total points: {total_points}")


if __name__ == "__main__":
    main()
