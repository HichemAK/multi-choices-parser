"""
Abstract interface for parsers to enable benchmarking of different implementations.

To add a new parser for benchmarking:
1. Create a class that inherits from ParserInterface
2. Implement all abstract methods
3. Register it in AVAILABLE_PARSERS dict
"""

from abc import ABC, abstractmethod
from typing import List, Tuple, Any, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class ParserInterface(ABC):
    """Abstract base class for parser implementations."""

    @classmethod
    @abstractmethod
    def name(cls) -> str:
        """Return the name of this parser implementation."""
        pass

    @abstractmethod
    def __init__(self, strings: List[str]) -> None:
        """
        Construct the parser from a list of strings.

        Args:
            strings: List of strings to be accepted by the parser
        """
        pass

    @abstractmethod
    def accepts(self, string: str) -> bool:
        """
        Check if the parser accepts the given string.

        Args:
            string: The string to validate

        Returns:
            True if the string is accepted, False otherwise
        """
        pass

    @abstractmethod
    def get_memory_bytes(self) -> int:
        """
        Return an estimate of memory usage in bytes.

        Returns:
            Estimated memory consumption in bytes
        """
        pass


class MultiChoicesParserWrapper(ParserInterface):
    """Wrapper for the multi-choices-parser implementation."""

    @classmethod
    def name(cls) -> str:
        return "MultiChoicesParser"

    def __init__(self, strings: List[str]) -> None:
        from multi_choices_parser import MultiChoicesParser, DEFAULT_END_SYMB
        # Wrap strings in a single choice group
        self._parser = MultiChoicesParser([strings])
        self._strings = strings
        self._end_symb = DEFAULT_END_SYMB

    def accepts(self, string: str) -> bool:
        # Step through the string and check if we can end
        parser_copy = self._parser.copy(stateful=False)
        for char in string:
            if parser_copy.finished:
                return False
            parser_copy.step(char)

        # Check if END is a valid next symbol
        if parser_copy.finished:
            return False
        return self._end_symb in parser_copy.next()

    def get_memory_bytes(self) -> int:
        # Estimate memory by counting nodes and transitions
        # This is an approximation based on the trie structure
        import sys
        visited = set()
        total_size = 0

        def traverse(node):
            nonlocal total_size
            if node is None or id(node) in visited:
                return
            visited.add(id(node))
            # Approximate size of a node: object overhead + transitions list
            total_size += sys.getsizeof(node) + sys.getsizeof(node.transitions)
            for trans in node.transitions:
                # Size of transition: character + pointer
                total_size += sys.getsizeof(trans)
                traverse(trans.next)

        if self._parser.root is not None:
            traverse(self._parser.root)

        return total_size


class SetBasedParser(ParserInterface):
    """Simple set-based parser for comparison (baseline)."""

    @classmethod
    def name(cls) -> str:
        return "SetBasedParser"

    def __init__(self, strings: List[str]) -> None:
        self._strings = set(strings)

    def accepts(self, string: str) -> bool:
        return string in self._strings

    def get_memory_bytes(self) -> int:
        import sys
        total = sys.getsizeof(self._strings)
        for s in self._strings:
            total += sys.getsizeof(s)
        return total


class TrieParser(ParserInterface):
    """Pure Python trie implementation for comparison."""

    @classmethod
    def name(cls) -> str:
        return "PythonTrie"

    def __init__(self, strings: List[str]) -> None:
        self._root = {}
        self._end_marker = '\x00'  # End of string marker
        for s in strings:
            self._insert(s)

    def _insert(self, string: str) -> None:
        node = self._root
        for char in string:
            if char not in node:
                node[char] = {}
            node = node[char]
        node[self._end_marker] = True

    def accepts(self, string: str) -> bool:
        node = self._root
        for char in string:
            if char not in node:
                return False
            node = node[char]
        return self._end_marker in node

    def get_memory_bytes(self) -> int:
        import sys

        def get_dict_size(d):
            total = sys.getsizeof(d)
            for k, v in d.items():
                total += sys.getsizeof(k)
                if isinstance(v, dict):
                    total += get_dict_size(v)
                else:
                    total += sys.getsizeof(v)
            return total

        return get_dict_size(self._root)


# Registry of available parsers
AVAILABLE_PARSERS = {
    'multi_choices': MultiChoicesParserWrapper,
    'set_based': SetBasedParser,
    'python_trie': TrieParser,
}


def get_parser_class(name: str) -> type:
    """Get a parser class by name."""
    if name not in AVAILABLE_PARSERS:
        raise ValueError(f"Unknown parser: {name}. Available: {list(AVAILABLE_PARSERS.keys())}")
    return AVAILABLE_PARSERS[name]


def list_available_parsers() -> List[str]:
    """Return list of available parser names."""
    return list(AVAILABLE_PARSERS.keys())
