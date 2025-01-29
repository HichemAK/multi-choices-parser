#include <vector>
#include <memory>
#include <algorithm>
#include "constants.h"




// Structure for a transition
struct Transition {
    int character; // Character for the transition (MIN_VALUE_INT32 for epsilon)
    std::shared_ptr<struct ParserNode> next;

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

auto comp_characters = [](const Transition& a, const Transition& b) {
    return a.character < b.character;
};

// Function to add a sequence to a tree
// Returns the last node before final_node
std::shared_ptr<ParserNode> add_sequence(std::shared_ptr<ParserNode> root, const std::vector<int>& sequence, const std::shared_ptr<ParserNode> final_node) {
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
        auto to_add = Transition{character, new_node};

        auto it = insertIntoOrderedVector(current_node->transitions, to_add, comp_characters);
        current_node = it->next;
    }
    return current_node;
}

// Function to build a tree for a single group
std::tuple<std::shared_ptr<ParserNode>, bool> build_group_tree(const std::vector<std::vector<int>>& group, const std::shared_ptr<ParserNode> final_node) {
    auto root = std::make_shared<ParserNode>();
    bool is_nullable = false;
    
    for (size_t i = 0; i<group.size(); i++) {
        const auto& sequence = group[i];
        if (sequence.empty()) {
            is_nullable = true; // Mark the group as nullable if it contains an empty sequence
        } else {
            add_sequence(root, sequence, final_node);
        }
    }

    return {root, is_nullable};
}

// Function to connect multiple group trees with epsilon transitions
void connect_trees(
    const std::vector<std::tuple<std::shared_ptr<ParserNode>, bool>>& group_trees,
    const std::vector<std::shared_ptr<ParserNode>> final_nodes
) {
    int n = group_trees.size();
    for (size_t i = 0; i < n-1; i++){
        auto group_tree = std::get<0>(group_trees[i]);
        for (size_t j = i; j < n && std::get<1>(group_trees[j]); j++){
            auto to_add = Transition{EPS_SYMBOL, final_nodes[j]};
            auto it = std::lower_bound(
            group_tree->transitions.begin(),
            group_tree->transitions.end(),
            to_add
            );

            if (it == group_tree->transitions.end() || it->character != EPS_SYMBOL) {
                group_tree->transitions.insert(it, to_add);
            }
        }
    }
}




// Function to construct the final tree
std::shared_ptr<ParserNode> construct_tree(const std::vector<std::vector<std::vector<int>>>& groups) {
    std::vector<std::tuple<std::shared_ptr<ParserNode>, bool>> group_trees;
    // Build a tree for each group
    std::vector<std::shared_ptr<ParserNode>> final_nodes(groups.size());    
    for (size_t i = 0; i < groups.size(); i++)
    {
        auto final_node = std::make_shared<ParserNode>();
        final_nodes[i] = final_node;
        if (i == groups.size()-1){
            final_node->transitions.push_back(Transition{END_SYMBOL, nullptr});
        }
        group_trees.push_back(build_group_tree(groups[i], final_node));
    }

    // Connect the group trees with epsilon transitions
    connect_trees(group_trees, final_nodes);
    return std::get<0>(group_trees[0]);
}



bool accepts(const std::shared_ptr<ParserNode>& root, const std::vector<int>& sequence) {
    std::vector<std::shared_ptr<ParserNode>> current_nodes = {root};

    for (int character : sequence) {
        std::vector<std::shared_ptr<ParserNode>> next_nodes;

        for (auto& node : current_nodes) {
            for (auto& transition : node->transitions) {
                if (transition.character == character || transition.character == END_SYMBOL) {
                    next_nodes.push_back(transition.next);
                }
            }
        }

        current_nodes = next_nodes;
    }

    // Check if any of the current nodes is terminal
    // for (auto& node : current_nodes) {
    //     if (node->is_terminal) {
    //         return true;
    //     }
    // }

    return false;
}


std::shared_ptr<ParserNode> step(const std::shared_ptr<ParserNode>& node, int character) {
    // First, try to follow a direct character transition
    for (const auto& transition : node->transitions) {
        if (transition.character == character) {
            return transition.next;
        }
    }

    // If no direct character transition is found, follow epsilon transitions
    for (const auto& transition : node->transitions) {
        if (transition.character == END_SYMBOL) { // Epsilon transition
            auto next_node = step(transition.next, character); // Recursively check the next node
            if (next_node != nullptr) {
                return next_node;
            }
        }
    }

    // If no valid transition is found, return nullptr
    return nullptr;
}