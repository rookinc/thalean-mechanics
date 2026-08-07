# G60 gauge-covariant update preregistration 011z

## Question

Does the locked native D8 chart bundle support a chart-independent,
instruction-parametrized update operation even though it does not select an
absolute chart orbit?

## Candidate operation

For a local D8 state `x`, supplied instruction `u`, and chart `phi`, test

`phi(xu) = phi(x) phi(u)`.

The chart, state, and instruction are transformed together by `Aut(D8)`.
The proposed quotient object is the multiplication graph, not a selected
chart and not an autonomous evolution rule.

## Frozen predictions

- Two gauge-related D8 presentations.
- Ten native D8 subgroups per presentation.
- Eight charts per subgroup.
- Sixty-four state/instruction rows per chart.
- 5,120 chart-decorated rows per presentation.
- A free order-eight gauge action producing 640 quotient rows.
- Exactly sixty-four quotient rows over each native subgroup.
- Quotient evaluation is well defined and bijective onto native subgroup
  multiplication.
- Both cocycle presentations produce the same native quotient relation.
- All four presentation gauge maps intertwine the relation.
- The local element orbit profile under `Aut(D8)` is `1,1,2,4`.
- The q-axis has two order-four instruction candidates and no invariant
  singleton.

## Logical boundary

A ternary multiplication graph answers:

`state + supplied instruction -> next state`.

It does not answer:

`state -> uniquely selected next state`.

Success therefore constructs only a gauge-covariant,
instruction-parametrized local update operation. It does not select an
absolute chart, an autonomous noncentral instruction, an orientation, a
mechanics state cell, or a physical direction. The order-four instruction
pair is not identified with the locked outer-C2 chart torsor unless a later
test proves that identification.
