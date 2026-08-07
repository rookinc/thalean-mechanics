# G60 orientation obstruction preregistration 011a

## Question

Does the unoriented raw G60 graph together with its characteristic
upper-central receipt tower select one evolver H, or only the reversal
orbit containing H and inverse(H)?

No evolver authority has been inspected or selected in this packet.

## Conditional obstruction theorem

Let D denote the unoriented graph, its full automorphism action, and the
characteristic tower `Z1 < Z2`.

Suppose H is a non-self-inverse admitted evolver and a D-preserving
symmetry exchanges H with inverse(H). Any canonical selector constructed
only from D must be invariant under that symmetry. It therefore cannot
select exactly one member of the pair.

The proof is immediate. If the selector chooses H, applying the preserving
symmetry must leave the selected result unchanged by invariance, while the
exchange law sends it to inverse(H). This would force
`H = inverse(H)`, contradicting the hypothesis.

The theorem is conditional until an exact native carrier, evolver pair,
and exchange symmetry are verified.

## Frozen native outcomes

- `exact_reversal_obstruction`
- `unique_orientation_selected`
- `self_inverse_collapse`
- `multiple_reversal_orbits`
- `no_exact_evolver_candidate`
- `computation_failure`

Negative and non-unique outcomes must be preserved. No preferred evolver
or directional datum may be chosen after inspecting its orientation
behavior.

## Minimal additional datum

A proposed directional datum is sufficient only if adjoining it selects
exactly one member of the reversal pair. It is minimal only if every
declared proper ablation restores the exchange symmetry or loses unique
selection.

Candidate forms such as an oriented cycle, ordered incident pair, generator
sign, or ordered source-target flag are examples only. None is
preregistered as the answer.

## Boundary

This packet does not define H, choose an orientation, verify a native
exchange symmetry, or identify a minimal directional datum. It does not
modify the manuscript and makes no geometry or physics claim.
