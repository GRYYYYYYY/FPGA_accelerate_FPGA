"""Explicit physical site-resource ownership and configuration compatibility.

Adapters must supply actual physical resource IDs and verified requirements.
This module does not infer route-through legality from names or IS_USED.
"""
from collections import defaultdict


class ConfigurationBits:
    """Shared configuration fields, independent of exclusive signal resources.

    Each requirement is (physical field ID, bit mask, value). Two signals may
    agree on shared bits; signal/output ownership is checked by SiteResources.
    """
    def __init__(self, fixed=()):
        self.fixed = self.normalize(fixed)
        self.by_net = {}

    @staticmethod
    def normalize(requirements):
        result = {}
        for field, mask, value in requirements:
            if not isinstance(mask,int) or not isinstance(value,int) or mask < 0 or value < 0 or value & ~mask:
                raise ValueError('Invalid configuration bit mask/value')
            old_mask,old_value = result.get(field,(0,0))
            if (old_value ^ value) & old_mask & mask:
                raise ValueError('Contradictory configuration bits: '+field)
            result[field] = (old_mask | mask,old_value | value)
        return result

    def conflicts(self, net, requirements):
        requested = self.normalize(requirements)
        conflicts = []
        for owner, existing in [(None,self.fixed),*self.by_net.items()]:
            if owner == net:continue
            for field,(mask,value) in requested.items():
                other_mask,other_value = existing.get(field,(0,0))
                if (value ^ other_value) & mask & other_mask:
                    conflicts.append((field,owner))
        return conflicts

    def replace(self, net, requirements):
        requirements = list(requirements)
        if self.conflicts(net,requirements):
            raise ValueError('Incompatible shared configuration')
        self.by_net[net] = self.normalize(requirements)

    def release(self, net):
        self.by_net.pop(net,None)


class SiteResources:
    def __init__(self, fixed=()):
        self.fixed = {}
        self.dynamic = defaultdict(dict)
        self.by_net = {}
        for resource, net, configuration in fixed:
            value = (net,configuration)
            if resource in self.fixed and self.fixed[resource] != value:
                raise ValueError('Conflicting fixed site resource: '+resource)
            self.fixed[resource] = value

    @staticmethod
    def normalize(requirements):
        result = {}
        for resource,configuration in requirements:
            if resource in result and result[resource] != configuration:
                raise ValueError('Incompatible requirements within one net: '+resource)
            result[resource] = configuration
        return result

    def conflicts(self, net, requirements):
        requested = self.normalize(requirements)
        conflicts = []
        for resource,configuration in requested.items():
            if resource in self.fixed:
                owner,existing = self.fixed[resource]
                if owner != net or existing != configuration:
                    conflicts.append((resource,owner,'fixed'))
            for owner,existing in self.dynamic.get(resource,{}).items():
                if owner != net or existing != configuration:
                    conflicts.append((resource,owner,'dynamic'))
        return conflicts

    def replace(self, net, requirements):
        """Atomically replace a net's demands; reject without releasing old ones."""
        requested = self.normalize(requirements)
        # A replacement may change its own configuration, but not fixed state.
        for resource,configuration in requested.items():
            if resource in self.fixed and self.fixed[resource] != (net,configuration):
                raise ValueError('Fixed site resource conflict: '+resource)
            if any(owner != net for owner in self.dynamic.get(resource,{})):
                raise ValueError('Dynamic site resource conflict: '+resource)
        self.release(net)
        for resource,configuration in requested.items():
            self.dynamic[resource][net] = configuration
        self.by_net[net] = requested

    def release(self, net):
        for resource in self.by_net.pop(net,{}):
            del self.dynamic[resource][net]
            if not self.dynamic[resource]:del self.dynamic[resource]


class SiteState:
    """Atomic ownership, INIT-bit and categorical configuration transactions."""
    def __init__(self, fixed_signals=(), fixed_bits=(), fixed_values=()):
        self.signals=SiteResources((resource,owner,0) for resource,owner in fixed_signals)
        self.bits=ConfigurationBits(fixed_bits)
        self.fixed_values={}
        for field,value in fixed_values:
            if field in self.fixed_values and self.fixed_values[field]!=value:
                raise ValueError('Contradictory fixed categorical configuration')
            self.fixed_values[field]=value
        self.values={}

    def conflicts(self, net, requirement):
        if 'status' in requirement or requirement.get('additional_requirements'):
            raise ValueError('Unverified requirement payload')
        signals=[(resource,0) for resource in requirement.get('signal_resources',())]
        bits=requirement.get('configuration_bits',())
        values={}
        for field,value in requirement.get('configuration_values',()):
            if field in values and values[field]!=value:
                raise ValueError('Contradictory categorical requirements')
            values[field]=value
        result=self.signals.conflicts(net,signals)+self.bits.conflicts(net,bits)
        for owner,existing in [(None,self.fixed_values),*self.values.items()]:
            if owner==net:continue
            for field,value in values.items():
                if field in existing and existing[field]!=value:
                    result.append((field,owner,'categorical'))
        return result

    def replace(self, net, requirement):
        if self.conflicts(net,requirement):raise ValueError('Conflicting site transaction')
        # All components validated before either ownership table is changed.
        signals=[(r,0) for r in requirement.get('signal_resources',())]
        bits=list(requirement.get('configuration_bits',()))
        values=dict(requirement.get('configuration_values',()))
        self.signals.replace(net,signals)
        self.bits.replace(net,bits)
        self.values[net]=values

    def release(self, net):
        self.signals.release(net);self.bits.release(net);self.values.pop(net,None)
