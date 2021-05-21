import json


# with open('/path/to/jidl_1.json', 'r') as f:
#     jidl_1 = json.load(f)
jidl_1 = {
    "namespaces": {},
    "enumerations": {},
    "unions": {},
    "structures": {
        "Structure1": {
            "byteSize": 8,
            "members": {
                "a": {
                    "byteOffset": 0,
                    "byteSize": 1,
                    "type": "char",
                    "accessibility": "public"
                },
                "b": {
                    "byteOffset": 4,
                    "byteSize": 4,
                    "type": "int",
                    "accessibility": "public"
                }
            }
        }
    }
}

# with open('/path/to/jidl_2.json', 'r') as f:
#     jidl_2 = json.load(f)
jidl_2 = {
    "namespaces": {
        "InnerNamespace": {
            "namespaces": {},
            "enumerations": {},
            "unions": {},
            "structures": {
                "Structure2": {
                    "byteSize": 1,
                    "members": {
                        "a": {
                            "byteOffset": 0,
                            "byteSize": 1,
                            "type": "char",
                            "accessibility": "public"
                        },
                    }
                }
            }
        }
    },
    "enumerations": {},
    "unions": {},
    "structures": {
        "MyStruct": {
            "byteSize": 8,
            "members": {
                "a": {
                    "byteOffset": 0,
                    "byteSize": 1,
                    "type": "char",
                    "accessibility": "public"
                },
                "b": {
                    "byteOffset": 4,
                    "byteSize": 4,
                    "type": "int",
                    "accessibility": "public"
                }
            }
        }
    }
}

# get structure 1 size
structure_1_size = jidl_1['structures']['Structure1']['byteSize']

# get structure 2 size, that resides in a different namespace and is of a different name
structure_2_size = jidl_2['namespaces']['InnerNamespace']['structures']['Structure2']['byteSize']

# ensure they are equal
if structure_1_size != structure_2_size:
    print ("Structure1 size does not eqaul InnerNamespace::Structure2 size!")