// Software Name : multi-choices-parser
// SPDX-FileCopyrightText: Copyright (c) 2025 Orange SA
// SPDX-License-Identifier: GPL-2.0-or-later

// This software is distributed under the GNU General Public License v2.0 or later,
// see the "LICENSE.txt" file for more details or GNU General Public License v2.0 or later

// Authors: Hichem Ammar Khodja

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

std::vector<int> stringToVector(const std::string& str) {
    std::vector<int> vec;

    // Convert each character in the string to its ASCII value and store it in the vector
    for (char c : str) {
        vec.push_back(static_cast<int>(c));
    }

    return vec;
}

void test(){
    size_t mem_init = get_memory_usage();
    std::cout << "Initial memory usage: " << mem_init << " KB" << std::endl;

    // Step 2: Create a large dataset
    std::vector<std::vector<std::vector<int>>> l;

    std::vector<std::vector<int>> large_data;
    for (int i = 0; i < 100000; ++i) {
        large_data.push_back(stringToVector(std::to_string(rand() % 10000000)));
    }
    l.push_back(large_data);

    // Step 3: Measure memory usage before creating the parser
    size_t mem_before = get_memory_usage();
    std::cout << "Memory usage after data creation: " << mem_before << " KB" << std::endl;

    // Step 4: Create the parser and measure memory usage
    auto root = construct_tree(l);
    // size_t mem_during = get_memory_usage();
    // std::cout << "Memory usage after parser creation: " << mem_during << " KB" << std::endl;
}
    

int main() {
    // Step 1: Measure initial memory usage
    test();
    // Step 5: Delete the parser and measure memory usage
    size_t mem_after = get_memory_usage();
    std::cout << "Memory usage final: " << mem_after << " KB" << std::endl;
    return 0;
}