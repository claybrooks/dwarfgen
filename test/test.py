import sys
import os

TEST_DIR = os.path.dirname(os.path.realpath(__file__))
DWARF_GEN_DIR = os.path.realpath(os.path.join(TEST_DIR, '..'))
if DWARF_GEN_DIR not in sys.path:
    sys.path.append(DWARF_GEN_DIR)

import unittest
import dwarfgen
import logging
import json


class TestDwarfgen(unittest.TestCase):
    def setUp(self):
        pass


    def tearDown(self):
        pass


    def __test_jidl_against_expected(self, calculated, expected_file):
        with open(expected_file, 'r') as f:
            expected_jidl = json.load(f)

        self.assertEqual(calculated, expected_jidl)


    def __calculate_jidl(self, files):
        ns = dwarfgen.process(files)
        jidl_json = {}
        ns.to_json(jidl_json)
        return jidl_json


    def __validate_so_against_expected(self, files, expected_jidl_file):
        jidl_json = self.__calculate_jidl(files)
        self.__test_jidl_against_expected(jidl_json, expected_jidl_file)


    def test_CPPStructAToJIDL(self):
        self.__validate_so_against_expected(
            [os.path.realpath('./bin/lib/libtest_cpp.so')],
            os.path.realpath('./src/cpp/struct_a_jidl.json'),
        )


    def test_ADARecordAToJIDL(self):
        self.__validate_so_against_expected(
            [os.path.realpath('./bin/lib/libtest_ada.so')],
            os.path.realpath('./src/ada/test_a/record_a_jidl.json'),
        )


if __name__ == '__main__':
    unittest.main()

