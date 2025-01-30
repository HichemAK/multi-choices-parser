#include <vector>
#include <memory>
#include <algorithm>
#include "constants.h"
#include <functional>



// Structure for a transition
struct Transition {
    int character; // Character for the transition (MIN_VALUE_INT32 for epsilon)
    ParserNode* next;

    bool operator<(const Transition& other) const {
        return character < other.character;
    }
};

// Structure for a parser node
struct ParserNode {
    std::vector<Transition> transitions;
};

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
// Returns the last node before final_node
ParserNode* add_sequence(ParserNode& root, const std::vector<int>& sequence, const ParserNode& final_node) {
    auto current_node = &root;

    for (size_t i = 0; i < sequence.size(); i++) {
        auto character = sequence[i];

        ParserNode new_node;
        if (i < sequence.size()-1){
            new_node = ParserNode();
        }
        else{
            new_node = final_node;
        }
        auto to_add = Transition{character, &new_node};

        auto it = insertIntoOrderedVector(current_node->transitions, to_add, comp_characters);
        current_node = it->next;
    }
    return current_node;
}

// Function to build a tree for a single group
std::tuple<ParserNode*, bool> build_group_tree(const std::vector<std::vector<int>>& group, const ParserNode& final_node) {
    auto root = ParserNode();
    bool is_nullable = false;
    
    for (size_t i = 0; i<group.size(); i++) {
        const auto& sequence = group[i];
        if (sequence.empty()) {
            is_nullable = true; // Mark the group as nullable if it contains an empty sequence
        } else {
            add_sequence(root, sequence, final_node);
        }
    }

    return {&root, is_nullable};
}

// Function to connect multiple group trees with epsilon transitions
void connect_trees(
    const std::vector<std::tuple<ParserNode*, bool>>& group_trees,
    const std::vector<ParserNode*>& final_nodes
) {
    int n = group_trees.size();
    for (size_t i = 0; i < n-1; i++){
        auto group_tree = std::get<0>(group_trees[i]);
        for (size_t j = i; j < n && std::get<1>(group_trees[j]); j++){
            ParserNode* arrival_node;
            // Link root of each group with nullable sequence
            if (j < n-1){
                arrival_node = std::get<0>(group_trees[j+1]);
            }
            else{
                arrival_node = final_nodes.back();
            }
            auto to_add = Transition{EPS_SYMBOL, arrival_node};
            insertIntoOrderedVector(group_tree->transitions, to_add, comp_characters);

            // Link final node to next root
            if (j < n-1){
                auto to_add = Transition{EPS_SYMBOL, std::get<0>(group_trees[j+1])};
                insertIntoOrderedVector(final_nodes[j]->transitions, to_add, comp_characters);
            }
        }
    }
}


// Function to construct the final tree
ParserNode* construct_tree(const std::vector<std::vector<std::vector<int>>>& groups) {
    std::vector<std::tuple<ParserNode*, bool>> group_trees;
    // Build a tree for each group
    std::vector<ParserNode*> final_nodes(groups.size());    
    for (size_t i = 0; i < groups.size(); i++)
    {
        auto final_node = ParserNode();
        final_nodes[i] = &final_node;
        if (i == groups.size()-1){
            final_node.transitions.push_back(Transition{END_SYMBOL, nullptr});
        }
        group_trees.push_back(build_group_tree(groups[i], final_node));
    }

    // Connect the group trees with epsilon transitions
    connect_trees(group_trees, final_nodes);
    return std::get<0>(group_trees[0]);
}

int min(int a, int b){
    return a<b ? a:b;
}


void unwrap(const std::vector<Transition>& transitions, std::vector<std::reference_wrapper<const std::vector<Transition>>>& result) {
    result.push_back(transitions);
    int steps = min(2, transitions.size());
    for (size_t i = 0; i < steps; i++)
    {
        auto transition = transitions[i];
        if (transition.character == EPS_SYMBOL){
            if (transition.next == nullptr){
                continue;
            }
            unwrap(transition.next->transitions, result);
        }
    }
}


bool accepts(const ParserNode& root, const std::vector<int>& sequence) {
    ParserNode current_node = root;

    for (int character : sequence) {
        // Unwrap epsilon transitions
        // unwrap should return an iterator of std::vector<Transition>
        std::vector<std::reference_wrapper<const std::vector<Transition>>> all_valid_transition_vectors = {};
        unwrap(root.transitions, all_valid_transition_vectors);

        bool success = false;

        for (size_t i = 0; i < all_valid_transition_vectors.size(); i++){
            auto it = findInVector(all_valid_transition_vectors[i].get(), Transition{character, nullptr}, comp_characters);
            if (it != nullptr){
                success = true;
                break;
            }
        }
        if (!success){
            return false;
        }
    }

    return true;
}


ParserNode* step(const ParserNode& node, int character) {
    // Unwrap epsilon transitions
    std::vector<std::reference_wrapper<const std::vector<Transition>>> all_valid_transition_vectors = {};
    unwrap(node.transitions, all_valid_transition_vectors);
    
    for (const auto& transition_vector : all_valid_transition_vectors) {
        for (const auto& transition : transition_vector.get()) {
            if (transition.character == character) {
                return transition.next; // Return the next node if the character matches
            }
        }
    }
    
    return nullptr; // Return nullptr if no valid transition is found
}
