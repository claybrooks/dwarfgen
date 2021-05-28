from ..default import policies as defaultpolicies
from ..default.policy import Policy as DefaultPolicy
from ..ipolicy import IPolicy
from ...lookups import ACCESSIBILITY

class AdaIsInheritancePolicy(IPolicy):
    def check(self, die, **kwargs):
        return die.is_member() and die.name() == '_parent'

class AdaValidStructurePolicy(defaultpolicies.ValidStructurePolicy):
    def check(self, die, **kwargs):
        return super(AdaValidStructurePolicy, self).check(die) and ('ada__' not in die.name())

class AdaDwarfV2InheritanceAccessibilityPolicy(IPolicy):
    def check(self, die, **kwargs):
        if not die.has_accessibility():
            return 'public'
        return ACCESSIBILITY[die.accessibility()]

class AdaAllowArtificialTypesPolicy(IPolicy):
    def check(self, die, **kwargs):
        return True

class Policy(DefaultPolicy):

    def __init__(self, dwarf_version, language):
        super(Policy, self).__init__(dwarf_version, language)

        self.is_inheritance_policy = AdaIsInheritancePolicy()
        self.valid_structure_policy = AdaValidStructurePolicy()
        self.allow_artificial_types_policy = AdaAllowArtificialTypesPolicy()

        if dwarf_version == 2:
            self.inheritance_accessibility_policy = AdaDwarfV2InheritanceAccessibilityPolicy()
