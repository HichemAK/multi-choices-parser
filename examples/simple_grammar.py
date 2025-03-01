# Software Name : multi-choices-parser
# SPDX-FileCopyrightText: Copyright (c) 2025 Orange SA
# SPDX-License-Identifier: GPL-2.0-or-later

# This software is distributed under the GNU General Public License v2.0 or later,
# see the "LICENSE.txt" file for more details or GNU General Public License v2.0 or later

# Authors: Hichem Ammar Khodja

from multi_choices_parser import MultiChoicesParser, DEFAULT_END_SYMB


l = [
    ['the', 'an', "a", ""],
    ['orange', 'apple', 'banana']
]
p = MultiChoicesParser(l)

for i, c in enumerate(tuple("apple") + (DEFAULT_END_SYMB, )):
    print('Step %s' % i)
    print("Authorized characters:", sorted(p.next()))
    print('Adding character:', c)
    p.step(c)
    print("State: Finished=%s, Success=%s" % (p.finished, p.success))
    print()
