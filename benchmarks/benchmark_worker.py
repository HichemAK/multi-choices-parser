#!/usr/bin/env python3
"""
Worker script for running individual benchmark measurements in isolation.

This script is spawned as a subprocess to ensure clean memory measurements.
It performs a single benchmark (construction or validation) and reports results.
"""

import argparse
import json
import sys
import time
import tracemalloc

import numpy as np

from data_generator import generate_string_list
from parser_interface import get_parser_class


def run_benchmark(parser_name: str, size: int, seed: int,
                                min_length: int, max_length: int, num_queries: int) -> dict:
    """Run construction benchmark and return results."""
    # Generate strings
    strings = generate_string_list(size, min_length, max_length, seed)
    # Select random strings to validate
    rng = np.random.default_rng(seed + 1000)
    indices = rng.integers(0, len(strings), size=num_queries)
    query_strings = [strings[i] for i in indices]

    parser_class = get_parser_class(parser_name)

    # Measure construction
    tracemalloc.start()
    start_time = time.perf_counter()

    parser = parser_class(strings)

    end_time = time.perf_counter()
    time_construction = end_time - start_time

    current, peak_construction = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # Measure validation (reusing the same parser instance)
    tracemalloc.start()
    start_time = time.perf_counter()

    for s in query_strings:
        parser.reset()
        result = validate_string(parser, s)
        if not result:
            raise RuntimeError(f"Parser should accept '{s}'")

    end_time = time.perf_counter()
    time_validation = end_time - start_time
    current, peak_validation = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        'parser': parser_name,
        'size': size,
        'time_construction': time_construction,
        'memory_construction': peak_construction,
        'time_validation': time_validation,
        'memory_validation': peak_validation,
    }


def validate_string(parser, string: str) -> bool:
    """Validate a string using step-based API."""
    for char in string:
        if parser.finished:
            return False
        parser.step(char)

    # For MultiChoicesParser, we need to check if END is valid
    # For TrieParser, we call complete()
    if hasattr(parser, 'complete'):
        parser.complete()
        return parser.success
    else:
        # MultiChoicesParser: check if end symbol is in next()
        if parser.finished:
            return False
        return parser._end_symb in parser._parser.next()


def main():
    parser = argparse.ArgumentParser(description='Benchmark worker process')
    parser.add_argument('--parser', required=False, default='multi_choices')
    parser.add_argument('--size', type=int, required=False, default=1000)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--min-length', type=int, default=1)
    parser.add_argument('--max-length', type=int, default=200)
    parser.add_argument('--num-queries', type=int, default=1000)

    args = parser.parse_args()

    try:
        result = run_benchmark(
            args.parser, args.size, args.seed,
            args.min_length, args.max_length, args.num_queries
        )
        print(json.dumps(result))

    except Exception as e:
        error_result = {
            'type': 'error',
            'error': str(e),
        }
        print(json.dumps(error_result))
        sys.exit(1)


if __name__ == '__main__':
    main()
