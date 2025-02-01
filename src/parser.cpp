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
    std::shared_ptr<ParserNode> final_node, 
    bool add_end_symb) 
{
    auto current_node = root;

    for (size_t i = 0; i < sequence.size(); i++) {
        auto character = sequence[i];

        std::shared_ptr<ParserNode> new_node;
        if (i < sequence.size()-1){
            new_node = std::make_shared<ParserNode>();
        }
        else{
            new_node = final_node;
        }
        Transition to_add = {character, new_node};
        auto it = insertIntoOrderedVector(current_node->transitions, to_add, comp_characters);
        
        if(new_node == final_node && it->next != final_node){
            Transition to_add = {SpecialSymb::EPS, final_node};
            insertIntoOrderedVector(it->next->transitions, to_add, comp_characters);
            current_node = final_node;
        }
        else{
            current_node = it->next;
        }
    }
    if (add_end_symb){
        Transition to_add = {END, nullptr};
        auto it = insertIntoOrderedVector(current_node->transitions, to_add, comp_characters);
        return it->next;
    }
    return nullptr;
}

// Function to build a tree for a single group
std::tuple<std::shared_ptr<ParserNode>, bool> build_group_tree(
    const std::vector<std::vector<int>>& group, 
    std::shared_ptr<ParserNode> final_node, 
    bool add_end_symbol
) {
    bool is_nullable = false;
    auto root = std::make_shared<ParserNode>();
    
    for (size_t i = 0; i<group.size(); i++) {
        const auto& sequence = group[i];
        if (sequence.empty()) {
            is_nullable = true; // Mark the group as nullable if it contains an empty sequence
        } else {
            add_sequence(root, sequence, final_node, add_end_symbol);
        }
    }

    return {root, is_nullable};
}

// Function to connect multiple group trees with epsilon transitions
void connect_trees(
    std::vector<std::tuple<std::shared_ptr<ParserNode>, bool>>& group_trees,
    std::vector<std::shared_ptr<ParserNode>>& final_nodes
) {
    int n = group_trees.size();
    for (size_t i = 0; i < n-1; i++){
        auto group_tree = std::get<0>(group_trees[i]);
        auto is_nullable = std::get<1>(group_trees[i]);
        auto next_group_tree = std::get<0>(group_trees[i+1]);
        if (next_group_tree != nullptr){
            Transition to_add = Transition{EPS, next_group_tree}; 
            insertIntoOrderedVector(final_nodes[i]->transitions, to_add, comp_characters);
        }
        
        if (is_nullable){
            Transition to_add = Transition{next_group_tree != nullptr ? EPS : END, next_group_tree};
            insertIntoOrderedVector(group_tree->transitions, to_add, comp_characters);
        }
    }
}

// Function to construct the final tree
std::shared_ptr<ParserNode> construct_tree(const std::vector<std::vector<std::vector<int>>>& groups) {
    std::vector<std::tuple<std::shared_ptr<ParserNode>, bool>> group_trees;
    // Build a tree for each group
    std::vector<std::shared_ptr<ParserNode>> final_nodes;    
    for (size_t i = 0; i < groups.size(); i++)
    {
        final_nodes.push_back(std::make_shared<ParserNode>());

        group_trees.push_back(build_group_tree(groups[i], final_nodes[i], i == groups.size()-1));
    }

    // Connect the group trees with epsilon transitions
    group_trees.push_back({nullptr, false});
    connect_trees(group_trees, final_nodes);
    return std::get<0>(group_trees[0]);
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
