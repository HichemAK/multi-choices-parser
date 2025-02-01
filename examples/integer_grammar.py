from multi_choices_parser import MultiChoicesParser, DEFAULT_END_SYMB


l = [
    [[0,1,2,3], [0,1]],
    [[5,6,7,8], [0,1,5], []]
]
p = MultiChoicesParser(l)

for i, c in enumerate((0,1,2,3) + (DEFAULT_END_SYMB, )):
    print('Step %s' % i)
    print("Authorized characters:", sorted(p.next()))
    print('Adding character:', c)
    p.step(c)
    print("State: Finished=%s, Success=%s" % (p.finished, p.success))
    print()