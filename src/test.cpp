// Software Name : multi-choices-parser
// SPDX-FileCopyrightText: Copyright (c) 2025 Orange SA
// SPDX-License-Identifier: GPL-2.0-or-later

// This software is distributed under the GNU General Public License v2.0 or later,
// see the "LICENSE.txt" file for more details or GNU General Public License v2.0 or later

// Authors: Hichem Ammar Khodja

#include <iostream>
#include <vector>
#include <memory>
#include "parser.h" // Include your parser implementation header

void test_accepts(std::shared_ptr<ParserNode> tree, const std::vector<std::vector<int>>& test_sequences) {
    ParserState state;
    state.nodes.push_back(tree);
    std::cout << "\nTesting sequences:\n";
    for (const auto& seq : test_sequences) {
        bool result = accepts(state, seq, false, false);
        std::cout << "Sequence { ";
        for (int c : seq) std::cout << c << " ";
        std::cout << "} is " << (result ? "ACCEPTED" : "REJECTED") << "\n";
    }
}

void test_step(std::shared_ptr<ParserNode> tree, const std::vector<int>& sequence) {
    std::cout << "\nTesting single-step traversal:\n";
    ParserState state;
    state.nodes.push_back(tree);

    for (int step_ : sequence) {
        std::cout << "Current node: " << state.nodes[0] << "\n";
        auto next_state = step(state, step_);
        if (next_state.nodes.size() == 0) {
            std::cout << "Step " << step_ << " failed! No valid transition.\n";
            break;
        }
        std::cout << "Step " << step_ << " succeeded. Moving to next node.\n";
        state = next_state;
    }
}

int main() {
    // Define groups of sequences
    std::vector<std::vector<std::vector<int>>> groups = {
        {{'t','h','e'}, {'a','n'}, {'a'}, {}}, 
        {{'o','r','a','n','g','e'}, {'a','p','p','l','e'}, {'b','a','n','a','n','a'}, {}}};
    
    // std::vector<std::vector<std::vector<int>>> groups = {
    //     {{'a'}, {'a', 'b'}}, {{'c'}}
    // };

    // Construct the parser tree
    std::cout << "Constructing the parser tree...\n";
    auto tree = construct_tree(groups, TransitionMode::HASH_MAP);

    // Print the tree structure for debugging
    std::cout << "\nParser tree structure:\n";
    // print_node(*tree);

    // Test sequences
    std::vector<std::vector<int>> test_sequences = {
        {'a','o','r','a','n','g','e',SpecialSymb::END}
    };

    // Test the accepts function
    test_accepts(tree, test_sequences);

    // Test single-step traversal
    std::vector<int> traversal_sequence = {97, 111, 114}; // Example valid sequence
    test_step(tree, traversal_sequence);

    return 0;
}
