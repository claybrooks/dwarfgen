import json
from elftools.elf.elffile import ELFFile

from .namespace import  Namespace
from .structure import Structure
from .member import Member


class FlatStructure:
    def __init__(self):
        self.structures = {}
        self.base_types = {}
        self.array_types = {}
        self.subrange_types = {}
        self.type_defs = {}


def wrap_die(die):

    setattr(die, "has_artificial",  lambda x=die: 'DW_AT_artificial' in x.attributes)
    setattr(die, "artificial",      lambda x=die: x.attributes['DW_AT_artificial'].value)
    setattr(die, "is_artificial",   lambda x=die: x.has_artificial() and x.artificial() == 1)

    setattr(die, "has_byte_size",   lambda x=die: 'DW_AT_byte_size' in x.attributes)
    setattr(die, "has_name",        lambda x=die: 'DW_AT_name' in x.attributes)
    setattr(die, "has_type",        lambda x=die: 'DW_AT_type' in x.attributes)
    setattr(die, "has_bit_size",    lambda x=die: 'DW_AT_bit_size' in x.attributes)
    setattr(die, "has_bit_offset",  lambda x=die: 'DW_AT_bit_offset' in x.attributes)
    setattr(die, "has_upper_bound", lambda x=die: 'DW_AT_upper_bound' in x.attributes)
    setattr(die, "has_namespace",   lambda x=die: hasattr(x, 'namespace'))

    setattr(die, "byte_size",       lambda x=die: x.attributes['DW_AT_byte_size'].value)
    setattr(die, "encoding",        lambda x=die: x.attributes['DW_AT_encoding'].value)
    setattr(die, "name",            lambda x=die: x.attributes['DW_AT_name'].value.decode())
    setattr(die, "member_location", lambda x=die: x.attributes['DW_AT_data_member_location'].value)
    setattr(die, "type",            lambda x=die: x.attributes['DW_AT_type'].value)
    setattr(die, "bit_size",        lambda x=die: x.attributes['DW_AT_bit_size'].value)
    setattr(die, "bit_offset",      lambda x=die: x.attributes['DW_AT_bit_offset'].value)
    setattr(die, "sibling",         lambda x=die: x.attributes['DW_AT_sibling'].value)
    setattr(die, "upper_bound",     lambda x=die: x.attributes['DW_AT_upper_bound'].value)


FLAT = None


def process(files):
    global FLAT

    namespace = Namespace('')

    for file in files:
        with open(file, 'rb') as f:
            elffile = ELFFile(f)

            if not elffile.has_dwarf_info():
                print('file has no DWARF info, compile with \'-g\'')
                return

            # get_dwarf_info returns a DWARFInfo context object, which is the
            # starting point for all DWARF-based processing in pyelftools.
            dwarfinfo = elffile.get_dwarf_info()

        FLAT = FlatStructure()

        for CU in dwarfinfo.iter_CUs():
            top_DIE = CU.get_top_DIE()
            die_info_rec(top_DIE, namespace)

        resolveNamespace(namespace)

    return namespace


def build_base_type(die):
    if die.offset in FLAT.base_types:
        return

    FLAT.base_types[die.offset] = {
        'size': die.byte_size(),
        'encoding': die.encoding(),
        'name': die.name()
    }


def build_structure_type(die, namespace):
    if die.offset in FLAT.structures:
        return

    # we don't care about non-named things
    if not die.has_name():
        return

    # we don't care about things that don't have a size
    if not die.has_byte_size():
        return

    if die.is_artificial():
        return

    structure = namespace.add_and_return_structure(die.name(), die.byte_size())

    if die.has_namespace():
        name = die.namespace + '::' + die.name()
    else:
        name = '::' + die.name()

    FLAT.structures[die.offset] = {
        'name': die.name(),
        'size': die.byte_size(),
        'members': {}
    }
    members = FLAT.structures[die.offset]['members']

    for child in die.iter_children():
        wrap_die(child)
        if child.tag == 'DW_TAG_member':

            _member = structure.add_and_return_member(
                child.name(), child.type(), child.member_location()
            )

            members[name] = {}
            member = members[name]

            member['name'] = child.name()
            member['byteOffset'] = child.member_location()
            member['typeOffset'] = child.type()

            if child.has_bit_size():
                value = child.bit_size()
                member['DW_AT_bit_size'] = value
                _member.bit_size = value

            if child.has_bit_offset():
                value = child.bit_offset()
                member['DW_AT_bit_offset'] = value
                _member.bit_offset = value

        elif child.tag == 'DW_AT_structure':
            members[name] = child.type()


def build_type_def(die):
    if die.offset in FLAT.type_defs:
        return

    # ignore typedefs with no type
    if not die.has_type():
        return

    FLAT.type_defs[die.offset] = {
        'name': die.name(),
        'type': die.type()
    }


def build_array_type(die):
    if die.offset in FLAT.array_types:
        return

    FLAT.array_types[die.offset] = {
        'type': die.type(),
        'sibling': die.sibling()
    }


def build_subrange_type(die):
    # don't care about things that don't have an underlying type
    if not die.has_type():
        return

    # don't care about things that don't have an upper bound
    if not die.has_upper_bound:
        return

    if die.offset not in FLAT.subrange_types:
        FLAT.subrange_types[die.offset] = {
            'type': die.type(),
            'upper_bound': die.upper_bound
        }
    parent = die.get_parent()
    if parent.offset in FLAT.array_types:
        FLAT.array_types[parent.offset]['upper_bound'] = FLAT.subrange_types[die.offset]['upper_bound']


def die_info_rec(die, namespace:Namespace):
    for child in die.iter_children():
        wrap_die(child)

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
            namespace = namespace.add_and_return_namespace(child.name())

            # inject ".namespace" attribute on all children
            for cchild in child.iter_children():
                curr_ns = getattr(child, 'namespace', None)
                if curr_ns is None:
                    cchild.namespace = child.name()
                else:
                    cchild.namespace = curr_ns + '::' + child.name()

        die_info_rec(child, namespace)


def resolveMember(member):
    type_offset = member.type_offset

    if type_offset in FLAT.array_types:
        type_offset = FLAT.array_types[type_offset]['type']

    while type_offset in FLAT.type_defs:
        type_offset = FLAT.type_defs[type_offset]['type']

    return type_offset


def resolveStructure(structure):
    for member in structure.members.values():
        type_offset = member.type_offset
        resolved_type = resolveMember(member)
        if resolved_type in FLAT.base_types:
            if member.bit_size is None:
                member.byte_size = FLAT.base_types[resolved_type]['size']
            member.type_str = FLAT.base_types[resolved_type]['name']
        elif resolved_type in FLAT.structures:
            if member.bit_size is None:
                member.byte_size = FLAT.structures[resolved_type]['size']
            member.type_str = FLAT.structures[resolved_type]['name']

        if type_offset in FLAT.array_types:
            member.upper_bound = FLAT.array_types[type_offset]['upper_bound']
            member.type_str = 'array of ' + member.type_str
            member.byte_size = (member.upper_bound + 1) * member.byte_size
            if member.bit_size is not None:
                member.bit_size = None


def resolveNamespace(namespace):

    for structure in namespace.structures.values():
        resolveStructure(structure)

    for n in namespace.namespaces.values():
        resolveNamespace(n)
