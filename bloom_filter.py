"""
Bloom filter implementation using double hashing.

A Bloom filter can return false positives, but never false negatives
(unless it is used incorrectly or modified externally).
"""

from __future__ import annotations

import hashlib
import math
from typing import Union

Item = Union[str, bytes]


class BloomFilter:
    """Memory-efficient probabilistic set membership data structure."""

    def __init__(
        self,
        expected_items: int,
        false_positive_rate: float = 0.01,
    ) -> None:
        """
        Create a Bloom filter.

        Parameters
        ----------
        expected_items:
            Expected number of distinct items to insert.
        false_positive_rate:
            Target false-positive probability, between 0 and 1.
        """
        if expected_items <= 0:
            raise ValueError("expected_items must be greater than zero")
        if not 0 < false_positive_rate < 1:
            raise ValueError("false_positive_rate must be between 0 and 1")

        self.expected_items = expected_items
        self.target_false_positive_rate = false_positive_rate

        # Optimal number of bits:
        # m = -(n * ln(p)) / (ln(2)^2)
        self.num_bits = math.ceil(
            -(expected_items * math.log(false_positive_rate))
            / (math.log(2) ** 2)
        )

        # Optimal number of hash functions:
        # k = (m / n) * ln(2)
        self.num_hashes = max(
            1, round((self.num_bits / expected_items) * math.log(2))
        )

        self._bits = bytearray((self.num_bits + 7) // 8)
        self.items_added = 0

    @staticmethod
    def _to_bytes(item: Item) -> bytes:
        """Convert supported input values to bytes."""
        if isinstance(item, bytes):
            return item
        if isinstance(item, str):
            return item.encode("utf-8")
        raise TypeError("Items must be strings or bytes")

    def _hashes(self, item: Item):
        """
        Yield k positions using double hashing.

        Two independent cryptographic hashes are combined as:
        h_i(x) = h1(x) + i * h2(x) mod m
        """
        data = self._to_bytes(item)

        digest_1 = hashlib.blake2b(
            data, digest_size=8, person=b"BloomHash1"
        ).digest()
        digest_2 = hashlib.blake2b(
            data, digest_size=8, person=b"BloomHash2"
        ).digest()

        h1 = int.from_bytes(digest_1, byteorder="big")
        h2 = int.from_bytes(digest_2, byteorder="big") or 1

        for index in range(self.num_hashes):
            yield (h1 + index * h2) % self.num_bits

    def _set_bit(self, position: int) -> None:
        """Set one bit in the internal byte array."""
        byte_index = position // 8
        bit_index = position % 8
        self._bits[byte_index] |= 1 << bit_index

    def _get_bit(self, position: int) -> bool:
        """Return whether a bit is set."""
        byte_index = position // 8
        bit_index = position % 8
        return bool(self._bits[byte_index] & (1 << bit_index))

    def add(self, item: Item) -> None:
        """Insert an item into the Bloom filter."""
        for position in self._hashes(item):
            self._set_bit(position)
        self.items_added += 1

    def __contains__(self, item: Item) -> bool:
        """Return True if item may be present, False if definitely absent."""
        return all(self._get_bit(position) for position in self._hashes(item))

    def theoretical_false_positive_rate(self) -> float:
        """Return the expected false-positive rate after current insertions."""
        return (
            1
            - math.exp(
                -self.num_hashes * self.items_added / self.num_bits
            )
        ) ** self.num_hashes

    @property
    def memory_bytes(self) -> int:
        """Memory used by the Bloom filter bit array."""
        return len(self._bits)

    def __len__(self) -> int:
        """Return the number of add operations performed."""
        return self.items_added

    def __repr__(self) -> str:
        return (
            "BloomFilter("
            f"expected_items={self.expected_items}, "
            f"false_positive_rate={self.target_false_positive_rate}, "
            f"num_bits={self.num_bits}, "
            f"num_hashes={self.num_hashes}"
            ")"
        )
