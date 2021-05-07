import os

from .lang_generators import cpp

KNOWN_GENERATORS = {
    'cpp': cpp
}

def register_generator(lang, module):
    KNOWN_GENERATORS[lang] = module


def __generate_type(generator, namespace, name, jidl):

    structure_format = generator.get_structure_format()

    relative_file_location = generator.calculate_relative_file_location(namespace, name)
    type_open_data = generator.calculate_type_open(namespace, name, jidl)
    type_body_data = generator.calculate_type_body(namespace, name, jidl)
    type_close_data = generator.calculate_type_close(namespace, name, jidl)

    data = {**type_open_data, **type_body_data, **type_close_data}

    return {relative_file_location: structure_format.format(**data)}

def __generate(generator, jidl, namespace=None):

    if namespace is None:
        namespace = []

    type_strs = {}

    namespaces, structures = jidl['namespaces'], jidl['structures']

    for name, _jidl in namespaces.items():
        type_strs.update(__generate(generator, _jidl, namespace+[name]))

    for name, _jidl in structures.items():
        type_strs.update(__generate_type(generator, namespace, name, _jidl))

    return type_strs


def generate(lang, jidl, dest):
    generator = KNOWN_GENERATORS[lang]

    ext = generator.get_ext()

    type_strs = __generate(generator, jidl)

    for type_dest, type_str in type_strs.items():
        full_dest = os.path.join(dest, type_dest)
        os.makedirs(os.path.dirname(full_dest), exist_ok=True)
        with open(full_dest, 'w+') as f:
            f.write(type_str)
