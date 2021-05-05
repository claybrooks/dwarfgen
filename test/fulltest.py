import os
import sys

TEST_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.realpath(os.path.join(TEST_DIR, '..')))

import build_cpp
import build_ada
import subprocess
import test
import time

success = True

build_ada.run()
success = success and test.run('./bin/lib/libtest_ada.so', './src/ada/jidl.json')

cpp_so = './bin/lib/libtest_cpp.so'
cpp_jidl = './src/cpp/jidl.json'
build_cpp.run(2)
success = success and test.run(cpp_so, cpp_jidl)

build_cpp.run(3)
success = success and test.run(cpp_so, cpp_jidl)

build_cpp.run(4)
success = success and test.run(cpp_so, cpp_jidl)

sys.exit(not success)