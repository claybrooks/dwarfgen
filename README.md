# Dwarfgen

## Description
Autogenerate IDL and code from compiled code.

## Requirements

* Python 3.3+
* Pip


## Install

```
pip install dwarfgen
```

## Examples

``` python
# Help command
python -m dwarfgen -h
```

``` python
# Generate JIDL for libtest_cpp.so and place jidl.json in ~/cpp/jidl
python -m dwarfgen --file test/bin/lib/libtest_cpp.so --to-idl jidl --to-idl-dest ~/cpp/jidl
```

``` python
# Generate JIDL for libtest_ada.so and place jidl.json in ~/ada/jidl
python -m dwarfgen --file test/bin/lib/libtest_ada.so --to-idl jidl --to-idl-dest ~/ada/jidl
```

