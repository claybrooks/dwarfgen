from .defaultpolicylist import DefaultPolicyList
from .policy import Policy
from . import defaultpolicies
from .accessibility import ACCESSIBILITY

class AdaIsInheritancePolicy(Policy):
    def check(self, die, **kwargs):
        return die.is_member() and die.name() == '_parent'

class AdaValidStructurePolicy(defaultpolicies.ValidStructurePolicy):
    def check(self, die, **kwargs):
        return super(AdaValidStructurePolicy, self).check(die) and ('ada__' not in die.name())

class AdaDwarfV2InheritanceAccessibilityPolicy(Policy):
    def check(self, die, **kwargs):
        if not die.has_accessibility():
            return 'public'
        return ACCESSIBILITY[die.accessibility()]

class AdaAllowArtificialTypesPolicy(Policy):
    def check(self, die, **kwargs):
        return True


class AdaPolicyList(DefaultPolicyList):

    def __init__(self, dwarf_version):
        super(AdaPolicyList, self).__init__(dwarf_version)

        self.is_inheritance_policy = AdaIsInheritancePolicy()
        self.valid_structure_policy = AdaValidStructurePolicy()
        self.allow_artificial_types_policy = AdaAllowArtificialTypesPolicy()
        if dwarf_version == 2:
            self.inheritance_accessibility_policy = AdaDwarfV2InheritanceAccessibilityPolicy()
        self.subrange_lower_bound_policy = defaultpolicies.OneIndexedSubrangeLowerBoundPolicy()
