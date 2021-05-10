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
            lambda inst=class_inst, x=name, ns=namespace: inst.assert_equal(x, ns)
        )

    @classmethod
    def __test_structures_from_jidl(cls, jidl_json, tests, namespaces):

        for struct in jidl_json['structures']:
            tests.append((struct, list(namespaces)))

        for enum in jidl_json['enumerations']:
            tests.append((enum, list(namespaces)))

        for union in jidl_json['unions']:
            tests.append((union, list(namespaces)))

        for ns in jidl_json['namespaces']:
            new_namespace = list(namespaces) + [ns]
            cls.__test_structures_from_jidl(jidl_json['namespaces'][ns], tests, new_namespace)

    @classmethod
    def structures_from_jidl(cls, jidl_json):
        tests = []
        namespaces = []
        cls.__test_structures_from_jidl(jidl_json, tests, namespaces)
        return tests

    def __init__(self, test_name, so_file, calculated_jidl, expected_jidl, *args, **kwargs):
        TestDwarfGen.add_test(self, test_name)
        self.so_file = so_file
        self.calculated_jidl = calculated_jidl
        self.expected_jidl = expected_jidl

        super().__init__(test_name, *args, **kwargs)
        self.maxDiff = None

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def __get(self, jidl, name, debug_name, namespace=None):
        json_ptr = jidl

        for ns in namespace:
            try:
                json_ptr = json_ptr['namespaces'][ns]
            except KeyError:
                self.fail("Namespace {} doesn't exist".format(ns))

        if name in json_ptr['structures']:
            return json_ptr['structures'][name]
        elif name in json_ptr['enumerations']:
            return json_ptr['enumerations'][name]
        elif name in json_ptr['unions']:
            return json_ptr['unions'][name]
        else:
            self.fail("{} doesn't exist in {}".format(name, debug_name))

    def __get_calculated(self, name, namespace=None):
        return self.__get(self.calculated_jidl, name, "calculated", namespace)

    def __get_expected(self, name, namespace=None):
        return self.__get(self.expected_jidl, name, "expected", namespace)

    def assert_equal(self, name, namespace=None):
        calculated = self.__get_calculated(name, namespace)
        expected = self.__get_expected(name, namespace)

        self.assertEqual(
            calculated,
            expected,
            msg="{}\nExpected\n{}\nCalculated\n{}".format(name, json.dumps(expected, indent=4), json.dumps(calculated, indent=4))
        )


def add_to_suite(test_class, so_file, jidl_file, loader, suite):

    ns = dwarfgen.process([so_file])
    calculated_jidl = {}
    ns.to_json(calculated_jidl)

    with open(jidl_file, 'r') as f:
        expected_jidl = json.load(f)

    names = test_class.get_tests(test_class.structures_from_jidl(expected_jidl))
    for name in names:
        suite.addTest(test_class(name, so_file, calculated_jidl, expected_jidl))


def run(so_file, jidl_file):
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    add_to_suite(TestDwarfGen, so_file, jidl_file, loader, suite)

    result = unittest.TextTestRunner().run(suite)
    return result.wasSuccessful()
