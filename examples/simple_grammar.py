from multi_choices_parser import MultiChoicesParser, end_symb

l = [
    [tuple(x,) for x in ['the', 'an', "a", ""]],
    [tuple(x,) for x in ['orange', 'apple', 'banana']]
]
p = MultiChoicesParser(l)
print(sorted(p.alphabet))

for i, c in enumerate(tuple("apple") + (end_symb, )):
    print('Step %s' % i)
    print("Authorized characters:", sorted(p.next()))
    print('Adding character:', c)
    p.step(c)
    print("State: Finished=%s, Success=%s" % (p.finished, p.success))
    print()