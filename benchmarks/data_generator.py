"""
Data generation utilities for benchmarking.

Generates random strings with configurable parameters for benchmarking parsers.
Uses streaming generation to minimize memory usage.
"""

import random
import string
import math
from typing import List, Iterator, Generator


def generate_logarithmic_sizes(min_size: int, max_size: int, num_steps: int) -> List[int]:
    """
    Generate a list of sizes in logarithmic scale.

    Args:
        min_size: Minimum list size (e.g., 1)
        max_size: Maximum list size (e.g., 1_000_000)
        num_steps: Number of steps (e.g., 20)

    Returns:
        List of integer sizes in logarithmic scale
    """
    if num_steps <= 1:
        return [max_size]

    log_min = math.log10(max(min_size, 1))
    log_max = math.log10(max_size)

    sizes = []
    for i in range(num_steps):
        log_val = log_min + (log_max - log_min) * i / (num_steps - 1)
        sizes.append(int(round(10 ** log_val)))

    # Ensure uniqueness
    sizes = sorted(set(sizes))
    return sizes


def generate_random_string(min_length: int = 1, max_length: int = 200,
                           chars: str = None, rng: random.Random = None) -> str:
    """
    Generate a random string with length uniformly distributed between min_length and max_length.

    Args:
        min_length: Minimum string length (inclusive)
        max_length: Maximum string length (inclusive)
        chars: Character set to use (default: ASCII letters + digits)
        rng: Random number generator instance

    Returns:
        Random string
    """
    if chars is None:
        chars = string.ascii_letters + string.digits
    if rng is None:
        rng = random.Random()

    length = rng.randint(min_length, max_length)
    return ''.join(rng.choice(chars) for _ in range(length))


def generate_string_generator(n: int, min_length: int = 1, max_length: int = 200,
                               chars: str = None, seed: int = None) -> Generator[str, None, None]:
    """
    Generate n random strings as a generator (memory efficient).

    Note: Does not guarantee uniqueness for memory efficiency.

    Args:
        n: Number of strings to generate
        min_length: Minimum string length (inclusive)
        max_length: Maximum string length (inclusive)
        chars: Character set to use (default: ASCII letters + digits)
        seed: Random seed for reproducibility

    Yields:
        Random strings
    """
    if chars is None:
        chars = string.ascii_letters + string.digits
    rng = random.Random(seed)

    for _ in range(n):
        length = rng.randint(min_length, max_length)
        yield ''.join(rng.choice(chars) for _ in range(length))


def generate_string_list(n: int, min_length: int = 1, max_length: int = 200,
                         chars: str = None, seed: int = None,
                         unique: bool = False) -> List[str]:
    """
    Generate a list of n random strings.

    Args:
        n: Number of strings to generate
        min_length: Minimum string length (inclusive)
        max_length: Maximum string length (inclusive)
        chars: Character set to use (default: ASCII letters + digits)
        seed: Random seed for reproducibility
        unique: If True, ensure all strings are unique (uses more memory)

    Returns:
        List of random strings
    """
    if not unique:
        return list(generate_string_generator(n, min_length, max_length, chars, seed))

    rng = random.Random(seed)
    if chars is None:
        chars = string.ascii_letters + string.digits

    strings = set()
    max_attempts = n * 3

    attempts = 0
    while len(strings) < n and attempts < max_attempts:
        length = rng.randint(min_length, max_length)
        s = ''.join(rng.choice(chars) for _ in range(length))
        strings.add(s)
        attempts += 1

    # If we couldn't get enough unique strings, just add more (may have duplicates)
    while len(strings) < n:
        length = rng.randint(min_length, max_length)
        s = ''.join(rng.choice(chars) for _ in range(length))
        strings.add(s)

    return list(strings)


def get_benchmark_sizes(num_steps: int = 20) -> List[int]:
    """
    Get the standard benchmark sizes from 1 to 1M in logarithmic scale.

    Args:
        num_steps: Number of size steps

    Returns:
        List of sizes
    """
    return generate_logarithmic_sizes(1, 1_000_000, num_steps)


class DataGenerator:
    """
    Generates test data for benchmarking without caching to save memory.
    Uses deterministic seeding for reproducibility.
    """

    def __init__(self, seed: int = 42, min_length: int = 1, max_length: int = 200):
        """
        Initialize the data generator.

        Args:
            seed: Random seed for reproducibility
            min_length: Minimum string length
            max_length: Maximum string length
        """
        self.seed = seed
        self.min_length = min_length
        self.max_length = max_length

    def get_strings(self, n: int) -> List[str]:
        """
        Get a list of n random strings (regenerated each time).

        For a given n with the same seed, always returns the same list.

        Args:
            n: Number of strings

        Returns:
            List of n random strings
        """
        # Use a deterministic seed based on n so same n always gives same strings
        return generate_string_list(
            n,
            min_length=self.min_length,
            max_length=self.max_length,
            seed=self.seed,
            unique=False  # Don't enforce uniqueness - saves memory and time
        )

    def get_random_valid_string(self, strings: List[str], rng: random.Random = None) -> str:
        """
        Get a random string from the list.

        Args:
            strings: List of valid strings
            rng: Random number generator

        Returns:
            A randomly selected string from the list
        """
        if rng is None:
            rng = random.Random()
        return rng.choice(strings)

    def get_random_indices(self, n: int, count: int, seed: int = None) -> List[int]:
        """
        Get random indices for selecting validation strings.

        Args:
            n: Size of the string list
            count: Number of indices to generate
            seed: Random seed

        Returns:
            List of random indices
        """
        rng = random.Random(seed if seed is not None else self.seed + 1000)
        return [rng.randint(0, n - 1) for _ in range(count)]
