// Software Name : multi-choices-parser
// SPDX-FileCopyrightText: Copyright (c) 2025 Orange SA
// SPDX-License-Identifier: GPL-2.0-or-later

// This software is distributed under the GNU General Public License v2.0 or later,
// see the "LICENSE.txt" file for more details or GNU General Public License v2.0 or later

// Authors: Hichem Ammar Khodja

#ifndef PARSER_H
#define PARSER_H

#include <vector>
#include <memory>

enum SpecialSymb {END=-2147483647, EPS=-2147483648};
const char NUM_SPECIAL_SYMB = 2;

// Forward declaration of ParserNode
struct ParserNode;

// Transition structure
struct Transition {
    int character;                // Character for the transition
    std::shared_ptr<ParserNode> next;  // Shared pointer to the next node
};

// ParserNode structure
struct ParserNode {
    std::vector<Transition> transitions;  // List of transitions from this node

    // Add a transition to another node
    void add_transition(int character, std::shared_ptr<ParserNode> next_node) {
        transitions.push_back({character, next_node});
    }
};

// ParserState structure to hold nodes
struct ParserState {
    std::vector<std::shared_ptr<ParserNode>> nodes;

    // Add a node to the state
    void add_node(std::shared_ptr<ParserNode> node) {
        nodes.push_back(node);
    }
};

// Function to construct a tree for a single group of sequences
std::tuple<std::shared_ptr<ParserNode>, bool> build_group_tree(
    const std::vector<std::vector<int>>& group, std::vector<std::shared_ptr<ParserNode>>& final_nodes
);

// Function to connect multiple group trees with epsilon transitions
void connect_trees(const std::vector<std::tuple<std::shared_ptr<ParserNode>, bool>>& group_trees, 
std::vector<std::vector<std::shared_ptr<ParserNode>>>& final_nodes_per_group);

// Function to construct the full parser tree from groups of sequences
std::shared_ptr<ParserNode> construct_tree(const std::vector<std::vector<std::vector<int>>>& groups);


bool add_sequence(
    std::shared_ptr<ParserNode> root, 
    const std::vector<int>& sequence, 
    std::vector<std::shared_ptr<ParserNode>>& final_nodes,
    bool add_last
);

bool delete_sequence(std::shared_ptr<ParserNode> root, const std::vector<int>& sequence);

// Function to check if the parser accepts a given sequence of characters
bool accepts(ParserState& state, const std::vector<int>& sequence, bool must_end, bool end_symb_expected);

// Function to perform a single step in the parser with the given character
ParserState step(const ParserState& state, int character);

bool special_symb_in_transitions(const ParserState& state, const SpecialSymb symb);
bool special_symb_in_transitions(const std::vector<Transition>& transitions, const SpecialSymb symb);
std::vector<int> next(const ParserState& state);

#endif // PARSER_H
