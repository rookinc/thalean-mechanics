# G60 upper-central receipt tower unblinding 010c

## Result

Let

`A = Aut(G60)`

for the exact native 480-element permutation action.

The frozen blind Phase A computation returned

`Z1(A) = [0, 326]`

and

`Z2(A) = [0, 65, 124, 326]`.

Phase B compares these frozen sets with the previously certified blind
receipt classes. The equalities are exact:

`Z1(A) = class 22 = C2`

and

`Z2(A) = class 20 = V4`.

Moreover,

`Z1(A) < Z2(A)`

and

`Z3(A) = Z2(A)`.

Thus the upper-central series stabilizes at the recovered V4 layer.

## Intrinsic selector

The construction uses:

- the full automorphism group of the raw graph;
- its center;
- its second center;
- upper-central subgroup inclusion;
- the third center only as a stabilization check.

It does not use a smallest-order rule, an additional selector, or a
replacement criterion. Upper-central terms are characteristic subgroups,
so the nested C2 and V4 layers are canonical within the full automorphism
group.

## Exact quotient tower

The Z1 action is free with thirty two-state vertex orbits. It has no edge
inversions and satisfies the local covering law. Exact subgroup equality
with the previously certified normal C2 transfers the exact labeled
G30 quotient and binary voltage construction to Z1.

The Z2 action is free with fifteen four-state vertex orbits. It has no edge
inversions and satisfies the local covering law. Exact subgroup equality
with the previously certified normal V4 transfers the exact labeled
G15 quotient and native V4 voltage construction to Z2.

The induced quotient by `Z2/Z1` agrees with the direct Z2 quotient, giving
the exact factorization

`G60 -> G30 -> G15`.

The binary holonomy image is all of C2. The V4 holonomy image is all of V4.
The V4 voltage retains the exact certificate 033 identity-label,
identity-basis, zero-gauge match.

## Earned theorem

The raw native graph determines its full automorphism group. The first two
terms of the upper-central series of that group are exactly the previously
recovered normal C2 and V4 receipt actions. Their orbit quotients reproduce
the exact G60 -> G30 -> G15 tower.

## Boundary

The blind spectrum still contains 22 cover-admissible conjugacy classes.
The theorem does not say that the raw graph uniquely selects every receipt
action. It says that a canonical group-theoretic filtration selects one
nested receipt tower from that spectrum.

No manuscript was changed. No orientation, geometry, electron, spin,
spacetime, force, energy, quantum, or physics claim is made.
