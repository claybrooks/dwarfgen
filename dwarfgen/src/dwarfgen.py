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


ACCESSIBILITY = {
    1: "public",
    2: "protected",
    3: "private"
}

def v2_accessibility_policy(die):

    if not die.has_accessibility():
        return 'public'

    return ACCESSIBILITY[die.accessibility()]

def v2_inheritance_accessibility_policy(die):

    if not die.has_accessibility():
        return 'private'

    return ACCESSIBILITY[die.accessibility()]

def default_accessibility_policy(die):

    if not die.has_accessibility():
        parent = die.get_parent()
        if parent.is_structure_type():
            return 'public'
        elif parent.is_class_type():
            return "private"
        else:
            raise ValueError("Unknown Default Accessibility for {}".format(parent))

    return ACCESSIBILITY[die.accessibility()]

def default_valid_structure_policy(die):
    return die.has_name() and die.has_byte_size() and not die.is_artificial()

def default_valid_typedef_policy(die):
    return die.has_type() and die.has_name()

def default_typedef_data_policy(die):
    return {
        'name': die.name(),
        'type': die.type()
    }

def default_valid_array_policy(die):
    return die.has_sibling()

def default_valid_subrange_policy(die):
    return die.has_type() and die.has_upper_bound()

def default_valid_basetype_policy(die):
    return die.has_byte_size() and die.has_encoding() and die.has_name()

def default_valid_static_structure_member_policy(die):
    return VALID_STRUCTURE_MEMBER_POLICY(die) and die.has_external()

def default_valid_instance_structure_member_policy(die):
    return VALID_STRUCTURE_MEMBER_POLICY(die) and die.has_data_member_location()

def default_valid_structure_member_policy(die):
    return die.has_name() and die.has_type()

def default_structure_member_data_policy(die):
    return {
        'name': die.name(),
        'typeOffset': die.type()
    }

def default_static_structure_member_data_policy(die, _member):
    _member.is_static = True
    return STRUCTURE_MEMBER_DATA_POLICY(die)

def default_instance_structure_member_data_policy(die, _member):
    ret = STRUCTURE_MEMBER_DATA_POLICY(die)

    ret.update({"byteOffset": die.data_member_location()})
    _member.byte_offset = die.data_member_location()

    if die.has_bit_size():
        ret.update({'DW_AT_bit_size': die.bit_size()})
        _member.bit_size = die.bit_size()
    if die.has_bit_offset():
        ret.update({'DW_AT_bit_offset':  die.bit_offset()})
        _member.bit_offset = die.bit_offset()

    return ret

def default_array_data_policy(die):
    return {
        'type': die.type(),
        'sibling': die.sibling()
    }

def default_basetype_data_policy(die):

    return {
        'size': die.byte_size(),
        'encoding': die.encoding(),
        'name': die.name()
    }

def default_subrange_data_policy(die):
    return {
        'type': die.type(),
        'lower_bound': SUBRANGE_LOWERBOUND_POLICY(die),
        'upper_bound': die.upper_bound(),
    }

def default_structure_data_policy(die):
    return {
        'name': NAME_POLICY(die),
        'size': die.byte_size(),
        'members': {}
    }

def zero_indexed_subrange_lowerbound_policy(die):
    return die.lower_bound() if die.has_lower_bound() else 0

def one_indexed_subrange_lowerbound_policy(die):
    return die.lower_bound() if die.has_lower_bound() else 1

def default_name_policy(die):

    if die.has_namespace():
        return die.namespace + '::' + die.name()
    else:
        return die.name()

def default_subrange_data_for_array_parent_policy(die, flat):
    parent = die.get_parent()
    if parent and parent.offset in flat.array_types:
        flat.array_types[parent.offset]['upper_bound'] = flat.subrange_types[die.offset]['upper_bound']
        flat.array_types[parent.offset]['lower_bound'] = flat.subrange_types[die.offset]['lower_bound']

def default_namespace_application_policy(namespace, die):
    new_namespace = namespace.create_namespace(die.name())

    # inject ".namespace" attribute on all children
    for child in die.iter_children():
        curr_ns = getattr(die, 'namespace', None)
        if curr_ns is None:
            child.namespace = die.name()
        else:
            child.namespace = curr_ns + '::' + die.name()

    return new_namespace

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
DETECTED_VERSION = None

# policies
def apply_default_policies():
    global VALID_STRUCTURE_POLICY
    global VALID_TYPEDEF_POLICY
    global VALID_ARRAY_POLICY
    global VALID_SUBRANGE_POLICY
    global VALID_BASETYPE_POLICY
    global VALID_STRUCTURE_MEMBER_POLICY
    global VALID_STATIC_STRUCTURE_MEMBER_POLICY
    global VALID_INSTANCE_STRUCTURE_MEMBER_POLICY
    global TYPEDEF_DATA_POLICY
    global ARRAY_DATA_POLICY
    global BASETYPE_DATA_POLICY
    global SUBRANGE_DATA_POLICY
    global STRUCTURE_DATA_POLICY
    global STRUCTURE_MEMBER_DATA_POLICY
    global STATIC_STRUCTURE_MEMBER_DATA_POLICY
    global INSTANCE_STRUCTURE_MEMBER_DATA_POLICY
    global SUBRANGE_LOWERBOUND_POLICY
    global SUBRANGE_DATA_FOR_ARRAY_PARENT_POLICY
    global NAMESPACE_APPLICATION_POLICY
    global ACCESSIBILITY_POLICY
    global INHERITANCE_ACCESSIBILITY_POLICY
    global NAME_POLICY

    VALID_STRUCTURE_POLICY = default_valid_structure_policy
    VALID_TYPEDEF_POLICY = default_valid_typedef_policy
    VALID_ARRAY_POLICY = default_valid_array_policy
    VALID_SUBRANGE_POLICY = default_valid_subrange_policy
    VALID_BASETYPE_POLICY = default_valid_basetype_policy
    VALID_STRUCTURE_MEMBER_POLICY = default_valid_structure_member_policy
    VALID_STATIC_STRUCTURE_MEMBER_POLICY = default_valid_static_structure_member_policy
    VALID_INSTANCE_STRUCTURE_MEMBER_POLICY = default_valid_instance_structure_member_policy

    TYPEDEF_DATA_POLICY = default_typedef_data_policy
    ARRAY_DATA_POLICY = default_array_data_policy
    BASETYPE_DATA_POLICY = default_basetype_data_policy
    SUBRANGE_DATA_POLICY = default_subrange_data_policy
    STRUCTURE_DATA_POLICY = default_structure_data_policy
    STRUCTURE_MEMBER_DATA_POLICY = default_structure_member_data_policy
    STATIC_STRUCTURE_MEMBER_DATA_POLICY = default_static_structure_member_data_policy
    INSTANCE_STRUCTURE_MEMBER_DATA_POLICY = default_instance_structure_member_data_policy

    SUBRANGE_LOWERBOUND_POLICY = zero_indexed_subrange_lowerbound_policy
    SUBRANGE_DATA_FOR_ARRAY_PARENT_POLICY = default_subrange_data_for_array_parent_policy

    NAMESPACE_APPLICATION_POLICY = default_namespace_application_policy

    ACCESSIBILITY_POLICY = default_accessibility_policy
    INHERITANCE_ACCESSIBILITY_POLICY = default_accessibility_policy

    NAME_POLICY = default_name_policy


def apply_policies(version, language):
    apply_default_policies()

    global ACCESSIBILITY_POLICY
    global SUBRANGE_LOWERBOUND_POLICY
    global INHERITANCE_ACCESSIBILITY_POLICY

    if version == 2:
        ACCESSIBILITY_POLICY = v2_accessibility_policy
        INHERITANCE_ACCESSIBILITY_POLICY = v2_inheritance_accessibility_policy

    if language == 'ADA':
        SUBRANGE_LOWERBOUND_POLICY = one_indexed_subrange_lowerbound_policy


def process(files):
    global FLAT
    global DETECTED_LANGUAGE
    global DETECTED_VERSION

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

            apply_policies(CU.header.version, DETECTED_LANGUAGE)

            die_info_rec(top_DIE, namespace)


        # Ada does not use DW_TAG_namespace like C++, so namespace inference comes from DW_AT_name of types
        # This function moves structures around and creates namespaces to make it look identical to what c++
        # processing would produce prior to calling "resolve_namespace".
        if DETECTED_LANGUAGE == 'ADA':
            ada_disperse_structures(namespace)

        resolve_namespace(namespace)

    return namespace


def build_base_type(die):
    if not VALID_BASETYPE_POLICY(die):
        return

    FLAT.base_types[die.offset] = BASETYPE_DATA_POLICY(die)


def build_structure_child(structure, members, die):
    wrap_die(die)

    if die.is_template_type_param():
        #TODO implement some sort of template parameters
        pass
    elif die.is_inheritance():
        structure.add_base_structure(die.type(), INHERITANCE_ACCESSIBILITY_POLICY(die), die.data_member_location())
    elif die.is_member():
        if not VALID_STRUCTURE_MEMBER_POLICY(die):
            return

        _member = structure.create_member(
            die.name(), die.type()
        )
        _member.accessibility = ACCESSIBILITY_POLICY(die)

        if VALID_STATIC_STRUCTURE_MEMBER_POLICY(die):
            return STATIC_STRUCTURE_MEMBER_DATA_POLICY(die, _member)
        elif VALID_INSTANCE_STRUCTURE_MEMBER_POLICY(die):
            return INSTANCE_STRUCTURE_MEMBER_DATA_POLICY(die, _member)
    elif die.is_subrange_type():
        build_subrange_type(die)
    elif die.is_structure_type():
        #members[parent_name] = die.type()
        pass

def build_structure_type(die, namespace):

    # invalid structure
    if not VALID_STRUCTURE_POLICY(die):
        return

    structure = namespace.create_structure(die.name(), die.byte_size())

    FLAT.structures[die.offset] = STRUCTURE_DATA_POLICY(die)
    members = FLAT.structures[die.offset]['members']

    for child in die.iter_children():
        build_structure_child(structure, members, child)

def build_type_def(die):
    if not VALID_TYPEDEF_POLICY(die):
        return

    FLAT.type_defs[die.offset] = TYPEDEF_DATA_POLICY(die)

def build_array_type(die):
    if not VALID_ARRAY_POLICY(die):
        return

    FLAT.array_types[die.offset] = ARRAY_DATA_POLICY(die)

def build_subrange_type(die):
    if not VALID_SUBRANGE_POLICY(die):
        return

    FLAT.subrange_types[die.offset] = SUBRANGE_DATA_POLICY(die)
    SUBRANGE_DATA_FOR_ARRAY_PARENT_POLICY(die, FLAT)

def die_info_rec(die, namespace:Namespace):
    for child in die.iter_children():
        wrap_die(child)

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
            new_namespace = NAMESPACE_APPLICATION_POLICY(namespace, child)
            die_info_rec(child, new_namespace)

        if not child.is_namespace():
            die_info_rec(child, namespace)


def resolve_type_offset(type_offset, flat):
    if type_offset in flat.array_types:
        type_offset = flat.array_types[type_offset]['type']

    if type_offset in flat.subrange_types:
        type_offset = flat.subrange_types[type_offset]['type']

    while type_offset in flat.type_defs:
        type_offset = flat.type_defs[type_offset]['type']

    return type_offset

def resolve_type(type_offset, flat):
    if type_offset in FLAT.base_types:
        return FLAT.base_types[type_offset]
    elif type_offset in FLAT.structures:
        return FLAT.structures[type_offset]
    return None

def resolve_type_offset_name(type_offset, flat):
    return resolve_type(type_offset, flat)['name']

def resolve_type_offset_size(type_offset, flat):
    return resolve_type(type_offset, flat)['size']

def resolve_structure(structure):

    for base_structure in structure.base_structures.values():
        resolved_type = resolve_type_offset(base_structure.type_offset, FLAT)
        base_structure.type = resolve_type_offset_name(resolved_type, FLAT)

    for member in structure.members.values():
        type_offset = member.type_offset
        resolved_type = resolve_type_offset(type_offset, FLAT)

        member.type_str = resolve_type_offset_name(resolved_type, FLAT)
        if member.bit_size is None:
            member.byte_size = resolve_type_offset_size(resolved_type, FLAT)

        if type_offset in FLAT.array_types:
            member.upper_bound = FLAT.array_types[type_offset]['upper_bound']
            member.lower_bound = FLAT.array_types[type_offset]['lower_bound']

            member.type_str = 'array of ' + member.type_str
            member.byte_size = (member.upper_bound - member.lower_bound + 1) * member.byte_size
            if member.bit_size is not None:
                member.bit_size = None

        if type_offset in FLAT.subrange_types:
            member.max_val = FLAT.subrange_types[type_offset]['upper_bound']
            member.min_val = FLAT.subrange_types[type_offset]['lower_bound']

def ada_disperse_structures(namespace):
    move_structures = []
    for structure in namespace.structures.values():
        tokens = structure.name.split('__')
        name = tokens[-1]
        namespaces = tokens[:-1]

        # add namespaces
        ns = namespace
        for n in namespaces:
            ns = ns.create_namespace(n)

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

