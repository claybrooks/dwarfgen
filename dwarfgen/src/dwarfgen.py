import json
import logging
from elftools.elf.elffile import ELFFile

from .namespace import  Namespace
from .structure import Structure
from .member import Member


DEFAULT_LOWER_BOUND = {
    'C++': 0,
    'ADA': 1,
}

class FlatStructure:
    def __init__(self):
        self.structures = {}
        self.base_types = {}
        self.array_types = {}
        self.subrange_types = {}
        self.type_defs = {}


def data_member_location(val):
    if isinstance(val, list):
        return val[1]
    return val


def wrap_die(die):

    # 'DW_AT_*'
    attributes = [
        "byte_size",
        "encoding",
        "data_member_location",
        "type",
        "bit_size",
        "bit_offset",
        "sibling",
        "upper_bound",
        "lower_bound",
        "artificial",
        "accessibility",
        "external",
    ]

    for attr in attributes:
        setattr(die, 'has_'+attr,   lambda x=die, a=attr: 'DW_AT_'+a in x.attributes)
        setattr(die, attr,          lambda x=die, a=attr: data_member_location(x.attributes['DW_AT_'+a].value))

    # 'DW_AT_*' but also decode .value
    decode_attributes = [
        'producer',
        'name'
    ]

    for attr in decode_attributes:
        setattr(die, 'has_'+attr,   lambda x=die, a=attr: 'DW_AT_'+a in x.attributes)
        setattr(die, attr,          lambda x=die, a=attr: x.attributes['DW_AT_'+a].value.decode())

    # 'DW_TAG_*'
    tag_types = [
        'structure_type',
        'class_type',
        'member',
        'base_type',
        'typedef',
        'sibling',
        'array_type',
        'subrange_type',
        'namespace',
        'variable',
        "template_type_param",
        "inheritance",
    ]

    for tag_type in tag_types:
        setattr(die, 'is_'+tag_type, lambda x=die, tag=tag_type: x.tag == 'DW_TAG_'+tag)

    # add a special one for artificial
    setattr(die, "is_artificial",   lambda x=die: x.has_artificial() and x.artificial() == 1)

    # add a special one for lower_bound, the default depends on the language
    setattr(
        die,
        "lower_bound",
        lambda x=die: x.attributes['DW_AT_lower_bound'].value if x.has_lower_bound() else DEFAULT_LOWER_BOUND[DETECTED_LANGUAGE]
    )

    # add a special one for namespace
    setattr(die, "has_namespace",   lambda x=die: hasattr(x, 'namespace'))

    # add a single member function to check all structure like types
    setattr(die, 'is_structure_like', lambda x=die: x.is_structure_type() or x.is_class_type())

FLAT = None
DETECTED_LANGUAGE = None

def process(files):
    global FLAT
    global DETECTED_LANGUAGE

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
            wrap_die(top_DIE)

            producer = top_DIE.producer()
            if 'C++' in producer:
                DETECTED_LANGUAGE = 'C++'
            elif 'Ada' in producer:
                DETECTED_LANGUAGE = 'ADA'
            else:
                logging.error('Unkown Language from producer {}'.format(producer))
                continue

            die_info_rec(top_DIE, namespace)


        # Ada does not use DW_TAG_namespace like C++, so namespace inference comes from DW_AT_name of types
        # This function moves structures around and creates namespaces to make it look identical to what c++
        # processing would produce prior to calling "resolve_namespace".
        if DETECTED_LANGUAGE == 'ADA':
            ada_disperse_structures(namespace)

        resolve_namespace(namespace)

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
        name = die.name()

    FLAT.structures[die.offset] = {
        'name': name,
        'size': die.byte_size(),
        'members': {}
    }
    members = FLAT.structures[die.offset]['members']

    for child in die.iter_children():
        wrap_die(child)
        if child.is_template_type_param():
            #TODO implement some sort of template parameters
            pass
        elif child.is_inheritance():
            #TODO implement some sort of inheritance
            pass
        elif child.is_member():

            _member = structure.add_and_return_member(
                child.name(), child.type()
            )

            if child.has_accessibility():
                _member.accessibility = child.accessibility()
                if _member.accessibility == 1:
                    _member.accessibility = "public"
                elif _member.accessibility == 2:
                    _member.accessibility = "protected"
                else:
                    _member.accessibility = "private"
            else:
                if die.is_structure_type():
                    _member.accessibility = "public"
                else:
                    _member.accessibility = "private"

            members[name] = {}
            member = members[name]

            # based on dwarf spec, if a member of structure is "external", then it's a static member of that class/struct
            if child.has_external():
                _member.is_static = True
            else:
                _member.byte_offset = child.data_member_location()
                member['byteOffset'] = child.data_member_location()

            member['name'] = child.name()
            member['typeOffset'] = child.type()

            if child.has_bit_size():
                value = child.bit_size()
                member['DW_AT_bit_size'] = value
                _member.bit_size = value

            if child.has_bit_offset():
                value = child.bit_offset()
                member['DW_AT_bit_offset'] = value
                _member.bit_offset = value

        elif child.is_structure_type():
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
            'lower_bound': die.lower_bound(),
            'upper_bound': die.upper_bound(),
        }

    parent = die.get_parent()
    if parent.offset in FLAT.array_types:
        FLAT.array_types[parent.offset]['upper_bound'] = FLAT.subrange_types[die.offset]['upper_bound']
        FLAT.array_types[parent.offset]['lower_bound'] = FLAT.subrange_types[die.offset]['lower_bound']


def die_info_rec(die, namespace:Namespace):
    for child in die.iter_children():
        wrap_die(child)

        # we need to do special name processing for ada types because DW_TAG_namespace is not used.  Namespace can
        # be inferred from names
        '''
        if DETECTED_LANGUAGE == 'ADA' and child.has_name():
            if '__' in child.name():
                tokens = child.name().split('__')
                name = tokens[-1]
                namespace = tokens[:-1]

                new_namespace = namespace
                for ns in namespace:
                    new_namespace = new_namespace.add_and_return_namespace(ns)
        '''

        if child.is_structure_like():
            build_structure_type(child, namespace)
        elif child.is_base_type():
            build_base_type(child)
        elif child.is_typedef():
            build_type_def(child)
        elif child.is_array_type():
            build_array_type(child)
        elif child.is_subrange_type():
            build_subrange_type(child)
        elif child.is_namespace():
            new_namespace = namespace.add_and_return_namespace(child.name())

            # inject ".namespace" attribute on all children
            for cchild in child.iter_children():
                curr_ns = getattr(child, 'namespace', None)
                if curr_ns is None:
                    cchild.namespace = child.name()
                else:
                    cchild.namespace = curr_ns + '::' + child.name()

            die_info_rec(child, new_namespace)

        if not child.is_namespace():
            die_info_rec(child, namespace)


def resolveMember(member):
    type_offset = member.type_offset

    if type_offset in FLAT.array_types:
        type_offset = FLAT.array_types[type_offset]['type']

    while type_offset in FLAT.type_defs:
        type_offset = FLAT.type_defs[type_offset]['type']

    return type_offset


def resolve_structure(structure):
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
            member.lower_bound = FLAT.array_types[type_offset]['lower_bound']

            member.type_str = 'array of ' + member.type_str
            member.byte_size = (member.upper_bound - member.lower_bound + 1) * member.byte_size
            if member.bit_size is not None:
                member.bit_size = None

def ada_disperse_structures(namespace):
    move_structures = []
    for structure in namespace.structures.values():
        tokens = structure.name.split('__')
        name = tokens[-1]
        namespaces = tokens[:-1]

        # add namespaces
        ns = namespace
        for n in namespaces:
            ns = ns.add_and_return_namespace(n)

        # we need to move this structure to the lower namespace
        move_structures.append((name, namespaces))

    for move in move_structures:
        name, namespaces = move
        name_key = '__'.join(namespaces) + '__' + name
        struct = namespace.structures.pop(name_key)

        ns = namespace
        for n in namespaces:
            ns = namespace.namespaces[n]

        ns.structures[name] = struct


def resolve_namespace(namespace):

    for structure in namespace.structures.values():
        resolve_structure(structure)

    for n in namespace.namespaces.values():
        resolve_namespace(n)

