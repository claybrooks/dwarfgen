project(dwarfgen_test)
cmake_minimum_required(VERSION 3.12.4)

add_library(test_cpp SHARED ${CMAKE_HOME_DIRECTORY}/src/cpp/struct_a.cpp)
set_target_properties(test_cpp PROPERTIES LINKER_LANGUAGE CXX)
target_compile_options(test_cpp PRIVATE -g -fPIC -fno-eliminate-unused-debug-symbols)

install(TARGETS test_cpp)

