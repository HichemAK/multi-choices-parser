#!/usr/bin/env python3
"""
Main script to run all benchmarks and generate plots.

Usage:
    python run_benchmarks.py [options]

Examples:
    # Run all benchmarks with default settings
    python run_benchmarks.py

    # Run quick benchmarks (fewer sizes and repeats)
    python run_benchmarks.py --quick

    # Run only specific parsers
    python run_benchmarks.py --parsers multi_choices set_based

    # Save results to a specific directory
    python run_benchmarks.py --output-dir ./results

    # Load existing results and regenerate plots
    python run_benchmarks.py --load-results ./results/benchmark_results.csv --plot-only
"""

import argparse
import os
import sys
from datetime import datetime

from benchmark_runner import BenchmarkRunner
from plotting import plot_all_benchmarks, create_combined_figure
from parser_interface import list_available_parsers
from data_generator import get_benchmark_sizes


def parse_args():
    parser = argparse.ArgumentParser(
        description='Run parser benchmarks and generate plots',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '--parsers',
        nargs='+',
        default=None,
        help=f'Parsers to benchmark (default: all). Available: {list_available_parsers()}'
    )

    parser.add_argument(
        '--num-steps',
        type=int,
        default=10,
        help='Number of size steps in logarithmic scale (default: 10)'
    )

    parser.add_argument(
        '--construction-repeats',
        type=int,
        default=10,
        help='Number of construction benchmark repeats (default: 10)'
    )

    parser.add_argument(
        '--validation-repeats',
        type=int,
        default=100,
        help='Number of validation queries per size (default: 100)'
    )

    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help='Random seed for reproducibility (default: 42)'
    )

    parser.add_argument(
        '--min-string-length',
        type=int,
        default=1,
        help='Minimum string length (default: 1)'
    )

    parser.add_argument(
        '--max-string-length',
        type=int,
        default=200,
        help='Maximum string length (default: 200)'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='./results',
        help='Directory to save results and plots (default: ./results)'
    )

    parser.add_argument(
        '--quick',
        action='store_true',
        help='Run quick benchmarks with fewer sizes and repeats'
    )

    parser.add_argument(
        '--load-results',
        type=str,
        default=None,
        help='Load existing results from CSV file instead of running benchmarks'
    )

    parser.add_argument(
        '--plot-only',
        action='store_true',
        help='Only generate plots (requires --load-results)'
    )

    parser.add_argument(
        '--no-show',
        action='store_true',
        help='Do not display plots (only save to files)'
    )

    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Reduce output verbosity'
    )

    return parser.parse_args()


def main():
    args = parse_args()

    # Apply quick mode settings
    if args.quick:
        args.num_steps = 10
        args.construction_repeats = 5
        args.validation_repeats = 100

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    # Generate timestamp for file naming
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    if args.load_results:
        # Load existing results
        import pandas as pd
        print(f"Loading results from {args.load_results}")
        df = pd.read_csv(args.load_results)
    else:
        if args.plot_only:
            print("Error: --plot-only requires --load-results")
            sys.exit(1)

        # Run benchmarks
        print("="*60)
        print("Parser Benchmark Suite")
        print("="*60)
        print(f"\nConfiguration:")
        print(f"  Parsers: {args.parsers or 'all'}")
        print(f"  Size steps: {args.num_steps}")
        print(f"  Construction repeats: {args.construction_repeats}")
        print(f"  Validation queries: {args.validation_repeats}")
        print(f"  String length: {args.min_string_length}-{args.max_string_length}")
        print(f"  Seed: {args.seed}")
        print(f"  Output: {args.output_dir}")
        print()

        # Show size steps
        sizes = get_benchmark_sizes(args.num_steps)
        print(f"Size steps: {sizes}")
        print()

        runner = BenchmarkRunner(
            parsers=args.parsers,
            num_steps=args.num_steps,
            construction_repeats=args.construction_repeats,
            validation_repeats=args.validation_repeats,
            seed=args.seed,
            min_string_length=args.min_string_length,
            max_string_length=args.max_string_length,
            verbose=not args.quiet
        )

        # Run all benchmarks
        runner.run_all_benchmarks()

        # Get results as DataFrame
        df = runner.get_results_dataframe()

        # Save results
        results_path = os.path.join(args.output_dir, f'benchmark_results_{timestamp}.csv')
        df.to_csv(results_path, index=False)
        print(f"\nResults saved to {results_path}")

        # Also save with a fixed name for easy access
        latest_path = os.path.join(args.output_dir, 'benchmark_results.csv')
        df.to_csv(latest_path, index=False)
        print(f"Latest results also saved to {latest_path}")

    # Generate plots
    print("\nGenerating plots...")

    # Individual plots
    plot_all_benchmarks(
        df,
        parsers=args.parsers,
        output_dir=args.output_dir,
        prefix=f'benchmark_{timestamp}',
        show=not args.no_show
    )

    # Combined figure
    combined_path = os.path.join(args.output_dir, f'benchmark_combined_{timestamp}.png')
    create_combined_figure(
        df,
        parsers=args.parsers,
        output_path=combined_path
    )

    # Save with fixed names for easy access
    plot_all_benchmarks(
        df,
        parsers=args.parsers,
        output_dir=args.output_dir,
        prefix='benchmark',
        show=False
    )

    create_combined_figure(
        df,
        parsers=args.parsers,
        output_path=os.path.join(args.output_dir, 'benchmark_combined.png')
    )

    print("\nBenchmark complete!")
    print(f"Results saved to: {args.output_dir}")


if __name__ == '__main__':
    main()
