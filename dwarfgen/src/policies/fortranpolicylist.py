from .defaultpolicylist import DefaultPolicyList
from .policy import Policy
from . import defaultpolicies
from .accessibility import ACCESSIBILITY


class FortranPolicyList(DefaultPolicyList):

    def __init__(self, dwarf_version):
        super(FortranPolicyList, self).__init__(dwarf_version)
        self.subrange_lower_bound_policy = defaultpolicies.OneIndexedSubrangeLowerBoundPolicy()
