"""
Benchmark runner for construction and validation benchmarks.

Measures time and memory for parser construction and string validation.
Memory-optimized: processes one size at a time and cleans up between runs.
"""

import time
import gc
import tracemalloc
import random
from typing import List, Dict, Any, Optional, Tuple, Type
from dataclasses import dataclass, field

from parser_interface import ParserInterface, get_parser_class, list_available_parsers
from data_generator import DataGenerator, get_benchmark_sizes, generate_string_list


def compute_stats(values: List[float]) -> Dict[str, float]:
    """Compute statistics for a list of values without numpy for small lists."""
    if not values:
        return {'mean': 0, 'std': 0, 'ci_low': 0, 'ci_high': 0, 'n': 0}

    n = len(values)
    mean = sum(values) / n

    if n > 1:
        variance = sum((x - mean) ** 2 for x in values) / (n - 1)
        std = variance ** 0.5

        # 95% confidence interval using t-distribution approximation
        # For n >= 20, t is approximately 2.0
        t_critical = 2.093 if n == 20 else 2.0
        margin = t_critical * (std / (n ** 0.5))
    else:
        std = 0
        margin = 0

    return {
        'mean': mean,
        'std': std,
        'ci_low': mean - margin,
        'ci_high': mean + margin,
        'n': n
    }


@dataclass
class BenchmarkResult:
    """Result of a single benchmark run."""
    parser_name: str
    list_size: int
    construction_times: List[float] = field(default_factory=list)
    construction_memories: List[int] = field(default_factory=list)
    validation_times: List[float] = field(default_factory=list)
    validation_memories: List[int] = field(default_factory=list)

    def add_construction_sample(self, time_sec: float, memory_bytes: int):
        self.construction_times.append(time_sec)
        self.construction_memories.append(memory_bytes)

    def add_validation_sample(self, time_sec: float, memory_bytes: int):
        self.validation_times.append(time_sec)
        self.validation_memories.append(memory_bytes)

    def construction_time_stats(self) -> Dict[str, float]:
        """Return mean, std, and confidence interval for construction time."""
        return compute_stats(self.construction_times)

    def construction_memory_stats(self) -> Dict[str, float]:
        """Return mean, std, and confidence interval for construction memory."""
        return compute_stats([float(x) for x in self.construction_memories])

    def validation_time_stats(self) -> Dict[str, float]:
        """Return mean, std, and confidence interval for validation time."""
        return compute_stats(self.validation_times)

    def validation_memory_stats(self) -> Dict[str, float]:
        """Return mean, std, and confidence interval for validation memory."""
        return compute_stats([float(x) for x in self.validation_memories])


class BenchmarkRunner:
    """Runs benchmarks for parser implementations."""

    def __init__(
        self,
        parsers: List[str] = None,
        sizes: List[int] = None,
        num_steps: int = 20,
        construction_repeats: int = 20,
        validation_repeats: int = 1000,
        seed: int = 42,
        min_string_length: int = 1,
        max_string_length: int = 200,
        verbose: bool = True
    ):
        """
        Initialize the benchmark runner.

        Args:
            parsers: List of parser names to benchmark (default: all available)
            sizes: List of sizes to test (default: logarithmic from 1 to 1M)
            num_steps: Number of size steps if sizes not specified
            construction_repeats: Number of times to repeat construction benchmark
            validation_repeats: Number of validation queries per size
            seed: Random seed for reproducibility
            min_string_length: Minimum string length
            max_string_length: Maximum string length
            verbose: Print progress information
        """
        self.parsers = parsers or list_available_parsers()
        self.sizes = sizes or get_benchmark_sizes(num_steps)
        self.construction_repeats = construction_repeats
        self.validation_repeats = validation_repeats
        self.seed = seed
        self.verbose = verbose

        self.data_generator = DataGenerator(
            seed=seed,
            min_length=min_string_length,
            max_length=max_string_length
        )

        self.results: Dict[str, Dict[int, BenchmarkResult]] = {}

    def _log(self, msg: str):
        """Print message if verbose mode is enabled."""
        if self.verbose:
            print(msg)

    def _measure_construction(
        self,
        parser_class: Type[ParserInterface],
        strings: List[str]
    ) -> Tuple[float, int]:
        """
        Measure construction time and memory for a parser.

        Args:
            parser_class: Parser class to instantiate
            strings: List of strings to construct parser with

        Returns:
            Tuple of (time_seconds, memory_bytes)
        """
        gc.collect()
        gc.disable()

        tracemalloc.start()
        start_time = time.perf_counter()

        parser = parser_class(strings)

        end_time = time.perf_counter()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        gc.enable()

        elapsed = end_time - start_time
        # Use parser's own memory estimate if available
        try:
            memory = parser.get_memory_bytes()
        except Exception:
            memory = peak

        return elapsed, memory

    def _measure_validation(
        self,
        parser: ParserInterface,
        strings: List[str],
        num_queries: int
    ) -> Tuple[float, int]:
        """
        Measure validation time for random valid strings.

        Args:
            parser: Parser instance
            strings: List of valid strings to query from
            num_queries: Number of validation queries

        Returns:
            Tuple of (avg_time_per_query_seconds, memory_bytes)
        """
        rng = random.Random(self.seed)

        # Pre-select strings to validate
        query_strings = [rng.choice(strings) for _ in range(num_queries)]

        gc.collect()
        gc.disable()

        tracemalloc.start()
        start_time = time.perf_counter()

        for s in query_strings:
            result = parser.accepts(s)
            assert result, f"Parser should accept '{s}'"

        end_time = time.perf_counter()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        gc.enable()

        elapsed = end_time - start_time
        avg_time = elapsed / num_queries

        return avg_time, peak

    def run_construction_benchmark(self, parser_name: str, size: int) -> BenchmarkResult:
        """
        Run construction benchmark for a specific parser and size.

        Args:
            parser_name: Name of the parser to benchmark
            size: Number of strings in the list

        Returns:
            BenchmarkResult with construction measurements
        """
        parser_class = get_parser_class(parser_name)
        strings = self.data_generator.get_strings(size)

        result = BenchmarkResult(parser_name=parser_name, list_size=size)

        for i in range(self.construction_repeats):
            time_sec, memory_bytes = self._measure_construction(parser_class, strings)
            result.add_construction_sample(time_sec, memory_bytes)

            if self.verbose and (i + 1) % 5 == 0:
                self._log(f"    Construction repeat {i + 1}/{self.construction_repeats}")

        return result

    def run_validation_benchmark(
        self,
        parser_name: str,
        size: int,
        result: BenchmarkResult = None
    ) -> BenchmarkResult:
        """
        Run validation benchmark for a specific parser and size.

        Args:
            parser_name: Name of the parser to benchmark
            size: Number of strings in the list
            result: Existing result to add to (optional)

        Returns:
            BenchmarkResult with validation measurements
        """
        parser_class = get_parser_class(parser_name)
        strings = self.data_generator.get_strings(size)

        if result is None:
            result = BenchmarkResult(parser_name=parser_name, list_size=size)

        # Construct parser once for validation
        parser = parser_class(strings)

        # Run validation queries
        avg_time, memory = self._measure_validation(
            parser, strings, self.validation_repeats
        )

        # Store as single aggregate measurement
        result.validation_times.append(avg_time)
        result.validation_memories.append(memory)

        return result

    def run_all_benchmarks(self) -> Dict[str, Dict[int, BenchmarkResult]]:
        """
        Run all benchmarks for all parsers and sizes.

        Memory-optimized: generates strings once per size, benchmarks all parsers,
        then frees memory before moving to next size.

        Returns:
            Nested dict: results[parser_name][size] = BenchmarkResult
        """
        self.results = {parser: {} for parser in self.parsers}

        total_sizes = len(self.sizes)

        for size_idx, size in enumerate(self.sizes):
            self._log(f"\n{'='*60}")
            self._log(f"Size: {size:,} ({size_idx + 1}/{total_sizes})")
            self._log(f"{'='*60}")

            # Generate strings once for this size
            strings = self.data_generator.get_strings(size)

            for parser_name in self.parsers:
                self._log(f"\n  Parser: {parser_name}")

                parser_class = get_parser_class(parser_name)
                result = BenchmarkResult(parser_name=parser_name, list_size=size)

                # Run construction benchmark
                for i in range(self.construction_repeats):
                    time_sec, memory_bytes = self._measure_construction(parser_class, strings)
                    result.add_construction_sample(time_sec, memory_bytes)
                    # Force cleanup after each construction
                    gc.collect()

                # Run validation benchmark (construct parser once)
                parser = parser_class(strings)
                avg_time, memory = self._measure_validation(
                    parser, strings, self.validation_repeats
                )
                result.validation_times.append(avg_time)
                result.validation_memories.append(memory)

                # Store result
                self.results[parser_name][size] = result

                # Print summary
                c_stats = result.construction_time_stats()
                v_stats = result.validation_time_stats()
                m_stats = result.construction_memory_stats()

                self._log(f"    Construction: {c_stats['mean']*1000:.3f}ms (+/- {c_stats['std']*1000:.3f}ms)")
                self._log(f"    Validation: {v_stats['mean']*1e6:.3f}us per query")
                self._log(f"    Memory: {m_stats['mean']/1024:.2f}KB")

                # Cleanup parser
                del parser
                gc.collect()

            # Free strings memory before next size
            del strings
            gc.collect()

        return self.results

    def get_results_dataframe(self):
        """
        Convert results to a pandas DataFrame.

        Returns:
            DataFrame with benchmark results
        """
        import pandas as pd

        rows = []
        for parser_name, size_results in self.results.items():
            for size, result in size_results.items():
                c_time = result.construction_time_stats()
                c_mem = result.construction_memory_stats()
                v_time = result.validation_time_stats()

                rows.append({
                    'parser': parser_name,
                    'size': size,
                    'construction_time_mean': c_time['mean'],
                    'construction_time_std': c_time['std'],
                    'construction_time_ci_low': c_time['ci_low'],
                    'construction_time_ci_high': c_time['ci_high'],
                    'construction_memory_mean': c_mem['mean'],
                    'construction_memory_std': c_mem['std'],
                    'construction_memory_ci_low': c_mem['ci_low'],
                    'construction_memory_ci_high': c_mem['ci_high'],
                    'validation_time_mean': v_time['mean'],
                    'validation_time_std': v_time['std'],
                    'validation_time_ci_low': v_time['ci_low'],
                    'validation_time_ci_high': v_time['ci_high'],
                })

        return pd.DataFrame(rows)

    def save_results(self, filepath: str):
        """Save results to a CSV file."""
        df = self.get_results_dataframe()
        df.to_csv(filepath, index=False)
        self._log(f"Results saved to {filepath}")

    def load_results(self, filepath: str):
        """Load results from a CSV file."""
        import pandas as pd
        return pd.read_csv(filepath)
