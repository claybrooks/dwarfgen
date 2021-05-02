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


class TestDwarfGen(unittest.TestCase):

    @classmethod
    def get_test_name(cls, name, namespaces):
        if namespaces == []:
            return 'test{}_{}'.format('_'.join(namespaces), name)
        else:
            return 'test_{}_{}'.format('_'.join(namespaces), name)

    @classmethod
    def get_tokens_from_name(cls, test_name):
        tokens = test_name.split('_')[1:]
        if len(tokens) == 1:
            name = tokens[0]
            namespace = []
        else:
            name = tokens[-1]
            namespace = tokens[:-1]

        return name, namespace

    @classmethod
    def get_tests(cls, structure_list):
        tests = []
        for name, namespaces in structure_list:
            tests.append(cls.get_test_name(name, namespaces))
        return tests

    @classmethod
    def add_test(cls, class_inst, test_name):
        name, namespace = cls.get_tokens_from_name(test_name)
        setattr(
            class_inst,
            test_name,
            lambda inst=class_inst, x=name, ns=namespace: inst.assert_struct_equal(x, ns)
        )

    @classmethod
    def __test_structures_from_jidl(cls, jidl_json, structures, namespaces):

        for struct in jidl_json['structures']:
            structures.append((struct, list(namespaces)))

        for ns in jidl_json['namespaces']:
            new_namespace = list(namespaces) + [ns]
            cls.__test_structures_from_jidl(jidl_json['namespaces'][ns], structures, new_namespace)

    @classmethod
    def test_structures_from_jidl(cls, jidl_path):
        with open(jidl_path, 'r') as f:
            jidl_json = json.load(f)

        structures = []
        namespaces = []
        cls.__test_structures_from_jidl(jidl_json, structures, namespaces)
        return structures

    def __init__(self, test_name, so_file, jidl_file, *args, **kwargs):
        TestDwarfGen.add_test(self, test_name)
        self.so_file = so_file
        self.jidl_file = jidl_file
        self.setup_done = False

        super().__init__(test_name, *args, **kwargs)

    def setUp(self):
        super().setUp()

        ns = dwarfgen.process([self.so_file])
        self.calculated_jidl = {}
        ns.to_json(self.calculated_jidl)

        with open(self.jidl_file, 'r') as f:
            self.expected_jidl = json.load(f)

    def tearDown(self):
        super().tearDown()

    def __get_structure(self, jidl, structure_name, namespace=None):
        json_ptr = jidl

        for ns in namespace:
            try:
                json_ptr = json_ptr['namespaces'][ns]
            except KeyError:
                self.fail("Namespace {} doesn't exist".format(ns))

        try:
            return json_ptr['structures'][structure_name]
        except KeyError:
            self.fail("Structure {} doesn't exist in \n{}".format(structure_name, json.dumps(jidl, indent=4)))

    def __get_calculated_structure(self, structure_name, namespace=None):
        return self.__get_structure(self.calculated_jidl, structure_name, namespace)

    def __get_expected_structure(self, structure_name, namespace=None):
        return self.__get_structure(self.expected_jidl, structure_name, namespace)

    def assert_struct_equal(self, structure_name, namespace=None):
        calculated_struct = self.__get_calculated_structure(structure_name, namespace)
        expected_struct = self.__get_expected_structure(structure_name, namespace)

        self.assertEqual(calculated_struct, expected_struct)


def add_to_suite(test_class, so_file, jidl_file, loader, suite):
    names = test_class.get_tests(test_class.test_structures_from_jidl(jidl_file))
    for name in names:
        suite.addTest(test_class(name, so_file, jidl_file))


if __name__ == '__main__':

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    add_to_suite(TestDwarfGen, './bin/lib/libtest_cpp.so', './src/cpp/jidl.json', loader, suite)
    add_to_suite(TestDwarfGen, './bin/lib/libtest_ada.so', './src/ada/jidl.json', loader, suite)

    result = unittest.TextTestRunner().run(suite)
    sys.exit(not result.wasSuccessful())
