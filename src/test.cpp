#include <iostream>
#include <vector>
#include <memory>
#include "parser.h" // Include your parser implementation header

void test_accepts(ParserNode* tree, const std::vector<std::vector<int>>& test_sequences) {
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

void test_step(ParserNode* tree, const std::vector<int>& sequence) {
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
        {{1}, {3}, {}},  // Group 1: [2], [3], nullable ([])
        {{1, 2}, {1, 4}} // Group 2: [1, 2], [1, 4]
    };

    // Construct the parser tree
    std::cout << "Constructing the parser tree...\n";
    auto tree = construct_tree(groups);

    // Print the tree structure for debugging
    std::cout << "\nParser tree structure:\n";
    // print_node(*tree);

    // Test sequences
    std::vector<std::vector<int>> test_sequences = {
        {1, 2, SpecialSymb::END},     // Valid (nullable group)
        {1, 4},     // Valid (nullable group)
        {2, 3},     // Invalid
        {1, 1, 2},  // Valid
        {1, 1, 4},  // Valid
        {3, 1, 2},  // Valid
        {3, 1, 4},  // Valid
        {1},        // Invalid
        {}          // Invalid
    };

    // Test the accepts function
    test_accepts(tree, test_sequences);

    // Test single-step traversal
    std::vector<int> traversal_sequence = {1, 1, 2}; // Example valid sequence
    test_step(tree, traversal_sequence);

    return 0;
}
