"""
Benchmark Bloom-filter insertion, lookup and false-positive performance.

Example:
python benchmark.py --data-type words --sizes 1000 10000 100000
"""

from __future__ import annotations

import argparse
import csv
import random
import string
import time
from pathlib import Path

import matplotlib.pyplot as plt

from bloom_filter import BloomFilter


def generate_words(count: int, length: int = 12) -> list[str]:
    alphabet = string.ascii_lowercase
    return [
        "".join(random.choices(alphabet, k=length))
        for _ in range(count)
    ]


def generate_dna(count: int, length: int = 80) -> list[str]:
    return [
        "".join(random.choices("ACGT", k=length))
        for _ in range(count)
    ]


def make_data(count: int, data_type: str) -> list[str]:
    if data_type == "words":
        return generate_words(count)
    return generate_dna(count)


def benchmark_size(
    size: int,
    data_type: str,
    false_positive_rate: float,
) -> dict:
    inserted_items = make_data(size, data_type)
    query_items = make_data(size, data_type)

    bloom = BloomFilter(
        expected_items=size,
        false_positive_rate=false_positive_rate,
    )

    start = time.perf_counter()
    for item in inserted_items:
        bloom.add(item)
    insert_seconds = time.perf_counter() - start

    start = time.perf_counter()
    found_inserted = sum(item in bloom for item in inserted_items)
    successful_lookup_seconds = time.perf_counter() - start

    start = time.perf_counter()
    false_positives = sum(item in bloom for item in query_items)
    unsuccessful_lookup_seconds = time.perf_counter() - start

    return {
        "size": size,
        "data_type": data_type,
        "insert_seconds": insert_seconds,
        "insert_microseconds_per_item": insert_seconds / size * 1_000_000,
        "successful_lookup_seconds": successful_lookup_seconds,
        "successful_lookup_microseconds_per_item": (
            successful_lookup_seconds / size * 1_000_000
        ),
        "unsuccessful_lookup_seconds": unsuccessful_lookup_seconds,
        "unsuccessful_lookup_microseconds_per_item": (
            unsuccessful_lookup_seconds / size * 1_000_000
        ),
        "found_inserted": found_inserted,
        "observed_false_positive_rate": false_positives / size,
        "theoretical_false_positive_rate": (
            bloom.theoretical_false_positive_rate()
        ),
        "memory_bytes": bloom.memory_bytes,
        "num_hashes": bloom.num_hashes,
    }


def save_csv(rows: list[dict], output_directory: Path) -> None:
    filename = output_directory / "benchmark_results.csv"

    with filename.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def create_plots(rows: list[dict], output_directory: Path) -> None:
    sizes = [row["size"] for row in rows]

    plt.figure(figsize=(8, 5))
    plt.plot(
        sizes,
        [row["insert_microseconds_per_item"] for row in rows],
        marker="o",
        label="Insert",
    )
    plt.plot(
        sizes,
        [row["successful_lookup_microseconds_per_item"] for row in rows],
        marker="o",
        label="Successful search",
    )
    plt.plot(
        sizes,
        [row["unsuccessful_lookup_microseconds_per_item"] for row in rows],
        marker="o",
        label="Unsuccessful search",
    )
    plt.xscale("log")
    plt.xlabel("Number of inserted items")
    plt.ylabel("Time per operation (microseconds)")
    plt.title("Bloom filter operation time")
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.savefig(output_directory / "operation_times.png", dpi=200)
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.plot(
        sizes,
        [row["observed_false_positive_rate"] for row in rows],
        marker="o",
        label="Observed",
    )
    plt.plot(
        sizes,
        [row["theoretical_false_positive_rate"] for row in rows],
        marker="o",
        label="Theoretical",
    )
    plt.xscale("log")
    plt.xlabel("Number of inserted items")
    plt.ylabel("False-positive rate")
    plt.title("Observed versus theoretical false-positive rate")
    plt.legend()
    plt.grid()
    plt.tight_layout()
    plt.savefig(output_directory / "false_positive_rate.png", dpi=200)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sizes",
        nargs="+",
        type=int,
        default=[1_000, 10_000, 100_000, 1_000_000],
    )
    parser.add_argument(
        "--data-type",
        choices=["words", "dna"],
        default="words",
    )
    parser.add_argument(
        "--false-positive-rate",
        type=float,
        default=0.01,
    )
    parser.add_argument(
        "--output-directory",
        default="results",
    )
    arguments = parser.parse_args()

    random.seed(42)

    output_directory = Path(arguments.output_directory)
    output_directory.mkdir(parents=True, exist_ok=True)

    rows = [
        benchmark_size(
            size=size,
            data_type=arguments.data_type,
            false_positive_rate=arguments.false_positive_rate,
        )
        for size in arguments.sizes
    ]

    save_csv(rows, output_directory)
    create_plots(rows, output_directory)

    for row in rows:
        print(
            f"n={row['size']:,} | "
            f"insert={row['insert_microseconds_per_item']:.2f} µs/item | "
            f"search={row['successful_lookup_microseconds_per_item']:.2f} µs/item | "
            f"FPR={row['observed_false_positive_rate']:.4f}"
        )


if __name__ == "__main__":
    main()
