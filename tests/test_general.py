import itertools
from typing import Iterator
from parser import MultiChoicesParser, end_symb
import pytest


def base_grammars():
    yield [
        ['the', 'an', "a"],
        ['orange', 'apple', 'banana']
    ]
    yield [
        ['the', 'an', "a", ""],
        ['orange', 'apple', 'banana']
    ]

def grammars() -> Iterator[list[list[str]]]:
    yield from base_grammars()
    yield [[' '],
    ['France', 'Paris', 'Madrid', 'Montréal', 'Berlin'],
    ['.']]

def grammar_expected_next():
    to_parse = 'theorange'
    nexts = [
        'oabt',
        'h',
        'e',
        'oab',
        'r',
        'a',
        'n',
        'g',
        'e',
        (end_symb, )
    ]
    return [
        (list(base_grammars())[1], to_parse, [tuple(x) for x in nexts if not isinstance(x, tuple)])
        ]



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
        assert not parser.success
        parser.step(c)
    assert not parser.success and parser.finished

@pytest.mark.parametrize(["grammar", "to_parse", "nexts"],
                         grammar_expected_next())
def test_next(grammar, to_parse, nexts) -> None:
    parser = MultiChoicesParser(grammar)
    for c, n in zip(tuple(to_parse) + (end_symb,), nexts):
        assert sorted(parser.next()) == sorted(n)
        parser.step(c)
    

@pytest.mark.parametrize("grammar",
                         grammars())
def test_alphabet(grammar) -> None:    
    parser = MultiChoicesParser(grammar)
    assert set(parser.alphabet) == set(c for y in grammar for x in y for c in x)

@pytest.mark.parametrize("grammar", grammars())
def test_parse_incorrect(grammar) -> None:
    parser = MultiChoicesParser(grammar)
    to_parse_incorrect = [
        ('z'),
        ("the"),
        ("appl"),
        ("a"),
        ("tzeorange")
    ]

    for p in to_parse_incorrect:
        incorrect_test(p, parser)

@pytest.mark.parametrize('grammar', grammars())
def test_parse_correct(grammar):

    parser = MultiChoicesParser(grammar)
    to_parse_correct = [
        ''.join(x) for x in itertools.product(*grammar)
    ]
    for p in to_parse_correct:
        correct_test(p, parser)

@pytest.mark.parametrize('grammar', base_grammars())
def test_copy(grammar):
    parser = MultiChoicesParser(grammar)

    parser.step('a')
    tests = grammar[1] + ['n'+x for x in grammar[1]]
    copies = [parser.copy(stateful=True) for _ in range(len(tests))]
    for test, c in zip(tests, copies):
        correct_test(test, c, reset=False)