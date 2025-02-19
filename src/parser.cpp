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

// Function to add a sequence to a tree
// Returns the end node pointer if exists else null pointer
std::shared_ptr<ParserNode> add_sequence(
    std::shared_ptr<ParserNode> root, 
    const std::vector<int>& sequence, 
    std::vector<std::shared_ptr<ParserNode>>& final_nodes) 
{
    auto current_node = root;

    for (size_t i = 0; i < sequence.size(); i++) {
        auto character = sequence[i];
        

        Transition to_add = {character, nullptr};
        auto it = insertIntoOrderedVector(current_node->transitions, to_add, comp_characters);
        if (it->next == nullptr){
            it->next = std::make_shared<ParserNode>();
        }
        if(i == sequence.size()-1){
            final_nodes.push_back(it->next);
        }
        current_node = it->next;
    }
    return nullptr;
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

// Function to construct the final tree
std::shared_ptr<ParserNode> construct_tree(const std::vector<std::vector<std::vector<int>>>& groups) {
    std::vector<std::tuple<std::shared_ptr<ParserNode>, bool>> groups_tree_infos;
    // Build a tree for each group
    std::vector<std::vector<std::shared_ptr<ParserNode>>> final_nodes_per_group = {};
    for (size_t i = 0; i < groups.size(); i++)
    {
        std::vector<std::shared_ptr<ParserNode>> final_nodes = {};
        groups_tree_infos.push_back(build_group_tree(groups[i], final_nodes));
        final_nodes_per_group.push_back(final_nodes);
    }

    // Connect the group trees with epsilon transitions
    groups_tree_infos.push_back({nullptr, false});
    connect_trees(groups_tree_infos, final_nodes_per_group);
    return std::get<0>(groups_tree_infos[0]);
}

int min(int a, int b){
    return a < b ? a : b;
}

void unwrap(const std::vector<Transition>& transitions, std::vector<const std::vector<Transition>*>& result) {
    result.push_back(&transitions);
    if (transitions[0].character == SpecialSymb::EPS){
        unwrap(transitions[0].next->transitions, result);
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

bool special_symb_in_transitions(const ParserState& state, const SpecialSymb symb){    
    for (size_t i = 0; i < state.nodes.size(); i++)
    {
        if(state.nodes[i] == nullptr){
            continue;
        }
        if (special_symb_in_transitions(state.nodes[i]->transitions, symb)){
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
            std::vector<const std::vector<Transition>*> all_valid_transition_vectors = {};
            unwrap(node->transitions, all_valid_transition_vectors);

            for (size_t i = 0; i < all_valid_transition_vectors.size(); i++){
                auto it = findInVector(*all_valid_transition_vectors[i], Transition{character, nullptr}, comp_characters);
                if (it != nullptr){
                    next_state.nodes.push_back(it->next);
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
        std::vector<const std::vector<Transition>*> all_valid_transition_vectors = {};
        unwrap(node->transitions, all_valid_transition_vectors);
        
        for (size_t i = 0; i < all_valid_transition_vectors.size(); i++){
            auto it = findInVector(*all_valid_transition_vectors[i], Transition{character, nullptr}, comp_characters);
            if (it != nullptr){
                new_state.nodes.push_back(it->next);
            }
        }
    }
    return new_state; // Return nullptr if no valid transition is found
}

std::vector<int> next(const ParserState& state) {
    std::vector<int> possible_characters;
    for (auto& node : state.nodes) {
        if (node == nullptr) {
            continue; // Skip null nodes
        }

        // Unwrap epsilon transitions
        std::vector<const std::vector<Transition>*> all_valid_transition_vectors = {};
        unwrap(node->transitions, all_valid_transition_vectors);

        // Collect all unique characters from the transitions
        for (const auto& transitions : all_valid_transition_vectors) {
            for (const auto& transition : *transitions) {
                if (transition.character != SpecialSymb::EPS) { // Skip epsilon transitions
                    // Avoid duplicates
                    if (std::find(possible_characters.begin(), possible_characters.end(), transition.character) == possible_characters.end()) {
                        possible_characters.push_back(transition.character);
                    }
                }
            }
        }
    }
    return possible_characters;
}
