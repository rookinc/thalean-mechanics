from __future__ import annotations

import itertools
import json
from pathlib import Path

TARGET = Path(__file__).resolve().parents[2]
ARTIFACT = (
    TARGET
    / "artifacts/json/"
    "c4_binary_receipt_order_forcing_theorem_001.v1.json"
)


def xor_all(values):
    out = 0
    for value in values:
        out ^= value
    return out


def successor(voltage):
    out = {}
    for phase in range(4):
        for sheet in range(2):
            out[(phase, sheet)] = (
                (phase + 1) % 4,
                sheet ^ voltage[phase],
            )
    return out


def order(permutation):
    identity = {state: state for state in permutation}
    power = dict(identity)
    for candidate in range(1, 65):
        power = {
            state: permutation[power[state]]
            for state in permutation
        }
        if power == identity:
            return candidate
    raise RuntimeError("order bound exceeded")


def cycles(permutation):
    unseen = set(permutation)
    lengths = []
    while unseen:
        current = min(unseen)
        length = 0
        while current in unseen:
            unseen.remove(current)
            current = permutation[current]
            length += 1
        lengths.append(length)
    return sorted(lengths)


def canonical(voltage):
    rows = []
    for gauge in itertools.product(range(2), repeat=4):
        rows.append(
            tuple(
                voltage[index]
                ^ gauge[index]
                ^ gauge[(index + 1) % 4]
                for index in range(4)
            )
        )
    return min(rows)


artifact = json.loads(ARTIFACT.read_text())

rows = []
for voltage in itertools.product(range(2), repeat=4):
    permutation = successor(voltage)
    holonomy = xor_all(voltage)

    for phase in range(4):
        for sheet in range(2):
            state = (phase, sheet)
            current = state
            for _ in range(4):
                current = permutation[current]
            assert current == (phase, sheet ^ holonomy)

    rows.append(
        {
            "voltage": voltage,
            "holonomy": holonomy,
            "canonical": canonical(voltage),
            "order": order(permutation),
            "cycles": cycles(permutation),
        }
    )

even = [row for row in rows if row["holonomy"] == 0]
odd = [row for row in rows if row["holonomy"] == 1]

all_classes = {row["canonical"] for row in rows}
even_classes = {row["canonical"] for row in even}
odd_classes = {row["canonical"] for row in odd}

assert len(rows) == 16
assert len(even) == 8
assert len(odd) == 8
assert len(all_classes) == 2
assert len(even_classes) == 1
assert len(odd_classes) == 1

assert all(
    row["order"] == 4 and row["cycles"] == [4, 4]
    for row in even
)
assert all(
    row["order"] == 8 and row["cycles"] == [8]
    for row in odd
)

assert artifact["audit_pass"] is True
assert artifact["premises"]["visible_base"]["first_return_step"] == 4
assert artifact["premises"]["receipt_fiber"]["isomorphism_type"] == "C2"
assert artifact["census"]["binary_edge_assignment_count"] == 16
assert artifact["census"]["gauge_class_count"] == 2
assert (
    artifact["census"]["nontrivial_class"]["lifted_successor_order"]
    == 8
)
assert (
    artifact["theorem"]["uniqueness_scope"]
    == "unique_up_to_fiber_preserving_gauge_and_isomorphism"
)
assert artifact["boundaries"]["physical_realization_derived"] is False
assert artifact["boundaries"]["physics_claim"] is False
assert (
    artifact["verdict"]
    == "visible_C4_with_binary_nontrivial_receipt_holonomy_"
    "uniquely_forces_connected_C8_lift_up_to_gauge"
)

print("AUDIT_PASS: true")
print("BINARY_EDGE_ASSIGNMENT_COUNT:", len(rows))
print("TRIVIAL_HOLONOMY_ASSIGNMENT_COUNT:", len(even))
print("NONTRIVIAL_HOLONOMY_ASSIGNMENT_COUNT:", len(odd))
print("GAUGE_CLASS_COUNT:", len(all_classes))
print("TRIVIAL_CLASS_CYCLE_PROFILE: [4,4]")
print("NONTRIVIAL_CLASS_CYCLE_PROFILE: [8]")
print("NONTRIVIAL_LIFT_ORDER: 8")
print("UNIQUENESS: up_to_fiber_preserving_gauge_and_isomorphism")
print("VERDICT:", artifact["verdict"])
