project(dwarfgen_test)
cmake_minimum_required(VERSION 3.12.4)

set(CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake-ada-master")

add_library(test_cpp SHARED
${CMAKE_HOME_DIRECTORY}/src/cpp/structs.cpp
)
target_compile_options(test_cpp PRIVATE -g -fPIC)

install(TARGETS test_cpp LIBRARY DESTINATION lib)
