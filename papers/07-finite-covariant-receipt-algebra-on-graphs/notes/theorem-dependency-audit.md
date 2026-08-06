# Theorem dependency audit

## Premises

Let `X` be a finite connected graph, `R` a finite group, and `alpha` an
assignment to oriented edges satisfying `alpha(reverse(e))=alpha(e)^-1`.
The regular lift has vertex set `V(X) x R` and sends an oriented edge
`e:u->v` from `(u,x)` to `(v,x alpha(e))`.

## Dependency chain

1. Regular covariance forces right multiplication on each lifted edge.
2. Vertex gauge acts by
   `alpha^g(e)=g(u)^-1 alpha(e) g(v)`.
3. Path receipts telescope under gauge.
4. A spanning-tree gauge makes every tree voltage trivial.
5. Cotree edge receipts freely specify `pi_1(X) -> R`.
6. Residual constant gauge simultaneously conjugates the representation.
7. Closed walks based at the root reach exactly the subgroup `H=im(rho)`.
8. Components are indexed by left cosets of `H` in `R`.

## Independence checks

- Root changes conjugate the holonomy image.
- Spanning-tree changes alter generators but not the represented gauge class.
- Component number depends on the subgroup image, not on a chosen generating
  set.
- The cycle theorem follows without additional assumptions.

## Boundary

The theorem begins after the raw graph, fiber action, and edge receipts have
been supplied. Deriving those inputs is a separate binding theorem.
