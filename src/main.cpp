#include <pybind11/pybind11.h>
#include <pybind11/stl.h> // For std::vector and other STL containers
#include <memory>         // For std::shared_ptr

namespace py = pybind11;

// Define the structures
struct Transition;
struct LinkedListTransition;

struct ParserNode {
    std::shared_ptr<LinkedListTransition> transitions;
};

struct Transition {
    int character;
    std::shared_ptr<ParserNode> next;
};

struct LinkedListTransition {
    Transition transition;
    std::shared_ptr<LinkedListTransition> next;
};

// Function to check if a sequence is accepted
bool accepts(std::shared_ptr<ParserNode> node, const std::vector<int>& array) {
    if (array.empty()) {
        return true;
    }
    size_t i = 0;
    while (node) {
        bool success = false;
        auto temp = node->transitions;
        while (temp) {
            if (array[i] == temp->transition.character) {
                success = true;
                node = temp->transition.next;
                break;
            }
            temp = temp->next;
        }
        if (!success) {
            return false;
        }
        i += 1;
        if (i == array.size()) {
            return true;
        }
    }
    return false;
}

// Function to perform a single step in the parser
std::shared_ptr<ParserNode> step(std::shared_ptr<ParserNode> node, int character) {
    auto temp = node->transitions;
    while (temp) {
        if (character == temp->transition.character) {
            return temp->transition.next;
        }
        temp = temp->next;
    }
    return nullptr;
}

// Expose the code to Python
PYBIND11_MODULE(_core, m) {
    m.doc() = "pybind11 ParserNode module";

    // Expose ParserNode
    py::class_<ParserNode, std::shared_ptr<ParserNode>>(m, "ParserNode")
        .def(py::init<>()) // Default constructor
        .def_readwrite("transitions", &ParserNode::transitions);

    // Expose Transition
    py::class_<Transition>(m, "Transition")
        .def(py::init<>()) // Default constructor
        .def_readwrite("character", &Transition::character)
        .def_readwrite("next", &Transition::next);

    // Expose LinkedListTransition
    py::class_<LinkedListTransition, std::shared_ptr<LinkedListTransition>>(m, "LinkedListTransition")
        .def(py::init<>()) // Default constructor
        .def_readwrite("transition", &LinkedListTransition::transition)
        .def_readwrite("next", &LinkedListTransition::next);

    // Expose accepts function
    m.def("accepts", &accepts, R"pbdoc(
        Check if the parser accepts the given sequence of characters.
    )pbdoc");

    // Expose step function
    m.def("step", &step, R"pbdoc(
        Perform a single step in the parser with the given character.
    )pbdoc");
}
