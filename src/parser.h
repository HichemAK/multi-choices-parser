#ifndef PARSER_H
#define PARSER_H


#include <vector>
#include <memory>

// Forward declaration of ParserNode
struct ParserNode;

// Transition structure
struct Transition {
    int character; // Character for the transition (-1 for epsilon transitions)
    std::shared_ptr<ParserNode> next; // Pointer to the next node

    // Comparison operator for sorting transitions
    bool operator<(const Transition& other) const {
        return character < other.character;
    }
};

// ParserNode structure
struct ParserNode {
    std::vector<Transition> transitions; // List of transitions from this node
    bool is_terminal = false; // Marks if this node is a terminal node
};

void collect_terminal_nodes(const std::shared_ptr<ParserNode>& root, std::vector<std::shared_ptr<ParserNode>>& next_nodes);

// Function to construct a tree for a single group of sequences
std::pair<std::shared_ptr<ParserNode>, bool> build_group_tree(const std::vector<std::vector<int>>& group);

// Function to connect multiple group trees with epsilon transitions
std::shared_ptr<ParserNode> connect_trees(
    const std::vector<std::pair<std::shared_ptr<ParserNode>, bool>>& group_trees
);

// Function to construct the full parser tree from groups of sequences
std::shared_ptr<ParserNode> construct_tree(const std::vector<std::vector<std::vector<int>>>& groups);

// Function to check if the parser accepts a given sequence of characters
bool accepts(const std::shared_ptr<ParserNode>& root, const std::vector<int>& sequence);

// Function to perform a single step in the parser with the given character
std::shared_ptr<ParserNode> step(const std::shared_ptr<ParserNode>& node, int character);

#endif // PARSER_H
