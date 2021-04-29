import unittest
import dwarfgen
import logging
import json


class TestDwarfgen(unittest.TestCase):
    def setUp(self):
        pass


    def tearDown(self):
        pass


    def test_structAToJIDL(self):
        jidl = dwarfgen.process_file('./test/test_data/bin/lib/libtest_data.so')

        jidl_json = {}
        jidl.to_json(jidl_json)

        with open('./test/test_data/cpp/struct_a_jidl.json') as f:
            expected_jidl = json.load(f)

        self.assertEqual(jidl_json, expected_jidl)


if __name__ == '__main__':
    unittest.main()

