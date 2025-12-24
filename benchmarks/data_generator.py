"""
Data generation utilities for benchmarking.

Generates random strings with configurable parameters for benchmarking parsers.
Uses numpy for efficient generation.
"""

import math
from typing import List
import numpy as np


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


def generate_string_list(n: int, min_length: int = 1, max_length: int = 200,
                         seed: int = None) -> List[str]:
    """
    Generate a list of n random strings using numpy for efficiency.

    Args:
        n: Number of strings to generate
        min_length: Minimum string length (inclusive)
        max_length: Maximum string length (inclusive)
        seed: Random seed for reproducibility

    Returns:
        List of random strings
    """
    rng = np.random.default_rng(seed)

    # ASCII letters + digits as numpy array for fast indexing
    chars = np.array(list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'))

    # Generate all lengths at once
    lengths = rng.integers(min_length, max_length + 1, size=n)

    # Generate strings
    strings = []
    for length in lengths:
        indices = rng.integers(0, len(chars), size=length)
        strings.append(''.join(chars[indices]))

    return strings


def get_benchmark_sizes(num_steps: int = 20) -> List[int]:
    """
    Get the standard benchmark sizes from 1 to 1M in logarithmic scale.

    Args:
        num_steps: Number of size steps

    Returns:
        List of sizes
    """
    return generate_logarithmic_sizes(1, 1_000_000, num_steps)
