import logging
import subprocess
import sys
import os
import platform


PLAT_STR = "{}-{}".format(platform.system(), platform.machine())

def run(compiler, compiler_options, linker_options):

    os.makedirs('cmake-build', exist_ok=True)

    CMAKE_GENERATE=[
        "cmake",
        "-S",
        ".",
        "-Bcmake-build/{}".format(PLAT_STR),
        "-DCMAKE_BUILD_TYPE=Debug",
        "-DCMAKE_INSTALL_PREFIX=bin",
        "-DCMAKE_CXX_FLAGS={}".format(' '.join(compiler_options))
    ]

    CMAKE_BUILD=[
        "cmake",
        "--build",
        "cmake-build/{}".format(PLAT_STR),
        "--target",
        "install",
    ]

    if sys.platform.startswith('win'):
        shell = True
    else:
        shell = False

    try:
        subprocess.check_call(CMAKE_GENERATE, stderr=subprocess.STDOUT, shell=shell)
        subprocess.check_call(CMAKE_BUILD, stderr=subprocess.STDOUT, shell=shell)
        return True
    except subprocess.CalledProcessError as e:
        logging.error("Error {}".format(e))
        return False

if __name__ == '__main__':
    run()