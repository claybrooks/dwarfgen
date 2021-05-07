
primitives = [
    'char',
    'unsigned char',
    'short',
    'unsigned short',
    'int',
    'unsigned int',
    'float',
    'double',
]

structure_format =\
"""{includes}
{namespace_open}
typedef struct {name}{inheritance} {{

public:
    {public_members}

protected:
    {protected_members}

private:
    {private_members}

}} {name};
{namespace_close}
"""


def default_struct_data():
    return {
        'includes': '',
        'namespace_open': '',
        'name': '',
        'inheritance': '',
        'public_members': '',
        'protected_members': '',
        'private_members': '',
        'namespace_close': '',
    }

def get_ext():
    return ".hpp"

def generate_type(namespace, name, jidl):
    struct_data = default_struct_data()

    if name == 'StructNDerived':
        i = 0

    includes = []
    public_members = []
    protected_members = []
    private_members =[]
    inheritance = []

    accessibility_map = {
        'public': public_members,
        'protected': protected_members,
        'private': private_members
    }

    struct_data['name'] = name
    if namespace != '':
        struct_data['namespace_open'] = 'namespace {} {{'.format(namespace)
        struct_data['namespace_close'] = '}'


    baseStructures = jidl.get('baseStructures', {})
    for baseStructureName, baseStructureJidl in baseStructures.items():
        base_struct_str = baseStructureName.replace('::', '_')
        includes.append('{}{}'.format(base_struct_str, get_ext()))
        inheritance.append(baseStructureJidl['accessibility'] + ' ' + base_struct_str)

    for type_name, type_jidl in jidl.get('staticMembers', {}).items():
        if 'members' not in jidl:
            jidl['members'] = {}

        jidl['members'][type_name] = dict(type_jidl)
        jidl['members'][type_name]['type'] = 'static ' + jidl['members'][type_name]['type']

    for type_name, type_jidl in jidl.get('members', {}).items():
        member_str_f = '{type} {name};'
        array_member_str_f = '{type} {name}[{size}];'

        str_f = member_str_f

        member_type = type_jidl['type']
        str_data = {
            'type': member_type,
            'name': type_name,
        }

        if member_type.startswith('static '):
            member_type = member_type.replace('static ', '')

        if member_type.startswith('array of '):
            member_type = member_type.replace('array of ', '')

        if member_type not in primitives:
            include_str = namespace.replace('::', '_')
            member_type = member_type.replace('::', '_')
            if include_str:
                include_str = include_str + '_' + member_type
            else:
                include_str = member_type

            includes.append('{}{}'.format(include_str, get_ext()))

        if 'array of' in type_jidl['type']:
            str_data['type'] = str_data['type'].replace('array of', '')
            str_data['size'] = type_jidl['upperBound'] + 1
            str_f = array_member_str_f

        accessibility_map[type_jidl['accessibility']].append(str_f.format(**str_data))

    struct_data['includes'] = '\n'.join(['#include "{}"'.format(x) for x in includes])
    struct_data['public_members'] = '\n    '.join(public_members)
    struct_data['protected_members'] = '\n    '.join(protected_members)
    struct_data['private_members'] = '\n    '.join(private_members)
    struct_data['inheritance'] = ' : ' + ', '.join(inheritance) if len(inheritance) > 0 else ''

    filename = namespace.replace('::', '_')
    if filename:
        filename = filename + '_' + name
    else:
        filename = name

    return {filename: structure_format.format(**struct_data)}

def generate(jidl, namespace=''):
    type_strs = {}

    namespaces, structures = jidl['namespaces'], jidl['structures']

    for name, _jidl in namespaces.items():
        type_strs.update(generate(_jidl, namespace + '::' + name if namespace != '' else name))

    for name, _jidl in structures.items():
        type_strs.update(generate_type(namespace, name, _jidl))

    return type_strs
