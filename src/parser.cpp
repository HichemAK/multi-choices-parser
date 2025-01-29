#include <vector>
#include <memory>
#include <algorithm>

// Structure for a transition
struct Transition {
    int character; // Character for the transition (-1 for epsilon)
    std::shared_ptr<struct ParserNode> next;

    bool operator<(const Transition& other) const {
        return character < other.character;
    }
};

// Structure for a parser node
struct ParserNode {
    std::vector<Transition> transitions;
    bool is_terminal = false; // Marks the end of a valid sequence
};

// Function to add a sequence to a tree
void add_sequence(std::shared_ptr<ParserNode> root, const std::vector<int>& sequence) {
    auto current_node = root;

    for (int character : sequence) {
        auto it = std::lower_bound(
            current_node->transitions.begin(),
            current_node->transitions.end(),
            Transition{character, nullptr}
        );

        if (it == current_node->transitions.end() || it->character != character) {
            auto new_node = std::make_shared<ParserNode>();
            current_node->transitions.insert(it, {character, new_node});
            current_node = new_node;
        } else {
            current_node = it->next;
        }
    }

    current_node->is_terminal = true; // Mark the end of the sequence
}

// Function to build a tree for a single group
std::pair<std::shared_ptr<ParserNode>, bool> build_group_tree(const std::vector<std::vector<int>>& group) {
    auto root = std::make_shared<ParserNode>();
    bool is_nullable = false;

    for (const auto& sequence : group) {
        if (sequence.empty()) {
            is_nullable = true; // Mark the group as nullable if it contains an empty sequence
        } else {
            add_sequence(root, sequence);
        }
    }

    return {root, is_nullable};
}


// Helper function to collect all terminal nodes directly reachable from the group tree
void collect_terminal_nodes(const std::shared_ptr<ParserNode>& root, std::vector<std::shared_ptr<ParserNode>>& next_nodes) {
    // Use a stack to simulate traversal (avoiding deep recursion)
    std::vector<std::shared_ptr<ParserNode>> stack = {root};

    while (!stack.empty()) {
        auto node = stack.back();
        stack.pop_back();

        // If the node is terminal, add it to the list
        if (node->is_terminal) {
            next_nodes.push_back(node);
        }

        // Traverse transitions
        for (const auto& transition : node->transitions) {
            if (transition.character == -1) { // Follow epsilon transitions
                stack.push_back(transition.next);
            }
        }
    }
}


// Function to connect multiple group trees with epsilon transitions
std::shared_ptr<ParserNode> connect_trees(
    const std::vector<std::pair<std::shared_ptr<ParserNode>, bool>>& group_trees
) {
    auto root = std::make_shared<ParserNode>();
    auto current_nodes = std::vector<std::shared_ptr<ParserNode>>{root};

    for (const auto& [group_tree, is_nullable] : group_trees) {
        auto next_nodes = std::vector<std::shared_ptr<ParserNode>>();

        // Add epsilon transitions from current nodes to the root of the group tree
        for (auto& node : current_nodes) {
            node->transitions.push_back({-1, group_tree}); // Epsilon transition
        }

        // Collect all terminal nodes directly reachable from the group tree
        collect_terminal_nodes(group_tree, next_nodes);

        // If the group is nullable, add epsilon transitions directly to the next group
        if (is_nullable) {
            next_nodes.insert(next_nodes.end(), current_nodes.begin(), current_nodes.end());
        }

        current_nodes = next_nodes;
    }

    // Mark all remaining terminal nodes as terminal
    for (auto& node : current_nodes) {
        node->is_terminal = true;
    }

    return root;
}




// Function to construct the final tree
std::shared_ptr<ParserNode> construct_tree(const std::vector<std::vector<std::vector<int>>>& groups) {
    std::vector<std::pair<std::shared_ptr<ParserNode>, bool>> group_trees;

    // Build a tree for each group
    for (const auto& group : groups) {
        group_trees.push_back(build_group_tree(group));
    }

    // Connect the group trees with epsilon transitions
    return connect_trees(group_trees);
}



bool accepts(const std::shared_ptr<ParserNode>& root, const std::vector<int>& sequence) {
    std::vector<std::shared_ptr<ParserNode>> current_nodes = {root};

    for (int character : sequence) {
        std::vector<std::shared_ptr<ParserNode>> next_nodes;

        for (auto& node : current_nodes) {
            for (auto& transition : node->transitions) {
                if (transition.character == character || transition.character == -1) {
                    next_nodes.push_back(transition.next);
                }
            }
        }

        current_nodes = next_nodes;
    }

    // Check if any of the current nodes is terminal
    for (auto& node : current_nodes) {
        if (node->is_terminal) {
            return true;
        }
    }

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
        if (transition.character == -1) { // Epsilon transition
            auto next_node = step(transition.next, character); // Recursively check the next node
            if (next_node != nullptr) {
                return next_node;
            }
        }
    }

    // If no valid transition is found, return nullptr
    return nullptr;
}