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

/**
 * @brief A trie data structure for a single choice group.
 *
 * Encapsulates a prefix tree (trie) built from a set of sequences.
 * Each trie represents one "choice group" in the grammar, where
 * any of the sequences in the group can be matched.
 *
 * Example: For choices ["the", "an", "a"], the trie efficiently
 * represents all three options with shared prefixes.
 */
class Trie {
private:
    std::shared_ptr<ParserNode> root_;
    std::vector<std::shared_ptr<ParserNode>> final_nodes_;
    bool is_nullable_;

public:
    /**
     * @brief Construct a trie from a group of sequences.
     * @param sequences Vector of integer sequences to add to the trie.
     *                  Empty sequences mark the trie as nullable.
     */
    explicit Trie(const std::vector<std::vector<int>>& sequences);

    /**
     * @brief Add a sequence to this trie dynamically.
     * @param sequence The sequence to add.
     * @return true if new nodes were created, false if sequence already existed.
     */
    bool add_sequence(const std::vector<int>& sequence);

    /** @brief Get the root node of this trie. */
    std::shared_ptr<ParserNode> root() const { return root_; }

    /** @brief Get the final nodes (sequence endpoints) of this trie. */
    const std::vector<std::shared_ptr<ParserNode>>& final_nodes() const { return final_nodes_; }

    /** @brief Check if this trie accepts the empty sequence. */
    bool is_nullable() const { return is_nullable_; }
};

/**
 * @brief Concatenates multiple tries to form a complete grammar.
 *
 * Connects a sequence of tries with epsilon transitions, allowing
 * the parser to match one choice from each group in order.
 *
 * Example: For grammar [["the", "a"], ["cat", "dog"]], this connects
 * the two tries so "the cat", "the dog", "a cat", "a dog" are all valid.
 *
 * Handles nullable tries by adding skip transitions.
 */
class TrieConcatenation {
private:
    std::vector<Trie> tries_;
    std::shared_ptr<ParserNode> root_;

    /** @brief Connect tries with epsilon/end transitions. */
    void connect();

public:
    /**
     * @brief Construct a concatenation from a vector of tries.
     * @param tries Vector of tries to concatenate. Takes ownership via move.
     */
    explicit TrieConcatenation(std::vector<Trie> tries);

    /** @brief Get the root node for parser state initialization. */
    std::shared_ptr<ParserNode> root() const { return root_; }

    /** @brief Get access to the individual tries. */
    const std::vector<Trie>& tries() const { return tries_; }
};

// Legacy function - use Trie class instead
// @deprecated Use Trie constructor for building group trees
std::tuple<std::shared_ptr<ParserNode>, bool> build_group_tree(
    const std::vector<std::vector<int>>& group, std::vector<std::shared_ptr<ParserNode>>& final_nodes
);

// Legacy function - use TrieConcatenation class instead
// @deprecated Use TrieConcatenation for connecting tries
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
