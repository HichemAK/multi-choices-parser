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

// Function to construct a tree for a single group of sequences
std::tuple<std::shared_ptr<ParserNode>, bool> build_group_tree(
    const std::vector<std::vector<int>>& group, 
    std::shared_ptr<ParserNode> final_node, 
    bool add_end_symbol
);

// Function to connect multiple group trees with epsilon transitions
void connect_trees(
    std::vector<std::tuple<std::shared_ptr<ParserNode>, bool>>& group_trees,
    std::vector<std::shared_ptr<ParserNode>>& final_nodes
);

// Function to construct the full parser tree from groups of sequences
std::shared_ptr<ParserNode> construct_tree(const std::vector<std::vector<std::vector<int>>>& groups);

// Function to check if the parser accepts a given sequence of characters
bool accepts(ParserState& state, const std::vector<int>& sequence, bool must_end, bool end_symb_expected);

// Function to perform a single step in the parser with the given character
ParserState step(const ParserState& state, int character);

bool special_symb_in_transitions(const ParserState& state, const SpecialSymb symb);
bool special_symb_in_transitions(const std::vector<Transition>& transitions, const SpecialSymb symb);
std::vector<int> next(const ParserState& state);

#endif // PARSER_H
