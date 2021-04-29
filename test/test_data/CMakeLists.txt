project(dwarfgen_test)
cmake_minimum_required(VERSION 3.12.4)

add_library(test_data SHARED cpp)
set_target_properties(test_data PROPERTIES LINKER_LANGUAGE CXX)

target_compile_options(test_data PRIVATE -g -fPIC -fno-eliminate-unused-debug-symbols)
add_subdirectory(cpp)

install(TARGETS test_data)