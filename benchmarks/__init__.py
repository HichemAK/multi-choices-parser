"""
Benchmark suite for multi-choices-parser.

This package provides tools for benchmarking parser implementations
with focus on construction time, memory usage, and validation performance.

Modules:
    parser_interface: Abstract interface for parser implementations
    data_generator: Random string generation utilities
    benchmark_runner: Core benchmarking logic
    plotting: Visualization with confidence intervals

Usage:
    python run_benchmarks.py --help
"""

from .parser_interface import (
    ParserInterface,
    MultiChoicesParserWrapper,
    SetBasedParser,
    TrieParser,
    AVAILABLE_PARSERS,
    get_parser_class,
    list_available_parsers,
)

from .data_generator import (
    DataGenerator,
    generate_logarithmic_sizes,
    generate_random_string,
    generate_string_list,
    generate_string_generator,
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
    'MultiChoicesParserWrapper',
    'SetBasedParser',
    'TrieParser',
    'AVAILABLE_PARSERS',
    'get_parser_class',
    'list_available_parsers',
    # Data generation
    'DataGenerator',
    'generate_logarithmic_sizes',
    'generate_random_string',
    'generate_string_list',
    'generate_string_generator',
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
