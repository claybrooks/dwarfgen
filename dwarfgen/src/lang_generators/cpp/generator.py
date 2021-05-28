import os

def get_primitives():
    return [
        'char',
        'unsigned char',
        'short',
        'unsigned short',
        'int',
        'unsigned int',
        'float',
        'double',
    ]

def get_structure_format():
    return \
"""{includes}
{namespace_open}
typedef struct {name}{inheritance} {{

    {members}

}} {name};
{namespace_close}
"""


def get_type_open_data():
    return {
        'includes': '',
    }

def get_type_body_data():
    return {
        'namespace_open': '',
        'name': '',
        'inheritance': '',
        'members': '',
        'namespace_close': '',
    }

def get_type_close_data():
    return {}

def get_ext():
    return ".hpp"

def calculate_relative_file_location(namespace, name):
    folders = os.path.sep.join(namespace)
    return os.path.join(folders, '{}{}'.format(name, get_ext()))

def calculate_member_include(member_name, member_data):
    member_type = member_data['type']

    if 'array of ' in member_type:
        member_type = member_type.replace('array of ', '')

    if member_type in get_primitives():
        return None

    tokens = member_type.split('::')
    namespace = tokens[:-1]
    typename = tokens[-1]

    return calculate_relative_file_location(namespace, typename)

def calculate_member_includes(jidl):
    includes = []
    for member_name, member_data in jidl.items():
        member_include = calculate_member_include(member_name, member_data)
        if member_include is not None:
            includes.append(member_include)
    return includes

def calculate_type_open(namespace, name, jidl):

    includes = []
    includes.extend(calculate_member_includes(jidl.get('staticMembers', {})))
    includes.extend(calculate_member_includes(jidl.get('members', {})))
    includes.extend(calculate_member_includes(jidl.get('baseStructures', {})))

    type_open_data = get_type_open_data()
    type_open_data['includes'] = '\n'.join('#include "{}"'.format(x) for x in includes)

    return type_open_data


def calculate_member_str(name, jidl, is_static=False):
    member_str_f = '{type} {name};'
    array_member_str_f = '{type} {name}[{size}];'

    str_f = member_str_f

    member_type = jidl['type']
    str_data = {
        'type': member_type,
        'name': name,
    }

    if member_type.startswith('static '):
        member_type = member_type.replace('static ', '')

    if member_type.startswith('array of '):
        member_type = member_type.replace('array of ', '')

    if 'array of ' in jidl['type']:
        str_data['type'] = str_data['type'].replace('array of', '')
        str_data['size'] = jidl['upperBound'] + 1
        str_f = array_member_str_f

    member_str = str_f.format(**str_data)
    if is_static:
        member_str = 'static ' + member_str

    member_str = jidl['accessibility'] + ': ' + member_str
    return member_str


def calculate_type_body(namespace, name, jidl):

    body_data = get_type_body_data()

    members = []
    inheritance = []

    body_data['name'] = name
    if namespace != []:
        body_data['namespace_open'] = 'namespace {} {{'.format('::'.join(namespace))
        body_data['namespace_close'] = '}'

    for type_name, data in jidl.get('baseStructures', {}).items():
        inheritance.append(data['accessibility'] + ' ' + type_name)

    for member_name, member_jidl in jidl.get('staticMembers', {}).items():
        members.append(calculate_member_str(member_name, member_jidl, is_static=True))

    for member_name, member_jidl in jidl.get('members', {}).items():
        members.append(calculate_member_str(member_name, member_jidl))

    body_data['members'] = '\n    '.join(members)
    body_data['inheritance'] = ' : ' + ', '.join(inheritance) if len(inheritance) > 0 else ''

    return body_data

def calculate_type_close(namespace, name, jidl):
    return {}
