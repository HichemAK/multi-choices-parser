import itertools
import re
from typing import Iterator
from parser import MultiChoicesParser, end_symb
import pytest

def appleorange_grammars():
    yield [
        ['the', 'an', "a"],
        ['orange', 'apple', 'banana']
    ], None
    yield [
        ['the', 'an', "a", ""],
        ['orange', 'apple', 'banana']
    ], None
    yield [
        ['the', 'an', "a", ""],
        ['orange', 'apple', 'banana', '']
    ], None

def integer_grammars():
    for grammar, _ in grammars():
        alphabet = set()
        for l in grammar:
            for c in l:
                for a in c:
                    alphabet.add(a)
        alphabet = {k:i for i,k in enumerate(alphabet)}
        int_grammar = []
        for l in grammar:
            nl = []
            for c in l:
                nc = []
                for a in c:
                    nc.append((alphabet[a],))
                nl.append(nc)
            int_grammar.append(nl)
        yield int_grammar, None

def grammars() -> Iterator[list[list[str]]]:
    yield from appleorange_grammars()
    yield [[' '],
    ['France', 'Paris', 'Madrid', 'Montréal', 'Berlin'],
    ['.']], None

    yield [[' '],
    ['France', 'Paris', 'Madrid', 'Montréal', 'Berlin', 'U.S. Open Cup', 'Manchester United F.C.', "Box Office U.S."],
    ['.']], None

def all_grammars() -> Iterator[list[list[str]]]:
    yield from grammars()
    yield from integer_grammars()
    yield from alphabet_contrained_grammars()

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
    yield list(appleorange_grammars())[1], to_parse, [tuple(x) for x in nexts if not isinstance(x, tuple)]

def alphabet_contrained_grammars():
    yield [
        ['the', 'an', "a"],
        ['orange', 'apple', 'banana']
    ], tuple((x,) for x in 'theanorgplb')
    yield [
        ['the', 'an', "a"],
        ['orange', 'apple', 'banana']
    ], tuple((x,) for x in 'theanorglbp') + (tuple('pp'),)   
    yield [
        ['the', 'an', "a"],
        ['orange', 'apple', 'banana']
    ], tuple((x,) for x in 'theanorglb') + (tuple('pp'),)  

def split_according_to_alphabet(text : str | list[int], alphabet : str | tuple[str | tuple[int]]) -> list:
    res = []
    alphaset = set(alphabet)
    buf = []
    for ch in text:
        buf.append(ch)
        if (letter := tuple(itertools.chain(*buf))) in alphaset:
            res.append(letter)
            buf.clear()
    return res

def correct_test(to_parse : str, parser : MultiChoicesParser, reset=True) -> None:
    if reset:
        parser.reset()
    to_parse = split_according_to_alphabet(to_parse, parser.alphabet) + [end_symb]
    # to_parse = tuple(to_parse) + (end_symb, )
    for c in to_parse:
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

@pytest.mark.parametrize(["grammar_alphabet", "to_parse", "nexts"],
                         grammar_expected_next())
def test_next(grammar_alphabet, to_parse, nexts) -> None:
    grammar, alphabet = grammar_alphabet
    parser = MultiChoicesParser(grammar, alphabet)
    for c, n in zip(split_according_to_alphabet(to_parse, parser.alphabet) + [end_symb], nexts):
        assert sorted(parser.next()) == sorted((x,) for x in n)
        parser.step(c)
    

@pytest.mark.parametrize("grammar_alphabet",
                         all_grammars())
def test_alphabet(grammar_alphabet) -> None:    
    grammar, alphabet = grammar_alphabet
    parser = MultiChoicesParser(grammar, alphabet)
    if alphabet is None:
        assert set(parser.alphabet) == set(tuple(c) for y in grammar for x in y for c in x)

@pytest.mark.parametrize("grammar_alphabet", all_grammars())
def test_parse_incorrect(grammar_alphabet) -> None:
    grammar, alphabet = grammar_alphabet
    parser = MultiChoicesParser(grammar, alphabet)
    to_parse_incorrect = [
        ('z'),
        ("them"),
        ("appl"),
        ("ana"),
        ("tzeorange")
    ]

    for p in to_parse_incorrect:
        incorrect_test(p, parser)

@pytest.mark.parametrize('grammar_alphabet', all_grammars())
def test_parse_correct(grammar_alphabet):

    grammar, alphabet = grammar_alphabet
    parser = MultiChoicesParser(grammar, alphabet)
    to_parse_correct = [
        itertools.chain(*x) for x in itertools.product(*grammar)
    ]
    for p in to_parse_correct:
        correct_test(p, parser)

@pytest.mark.parametrize('grammar_alphabet', appleorange_grammars())
def test_copy(grammar_alphabet):
    grammar, alphabet = grammar_alphabet
    parser = MultiChoicesParser(grammar, alphabet)

    parser.step(('a',))
    tests = grammar[1] + ['n'+x for x in grammar[1]]
    copies = [parser.copy(stateful=True) for _ in range(len(tests))]
    for test, c in zip(tests, copies):
        correct_test(test, c, reset=False)