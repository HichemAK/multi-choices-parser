#include <pybind11/pybind11.h>
#include <pybind11/stl.h> // For std::vector
#include <memory>         // For std::shared_ptr
#include <algorithm>      // For std::lower_bound

namespace py = pybind11;

// Define the structures
struct Transition {
    int character;
    std::shared_ptr<struct ParserNode> next;

    // Comparison operator for sorting and binary search
    bool operator<(const Transition& other) const {
        return character < other.character;
    }
};

struct ParserNode {
    std::vector<Transition> transitions; // Sorted vector of transitions
};

// Function to add a sequence to the tree
void add_sequence(std::shared_ptr<ParserNode> root, const std::vector<int>& sequence) {
    auto current_node = root;

    for (int character : sequence) {
        // Find the transition using binary search
        auto it = std::lower_bound(
            current_node->transitions.begin(),
            current_node->transitions.end(),
            Transition{character, nullptr}
        );

        if (it == current_node->transitions.end() || it->character != character) {
            // Transition not found, create a new one
            auto new_node = std::make_shared<ParserNode>();
            current_node->transitions.insert(it, {character, new_node});
            current_node = new_node;
        } else {
            // Transition found, move to the next node
            current_node = it->next;
        }
    }
}

// Function to construct the tree from a list of sequences
std::shared_ptr<ParserNode> construct_tree(const std::vector<std::vector<int>>& sequences) {
    auto root = std::make_shared<ParserNode>();

    for (const auto& sequence : sequences) {
        add_sequence(root, sequence);
    }

    return root;
}

// Function to check if a sequence is accepted by the tree
bool accepts(const std::shared_ptr<ParserNode>& root, const std::vector<int>& sequence) {
    auto current_node = root;

    for (int character : sequence) {
        // Find the transition using binary search
        auto it = std::lower_bound(
            current_node->transitions.begin(),
            current_node->transitions.end(),
            Transition{character, nullptr}
        );

        if (it == current_node->transitions.end() || it->character != character) {
            return false; // Transition not found
        }

        current_node = it->next;
    }

    return true; // All characters in the sequence were matched
}

// Function to perform a single step in the parser
std::shared_ptr<ParserNode> step(const std::shared_ptr<ParserNode>& node, int character) {
    // Find the transition using binary search
    auto it = std::lower_bound(
        node->transitions.begin(),
        node->transitions.end(),
        Transition{character, nullptr}
    );

    if (it != node->transitions.end() && it->character == character) {
        return it->next; // Return the next node
    }

    return nullptr; // Transition not found
}

// Expose the code to Python
PYBIND11_MODULE(_core, m) {
    m.doc() = "pybind11 ParserNode module using std::vector";

    // Expose ParserNode
    py::class_<ParserNode, std::shared_ptr<ParserNode>>(m, "ParserNode")
        .def(py::init<>()) // Default constructor
        .def_readwrite("transitions", &ParserNode::transitions);

    // Expose Transition
    py::class_<Transition>(m, "Transition")
        .def(py::init<>()) // Default constructor
        .def_readwrite("character", &Transition::character)
        .def_readwrite("next", &Transition::next);

    // Expose construct_tree function
    m.def("construct_tree", &construct_tree, R"pbdoc(
        Construct a ParserNode tree from a list of sequences of integers.
    )pbdoc");

    // Expose accepts function
    m.def("accepts", &accepts, R"pbdoc(
        Check if the parser accepts the given sequence of characters.
    )pbdoc");

    // Expose step function
    m.def("step", &step, R"pbdoc(
        Perform a single step in the parser with the given character.
    )pbdoc");
}
