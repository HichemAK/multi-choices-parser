import json

import numpy as np

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

def tree_from_list_of_choices(list_of_choices : list[list[str]]) -> dict:
    root = {}
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
                d = current.get(c)
                
                if d is None:
                    d = {}
                    current[c] = d
                
                current = d
                if i == last_idx:
                    current[''] = common_leaf
        any_is_empty.append(any_is_empty_k)


    # Handle empty choices
    for i in range(len_list_choices):
        count_successive_empty = 0
        for k in any_is_empty[i:]:
            if not k:
                break
            count_successive_empty += 1

        for j in range(i+1, i+1+count_successive_empty):
            leaves_from_root[i][''] = leaves_from_root[j]

    return root

def unfold_authorized_characters(where_am_i : list[dict], authorized : set):
    for wh in where_am_i:
        if wh is end_symb:
            authorized.add(wh)
            return
        for k,v in wh.items():
            if len(k):
                authorized.add(k)
            else:
                unfold_authorized_characters([v], authorized)
    return authorized

def unfold_where_am_i(where_am_i : list[dict], current : dict) -> dict:
    for wh in where_am_i:
        if wh is None:
            continue
        if wh is end_symb:
            current[end_symb] = 0
            continue
        for k,v in wh.items():
            if k is end_symb or len(k):
                vc = current.get(k)
                if vc is None:
                    current[k] = v
                else:
                    insert_branch_into_tree(vc, v)
            else:
                unfold_where_am_i([v], current)
    return current

                    

class ChoicesConcatenationParser:
    """A efficient incremental parser for choices-concatenation grammars. They are of the form:

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
    def __init__(self, list_of_choices : list[list[str]]) -> None:
        """Initialize the parser using a list of choices (a list of lists) which correspond 
        to the lists introduced in the documentation of the class

        Args:
            list_of_choices (list[list[str]]): List of choices
        """
        self.tree = tree_from_list_of_choices(list_of_choices)
        self.reset()

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
        assert ch is end_symb or len(ch) == 1
        where_am_i_post = []
        for x in self.where_am_i:
            x = unfold_where_am_i([x], dict())
            next = x.get(ch)
            if ch is end_symb:
                if next is not None:
                    self.success = True
                    self.finished = True
                else:
                    self.success = False
                    self.finished = True
                where_am_i_post.clear()
                break
            where_am_i_post.append(next)                    
        self.where_am_i = where_am_i_post
    
    def reset(self) -> None:
        """Reset the state of the parser.
        """
        self.finished = False
        self.success = False
        self.where_am_i = [self.tree]
