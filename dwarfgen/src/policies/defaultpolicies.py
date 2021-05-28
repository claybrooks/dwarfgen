from .policy import Policy
from .accessibility import ACCESSIBILITY
from ..wrapdie import wrap_die

class AritificialTypesPolicy(Policy):
    def check(self, die, **kwargs):
        return True

class AccessibilityPolicy(Policy):
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

        return ACCESSIBILITY[die.accessibility()]

class StructureDataPolicy(Policy):

    def check(self, die, **kwargs):

        name_policy = kwargs.pop("name_policy")

        size = 0
        if die.has_byte_size():
            size = die.byte_size()

        return {
            'name': name_policy.check(die, **kwargs),
            'size': size,
            'members': {}
        }

class ValidStructurePolicy(Policy):
    def check(self, die, **kwargs):
        return (
            die.has_name() or
            die.has_MIPS_linkage_name() or
            die.has_linkage_name()
        ) and not die.is_artificial()

class ValidTypedefPolicy(Policy):
    def check(self, die, **kwargs):
        return die.has_name()

class TypedefDataPolicy(Policy):
    def check(self, die, **kwargs):
        return {
            'name': die.name(),
            'type': die.type() if die.has_type() else ""
        }

class ValidConstTypePolicy(Policy):
    def check(self, die, **kwargs):
        return die.has_type()

class ConstTypeDataPolicy(Policy):
    def check(self, die, **kwargs):
        return {
        "type": die.type()
    }

class ValidUnionMemberPolicy(Policy):
    def check(self, die, **kwargs):
        return die.has_name() and die.has_type()

class UnionMemberDataPolicy(Policy):
    def check(self, die, **kwargs):
        return {
            "name": die.name(),
            "type": die.type()
        }

class ValidUnionPolicy(Policy):
    def check(self, die, **kwargs):
        return die.has_byte_size()

class UnionDataPolicy(Policy):
    def check(self, die, **kwargs):
        no_namespace_name_policy = kwargs.pop("no_namespace_name_policy")

        return {
            "name": no_namespace_name_policy.check(die),
            "size": die.byte_size(),
            "members": {}
        }

class ValidArrayPolicy(Policy):
    def check(self, die, **kwargs):
        return die.has_sibling()

class ValidSubrangePolicy(Policy):
    def check(self, die, **kwargs):
        return die.has_type() and die.has_upper_bound()

class ValidBaseTypePolicy(Policy):
    def check(self, die, **kwargs):
        return die.has_byte_size() and die.has_encoding() and die.has_name()

class ValidStringTypePolicy(Policy):
    def check(self, die, **kwargs):
        return die.has_byte_size()

class ValidEnumerationPolicy(Policy):
    def check(self, die, **kwargs):
        return die.has_name() and die.has_byte_size() and die.has_type() and die.has_encoding()

class ValidStaticStructureMemberPolicy(Policy):
    def check(self, die, **kwargs):
        valid_structuremember_policy = kwargs.pop("valid_structuremember_policy")
        return valid_structuremember_policy.check(die) and die.has_external()

class ValidInstanceStructureMemberPolicy(Policy):
    def check(self, die, **kwargs):
        valid_structuremember_policy = kwargs.pop("valid_structuremember_policy")
        return valid_structuremember_policy.check(die) and die.has_data_member_location()

class ValidStructureMemberPolicy(Policy):
    def check(self, die, **kwargs):
        return die.has_name() and die.has_type()

class StructureMemberDataPolicy(Policy):
    def check(self, die, **kwargs):
        return {
            'name': die.name(),
            'typeOffset': die.type()
        }

class EnumerationDataPolicy(Policy):
    def check(self, die, **kwargs):
        return {
            'name': die.name(),
            'encoding': die.encoding(),
            'type': die.type(),
            'size': die.byte_size(),
            'values': {}
        }

class ValidEnumeratorPolicy(Policy):
    def check(self, die, **kwargs):
        return die.has_name() and die.has_const_value()

class EnumeratorDataPolicy(Policy):
    def check(self, die, **kwargs):
        return {
            'name': die.name(),
            'value': die.const_value()
        }

class ValidPointerTypePolicy(Policy):
    def check(self, die, **kwargs):
        return die.has_byte_size()

class ValidReferenceTypePolicy(Policy):
    def check(self, die, **kwargs):
        return die.has_byte_size()

class PointerTypeDataPolicy(Policy):
    def check(self, die, **kwargs):
        return {
            'size': die.byte_size(),
            'type': die.type() if die.has_type() else str("void")
        }

class ReferenceTypeDataPolicy(Policy):
    def check(self, die, **kwargs):
        return {
            'size': die.byte_size(),
            'type': die.type() if die.has_type() else str("void")
        }

class StaticStructureMemberDataPolicy(Policy):
    def check(self, die, **kwargs):
        member = kwargs.pop("member")
        structuremember_data_policy = kwargs.pop("structuremember_data_policy")

        member.is_static = True
        return structuremember_data_policy.check(die)

class InstanceStructureMemberDataPolicy(Policy):

    def check(self, die, **kwargs):
        member = kwargs.pop("member")
        structuremember_data_policy = kwargs.pop("structuremember_data_policy")

        ret = structuremember_data_policy.check(die)

        ret.update({"byteOffset": die.data_member_location()})
        member.byte_offset = die.data_member_location()

        if die.has_bit_size():
            ret.update({'DW_AT_bit_size': die.bit_size()})
            member.bit_size = die.bit_size()
        if die.has_bit_offset():
            ret.update({'DW_AT_bit_offset':  die.bit_offset()})
            member.bit_offset = die.bit_offset()
        return ret

class ArrayDataPolicy(Policy):
    def check(self, die, **kwargs):
        types = [x.offset for x in die.iter_children() if wrap_die(x).is_subrange_type()]
        return {
            'type': die.type(),
            'subranges': types
        }

class BaseTypeDataPolicy(Policy):

    def check(self, die, **kwargs):
        name = die.name()
        if '(kind' in name:
            name = name.split('(')[0]
        return {
            'size': die.byte_size(),
            'encoding': die.encoding(),
            'name': name
        }

class StringTypeDataPolicy(Policy):
    def check(self, die, **kwargs):
        return {
            'size': die.byte_size(),
            'name': 'string' if die.byte_size() > 1 else 'char'
        }

class SubrangeDataPolicy(Policy):
    def check(self, die, **kwargs):
        subrange_lower_bound_policy = kwargs.pop("subrange_lower_bound_policy")

        return {
            'type': die.type(),
            'lower_bound': subrange_lower_bound_policy.check(die),
            'upper_bound': die.upper_bound(),
        }

class ZeroIndexedSubrangeLowerBoundPolicy(Policy):
    def check(self, die, **kwargs):
        return die.lower_bound() if die.has_lower_bound() else 0

class OneIndexedSubrangeLowerBoundPolicy(Policy):
    def check(self, die, **kwargs):
        return die.lower_bound() if die.has_lower_bound() else 1

class NoNamespaceNamePolicy(Policy):

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

class NamePolicy(Policy):
    def check(self, die, **kwargs):
        no_namespace_name_policy = kwargs.pop("no_namespace_name_policy")
        name = no_namespace_name_policy.check(die)

        if die.has_namespace():
            return die.namespace + '::' + name
        else:
            return name

class SubrangeDataForArrayParentPolicy(Policy):
    def check(self, die, **kwargs):
        flat = kwargs.pop("flat")

        parent = die.get_parent()
        if parent and parent.offset in flat.array_types:
            flat.array_types[parent.offset]['upper_bound'] = flat.subrange_types[die.offset]['upper_bound']
            flat.array_types[parent.offset]['lower_bound'] = flat.subrange_types[die.offset]['lower_bound']

class NamespaceApplicationPolicy(Policy):

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

class IsInheritancePolicy(Policy):
    def check(self, die, **kwargs):
        return die.is_inheritance()

class AllowArtificialTypesPolicy(Policy):
    def check(self, die, **kwargs):
        return False

class DwarfV2AccessibilityPolicy(Policy):
    def check(self, die, **kwargs):
        if not die.has_accessibility():
            return 'public'
        return ACCESSIBILITY[die.accessibility()]

class DwarfV2InheritanceAccessibilityPolicy(Policy):
    def check(self, die, **kwargs):
        if not die.has_accessibility():
            return 'private'
        return ACCESSIBILITY[die.accessibility()]
