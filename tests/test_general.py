# Software Name : multi-choices-parser
# SPDX-FileCopyrightText: Copyright (c) 2025 Orange SA
# SPDX-License-Identifier: GPL-2.0-or-later

# This software is distributed under the GNU General Public License v2.0 or later,
# see the "LICENSE.txt" file for more details or GNU General Public License v2.0 or later

# Authors: Hichem Ammar Khodja
import os.path as osp
import itertools
import json
from typing import Iterable, Iterator, List, Set, Tuple, Union

from multi_choices_parser.trie import MultiChoicesParserTrie, DEFAULT_END_SYMB
import pytest
import random

from multi_choices_parser.trie import ParserError

TEST_END_SYMBS = [DEFAULT_END_SYMB, "ezaoijoir", 2168721468721]

PARSER_CLASSES = [MultiChoicesParserTrie]


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

def grammars() -> Iterator[List[List[str]]]:
    yield from appleorange_grammars()
    yield [[' '],
    ['France', 'Paris', 'Madrid', 'Montréal', 'Berlin'],
    ['.']], None

    yield [[' '],
    ['France', 'Paris', 'Madrid', 'Montréal', 'Berlin', 'U.S. Open Cup', 'Manchester United F.C.', "Box Office U.S."],
    ['.']], None


def all_grammars() -> Iterator[List[List[str]]]:
    yield from grammars()
    yield from integer_grammars()
    yield from alphabet_constrained_grammars()

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
        ''
    ]
    yield list(appleorange_grammars())[1], to_parse, [tuple(x) for x in nexts if not isinstance(x, tuple)]
    grammar = [
        ['the', 'an', "a"],
        ['orange', 'apple', 'banana']
    ]
    alphabet = tuple('theanorgpbl') + ('anapp', 'le')
    to_parse = ('anapp',) + tuple('le')
    nexts = [
        tuple('ta') + ('anapp',),
        ('le','l'),
        ('e',),
        tuple()
    ]
    yield (grammar, alphabet), to_parse, nexts


    grammar = [[
        [6342],
        [14708],
        [6342, 31248],
        [25866, 8290, 275, 472, 12303, 10682, 2806, 16426]
    ]]
    alphabet = None
    to_parse = [14708]
    nexts = [
        [6342, 14708, 25866],
        [],
    ]
    yield (grammar, alphabet), to_parse, nexts

def alphabet_constrained_grammars():
    yield [
        ['the', 'an', "a"],
        ['orange', 'apple', 'banana']
    ], 'theanorgplb'
    yield [
        ['the', 'an', "a"],
        ['orange', 'apple', 'banana']
    ], tuple('theanorglbp') + ('pp',)   
    yield [
        ['the', 'an', "a"],
        ['orange', 'apple', 'banana']
    ], tuple('theanorglb') + ('pp',)


    # Real world grammars (the alphabet is from the GPT2 tokenizer 
    # and the entities are the first entities from Wikidata)
    root = osp.dirname(__file__)
    entities = json.load(open(osp.join(root, 'choices.json')))
    alphabet = json.load(open(osp.join(root, 'alphabet.json')))
    
    yield [[' '],
    entities,
    ['.']], None

    yield [[' '],
    entities,
    ['.']], alphabet

    # yield [[' '],
    # entities,
    # ['.']], ["Ġ" + x for x in alphabet]

def adapt_grammar_to_parser(grammar, parser_class):
    if parser_class is MultiChoicesParserTrie:
        choice1 = grammar[0][0][0]
        if isinstance(choice1, tuple) and isinstance(choice1[0], int):
            grammar = [[[x[0] for x in choice] for choice in choices] for choices in grammar]
    return grammar


def create_parser(parser_class, grammar, alphabet=None, end_symb=DEFAULT_END_SYMB):
    """Helper to create parser with transition_mode support."""
    if parser_class is MultiChoicesParserTrie:
        return parser_class(grammar, alphabet=alphabet, end_symb=end_symb)
    return parser_class(grammar, alphabet=alphabet, end_symb=end_symb)

def split_according_to_alphabet(text : Union[str, List[int]], alphabet : Union[str, Tuple[Union[str, Tuple[int]]]]) -> Tuple[list, bool]:
    if alphabet is None:
        return text, True
    res = []
    alphaset = set(alphabet)
    buf = []
    all_str = True
    for ch in text:
        buf.append(ch)
        all_str &= isinstance(ch, str)
        if all_str:
            letter = ''.join(itertools.chain(*buf))
        else:
            letter = tuple(itertools.chain(*buf))
        if letter in alphaset:
            res.append(letter)
            buf.clear()
            all_str = True
    return res, len(buf) == 0

def correct_test(to_parse : str, parser : MultiChoicesParserTrie, reset=True, test_accept=True) -> None:
    random.seed(42112)
    if reset:
        parser.reset()
        assert parser.is_at_initial_state
    initial_parser = parser.copy()
    to_parse2 = list(to_parse)
    to_parse, success = split_according_to_alphabet(to_parse2, parser.alphabet)
    to_parse += [parser.end_symb]
    if not success:
        return
    for c in to_parse:
        # Verify that parser is not finished while the parsing did not end
        assert not parser.finished and not parser.success
        parser.step(c)
        assert not parser.is_at_initial_state

        # Verify that initial parser and post-step parsers are different
        assert initial_parser != parser and hash(initial_parser) != hash(parser)
    else:
        print(to_parse)
        assert parser.finished and parser.success
        assert not parser.is_at_initial_state
        assert len(parser.next()) == 0
    if test_accept:
        # Test .accepts method
        parser.reset()
        assert parser.accepts(to_parse)

    parser.accepts(to_parse[:random.randint(0, len(to_parse)-1)])

def incorrect_test(to_parse : str, parser : MultiChoicesParserTrie) -> None:
    parser.reset()
    to_parse = tuple(to_parse) + (parser.end_symb, )
    for c in to_parse:
        assert not parser.success
        try:
            parser.step(c)
        except ParserError:
            break
        assert not parser.is_at_initial_state
    assert not parser.success and parser.finished
    parser.reset()
    assert not parser.accepts(to_parse)

@pytest.mark.parametrize('parser_class', PARSER_CLASSES)
@pytest.mark.parametrize(["grammar_alphabet", "to_parse", "nexts"],
                         grammar_expected_next())
@pytest.mark.parametrize('end_symb', TEST_END_SYMBS)
def test_next(parser_class, grammar_alphabet, to_parse, nexts, end_symb) -> None:
    grammar, alphabet = grammar_alphabet
    if alphabet is not None and parser_class is MultiChoicesParserTrie:
        pytest.skip("%s does not support this feature yet" % parser_class.__name__)
    grammar = adapt_grammar_to_parser(grammar, parser_class)
    parser = create_parser(parser_class, grammar, alphabet=alphabet, end_symb=end_symb)
    nexts = nexts + [(end_symb, )]
    for c, n in zip(list(split_according_to_alphabet(to_parse, parser.alphabet)[0]) + [end_symb], nexts):
        if c is end_symb:
            n = list(n) + [end_symb]
        assert sorted(parser.next()) == sorted(n)
        parser.step(c)

    

@pytest.mark.parametrize("grammar_alphabet",
                         all_grammars())
@pytest.mark.parametrize('end_symb', TEST_END_SYMBS)
@pytest.mark.parametrize('parser_class', PARSER_CLASSES)
def test_alphabet(parser_class, grammar_alphabet, end_symb) -> None:
    grammar, alphabet = grammar_alphabet
    if parser_class is MultiChoicesParserTrie:
        pytest.skip("%s does not support this feature yet" % parser_class.__name__)
    parser = create_parser(parser_class, grammar, alphabet=alphabet, end_symb=end_symb)
    if alphabet is None:
        assert set(parser.alphabet) == set(c for y in grammar for x in y for c in x)

@pytest.mark.parametrize("grammar_alphabet", all_grammars())
@pytest.mark.parametrize('end_symb', TEST_END_SYMBS)
@pytest.mark.parametrize('parser_class', PARSER_CLASSES)
def test_parse_incorrect(parser_class, grammar_alphabet, end_symb) -> None:
    grammar, alphabet = grammar_alphabet
    if alphabet is not None and parser_class is MultiChoicesParserTrie:
        pytest.skip("%s does not support this feature yet" % parser_class.__name__)
    grammar = adapt_grammar_to_parser(grammar, parser_class)
    parser = create_parser(parser_class, grammar, alphabet=alphabet, end_symb=end_symb)
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
@pytest.mark.parametrize('end_symb', TEST_END_SYMBS)
@pytest.mark.parametrize('parser_class', PARSER_CLASSES)

def test_parse_correct(parser_class, grammar_alphabet, end_symb):

    grammar, alphabet = grammar_alphabet
    if alphabet is not None and parser_class is MultiChoicesParserTrie:
        pytest.skip("%s does not support this feature yet" % parser_class.__name__)
    grammar = adapt_grammar_to_parser(grammar, parser_class)
    parser = create_parser(parser_class, grammar, alphabet=alphabet, end_symb=end_symb)
    to_parse_correct = [
        itertools.chain(*x) for x in itertools.product(*grammar)
    ]
    for p in to_parse_correct:
        correct_test(p, parser)

@pytest.mark.parametrize('grammar_alphabet', appleorange_grammars())
@pytest.mark.parametrize('end_symb', TEST_END_SYMBS)
@pytest.mark.parametrize('parser_class', PARSER_CLASSES)

def test_copy(parser_class, grammar_alphabet, end_symb):
    grammar, alphabet = grammar_alphabet
    if alphabet is not None and parser_class is MultiChoicesParserTrie:
        pytest.skip("%s does not support this feature yet" % parser_class.__name__)
    grammar = adapt_grammar_to_parser(grammar, parser_class)
    parser = create_parser(parser_class, grammar, alphabet=alphabet, end_symb=end_symb)

    parser.step('a')
    tests = grammar[1] + ['n'+x for x in grammar[1]]
    copies = [parser.copy(stateful=True) for _ in range(len(tests))]
    assert all(x == parser and hash(x) == hash(parser) for x in copies)
    for test, c in zip(tests, copies):
        correct_test(test, c, reset=False, test_accept=False)

def extract_all_correct_sequences(parser : MultiChoicesParserTrie, buf : list) -> Iterable[str]:
    result = []
    n = parser.next()
    if len(n) == 0:
        yield ''.join(buf)
    for c in n:
        parser_ = parser.copy()
        parser_.step(c)
        buf_ = buf.copy()
        if c is not parser.end_symb:
            buf_.append(c)
        yield from extract_all_correct_sequences(parser_, buf_)


def extensive_toy_grammars(n : int) -> Tuple[Iterable, list]:
    possible_choices = [''.join(x).replace('_', '') for x in itertools.product('ab_','ab_')]
    possible_groups = list(itertools.combinations(possible_choices, 2))
    possible_grammars = itertools.product(*([possible_groups]*n))
    all_strings = list(''.join(x).replace('_', '') for x in itertools.product(*['ab_']*n))
    return possible_grammars, all_strings

def full_test(parser, to_parse_correct : Set[str], all_strings : List[str]) -> None:
    for p in to_parse_correct:
        correct_test(p, parser)
    for p in all_strings:
        if p not in to_parse_correct:
            incorrect_test(p, parser)
    all_correct_seq = sorted(extract_all_correct_sequences(parser, []))
    assert set(all_correct_seq) == to_parse_correct

def get_all_correct_sequences(grammar : List[List[str]]) -> Set[str]:
    return set(
        "".join(itertools.chain(*x)) for x in itertools.product(*grammar)
    )

@pytest.mark.parametrize('parser_class', PARSER_CLASSES)

def test_stress(parser_class):
    N_LIST = 3
    possible_grammars, all_strings = extensive_toy_grammars(N_LIST)

    for grammar in possible_grammars:
        parser = create_parser(parser_class, grammar)
        to_parse_correct = get_all_correct_sequences(grammar)
        full_test(parser, to_parse_correct, all_strings)

@pytest.mark.parametrize('parser_class', PARSER_CLASSES)

def test_add_sequence(parser_class):
    N_LIST = 2
    possible_grammars, all_strings = extensive_toy_grammars(N_LIST)
    for grammar in possible_grammars:
        parser = create_parser(parser_class, grammar)
        to_parse_correct = get_all_correct_sequences(grammar)
        for i in range(4):
            toadd = random.choice(tuple(to_parse_correct)) + chr(99+i) # WARNING: Inefficient sampling
            to_parse_correct.add(toadd)
            assert parser.add_sequence(toadd)
            assert not parser.add_sequence(toadd)
            full_test(parser, to_parse_correct, all_strings)


# @pytest.mark.parametrize('parser_class', PARSER_CLASSES)
# def test_delete_sequence(parser_class):
#     N_LIST = 2
#     possible_grammars, all_strings = extensive_toy_grammars(N_LIST)
#     for grammar in possible_grammars:
#         parser = parser_class(grammar)
#         to_parse_correct = get_all_correct_sequences(grammar)
#         for _ in range(4):
#             if len(to_parse_correct):
#                 torm = random.choice(tuple(to_parse_correct)) # WARNING: Inefficient sampling
#                 to_parse_correct.remove(torm)
#                 assert parser.delete_sequence(torm)
#                 assert not parser.delete_sequence(torm)
#                 full_test(parser, to_parse_correct, all_strings)