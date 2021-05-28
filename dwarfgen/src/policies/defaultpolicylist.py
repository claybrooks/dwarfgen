from . import defaultpolicies

class DefaultPolicyList:

    def __init__(self, dwarf_version):
        self.aritificialtypes_policy                    = defaultpolicies.AritificialTypesPolicy()

        if dwarf_version == 2:
            self.accessibility_policy                   = defaultpolicies.DwarfV2AccessibilityPolicy()
            self.inheritance_accessibility_policy       = defaultpolicies.DwarfV2InheritanceAccessibilityPolicy()
        else:
            self.accessibility_policy                   = defaultpolicies.AccessibilityPolicy()
            self.inheritance_accessibility_policy       = defaultpolicies.AccessibilityPolicy()

        self.structure_data_policy                      = defaultpolicies.StructureDataPolicy()
        self.valid_structure_policy                     = defaultpolicies.ValidStructurePolicy()
        self.valid_typedef_policy                       = defaultpolicies.ValidTypedefPolicy()
        self.typedef_data_policy                        = defaultpolicies.TypedefDataPolicy()
        self.valid_consttype_policy                     = defaultpolicies.ValidConstTypePolicy()
        self.consttype_data_policy                      = defaultpolicies.ConstTypeDataPolicy()
        self.valid_unionmember_policy                   = defaultpolicies.ValidUnionMemberPolicy()
        self.unionmember_data_policy                    = defaultpolicies.UnionMemberDataPolicy()
        self.valid_union_policy                         = defaultpolicies.ValidUnionPolicy()
        self.union_data_policy                          = defaultpolicies.UnionDataPolicy()
        self.valid_array_policy                         = defaultpolicies.ValidArrayPolicy()
        self.valid_subrange_policy                      = defaultpolicies.ValidSubrangePolicy()
        self.valid_basetype_policy                      = defaultpolicies.ValidBaseTypePolicy()
        self.valid_stringtype_policy                    = defaultpolicies.ValidStringTypePolicy()
        self.valid_enumeration_policy                   = defaultpolicies.ValidEnumerationPolicy()
        self.valid_static_structuremember_policy        = defaultpolicies.ValidStaticStructureMemberPolicy()
        self.valid_instanced_structuremember_policy     = defaultpolicies.ValidInstanceStructureMemberPolicy()
        self.valid_structuremember_policy               = defaultpolicies.ValidStructureMemberPolicy()
        self.structuremember_data_policy                = defaultpolicies.StructureMemberDataPolicy()
        self.enumeration_data_policy                    = defaultpolicies.EnumerationDataPolicy()
        self.valid_enumerator_policy                    = defaultpolicies.ValidEnumeratorPolicy()
        self.enumerator_data_policy                     = defaultpolicies.EnumeratorDataPolicy()
        self.valid_pointertype_policy                   = defaultpolicies.ValidPointerTypePolicy()
        self.valid_referencetype_policy                 = defaultpolicies.ValidReferenceTypePolicy()
        self.pointertype_data_policy                    = defaultpolicies.PointerTypeDataPolicy()
        self.referencetype_data_policy                  = defaultpolicies.ReferenceTypeDataPolicy()
        self.static_structuremember_data_policy         = defaultpolicies.StaticStructureMemberDataPolicy()
        self.instanced_structuremember_data_policy      = defaultpolicies.InstanceStructureMemberDataPolicy()
        self.array_data_policy                          = defaultpolicies.ArrayDataPolicy()
        self.basetype_data_policy                       = defaultpolicies.BaseTypeDataPolicy()
        self.stringtype_data_policy                     = defaultpolicies.StringTypeDataPolicy()
        self.subrange_data_policy                       = defaultpolicies.SubrangeDataPolicy()
        self.zero_indexed_subrange_lowerbound_policy    = defaultpolicies.ZeroIndexedSubrangeLowerBoundPolicy()
        self.one_indexed_subrange_lowerbound_policy     = defaultpolicies.OneIndexedSubrangeLowerBoundPolicy()
        self.no_namespace_name_policy                   = defaultpolicies.NoNamespaceNamePolicy()
        self.name_policy                                = defaultpolicies.NamePolicy()
        self.subrange_dataforarrayparent_policy         = defaultpolicies.SubrangeDataForArrayParentPolicy()
        self.namespace_application_policy               = defaultpolicies.NamespaceApplicationPolicy()
        self.is_inheritance_policy                      = defaultpolicies.IsInheritancePolicy()
        self.subrange_lower_bound_policy                = defaultpolicies.ZeroIndexedSubrangeLowerBoundPolicy()

    def AritificialTypesPolicy(self, die):
        return self.aritificialtypes_policy.check(die)

    def AccessibilityPolicy(self, die):
        return self.accessibility_policy.check(die)

    def InheritanceAccessibilityPolicy(self, die):
        return self.inheritance_accessibility_policy.check(die)

    def StructureDataPolicy(self, die):
        return self.structure_data_policy.check(die, name_policy=self.name_policy, no_namespace_name_policy=self.no_namespace_name_policy)

    def ValidStructurePolicy(self, die):
        return self.valid_structure_policy.check(die)

    def ValidTypedefPolicy(self, die):
        return self.valid_typedef_policy.check(die)

    def TypedefDataPolicy(self, die):
        return self.typedef_data_policy.check(die)

    def ValidConstTypePolicy(self, die):
        return self.valid_consttype_policy.check(die)

    def ConstTypeDataPolicy(self, die):
        return self.consttype_data_policy.check(die)

    def ValidUnionMemberPolicy(self, die):
        return self.valid_unionmember_policy.check(die)

    def UnionMemberDataPolicy(self, die):
        return self.unionmember_data_policy.check(die)

    def ValidUnionPolicy(self, die):
        return self.valid_union_policy.check(die)

    def UnionDataPolicy(self, die):
        return self.union_data_policy.check(die, no_namespace_name_policy=self.no_namespace_name_policy)

    def ValidArrayPolicy(self, die):
        return self.valid_array_policy.check(die)

    def ValidSubrangePolicy(self, die):
        return self.valid_subrange_policy.check(die)

    def ValidBaseTypePolicy(self, die):
        return self.valid_basetype_policy.check(die)

    def ValidStringTypePolicy(self, die):
        return self.valid_stringtype_policy.check(die)

    def ValidEnumerationPolicy(self, die):
        return self.valid_enumeration_policy.check(die)

    def ValidStaticStructureMemberPolicy(self, die):
        return self.valid_static_structuremember_policy.check(die, valid_structuremember_policy=self.valid_structuremember_policy)

    def ValidInstanceStructureMemberPolicy(self, die):
        return self.valid_instanced_structuremember_policy.check(die, valid_structuremember_policy=self.valid_structuremember_policy)

    def ValidStructureMemberPolicy(self, die):
        return self.valid_structuremember_policy.check(die)

    def StructureMemberDataPolicy(self, die):
        return self.structuremember_data_policy.check(die)

    def EnumerationDataPolicy(self, die):
        return self.enumeration_data_policy.check(die)

    def ValidEnumeratorPolicy(self, die):
        return self.valid_enumerator_policy.check(die)

    def EnumeratorDataPolicy(self, die):
        return self.enumerator_data_policy.check(die)

    def ValidPointerTypePolicy(self, die):
        return self.valid_pointertype_policy.check(die)

    def ValidReferenceTypePolicy(self, die):
        return self.valid_referencetype_policy.check(die)

    def PointerTypeDataPolicy(self, die):
        return self.pointertype_data_policy.check(die)

    def ReferenceTypeDataPolicy(self, die):
        return self.referencetype_data_policy.check(die)

    def StaticStructureMemberDataPolicy(self, die, member):
        return self.static_structuremember_data_policy.check(die, member=member, structuremember_data_policy=self.structuremember_data_policy)

    def InstanceStructureMemberDataPolicy(self, die, member):
        return self.instanced_structuremember_data_policy.check(die, member=member, structuremember_data_policy=self.structuremember_data_policy)

    def ArrayDataPolicy(self, die):
        return self.array_data_policy.check(die)

    def BaseTypeDataPolicy(self, die):
        return self.basetype_data_policy.check(die)

    def StringTypeDataPolicy(self, die):
        return self.stringtype_data_policy.check(die)

    def SubrangeDataPolicy(self, die):
        return self.subrange_data_policy.check(die, subrange_lower_bound_policy=self.subrange_lower_bound_policy)

    def ZeroIndexedSubrangeLowerBoundPolicy(self, die):
        return self.zero_indexed_subrange_lowerbound_policy.check(die)

    def OneIndexedSubrangeLowerBoundPolicy(self, die):
        return self.one_indexed_subrange_lowerbound_policy.check(die)

    def NoNamespaceNamePolicy(self, die):
        return self.no_namespace_name_policy.check(die)

    def NamePolicy(self, die):
        return self.name_policy.check(die, no_namespace_name_policy=self.no_namespace_name_policy)

    def SubrangeDataForArrayParentPolicy(self, die, flat):
        return self.subrange_dataforarrayparent_policy.check(die, flat=flat)

    def NamespaceApplicationPolicy(self, die, namespace):
        return self.namespace_application_policy.check(die, namespace=namespace)

    def IsInheritancePolicy(self, die):
        return self.is_inheritance_policy.check(die)


