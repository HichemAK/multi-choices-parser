// Software Name : multi-choices-parser
// SPDX-FileCopyrightText: Copyright (c) 2025 Orange SA
// SPDX-License-Identifier: GPL-2.0-or-later

// This software is distributed under the GNU General Public License v2.0 or later,
// see the "LICENSE.txt" file for more details or GNU General Public License v2.0 or later

// Authors: Hichem Ammar Khodja

#include <vector>
#include <memory>
#include <algorithm>
#include <functional>
#include "parser.h"


template <typename T, typename Compare>
typename std::vector<T>::iterator insertIntoOrderedVector(
    std::vector<T>& vec, 
    const T& element, 
    Compare comp) 
{
    auto it = std::lower_bound(vec.begin(), vec.end(), element, comp); // Find the correct position
    if (it == vec.end() || comp(element, *it)) { // Ensure no duplication
        return vec.insert(it, element); // Insert the element if not a duplicate
    }
    return it; // Return iterator to the existing element
}

template <typename T, typename Compare>
const T* findInVector(const std::vector<T>& vec, const T& element, Compare comp) {
    auto it = std::lower_bound(vec.begin(), vec.end(), element, comp); // Find the position
    if (it != vec.end() && !comp(element, *it) && !comp(*it, element)) {
        return &(*it); // Return a pointer to the found object
    }
    return nullptr; // Return nullptr if not found
}

auto comp_characters = [](const Transition& a, const Transition& b) {
    return a.character < b.character;
};

// ParserNode method implementations

void ParserNode::add_transition(int character, std::shared_ptr<ParserNode> next_node) {
    if (mode == TransitionMode::HASH_MAP) {
        transitions_map[character] = next_node;
    } else {
        // SORTED_ARRAY mode: use ordered insertion
        Transition to_add = {character, next_node};
        insertIntoOrderedVector(transitions, to_add, comp_characters);
    }
}

std::shared_ptr<ParserNode> ParserNode::find_transition(int character) const {
    if (mode == TransitionMode::HASH_MAP) {
        auto it = transitions_map.find(character);
        if (it != transitions_map.end()) {
            return it->second;
        }
        return nullptr;
    } else {
        // SORTED_ARRAY mode: use binary search
        auto result = findInVector(transitions, Transition{character, nullptr}, comp_characters);
        if (result != nullptr) {
            return result->next;
        }
        return nullptr;
    }
}

std::vector<Transition> ParserNode::get_all_transitions() const {
    if (mode == TransitionMode::HASH_MAP) {
        std::vector<Transition> result;
        result.reserve(transitions_map.size());
        for (const auto& pair : transitions_map) {
            result.push_back({pair.first, pair.second});
        }
        return result;
    } else {
        return transitions;
    }
}

bool ParserNode::has_transition(int character) const {
    if (mode == TransitionMode::HASH_MAP) {
        return transitions_map.find(character) != transitions_map.end();
    } else {
        return findInVector(transitions, Transition{character, nullptr}, comp_characters) != nullptr;
    }
}

// Trie class implementation

Trie::Trie(const std::vector<std::vector<int>>& sequences, TransitionMode mode)
    : root_(std::make_shared<ParserNode>(mode)), is_nullable_(false), mode_(mode) {
    for (const auto& sequence : sequences) {
        if (sequence.empty()) {
            is_nullable_ = true;
        } else {
            ::add_sequence(root_, sequence, final_nodes_, true);
        }
    }
}

bool Trie::add_sequence(const std::vector<int>& sequence) {
    return ::add_sequence(root_, sequence, final_nodes_, true);
}

// TrieConcatenation class implementation

TrieConcatenation::TrieConcatenation(std::vector<Trie> tries)
    : tries_(std::move(tries)) {
    if (tries_.empty()) {
        root_ = nullptr;
    } else {
        root_ = tries_[0].root();
        connect();
    }
}

void TrieConcatenation::connect() {
    int n = tries_.size();
    for (int i = 0; i < n; i++) {
        const auto& trie = tries_[i];
        const auto& final_nodes = trie.final_nodes();
        TransitionMode mode = trie.mode();

        // Determine what to connect to: next trie's root or nullptr (end)
        std::shared_ptr<ParserNode> next_root = (i < n - 1) ? tries_[i + 1].root() : nullptr;
        int ch = (next_root == nullptr) ? END : EPS;

        // Connect final nodes to next trie (or END)
        for (const auto& final_node : final_nodes) {
            if (final_node) {
                if (mode == TransitionMode::HASH_MAP) {
                    final_node->transitions_map[ch] = next_root;
                } else {
                    Transition to_add = {ch, next_root};
                    insertIntoOrderedVector(final_node->transitions, to_add, comp_characters);
                }
            }
        }

        // If this trie is nullable, also connect its root to the next trie
        if (trie.is_nullable() && i < n - 1) {
            if (mode == TransitionMode::HASH_MAP) {
                trie.root()->transitions_map[EPS] = next_root;
            } else {
                Transition to_add = {EPS, next_root};
                insertIntoOrderedVector(trie.root()->transitions, to_add, comp_characters);
            }
        } else if (trie.is_nullable() && i == n - 1) {
            // Last trie is nullable - connect root to END
            if (mode == TransitionMode::HASH_MAP) {
                trie.root()->transitions_map[END] = nullptr;
            } else {
                Transition to_add = {END, nullptr};
                insertIntoOrderedVector(trie.root()->transitions, to_add, comp_characters);
            }
        }
    }
}

// Function to add a sequence to a tree
// Returns the end node pointer if exists else null pointer
bool add_sequence(
    std::shared_ptr<ParserNode> root,
    const std::vector<int>& sequence,
    std::vector<std::shared_ptr<ParserNode>>& final_nodes,
    bool add_last = true
)
{
    auto current_node = root;
    auto created = false;
    TransitionMode mode = root->mode;

    for (size_t i = 0; i < sequence.size(); i++) {
        auto character = sequence[i];

        if (mode == TransitionMode::HASH_MAP) {
            // HASH_MAP mode
            auto it = current_node->transitions_map.find(character);
            if (it == current_node->transitions_map.end()) {
                // Create new node if needed
                if (i != sequence.size()-1 || add_last) {
                    auto new_node = std::make_shared<ParserNode>(mode);
                    current_node->transitions_map[character] = new_node;
                    created = true;
                    if (i == sequence.size()-1) {
                        final_nodes.push_back(new_node);
                    }
                    current_node = new_node;
                } else {
                    current_node->transitions_map[character] = nullptr;
                    final_nodes.push_back(nullptr);
                    current_node = nullptr;
                }
            } else {
                if (it->second == nullptr && (i != sequence.size()-1 || add_last)) {
                    it->second = std::make_shared<ParserNode>(mode);
                    created = true;
                }
                if (i == sequence.size()-1) {
                    final_nodes.push_back(it->second);
                }
                current_node = it->second;
            }
        } else {
            // SORTED_ARRAY mode (original logic)
            Transition to_add = {character, nullptr};
            auto it = insertIntoOrderedVector(current_node->transitions, to_add, comp_characters);
            if (it->next == nullptr && (i != sequence.size()-1 || add_last)){
                it->next = std::make_shared<ParserNode>(mode);
                created = true;
            }
            if(i == sequence.size()-1){
                final_nodes.push_back(it->next);
            }
            current_node = it->next;
        }
    }
    return created;
}

bool delete_sequence(std::shared_ptr<ParserNode> root, const std::vector<int>& sequence) {
    if (!root || sequence.empty()) {
        return false; // Invalid input or empty sequence
    }

    struct PathNode {
        std::shared_ptr<ParserNode> node;
        size_t transition_index;
    };

    std::vector<std::vector<PathNode>> paths_to_delete; // Store all valid paths to delete
    std::vector<PathNode> current_path; // Track the current path during traversal

    // Recursive function to explore all paths
    std::function<void(std::shared_ptr<ParserNode>, size_t)> explore_paths = [&](std::shared_ptr<ParserNode> current_node, size_t seq_index) {
        if (seq_index == sequence.size()) {
            // If the sequence is fully matched, store the path
            paths_to_delete.push_back(current_path);
            return;
        }

        int character = sequence[seq_index];
        for (size_t i = 0; i < current_node->transitions.size(); ++i) {
            const auto& transition = current_node->transitions[i];

            if (transition.character == SpecialSymb::EPS) {
                // Follow epsilon transitions
                current_path.push_back({current_node, i});
                explore_paths(transition.next, seq_index);
                current_path.pop_back();
            } else if (transition.character == character) {
                // Follow matching character transitions
                current_path.push_back({current_node, i});
                explore_paths(transition.next, seq_index + 1);
                current_path.pop_back();
            }
        }
    };

    // Start exploring paths from the root
    explore_paths(root, 0);

    // Backtrack to delete all valid paths
    bool deleted = false;
    for (const auto& path : paths_to_delete) {
        for (auto it = path.rbegin(); it != path.rend(); ++it) {
            auto& [node, index] = *it;
            auto& transition = node->transitions[index];

            // If the transition's next node has no further transitions, delete it
            if (transition.next && transition.next->transitions.empty()) {
                transition.next.reset();
            }

            // Remove the transition itself
            node->transitions.erase(node->transitions.begin() + index);

            // Stop if the current node still has other transitions
            if (!node->transitions.empty()) {
                break;
            }
        }
        deleted = true;
    }

    return deleted; // Return true if at least one path was deleted
}


// Function to build a tree for a single group
std::tuple<std::shared_ptr<ParserNode>, bool> build_group_tree(
    const std::vector<std::vector<int>>& group, std::vector<std::shared_ptr<ParserNode>>& final_nodes
) {
    bool is_nullable = false;
    auto root = std::make_shared<ParserNode>();
    
    for (size_t i = 0; i<group.size(); i++) {
        const auto& sequence = group[i];
        if (sequence.empty()) {
            is_nullable = true; // Mark the group as nullable if it contains an empty sequence
        } else {
            add_sequence(root, sequence, final_nodes);
        }
    }

    return {root, is_nullable};
}

// Function to connect multiple group trees with epsilon transitions
void connect_trees(const std::vector<std::tuple<std::shared_ptr<ParserNode>, bool>>& group_trees, 
std::vector<std::vector<std::shared_ptr<ParserNode>>>& final_nodes_per_group) {
    int n = group_trees.size();
    for (size_t i = 0; i < n-1; i++){
        auto group_tree = std::get<0>(group_trees[i]);
        auto is_nullable = std::get<1>(group_trees[i]);
        auto final_nodes = final_nodes_per_group[i];
        auto next_group_tree = std::get<0>(group_trees[i+1]);
        auto ch = next_group_tree == nullptr ? END : EPS;
        for (size_t j = 0; j < final_nodes.size(); j++)
        {
            Transition to_add = Transition{ch, next_group_tree}; 
            insertIntoOrderedVector(final_nodes[j]->transitions, to_add, comp_characters);
        }
        if (is_nullable){
            Transition to_add = Transition{next_group_tree != nullptr ? EPS : END, next_group_tree};
            insertIntoOrderedVector(group_tree->transitions, to_add, comp_characters);
        }
    }
}

// Function to construct the final tree using new Trie and TrieConcatenation classes
std::shared_ptr<ParserNode> construct_tree(const std::vector<std::vector<std::vector<int>>>& groups,
                                            TransitionMode mode) {
    if (groups.empty()) {
        return nullptr;
    }

    // Build a Trie for each group with the specified mode
    std::vector<Trie> tries;
    tries.reserve(groups.size());
    for (const auto& group : groups) {
        tries.emplace_back(group, mode);
    }

    // Connect the tries and return the root
    TrieConcatenation concatenation(std::move(tries));
    return concatenation.root();
}

int min(int a, int b){
    return a < b ? a : b;
}

// Unwrap epsilon transitions for SORTED_ARRAY mode
void unwrap(const std::vector<Transition>& transitions, std::vector<const std::vector<Transition>*>& result) {
    result.push_back(&transitions);
    if (!transitions.empty() && transitions[0].character == SpecialSymb::EPS){
        unwrap(transitions[0].next->transitions, result);
    }
}

// Unwrap epsilon transitions for a node (mode-aware)
void unwrap_node(const std::shared_ptr<ParserNode>& node, std::vector<std::shared_ptr<ParserNode>>& result) {
    if (!node) return;
    result.push_back(node);

    if (node->mode == TransitionMode::HASH_MAP) {
        auto it = node->transitions_map.find(SpecialSymb::EPS);
        if (it != node->transitions_map.end() && it->second) {
            unwrap_node(it->second, result);
        }
    } else {
        if (!node->transitions.empty() && node->transitions[0].character == SpecialSymb::EPS) {
            unwrap_node(node->transitions[0].next, result);
        }
    }
}

bool special_symb_in_transitions(const std::vector<Transition>& transitions, const SpecialSymb symb){
    for (size_t i = 0; i < min(transitions.size(), NUM_SPECIAL_SYMB); i++)
    {
        if (symb == transitions[i].character){
            return true;
        }
    }
    return false;
}

// Mode-aware version for ParserNode
bool special_symb_in_node(const std::shared_ptr<ParserNode>& node, const SpecialSymb symb) {
    if (!node) return false;

    if (node->mode == TransitionMode::HASH_MAP) {
        return node->transitions_map.find(symb) != node->transitions_map.end();
    } else {
        return special_symb_in_transitions(node->transitions, symb);
    }
}

bool special_symb_in_transitions(const ParserState& state, const SpecialSymb symb){
    for (size_t i = 0; i < state.nodes.size(); i++)
    {
        if(state.nodes[i] == nullptr){
            continue;
        }
        if (special_symb_in_node(state.nodes[i], symb)){
            return true;
        }
    }
    return false;
}

bool accepts(ParserState& state, const std::vector<int>& sequence, bool must_end, bool end_symb_expected) {
    ParserState current_state = state;
    for (int character : sequence) {
        ParserState next_state;
        for (auto& node : current_state.nodes)
        {
            // Unwrap epsilon transitions
            if (node == nullptr){
                continue;
            }

            std::vector<std::shared_ptr<ParserNode>> unwrapped_nodes;
            unwrap_node(node, unwrapped_nodes);

            for (const auto& unwrapped : unwrapped_nodes) {
                if (!unwrapped) continue;

                std::shared_ptr<ParserNode> next_node = unwrapped->find_transition(character);
                if (next_node || unwrapped->has_transition(character)) {
                    // has_transition checks if transition exists (even to nullptr)
                    if (unwrapped->mode == TransitionMode::HASH_MAP) {
                        auto it = unwrapped->transitions_map.find(character);
                        if (it != unwrapped->transitions_map.end()) {
                            next_state.nodes.push_back(it->second);
                        }
                    } else {
                        auto it = findInVector(unwrapped->transitions, Transition{character, nullptr}, comp_characters);
                        if (it != nullptr){
                            next_state.nodes.push_back(it->next);
                        }
                    }
                }
            }
        }
        if (next_state.nodes.size() == 0){
            return false;
        }
        current_state = next_state;
    }
    if(must_end && end_symb_expected){
        if (current_state.nodes.size()){
            return current_state.nodes[0] == nullptr;
        }
        return false;
    }
    else if (must_end && !end_symb_expected){
        return special_symb_in_transitions(current_state, SpecialSymb::END);
    }
    return true;
}

ParserState step(const ParserState& state, int character) {
    ParserState new_state;
    for (auto& node : state.nodes)
    {
        if (!node) continue;

        std::vector<std::shared_ptr<ParserNode>> unwrapped_nodes;
        unwrap_node(node, unwrapped_nodes);

        for (const auto& unwrapped : unwrapped_nodes) {
            if (!unwrapped) continue;

            if (unwrapped->mode == TransitionMode::HASH_MAP) {
                auto it = unwrapped->transitions_map.find(character);
                if (it != unwrapped->transitions_map.end()) {
                    new_state.nodes.push_back(it->second);
                }
            } else {
                auto it = findInVector(unwrapped->transitions, Transition{character, nullptr}, comp_characters);
                if (it != nullptr){
                    new_state.nodes.push_back(it->next);
                }
            }
        }
    }
    return new_state;
}

std::vector<int> next(const ParserState& state) {
    std::vector<int> possible_characters;
    for (auto& node : state.nodes) {
        if (node == nullptr) {
            continue; // Skip null nodes
        }

        // Unwrap epsilon transitions (mode-aware)
        std::vector<std::shared_ptr<ParserNode>> unwrapped_nodes;
        unwrap_node(node, unwrapped_nodes);

        // Collect all unique characters from the transitions
        for (const auto& unwrapped : unwrapped_nodes) {
            if (!unwrapped) continue;

            if (unwrapped->mode == TransitionMode::HASH_MAP) {
                for (const auto& pair : unwrapped->transitions_map) {
                    if (pair.first != SpecialSymb::EPS) {
                        if (std::find(possible_characters.begin(), possible_characters.end(), pair.first) == possible_characters.end()) {
                            possible_characters.push_back(pair.first);
                        }
                    }
                }
            } else {
                for (const auto& transition : unwrapped->transitions) {
                    if (transition.character != SpecialSymb::EPS) {
                        if (std::find(possible_characters.begin(), possible_characters.end(), transition.character) == possible_characters.end()) {
                            possible_characters.push_back(transition.character);
                        }
                    }
                }
            }
        }
    }
    return possible_characters;
}
