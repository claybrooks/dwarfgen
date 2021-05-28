from ..ipolicy import IPolicy
from ... import lookups
from ...wrapdie import wrap_die

class AritificialTypesPolicy(IPolicy):
    def check(self, die, **kwargs):
        return True

class AccessibilityPolicy(IPolicy):
    def check(self, die, **kwargs):
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

        return lookups.ACCESSIBILITY[die.accessibility()]

class StructureDataPolicy(IPolicy):

    def __init__(self, name_policy):
        self.name_policy = name_policy

    def check(self, die, **kwargs):
        size = 0
        if die.has_byte_size():
            size = die.byte_size()

        return {
            'name': self.name_policy.check(die, **kwargs),
            'size': size,
            'members': {}
        }

class ValidStructurePolicy(IPolicy):
    def check(self, die, **kwargs):
        return (
            die.has_name() or
            die.has_MIPS_linkage_name() or
            die.has_linkage_name()
        ) and not die.is_artificial()

class ValidTypedefPolicy(IPolicy):
    def check(self, die, **kwargs):
        return die.has_name()

class TypedefDataPolicy(IPolicy):
    def check(self, die, **kwargs):
        return {
            'name': die.name(),
            'type': die.type() if die.has_type() else ""
        }

class ValidConstTypePolicy(IPolicy):
    def check(self, die, **kwargs):
        return die.has_type()

class ConstTypeDataPolicy(IPolicy):
    def check(self, die, **kwargs):
        return {
        "type": die.type()
    }

class ValidUnionMemberPolicy(IPolicy):
    def check(self, die, **kwargs):
        return die.has_name() and die.has_type()

class UnionMemberDataPolicy(IPolicy):
    def check(self, die, **kwargs):
        return {
            "name": die.name(),
            "type": die.type()
        }

class ValidUnionPolicy(IPolicy):
    def check(self, die, **kwargs):
        return die.has_byte_size()

class UnionDataPolicy(IPolicy):
    def __init__(self, no_namespace_name_policy):
        self.no_namespace_name_policy = no_namespace_name_policy

    def check(self, die, **kwargs):
        return {
            "name": self.no_namespace_name_policy.check(die),
            "size": die.byte_size(),
            "members": {}
        }

class ValidArrayPolicy(IPolicy):
    def check(self, die, **kwargs):
        return die.has_sibling()

class ValidSubrangePolicy(IPolicy):
    def check(self, die, **kwargs):
        return die.has_type() and die.has_upper_bound()

class ValidBaseTypePolicy(IPolicy):
    def check(self, die, **kwargs):
        return die.has_byte_size() and die.has_encoding() and die.has_name()

class ValidStringTypePolicy(IPolicy):
    def check(self, die, **kwargs):
        return die.has_byte_size()

class ValidEnumerationPolicy(IPolicy):
    def check(self, die, **kwargs):
        return die.has_name() and die.has_byte_size() and die.has_type() and die.has_encoding()

class ValidStaticStructureMemberPolicy(IPolicy):
    def __init__(self, valid_structure_member_policy):
        self.valid_structure_member_policy = valid_structure_member_policy

    def check(self, die, **kwargs):
        return self.valid_structure_member_policy.check(die) and die.has_external()

class ValidInstanceStructureMemberPolicy(IPolicy):
    def __init__(self, valid_structure_member_policy):
        self.valid_structure_member_policy = valid_structure_member_policy

    def check(self, die, **kwargs):
        return self.valid_structure_member_policy.check(die) and die.has_data_member_location()

class ValidStructureMemberPolicy(IPolicy):
    def check(self, die, **kwargs):
        return die.has_name() and die.has_type()

class StructureMemberDataPolicy(IPolicy):
    def check(self, die, **kwargs):
        return {
            'name': die.name(),
            'typeOffset': die.type()
        }

class EnumerationDataPolicy(IPolicy):
    def check(self, die, **kwargs):
        return {
            'name': die.name(),
            'encoding': die.encoding(),
            'type': die.type(),
            'size': die.byte_size(),
            'values': {}
        }

class ValidEnumeratorPolicy(IPolicy):
    def check(self, die, **kwargs):
        return die.has_name() and die.has_const_value()

class EnumeratorDataPolicy(IPolicy):
    def check(self, die, **kwargs):
        return {
            'name': die.name(),
            'value': die.const_value()
        }

class ValidPointerTypePolicy(IPolicy):
    def check(self, die, **kwargs):
        return die.has_byte_size()

class ValidReferenceTypePolicy(IPolicy):
    def check(self, die, **kwargs):
        return die.has_byte_size()

class PointerTypeDataPolicy(IPolicy):
    def check(self, die, **kwargs):
        return {
            'size': die.byte_size(),
            'type': die.type() if die.has_type() else str("void")
        }

class ReferenceTypeDataPolicy(IPolicy):
    def check(self, die, **kwargs):
        return {
            'size': die.byte_size(),
            'type': die.type() if die.has_type() else str("void")
        }

class StaticStructureMemberDataPolicy(IPolicy):
    def __init__(self, structure_member_data_policy):
        self.structure_member_data_policy = structure_member_data_policy

    def check(self, die, **kwargs):
        member = kwargs.pop('member')
        member.is_static = True
        return self.structure_member_data_policy.check(die)

class InstanceStructureMemberDataPolicy(IPolicy):
    def __init__(self, structure_member_data_policy):
        self.structure_member_data_policy = structure_member_data_policy

    def check(self, die, **kwargs):
        member = kwargs.pop('member')

        ret = self.structure_member_data_policy.check(die)
        ret.update({"byteOffset": die.data_member_location()})
        member.byte_offset = die.data_member_location()

        if die.has_bit_size():
            ret.update({'DW_AT_bit_size': die.bit_size()})
            member.bit_size = die.bit_size()
        if die.has_bit_offset():
            ret.update({'DW_AT_bit_offset':  die.bit_offset()})
            member.bit_offset = die.bit_offset()
        return ret

class ArrayDataPolicy(IPolicy):
    def check(self, die, **kwargs):
        types = [x.offset for x in die.iter_children() if wrap_die(x).is_subrange_type()]
        return {
            'type': die.type(),
            'subranges': types
        }

class BaseTypeDataPolicy(IPolicy):

    def check(self, die, **kwargs):
        name = die.name()
        if '(kind' in name:
            name = name.split('(')[0]
        return {
            'size': die.byte_size(),
            'encoding': die.encoding(),
            'name': name
        }

class StringTypeDataPolicy(IPolicy):
    def check(self, die, **kwargs):
        return {
            'size': die.byte_size(),
            'name': 'string' if die.byte_size() > 1 else 'char'
        }

class SubrangeDataPolicy(IPolicy):
    def __init__(self, lower_bound_policy):
        self.lower_bound_policy = lower_bound_policy

    def check(self, die, **kwargs):
        return {
            'type': die.type(),
            'lower_bound': self.lower_bound_policy.check(die),
            'upper_bound': die.upper_bound(),
        }

class SubrangeLowerBoundPolicy(IPolicy):
    def __init__(self, default):
        self.default = default

    def check(self, die, **kwargs):
        return die.lower_bound() if die.has_lower_bound() else self.default

class NoNamespaceNamePolicy(IPolicy):

    def check(self, die, **kwargs):
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

class NamePolicy(IPolicy):
    def __init__(self, no_namespace_name_policy):
        self.no_namespace_name_policy = no_namespace_name_policy

    def check(self, die, **kwargs):
        name = self.no_namespace_name_policy.check(die)

        if die.has_namespace():
            return die.namespace + '::' + name
        else:
            return name

class NamespaceApplicationPolicy(IPolicy):
    def check(self, die, **kwargs):
        namespace = kwargs.pop("namespace")
        new_namespace = namespace.create_namespace(die.name())

        # inject ".namespace" attribute on all children
        for child in die.iter_children():
            curr_ns = getattr(die, 'namespace', None)
            if curr_ns is None:
                child.namespace = die.name()
            else:
                child.namespace = curr_ns + '::' + die.name()
        return new_namespace

class IsInheritancePolicy(IPolicy):
    def check(self, die, **kwargs):
        return die.is_inheritance()

class AllowArtificialTypesPolicy(IPolicy):
    def check(self, die, **kwargs):
        return False

class DwarfV2AccessibilityPolicy(IPolicy):
    def check(self, die, **kwargs):
        if not die.has_accessibility():
            return 'public'
        return lookups.ACCESSIBILITY[die.accessibility()]

class DwarfV2InheritanceAccessibilityPolicy(IPolicy):
    def check(self, die, **kwargs):
        if not die.has_accessibility():
            return 'private'
        return lookups.ACCESSIBILITY[die.accessibility()]
