from __future__ import annotations

class Leaf(dict):
    def __repr__(self) -> str:
        return "Leaf(%s)" % super().__repr__()
    
class End:
    def __repr__(self) -> str:
        return "End"
end_symb = End()

def insert_branch_into_tree(tree : dict, branch : dict) -> None:
    if not (dict == type(tree) == type(tree)):
        return
    for kb,vb in branch.items():
        vt = tree.get(kb)
        if vt is None:
            tree[kb] = vb
        else:
            insert_branch_into_tree(vt, vb)

def tree_from_list_of_choices(list_of_choices : list[list[str]]) -> tuple[dict, tuple]:
    root = {}
    alphabet = set()
    common_leaf = root
    any_is_empty = []
    leaves_from_root = []
    len_list_choices = len(list_of_choices)
    for k,l in enumerate(list_of_choices):
        leaves_from_root.append(common_leaf)
        current_tree = common_leaf
        common_leaf = Leaf() if k != len_list_choices - 1 else end_symb
        any_is_empty_k = False
        for ch in l:
            current = current_tree
            last_idx = len(ch) - 1
            # (last_idx == -1) means ch is an empty string
            any_is_empty_k = any_is_empty_k or last_idx == -1
            for i,c in enumerate(ch):
                alphabet.add(c)
                d = current.get(c)
                
                if d is None:
                    d = {}
                    current[c] = d
                
                current = d
                if i == last_idx:
                    current[''] = common_leaf
        any_is_empty.append(any_is_empty_k)
    else:
        leaves_from_root.append(common_leaf)


    # Handle empty choices
    for i in range(len_list_choices):
        count_successive_empty = 0
        for k in any_is_empty[i:]:
            if not k:
                break
            count_successive_empty += 1

        for j in range(i+1, i+1+count_successive_empty):
            d = leaves_from_root[i].get('')
            if d is None:
                leaves_from_root[i][''] = leaves_from_root[j]
            else:
                insert_branch_into_tree(d, leaves_from_root[j])

    return root, tuple(alphabet)

def unfold_authorized_characters(where_am_i : dict | None, authorized : set):
    if where_am_i is None:
        return authorized
    if where_am_i is end_symb:
        authorized.add(where_am_i)
        return authorized
    for k,v in where_am_i.items():
        if len(k):
            authorized.add(k)
        else:
            unfold_authorized_characters(v, authorized)
    return authorized

def unfold_where_am_i(where_am_i : dict | None, current : dict) -> dict:
    if where_am_i is None:
        return current
    if where_am_i is end_symb:
        current[end_symb] = 0
        return current
    for k,v in where_am_i.items():
        if k is end_symb or len(k):
            vc = current.get(k)
            if vc is None:
                current[k] = v
            else:
                insert_branch_into_tree(vc, v)
        else:
            unfold_where_am_i(v, current)
    return current

                    

class MultiChoicesParser:
    """A efficient incremental parser for multi-choice grammars. They are defined as grammars of the form:

    start: list1 list2 ... listn

    list1: choice1_1 | choice1_2 | ... | choice1_k1

    list2: choice2_1 | choice2_2 | ... | choice2_k2

    ...
    
    listm: choicem_1 | choicem_2 | ... | choicem_km

    where choicex_y are all literals (strings) and can possibly be empty

    Example:
    start: det noun
    
    det: "the " | "an " | "a " | ""

    noun: "orange" | "apple" | "banana"

    This was particularly optimized when the size of the lists of choices is 
    very large (up to order of millions), which can be helpful
    to represent entities preceeded (or not) by a determinent. 
    For example, in Wikipedia, there are around 7 million entities (one article per entity).
    """
    def __init__(self, list_of_choices : list[list[str]] | None) -> None:
        """Initialize the parser using a list of choices (a list of lists) which correspond 
        to the lists introduced in the documentation of the class

        Args:
            list_of_choices (list[list[str]]): List of choices
        """
        if list_of_choices is not None:
            self.tree, self.alphabet = tree_from_list_of_choices(list_of_choices)
        else:
            self.tree, self.alphabet = {}, tuple()
        self.reset()

    @staticmethod
    def init_empty() -> MultiChoicesParser:
        empty = MultiChoicesParser(None)
        return empty

    def next(self) -> tuple:
        """Returns all authorized tokens for the current state

        Returns:
            tuple: A tuple of characters or the End symbol 
        """
        return tuple(unfold_authorized_characters(self.where_am_i, set()))
    
    def step(self, ch : str | End) -> None:
        """Feed the character to the parser.

        Note: Feed the End symbol when the string to parse is finished.
        After this is done, the flag self.success will tell you if the parsed string is correct or not

        Args:
            ch (str): A charachter or End symbol 
        """
        if self.finished:
            return
        assert ch is end_symb or len(ch) == 1
        where_am_i_unfolded = unfold_where_am_i(self.where_am_i, dict())
        next = where_am_i_unfolded.get(ch)
        if next == 0 and ch is end_symb:
            self.success = True
            self.finished = True
        elif next is None:
            self.success = False
            self.finished = True
        elif ch is not end_symb:
            self.buf += ch
        self.where_am_i = next
    
    def reset(self) -> None:
        """Reset the state of the parser.
        """
        self.finished = False
        self.success = False
        self.where_am_i = self.tree
        self.buf = ''


    def copy(self, stateful=True) -> MultiChoicesParser:
        c = MultiChoicesParser.init_empty()
        c.tree = self.tree
        c.alphabet = self.alphabet
        if stateful:
            c.finished = self.finished
            c.success = self.success
            c.where_am_i = self.where_am_i
        else:
            c.where_am_i = c.tree
        return c