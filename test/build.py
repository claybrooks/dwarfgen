import subprocess
import sys

CXX_COMPILER="g++-10"
CXX_STANDARD="20"

CMAKE_GENERATE=[
    "cmake",
    "-Bcmake-build",
    "-DCMAKE_BUILD_TYPE=Debug",
    "-DCMAKE_INSTALL_PREFIX=bin",
]

CMAKE_INSTALL=[
    "cmake",
    "--build",
    "cmake-build",
    "--target install"
]

if sys.platform.startswith('win'):
    shell = True
else:
    shell = False

subprocess.check_call(CMAKE_GENERATE, stderr=subprocess.STDOUT, shell=shell, cwd="test")
subprocess.check_call(CMAKE_INSTALL, stderr=subprocess.STDOUT, shell=shell, cwd="test")