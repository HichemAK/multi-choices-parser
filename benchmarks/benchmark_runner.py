"""
Benchmark runner for construction and validation benchmarks.

Spawns separate processes for each measurement to ensure clean memory readings.
"""

import json
import subprocess
import sys
import os
from typing import List, Dict
from dataclasses import dataclass, field

from parser_interface import list_available_parsers
from data_generator import get_benchmark_sizes


def compute_stats(values: List[float]) -> Dict[str, float]:
    """Compute statistics for a list of values."""
    if not values:
        return {'mean': 0, 'std': 0, 'ci_low': 0, 'ci_high': 0, 'n': 0}

    n = len(values)
    mean = sum(values) / n

    if n > 1:
        variance = sum((x - mean) ** 2 for x in values) / (n - 1)
        std = variance ** 0.5
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

    def construction_time_stats(self) -> Dict[str, float]:
        return compute_stats(self.construction_times)

    def construction_memory_stats(self) -> Dict[str, float]:
        return compute_stats([float(x) for x in self.construction_memories])

    def validation_time_stats(self) -> Dict[str, float]:
        return compute_stats(self.validation_times)

    def validation_memory_stats(self) -> Dict[str, float]:
        return compute_stats([float(x) for x in self.validation_memories])


class BenchmarkRunner:
    """Runs benchmarks using subprocess for each measurement."""

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
        self.parsers = parsers or list_available_parsers()
        self.sizes = sizes or get_benchmark_sizes(num_steps)
        self.construction_repeats = construction_repeats
        self.validation_repeats = validation_repeats
        self.seed = seed
        self.min_string_length = min_string_length
        self.max_string_length = max_string_length
        self.verbose = verbose
        self.results: Dict[str, Dict[int, BenchmarkResult]] = {}

        # Path to worker script
        self.worker_script = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'benchmark_worker.py'
        )

    def _log(self, msg: str):
        if self.verbose:
            print(msg, flush=True)

    def _run_worker(self, parser_name: str, size: int,
                    repeat_seed: int = 0) -> dict:
        """Run a single benchmark in a subprocess."""
        cmd = [
            sys.executable,
            self.worker_script,
            '--parser', parser_name,
            '--size', str(size),
            '--seed', str(self.seed + repeat_seed),
            '--min-length', str(self.min_string_length),
            '--max-length', str(self.max_string_length),
            '--num-queries', str(self.validation_repeats),
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            raise RuntimeError(f"Worker failed: {result.stderr}")

        return json.loads(result.stdout.strip())

    def run_all_benchmarks(self) -> Dict[str, Dict[int, BenchmarkResult]]:
        """Run all benchmarks for all parsers and sizes."""
        self.results = {parser: {} for parser in self.parsers}
        total_sizes = len(self.sizes)

        for size_idx, size in enumerate(self.sizes):
            self._log(f"\n{'='*60}")
            self._log(f"Size: {size:,} ({size_idx + 1}/{total_sizes})")
            self._log(f"{'='*60}")

            for parser_name in self.parsers:
                self._log(f"\n  Parser: {parser_name}")
                result = BenchmarkResult(parser_name=parser_name, list_size=size)

                # Run combined benchmarks (construction + validation)
                self._log(f"    Running {self.construction_repeats} repeats ({self.validation_repeats} queries each)...")
                for i in range(self.construction_repeats):
                    data = self._run_worker(parser_name, size, repeat_seed=i)
                    result.construction_times.append(data['time_construction'])
                    result.construction_memories.append(data['memory_construction'])
                    result.validation_times.append(data['time_validation'] / self.validation_repeats)
                    result.validation_memories.append(data['memory_validation'])

                self.results[parser_name][size] = result

                # Print summary
                c_stats = result.construction_time_stats()
                v_stats = result.validation_time_stats()
                m_stats = result.construction_memory_stats()
                vm_stats = result.validation_memory_stats()


                self._log(f"    -> Construction: {c_stats['mean']*1000:.3f}ms (+/- {c_stats['std']*1000:.3f}ms)")
                self._log(f"    -> Validation: {v_stats['mean']*1e6:.3f}us (+/- {v_stats['std']*1e6:.3f}us) per query")
                self._log(f"    -> Memory (Construction): {m_stats['mean']/1024:.2f}KB (+/- {m_stats['std']/1024:.2f}KB)")
                self._log(f"    -> Memory (Validation): {vm_stats['mean']/1024:.2f}KB (+/- {vm_stats['std']/1024:.2f}KB)")

        return self.results

    def get_results_dataframe(self):
        """Convert results to a pandas DataFrame."""
        import pandas as pd

        rows = []
        for parser_name, size_results in self.results.items():
            for size, result in size_results.items():
                c_time = result.construction_time_stats()
                c_mem = result.construction_memory_stats()
                v_time = result.validation_time_stats()
                v_mem = result.validation_memory_stats()

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
                    'validation_memory_mean': v_mem['mean'],
                    'validation_memory_std': v_mem['std'],
                    'validation_memory_ci_low': v_mem['ci_low'],
                    'validation_memory_ci_high': v_mem['ci_high'],
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
