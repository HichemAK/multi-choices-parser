"""
Benchmark suite for multi-choices-parser.

This package provides tools for benchmarking parser implementations
with focus on construction time, memory usage, and validation performance.

Modules:
    parser_interface: Abstract interface for parser implementations
    data_generator: Random string generation utilities
    benchmark_runner: Core benchmarking logic (uses subprocesses)
    benchmark_worker: Worker process for isolated measurements
    plotting: Visualization with confidence intervals

Usage:
    uv run python benchmarks/run_benchmarks.py --help
"""

from .parser_interface import (
    ParserInterface,
    MultiChoicesParserTrieWrapper,
    TrieParser,
    AVAILABLE_PARSERS,
    get_parser_class,
    list_available_parsers,
)

from .data_generator import (
    generate_logarithmic_sizes,
    generate_string_list,
    get_benchmark_sizes,
)

from .benchmark_runner import (
    BenchmarkResult,
    BenchmarkRunner,
)

from .plotting import (
    plot_construction_time,
    plot_construction_memory,
    plot_validation_time,
    plot_all_benchmarks,
    create_combined_figure,
)

__all__ = [
    # Parser interface
    'ParserInterface',
    'MultiChoicesParserTrieWrapper',
    'TrieParser',
    'AVAILABLE_PARSERS',
    'get_parser_class',
    'list_available_parsers',
    # Data generation
    'generate_logarithmic_sizes',
    'generate_string_list',
    'get_benchmark_sizes',
    # Benchmark runner
    'BenchmarkResult',
    'BenchmarkRunner',
    # Plotting
    'plot_construction_time',
    'plot_construction_memory',
    'plot_validation_time',
    'plot_all_benchmarks',
    'create_combined_figure',
]
