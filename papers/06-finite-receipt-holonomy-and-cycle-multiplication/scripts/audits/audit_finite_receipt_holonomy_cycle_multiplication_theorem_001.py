#!/usr/bin/env python3
from __future__ import annotations

import itertools
from dataclasses import dataclass


@dataclass(frozen=True)
class FiniteGroup:
    name: str
    elements: tuple[object, ...]
    mul: tuple[tuple[int, ...], ...]
    inv: tuple[int, ...]

    @property
    def order(self) -> int:
        return len(self.elements)

    def product(self, values: tuple[int, ...] | list[int]) -> int:
        out = 0
        for value in values:
            out = self.mul[out][value]
        return out

    def element_order(self, value: int) -> int:
        out = 0
        for exponent in range(1, self.order + 1):
            out = self.mul[out][value]
            if out == 0:
                return exponent
        raise AssertionError("element order exceeded group order")

    def conjugacy_class(self, value: int) -> frozenset[int]:
        return frozenset(
            self.mul[self.mul[self.inv[t]][value]][t]
            for t in range(self.order)
        )


def table_group(name: str, elements: list[object], operation) -> FiniteGroup:
    identity = elements.index(operation(elements[0], elements[0]))
    if identity != 0:
        raise AssertionError(f"{name}: identity must be listed first")
    index = {value: i for i, value in enumerate(elements)}
    mul = tuple(
        tuple(index[operation(a, b)] for b in elements)
        for a in elements
    )
    inv = []
    for i in range(len(elements)):
        matches = [j for j in range(len(elements)) if mul[i][j] == 0 and mul[j][i] == 0]
        if len(matches) != 1:
            raise AssertionError(f"{name}: inverse failure for {i}")
        inv.append(matches[0])
    return FiniteGroup(name, tuple(elements), mul, tuple(inv))


def cyclic_group(order: int) -> FiniteGroup:
    return table_group(f"C{order}", list(range(order)), lambda a, b: (a + b) % order)


def klein_four() -> FiniteGroup:
    elements = [(0, 0), (1, 0), (0, 1), (1, 1)]
    return table_group("V4", elements, lambda a, b: (a[0] ^ b[0], a[1] ^ b[1]))


def symmetric_three() -> FiniteGroup:
    identity = (0, 1, 2)
    elements = [identity] + [p for p in itertools.permutations(range(3)) if p != identity]
    return table_group("S3", elements, lambda p, q: tuple(p[q[i]] for i in range(3)))


def dihedral_eight() -> FiniteGroup:
    elements = [(0, 0)] + [(k, e) for e in range(2) for k in range(4) if (k, e) != (0, 0)]

    def operation(a, b):
        k, e = a
        ell, f = b
        signed_ell = ell if e == 0 else -ell
        return ((k + signed_ell) % 4, e ^ f)

    return table_group("D8", elements, operation)


def lifted_cycle_profile(group: FiniteGroup, n: int, voltage: tuple[int, ...]) -> tuple[int, ...]:
    state_count = n * group.order

    def successor(state: int) -> int:
        i, receipt = divmod(state, group.order)
        return ((i + 1) % n) * group.order + group.mul[receipt][voltage[i]]

    seen: set[int] = set()
    lengths = []
    for start in range(state_count):
        if start in seen:
            continue
        cursor = start
        length = 0
        while cursor not in seen:
            seen.add(cursor)
            length += 1
            cursor = successor(cursor)
        lengths.append(length)
    return tuple(sorted(lengths))


def normalize_voltage(group: FiniteGroup, voltage: tuple[int, ...]) -> tuple[int, ...]:
    n = len(voltage)
    gauge = [0] * n
    for i in range(n - 1):
        gauge[i + 1] = group.mul[group.inv[voltage[i]]][gauge[i]]
    return tuple(
        group.mul[group.mul[group.inv[gauge[i]]][voltage[i]]][gauge[(i + 1) % n]]
        for i in range(n)
    )


def canonical_conjugate(group: FiniteGroup, holonomy: int) -> tuple[int, int]:
    representative = min(group.conjugacy_class(holonomy))
    witnesses = [
        t for t in range(group.order)
        if group.mul[group.mul[group.inv[t]][holonomy]][t] == representative
    ]
    if not witnesses:
        raise AssertionError("conjugating witness not found")
    return representative, witnesses[0]


def main() -> None:
    print("OUT ==")
    print("PACKET: finite_receipt_holonomy_cycle_multiplication_theorem_audit_001")
    print("MODE: read-only exhaustive finite-group voltage audit")
    print("REPOSITORY_MUTATION: none")
    print()

    cases = [
        (cyclic_group(2), range(3, 9)),
        (cyclic_group(3), range(3, 7)),
        (cyclic_group(4), range(3, 6)),
        (cyclic_group(5), range(3, 6)),
        (cyclic_group(6), range(3, 5)),
        (klein_four(), range(3, 6)),
        (symmetric_three(), range(3, 6)),
        (dihedral_eight(), range(3, 5)),
    ]
    work = [(group, n) for group, ns in cases for n in ns]

    assignment_total = 0
    normalization_failures = 0
    canonical_gauge_failures = 0
    profile_failures = 0
    connectedness_failures = 0
    cyclicity_failures = 0
    case_rows = []

    print("== EXHAUSTIVE CASE PROGRESS ==")
    for case_index, (group, n) in enumerate(work, start=1):
        assignment_count = group.order ** n
        class_profiles: dict[int, set[tuple[int, ...]]] = {}
        connected_count = 0
        for voltage in itertools.product(range(group.order), repeat=n):
            assignment_total += 1
            holonomy = group.product(voltage)
            holonomy_order = group.element_order(holonomy)
            normalized = normalize_voltage(group, voltage)
            expected_normalized = (0,) * (n - 1) + (holonomy,)
            if normalized != expected_normalized:
                normalization_failures += 1

            representative, witness = canonical_conjugate(group, holonomy)
            canonical = tuple(
                group.mul[group.mul[group.inv[witness]][value]][witness]
                for value in normalized
            )
            if canonical != (0,) * (n - 1) + (representative,):
                canonical_gauge_failures += 1

            actual_profile = lifted_cycle_profile(group, n, voltage)
            expected_profile = tuple([n * holonomy_order] * (group.order // holonomy_order))
            if actual_profile != expected_profile:
                profile_failures += 1

            actually_connected = len(actual_profile) == 1
            expected_connected = holonomy_order == group.order
            if actually_connected != expected_connected:
                connectedness_failures += 1
            if actually_connected:
                connected_count += 1
                generated = {group.product([holonomy] * power) for power in range(group.order)}
                if len(generated) != group.order:
                    cyclicity_failures += 1

            class_profiles.setdefault(representative, set()).add(actual_profile)

        case_rows.append(
            {
                "group": group.name,
                "n": n,
                "assignments": assignment_count,
                "conjugacy_classes": len(class_profiles),
                "connected_assignments": connected_count,
                "profiles": sorted({profile for profiles in class_profiles.values() for profile in profiles}),
            }
        )
        print(
            f"PROGRESS: [{case_index}/{len(work)}] group={group.name} n={n} "
            f"assignments={assignment_count} failures="
            f"{normalization_failures + canonical_gauge_failures + profile_failures + connectedness_failures + cyclicity_failures}"
        )

    print()
    print("== CASE CENSUS ==")
    for row in case_rows:
        print("CASE:", row)

    binary_failures = 0
    for n in range(3, 13):
        group = cyclic_group(2)
        voltage = (0,) * (n - 1) + (1,)
        if lifted_cycle_profile(group, n, voltage) != (2 * n,):
            binary_failures += 1

    cyclic_generator_failures = 0
    for m in range(2, 13):
        group = cyclic_group(m)
        for n in range(3, 9):
            voltage = (0,) * (n - 1) + (1,)
            if lifted_cycle_profile(group, n, voltage) != (n * m,):
                cyclic_generator_failures += 1

    noncyclic_connected_failures = 0
    for group in (klein_four(), symmetric_three(), dihedral_eight()):
        if any(group.element_order(element) == group.order for element in range(group.order)):
            noncyclic_connected_failures += 1

    failed_checks = {
        "normalization": normalization_failures,
        "canonical_gauge": canonical_gauge_failures,
        "cycle_profile": profile_failures,
        "connectedness": connectedness_failures,
        "connected_implies_cyclic": cyclicity_failures,
        "binary_corollary": binary_failures,
        "cyclic_generator_corollary": cyclic_generator_failures,
        "noncyclic_connectedness": noncyclic_connected_failures,
    }

    print()
    print("== THEOREM CHECKS ==")
    print("RECEIPT_GROUP_COUNT:", len(cases))
    print("GROUP_CYCLE_CASE_COUNT:", len(work))
    print("VOLTAGE_ASSIGNMENT_COUNT:", assignment_total)
    print("NORMALIZATION_FAILURE_COUNT:", normalization_failures)
    print("CANONICAL_GAUGE_FAILURE_COUNT:", canonical_gauge_failures)
    print("CYCLE_PROFILE_FAILURE_COUNT:", profile_failures)
    print("CONNECTEDNESS_FAILURE_COUNT:", connectedness_failures)
    print("CONNECTED_IMPLIES_CYCLIC_FAILURE_COUNT:", cyclicity_failures)
    print("BINARY_COROLLARY_FAILURE_COUNT:", binary_failures)
    print("CYCLIC_GENERATOR_COROLLARY_FAILURE_COUNT:", cyclic_generator_failures)
    print("NONCYCLIC_CONNECTEDNESS_FAILURE_COUNT:", noncyclic_connected_failures)
    print("CHECK_GAUGE_NORMAL_FORM_EXACT:", str(normalization_failures == 0).lower())
    print("CHECK_CONJUGACY_CLASSIFICATION_EXACT:", str(canonical_gauge_failures == 0).lower())
    print("CHECK_COMPONENT_COUNT_AND_LENGTH_EXACT:", str(profile_failures == 0).lower())
    print("CHECK_CONNECTED_IFF_HOLONOMY_HAS_FULL_ORDER:", str(connectedness_failures == 0).lower())
    print("CHECK_CONNECTED_LIFT_FORCES_CYCLIC_RECEIPT_GROUP:", str(cyclicity_failures == 0).lower())
    print("CHECK_BINARY_NONTRIVIAL_RECEIPT_DOUBLES_CYCLE:", str(binary_failures == 0).lower())
    print("CHECK_CYCLIC_GENERATOR_MULTIPLIES_CYCLE:", str(cyclic_generator_failures == 0).lower())
    print("FAILED_CHECKS:", [key for key, count in failed_checks.items() if count])

    theorem_pass = all(count == 0 for count in failed_checks.values())
    print()
    print("THEOREM_PASS:", str(theorem_pass).lower())
    print(
        "FINAL_CLASSIFICATION:",
        "finite_regular_cycle_lifts_are_classified_by_receipt_holonomy_conjugacy_and_multiply_cycle_length_by_holonomy_order",
    )
    print(
        "THEOREM:",
        "A deterministic regular R-covariant lift of C_n is classified up to gauge by the conjugacy class of its holonomy h. If d=ord(h), the lift has |R|/d cycles of length n*d; it is connected exactly when d=|R|.",
    )
    print(
        "BOUNDARY:",
        "The audit checks the finite theorem exhaustively on the declared cyclic, abelian noncyclic, and nonabelian groups. It does not derive the receipt group or select a holonomy from physical structure.",
    )
    print(
        "KEEPER:",
        "A receipt does not merely remember the circuit. Its order determines how many circuits are required for complete return.",
    )
    print("MUTATION_PERFORMED: false")

    if not theorem_pass:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
