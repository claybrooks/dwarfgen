import importlib
import json
import logging
from elftools.elf.elffile import ELFFile

from .namespace import  Namespace
from .structure import Structure
from .member import Member

from .wrapdie import wrap_die
from . import policies
from .policies import default
from .lookups import CODE_TO_LANG


FLAT = None
class FlatStructure:
    '''
    This is a structure that maps type-reference info to a dictionary
    of data.  By type-reference, I mean the hexadecimal lookup value
    found for each type in a dwarf structure.  This FlatStructure reduces
    the amount of data and transforms it  for the purposes of this
    script.  There is another set of data that is calculated as the script
    processes the dwarf structure, and those are member.py, structure.py,
    etc...  It's not enough to either maintain the FLAT structure or the
    nested member structure currently.  Until I find a better way, both
    are calculated at the same time and then the FLAT structure is used
    to supplement the nested structures at the end of the script.
    '''
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
        self.reference_types = {}
        self.ignored_types = {}
        self.const_types = {}

'''
This is the policy class that will be created based on the language
'''
POLICY = None

def apply_policies(version, language):
    global POLICY

    policy_language_module = default
    detected_language = CODE_TO_LANG[language].lower()

    try:
        policy_language_module = importlib.import_module(policies.__name__+'.'+detected_language)
    except Exception:
        pass

    policy_module = importlib.import_module(policy_language_module.__name__+'.policy')
    POLICY = policy_module.Policy(version, language)

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
            wrap_die(top_DIE)

            language = top_DIE.language()

            if language not in CODE_TO_LANG:
                logging.error('Unkown Language from producer {}'.format(language))
                continue
            else:
                logging.info("Detected Language " + CODE_TO_LANG[language])

            apply_policies(CU.header.version, language)
            die_info_rec(top_DIE, namespace)


        # Ada does not use DW_TAG_namespace like C++, so namespace inference comes from DW_AT_name of types
        # This function moves structures around and creates namespaces to make it look identical to what c++
        # processing would produce prior to calling "resolve_namespace".
        if CODE_TO_LANG[language] == 'ADA':
            ada_disperse_structures(namespace)

        resolve_namespace(namespace)

    return namespace

def build_base_type(die):
    if not POLICY.valid_base_type_policy(die):
        return

    FLAT.base_types[die.offset] = POLICY.base_type_data_policy(die)

def build_structure_child(structure, die, namespace):
    wrap_die(die)

    if die.is_template_type_param():
        #TODO implement some sort of template parameters
        pass
    elif POLICY.is_inheritance_policy(die):
        structure.add_base_structure(die.type(), POLICY.inheritance_accessibility_policy(die), die.data_member_location())
    elif die.is_member():
        if not POLICY.valid_structure_member_policy(die):
            return

        _member = structure.create_member(
            die.name(), die.type()
        )
        _member.accessibility = POLICY.accessibility_policy(die)

        if POLICY.valid_static_structure_member_policy(die):
            return POLICY.static_structure_member_data_policy(die, member=_member)
        elif POLICY.valid_instance_structure_member_policy(die, member=_member):
            return POLICY.instance_structure_member_data_policy(die, member=_member)
    elif die.is_subrange_type():
        build_subrange_type(die)
    elif die.is_structure_type():
        #members[parent_name] = die.type()
        pass
    elif die.is_union_type():
        build_union_type(die, namespace)

def build_structure_type(die, namespace):

    # invalid structure
    if not POLICY.valid_structure_policy(die):
        return

    structure = namespace.create_structure(POLICY.no_namespace_name_policy(die), die.byte_size() if die.has_byte_size() else 0)

    FLAT.structures[die.offset] = POLICY.structure_data_policy(die)

    for child in die.iter_children():
        build_structure_child(structure, child, namespace)

def build_union_child(union, members, die):
    wrap_die(die)

    if die.is_template_type_param():
        #TODO implement some sort of template parameters
        pass
    elif die.is_member():
        if not POLICY.valid_union_member_policy(die):
            return

        _member = union.create_member(
            die.name(), die.type()
        )
        _member.accessibility = POLICY.accessibility_policy(die)

        return POLICY.union_member_data_policy(die)
    elif die.is_subrange_type():
        build_subrange_type(die)

def build_union_type(die, namespace):

    # invalid structure
    if not POLICY.valid_union_policy(die):
        return

    union = namespace.create_union(POLICY.no_namespace_name_policy(die), die.byte_size())

    FLAT.unions[die.offset] = POLICY.union_data_policy(die)
    members = FLAT.unions[die.offset]['members']

    for child in die.iter_children():
        build_union_child(union, members, child)

def build_type_def(die):
    if not POLICY.valid_typedef_policy(die):
        return

    FLAT.type_defs[die.offset] = POLICY.typedef_data_policy(die)

def build_array_type(die):
    if not POLICY.valid_array_policy(die):
        return

    FLAT.array_types[die.offset] = POLICY.array_data_policy(die)

def build_subrange_type(die):
    if not POLICY.valid_subrange_policy(die):
        return

    FLAT.subrange_types[die.offset] = POLICY.subrange_data_policy(die)

def build_string_type(die):
    if not POLICY.valid_string_type_policy(die):
        return

    FLAT.string_types[die.offset] = POLICY.string_type_data_policy(die)

def build_pointer_type(die):
    if not POLICY.valid_pointer_type_policy(die):
        return

    FLAT.pointer_types[die.offset] = POLICY.pointer_type_data_policy(die)

def build_reference_type(die):
    if not POLICY.valid_reference_type_policy(die):
        return

    FLAT.reference_types[die.offset] = POLICY.reference_type_data_policy(die)

def build_enumeration_child(enumeration, values, die):
    wrap_die(die)

    if not POLICY.valid_enumerator_policy(die):
        return

    _value = enumeration.add_value(
        die.name(), die.const_value()
    )

    return POLICY.enumerator_data_policy(die)

def build_enumeration_type(die, namespace):
    if not POLICY.valid_enumeration_policy(die):
        return

    enumeration = namespace.create_enumeration(
        die.name(),
        die.byte_size(),
        die.type(),
        die.encoding()
    )

    FLAT.enumerations[die.offset] = POLICY.enumeration_data_policy(die)
    values = FLAT.enumerations[die.offset]['values']

    for child in die.iter_children():
        build_enumeration_child(enumeration, values, child)

def build_const_type(die):
    if not POLICY.valid_const_type_policy(die):
        return

    FLAT.const_types[die.offset] = POLICY.const_type_data_policy(die)

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
        elif child.is_reference_type():
            build_reference_type(child)
        elif child.is_array_type():
            build_array_type(child)
        elif child.is_subrange_type():
            build_subrange_type(child)
        elif child.is_enumeration_type():
            build_enumeration_type(child, namespace)
        elif child.is_const_type():
            build_const_type(child)
        elif child.is_namespace():
            new_namespace = POLICY.namespace_application_policy(child, namespace=namespace)
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
    elif type_offset in FLAT.reference_types:
        return FLAT.reference_types[type_offset]
    elif type_offset in FLAT.enumerations:
        return FLAT.enumerations[type_offset]
    elif type_offset in FLAT.const_types:
        return FLAT.const_types[type_offset]
    elif type_offset in FLAT.array_types:
        return FLAT.array_types[type_offset]
    raise ValueError

def get_pointer_chain_count(type_offset):
    count = 0
    while type_offset in FLAT.pointer_types:
        type_offset = FLAT.pointer_types[type_offset]['type']
        count += 1

    return count

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

def resolve(base_type):
    for member in base_type.members.values():
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

        if type_offset in FLAT.reference_types:

            type_ref = FLAT.reference_types[type_offset]['type']

            if type_ref in FLAT.pointer_types:
                count = get_pointer_chain_count(type_ref)
                member.type_str += (" " + " ".join(["pointer"]*count))

            member.type_str += " reference"

        if type_offset in FLAT.pointer_types:
            count = get_pointer_chain_count(type_offset)
            member.type_str += (" " + " ".join(["pointer"]*count))

        if type_offset in FLAT.subrange_types:
            member.max_val = FLAT.subrange_types[type_offset]['upper_bound']
            member.min_val = FLAT.subrange_types[type_offset]['lower_bound']

def resolve_union(union):
    resolve(union)

def resolve_structure(structure):

    for base_structure in structure.base_structures.values():
        resolved_type = resolve_type_offset(base_structure.type_offset, FLAT)
        base_structure.type = resolve_type_offset_name(resolved_type, FLAT)

    resolve(structure)

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

