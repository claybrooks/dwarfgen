import os
import sys

TEST_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.realpath(os.path.join(TEST_DIR, '..')))

import build_cpp
import build_ada
import subprocess
import test
import time
import json
import copy

builder_map = {
    'ada': (build_ada, './bin/lib/libtest_ada.so', './src/ada/jidl.json'),
    'cpp': (build_cpp, './bin/lib/libtest_cpp.so', './src/cpp/jidl.json')
}

def test_lang(lang, config):
    builder, so, jidl = builder_map[lang]

    compilers = config['compilers']
    compiler_options = config['compilerOptions']
    linker_options = config['linkerOptions']

    success = True
    for compiler in compilers:
        for i in range(len(compiler_options)):
            dashed_options = ['-'+x for x in compiler_options[i]]
            if builder.run(compiler, dashed_options, linker_options[i]):
                test_result = test.run(so, jidl)
                success = success and test_result
            else:
                success = False
    return success


if __name__ == '__main__':
    # load the matrix file
    with open("build_matrix.json", 'r') as f:
        build_matrix = json.load(f)

    global_matrix = build_matrix['global']
    language_matrix = build_matrix['language']

    global_compiler_options = global_matrix['compilerOptions']
    global_linker_options = global_matrix['linkerOptions']
    update_matrix = global_matrix['matrix']

    for compilerOptionsList in update_matrix['compilerOptions']:
        compilerOptionsList.extend(global_compiler_options)

    for linkerOptionsList in update_matrix['linkerOptions']:
        linkerOptionsList.extend(global_linker_options)

    for lang, config in language_matrix.items():

        langCompilers = copy.deepcopy(config['compilers'])
        langCompilerOptions = copy.deepcopy(config['compilerOptions'])
        langLinkerOptions = copy.deepcopy(config['linkerOptions'])

        config['compilerOptions'] = copy.deepcopy(update_matrix['compilerOptions'])
        for compilerOptionsList in config['compilerOptions']:
            compilerOptionsList.extend(langCompilerOptions)

        config['linkerOptions'] = copy.deepcopy(update_matrix['linkerOptions'])
        for compilerOptionsList in config['linkerOptions']:
            compilerOptionsList.extend(langLinkerOptions)


    success = True
    for lang, config in language_matrix.items():
        success = success and test_lang(lang, config)

sys.exit(0 if success else 1)