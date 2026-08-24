import random
import statistics
import string

import pytest

from bloom_filter import BloomFilter


def random_word(length: int = 12) -> str:
    alphabet = string.ascii_lowercase
    return "".join(random.choices(alphabet, k=length))


def random_dna(length: int = 40) -> str:
    return "".join(random.choices("ACGT", k=length))


def test_inserted_items_are_always_found():
    bloom = BloomFilter(expected_items=1000, false_positive_rate=0.01)
    items = [f"word_{i}" for i in range(1000)]

    for item in items:
        bloom.add(item)

    for item in items:
        assert item in bloom


def test_empty_filter_does_not_contain_item():
    bloom = BloomFilter(expected_items=100, false_positive_rate=0.01)
    assert "not inserted" not in bloom


def test_invalid_parameters():
    with pytest.raises(ValueError):
        BloomFilter(expected_items=0)

    with pytest.raises(ValueError):
        BloomFilter(expected_items=10, false_positive_rate=0)

    with pytest.raises(ValueError):
        BloomFilter(expected_items=10, false_positive_rate=1)


def test_bytes_are_supported():
    bloom = BloomFilter(expected_items=10)
    bloom.add(b"hello")
    assert b"hello" in bloom


def test_hashes_stay_inside_bit_array():
    bloom = BloomFilter(expected_items=1000)

    for position in bloom._hashes("example"):
        assert 0 <= position < bloom.num_bits


@pytest.mark.parametrize(
    "generator",
    [
        lambda i: f"english_word_{i}",
        lambda i: random_dna(50),
    ],
)
def test_hash_distribution_is_reasonably_uniform(generator):
    """
    Test hash quality on two data types:
    natural-language-like words and DNA sequences.

    This is not a proof of perfect uniformity, but it checks that the first
    hash positions do not cluster excessively in a small number of buckets.
    """
    random.seed(42)

    bloom = BloomFilter(expected_items=5000)
    buckets = [0] * 64
    sample_size = 2000

    for i in range(sample_size):
        position = next(bloom._hashes(generator(i)))
        bucket = position * len(buckets) // bloom.num_bits
        buckets[bucket] += 1

    mean = statistics.mean(buckets)
    standard_deviation = statistics.stdev(buckets)

    # A uniform distribution should have relatively small variation.
    assert standard_deviation / mean < 0.35


def test_observed_false_positive_rate_is_reasonable():
    random.seed(42)

    inserted = {f"inserted_{i}" for i in range(5000)}
    bloom = BloomFilter(expected_items=5000, false_positive_rate=0.01)

    for item in inserted:
        bloom.add(item)

    queries = {f"query_{i}" for i in range(10000)}
    false_positives = sum(item in bloom for item in queries)

    observed_rate = false_positives / len(queries)

    # Random variation is expected; allow a practical upper bound.
    assert observed_rate < 0.03
