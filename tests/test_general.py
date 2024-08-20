import itertools
from parser import MultiChoicesParser, end_symb


def correct_test(to_parse : str, parser : MultiChoicesParser, reset=True) -> None:
    if reset:
        parser.reset()
    for c in tuple(to_parse) + (end_symb, ):
        assert not parser.finished and not parser.success
        parser.step(c)
    else:
        print(to_parse)
        assert parser.finished and parser.success

def incorrect_test(to_parse : str, parser : MultiChoicesParser) -> None:
    parser.reset()
    for c in tuple(to_parse) + (end_symb, ):
        assert not parser.finished and not parser.success
        parser.step(c)
    assert not parser.success and parser.finished

def test_alphabet() -> None:
    l = [
        ['the', 'an', "a", ""],
        ['orange', 'apple', 'banana']
    ]
    
    parser = MultiChoicesParser(l)
    assert sorted(parser.alphabet) == ['a', 'b', 'e', 'g', 'h', 'l', 'n', 'o', 'p', 'r', 't']

def test_parse_incorrect() -> None:
    l = [
        ['the', 'an', "a", ""],
        ['orange', 'apple', 'banana']
    ]

    parser = MultiChoicesParser(l)
    to_parse_incorrect = [
        ('z'),
        ("the"),
        ("appl"),
        ("a"),
        ("tzeorange")
    ]

    for p in to_parse_incorrect:
        incorrect_test(p, parser)

def test_parse_correct_without_empty():
    l = [
        ['the', 'an', "a"],
        ['orange', 'apple', 'banana']
    ]

    parser = MultiChoicesParser(l)
    to_parse_correct = [
        x + y for x, y in itertools.product(l[0], l[1])
    ]
    for p in to_parse_correct:
        correct_test(p, parser)

def test_parse_correct_with_empty():
    l = [
        ['the', 'an', "a", ""],
        ['orange', 'apple', 'banana']
    ]

    parser = MultiChoicesParser(l)
    to_parse_correct = [
        x + y for x, y in itertools.product(l[0], l[1])
    ]

    for p in to_parse_correct:
        parser.reset()
        for c in tuple(p) + (end_symb, ):
            assert not parser.finished and not parser.success
            parser.step(c)
        else:
            print(p)
            assert parser.finished and parser.success


def test_copy() -> None:
    l = [
        ['the', 'an', "a", ""],
        ['orange', 'apple', 'banana']
    ]

    parser = MultiChoicesParser(l)

    parser.step('a')
    tests = l[1] + ['n'+x for x in l[1]]
    copies = [parser.copy(stateful=True) for _ in range(len(tests))]
    for test, c in zip(tests, copies):
        correct_test(test, c, reset=False)