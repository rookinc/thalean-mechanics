# G60 upper-central receipt selector preregistration 010a

## Question

Let A be the exact full automorphism group of the raw native G60 graph.
Does the upper-central series of A intrinsically select a nested receipt
tower whose first layer has order 2 and whose second layer has order 4?

## Blind Phase A

Phase A may use only the raw 120-edge G60 graph and the exact 480-element
permutation action. From the action authority it may read only
`actual_index`, `actual_permutation`, and `actual_order`.

Historical reference fields, historical deck names, prior class identities,
prior quotient labels, and prior voltage certificates are excluded.

## Frozen conventions

A permutation p is represented by the images p[v]. The product p*q is
defined by `(p*q)[v] = p[q[v]]`, meaning that q acts first.

The commutator is

`[g,h] = inverse(g)*inverse(h)*g*h`.

The first center Z1 consists of the elements commuting with every group
element. The second center Z2 consists of the elements whose commutators
with every group element lie in Z1.

## Frozen outcomes

1. `computation_failure`: the exact operation cannot be reconstructed
   consistently.
2. `unexpected_center`: Z1 does not have order 2.
3. `center_only`: Z1 has order 2 and Z2 equals Z1.
4. `exact_target`: Z1 has order 2 and Z2 has order 4.
5. `larger_second_center`: Z1 has order 2 and Z2 has order greater than 4.

These predicates contain no preregistered member identities.

## Falsification boundary

A negative or weakened result must be retained. No smallest-order rule,
replacement selector, or retrofitted criterion may be introduced in the
same packet. Phase B unblinding is forbidden until the blind Phase A report
has been written and hashed, and preferably committed.

Even if the exact target passes, the blind spectrum still contains 22
admissible actions. The possible theorem is only that a canonical
group-theoretic filtration selects one nested receipt tower from that
spectrum.

No orientation, geometry, electron, spin, spacetime, gravity, radiation,
energy, quantum, force, or physics claim is made. The existing manuscript
is outside this exploration and must not be mutated.

## Repository status snapshot correction

The generator was rerun before this packet was committed. Its repository
status snapshot therefore includes the untracked preregistration files
themselves. The snapshot is labeled as the status at the final
preregistration freeze, not as a clean worktree or pre-packet status claim.

This metadata correction changes no outcome predicate, group convention,
blindness condition, or theorem boundary. No central-series computation had
been performed when the correction was made.
