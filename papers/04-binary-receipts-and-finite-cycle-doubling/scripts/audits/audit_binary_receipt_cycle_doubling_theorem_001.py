from __future__ import annotations

import itertools
import json
from pathlib import Path


TARGET = Path(__file__).resolve().parents[2]
ARTIFACT = TARGET / "artifacts/json/binary_receipt_cycle_doubling_theorem_001.v1.json"
MIN_N = 3
MAX_N = 12


def lifted_successor(n: int, voltage: tuple[int, ...]) -> list[int]:
    permutation = [0] * (2 * n)
    for i in range(n):
        for sheet in range(2):
            source = 2 * i + sheet
            target = 2 * ((i + 1) % n) + ((sheet + voltage[i]) % 2)
            permutation[source] = target
    return permutation


def cycle_profile(permutation: list[int]) -> list[int]:
    seen: set[int] = set()
    lengths: list[int] = []
    for start in range(len(permutation)):
        if start in seen:
            continue
        current = start
        length = 0
        while current not in seen:
            seen.add(current)
            current = permutation[current]
            length += 1
        lengths.append(length)
    return sorted(lengths)


def canonical_gauge(voltage: tuple[int, ...]) -> tuple[int, ...]:
    n = len(voltage)
    gauge = [0] * n
    for i in range(n - 1):
        gauge[i + 1] = gauge[i] ^ voltage[i]
    transformed = tuple(
        voltage[i] ^ gauge[i] ^ gauge[(i + 1) % n]
        for i in range(n)
    )
    return transformed


def main() -> None:
    artifact = json.loads(ARTIFACT.read_text())
    assert artifact["audit_pass"] is True
    assert artifact["audit_range"] == {
        "minimum_n": MIN_N,
        "maximum_n": MAX_N,
        "exhaustive_within_each_n": True,
    }

    total_assignments = 0
    total_failures: list[dict[str, object]] = []
    rows: list[dict[str, object]] = []

    span = MAX_N - MIN_N + 1
    print("== EXHAUSTIVE CYCLE CENSUS ==")
    for index, n in enumerate(range(MIN_N, MAX_N + 1), start=1):
        assignments = list(itertools.product((0, 1), repeat=n))
        holonomy_counts = {0: 0, 1: 0}
        canonical_classes: set[tuple[int, ...]] = set()
        profile_counts: dict[tuple[int, ...], int] = {}
        order_counts: dict[int, int] = {}
        failures: list[dict[str, object]] = []

        for voltage in assignments:
            holonomy = sum(voltage) % 2
            holonomy_counts[holonomy] += 1
            canonical = canonical_gauge(voltage)
            canonical_classes.add(canonical)

            permutation = lifted_successor(n, voltage)
            profile = tuple(cycle_profile(permutation))
            profile_counts[profile] = profile_counts.get(profile, 0) + 1
            lifted_order = max(profile)
            order_counts[lifted_order] = order_counts.get(lifted_order, 0) + 1

            expected_canonical = (0,) * (n - 1) + (holonomy,)
            expected_profile = (n, n) if holonomy == 0 else (2 * n,)
            expected_order = n if holonomy == 0 else 2 * n
            if (
                canonical != expected_canonical
                or profile != expected_profile
                or lifted_order != expected_order
            ):
                failures.append(
                    {
                        "voltage": list(voltage),
                        "holonomy": holonomy,
                        "canonical": list(canonical),
                        "profile": list(profile),
                        "lifted_order": lifted_order,
                    }
                )

        expected_half = 2 ** (n - 1)
        checks = {
            "assignment_count_exact": len(assignments) == 2**n,
            "holonomy_classes_balanced": holonomy_counts == {0: expected_half, 1: expected_half},
            "canonical_gauge_class_count_two": len(canonical_classes) == 2,
            "canonical_representatives_exact": canonical_classes
            == {(0,) * n, (0,) * (n - 1) + (1,)},
            "cycle_profiles_exact": profile_counts
            == {(n, n): expected_half, (2 * n,): expected_half},
            "lifted_orders_exact": order_counts
            == {n: expected_half, 2 * n: expected_half},
            "row_failure_count_zero": not failures,
        }
        failed_checks = [name for name, passed in checks.items() if not passed]
        row = {
            "n": n,
            "assignment_count": len(assignments),
            "holonomy_counts": holonomy_counts,
            "gauge_class_count": len(canonical_classes),
            "cycle_profile_counts": {str(list(k)): v for k, v in profile_counts.items()},
            "lifted_order_counts": order_counts,
            "failed_checks": failed_checks,
        }
        rows.append(row)
        total_assignments += len(assignments)
        total_failures.extend(failures)
        if failed_checks:
            total_failures.append({"n": n, "failed_checks": failed_checks})
        print(
            f"PROGRESS: [{index}/{span}] n={n} assignments={len(assignments)} "
            f"gauge_classes={len(canonical_classes)} failures={len(failures) + len(failed_checks)}"
        )

    print("")
    print("== CENSUS ROWS ==")
    for row in rows:
        print("CYCLE_ROW:", json.dumps(row, sort_keys=True, separators=(",", ":")))

    print("")
    print("== THEOREM CHECKS ==")
    theorem_checks = {
        "all_cycle_sizes_exhausted": len(rows) == span,
        "all_voltage_assignments_exhausted": total_assignments
        == sum(2**n for n in range(MIN_N, MAX_N + 1)),
        "exactly_two_gauge_classes_for_every_n": all(row["gauge_class_count"] == 2 for row in rows),
        "trivial_holonomy_gives_two_Cn_components": not total_failures,
        "nontrivial_holonomy_gives_one_C2n_component": not total_failures,
        "connectedness_equivalent_to_nontrivial_receipt": not total_failures,
        "nontrivial_receipt_forces_order_2n": not total_failures,
        "artifact_boundary_preserved": artifact["boundaries"]["physics_claim"] is False,
    }
    for name, passed in theorem_checks.items():
        print(f"CHECK_{name.upper()}:", str(passed).lower())

    failed = [name for name, passed in theorem_checks.items() if not passed]
    assert not failed, failed
    assert not total_failures, total_failures[:5]

    print("")
    print("AUDIT_PASS: true")
    print("CYCLE_SIZE_RANGE:", [MIN_N, MAX_N])
    print("TOTAL_VOLTAGE_ASSIGNMENT_COUNT:", total_assignments)
    print("GAUGE_CLASS_COUNT_PER_CYCLE: 2")
    print("TRIVIAL_CLASS_PROFILE: [n,n]")
    print("NONTRIVIAL_CLASS_PROFILE: [2n]")
    print("THEOREM_PASS: true")
    print("VERDICT:", artifact["verdict"])
    print("KEEPER:", artifact["keeper"])


if __name__ == "__main__":
    main()

