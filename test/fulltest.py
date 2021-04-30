import os
import sys

TEST_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.realpath(os.path.join(TEST_DIR, '..')))

import build_cpp
import build_ada
import subprocess

build_cpp.run()
build_ada.run()

try:
    subprocess.check_call([
        "python3",
        "test.py",
    ])
except subprocess.CalledProcessError:
    sys.exit(1)

