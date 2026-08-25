"""
Measure how the false-positive rate changes as the Bloom filter fills up.

The filter is designed for a fixed number of items, then deliberately
overfilled to show what happens beyond its intended capacity.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt

from bloom_filter import BloomFilter


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--expected-items",
        type=int,
        default=100_000,
        help="Number of items for which the Bloom filter is designed.",
    )
    parser.add_argument(
        "--false-positive-rate",
        type=float,
        default=0.01,
        help="Target false-positive rate used when designing the filter.",
    )
    parser.add_argument(
        "--query-count",
        type=int,
        default=50_000,
        help="Number of items not inserted, used to measure false positives.",
    )
    parser.add_argument(
        "--output-directory",
        default="results",
    )
    arguments = parser.parse_args()

    output_directory = Path(arguments.output_directory)
    output_directory.mkdir(parents=True, exist_ok=True)

    # Includes values below, equal to, and above expected capacity.
    insertion_counts = [
        arguments.expected_items // 4,
        arguments.expected_items // 2,
        arguments.expected_items,
        int(arguments.expected_items * 1.5),
        arguments.expected_items * 2,
    ]

    query_items = [
        f"query_item_{index}"
        for index in range(arguments.query_count)
    ]

    rows = []

    for count in insertion_counts:
        bloom = BloomFilter(
            expected_items=arguments.expected_items,
            false_positive_rate=arguments.false_positive_rate,
        )

        for index in range(count):
            bloom.add(f"inserted_item_{index}")

        false_positives = sum(
            item in bloom for item in query_items
        )

        observed_rate = false_positives / arguments.query_count

        rows.append(
            {
                "expected_items": arguments.expected_items,
                "inserted_items": count,
                "target_false_positive_rate": (
                    arguments.false_positive_rate
                ),
                "observed_false_positive_rate": observed_rate,
                "theoretical_false_positive_rate": (
                    bloom.theoretical_false_positive_rate()
                ),
                "memory_bytes": bloom.memory_bytes,
            }
        )

        print(
            f"Inserted: {count:,} | "
            f"Observed FPR: {observed_rate:.4f} | "
            f"Theoretical FPR: "
            f"{bloom.theoretical_false_positive_rate():.4f}"
        )

    csv_file = output_directory / "false_positive_overload.csv"

    with csv_file.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=rows[0].keys(),
        )
        writer.writeheader()
        writer.writerows(rows)

    plt.figure(figsize=(8, 5))

    plt.plot(
        [row["inserted_items"] for row in rows],
        [row["observed_false_positive_rate"] for row in rows],
        marker="o",
        label="Observed false-positive rate",
    )

    plt.plot(
        [row["inserted_items"] for row in rows],
        [row["theoretical_false_positive_rate"] for row in rows],
        marker="o",
        label="Theoretical false-positive rate",
    )

    plt.axvline(
        arguments.expected_items,
        color="red",
        linestyle="--",
        label="Designed capacity",
    )

    plt.xlabel("Number of inserted items")
    plt.ylabel("False-positive rate")
    plt.title("False-positive rate when exceeding Bloom-filter capacity")
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.savefig(
        output_directory / "false_positive_overload.png",
        dpi=200,
    )

    print(f"\nSaved CSV: {csv_file}")
    print(
        "Saved plot: "
        f"{output_directory / 'false_positive_overload.png'}"
    )


if __name__ == "__main__":
    main()
