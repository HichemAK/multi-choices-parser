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

    // Recursively delete all nodes reachable from this node
    void delete_recursive() {
        for (Transition& transition : transitions) {
            if (transition.next) {
                transition.next->delete_recursive(); // Recursively delete the next node
                delete transition.next; // Delete the next node
                transition.next = nullptr; // Set the pointer to null
            }
        }
    }
};

struct ParserState {
    std::vector<ParserNode*> nodes;

    // Add a node to the state
    void add_node(ParserNode* node) {
        nodes.push_back(node);
    }

    // Free memory for all nodes in the state, recursively
    void free_memory() {
        for (ParserNode* node : nodes) {
            if (node) {
                node->delete_recursive(); // Recursively delete all reachable nodes
                delete node; // Delete the current node
            }
        }
        nodes.clear(); // Clear the vector after deleting the nodes
    }
};

// Function to construct a tree for a single group of sequences
std::tuple<ParserNode*, bool> build_group_tree(const std::vector<std::vector<int>>& group, ParserNode* final_node);

// Function to connect multiple group trees with epsilon transitions
void connect_trees(
    std::vector<std::tuple<ParserNode*, bool>>& group_trees,
    std::vector<ParserNode*>& final_nodes
);

// Function to construct the full parser tree from groups of sequences
ParserNode* construct_tree(const std::vector<std::vector<std::vector<int>>>& groups);

// Function to check if the parser accepts a given sequence of characters
bool accepts(ParserState& state, const std::vector<int>& sequence, bool must_end, bool end_symb_expected);

// Function to perform a single step in the parser with the given character
ParserState step(const ParserState& state, int character) ;

bool special_symb_in_transitions(const ParserState& state, const SpecialSymb symb);
bool special_symb_in_transitions(const std::vector<Transition>& transitions, const SpecialSymb symb);
#endif // PARSER_H
