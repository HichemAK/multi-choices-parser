"""
Plotting utilities for benchmark visualization.

Creates plots with confidence intervals for construction and validation benchmarks.
"""

import os
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


# Color palette for different parsers
PARSER_COLORS = {
    'multi_choices': '#2ecc71',      # Green
    'set_based': '#3498db',          # Blue
    'python_trie': '#e74c3c',        # Red
    'marisa_trie': '#9b59b6',        # Purple
    'datrie': '#f39c12',             # Orange
    'pygtrie': '#1abc9c',            # Teal
}

# Line styles for different parsers
PARSER_LINESTYLES = {
    'multi_choices': '-',
    'set_based': '--',
    'python_trie': '-.',
    'marisa_trie': ':',
    'datrie': '-',
    'pygtrie': '--',
}

# Markers for different parsers
PARSER_MARKERS = {
    'multi_choices': 'o',
    'set_based': 's',
    'python_trie': '^',
    'marisa_trie': 'D',
    'datrie': 'v',
    'pygtrie': 'p',
}


def get_parser_style(parser_name: str) -> Dict:
    """Get plot style for a parser."""
    return {
        'color': PARSER_COLORS.get(parser_name, '#7f8c8d'),
        'linestyle': PARSER_LINESTYLES.get(parser_name, '-'),
        'marker': PARSER_MARKERS.get(parser_name, 'o'),
        'markersize': 6,
        'linewidth': 2,
    }


def format_size_axis(ax, axis: str = 'x'):
    """Format axis for size (1, 10, 100, 1K, 10K, 100K, 1M)."""
    def size_formatter(x, p):
        if x >= 1_000_000:
            return f'{x/1_000_000:.0f}M'
        elif x >= 1_000:
            return f'{x/1_000:.0f}K'
        else:
            return f'{x:.0f}'

    if axis == 'x':
        ax.set_xscale('log')
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(size_formatter))
    else:
        ax.set_yscale('log')
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(size_formatter))


def format_time_axis(ax, axis: str = 'y', unit: str = 'auto'):
    """Format axis for time values."""
    def time_formatter(x, p):
        if x >= 1:
            return f'{x:.1f}s'
        elif x >= 0.001:
            return f'{x*1000:.1f}ms'
        elif x >= 0.000001:
            return f'{x*1_000_000:.1f}us'
        else:
            return f'{x*1_000_000_000:.1f}ns'

    if axis == 'y':
        ax.set_yscale('log')
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(time_formatter))
    else:
        ax.set_xscale('log')
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(time_formatter))


def format_memory_axis(ax, axis: str = 'y'):
    """Format axis for memory values (bytes)."""
    def memory_formatter(x, p):
        if x >= 1_000_000_000:
            return f'{x/1_000_000_000:.1f}GB'
        elif x >= 1_000_000:
            return f'{x/1_000_000:.1f}MB'
        elif x >= 1_000:
            return f'{x/1_000:.1f}KB'
        else:
            return f'{x:.0f}B'

    if axis == 'y':
        ax.set_yscale('log')
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(memory_formatter))
    else:
        ax.set_xscale('log')
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(memory_formatter))


def plot_with_confidence_interval(
    ax,
    x: np.ndarray,
    y_mean: np.ndarray,
    y_ci_low: np.ndarray,
    y_ci_high: np.ndarray,
    label: str,
    style: Dict,
    alpha: float = 0.2
):
    """Plot a line with confidence interval shading."""
    # Plot the main line
    ax.plot(x, y_mean, label=label, **style)

    # Plot the confidence interval
    ax.fill_between(
        x, y_ci_low, y_ci_high,
        alpha=alpha,
        color=style['color']
    )


def plot_construction_time(
    df: pd.DataFrame,
    parsers: List[str] = None,
    title: str = 'Construction Time vs List Size',
    output_path: str = None,
    figsize: Tuple[int, int] = (10, 6)
) -> plt.Figure:
    """
    Plot construction time vs list size with confidence intervals.

    Args:
        df: DataFrame with benchmark results
        parsers: List of parsers to include (default: all)
        title: Plot title
        output_path: Path to save the figure (optional)
        figsize: Figure size

    Returns:
        matplotlib Figure
    """
    fig, ax = plt.subplots(figsize=figsize)

    if parsers is None:
        parsers = df['parser'].unique()

    for parser in parsers:
        parser_df = df[df['parser'] == parser].sort_values('size')
        style = get_parser_style(parser)

        plot_with_confidence_interval(
            ax,
            parser_df['size'].values,
            parser_df['construction_time_mean'].values,
            parser_df['construction_time_ci_low'].values,
            parser_df['construction_time_ci_high'].values,
            label=parser,
            style=style
        )

    format_size_axis(ax, 'x')
    format_time_axis(ax, 'y')

    ax.set_xlabel('Number of Strings')
    ax.set_ylabel('Construction Time')
    ax.set_title(title)
    ax.legend(loc='upper left')
    ax.grid(True, alpha=0.3, which='both')

    plt.tight_layout()

    if output_path:
        fig.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved plot to {output_path}")

    return fig


def plot_construction_memory(
    df: pd.DataFrame,
    parsers: List[str] = None,
    title: str = 'Memory Consumption vs List Size',
    output_path: str = None,
    figsize: Tuple[int, int] = (10, 6)
) -> plt.Figure:
    """
    Plot memory consumption vs list size with confidence intervals.

    Args:
        df: DataFrame with benchmark results
        parsers: List of parsers to include (default: all)
        title: Plot title
        output_path: Path to save the figure (optional)
        figsize: Figure size

    Returns:
        matplotlib Figure
    """
    fig, ax = plt.subplots(figsize=figsize)

    if parsers is None:
        parsers = df['parser'].unique()

    for parser in parsers:
        parser_df = df[df['parser'] == parser].sort_values('size')
        style = get_parser_style(parser)

        plot_with_confidence_interval(
            ax,
            parser_df['size'].values,
            parser_df['construction_memory_mean'].values,
            parser_df['construction_memory_ci_low'].values,
            parser_df['construction_memory_ci_high'].values,
            label=parser,
            style=style
        )

    format_size_axis(ax, 'x')
    format_memory_axis(ax, 'y')

    ax.set_xlabel('Number of Strings')
    ax.set_ylabel('Memory Consumption')
    ax.set_title(title)
    ax.legend(loc='upper left')
    ax.grid(True, alpha=0.3, which='both')

    plt.tight_layout()

    if output_path:
        fig.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved plot to {output_path}")

    return fig


def plot_validation_time(
    df: pd.DataFrame,
    parsers: List[str] = None,
    title: str = 'Validation Time vs List Size',
    output_path: str = None,
    figsize: Tuple[int, int] = (10, 6)
) -> plt.Figure:
    """
    Plot validation time per query vs list size with confidence intervals.

    Args:
        df: DataFrame with benchmark results
        parsers: List of parsers to include (default: all)
        title: Plot title
        output_path: Path to save the figure (optional)
        figsize: Figure size

    Returns:
        matplotlib Figure
    """
    fig, ax = plt.subplots(figsize=figsize)

    if parsers is None:
        parsers = df['parser'].unique()

    for parser in parsers:
        parser_df = df[df['parser'] == parser].sort_values('size')
        style = get_parser_style(parser)

        plot_with_confidence_interval(
            ax,
            parser_df['size'].values,
            parser_df['validation_time_mean'].values,
            parser_df['validation_time_ci_low'].values,
            parser_df['validation_time_ci_high'].values,
            label=parser,
            style=style
        )

    format_size_axis(ax, 'x')
    format_time_axis(ax, 'y')

    ax.set_xlabel('Number of Strings')
    ax.set_ylabel('Validation Time (per query)')
    ax.set_title(title)
    ax.legend(loc='upper left')
    ax.grid(True, alpha=0.3, which='both')

    plt.tight_layout()

    if output_path:
        fig.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved plot to {output_path}")

    return fig


def plot_validation_memory(
    df: pd.DataFrame,
    parsers: List[str] = None,
    title: str = 'Validation Memory vs List Size',
    output_path: str = None,
    figsize: Tuple[int, int] = (10, 6)
) -> plt.Figure:
    """
    Plot validation memory consumption vs list size with confidence intervals.

    Args:
        df: DataFrame with benchmark results
        parsers: List of parsers to include (default: all)
        title: Plot title
        output_path: Path to save the figure (optional)
        figsize: Figure size

    Returns:
        matplotlib Figure
    """
    fig, ax = plt.subplots(figsize=figsize)

    if parsers is None:
        parsers = df['parser'].unique()

    for parser in parsers:
        parser_df = df[df['parser'] == parser].sort_values('size')
        style = get_parser_style(parser)

        plot_with_confidence_interval(
            ax,
            parser_df['size'].values,
            parser_df['validation_memory_mean'].values,
            parser_df['validation_memory_ci_low'].values,
            parser_df['validation_memory_ci_high'].values,
            label=parser,
            style=style
        )

    format_size_axis(ax, 'x')
    format_memory_axis(ax, 'y')

    ax.set_xlabel('Number of Strings')
    ax.set_ylabel('Validation Memory')
    ax.set_title(title)
    ax.legend(loc='upper left')
    ax.grid(True, alpha=0.3, which='both')

    plt.tight_layout()

    if output_path:
        fig.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved plot to {output_path}")

    return fig


def plot_all_benchmarks(
    df: pd.DataFrame,
    parsers: List[str] = None,
    output_dir: str = None,
    prefix: str = 'benchmark',
    show: bool = True
) -> Dict[str, plt.Figure]:
    """
    Create all benchmark plots.

    Args:
        df: DataFrame with benchmark results
        parsers: List of parsers to include (default: all)
        output_dir: Directory to save figures (optional)
        prefix: Prefix for output filenames
        show: Whether to display the plots

    Returns:
        Dict of figure name to Figure
    """
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    figures = {}

    # Construction time plot
    output_path = os.path.join(output_dir, f'{prefix}_construction_time.png') if output_dir else None
    figures['construction_time'] = plot_construction_time(
        df, parsers, output_path=output_path
    )

    # Construction memory plot
    output_path = os.path.join(output_dir, f'{prefix}_construction_memory.png') if output_dir else None
    figures['construction_memory'] = plot_construction_memory(
        df, parsers, output_path=output_path
    )

    # Validation time plot
    output_path = os.path.join(output_dir, f'{prefix}_validation_time.png') if output_dir else None
    figures['validation_time'] = plot_validation_time(
        df, parsers, output_path=output_path
    )

    # Validation memory plot
    output_path = os.path.join(output_dir, f'{prefix}_validation_memory.png') if output_dir else None
    figures['validation_memory'] = plot_validation_memory(
        df, parsers, output_path=output_path
    )

    if show:
        plt.show()

    return figures


def create_combined_figure(
    df: pd.DataFrame,
    parsers: List[str] = None,
    output_path: str = None,
    figsize: Tuple[int, int] = (12, 10)
) -> plt.Figure:
    """
    Create a combined figure with all four plots in a 2x2 grid.

    Args:
        df: DataFrame with benchmark results
        parsers: List of parsers to include (default: all)
        output_path: Path to save the figure (optional)
        figsize: Figure size

    Returns:
        matplotlib Figure
    """
    fig, axes = plt.subplots(2, 2, figsize=figsize)

    if parsers is None:
        parsers = df['parser'].unique()

    # Plot 1: Construction Time (top-left)
    ax = axes[0, 0]
    for parser in parsers:
        parser_df = df[df['parser'] == parser].sort_values('size')
        style = get_parser_style(parser)
        plot_with_confidence_interval(
            ax,
            parser_df['size'].values,
            parser_df['construction_time_mean'].values,
            parser_df['construction_time_ci_low'].values,
            parser_df['construction_time_ci_high'].values,
            label=parser,
            style=style
        )
    format_size_axis(ax, 'x')
    format_time_axis(ax, 'y')
    ax.set_xlabel('Number of Strings')
    ax.set_ylabel('Construction Time')
    ax.set_title('Construction Time')
    ax.legend(loc='upper left', fontsize=8)
    ax.grid(True, alpha=0.3, which='both')

    # Plot 2: Construction Memory (top-right)
    ax = axes[0, 1]
    for parser in parsers:
        parser_df = df[df['parser'] == parser].sort_values('size')
        style = get_parser_style(parser)
        plot_with_confidence_interval(
            ax,
            parser_df['size'].values,
            parser_df['construction_memory_mean'].values,
            parser_df['construction_memory_ci_low'].values,
            parser_df['construction_memory_ci_high'].values,
            label=parser,
            style=style
        )
    format_size_axis(ax, 'x')
    format_memory_axis(ax, 'y')
    ax.set_xlabel('Number of Strings')
    ax.set_ylabel('Memory Consumption')
    ax.set_title('Construction Memory')
    ax.legend(loc='upper left', fontsize=8)
    ax.grid(True, alpha=0.3, which='both')

    # Plot 3: Validation Time (bottom-left)
    ax = axes[1, 0]
    for parser in parsers:
        parser_df = df[df['parser'] == parser].sort_values('size')
        style = get_parser_style(parser)
        plot_with_confidence_interval(
            ax,
            parser_df['size'].values,
            parser_df['validation_time_mean'].values,
            parser_df['validation_time_ci_low'].values,
            parser_df['validation_time_ci_high'].values,
            label=parser,
            style=style
        )
    format_size_axis(ax, 'x')
    format_time_axis(ax, 'y')
    ax.set_xlabel('Number of Strings')
    ax.set_ylabel('Validation Time (per query)')
    ax.set_title('Validation Time')
    ax.legend(loc='upper left', fontsize=8)
    ax.grid(True, alpha=0.3, which='both')

    # Plot 4: Validation Memory (bottom-right)
    ax = axes[1, 1]
    for parser in parsers:
        parser_df = df[df['parser'] == parser].sort_values('size')
        style = get_parser_style(parser)
        plot_with_confidence_interval(
            ax,
            parser_df['size'].values,
            parser_df['validation_memory_mean'].values,
            parser_df['validation_memory_ci_low'].values,
            parser_df['validation_memory_ci_high'].values,
            label=parser,
            style=style
        )
    format_size_axis(ax, 'x')
    format_memory_axis(ax, 'y')
    ax.set_xlabel('Number of Strings')
    ax.set_ylabel('Memory Consumption')
    ax.set_title('Validation Memory')
    ax.legend(loc='upper left', fontsize=8)
    ax.grid(True, alpha=0.3, which='both')

    plt.tight_layout()

    if output_path:
        fig.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved combined plot to {output_path}")

    return fig


def create_combined_figure_linear(
    df: pd.DataFrame,
    parsers: List[str] = None,
    output_path: str = None,
    figsize: Tuple[int, int] = (12, 10)
) -> plt.Figure:
    """
    Create a combined figure with all four plots in a 2x2 grid using linear scales.

    Args:
        df: DataFrame with benchmark results
        parsers: List of parsers to include (default: all)
        output_path: Path to save the figure (optional)
        figsize: Figure size

    Returns:
        matplotlib Figure
    """
    fig, axes = plt.subplots(2, 2, figsize=figsize)

    if parsers is None:
        parsers = df['parser'].unique()

    # Plot 1: Construction Time (top-left)
    ax = axes[0, 0]
    for parser in parsers:
        parser_df = df[df['parser'] == parser].sort_values('size')
        style = get_parser_style(parser)
        plot_with_confidence_interval(
            ax,
            parser_df['size'].values,
            parser_df['construction_time_mean'].values,
            parser_df['construction_time_ci_low'].values,
            parser_df['construction_time_ci_high'].values,
            label=parser,
            style=style
        )
    ax.set_xlabel('Number of Strings')
    ax.set_ylabel('Construction Time (s)')
    ax.set_title('Construction Time')
    ax.legend(loc='upper left', fontsize=8)
    ax.grid(True, alpha=0.3)

    # Plot 2: Construction Memory (top-right)
    ax = axes[0, 1]
    for parser in parsers:
        parser_df = df[df['parser'] == parser].sort_values('size')
        style = get_parser_style(parser)
        plot_with_confidence_interval(
            ax,
            parser_df['size'].values,
            parser_df['construction_memory_mean'].values / 1024 / 1024,  # Convert to MB
            parser_df['construction_memory_ci_low'].values / 1024 / 1024,
            parser_df['construction_memory_ci_high'].values / 1024 / 1024,
            label=parser,
            style=style
        )
    ax.set_xlabel('Number of Strings')
    ax.set_ylabel('Memory (MB)')
    ax.set_title('Construction Memory')
    ax.legend(loc='upper left', fontsize=8)
    ax.grid(True, alpha=0.3)

    # Plot 3: Validation Time (bottom-left)
    ax = axes[1, 0]
    for parser in parsers:
        parser_df = df[df['parser'] == parser].sort_values('size')
        style = get_parser_style(parser)
        plot_with_confidence_interval(
            ax,
            parser_df['size'].values,
            parser_df['validation_time_mean'].values * 1e6,  # Convert to microseconds
            parser_df['validation_time_ci_low'].values * 1e6,
            parser_df['validation_time_ci_high'].values * 1e6,
            label=parser,
            style=style
        )
    ax.set_xlabel('Number of Strings')
    ax.set_ylabel('Validation Time (µs per query)')
    ax.set_title('Validation Time')
    ax.legend(loc='upper left', fontsize=8)
    ax.grid(True, alpha=0.3)

    # Plot 4: Validation Memory (bottom-right)
    ax = axes[1, 1]
    for parser in parsers:
        parser_df = df[df['parser'] == parser].sort_values('size')
        style = get_parser_style(parser)
        plot_with_confidence_interval(
            ax,
            parser_df['size'].values,
            parser_df['validation_memory_mean'].values / 1024 / 1024,  # Convert to MB
            parser_df['validation_memory_ci_low'].values / 1024 / 1024,
            parser_df['validation_memory_ci_high'].values / 1024 / 1024,
            label=parser,
            style=style
        )
    ax.set_xlabel('Number of Strings')
    ax.set_ylabel('Memory (MB)')
    ax.set_title('Validation Memory')
    ax.legend(loc='upper left', fontsize=8)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    if output_path:
        fig.savefig(output_path, dpi=150, bbox_inches='tight')
        print(f"Saved combined linear plot to {output_path}")

    return fig
