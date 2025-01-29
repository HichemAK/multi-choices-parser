#include <pybind11/pybind11.h>


typedef struct ParserNode {
    LinkedListTransition transitions;
}ParserNode;

typedef struct Transition {
    int character;
    ParserNode* next;
}Transition;

typedef struct LinkedListTransition{
    Transition transition;
    LinkedListTransition* next;
}LinkedListTransition;

bool accepts(ParserNode node, int* array, int size){
    if (size == 0){
        return true;
    }
    int i = 0;
    bool success;
    while(node) {
        success = false;
        LinkedListTransition temp = node.transitions;
        while(temp){
            if (array[i] == temp.transition.character){
                success = true;
                node = temp.transition.next;
                break; 
            }
            temp = temp.next;
        }
        if(!success) {
            return false;
        }
        i += 1;
        if (i == size){
            return true;
        }
    }
    return false;
}

ParserNode step(ParserNode node, int character){
    LinkedListTransition temp = node.transitions;
    while(temp){
        if (character == temp.transition.character){
            return temp.transition.next;
        }
        temp = temp->next;
    }
    return NULL;
}




std::string hello_from_bin() { return "Hello from multi-choices-parser!"; }

namespace py = pybind11;

PYBIND11_MODULE(_core, m) {
    m.doc() = "pybind11 hello module";

    m.def("hello_from_bin", &hello_from_bin, R"pbdoc(
        A function that returns a Hello string.
    )pbdoc");
}
