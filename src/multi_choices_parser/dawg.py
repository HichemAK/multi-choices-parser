# Software Name : multi-choices-parser
# SPDX-FileCopyrightText: Copyright (c) 2025 Orange SA
# SPDX-License-Identifier: GPL-2.0-or-later

# This software is distributed under the GNU General Public License v2.0 or later,
# see the "LICENSE.txt" file for more details or GNU General Public License v2.0 or later

# Authors: Hichem Ammar Khodja

from __future__ import annotations

from dawg import CompletionDAWG
from typing import List, Tuple, Union

from .common import DEFAULT_END_SYMB, ParserError


class MultiChoicesParserDAWG:
    """
    A DAWG-based incremental parser for multi-choice grammars.

    This class provides the same interface as MultiChoicesParserTrie but uses
    DAWG (Directed Acyclic Word Graph) for more memory-efficient storage.
    """

    def __init__(self, list_of_choices: List[List[Union[Tuple[int], str]]], alphabet=None, end_symb=DEFAULT_END_SYMB) -> None:
        """
        Initialize the parser using a list of choices.

        Args:
            list_of_choices (list[list[Union[tuple[int], str]]]): The grammar choices.
            alphabet: Unused, kept for interface compatibility.
            end_symb: An optional end symbol to signify the end of input.
        """
        self.end_symb = end_symb
        self.alphabet = alphabet

        # Determine the mode (string mode or integer mode) based on the first element
        if list_of_choices and list_of_choices[0] and isinstance(list_of_choices[0][0], str):
            self.string_mode = True
        else:
            self.string_mode = False

        # Build a CompletionDAWG for each list of choices
        if self.string_mode:
            self.dawgs = [CompletionDAWG(choices) for choices in list_of_choices]
        else:
            # For integer mode, convert to strings for DAWG storage
            self.dawgs = []
            for choices in list_of_choices:
                str_choices = [''.join(chr(c) for c in choice) for choice in choices]
                self.dawgs.append(CompletionDAWG(str_choices))


        # Initialize state
        self.current_list_idx = 0
        self.current_prefix = ""
        self.finished = False
        self.success = False
        self._is_at_initial_state = True

    def next(self) -> List[Union[int, str]]:
        """
        Returns all authorized tokens for the current state.

        Returns:
            list: A list of characters (if in string mode) or integers, or the End symbol.
        """
        if self.finished:
            return []

        dawg = self.dawgs[self.current_list_idx]
        completions = list(dawg.keys(self.current_prefix))

        next_chars = set()
        prefix_len = len(self.current_prefix)

        for comp in completions:
            if len(comp) > prefix_len:
                next_chars.add(comp[prefix_len])
            elif comp == self.current_prefix:
                # Current prefix is a complete word - can move to next list or finish
                if self.current_list_idx < len(self.dawgs) - 1:
                    # Add first chars from next DAWG
                    next_dawg = self.dawgs[self.current_list_idx + 1]
                    for word in next_dawg.keys():
                        if word:
                            next_chars.add(word[0])
                        else:
                            # Empty string in next list - look ahead further
                            if self.current_list_idx + 1 < len(self.dawgs) - 1:
                                next_next_dawg = self.dawgs[self.current_list_idx + 2]
                                for w in next_next_dawg.keys():
                                    if w:
                                        next_chars.add(w[0])
                            else:
                                next_chars.add(self.end_symb)
                else:
                    next_chars.add(self.end_symb)

        result = list(next_chars)
        if not self.string_mode:
            result = [ord(c) if isinstance(c, str) else c for c in result]
        return result

    def step(self, ch: Union[int, str]) -> None:
        """
        Feed a character to the parser.

        Args:
            ch (Union[int, str]): A character (string) or an integer.
        """
        if self.finished:
            raise ParserError("The parser is in 'finished' state!")

        if ch is self.end_symb:
            # Check if current prefix is valid and we're at last list
            if (self.current_prefix in self.dawgs[self.current_list_idx] and
                    self.current_list_idx == len(self.dawgs) - 1):
                self.finished = True
                self.success = True
            else:
                self.finished = True
                self.success = False
            self._is_at_initial_state = False
            return

        if isinstance(ch, int):
            ch = chr(ch)

        self.current_prefix += ch
        self._is_at_initial_state = False

        # Check if current prefix is a complete match
        if self.current_prefix in self.dawgs[self.current_list_idx]:
            # Check if we can continue with current prefix or need to move to next list
            dawg = self.dawgs[self.current_list_idx]
            completions = list(dawg.keys(self.current_prefix))
            has_longer = any(len(c) > len(self.current_prefix) for c in completions)

            if not has_longer:
                # Must move to next list
                if self.current_list_idx < len(self.dawgs) - 1:
                    self.current_list_idx += 1
                    self.current_prefix = ""

        # Check if current state is valid
        dawg = self.dawgs[self.current_list_idx]
        completions = list(dawg.keys(self.current_prefix))
        if not completions:
            self.finished = True
            self.success = False

    def reset(self) -> None:
        """
        Reset the state of the parser to its origin.
        """
        self.current_list_idx = 0
        self.current_prefix = ""
        self.finished = False
        self.success = False
        self._is_at_initial_state = True

    def copy(self, stateful=True) -> MultiChoicesParserDAWG:
        """
        Return a copy of this parser (stateful or not).

        Args:
            stateful (bool): If True, the copy retains the current state.

        Returns:
            MultiChoicesParserDAWG: A new parser instance.
        """
        new_parser = MultiChoicesParserDAWG([], end_symb=self.end_symb)
        new_parser.dawgs = self.dawgs  # Share the same DAWGs
        new_parser.string_mode = self.string_mode
        new_parser.alphabet = self.alphabet
        if stateful:
            new_parser.current_list_idx = self.current_list_idx
            new_parser.current_prefix = self.current_prefix
            new_parser.success = self.success
            new_parser.finished = self.finished
            new_parser._is_at_initial_state = self._is_at_initial_state
        else:
            new_parser.reset()
        return new_parser

    def accepts(self, string: Union[Tuple[int], str], must_end=False) -> bool:
        """
        Check whether the input string is correct according to this parser.

        Args:
            string (Union[tuple[int], str]): The input string.
            must_end (bool): If True, require end symbol at end.

        Returns:
            bool: True if the string is accepted, False otherwise.
        """
        # Create a temporary copy to test
        temp = self.copy(stateful=True)
        try:
            for ch in string:
                if temp.finished:
                    return False
                temp.step(ch)
            return temp.success or (not temp.finished and not must_end)
        except ParserError:
            return False

    def __eq__(self, other: object) -> bool:
        """
        Check equality between two parsers.
        """
        if not isinstance(other, MultiChoicesParserDAWG):
            return False
        return (
            self.dawgs is other.dawgs
            and self.current_list_idx == other.current_list_idx
            and self.current_prefix == other.current_prefix
        )

    def __hash__(self) -> int:
        """
        Compute a hash value for the parser.
        """
        return hash((id(self.dawgs), self.current_list_idx, self.current_prefix))

    @property
    def is_at_initial_state(self) -> bool:
        return self._is_at_initial_state

    # def add_sequence(self, string: Union[Tuple[int], str]) -> bool:
    #     """
    #     Add a sequence to the parsing tree.

    #     Note: DAWG does not support dynamic updates efficiently.
    #     This rebuilds the DAWG which is expensive.

    #     Args:
    #         string (Union[Tuple[int], str]): String to add.

    #     Returns:
    #         bool: If something was added.
    #     """
    #     if self.string_mode:
    #         if string in self._original_choices[0]:
    #             return False
    #         self._original_choices[0].append(string)
    #         self.dawgs[0] = CompletionDAWG(self._original_choices[0])
    #         return True
    #     else:
    #         str_string = ''.join(chr(c) for c in string)
    #         choices_as_str = [''.join(chr(c) for c in choice) for choice in self._original_choices[0]]
    #         if str_string in choices_as_str:
    #             return False
    #         self._original_choices[0].append(list(string))
    #         choices_as_str.append(str_string)
    #         self.dawgs[0] = CompletionDAWG(choices_as_str)
    #         return True
