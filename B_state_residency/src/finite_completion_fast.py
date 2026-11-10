"""Equivalent finite allocator for closed single-owner domain use.

The issued set is always {0,...,n-1}: IDs are appended, never removed until fence.
Its cardinality therefore equals the next free ID. No unbounded sequence counter
or change to the wire descriptor, quarantine, or fence semantics is introduced.
External mutation of domain internals remains outside the supported interface.
"""
from .finite_completion import FiniteCompletionDomain,Descriptor,WouldBlock


class SequentialFiniteDomain(FiniteCompletionDomain):
    def issue(self, binding, kind):
        self._open();self._bound(binding)
        if binding.query!=self.active:raise ValueError('Query invalidated')
        if kind not in ('refill','writeback','pin'):raise ValueError('Invalid operation')
        same=[d for d in self.pending.values() if d.binding.slot==binding.slot]
        if (kind!='pin' and same) or (kind=='pin' and any(d.kind!='pin' for d in same)):
            raise WouldBlock('Incompatible outstanding slot leases')
        transaction=len(self.used_transactions)
        if transaction>=self.transaction_limit:raise WouldBlock('Transaction IDs exhausted; drain before reuse')
        descriptor=Descriptor(transaction,binding,kind)
        self.used_transactions.add(transaction);self.pending[transaction]=descriptor
        return descriptor
