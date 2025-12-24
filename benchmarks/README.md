# Parser Benchmarks

This directory contains a comprehensive benchmarking suite for comparing parser implementations.

## Quick Start

```bash
# Install dev dependencies (from project root)
uv sync --group dev

# Run quick benchmarks (10 sizes, 5 construction repeats)
uv run python benchmarks/run_benchmarks.py --quick

# Run full benchmarks (20 sizes, 20 construction repeats, 1000 validation queries)
uv run python benchmarks/run_benchmarks.py
```

## Benchmark Description

### Test Scenarios

1. **String Generation**
   - Generate n lists of random strings where n ranges from 1 to 1M in logarithmic scale with 20 steps
   - String lengths vary randomly from 1 to 200 characters (uniform distribution)

2. **Construction Benchmark**
   - Measures time and memory for parser construction
   - Repeated 20 times per size step (configurable)
   - Reports mean, standard deviation, and 95% confidence intervals

3. **Validation Benchmark**
   - Measures time to validate a valid string taken randomly from the original list
   - Performs 1000 validation queries per size step (configurable)
   - Reports mean validation time with confidence intervals

## Adding New Parsers

To add a new parser implementation for benchmarking:

1. Create a class that inherits from `ParserInterface`:

```python
from parser_interface import ParserInterface

class MyCustomParser(ParserInterface):
    @classmethod
    def name(cls) -> str:
        return "MyCustomParser"

    def __init__(self, strings: List[str]) -> None:
        # Initialize your parser with the list of strings
        self._data = your_construction_logic(strings)

    def accepts(self, string: str) -> bool:
        # Return True if string is in the accepted set
        return your_validation_logic(string)

    def get_memory_bytes(self) -> int:
        # Return estimated memory usage in bytes
        return your_memory_estimate()
```

2. Register it in `parser_interface.py`:

```python
AVAILABLE_PARSERS = {
    'multi_choices': MultiChoicesParserWrapper,
    'set_based': SetBasedParser,
    'python_trie': TrieParser,
    'my_custom': MyCustomParser,  # Add your parser here
}
```

3. Run benchmarks:

```bash
python run_benchmarks.py --parsers my_custom multi_choices
```

## Command Line Options

```
--parsers           Parsers to benchmark (default: all available)
--num-steps         Number of size steps in log scale (default: 20)
--construction-repeats  Repeats for construction benchmark (default: 20)
--validation-repeats    Validation queries per size (default: 1000)
--seed              Random seed for reproducibility (default: 42)
--min-string-length Minimum string length (default: 1)
--max-string-length Maximum string length (default: 200)
--output-dir        Directory for results and plots (default: ./results)
--quick             Use reduced settings for quick testing
--load-results      Load existing results from CSV
--plot-only         Only generate plots (requires --load-results)
--no-show           Don't display plots, only save to files
--quiet             Reduce output verbosity
```

## Output Files

After running, the following files are created in the output directory:

- `benchmark_results.csv` - Raw benchmark data
- `benchmark_construction_time.png` - Construction time vs list size
- `benchmark_memory.png` - Memory consumption vs list size
- `benchmark_validation_time.png` - Validation time vs list size
- `benchmark_combined.png` - All three plots combined

## Example Results

The benchmarks compare:

1. **MultiChoicesParser** - The C++ trie-based implementation from this project
2. **SetBasedParser** - Simple Python set lookup (baseline)
3. **PythonTrie** - Pure Python trie implementation

Expected characteristics:
- MultiChoicesParser should have O(n) construction time and memory
- Set-based lookup should have O(1) validation but O(n) memory
- Trie implementations share prefixes, potentially using less memory for similar strings
