# Finite Covariant Receipt Algebra on Graphs

Paper 7 develops the graph-general form of finite receipt holonomy.

For a connected finite graph `X`, a finite receipt group `R`, and an
inverse-compatible voltage assignment on oriented edges, it proves that:

- gauge classes are classified by conjugacy classes of representations
  `pi_1(X) -> R`;
- the image of the holonomy representation controls the connected components
  of the lifted graph;
- the lift is connected exactly when the holonomy image is all of `R`;
- the cycle-multiplication theorem is the rank-one specialization.

The project contains a source-only LaTeX manuscript, an executable finite
census, a theorem artifact, and a raw-graph binding certificate schema.

No physical realization is claimed.

## Verification

```text
python scripts/audits/audit_finite_covariant_receipt_algebra_on_graphs_001.py
bash scripts/zipit.sh
```

The packaging script does not compile LaTeX.
