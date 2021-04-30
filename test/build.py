import subprocess
import sys
import os
import platform


PLAT_STR = "{}-{}".format(platform.system(), platform.machine())


def run():
    os.makedirs('cmake-build', exist_ok=True)

    CXX_COMPILER="g++-10"
    CXX_STANDARD="20"

    CMAKE_GENERATE=[
        "cmake",
        "-S",
        ".",
        "-Bcmake-build/{}".format(PLAT_STR),
        "-DCMAKE_BUILD_TYPE=Debug",
        "-DCMAKE_INSTALL_PREFIX=bin",
    ]

    CMAKE_INSTALL=[
        "cmake",
        "--build",
        "cmake-build/{}".format(PLAT_STR),
        "--target",
        "install"
    ]

    if sys.platform.startswith('win'):
        shell = True
    else:
        shell = False

    subprocess.check_call(CMAKE_GENERATE, stderr=subprocess.STDOUT, shell=shell)
    subprocess.check_call(CMAKE_INSTALL, stderr=subprocess.STDOUT, shell=shell)

if __name__ == '__main__':
    run()