project(dwarfgen_test)
cmake_minimum_required(VERSION 3.12.4)

add_library(test_c SHARED
${CMAKE_HOME_DIRECTORY}/src/structs.c
)
target_compile_options(test_c PRIVATE -g -fPIC)

install(TARGETS test_c LIBRARY DESTINATION lib)
