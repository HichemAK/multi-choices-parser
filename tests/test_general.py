import itertools
from choice_concat_parser import ChoicesConcatenationParser


def test_parse_incorrect() -> None:
    l = [
        ['the', 'an', "a", ""],
        ['orange', 'apple', 'banana']
    ]

    parser = ChoicesConcatenationParser(l)
    to_parse_incorrect = [
        'z',
        "the",
        "appl",
        "a",
        "tzeorange"
    ]

    for p in to_parse_incorrect:
        parser.reset()
        for c in p:
            parser.step(c)
        assert not parser.success

def test_parse_correct_without_empty():
    l = [
        ['the', 'an', "a"],
        ['orange', 'apple', 'banana']
    ]

    parser = ChoicesConcatenationParser(l)
    to_parse_correct = [
        x + y for x, y in itertools.product(l[0], l[1])
    ]

    for p in to_parse_correct:
        parser.reset()
        for c in p:
            parser.step(c)
            if parser.finished and parser.success:
                break
        else:
            print(p)
            assert False

def test_parse_correct_with_empty():
    l = [
        ['the', 'an', "a", ""],
        ['orange', 'apple', 'banana']
    ]

    parser = ChoicesConcatenationParser(l)
    to_parse_correct = [
        x + y for x, y in itertools.product(l[0], l[1])
    ]

    for p in to_parse_correct:
        parser.reset()
        for c in p:
            parser.step(c)
            if parser.finished and parser.success:
                break
        else:
            print(p)
            assert False