import json
import logging
from elftools.elf.elffile import ELFFile

from .namespace import  Namespace
from .structure import Structure
from .member import Member


DEFAULT_LOWER_BOUND = {
    0x01: 0,
    0x02: 0,
    0x03: 1,
    0x04: 0,
    0x05: 1,
    0x06: 1,
    0x07: 1,
    0x08: 1,
    0x09: 1,
    0x0a: 1,
    0x0b: 0,
    0x0c: 0,
    0x0d: 1,
    0x0e: 1,
    0x0f: 1,
    0x10: 0,
    0x11: 0,
    0x12: 0,
    0x13: 0,
    0x14: 0,
}

LANG_CODES = {
    0x01: "C",
    0x02: "C",
    0x03: "ADA",
    0x04: "C++",
    0x05: "COBOL",
    0x06: "COBOL",
    0x07: "FORTRAN",
    0x08: "FORTRAN",
    0x09: "PASCAL",
    0x0a: "MODULA",
    0x0b: "JAVA",
    0x0c: "C",
    0x0d: "ADA",
    0x0e: "FORTRAN",
    0x0f: "PLI",
    0x10: "OBJ_C",
    0x11: "OBJ_C++",
    0x12: "UPC",
    0x13: "D",
    0x14: "PYTHON",
}

class FlatStructure:
    def __init__(self):
        self.structures = {}
        self.enumerations = {}
        self.unions = {}
        self.base_types = {}
        self.string_types = {}
        self.array_types = {}
        self.subrange_types = {}
        self.type_defs = {}
        self.pointer_types = {}
        self.ignored_types = {}
        self.const_types = {}

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

def ada_v2_inheritance_accessibility_policy(die):

    if not die.has_accessibility():
        return 'public'

    return ACCESSIBILITY[die.accessibility()]

def default_accessibility_policy(die):

    if not die.has_accessibility():
        parent = die.get_parent()
        if parent.is_structure_type():
            return 'public'
        elif parent.is_class_type():
            return "private"
        elif parent.is_union_type():
            return "public"
        else:
            raise ValueError("Unknown Default Accessibility for {}".format(parent))

    return ACCESSIBILITY[die.accessibility()]

def default_structure_data_policy(die):
    size = 0
    if die.has_byte_size():
        size = die.byte_size()

    return {
        'name': NAME_POLICY(die),
        'size': size,
        'members': {}
    }

def default_valid_structure_policy(die):
    return (die.has_name() or die.has_MIPS_linkage_name() or die.has_linkage_name()) and not die.is_artificial()

def default_valid_typedef_policy(die):
    return die.has_name()

def default_typedef_data_policy(die):
    return {
        'name': die.name(),
        'type': die.type() if die.has_type() else ""
    }

def default_valid_consttype_policy(die):
    return die.has_type()

def default_consttype_data_policy(die):
    return {
        "type": die.type()
    }

def default_valid_union_member_policy(die):
    return die.has_name() and die.has_type()

def default_union_member_data_policy(die):
    return {
        "name": die.name(),
        "type": die.type()
    }

def default_valid_union_policy(die):
    return die.has_byte_size()

def default_union_data_policy(die):
    return {
        "name": NO_NS_NAME_POLICY(die),
        "size": die.byte_size(),
        "members": {}
    }

def default_valid_array_policy(die):
    return die.has_sibling()

def default_valid_subrange_policy(die):
    return die.has_type() and die.has_upper_bound()

def default_valid_basetype_policy(die):
    return die.has_byte_size() and die.has_encoding() and die.has_name()

def default_valid_stringtype_policy(die):
    return die.has_byte_size()

def default_valid_enumeration_policy(die):
    return die.has_name() and die.has_byte_size() and die.has_type() and die.has_encoding()

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

def default_enumeration_data_policy(die):
    return {
        'name': die.name(),
        'encoding': die.encoding(),
        'type': die.type(),
        'size': die.byte_size(),
        'values': {}
    }

def default_valid_enumerator_policy(die):
    return die.has_name() and die.has_const_value()

def default_enumerator_data_policy(die):
    return {
        'name': die.name(),
        'value': die.const_value()
    }

def default_valid_pointertype_policy(die):
    return die.has_byte_size()

def default_pointertype_data_policy(die):
    return {
        'size': die.byte_size(),
        'type': die.type() if die.has_type() else str("void")
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

    types = [x.offset for x in die.iter_children() if wrap_die(x).is_subrange_type()]

    return {
        'type': die.type(),
        'subranges': types
    }

def default_basetype_data_policy(die):

    name = die.name()
    if '(kind' in name:
        name = name.split('(')[0]

    return {
        'size': die.byte_size(),
        'encoding': die.encoding(),
        'name': name
    }

def default_valid_stringtype_data_policy(die):
    return {
        'size': die.byte_size(),
        'name': 'string' if die.byte_size() > 1 else 'char'
    }

def default_subrange_data_policy(die):
    return {
        'type': die.type(),
        'lower_bound': SUBRANGE_LOWERBOUND_POLICY(die),
        'upper_bound': die.upper_bound(),
    }

def zero_indexed_subrange_lowerbound_policy(die):
    return die.lower_bound() if die.has_lower_bound() else 0

def one_indexed_subrange_lowerbound_policy(die):
    return die.lower_bound() if die.has_lower_bound() else 1

def default_no_ns_name_policy(die):
    name = ''
    if die.has_name():
        name = die.name()
    elif die.has_MIPS_linkage_name():
        name = die.MIPS_linkage_name()
    elif die.has_linkage_name():
        name = die.linkage_name()
    else:
        name = "UNKNOWN"

    return name

def default_name_policy(die):

    name = NO_NS_NAME_POLICY(die)

    if die.has_namespace():
        return die.namespace + '::' + name
    else:
        return name

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

def default_is_inheritance_policy(die):
    return die.is_inheritance() or \
        (DETECTED_LANGUAGE=='ADA' and die.is_member() and die.name() == '_parent')

def ada_valid_struct_policy(die):
    return default_valid_structure_policy(die) and \
        ('ada__' not in die.name())


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
        "const_value",
        "language",
    ]

    for attr in attributes:
        setattr(die, 'has_'+attr,   lambda x=die, a=attr: 'DW_AT_'+a in x.attributes)
        setattr(die, attr,          lambda x=die, a=attr: data_member_location(x.attributes['DW_AT_'+a].value))

    # 'DW_AT_*' but also decode .value
    decode_attributes = [
        'producer',
        'name',
        "MIPS_linkage_name",
        "linkage_name"
    ]

    for attr in decode_attributes:
        setattr(die, 'has_'+attr,   lambda x=die, a=attr: 'DW_AT_'+a in x.attributes)
        setattr(die, attr,          lambda x=die, a=attr: x.attributes['DW_AT_'+a].value.decode())

    # 'DW_TAG_*'
    tag_types = [
        'structure_type',
        'class_type',
        "union_type",
        'member',
        'base_type',
        'string_type',
        'typedef',
        'sibling',
        'array_type',
        'subrange_type',
        'namespace',
        'variable',
        "template_type_param",
        "inheritance",
        "pointer_type",
        "enumeration_type",
        "enumerator",
        "const_type"
    ]

    for tag_type in tag_types:
        setattr(die, 'is_'+tag_type, lambda x=die, tag=tag_type: x.tag == 'DW_TAG_'+tag)

    # add a special one for artificial
    setattr(die, "is_artificial",   lambda x=die: x.has_artificial() and x.artificial() == 1)

    # add a special one for lower_bound, the default depends on the language
    setattr(
        die,
        "lower_bound",
        lambda x=die: x.attributes['DW_AT_lower_bound'].value if x.has_lower_bound() else DETECTED_DEFAULT_LOWER_BOUND
    )

    # add a special one for namespace
    setattr(die, "has_namespace",   lambda x=die: hasattr(x, 'namespace'))

    # add a single member function to check all structure like types
    setattr(die, 'is_structure_like', lambda x=die: x.is_structure_type() or x.is_class_type())

    return die


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
    global VALID_STRINGTYPE_POLICY
    global VALID_STRUCTURE_MEMBER_POLICY
    global VALID_STATIC_STRUCTURE_MEMBER_POLICY
    global VALID_INSTANCE_STRUCTURE_MEMBER_POLICY
    global VALID_POINTERTYPE_POLICY
    global VALID_ENUMERATION_POLICY
    global VALID_ENUMERATOR_POLICY
    global TYPEDEF_DATA_POLICY
    global ARRAY_DATA_POLICY
    global BASETYPE_DATA_POLICY
    global STRINGTYPE_DATA_POLICY
    global SUBRANGE_DATA_POLICY
    global STRUCTURE_DATA_POLICY
    global STRUCTURE_MEMBER_DATA_POLICY
    global STATIC_STRUCTURE_MEMBER_DATA_POLICY
    global INSTANCE_STRUCTURE_MEMBER_DATA_POLICY
    global POINTERTYPE_DATA_POLICY
    global SUBRANGE_LOWERBOUND_POLICY
    global SUBRANGE_DATA_FOR_ARRAY_PARENT_POLICY
    global ENUMERATION_DATA_POLICY
    global ENUMERATOR_DATA_POLICY
    global NAMESPACE_APPLICATION_POLICY
    global ACCESSIBILITY_POLICY
    global INHERITANCE_ACCESSIBILITY_POLICY
    global IS_INHERITANCE_POLICY
    global NAME_POLICY
    global VALID_CONSTTYPE_POLICY
    global CONSTTYPE_DATA_POLICY
    global VALID_UNION_POLICY
    global UNION_DATA_POLICY
    global VALID_UNION_MEMBER_POLICY
    global UNION_MEMBER_DATA_POLICY
    global NO_NS_NAME_POLICY

    VALID_STRUCTURE_POLICY = default_valid_structure_policy
    VALID_TYPEDEF_POLICY = default_valid_typedef_policy
    VALID_ARRAY_POLICY = default_valid_array_policy
    VALID_SUBRANGE_POLICY = default_valid_subrange_policy
    VALID_BASETYPE_POLICY = default_valid_basetype_policy
    VALID_STRINGTYPE_POLICY = default_valid_stringtype_policy
    VALID_STRUCTURE_MEMBER_POLICY = default_valid_structure_member_policy
    VALID_STATIC_STRUCTURE_MEMBER_POLICY = default_valid_static_structure_member_policy
    VALID_INSTANCE_STRUCTURE_MEMBER_POLICY = default_valid_instance_structure_member_policy
    VALID_POINTERTYPE_POLICY = default_valid_pointertype_policy
    VALID_ENUMERATION_POLICY = default_valid_enumeration_policy
    VALID_ENUMERATOR_POLICY = default_valid_enumerator_policy
    VALID_CONSTTYPE_POLICY = default_valid_consttype_policy
    VALID_UNION_POLICY = default_valid_union_policy
    VALID_UNION_MEMBER_POLICY = default_valid_union_member_policy

    UNION_MEMBER_DATA_POLICY = default_union_member_data_policy
    UNION_DATA_POLICY = default_union_data_policy
    CONSTTYPE_DATA_POLICY = default_consttype_data_policy
    TYPEDEF_DATA_POLICY = default_typedef_data_policy
    ARRAY_DATA_POLICY = default_array_data_policy
    BASETYPE_DATA_POLICY = default_basetype_data_policy
    STRINGTYPE_DATA_POLICY = default_valid_stringtype_data_policy
    SUBRANGE_DATA_POLICY = default_subrange_data_policy
    STRUCTURE_DATA_POLICY = default_structure_data_policy
    STRUCTURE_MEMBER_DATA_POLICY = default_structure_member_data_policy
    STATIC_STRUCTURE_MEMBER_DATA_POLICY = default_static_structure_member_data_policy
    INSTANCE_STRUCTURE_MEMBER_DATA_POLICY = default_instance_structure_member_data_policy
    POINTERTYPE_DATA_POLICY = default_pointertype_data_policy
    ENUMERATION_DATA_POLICY = default_enumeration_data_policy
    ENUMERATOR_DATA_POLICY = default_enumerator_data_policy

    SUBRANGE_LOWERBOUND_POLICY = zero_indexed_subrange_lowerbound_policy
    SUBRANGE_DATA_FOR_ARRAY_PARENT_POLICY = default_subrange_data_for_array_parent_policy

    NAMESPACE_APPLICATION_POLICY = default_namespace_application_policy

    ACCESSIBILITY_POLICY = default_accessibility_policy
    INHERITANCE_ACCESSIBILITY_POLICY = default_accessibility_policy
    IS_INHERITANCE_POLICY = default_is_inheritance_policy

    NO_NS_NAME_POLICY = default_no_ns_name_policy
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
        if version == 2:
            INHERITANCE_ACCESSIBILITY_POLICY = ada_v2_inheritance_accessibility_policy

        VALID_STRUCTURE_POLICY = ada_valid_struct_policy

    if language == 'ADA' or language == 'FORTRAN':
        SUBRANGE_LOWERBOUND_POLICY = one_indexed_subrange_lowerbound_policy


def process(files):
    global FLAT
    global DETECTED_LANGUAGE
    global DETECTED_DEFAULT_LOWER_BOUND
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

            language = top_DIE.language()

            if language not in LANG_CODES:
                logging.error('Unkown Language from producer {}'.format(language))
                continue
            else:
                DETECTED_LANGUAGE = LANG_CODES[language]
                DETECTED_DEFAULT_LOWER_BOUND = DEFAULT_LOWER_BOUND[language]
                logging.info("Detected Language " + DETECTED_LANGUAGE)

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

def build_structure_child(structure, die, namespace):
    wrap_die(die)

    if die.is_template_type_param():
        #TODO implement some sort of template parameters
        pass
    elif IS_INHERITANCE_POLICY(die):
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
    elif die.is_union_type():
        build_union_type(die, namespace)

def build_structure_type(die, namespace):

    # invalid structure
    if not VALID_STRUCTURE_POLICY(die):
        return

    structure = namespace.create_structure(NO_NS_NAME_POLICY(die), die.byte_size() if die.has_byte_size() else 0)

    FLAT.structures[die.offset] = STRUCTURE_DATA_POLICY(die)
    members = FLAT.structures[die.offset]['members']

    for child in die.iter_children():
        build_structure_child(structure, child, namespace)

def build_union_child(union, members, die):
    wrap_die(die)

    if die.is_template_type_param():
        #TODO implement some sort of template parameters
        pass
    elif die.is_member():
        if not VALID_UNION_MEMBER_POLICY(die):
            return

        _member = union.create_member(
            die.name(), die.type()
        )
        _member.accessibility = ACCESSIBILITY_POLICY(die)

        return UNION_MEMBER_DATA_POLICY(die)
    elif die.is_subrange_type():
        build_subrange_type(die)

def build_union_type(die, namespace):

    # invalid structure
    if not VALID_UNION_POLICY(die):
        return

    union = namespace.create_union(NO_NS_NAME_POLICY(die), die.byte_size())

    FLAT.unions[die.offset] = UNION_DATA_POLICY(die)
    members = FLAT.unions[die.offset]['members']

    for child in die.iter_children():
        build_union_child(union, members, child)

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
    #SUBRANGE_DATA_FOR_ARRAY_PARENT_POLICY(die, FLAT)

def build_string_type(die):
    if not VALID_STRINGTYPE_POLICY(die):
        return

    FLAT.string_types[die.offset] = STRINGTYPE_DATA_POLICY(die)

def build_pointer_type(die):
    if not VALID_POINTERTYPE_POLICY(die):
        return

    FLAT.pointer_types[die.offset] = POINTERTYPE_DATA_POLICY(die)

def build_enumeration_child(enumeration, values, die):
    wrap_die(die)

    if not VALID_ENUMERATOR_POLICY(die):
        return

    _value = enumeration.add_value(
        die.name(), die.const_value()
    )

    return ENUMERATOR_DATA_POLICY(die)

def build_enumeration_type(die, namespace):
    if not VALID_ENUMERATION_POLICY(die):
        return

    enumeration = namespace.create_enumeration(
        die.name(),
        die.byte_size(),
        die.type(),
        die.encoding()
    )

    FLAT.enumerations[die.offset] = ENUMERATION_DATA_POLICY(die)
    values = FLAT.enumerations[die.offset]['values']

    for child in die.iter_children():
        build_enumeration_child(enumeration, values, child)

def build_const_type(die):
    if not VALID_CONSTTYPE_POLICY(die):
        return

    FLAT.const_types[die.offset] = CONSTTYPE_DATA_POLICY(die)

def die_info_rec(die, namespace:Namespace):
    for child in die.iter_children():
        wrap_die(child)

        if child.is_structure_like():
            build_structure_type(child, namespace)
        elif child.is_union_type():
            build_union_type(child, namespace)
        elif child.is_base_type():
            build_base_type(child)
        elif child.is_string_type():
            build_string_type(child)
        elif child.is_typedef():
            build_type_def(child)
        elif child.is_pointer_type():
            build_pointer_type(child)
        elif child.is_array_type():
            build_array_type(child)
        elif child.is_subrange_type():
            build_subrange_type(child)
        elif child.is_enumeration_type():
            build_enumeration_type(child, namespace)
        elif child.is_const_type():
            build_const_type(child)
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
    elif type_offset in FLAT.unions:
        return FLAT.unions[type_offset]
    elif type_offset in FLAT.string_types:
        return FLAT.string_types[type_offset]
    elif type_offset in FLAT.type_defs:
        return FLAT.type_defs[type_offset]
    elif type_offset in FLAT.pointer_types:
        return FLAT.pointer_types[type_offset]
    elif type_offset in FLAT.enumerations:
        return FLAT.enumerations[type_offset]
    elif type_offset in FLAT.const_types:
        return FLAT.const_types[type_offset]
    elif type_offset in FLAT.array_types:
        return FLAT.array_types[type_offset]
    raise ValueError

def resolve_type_offset_name(type_offset, flat):

    try:
        data = {}
        while 'name' not in data:
            data = resolve_type(type_offset, flat)
            if 'type' in data:
                type_offset = data['type']
            else:
                break

            # TODO this is a hack to fix some DW_TAG_pointer_types not having
            # a type offset.  The assumption is this is 'void*', but it's not
            # validated yet
            if isinstance(type_offset, str):
                return type_offset

        return data['name']
    except ValueError:
        logging.warning("Can't resolve name for type offset {}".format(type_offset))
        raise

def resolve_type_offset_size(type_offset, flat):
    try:
        data = resolve_type(type_offset, flat)
        while 'size' not in data:
            data = resolve_type(type_offset, flat)
            if 'type' in data:
                type_offset = data['type']
            else:
                break

        return data['size']
    except ValueError:
        logging.warning("Can't resolve name for type offset {}".format(type_offset))
        raise

def resolve_enumeration(enumeration):
    type_offset = enumeration.type
    resolved_type = resolve_type_offset(type_offset, FLAT)
    enumeration.type_str = resolve_type_offset_name(resolved_type, FLAT)

def resolve_union(union):

    for member in union.members.values():
        type_offset = member.type_offset
        resolved_type = resolve_type_offset(type_offset, FLAT)

        member.type_str = resolve_type_offset_name(resolved_type, FLAT)
        if member.bit_size is None:
            member.byte_size = resolve_type_offset_size(resolved_type, FLAT)

        if type_offset in FLAT.array_types:
            FLAT_array_type = FLAT.array_types[type_offset]
            array_subranges = FLAT_array_type['subranges']

            size = 0
            for subrange in array_subranges:
                subrange_type = FLAT.subrange_types[subrange]
                upper_bound = subrange_type['upper_bound']
                lower_bound = subrange_type['lower_bound']

                size += (upper_bound - lower_bound + 1) * member.byte_size
                member.add_to_bounds_list(lower_bound, upper_bound)

            member.type_str = member.type_str
            member.byte_size = size
            if member.bit_size is not None:
                member.byte_size = None

        if type_offset in FLAT.subrange_types:
            member.max_val = FLAT.subrange_types[type_offset]['upper_bound']
            member.min_val = FLAT.subrange_types[type_offset]['lower_bound']

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
            FLAT_array_type = FLAT.array_types[type_offset]
            array_subranges = FLAT_array_type['subranges']

            size = 0
            for subrange in array_subranges:
                subrange_type = FLAT.subrange_types[subrange]
                upper_bound = subrange_type['upper_bound']
                lower_bound = subrange_type['lower_bound']

                subrange_size = (upper_bound - lower_bound + 1) * member.byte_size
                if size == 0:
                    size = subrange_size
                else:
                    size *= subrange_size

                member.add_to_bounds_list(lower_bound, upper_bound)

            member.type_str = member.type_str
            member.byte_size = size
            if member.bit_size is not None:
                member.byte_size = None

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

        try:
            ns = namespace
            for n in namespaces:
                ns = namespace.namespaces[n]
        except KeyError:
            logging.warning("Skipping namespace \"{}\" because it wasn't resolved".format(n))
        else:
            ns.structures[name] = struct

def resolve_namespace(namespace):

    for enumeration in namespace.enumerations.values():
        resolve_enumeration(enumeration)

    for structure in namespace.structures.values():
        resolve_structure(structure)

    for union in namespace.unions.values():
        resolve_union(union)

    for n in namespace.namespaces.values():
        resolve_namespace(n)

