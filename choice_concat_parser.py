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
    def __init__(self, list_of_choices : list[list[str]]) -> None:
        self.tree = tree_from_list_of_choices(list_of_choices)
        self.reset()

    def next(self) -> tuple:
        return tuple(unfold_authorized_characters(self.where_am_i, set()))
    
    def step(self, ch : str) -> None:
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
        self.finished = False
        self.success = False
        self.where_am_i = [self.tree]


if __name__ == "__main__":
    l = np.random.randint(0, 10**9, 7000000).astype(str)
    l = [
        ['the', 'an', "a", ""],
        l
    ]
    # l = [
    #     ['the', 'an', "a", ""],
    #     ['orange', 'apple', 'banana']
    # ]
    p = ChoicesConcatenationParser(l)

    to_parse = l[1][0]
    for i, c in enumerate(tuple(to_parse) + (end_symb, )):
        print('Step %s' % i)
        print("Authorized characters :", sorted(p.next()))
        print('Adding character:', c)
        p.step(c)
        print("State: Finished=%s, Success=%s" % (p.finished, p.success))
        print()
