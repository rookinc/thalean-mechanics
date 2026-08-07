# G60 full-A orientation character-extension census 011o

## Result

The parity-twisted twenty-object N-action has exactly two extensions to
the full automorphism group A:

- alpha_0 = p
- alpha_1 = p+n

Here p is the parity character of the canonical five-point S5 image and
n is the index-two membership character of N in A.

Both extensions define valid transitive twenty-object A-actions.
They are not equivalent as orientation carriers.

The p-only action has pointwise kernel

    V4 = {0, 65, 124, 326}

and admits no A-equivariant bijection to the twenty orientation roots.

The p+n action has pointwise kernel

    Z1 = {0, 326}

and admits exactly two A-equivariant bijections to the orientation
roots. Their map hashes are:

- 782dbcb9dae045cfc5dadd1b81f51895e447e981491263e09514c9077dfe1728
- bb61e5018270d8954e8115bb9c1fbbcfb07f360ba307c451cb16103ef7336c01

These are exactly the two maps frozen in census 011m over N.

## Character census

The complete binary-character census found four valid characters of A.
Exactly two restrict to the locked N-sheet character. They are p and
p+n. The homomorphism failure counts for p, n, alpha_0, and alpha_1 are
all zero.

The residual elements 65 and 124 lie outside N. Under alpha_0 they fix
the source sheets, leaving V4 in the pointwise kernel. Under alpha_1
they exchange the source sheets, reducing the kernel to Z1 and matching
their inversion action on the roots.

## Reversal and anchor

Global source-sheet reversal and root inversion exchange the same two
bridges. Without an anchor, both bridges remain. Each of the forty
compatible source-root anchors selects exactly one bridge.

The native structure therefore constructs the orientation double cover
and its full-A action, but does not select one global orientation by
itself.

## Provenance

The successful candidate was promoted without recomputation.

- candidate JSON SHA256:
  4a33590b9585a782ea4ae073afb0b778f39c4323e70ff606ab3d12ba66099f21
- raw run receipt SHA256:
  83e5c75e98f4c4c676cbdac9ef522e516604bac8520f3429563c8f1d7c2bdc28
- computation script SHA256:
  98356ac2b2b0f19b6d8ec6d8f79056877d63b3d0981e4140ac966dd6805cc695

An earlier generated draft failed syntax validation before the census.
It produced no candidate JSON, was not used for the successful run, and
is not promoted. The permanent compute script is byte-identical to the
successful temporary compute script.

## Boundary

This is a finite group-action and character-extension theorem.

It identifies the unique extension character supporting the full-A
bridge and proves bounded one-bit anchor sufficiency within this
constructed source action.

It does not select an orientation without an anchor. It makes no global
minimality claim, geometric claim, physical-direction claim, or
physical claim. The manuscript and existing polish pile are unchanged.
