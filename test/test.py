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


CPP_STRUCTURES = [
    ('StructA', []),
    ('StructB', []),
    ('StructC', ['Namespace']),
    ('StructD', ['Namespace', 'InnerNamespace'])
]

ADA_STRUCTURES = [
    ('records__record_a', []),
    ('records__record_b', []),
]


class TestDwarfGen(unittest.TestCase):

    @classmethod
    def get_test_name(cls, name, namespaces):
        return 'test_{}_{}'.format('_'.join(namespaces), name)

    @classmethod
    def get_tests(cls, structure_list):
        tests = []
        for name, namespaces in structure_list:
            tests.append(cls.get_test_name(name, namespaces))
        return tests

    @classmethod
    def add_tests(cls, class_inst, structure_list):

        for name, namespace in structure_list:
            setattr(
                class_inst,
                cls.get_test_name(name, namespace),
                lambda inst=class_inst, x=name, ns=list(namespace): inst.assert_struct_equal(x, ns)
            )

    def __init__(self, test_name, structures, so_file, jidl_file, *args, **kwargs):
        TestDwarfGen.add_tests(self, structures)
        self.so_file = so_file
        self.jidl_file = jidl_file

        super().__init__(test_name, *args, **kwargs)

    def setUp(self):
        super().setUp()

        self.ns = dwarfgen.process([self.so_file])
        self.calculated_jidl = {}
        self.ns.to_json(self.calculated_jidl)

        with open(self.jidl_file, 'r') as f:
            self.expected_jidl = json.load(f)

    def tearDown(self):
        super().tearDown()

    def __get_structure(self, jidl, structure_name, namespace=None):
        json_ptr = jidl

        for ns in namespace:
            json_ptr = json_ptr['namespaces'][ns]

        return json_ptr['structures'][structure_name]

    def __get_calculated_structure(self, structure_name, namespace=None):
        return self.__get_structure(self.calculated_jidl, structure_name, namespace)

    def __get_expected_structure(self, structure_name, namespace=None):
        return self.__get_structure(self.expected_jidl, structure_name, namespace)

    def assert_struct_equal(self, structure_name, namespace=None):
        calculated_struct = self.__get_calculated_structure(structure_name, namespace)
        expected_struct = self.__get_expected_structure(structure_name, namespace)

        self.assertEqual(calculated_struct, expected_struct)


def add_to_suite(test_class, structures, so_file, jidle_file, loader, suite):
    names = test_class.get_tests(structures)
    for name in names:
        suite.addTest(test_class(name, structures, so_file, jidle_file))

if __name__ == '__main__':

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    add_to_suite(TestDwarfGen, CPP_STRUCTURES, './bin/lib/libtest_cpp.so', './src/cpp/jidl.json', loader, suite)
    add_to_suite(TestDwarfGen, ADA_STRUCTURES, './bin/lib/libtest_ada.so', './src/ada/jidl.json', loader, suite)

    result = unittest.TextTestRunner().run(suite)
    sys.exit(not result.wasSuccessful())

