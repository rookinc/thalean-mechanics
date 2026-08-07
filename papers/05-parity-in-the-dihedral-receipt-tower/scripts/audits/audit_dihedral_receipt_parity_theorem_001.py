from __future__ import annotations

import json
from collections import deque
from pathlib import Path


TARGET = Path(__file__).resolve().parents[2]
ARTIFACT = TARGET / "artifacts/json/dihedral_receipt_parity_theorem_001.v1.json"
MIN_N = 3
MAX_N = 32


Permutation = tuple[int, ...]


def compose(p: Permutation, q: Permutation) -> Permutation:
    return tuple(p[q[x]] for x in range(len(p)))


def inverse(p: Permutation) -> Permutation:
    out = [0] * len(p)
    for i, value in enumerate(p):
        out[value] = i
    return tuple(out)


def power(p: Permutation, exponent: int) -> Permutation:
    result = tuple(range(len(p)))
    base = p
    e = exponent
    while e:
        if e & 1:
            result = compose(result, base)
        base = compose(base, base)
        e >>= 1
    return result


def order(p: Permutation) -> int:
    identity = tuple(range(len(p)))
    current = identity
    for k in range(1, len(p) * 2 + 1):
        current = compose(current, p)
        if current == identity:
            return k
    raise ValueError("order bound exceeded")


def generated_group(generators: tuple[Permutation, ...]) -> set[Permutation]:
    identity = tuple(range(len(generators[0])))
    found = {identity}
    queue = deque([identity])
    while queue:
        current = queue.popleft()
        for generator in generators:
            candidate = compose(current, generator)
            if candidate not in found:
                found.add(candidate)
                queue.append(candidate)
    return found


def add_v4(x: tuple[int, int], y: tuple[int, int]) -> tuple[int, int]:
    return (x[0] ^ y[0], x[1] ^ y[1])


def main() -> None:
    artifact = json.loads(ARTIFACT.read_text())
    assert artifact["audit_pass"] is True
    assert artifact["audit_range"] == {
        "minimum_n": MIN_N,
        "maximum_n": MAX_N,
        "full_group_enumeration_for_each_n": True,
    }

    rows: list[dict[str, object]] = []
    global_failures: list[dict[str, object]] = []
    expected_even_count = len([n for n in range(MIN_N, MAX_N + 1) if n % 2 == 0])
    expected_odd_count = len([n for n in range(MIN_N, MAX_N + 1) if n % 2 == 1])

    print("== FINITE DIHEDRAL PARITY CENSUS ==")
    span = MAX_N - MIN_N + 1
    for index, n in enumerate(range(MIN_N, MAX_N + 1), start=1):
        modulus = 2 * n
        identity = tuple(range(modulus))
        H = tuple((x + 1) % modulus for x in range(modulus))
        A = tuple((-x) % modulus for x in range(modulus))
        B = tuple((-x - 1) % modulus for x in range(modulus))
        H_inverse = inverse(H)
        BA = compose(B, A)
        commutator = compose(compose(compose(A, B), A), B)
        c = power(H, 2)
        tau = power(H, n)

        group = generated_group((A, B))
        rotations = {power(H, k) for k in range(modulus)}
        reflections = {compose(A, power(H, k)) for k in range(modulus)}
        normal_forms = rotations | reflections
        c_subgroup = {power(c, k) for k in range(n)}
        tau_subgroup = {identity, tau}

        q: dict[Permutation, tuple[int, int]] = {}
        quotient_conflicts: list[dict[str, object]] = []
        for k in range(modulus):
            p = k % 2
            candidates = (
                (power(H, k), (p, p), f"H^{k}"),
                (compose(A, power(H, k)), (1 ^ p, p), f"A H^{k}"),
            )
            for element, image, label in candidates:
                if element in q and q[element] != image:
                    quotient_conflicts.append(
                        {"label": label, "old": q[element], "new": image}
                    )
                q[element] = image

        homomorphism_failures = 0
        group_list = list(group)
        for left in group_list:
            for right in group_list:
                if q[compose(left, right)] != add_v4(q[left], q[right]):
                    homomorphism_failures += 1

        kernel = {element for element, image in q.items() if image == (0, 0)}
        even = n % 2 == 0
        if even:
            parity_formula = power(c, n // 2) == tau
            odd_split = None
            reconstruction = None
        else:
            parity_formula = tau not in c_subgroup
            odd_split = (
                c_subgroup & tau_subgroup == {identity}
                and {compose(x, y) for x in c_subgroup for y in tau_subgroup}
                == rotations
            )
            reconstruction = compose(power(c, (n + 1) // 2), tau) == H

        checks = {
            "A_involution": order(A) == 2,
            "B_involution": order(B) == 2,
            "H_equals_AB": compose(A, B) == H,
            "H_order_2n": order(H) == modulus,
            "H_inverse_equals_BA": H_inverse == BA,
            "A_conjugates_H_to_inverse": compose(compose(A, H), A) == H_inverse,
            "generated_group_order_4n": len(group) == 4 * n,
            "normal_forms_exact": len(normal_forms) == 4 * n and normal_forms == group,
            "rotation_reflection_cosets_disjoint": not rotations & reflections,
            "commutator_equals_H2": commutator == c,
            "commutator_order_n": order(c) == n,
            "tau_equals_Hn": tau == power(H, n),
            "tau_order_two": order(tau) == 2,
            "tau_central": all(
                compose(tau, generator) == compose(generator, tau)
                for generator in (A, B)
            ),
            "quotient_conflict_free": not quotient_conflicts,
            "quotient_defined_on_full_group": set(q) == group,
            "quotient_homomorphism": homomorphism_failures == 0,
            "quotient_surjective": set(q.values())
            == {(0, 0), (1, 0), (0, 1), (1, 1)},
            "quotient_kernel_equals_c_subgroup": kernel == c_subgroup,
            "tau_membership_matches_parity": (tau in c_subgroup) == even,
            "tau_quotient_image_matches_parity": q[tau]
            == ((0, 0) if even else (1, 1)),
            "parity_formula_exact": parity_formula,
            "odd_direct_product_exact": odd_split is True if not even else True,
            "odd_H_reconstruction_exact": reconstruction is True if not even else True,
        }
        failed_checks = [name for name, passed in checks.items() if not passed]
        row = {
            "n": n,
            "parity": "even" if even else "odd",
            "H_order": order(H),
            "generated_group_order": len(group),
            "commutator_order": order(c),
            "tau_in_commutator_subgroup": tau in c_subgroup,
            "tau_encounter_image": list(q[tau]),
            "quotient_kernel_order": len(kernel),
            "failed_checks": failed_checks,
        }
        rows.append(row)
        if failed_checks:
            global_failures.append(row)
        print(
            f"PROGRESS: [{index}/{span}] n={n} parity={row['parity']} "
            f"group_order={len(group)} failures={len(failed_checks)}"
        )

    print("")
    print("== PARITY ROWS ==")
    for row in rows:
        print("PARITY_ROW:", json.dumps(row, sort_keys=True, separators=(",", ":")))

    even_rows = [row for row in rows if row["parity"] == "even"]
    odd_rows = [row for row in rows if row["parity"] == "odd"]
    theorem_checks = {
        "full_n_range_tested": len(rows) == span,
        "even_row_count_exact": len(even_rows) == expected_even_count,
        "odd_row_count_exact": len(odd_rows) == expected_odd_count,
        "all_generated_groups_dihedral_order_4n": all(
            row["generated_group_order"] == 4 * row["n"] for row in rows
        ),
        "all_commutator_orders_equal_n": all(
            row["commutator_order"] == row["n"] for row in rows
        ),
        "tau_in_commutator_exactly_for_even_n": all(
            row["tau_in_commutator_subgroup"] == (row["parity"] == "even")
            for row in rows
        ),
        "tau_hidden_by_encounter_exactly_for_even_n": all(
            row["tau_encounter_image"]
            == ([0, 0] if row["parity"] == "even" else [1, 1])
            for row in rows
        ),
        "all_row_checks_pass": not global_failures,
        "artifact_boundary_preserved": artifact["boundaries"]["physics_claim"] is False,
    }

    print("")
    print("== THEOREM CHECKS ==")
    for name, passed in theorem_checks.items():
        print(f"CHECK_{name.upper()}:", str(passed).lower())
    failed = [name for name, passed in theorem_checks.items() if not passed]
    assert not failed, failed
    assert not global_failures, global_failures[:3]

    print("")
    print("AUDIT_PASS: true")
    print("N_RANGE:", [MIN_N, MAX_N])
    print("TESTED_N_COUNT:", len(rows))
    print("EVEN_N_COUNT:", len(even_rows))
    print("ODD_N_COUNT:", len(odd_rows))
    print("EVEN_LAW: tau=c^(n/2)")
    print("ODD_LAW: <H>=<c>x<tau> and H=c^((n+1)/2)tau")
    print("THEOREM_PASS: true")
    print("VERDICT:", artifact["verdict"])
    print("KEEPER:", artifact["keeper"])


if __name__ == "__main__":
    main()

