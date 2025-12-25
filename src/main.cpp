// Software Name : multi-choices-parser
// SPDX-FileCopyrightText: Copyright (c) 2025 Orange SA
// SPDX-License-Identifier: GPL-2.0-or-later

// This software is distributed under the GNU General Public License v2.0 or later,
// see the "LICENSE.txt" file for more details or GNU General Public License v2.0 or later

// Authors: Hichem Ammar Khodja

#include <pybind11/pybind11.h>
#include <pybind11/stl.h> // For std::vector
#include <pybind11/functional.h> // For std::function
#include "parser.h"

namespace py = pybind11;

// Expose the code to Python
PYBIND11_MODULE(_core, m) {
    m.doc() = "pybind11 ParserNode module with epsilon transitions and group-based tree construction";

    // Expose TransitionMode enum
    py::enum_<TransitionMode>(m, "TransitionMode")
        .value("SORTED_ARRAY", TransitionMode::SORTED_ARRAY)
        .value("HASH_MAP", TransitionMode::HASH_MAP)
        .export_values();

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
        .def_readwrite("next", &Transition::next);
        // .def("__lt__", &Transition::operator<); // Expose comparison operator

    // Expose ParserNode
    py::class_<ParserNode, std::shared_ptr<ParserNode>>(m, "ParserNode")
        .def(py::init<TransitionMode>(), py::arg("mode") = TransitionMode::SORTED_ARRAY)
        .def_readwrite("mode", &ParserNode::mode)
        .def_readwrite("transitions", &ParserNode::transitions)
        .def_readwrite("transitions_map", &ParserNode::transitions_map)
        .def("add_transition", &ParserNode::add_transition, "Add a transition to another node")
        .def("find_transition", &ParserNode::find_transition, "Find a transition by character")
        .def("has_transition", &ParserNode::has_transition, "Check if transition exists")
        .def("get_all_transitions", &ParserNode::get_all_transitions, "Get all transitions as vector");

    // Expose ParserState
    py::class_<ParserState>(m, "ParserState")
        .def(py::init<>()) // Default constructor
        .def_readwrite("nodes", &ParserState::nodes)
        .def("add_node", &ParserState::add_node, "Add a node to the state");

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

    // Expose connect_trees function
    m.def("add_sequence", &add_sequence, R"pbdoc(
        Add sequence to parser tree.
    )pbdoc");

    // Expose connect_trees function
    m.def("delete_sequence", &delete_sequence, R"pbdoc(
        Delete sequence from parser tree.
    )pbdoc");

    // Expose construct_tree function
    m.def("construct_tree", &construct_tree,
          py::arg("groups"),
          py::arg("mode") = TransitionMode::SORTED_ARRAY,
          R"pbdoc(
        Construct a ParserNode tree from a list of groups of sequences of integers.
        Each group is a list of sequences, and the tree supports epsilon transitions
        for nullable groups.

        Args:
            groups: List of groups of sequences (list of list of list of int)
            mode: TransitionMode.SORTED_ARRAY (default) or TransitionMode.HASH_MAP
    )pbdoc");

    // Expose accepts function
    m.def("accepts", &accepts, R"pbdoc(
        Check if the parser accepts the given sequence of characters.
        This function dynamically traverses the tree, following both character
        transitions and epsilon transitions.
    )pbdoc");

    m.def("next", &next, R"pbdoc(
        Get next possible characters given Parser state
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
