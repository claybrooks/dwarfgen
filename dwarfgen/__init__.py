import json
from elftools.elf.elffile import ELFFile

from .namespace import  Namespace
from .structure import Structure
from .member import Member

structures = {}
base_types = {}
array_types = {}
subrange_types = {}
type_defs = {}

def process_file(filename):

    with open(filename, 'rb') as f:
        elffile = ELFFile(f)

        if not elffile.has_dwarf_info():
            print('file has no DWARF info, compile with \'-g\'')
            return

        # get_dwarf_info returns a DWARFInfo context object, which is the
        # starting point for all DWARF-based processing in pyelftools.
        dwarfinfo = elffile.get_dwarf_info()

    namespace = Namespace('')

    for CU in dwarfinfo.iter_CUs():
        top_DIE = CU.get_top_DIE()
        die_info_rec(top_DIE, namespace)

    resolveNamespace(namespace)

    return namespace

def build_base_type(die):
    if die.offset in base_types:
        return

    base_types[die.offset] = {
        'size': die.attributes['DW_AT_byte_size'].value,
        'encoding': die.attributes['DW_AT_encoding'].value,
        'name': die.attributes['DW_AT_name'].value.decode()
    }

def build_structure_type(die, namespace):
    if die.offset in structures:
        return

    # we don't care about non-named things
    if 'DW_AT_name' not in die.attributes:
        return

    # we don't care about things that don't have a size
    if 'DW_AT_byte_size' not in die.attributes:
        return

    name = die.attributes['DW_AT_name'].value.decode()
    size = die.attributes['DW_AT_byte_size'].value

    structure = namespace.add_and_return_structure(name, size)

    if hasattr(die, 'namespace'):
        name = die.namespace + '::' + name
    else:
        name = '::' + name

    structures[die.offset] = {
        'name': name,
        'size': size,
        'members': {}
    }
    members = structures[die.offset]['members']

    for child in die.iter_children():
        if child.tag == 'DW_TAG_member':
            name        = child.attributes['DW_AT_name'].value.decode()
            byte_offset = child.attributes['DW_AT_data_member_location'].value
            type_offset = child.attributes['DW_AT_type'].value

            _member = structure.add_and_return_member(
                name, type_offset, byte_offset
            )

            members[name] = {}
            member = members[name]

            member['name'] = name
            member['byteOffset'] = byte_offset
            member['typeOffset'] = type_offset

            if 'DW_AT_bit_size' in child.attributes:
                value = child.attributes['DW_AT_bit_size'].value
                member['DW_AT_bit_size'] = value
                _member.bit_size = value

            if 'DW_AT_bit_offset' in child.attributes:
                value = child.attributes['DW_AT_bit_offset'].value
                member['DW_AT_bit_offset'] = value
                _member.bit_offset = value

        elif child.tag == 'DW_AT_structure':
            members[name] = child.attributes['DW_AT_type'].value

def build_type_def(die):
    if die.offset in type_defs:
        return

    # ignore typedefs with no type
    if 'DW_AT_type' not in die.attributes:
        return

    type_defs[die.offset] = {
        'name': die.attributes['DW_AT_name'].value.decode(),
        'type': die.attributes['DW_AT_type'].value
    }

def build_array_type(die):
    if die.offset in array_types:
        return

    array_types[die.offset] = {
        'type': die.attributes['DW_AT_type'].value,
        'sibling': die.attributes['DW_AT_sibling'].value
    }

def build_subrange_type(die):
    # don't care about things that don't have an underlying type
    if 'DW_AT_type' not in die.attributes:
        return

    # don't care about things that don't have an upper bound
    if 'DW_AT_upper_bound' not in die.attributes:
        return

    if die.offset not in subrange_types:
        subrange_types[die.offset] = {
            'type': die.attributes['DW_AT_type'].value,
            'upper_bound': die.attributes['DW_AT_upper_bound'].value
        }
    parent = die.get_parent()
    if parent.offset in array_types:
        array_types[parent.offset]['upper_bound'] = subrange_types[die.offset]['upper_bound']

def die_info_rec(die, namespace:Namespace):
    for child in die.iter_children():
        if child.tag == 'DW_TAG_structure_type':
            build_structure_type(child, namespace)
        elif child.tag == 'DW_TAG_base_type':
            build_base_type(child)
        elif child.tag == 'DW_TAG_typedef':
            build_type_def(child)
        elif child.tag == 'DW_TAG_array_type':
            build_array_type(child)
        elif child.tag == 'DW_TAG_subrange_type':
            build_subrange_type(child)
        elif child.tag == 'DW_TAG_namespace':
            namespace = namespace.add_and_return_namespace(
                child.attributes['DW_AT_name'].value.decode()
            )
            # inject ".namespace" attribute on all children
            for cchild in child.iter_children():
                cchild.namespace = \
                    getattr(child, 'namespace', '') + '::' +\
                        child.attributes['DW_AT_name'].value.decode()

        die_info_rec(child, namespace)

def resolveMember(member):
    type_offset = member.type_offset

    if type_offset in array_types:
        type_offset = array_types[type_offset]['type']

    while type_offset in type_defs:
        type_offset = type_defs[type_offset]['type']

    return type_offset

def resolveStructure(structure):
    for member in structure.members.values():
        type_offset = member.type_offset
        resolved_type = resolveMember(member)
        if resolved_type in base_types:
            if member.bit_size is None:
                member.byte_size = base_types[resolved_type]['size']
            member.type_str = base_types[resolved_type]['name']
        elif resolved_type in structures:
            if member.bit_size is None:
                member.byte_size = structures[resolved_type]['size']
            member.type_str = structures[resolved_type]['name']

        if type_offset in array_types:
            member.upper_bound = array_types[type_offset]['upper_bound']
            member.type_str = 'array of ' + member.type_str
            member.byte_size = (member.upper_bound + 1) * member.byte_size
            if member.bit_size is not None:
                member.bit_size = None

def resolveNamespace(namespace):

    for structure in namespace.structures.values():
        resolveStructure(structure)

    for n in namespace.namespaces.values():
        resolveNamespace(n)
