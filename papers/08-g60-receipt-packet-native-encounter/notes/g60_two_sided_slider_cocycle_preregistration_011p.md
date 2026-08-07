# G60 two-sided slider cocycle preregistration 011p

## Question

Can the native four-state V4 register be lifted to a two-sided
eight-state register that remembers the difference between the routes
A then B and B then A?

The visible V4 state identifies ab with ba. The proposed side bit is a
central C2 coordinate. Multiplication is declared as

    (x,e)*(y,f) = (xy, e+f+omega(x,y)) mod 2.

The two routes have the same visible endpoint ab. They occupy opposite
sides exactly when

    omega(a,b) + omega(b,a) = 1 mod 2.

## Frozen prediction

The census will enumerate all 512 normalized binary two-cochains on V4.

The predicted result is:

- 16 normalized two-cocycles;
- 2 distinct normalized two-coboundaries;
- 8 cohomology classes;
- 2 normalized cocycle representatives per class;
- class profile 1 C2^3, 3 C4xC2, 3 D8, and 1 Q8;
- 4 route-separating nonabelian classes represented by 8 cocycles.

The native authority fixes a and exchanges b with ab. The prediction is
that adding the native D8 order profile and the square signature

    q(a)=1, q(b)=0, q(ab)=0

selects exactly one D8 cohomology class. That class should distinguish
AB from BA by the central side bit. Its two normalized representatives
should be gauge-related; no unique representative is predicted.

## Native comparison authorities

The locked native data already proves:

- the four-state register is V4;
- the local square structure group is D8;
- its center has order two;
- its element-order profile is 1,5,2 for orders 1,2,4;
- the carrier axis a is fixed;
- b and ab are exchanged;
- every K5 triangle has nontrivial C2 holonomy;
- no global b/ab axis trivialization exists.

Those facts constrain the new central-extension census but do not
pre-answer whether the central side records AB versus BA.

## Boundary

This is a finite central-extension and path-order test.

It does not identify the local central side with the 011o orientation
sheet because no canonical local-to-global side map has been defined.
It does not construct a native update law or establish a mechanics
state cell. It makes no geometric, physical-direction, or physical
claim. The manuscript is unchanged.
