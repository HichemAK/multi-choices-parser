#include <vector>
#include <memory>
#include <algorithm>
#include "constants.h"
#include <functional>
#include "parser.h"



// Structure for a transition
// struct Transition {
//     int character; // Character for the transition (MIN_VALUE_INT32 for epsilon)
//     ParserNode* next;

//     bool operator<(const Transition& other) const {
//         return character < other.character;
//     }
// };

// // Structure for a parser node
// struct ParserNode {
//     std::vector<Transition> transitions;
// };

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
// Returns the last node before end_symbol if it exists
ParserNode* add_sequence(ParserNode* root, const std::vector<int>& sequence, ParserNode* final_node, bool add_end_symb) {
    auto current_node = root;

    for (size_t i = 0; i < sequence.size(); i++) {
        auto character = sequence[i];

        ParserNode* new_node;
        if (i < sequence.size()-1){
            new_node = new ParserNode();
        }
        else{
            new_node = final_node;
        }
        Transition to_add = {character, new_node};
        auto it = insertIntoOrderedVector(current_node->transitions, to_add, comp_characters);
        current_node = it->next;
    }
    if (add_end_symb){
        Transition to_add = {END, nullptr};
        auto it = insertIntoOrderedVector(current_node->transitions, to_add, comp_characters);
    }
    return current_node;
}

// Function to build a tree for a single group
std::tuple<ParserNode*, bool> build_group_tree(const std::vector<std::vector<int>>& group, ParserNode* final_node) {
    bool is_nullable = false;
    ParserNode* root = new ParserNode();
    
    for (size_t i = 0; i<group.size(); i++) {
        const auto& sequence = group[i];
        if (sequence.empty()) {
            is_nullable = true; // Mark the group as nullable if it contains an empty sequence
        } else {
            add_sequence(root, sequence, final_node, i == group.size()-1);
        }
    }

    return {root, is_nullable};
}

// Function to connect multiple group trees with epsilon transitions
void connect_trees(
    std::vector<std::tuple<ParserNode*, bool>>& group_trees,
    std::vector<ParserNode*>& final_nodes
) {
    int n = group_trees.size();
    for (size_t i = 0; i < n-1; i++){
        ParserNode* group_tree = std::get<0>(group_trees[i]);
        for (size_t j = i; j < n && std::get<1>(group_trees[j]); j++){
            ParserNode* arrival_node;
            // Link root of each group with nullable sequence
            if (j < n-1){
                arrival_node = std::get<0>(group_trees[j+1]);
            }
            else{
                arrival_node = final_nodes.back();
            }
            Transition to_add = Transition{EPS, arrival_node};
            insertIntoOrderedVector(group_tree->transitions, to_add, comp_characters);

            // Link final node to next root
            if (j < n-1){
                Transition to_add = Transition{EPS, std::get<0>(group_trees[j+1])};
                insertIntoOrderedVector(final_nodes[j]->transitions, to_add, comp_characters);
            }
        }
    }
}

// Function to construct the final tree
ParserNode* construct_tree(const std::vector<std::vector<std::vector<int>>>& groups) {
    std::vector<std::tuple<ParserNode*, bool>> group_trees;
    // Build a tree for each group
    std::vector<ParserNode*> final_nodes;    
    for (size_t i = 0; i < groups.size(); i++)
    {
        final_nodes.push_back(new ParserNode());

        group_trees.push_back(build_group_tree(groups[i], final_nodes[i]));
    }

    // Connect the group trees with epsilon transitions
    connect_trees(group_trees, final_nodes);
    return std::get<0>(group_trees[0]);
}

int min(int a, int b){
    return a<b ? a:b;
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
        if (special_symb_in_transitions(state.nodes[i]->transitions, symb)){
            return true;
        }
    }
    return false;
}

bool accepts(ParserState& state, const std::vector<int>& sequence, bool must_end, bool end_symb_mandatory) {
    ParserState current_state = state;
    for (int character : sequence) {
        ParserState next_state;
        for (ParserNode* node : current_state.nodes)
        {      
            // Unwrap epsilon transitions
            // unwrap should return an iterator of std::vector<Transition>
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
    if(must_end && end_symb_mandatory){
        for (ParserNode* node : current_state.nodes)
        {
            if (node == nullptr){
                return true;
            }
        }
        return false;
    }
    else if (must_end && !end_symb_mandatory){
        return special_symb_in_transitions(current_state, SpecialSymb::END);
    }
    return true;
}


ParserState step(const ParserState& state, int character) {
    // Unwrap epsilon transitions
    ParserState new_state;
    for (ParserNode* node: state.nodes)
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
