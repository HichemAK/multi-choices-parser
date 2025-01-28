from __future__ import annotations
from marisa_trie import Trie

from .parser import DEFAULT_END_SYMB, End

def build_marisa_tries(list_of_choices : list[list[str]]) -> list[Trie]:
    return [Trie(x) for x in list_of_choices]
    

class MultiChoicesParserMarisa:
    """A efficient incremental parser for multi-choice grammars optimized for integer grammars and based on the marisa-trie package. They are defined as grammars of the form:

    start: list1 list2 ... listn

    list1: choice1_1 | choice1_2 | ... | choice1_k1

    list2: choice2_1 | choice2_2 | ... | choice2_k2

    ...
    
    listm: choicem_1 | choicem_2 | ... | choicem_km

    where choicex_y is a string or list of integers and can possibly be empty

    Example:
    start: det noun
    
    det: [1,2,3] | [1,2] | [3,2] | []

    noun: [5,8,9,4,2,3] | [5,1,2,3,4,5,6] | [5,2,3,4,5,9]

    This was particularly optimized when the size of the lists of choices is 
    very large (up to order of millions), which can be helpful
    to represent entities preceeded (or not) by a determinent.
    For example, in Wikipedia, there are around 7 million entities.

    NOTE: It is possible to use other types of sequences that strings as choices, such as a list of integers.
    """
    def __init__(self, list_of_choices : list[list[str | tuple[int]]] | None, end_symb=DEFAULT_END_SYMB) -> None:
        """Initialize the parser using a list of choices (a list of lists) which correspond 
        to the lists introduced in the documentation of the class
        """
        self.alphabet = None
        if list_of_choices is None:
            list_of_choices = []
        self.tries = build_marisa_tries(list_of_choices)
        self.end_symb = end_symb
        self.trie_index = 0
        self.buf = []
        self.finished = False
        self.success = False

    @staticmethod
    def init_empty() -> MultiChoicesParserMarisa:
        empty = MultiChoicesParserMarisa(None)
        return empty

    def next(self) -> tuple:
        """Returns all authorized tokens for the current state

        Returns:
            tuple: A tuple of characters or the End symbol 
        """
        if self.buf[-1] is self.end_symb:
            return tuple()
        s = set()
        all_pref = self.tries[self.trie_index].keys(self.buf)
        for pref in all_pref:
            if len(self.buf) < len(pref):
                pref = pref[len(self.buf)]
            elif self.trie_index + 1 < len(self.tries):
                s.update(x[0] for x in self.tries[self.trie_index+1].keys('') if len(x))
            else:
                s.add(self.end_symb)
        return tuple(s)

    def step(self, ch : str | int | tuple[int] | End) -> None:
        """Feed the character to the parser.

        Note: Feed the End symbol when the string to parse is finished.
        After this is done, the flag self.success will tell you if the parsed string is correct or not

        Args:
            ch (str): A charachter or End symbol 
        """
        assert isinstance(ch, (str,tuple,int,End)) or ch is self.end_symb
        if self.finished:
            return
        
        # Format int to tuple
        if isinstance(ch,int) and ch is not self.end_symb:
            ch = (ch,)
        
        where_am_i_unfolded = unfold_where_am_i(self.where_am_i, dict(), self.end_symb)
        next = where_am_i_unfolded.get(ch)
        if next == 0 and ch is self.end_symb:
            self.success = True
            self.finished = True
        elif next is None:
            self.success = False
            self.finished = True
        elif ch is not self.end_symb:
            self.buf.append(ch)
        self.where_am_i = next
    
    def reset(self) -> None:
        """Reset the state of the parser.
        """
        self.trie_index = 0
        self.buf = []
        self.finished = False
        self.success = False


    def copy(self, stateful=True) -> MultiChoicesParserMarisa:
        """Return a copy of this parser (stateful or not)"""
        c = MultiChoicesParserMarisa.init_empty()
        c.tries = self.tries
        c.alphabet = self.alphabet
        c.end_symb = self.end_symb
        c.tries = self.tries
        if stateful:
            c.finished = self.finished
            c.success = self.success
            c.trie_index = c.trie_index
            c.buf = list(self.buf)
        return c
    
    def accepts(self, string : str) -> bool:
        """Check whether the input string is correct according to this parser"""
        if len(string) == 0:
            return True
        
        # Remove last end symb
        if string[-1] is self.end_symb:
            string = string[:-1]
            has_end_symb=  True
        else:
            has_end_symb = False

        # Check that there are no more end symbols
        for c in string:
            if c is self.end_symb:
                return False
        trie_index = self.trie_index
        add_buf = True
        for i in range(trie_index, len(self.tries)):
            inp = string
            if add_buf:
                inp = self.buf + string
                add_buf = False
            accept = len(self.tries[i].prefixes(inp)) > 0
            if not accept:
                return False
            
                
        return True
    
    # [parser1 == parser2 or hash(parser1) == hash(parser2)] ===> parser1 and parser2 will behave exactly the same 
    # (but the reverse is not necessarily True)
    def __eq__(self, value: object) -> bool:
        if not isinstance(value, MultiChoicesParserMarisa):
            return False
        return self.alphabet is value.alphabet and self.tree is value.tree \
            and self.where_am_i is value.where_am_i and self.finished == value.finished and self.success == value.success
    
    def __hash__(self) -> int:
        return sum(hash(x) for x in (id(self.alphabet), id(self.where_am_i), 
                                     id(self.tree), self.finished, self.success))