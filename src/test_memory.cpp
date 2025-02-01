#include <iostream>
#include <vector>
#include <string>
#include <cstdlib> // For rand()
#include <fstream> // For reading memory usage
#include <unistd.h> // For getpid()
#include "parser.h"

// Function to get the current memory usage in KB (Linux-specific)
size_t get_memory_usage() {
    std::ifstream statm("/proc/self/statm");
    size_t size, resident, share, text, lib, data, dt;
    statm >> size >> resident >> share >> text >> lib >> data >> dt;
    statm.close();
    return resident * sysconf(_SC_PAGESIZE) / 1024; // Convert pages to KB
}

// Mock FastMultiChoicesParser class for demonstration
class FastMultiChoicesParser {
public:
    FastMultiChoicesParser(const std::vector<std::vector<std::string>>& data) {
        // Simulate some memory usage
        this->data = data;
    }

    ~FastMultiChoicesParser() {
        // Clean up resources
    }

private:
    std::vector<std::vector<std::string>> data;
};

std::vector<int> stringToVector(const std::string& str) {
    std::vector<int> vec;

    // Convert each character in the string to its ASCII value and store it in the vector
    for (char c : str) {
        vec.push_back(static_cast<int>(c));
    }

    return vec;
}

int main() {
    // Step 1: Measure initial memory usage
    size_t mem_init = get_memory_usage();
    std::cout << "Initial memory usage: " << mem_init << " KB" << std::endl;

    // Step 2: Create a large dataset
    std::vector<std::vector<std::vector<int>>> l;

    std::vector<std::vector<int>> large_data;
    for (int i = 0; i < 100000; ++i) {
        large_data.push_back(stringToVector(std::to_string(rand() % 10)));
    }
    l.push_back(large_data);

    // Step 3: Measure memory usage before creating the parser
    size_t mem_before = get_memory_usage();
    std::cout << "Memory usage before parser creation: " << mem_before << " KB" << std::endl;

    // Step 4: Create the parser and measure memory usage
    auto root = construct_tree(l);
    size_t mem_during = get_memory_usage();
    std::cout << "Memory usage during parser lifetime: " << mem_during << " KB" << std::endl;

    // Step 5: Delete the parser and measure memory usage
    delete root;
    size_t mem_after = get_memory_usage();
    std::cout << "Memory usage after parser deletion: " << mem_after << " KB" << std::endl;

    // Step 6: Print memory usage at each stage
    std::cout << "Memory usage summary:" << std::endl;
    std::cout << "  Initial: " << mem_init << " KB" << std::endl;
    std::cout << "  Before parser creation: " << mem_before << " KB" << std::endl;
    std::cout << "  During parser lifetime: " << mem_during << " KB" << std::endl;
    std::cout << "  After parser deletion: " << mem_after << " KB" << std::endl;

    return 0;
}