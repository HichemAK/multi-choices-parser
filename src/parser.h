#ifndef PARSER_H
#define PARSER_H


#include <vector>
#include <memory>

// Forward declaration of ParserNode
struct ParserNode;

// Transition structure
struct Transition {
    int character; // Character for the transition (-1 for epsilon transitions)
    ParserNode* next; // Pointer to the next node

    // Comparison operator for sorting transitions
    bool operator<(const Transition& other) const {
        return character < other.character;
    }
};  

// ParserNode structure
struct ParserNode {
    std::vector<Transition> transitions; // List of transitions from this node
};

void collect_terminal_nodes(const ParserNode& root, std::vector<ParserNode>& next_nodes);

// Function to construct a tree for a single group of sequences
std::pair<ParserNode, bool> build_group_tree(const std::vector<std::vector<int>>& group);

// Function to connect multiple group trees with epsilon transitions
ParserNode connect_trees(
    const std::vector<std::pair<ParserNode, bool>>& group_trees
);

// Function to construct the full parser tree from groups of sequences
ParserNode* construct_tree(const std::vector<std::vector<std::vector<int>>>& groups);

// Function to check if the parser accepts a given sequence of characters
bool accepts(const ParserNode& root, const std::vector<int>& sequence);

// Function to perform a single step in the parser with the given character
ParserNode* step(const ParserNode& node, int character);

#endif // PARSER_H
