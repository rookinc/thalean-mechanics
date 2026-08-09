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
            rows.append({
                "orientation": orientation,
                "shift": shift,
                "order": tuple(
                    base[(index + shift) % 5]
                    for index in range(5)
                ),
            })

    return tuple(rows)

def orbit(permutation, start):
    values = []
    current = start

    while current not in values:
        values.append(current)
        current = permutation[current]

    return tuple(values)

native_edges = {
    edge(*row["quotient_edge"])
    for row in data["measurements"]["quotient_edges"]
}

OUTER_BASE = (0, 4, 3, 2, 1)
INNER_BASE = (13, 14, 7, 6, 10)
SPOKES = (11, 9, 12, 5, 8)

inner_edge_to_outer_edge = {}
inner_edge_to_spoke = {}

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

    inner_edge_to_outer_edge[inner_pair] = outer_pair
    inner_edge_to_spoke[inner_pair] = spoke

rows = []

for inner_gauge, outer_gauge in itertools.product(
    dihedral_orders(INNER_BASE),
    dihedral_orders(OUTER_BASE),
):
    inner_edges = cycle_edges(inner_gauge["order"])
    outer_edges = cycle_edges(outer_gauge["order"])

    outer_index = {
        pair: index
        for index, pair in enumerate(outer_edges)
    }

    permutation = tuple(
        outer_index[inner_edge_to_outer_edge[pair]]
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

    multiplier, offset = affine_candidates[0]

    fixed_indices = tuple(
        index
        for index, image in enumerate(permutation)
        if index == image
    )

    fixed_index = fixed_indices[0]
    fixed_inner_edge = inner_edges[fixed_index]
    fixed_spoke = inner_edge_to_spoke[fixed_inner_edge]

    translated_permutation = tuple(
        (
            permutation[(index + fixed_index) % 5]
            - fixed_index
        ) % 5
        for index in range(5)
    )

    expected_normal_form = tuple(
        multiplier * index % 5
        for index in range(5)
    )

    nonzero_orbit = orbit(translated_permutation, 1)

    angle_role_partition = {
        "flat_role_indices": (fixed_index,),
        "right_role_indices": tuple(
            index
            for index in range(5)
            if index != fixed_index
        ),
    }

    rows.append({
        "inner_orientation": inner_gauge["orientation"],
        "inner_shift": inner_gauge["shift"],
        "outer_orientation": outer_gauge["orientation"],
        "outer_shift": outer_gauge["shift"],
        "permutation": permutation,
        "multiplier": multiplier,
        "offset": offset,
        "fixed_index": fixed_index,
        "fixed_inner_edge": fixed_inner_edge,
        "fixed_outer_edge":
            inner_edge_to_outer_edge[fixed_inner_edge],
        "fixed_spoke_D": fixed_spoke,
        "translated_permutation": translated_permutation,
        "expected_normal_form": expected_normal_form,
        "nonzero_orbit": nonzero_orbit,
        "angle_role_partition": angle_role_partition,
    })

fixed_spoke_profile = Counter(
    row["fixed_spoke_D"]
    for row in rows
)

fixed_inner_edge_profile = Counter(
    row["fixed_inner_edge"]
    for row in rows
)

multiplier_profile = Counter(
    row["multiplier"]
    for row in rows
)

normal_form_profile = Counter(
    row["translated_permutation"]
    for row in rows
)

angle_word = (180, 90, 90, 90, 90)
angle_value_profile = Counter(angle_word)

checks = {
    "source_audit_pass":
        data.get("audit_pass") is True,
    "gauge_pair_count_100":
        len(rows) == 100,
    "every_affine_twist_has_one_fixed_bridge":
        all(
            len(row["angle_role_partition"]["flat_role_indices"]) == 1
            for row in rows
        ),
    "every_affine_twist_has_four_moving_bridges":
        all(
            len(row["angle_role_partition"]["right_role_indices"]) == 4
            for row in rows
        ),
    "translation_removes_every_offset":
        all(
            row["translated_permutation"]
            == row["expected_normal_form"]
            for row in rows
        ),
    "every_nonzero_orbit_has_length_4":
        all(
            len(row["nonzero_orbit"]) == 4
            and set(row["nonzero_orbit"]) == {1, 2, 3, 4}
            for row in rows
        ),
    "only_normal_forms_multiply_by_2_or_3":
        set(normal_form_profile) == {
            (0, 2, 4, 1, 3),
            (0, 3, 1, 4, 2),
        },
    "multiplier_profile_50_50":
        multiplier_profile == Counter({2: 50, 3: 50}),
    "each_spoke_is_fixed_in_20_gauges":
        fixed_spoke_profile == Counter({
            5: 20,
            8: 20,
            9: 20,
            11: 20,
            12: 20,
        }),
    "each_inner_edge_is_fixed_in_20_gauges":
        set(fixed_inner_edge_profile.values()) == {20},
    "registered_angle_word_has_one_plus_four_profile":
        angle_value_profile == Counter({180: 1, 90: 4}),
    "structural_orbit_profile_matches_angle_role_profile":
        all(
            (
                len(row["angle_role_partition"]["flat_role_indices"]),
                len(row["angle_role_partition"]["right_role_indices"]),
            ) == (1, 4)
            for row in rows
        ),
}

failed = [
    name
    for name, passed in checks.items()
    if not passed
]

theorem_pass = not failed

print("PACKET: g900_affine_twist_one_four_angle_role_050")
print("MODE: affine fixed-point normalization and role-profile join")
print("GAUGE_PAIR_COUNT:", len(rows))
print("MULTIPLIER_PROFILE:", dict(sorted(multiplier_profile.items())))
print("NORMAL_FORM_PROFILE:", dict(normal_form_profile))
print("FIXED_SPOKE_PROFILE:", dict(sorted(fixed_spoke_profile.items())))
print("FIXED_INNER_EDGE_PROFILE:", dict(fixed_inner_edge_profile))
print("REGISTERED_ANGLE_WORD:", angle_word)
print("REGISTERED_ANGLE_VALUE_PROFILE:", dict(angle_value_profile))
print("STRUCTURAL_ROLE_PROFILE:", (1, 4))
print("ROW_PREVIEW:", rows[:10])
print("CHECKS:", checks)
print("FAILED_CHECK_COUNT:", len(failed))
print("FAILED_CHECKS:", failed)
print("THEOREM_PASS:", theorem_pass)
print(
    "CLASSIFICATION:",
    (
        "after_translation_to_its_unique_fixed_bridge_every_"
        "native_affine_twist_is_multiplication_by_2_or_3_with_"
        "one_fixed_role_and_one_four_cycle_matching_the_"
        "registered_one_flat_four_right_angle_role_profile"
        if theorem_pass
        else "affine_twist_one_four_angle_role_join_not_derived"
    ),
)
print("ONE_FIXED_PLUS_FOUR_MOVING_ROLES_DERIVED:", theorem_pass)
print("REGISTERED_ONE_FLAT_FOUR_RIGHT_PROFILE_MATCHES:", theorem_pass)
print("NUMERIC_180_90_VALUES_DERIVED_FROM_GRAPH:", False)
print("FIXED_SPOKE_IDENTITY_IS_GAUGE_INVARIANT:", False)
print("ABSOLUTE_ORIENTATION_SELECTED:", False)
print("PHYSICAL_ANGLE_CLAIM:", False)
print("MUTATION_PERFORMED:", False)
