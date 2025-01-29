from __future__ import annotations
from . import _core
from typing import List, Tuple, Union

class FastMultiChoicesParser:
    """
    A efficient incremental parser for multi-choice grammars. They are defined as grammars of the form:

    start: list1 list2 ... listn

    list1: choice1_1 | choice1_2 | ... | choice1_k1

    list2: choice2_1 | choice2_2 | ... | choice2_k2

    ...
    
    listm: choicem_1 | choicem_2 | ... | choicem_km

    where choicex_y is a sequence of integers and can possibly be empty

    Example:
    start: det noun
    
    det: "the " | "an " | "a " | ""

    noun: "orange" | "apple" | "banana"
    
    Except characters are represented as integers

    This was particularly optimized when the size of the lists of choices is 
    very large (up to order of millions), which can be helpful
    to represent entities preceeded (or not) by a determinent. 
    For example, in Wikipedia, there are around 7 million entities.

    TODO: It is possible to use other types of sequences that strings as choices, such as a list of integers.
    """

    def __init__(self, list_of_choices: List[List[Union[Tuple[int], str]]], alphabet=None, end_symb=None) -> None:
        """
        Initialize the parser using a list of choices (a list of lists) which correspond
        to the lists introduced in the documentation of the class.

        Args:
            list_of_choices (list[list[Union[tuple[int], str]]]): The grammar choices.
                Each choice can be a tuple of integers or a string.
            end_symb (Union[int, str], optional): An optional end symbol to signify the end of input.
            alphabet has no use, ignore it.
        """
        self.end_symb = end_symb
        self.alphabet = alphabet

        # Determine the mode (string mode or integer mode) based on the first element
        if list_of_choices and list_of_choices[0] and isinstance(list_of_choices[0][0], str):
            self.string_mode = True
        else:
            self.string_mode = False

        # Convert all choices to lists of integers
        self.roots = []
        self.can_be_empty = []
        for choices in list_of_choices:
            can_be_empty = False
            if self.string_mode:
                sequences = []
                for choice in choices:
                    if not can_be_empty and len(choice) == 0:
                        can_be_empty = True
                    # Convert string to a list of integers (e.g., ASCII values)
                    sequences.append([ord(ch) for ch in choice])
            else:
                sequences = choices
                can_be_empty = any(len(choice) == 0 for choice in choices)
            # Construct a tree for this list of choices
            root = _core.construct_tree(sequences)
            self.roots.append(root)
            self.can_be_empty.append(can_be_empty)

        # Initialize the current state
        self.current_root_index = 0  # Start at the first root
        self.current_state = self.roots[0] if self.roots else None

        # Initialize success and finished flags
        self.success = False
        self.finished = False
        self.waiting_for_end_symb = False


    def next(self) -> Tuple[Union[int, str]]:
        """
        Returns all authorized tokens for the current state.

        Returns:
            tuple: A tuple of characters (if in string mode) or integers, or the End symbol.
        """
        if self.current_state is None:
            return (self.end_symb,) if self.end_symb is not None else ()

        if not self.current_state.transitions:
            # If no transitions are available, move to the next root (if any)
            if self.current_root_index + 1 < len(self.roots):
                return (self.end_symb,) if self.end_symb is not None else ()
            else:
                return ()

        # Collect all possible transitions from the current state
        transitions = tuple(transition.character for transition in self.current_state.transitions)
        if self.string_mode:
            # Convert integers to characters if in string mode
            return tuple(chr(ch) for ch in transitions)
        return transitions

    def step(self, ch: Union[int, str]) -> None:
        """
        Feed the character to the parser.

        Args:
            ch (Union[int, str]): A character (string) or an integer.
        """

        if self.finished:
            return

        if self.current_state is None:
            raise ValueError("Parser is in an invalid state.")

        # Convert character to integer if in string mode
        if self.string_mode and isinstance(ch, str):
            ch = ord(ch)

        # Check if the character is the end symbol
        if ch is self.end_symb and self.waiting_for_end_symb:
            # If the end symbol is fed, mark the parsing as finished
            self.finished = True
            # Check if the parser is in the final state
            if self.waiting_for_end_symb:
                self.success = True
            else:
                self.success = False
            self.waiting_for_end_symb = False
            return

        # Use the C++ step function to move to the next state
        next_state = _core.step(self.current_state, ch)
        if next_state is None and self.can_be_empty[self.current_root_index]:
            k = 1
            continue_ = True
            while self.current_root_index + k < len(self.roots) and continue_:
                next_root = self.roots[self.current_root_index+k]
                next_state = _core.step(next_root, ch)
                continue_ = self.can_be_empty[self.current_root_index + k]
                k += 1
                
            if next_state is not None:
                self.current_root_index += k
            else:
                # If the step fails, mark the parsing as finished but unsuccessful
                self.finished = True
                self.success = False

        self.current_state = next_state

        # If we reach the end of the current root, move to the next root
        if not self.current_state.transitions:
            if self.current_root_index + 1 < len(self.roots):
                self.current_root_index += 1
                self.current_state = self.roots[self.current_root_index]
            else:
                # If no more roots are available, mark the parsing as finished
                self.waiting_for_end_symb = True

    def reset(self) -> None:
        """
        Reset the state of the parser to its origin.
        """
        self.current_root_index = 0
        self.current_state = self.roots[0] if self.roots else None
        self.success = False
        self.finished = False
        self.waiting_for_end_symb = False

    def copy(self, stateful=True) -> FastMultiChoicesParser:
        """
        Return a copy of this parser (stateful or not).

        Note: The root ParserNodes remain the same (no additional memory allocation).

        Args:
            stateful (bool): If True, the copy retains the current state. Otherwise, it resets to the root.

        Returns:
            FastMultiChoicesParser: A new parser instance.
        """
        new_parser = FastMultiChoicesParser([], self.end_symb)
        new_parser.roots = self.roots  # Share the same roots
        new_parser.string_mode = self.string_mode
        if stateful:
            new_parser.current_root_index = self.current_root_index
            new_parser.current_state = self.current_state
            new_parser.success = self.success
            new_parser.finished = self.finished
            new_parser.waiting_for_end_symb = self.waiting_for_end_symb
        else:
            new_parser.reset()
        return new_parser

    def accepts(self, string: Union[Tuple[int], str]) -> bool:
        """
        Check whether the input string is correct according to this parser.

        Args:
            string (Union[tuple[int], str]): The input string as a tuple of integers or a string.

        Returns:
            bool: True if the string is accepted, False otherwise.
        """
        # Convert string to tuple of integers if necessary
        if self.string_mode:
            string = tuple(ord(ch) if ch is not self.end_symb else ch for ch in string)

        # Simulate the parsing process
        current_root_index = self.current_root_index
        current_state = self.roots[current_root_index] if self.roots else None

        for ch in string:
            if current_state is None:
                return ch is self.end_symb

            # Use the C++ step function to move to the next state
            next_state = _core.step(current_state, ch)
            if next_state is None:
                if current_root_index + 1 < len(self.roots):
                    next_root = self.roots[current_root_index+1]
                    next_state = _core.step(next_root, ch)
                    if next_state is not None:
                        current_root_index += 1
                if next_state is None:
                    return False

            current_state = next_state

            # If we reach the end of the current root, move to the next root
            if not current_state.transitions:
                current_root_index += 1
                if current_root_index < len(self.roots):
                    current_state = self.roots[current_root_index]
                else:
                    current_state = None

        # If we successfully parse through all roots, the string is accepted
        return True

    def __eq__(self, other: object) -> bool:
        """
        Check equality between two parsers.

        Args:
            other (object): Another parser instance.

        Returns:
            bool: True if the parsers are equivalent, False otherwise.
        """
        if not isinstance(other, FastMultiChoicesParser):
            return False
        return (
            self.roots == other.roots
            and self.current_root_index == other.current_root_index
            and self.current_state == other.current_state
        )

    def __hash__(self) -> int:
        """
        Compute a hash value for the parser.

        Returns:
            int: The hash value.
        """
        return hash((tuple(self.roots), self.current_root_index, id(self.current_state)))
