# Dwarfgen

## Description

Use dwarfgen to

- Generate datastructures that promote easy domain specific analysis of code
- Generate code in other languages
- Generate IDL's (Interactive Data Language)

Dwarfgen introduces JIDL (JSON IDL) to the already crowded IDL space.  JIDL
is less about being an IDL and more about being an intermediate representation
of your code for downstream processing.

``` cpp
// sample.cpp, compiled with '-g -fPIC -gdwarf-2' and default alignment
typedef struct MyStruct
{
    char a;
    int b;
} MyStruct;
```

``` json
// output of 'dwarfgen --file sample.o --to-idl jidl --to-idl-dest ~/jidl'
{
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
```

``` python
# Some simple domain-specific static analysis
import json

with open('/path/to/jidl.json', 'r') as f:
    jidl = json.load(f)

# list all public integers
for name, data in jidl['structures'].items():
    for member_name, member_data in data['members'].items():
        if member_data['accessibility'] == 'public' and member_data['type'] == 'int':
            print ("{}.{}".format(name, member_name) + " is a public int!")
```

The above example isn't extremely complicated or even useful.  It's meant to illustrate the simplicity of JIDL analysis
where source code analysis would be rather difficult to implement correctly.  The amount of effort required for source
level analysis only increases when multiple languages are involved.

A more useful example would be to ensure types are identical in size, within and across shared objects.

``` python
import json

with open('/path/to/jidl_1.json', 'r') as f:
    jidl_1 = json.load(f)

with open('/path/to/jid_2.json', 'r') as f:
    jidl_2 = json.load(f)

# get structure 1 size
structure_1_size = jidl_1['structures']['Structure1']['byteSize']

# get structure 2 size, that resides in a different namespace and is of a different name
structure_2_size = jidl_2['namespaces']['InnerNamespace']['structures']['Structure2']['byteSize']

# ensure they are equal
if structure_1_size != structure_2_size:
    print ("Structure1 != InnerNamespace::Structure2 !!")
```

One thing that can be easily missed when analyzing source code directly are packing rules of languages as well as
compiler options that can adjust alignment of structures.

For example

``` cpp
typedef struct StructA {
    char a;
    int b;
} StructA;

#pragma pack(1)
typedef struct StructB {
    char a;
    int b;
} StructB;
```

StructA bytesize is 8 while StructB bytesize is 5.  The `#pragma pack(1)` statement tells the compiler to not add
padding to the structure.  This is easily handled by dwarfgen but can be difficult to implement correctly otherwise.

>In general, analyzing the output of the compiler hides almost all complicating factors versus analyzing the source code
directly.  The simple reason is that you would have to re-implement all compiler specific rules in your analysis
(including platform specific differences)

## Install

```
pip install dwarfgen
```

# DWARF Version Support

- :heavy_check_mark: - Language specific features implemented
- :warning: - Core DWARF features implemented, language specific features are not implemented
- :x: - Not implemented

|          | Ada                |  C                 | C++                | Cobol              | Fortran            |
| -------- | :----------------: | :----------------: | :----------------: | :----------------: | :----------------: |
| DWARF v2 | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :warning:          | :warning:          |
| DWARF v3 | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :warning:          | :warning:          |
| DWARF v4 | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :warning:          | :warning:          |
| DWARF v5 | :x:                | :x:                | :x:                | :x:                | :x:                |

# Compiler Support

- :heavy_check_mark: - Tested
- :warning: - Untested
- :x: - Not Implemented

|          | gcc                |  llvm              |
| -------- | :----------------: | :----------------: |
| DWARF v2 | :heavy_check_mark: | :warning:          |
| DWARF v3 | :heavy_check_mark: | :warning:          |
| DWARF v4 | :heavy_check_mark: | :warning:          |
| DWARF v5 | :x:                | :x:                |

# Language-Feature Support

- :heavy_check_mark: - Implemented
- :warning: - Results may vary
- :x: - Not implemented

| Common   | Accessibility      | Arrays             | Custom Types        |
| -------- | :----------------: | :----------------: | :-----------------: |
| DWARF v2 | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark:  |
| DWARF v3 | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark:  |
| DWARF v4 | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark:  |
| DWARF v5 | :x:                | :x:                | :x:                 |

| Ada      | Constrained Types   | Records            | Repspec            | Tagged Types       | Variant Records |
| -------- | :-----------------: | :----------------: | :----------------: | :----------------: | :-------------: |
| DWARF v2 | :heavy_check_mark:  | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :x:             |
| DWARF v3 | :heavy_check_mark:  | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :x:             |
| DWARF v4 | :heavy_check_mark:  | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :x:             |
| DWARF v5 | :x:                 | :x:                | :x:                | :x:                | :x:             |

| C        | Enumerations       | Structures         | Unions             | Bitfields          | Pointers           |
| -------- | :----------------: | :----------------: | :----------------: | :----------------: | :----------------: |
| DWARF v2 | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
| DWARF v3 | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
| DWARF v4 | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: |
| DWARF v5 | :x:                | :x:                | :x:                | :x:                | :x:                |

| C++      | Classes            | Inheritance        | Namespaces         | References         | STL       | Templates      |
| -------- | :----------------: | :----------------: | :----------------: | :----------------: | :-------: | :------------: |
| DWARF v2 | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :warning: | :warning:      |
| DWARF v3 | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :warning: | :warning:      |
| DWARF v4 | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :heavy_check_mark: | :warning: | :warning:      |
| DWARF v5 | :x:                | :x:                | :x:                | :x:                | :x:       | :x:            |

## Examples

``` python
# Help command
python -m dwarfgen -h
```

``` python
# Generate JIDL from a shared object
python -m dwarfgen --file /path/to/shared_object.so --to-idl jidl --to-idl-dest ~/jidl
```

``` python
# Generate cpp code from a shared object
python -m dwarfgen --file /path/to/shared_object.so --to-lang cpp --to-lang-dest ~/autogen/cpp
```

``` python
# Register a custom language generator module and generate in that language
python -m dwarfgen --file /path/to/shared_object.so \
                   --lang-generator python /path/to/module \
                   --to-lang python \
                   --to-lang-dest ~/autogen/python
```
