"""
Abstract interface for parsers to enable benchmarking of different implementations.

To add a new parser for benchmarking:
1. Create a class that inherits from ParserInterface
2. Implement all abstract methods (step, reset, and properties)
3. Register it in AVAILABLE_PARSERS dict
"""

from abc import ABC, abstractmethod
from typing import List

class ParserInterface(ABC):
    """Abstract base class for parser implementations using step-based validation."""

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
    def step(self, char: str) -> None:
        """
        Feed a single character to the parser.

        Args:
            char: A single character to process
        """
        pass

    @abstractmethod
    def reset(self) -> None:
        """Reset parser state to initial state."""
        pass

    @property
    @abstractmethod
    def finished(self) -> bool:
        """Return True if parser cannot accept more input."""
        pass

    @property
    @abstractmethod
    def success(self) -> bool:
        """Return True if parser successfully matched a complete string."""
        pass


class MultiChoicesParserWrapper(ParserInterface):
    """Wrapper for the multi-choices-parser implementation (sorted array mode)."""

    @classmethod
    def name(cls) -> str:
        return "MultiChoicesParser"

    def __init__(self, strings: List[str]) -> None:
        from multi_choices_parser import MultiChoicesParser, DEFAULT_END_SYMB, TransitionMode
        self._parser = MultiChoicesParser([strings], transition_mode=TransitionMode.SORTED_ARRAY)
        self._end_symb = DEFAULT_END_SYMB

    def step(self, char: str) -> None:
        self._parser.step(char)

    def reset(self) -> None:
        self._parser.reset()

    @property
    def finished(self) -> bool:
        return self._parser.finished

    @property
    def success(self) -> bool:
        return self._parser.success


class MultiChoicesHashMapWrapper(ParserInterface):
    """Wrapper for the multi-choices-parser implementation (hash map mode)."""

    @classmethod
    def name(cls) -> str:
        return "MultiChoicesHashMap"

    def __init__(self, strings: List[str]) -> None:
        from multi_choices_parser import MultiChoicesParser, DEFAULT_END_SYMB, TransitionMode
        self._parser = MultiChoicesParser([strings], transition_mode=TransitionMode.HASH_MAP)
        self._end_symb = DEFAULT_END_SYMB

    def step(self, char: str) -> None:
        self._parser.step(char)

    def reset(self) -> None:
        self._parser.reset()

    @property
    def finished(self) -> bool:
        return self._parser.finished

    @property
    def success(self) -> bool:
        return self._parser.success


class TrieParser(ParserInterface):
    """Pure Python trie implementation for comparison."""

    @classmethod
    def name(cls) -> str:
        return "PythonTrie"

    def __init__(self, strings: List[str]) -> None:
        self._root = {}
        self._end_marker = '\x00'
        for s in strings:
            self._insert(s)
        self._current_node = self._root
        self._finished = False
        self._success = False

    def _insert(self, string: str) -> None:
        node = self._root
        for char in string:
            if char not in node:
                node[char] = {}
            node = node[char]
        node[self._end_marker] = True

    def step(self, char: str) -> None:
        if self._finished:
            return

        if char not in self._current_node:
            self._finished = True
            self._success = False
        else:
            self._current_node = self._current_node[char]
            # Check if we've reached end of a valid string
            if self._end_marker in self._current_node and len(self._current_node) == 1:
                # Only end marker present, no more characters possible
                pass

    def reset(self) -> None:
        self._current_node = self._root
        self._finished = False
        self._success = False

    @property
    def finished(self) -> bool:
        return self._finished

    @property
    def success(self) -> bool:
        return self._success

    def complete(self) -> None:
        """Mark validation as complete and check if current position is valid end."""
        if not self._finished:
            self._finished = True
            self._success = self._end_marker in self._current_node

# Registry of available parsers
AVAILABLE_PARSERS = {
    'multi_choices': MultiChoicesParserWrapper,
    'multi_choices_hashmap': MultiChoicesHashMapWrapper,
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
