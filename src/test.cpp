#include <iostream>
#include <vector>
#include <memory>
#include "parser.h" // Include your parser implementation header

void print_node(const std::shared_ptr<ParserNode>& node, int depth = 0) {
    if (!node) return;

    // Print the current node
    std::cout << std::string(depth, ' ') << "Node:\n";

    // Print transitions
    for (const auto& transition : node->transitions) {
        std::cout << std::string(depth + 2, ' ') << "Transition (character=" << transition.character << ")\n";
        print_node(transition.next, depth + 4);
    }
}

void test_accepts(const std::shared_ptr<ParserNode>& tree, const std::vector<std::vector<int>>& test_sequences) {
    std::cout << "\nTesting sequences:\n";
    for (const auto& seq : test_sequences) {
        bool result = accepts(tree, seq);
        std::cout << "Sequence { ";
        for (int c : seq) std::cout << c << " ";
        std::cout << "} is " << (result ? "ACCEPTED" : "REJECTED") << "\n";
    }
}

void test_step(const std::shared_ptr<ParserNode>& tree, const std::vector<int>& sequence) {
    std::cout << "\nTesting single-step traversal:\n";
    auto current_node = tree;

    for (int step_ : sequence) {
        std::cout << "Current node: " << current_node.get() << "\n";
        auto next_node = step(current_node, step_);
        if (!next_node) {
            std::cout << "Step " << step_ << " failed! No valid transition.\n";
            break;
        }
        std::cout << "Step " << step_ << " succeeded. Moving to next node.\n";
        current_node = next_node;
    }

    if (current_node) {
        std::cout << "Traversal ended on a terminal node. Sequence is valid!\n";
    } else {
        std::cout << "Traversal did not end on a terminal node. Sequence is invalid.\n";
    }
}

int main() {
    // Define groups of sequences
    std::vector<std::vector<std::vector<int>>> groups = {
        {{2}, {3}, {}},  // Group 1: [2], [3], nullable ([])
        {{1, 2}, {1, 4}} // Group 2: [1, 2], [1, 4]
    };

    // Construct the parser tree
    std::cout << "Constructing the parser tree...\n";
    auto tree = construct_tree(groups);

    // Print the tree structure for debugging
    std::cout << "\nParser tree structure:\n";
    print_node(tree);

    // Test sequences
    std::vector<std::vector<int>> test_sequences = {
        {2, 1, 2},  // Valid
        {2, 1, 4},  // Valid
        {3, 1, 2},  // Valid
        {3, 1, 4},  // Valid
        {1, 2},     // Valid (nullable group)
        {1, 4},     // Valid (nullable group)
        {2, 3},     // Invalid
        {1},        // Invalid
        {}          // Invalid
    };

    // Test the accepts function
    test_accepts(tree, test_sequences);

    // Test single-step traversal
    std::vector<int> traversal_sequence = {2, 1, 2}; // Example valid sequence
    test_step(tree, traversal_sequence);

    return 0;
}
