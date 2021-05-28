from . import lookups

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
        'reference_type',
        "enumeration_type",
        "enumerator",
        "const_type"
    ]

    for tag_type in tag_types:
        setattr(die, 'is_'+tag_type, lambda x=die, tag=tag_type: x.tag == 'DW_TAG_'+tag)

    # add a special one for artificial
    setattr(die, "is_artificial",   lambda x=die: x.has_artificial() and x.artificial() == 1)

    # add a special one for namespace
    setattr(die, "has_namespace",   lambda x=die: hasattr(x, 'namespace'))

    # add a single member function to check all structure like types
    setattr(die, 'is_structure_like', lambda x=die: x.is_structure_type() or x.is_class_type())

    return die

