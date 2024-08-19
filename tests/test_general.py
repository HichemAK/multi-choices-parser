import itertools
from multi_choices_parser.parser import MultiChoicesParser, end_symb


def test_parse_incorrect() -> None:
    l = [
        ['the', 'an', "a", ""],
        ['orange', 'apple', 'banana']
    ]

    parser = MultiChoicesParser(l)
    to_parse_incorrect = [
        ('z', True),
        ("the", True),
        ("appl", True),
        ("a", True),
        ("tzeorange", True)
    ]

    for p, check in to_parse_incorrect:
        parser.reset()
        for c in tuple(p) + (end_symb, ):
            if check:
                assert not parser.finished and not parser.success
            parser.step(c)
        assert not parser.success and parser.finished

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
        parser.reset()
        for c in tuple(p) + (end_symb, ):
            assert not parser.finished and not parser.success
            parser.step(c)
        else:
            print(p)
            assert parser.finished and parser.success

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