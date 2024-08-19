import json

import numpy as np

class Leaf(dict):
    def __repr__(self) -> str:
        return "Leaf(%s)" % super().__repr__()
    
class End:
    def __repr__(self) -> str:
        return "End"

def insert_branch_into_tree(tree : dict, branch : dict) -> None:
    if End in (type(tree), type(branch)):
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
    end_symb = End()
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
        for k,v in wh.items():
            if len(k):
                authorized.add(k)
            else:
                unfold_authorized_characters([v], authorized)
    return authorized

def unfold_where_am_i(where_am_i : list[dict], current : dict) -> dict:
    for wh in where_am_i:
        for k,v in wh.items():
            # v = Leaf(v) if is_leaf else v
            if len(k):
                vc = current.get(k)
                if vc is None:
                    current[k] = v
                else:
                    insert_branch_into_tree(vc, v)
            else:
                unfold_where_am_i([v], current)
    return current

                    

class ChoicesConcatenationParser:
    def __init__(self, list_of_choices : list[list[str]]) -> None:
        
        self.tree = tree_from_list_of_choices(list_of_choices)
        
        self.where_am_i = [(self.tree, "")]
        self.finished = False
        self.success = False
        self.choices_found = [None]*len(list_of_choices)
        self.choice_idx = 0

    def next(self) -> str:
        return ''.join(unfold_authorized_characters((d[0] for d in self.where_am_i), set()))
    
    def step(self, ch : str) -> None:
        assert len(ch) == 1
        where_am_i_post = []
        for x, buf in self.where_am_i:
            x = unfold_where_am_i([x], dict())
            next = x.get(ch)
            if next is not None:
                # if isinstance(next, Leaf):
                #     self.choices_found[self.choice_idx] = buf[:-1]
                #     buf = buf[-1]
                #     self.choice_idx += 1
                if (after_empty := next.get('')) is not None and after_empty.__class__ is End:
                    self.success = True
                    self.choices_found[self.choice_idx] = buf
                    where_am_i_post.clear()
                    break
                buf = buf + ch
                where_am_i_post.append((next, buf))                    
        self.where_am_i = where_am_i_post
        if len(self.where_am_i) == 0:
            self.finished = True
    
    def reset(self) -> None:
        self.finished = False
        self.success = False
        self.where_am_i = [(self.tree, "")]
        self.choice_idx = 0
        self.choices_found = [None]*len(self.choices_found)


if __name__ == "__main__":
    # l = np.random.randint(0, 10**9, 7000000).astype(str)
    l = [
        ['the', 'an', "a", ""],
        ['orange', 'apple', 'banana']
    ]
    p = ChoicesConcatenationParser(l)


    for c in 'apple':
        print(p.next())
        print('Adding', c)
        p.step(c)
        print(p.finished, p.success, p.choices_found)