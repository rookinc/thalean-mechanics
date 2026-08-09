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
            shifted = tuple(
                base[(index + shift) % 5]
                for index in range(5)
            )
            rows.append({
                "orientation": orientation,
                "shift": shift,
                "order": shifted,
            })

    return tuple(rows)

def permutation_order(permutation):
    current = tuple(range(5))
    identity = current

    for exponent in range(1, 101):
        current = tuple(
            permutation[value]
            for value in current
        )
        if current == identity:
            return exponent

    return None

def cycle_profile(permutation):
    seen = set()
    profile = []

    for start in range(5):
        if start in seen:
            continue

        current = start
        size = 0

        while current not in seen:
            seen.add(current)
            size += 1
            current = permutation[current]

        profile.append(size)

    return tuple(sorted(profile))

native_edges = {
    edge(*row["quotient_edge"])
    for row in data["measurements"]["quotient_edges"]
}

OUTER_BASE = (0, 4, 3, 2, 1)
INNER_BASE = (13, 14, 7, 6, 10)
SPOKES = (11, 9, 12, 5, 8)

inner_to_outer = {}

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

    inner_to_outer[edge(*inner_neighbors)] = edge(*outer_neighbors)

inner_gauges = dihedral_orders(INNER_BASE)
outer_gauges = dihedral_orders(OUTER_BASE)

rows = []

for inner_gauge, outer_gauge in itertools.product(
    inner_gauges,
    outer_gauges,
):
    inner_edges = cycle_edges(inner_gauge["order"])
    outer_edges = cycle_edges(outer_gauge["order"])

    outer_index = {
        pair: index
        for index, pair in enumerate(outer_edges)
    }

    permutation = tuple(
        outer_index[inner_to_outer[pair]]
        for pair in inner_edges
    )

    affine_candidates = tuple(
        (multiplier, offset)
        for multiplier in range(5)
        for offset in range(5)
        if all(
            permutation[index]
            == (multiplier * index + offset) % 5
            for index in range(5)
        )
    )

    multiplier = (
        affine_candidates[0][0]
        if len(affine_candidates) == 1
        else None
    )
    offset = (
        affine_candidates[0][1]
        if len(affine_candidates) == 1
        else None
    )

    fixed_indices = tuple(
        index
        for index, image in enumerate(permutation)
        if index == image
    )

    rows.append({
        "inner_orientation": inner_gauge["orientation"],
        "inner_shift": inner_gauge["shift"],
        "outer_orientation": outer_gauge["orientation"],
        "outer_shift": outer_gauge["shift"],
        "permutation": permutation,
        "affine_candidates": affine_candidates,
        "multiplier": multiplier,
        "offset": offset,
        "permutation_order": permutation_order(permutation),
        "cycle_profile": cycle_profile(permutation),
        "fixed_indices": fixed_indices,
    })

multiplier_profile = Counter(
    row["multiplier"]
    for row in rows
)

offset_profile = Counter(
    row["offset"]
    for row in rows
)

affine_pair_profile = Counter(
    (row["multiplier"], row["offset"])
    for row in rows
)

orientation_relation_profile = Counter(
    (
        row["inner_orientation"] == row["outer_orientation"],
        row["multiplier"],
    )
    for row in rows
)

order_profile = Counter(
    row["permutation_order"]
    for row in rows
)

cycle_profile_counts = Counter(
    row["cycle_profile"]
    for row in rows
)

fixed_point_count_profile = Counter(
    len(row["fixed_indices"])
    for row in rows
)

checks = {
    "source_audit_pass":
        data.get("audit_pass") is True,
    "inner_gauge_count_10":
        len(inner_gauges) == 10,
    "outer_gauge_count_10":
        len(outer_gauges) == 10,
    "gauge_pair_count_100":
        len(rows) == 100,
    "every_gauge_has_unique_affine_law":
        all(
            len(row["affine_candidates"]) == 1
            for row in rows
        ),
    "only_multipliers_2_and_3":
        set(multiplier_profile) == {2, 3},
    "multipliers_balanced_50_50":
        multiplier_profile == Counter({2: 50, 3: 50}),
    "all_offsets_occur_uniformly":
        offset_profile == Counter({
            0: 20,
            1: 20,
            2: 20,
            3: 20,
            4: 20,
        }),
    "all_ten_affine_laws_occur_ten_times":
        len(affine_pair_profile) == 10
        and set(affine_pair_profile.values()) == {10},
    "every_permutation_has_order_4":
        order_profile == Counter({4: 100}),
    "every_permutation_has_cycle_profile_1_4":
        cycle_profile_counts == Counter({(1, 4): 100}),
    "every_permutation_has_one_fixed_edge":
        fixed_point_count_profile == Counter({1: 100}),
    "orientation_relation_controls_inverse_pair":
        orientation_relation_profile == Counter({
            (True, 2): 50,
            (False, 3): 50,
        }),
}

failed = [
    name
    for name, passed in checks.items()
    if not passed
]

theorem_pass = not failed

print("PACKET: g900_native_c5_affine_twist_gauge_census_047")
print("MODE: exhaustive independent dihedral coordinate census")
print("INNER_GAUGE_COUNT:", len(inner_gauges))
print("OUTER_GAUGE_COUNT:", len(outer_gauges))
print("GAUGE_PAIR_COUNT:", len(rows))
print("MULTIPLIER_PROFILE:", dict(sorted(multiplier_profile.items())))
print("OFFSET_PROFILE:", dict(sorted(offset_profile.items())))
print("AFFINE_PAIR_PROFILE:", dict(sorted(affine_pair_profile.items())))
print(
    "ORIENTATION_RELATION_PROFILE:",
    dict(sorted(orientation_relation_profile.items())),
)
print("PERMUTATION_ORDER_PROFILE:", dict(sorted(order_profile.items())))
print(
    "PERMUTATION_CYCLE_PROFILE:",
    dict(sorted(cycle_profile_counts.items())),
)
print(
    "FIXED_POINT_COUNT_PROFILE:",
    dict(sorted(fixed_point_count_profile.items())),
)
print("ROW_PREVIEW:", rows[:10])
print("CHECKS:", checks)
print("FAILED_CHECK_COUNT:", len(failed))
print("FAILED_CHECKS:", failed)
print("THEOREM_PASS:", theorem_pass)
print(
    "CLASSIFICATION:",
    (
        "under_all_independent_dihedral_C5_relabelings_the_"
        "native_spoke_bridge_remains_an_order_four_affine_"
        "twist_with_unoriented_multiplier_pair_2_and_3"
        if theorem_pass
        else "native_affine_twist_gauge_invariance_not_derived"
    ),
)
print("COORDINATE_FREE_ORDER_FOUR_TWIST_DERIVED:", theorem_pass)
print("UNORIENTED_MULTIPLIER_PAIR:", (2, 3))
print("OFFSET_IS_GAUGE_DEPENDENT:", theorem_pass)
print("FIXED_EDGE_LABEL_IS_GAUGE_DEPENDENT:", theorem_pass)
print("ABSOLUTE_ORIENTATION_SELECTED:", False)
print("ANGLE_180_DERIVED:", False)
print("PHYSICAL_ROTATION_CLAIM:", False)
print("MUTATION_PERFORMED:", False)
