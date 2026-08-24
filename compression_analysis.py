"""
Analyse Bloom-filter compression as expected item count and target FPR change.

Compression ratio:
raw storage required for the original strings / Bloom filter storage
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

import matplotlib.pyplot as plt

from bloom_filter import BloomFilter


def bloom_bits(expected_items: int, false_positive_rate: float) -> int:
    return math.ceil(
        -expected_items * math.log(false_positive_rate)
        / (math.log(2) ** 2)
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--expected-items",
        nargs="+",
        type=int,
        default=[1_000, 10_000, 100_000, 1_000_000],
    )
    parser.add_argument(
        "--false-positive-rates",
        nargs="+",
        type=float,
        default=[0.1, 0.01, 0.001, 0.0001],
    )
    parser.add_argument(
        "--average-string-length",
        type=int,
        default=12,
    )
    parser.add_argument(
        "--output-directory",
        default="results",
    )
    args = parser.parse_args()

    output_directory = Path(args.output_directory)
    output_directory.mkdir(parents=True, exist_ok=True)

    rows = []

    for expected_items in args.expected_items:
        raw_bytes = expected_items * args.average_string_length

        for rate in args.false_positive_rates:
            bloom = BloomFilter(expected_items, rate)
            ratio = raw_bytes / bloom.memory_bytes

            rows.append(
                {
                    "expected_items": expected_items,
                    "target_false_positive_rate": rate,
                    "bloom_memory_bytes": bloom.memory_bytes,
                    "raw_string_memory_bytes": raw_bytes,
                    "compression_ratio": ratio,
                    "num_hashes": bloom.num_hashes,
                }
            )

    csv_path = output_directory / "compression_results.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    plt.figure(figsize=(8, 5))

    for rate in args.false_positive_rates:
        selected = [
            row for row in rows
            if row["target_false_positive_rate"] == rate
        ]

        plt.plot(
            [row["expected_items"] for row in selected],
            [row["compression_ratio"] for row in selected],
            marker="o",
            label=f"Target FPR = {rate}",
        )

    plt.xscale("log")
    plt.xlabel("Expected number of items")
    plt.ylabel("Compression ratio")
    plt.title("Bloom-filter compression ratio")
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.savefig(output_directory / "compression_ratio.png", dpi=200)

    print(f"Saved results to {csv_path}")


if __name__ == "__main__":
    main()
