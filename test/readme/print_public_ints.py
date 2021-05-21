
# with open('/path/to/jidl.json', 'r') as f:
#     jidl = json.load(f)
jidl = {
    "namespaces": {},
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

# list all public integers
for name, data in jidl['structures'].items():
    for member_name, member_data in data['members'].items():
        if member_data['accessibility'] == 'public' and member_data['type'] == 'int':
            print ("{}.{}".format(name, member_name) + " is a public int!")