# Theorem dependency audit

The main theorem requires:

1. an integer `n >= 3`;
2. two involutions `A` and `B`;
3. the product `H=AB` having exact order `2n`.

Everything else is derived:

- inversion covariance follows from `AHA=H_inverse`;
- the dihedral normal forms are `H^k` and `A H^k`;
- the commutator is `H^2`;
- the unique lifted half-cycle involution is `H^n`;
- membership of `H^n` in `<H^2>` is equivalent to evenness of `n`;
- the encounter quotient is the abelianization `C2 x C2`;
- quotient visibility of `H^n` is determined by the parity of `n`.

The proof does not assume Paper 4's binary-lift construction. That result
explains one source of an order-`2n` generator, but is not needed to prove
the parity theorem once such a generator is given.

