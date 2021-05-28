from ... import lookups
from . import policies

class Policy:

    def __init__(self, dwarf_version, language):
        self.aritificialtypes_policy                    = policies.AritificialTypesPolicy()

        if dwarf_version == 2:
            self.accessibility_policy                   = policies.DwarfV2AccessibilityPolicy()
            self.inheritance_accessibility_policy       = policies.DwarfV2InheritanceAccessibilityPolicy()
        else:
            self.accessibility_policy                   = policies.AccessibilityPolicy()
            self.inheritance_accessibility_policy       = policies.AccessibilityPolicy()

        self.no_namespace_name_policy                   = policies.NoNamespaceNamePolicy()
        self.name_policy                                = policies.NamePolicy(self.no_namespace_name_policy)

        self.structure_data_policy                      = policies.StructureDataPolicy(self.name_policy)
        self.valid_structure_policy                     = policies.ValidStructurePolicy()
        self.valid_typedef_policy                       = policies.ValidTypedefPolicy()
        self.typedef_data_policy                        = policies.TypedefDataPolicy()
        self.valid_const_type_policy                    = policies.ValidConstTypePolicy()
        self.const_type_data_policy                     = policies.ConstTypeDataPolicy()
        self.valid_union_member_policy                  = policies.ValidUnionMemberPolicy()
        self.union_member_data_policy                   = policies.UnionMemberDataPolicy()
        self.valid_union_policy                         = policies.ValidUnionPolicy()
        self.union_data_policy                          = policies.UnionDataPolicy(self.no_namespace_name_policy)
        self.valid_array_policy                         = policies.ValidArrayPolicy()
        self.valid_subrange_policy                      = policies.ValidSubrangePolicy()
        self.valid_base_type_policy                     = policies.ValidBaseTypePolicy()
        self.valid_string_type_policy                   = policies.ValidStringTypePolicy()
        self.valid_enumeration_policy                   = policies.ValidEnumerationPolicy()
        self.valid_structure_member_policy              = policies.ValidStructureMemberPolicy()
        self.valid_static_structure_member_policy       = policies.ValidStaticStructureMemberPolicy(self.valid_structure_member_policy)
        self.valid_instance_structure_member_policy     = policies.ValidInstanceStructureMemberPolicy(self.valid_structure_member_policy)
        self.structure_member_data_policy               = policies.StructureMemberDataPolicy()
        self.enumeration_data_policy                    = policies.EnumerationDataPolicy()
        self.valid_enumerator_policy                    = policies.ValidEnumeratorPolicy()
        self.enumerator_data_policy                     = policies.EnumeratorDataPolicy()
        self.valid_pointer_type_policy                  = policies.ValidPointerTypePolicy()
        self.valid_reference_type_policy                = policies.ValidReferenceTypePolicy()
        self.pointer_type_data_policy                   = policies.PointerTypeDataPolicy()
        self.reference_type_data_policy                 = policies.ReferenceTypeDataPolicy()
        self.static_structure_member_data_policy        = policies.StaticStructureMemberDataPolicy(self.structure_member_data_policy)
        self.instance_structure_member_data_policy      = policies.InstanceStructureMemberDataPolicy(self.structure_member_data_policy)
        self.array_data_policy                          = policies.ArrayDataPolicy()
        self.base_type_data_policy                      = policies.BaseTypeDataPolicy()
        self.string_type_data_policy                    = policies.StringTypeDataPolicy()
        self.subrange_lower_bound_policy                = policies.SubrangeLowerBoundPolicy(lookups.DEFAULT_LOWER_BOUND[language])
        self.subrange_data_policy                       = policies.SubrangeDataPolicy(self.subrange_lower_bound_policy)
        #self.subrange_data_for_array_parent_policy      = policies.SubrangeDataForArrayParentPolicy()
        self.namespace_application_policy               = policies.NamespaceApplicationPolicy()
        self.is_inheritance_policy                      = policies.IsInheritancePolicy()
