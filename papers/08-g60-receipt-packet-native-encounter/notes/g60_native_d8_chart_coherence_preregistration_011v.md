# G60 native D8 chart-coherence preregistration 011v

## Question

The locked 011u result reconstructs ten native transposition-local D8
subgroups and eight isomorphism charts from each selected local D8
presentation to each native subgroup.

The next test asks whether the full automorphism group admits a strict
equivariant choice of one chart over each of the ten native subgroups,
or whether a residual chart gauge obstructs such a section.

## Registered action

For a chart phi:E->H and g in A, the proposed action is:

g.phi = conjugation_by_g composed_with phi

Its target is gHg^-1. The base action is conjugation on the ten native
D8 subgroups, equivalently the natural S5 action on transpositions.

The chart maps are not stored in the 011u JSON and must be reconstructed
from the frozen 011u computation.

## Prediction

For each selected cocycle presentation:

- there are 80 charts
- the ten native subgroups form one base orbit
- each base stabilizer has order 48
- each chart stabilizer has order 12
- the 80 charts split into two orbits of size 40
- the normalizer acts on each eight-chart fiber through Inner(D8)
- the fiber splits into two four-chart orbits
- the residual chart gauge is Out(D8)=C2
- no strict equivariant one-chart-per-subgroup section exists

Across both presentations the predicted orbit profile is four orbits
of size forty. The two gauge-related presentations are predicted to
give equivalent chart bundles.

The locked alpha_1 character and q-axis signature are predicted to be
constant across both outer chart orbits. They therefore do not select
an absolute chart.

## Interpretation boundary

A positive result would classify a gauge-covariant native D8 chart
bundle while proving that no strict global chart is selected. It would
not yet construct a native update law or mechanics state cell.

This test does not identify the local central side with the 011o
orientation sheet, select an orientation, mutate the manuscript, or
make a geometry or physical claim.
