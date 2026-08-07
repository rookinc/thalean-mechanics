# G60 root stabilizer action-type census 011k

## Status

This packet freezes the complete stabilizer census performed after the
preregistered 011j action-type test.

The computation used the locked head:

`ea06a19 Preregister G60 root stabilizer action type`

All five declared authority hashes matched.

## Exact result

The root and ordered-duad stabilizers have the same abstract element-order
profile:

`S3 = {1^1, 2^3, 3^2}`.

They are nevertheless different embeddings in the canonical five-point
`S5` action.

The ordered-duad stabilizer has:

- order 6 in the five-point image;
- cycle types `1`, three transpositions, and two 3-cycles;
- parity profile `even: 3, odd: 3`;
- orbit-size profile `1+1+3`.

The root stabilizer has:

- order 6 in the five-point image;
- cycle types `1`, three double transpositions, and two 3-cycles;
- parity profile `even: 6`;
- orbit-size profile `2+3`.

The two stabilizer embeddings are not conjugate in `S5`.

There are ten distinct root-stabilizer images, ten distinct
ordered-duad-stabilizer images, and ten even unordered-duad setwise
stabilizers. Under the unique bridge from unordered duads to inverse-root
pairs, the root-stabilizer family equals the even-duad-stabilizer family
exactly.

The exact-match failure count is zero in the canonical order-240 subgroup
`N` and zero across both native `S5` complements.

## Earned statement

The orientation failure is an embedding obstruction, not an abstract-group
obstruction. The root layer naturally carries the all-even setwise
stabilizer of an unordered duad. It does not carry the mixed-parity
pointwise stabilizer associated with an ordered duad.

## Boundary

This packet classifies the stabilizer embedding only.

It does not construct a replacement source `A`-set, select an orientation,
identify a minimal directional datum, mutate the manuscript, derive
geometry, or make a physical claim.
