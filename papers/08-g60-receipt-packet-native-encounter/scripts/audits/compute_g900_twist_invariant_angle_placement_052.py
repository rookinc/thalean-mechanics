#!/usr/bin/env python3

import itertools
import json
import pathlib
from collections import Counter

SOURCE = pathlib.Path(
    "/data/data/com.termux/files/home/dev/cori/research/"
    "mathematics/41-order-4-dodecahedral-residue/"
    "artifacts/json/intrinsic_g15_line_petersen_audit_015.json"
)

data = json.loads(SOURCE.read_text(encoding="utf-8"))

def edge(left, right):
    return tuple(sorted((int(left), int(right))))

def cycle_edges(order):
    return tuple(
        edge(order[index], order[(index + 1) % 5])
        for index in range(5)
    )

def dihedral_orders(order):
    rows = []

    for orientation in ("forward", "reverse"):
        base = order if orientation == "forward" else tuple(reversed(order))

        for shift in range(5):
            rows.append(tuple(
                base[(index + shift) % 5]
                for index in range(5)
            ))

    return tuple(rows)

def invariant_labeling(permutation, labeling):
    return all(
        labeling[permutation[index]] == labeling[index]
        for index in range(5)
    )

native_edges = {
    edge(*row["quotient_edge"])
    for row in data["measurements"]["quotient_edges"]
}

OUTER_BASE = (0, 4, 3, 2, 1)
INNER_BASE = (13, 14, 7, 6, 10)
SPOKES = (11, 9, 12, 5, 8)

inner_to_outer = {}
inner_to_spoke = {}

for spoke in SPOKES:
    inner_neighbors = tuple(sorted(
        vertex
        for vertex in INNER_BASE
        if edge(spoke, vertex) in native_edges
    ))
    outer_neighbors = tuple(sorted(
        vertex
        for vertex in OUTER_BASE
        if edge(spoke, vertex) in native_edges
    ))

    inner_pair = edge(*inner_neighbors)
    outer_pair = edge(*outer_neighbors)

    inner_to_outer[inner_pair] = outer_pair
    inner_to_spoke[inner_pair] = spoke

rows = []

for inner_order, outer_order in itertools.product(
    dihedral_orders(INNER_BASE),
    dihedral_orders(OUTER_BASE),
):
    inner_edges = cycle_edges(inner_order)
    outer_edges = cycle_edges(outer_order)

    outer_index = {
        pair: index
        for index, pair in enumerate(outer_edges)
    }

    permutation = tuple(
        outer_index[inner_to_outer[pair]]
        for pair in inner_edges
    )

    fixed_indices = tuple(
        index
        for index, image in enumerate(permutation)
        if index == image
    )

    candidate_labelings = tuple(
        tuple(
            180 if index == flat_index else 90
            for index in range(5)
        )
        for flat_index in range(5)
    )

    invariant_candidates = tuple(
        labeling
        for labeling in candidate_labelings
        if invariant_labeling(permutation, labeling)
    )

    fixed_index = fixed_indices[0]
    fixed_inner_edge = inner_edges[fixed_index]
    fixed_outer_edge = inner_to_outer[fixed_inner_edge]
    fixed_spoke = inner_to_spoke[fixed_inner_edge]

    expected_labeling = tuple(
        180 if index == fixed_index else 90
        for index in range(5)
    )

    rows.append({
        "permutation": permutation,
        "fixed_index": fixed_index,
        "fixed_inner_edge": fixed_inner_edge,
        "fixed_outer_edge": fixed_outer_edge,
        "fixed_spoke_D": fixed_spoke,
        "formal_midpoint_Y": "Y_" + str(fixed_index),
        "candidate_labeling_count": len(candidate_labelings),
        "invariant_labeling_count": len(invariant_candidates),
        "invariant_labeling": invariant_candidates[0],
        "expected_labeling": expected_labeling,
    })

fixed_spoke_profile = Counter(
    row["fixed_spoke_D"]
    for row in rows
)

invariant_count_profile = Counter(
    row["invariant_labeling_count"]
    for row in rows
)

checks = {
    "source_audit_pass":
        data.get("audit_pass") is True,
    "gauge_pair_count_100":
        len(rows) == 100,
    "five_candidate_angle_placements_per_gauge":
        all(
            row["candidate_labeling_count"] == 5
            for row in rows
        ),
    "exactly_one_twist_invariant_placement_per_gauge":
        invariant_count_profile == Counter({1: 100}),
    "invariant_placement_puts_180_at_fixed_bridge":
        all(
            row["invariant_labeling"]
            == row["expected_labeling"]
            for row in rows
        ),
    "invariant_placement_puts_90_on_four_cycle":
        all(
            Counter(row["invariant_labeling"])
            == Counter({180: 1, 90: 4})
            for row in rows
        ),
    "each_spoke_can_be_fixed_under_gauge":
        fixed_spoke_profile == Counter({
            5: 20,
            8: 20,
            9: 20,
            11: 20,
            12: 20,
        }),
}

failed = [
    name
    for name, passed in checks.items()
    if not passed
]

theorem_pass = not failed

print("PACKET: g900_twist_invariant_angle_placement_052")
print("MODE: invariant registered-angle placement census")
print("GAUGE_PAIR_COUNT:", len(rows))
print("ANGLE_MULTISET:", (180, 90, 90, 90, 90))
print(
    "INVARIANT_LABELING_COUNT_PROFILE:",
    dict(invariant_count_profile),
)
print("FIXED_SPOKE_PROFILE:", dict(sorted(fixed_spoke_profile.items())))
print("ROW_PREVIEW:", rows[:10])
print("CHECKS:", checks)
print("FAILED_CHECK_COUNT:", len(failed))
print("FAILED_CHECKS:", failed)
print("THEOREM_PASS:", theorem_pass)
print(
    "CLASSIFICATION:",
    (
        "given_the_registered_angle_multiset_one_180_and_four_"
        "90_the_native_order_four_twist_uniquely_places_180_on_"
        "its_fixed_bridge_and_90_on_its_four_cycle"
        if theorem_pass
        else "twist_invariant_angle_placement_not_derived"
    ),
)
print("ANGLE_MULTISET_REGISTERED_EXTERNALLY:", True)
print("ANGLE_PLACEMENT_FORCED_BY_TWIST:", theorem_pass)
print("FIXED_BRIDGE_RECEIVES_180:", theorem_pass)
print("FOUR_CYCLE_RECEIVES_90:", theorem_pass)
print("FIXED_SPOKE_TO_MIDPOINT_PULLBACK_AVAILABLE:", theorem_pass)
print("NUMERIC_ANGLE_MULTISET_DERIVED_FROM_GRAPH:", False)
print("FIXED_SPOKE_IDENTITY_GAUGE_INVARIANT:", False)
print("PHYSICAL_ANGLE_CLAIM:", False)
print("MUTATION_PERFORMED:", False)
