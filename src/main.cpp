#include <pybind11/pybind11.h>
#include <pybind11/stl.h> // For std::vector
#include <pybind11/functional.h> // For std::function
#include "parser.h"

namespace py = pybind11;

// Expose the code to Python
PYBIND11_MODULE(_core, m) {
    m.doc() = "pybind11 ParserNode module with epsilon transitions and group-based tree construction";

    // Expose SpecialSymb enum
    py::enum_<SpecialSymb>(m, "SpecialSymb")
        .value("END", SpecialSymb::END)
        .value("EPS", SpecialSymb::EPS)
        .export_values();

    // Expose NUM_SPECIAL_SYMB constant
    m.attr("NUM_SPECIAL_SYMB") = NUM_SPECIAL_SYMB;

    // Expose Transition
    py::class_<Transition>(m, "Transition")
        .def(py::init<>()) // Default constructor
        .def_readwrite("character", &Transition::character)
        .def_readwrite("next", &Transition::next)
        .def("__lt__", &Transition::operator<); // Expose comparison operator

    // Expose ParserNode
    py::class_<ParserNode>(m, "ParserNode")
        .def(py::init<>()) // Default constructor
        .def_readwrite("transitions", &ParserNode::transitions);

    // Expose ParserState
    py::class_<ParserState>(m, "ParserState")
        .def(py::init<>()) // Default constructor
        .def_readwrite("nodes", &ParserState::nodes)
        .def("add_node", &ParserState::add_node, "Add a node to the state")
        .def("free_memory", &ParserState::free_memory, "Free memory for all nodes in the state, recursively");

    // Expose build_group_tree function
    m.def("build_group_tree", &build_group_tree, R"pbdoc(
        Build a tree for a single group of sequences. Returns the root of the tree
        and a boolean indicating whether the group is nullable (contains an empty sequence).
    )pbdoc");

    // Expose connect_trees function
    m.def("connect_trees", &connect_trees, R"pbdoc(
        Connect multiple group trees with epsilon transitions. Takes a list of
        (tree, is_nullable) pairs and returns the root of the connected tree.
    )pbdoc");

    // Expose construct_tree function
    m.def("construct_tree", &construct_tree, R"pbdoc(
        Construct a ParserNode tree from a list of groups of sequences of integers.
        Each group is a list of sequences, and the tree supports epsilon transitions
        for nullable groups.
    )pbdoc");

    // Expose accepts function
    m.def("accepts", &accepts, R"pbdoc(
        Check if the parser accepts the given sequence of characters.
        This function dynamically traverses the tree, following both character
        transitions and epsilon transitions.
    )pbdoc");

    // Expose step function
    m.def("step", &step, R"pbdoc(
        Perform a single step in the parser with the given character.
        Supports epsilon transitions and returns the next ParserNode.
    )pbdoc");

    // Expose special_symb_in_transitions (ParserState version)
    m.def("special_symb_in_transitions", 
          py::overload_cast<const ParserState&, const SpecialSymb>(&special_symb_in_transitions), 
          R"pbdoc(
              Check if a special symbol is present in the transitions of a given parser state.
          )pbdoc");

    // Expose special_symb_in_transitions (Transition vector version)
    m.def("special_symb_in_transitions", 
          py::overload_cast<const std::vector<Transition>&, const SpecialSymb>(&special_symb_in_transitions), 
          R"pbdoc(
              Check if a special symbol is present in a vector of transitions.
          )pbdoc");
}
