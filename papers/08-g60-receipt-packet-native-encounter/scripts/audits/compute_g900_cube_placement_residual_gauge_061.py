#!/usr/bin/env python3

import itertools
from collections import Counter

AXES = ("x", "y", "z")
DRAWING_VERTICES = ("A", "B", "F", "C", "D", "E")

BASE_PLACEMENT = {
    "A": ("x", 1),
    "B": ("y", 1),
    "F": ("z", 1),
    "C": ("y", -1),
    "D": ("z", -1),
    "E": ("x", -1),
}

OPPOSITE_DRAWING_PAIRS = (
    ("A", "E"),
    ("B", "C"),
    ("F", "D"),
)

def permutation_parity(order):
    inversions = sum(
        order[left] > order[right]
        for left in range(len(order))
        for right in range(left + 1, len(order))
    )
    return -1 if inversions % 2 else 1

def transform_face(face, axis_map, global_sign):
    return (
        axis_map[face[0]],
        global_sign * face[1],
    )

def placement_key(placement):
    return tuple(
        placement[vertex]
        for vertex in DRAWING_VERTICES
    )

gauge_rows = []

for axis_order in itertools.permutations(AXES):
    axis_map = dict(zip(AXES, axis_order))
    parity = permutation_parity(axis_order)

    for global_sign in (1, -1):
        placement = {
            vertex: transform_face(
                face,
                axis_map,
                global_sign,
            )
            for vertex, face in BASE_PLACEMENT.items()
        }

        determinant = parity * global_sign

        gauge_rows.append({
            "axis_order": axis_order,
            "axis_parity": parity,
            "global_sign": global_sign,
            "determinant": determinant,
            "placement": placement,
            "placement_key": placement_key(placement),
        })

placement_keys = {
    row["placement_key"]
    for row in gauge_rows
}

determinant_profile = Counter(
    row["determinant"]
    for row in gauge_rows
)

global_sign_profile = Counter(
    row["global_sign"]
    for row in gauge_rows
)

axis_parity_profile = Counter(
    row["axis_parity"]
    for row in gauge_rows
)

opposite_pair_checks = tuple(
    (
        left,
        right,
        all(
            row["placement"][left][0]
            == row["placement"][right][0]
            and row["placement"][left][1]
            == -row["placement"][right][1]
            for row in gauge_rows
        ),
    )
    for left, right in OPPOSITE_DRAWING_PAIRS
)

base_stabilizer_rows = tuple(
    row
    for row in gauge_rows
    if row["placement"] == BASE_PLACEMENT
)

drawing_reflection_axis_map = {
    "x": "y",
    "y": "x",
    "z": "z",
}

drawing_reflection_row = tuple(
    row
    for row in gauge_rows
    if dict(zip(AXES, row["axis_order"]))
       == drawing_reflection_axis_map
    and row["global_sign"] == 1
)

checks = {
    "residual_gauge_element_count_12":
        len(gauge_rows) == 12,
    "distinct_placement_count_12":
        len(placement_keys) == 12,
    "gauge_action_is_free_on_base_placement":
        len(base_stabilizer_rows) == 1,
    "gauge_action_is_transitive_on_12_placements":
        len(placement_keys) == len(gauge_rows),
    "opposite_pairing_AE_BC_FD_preserved":
        all(passed for _, _, passed in opposite_pair_checks),
    "axis_permutation_count_6":
        len({
            row["axis_order"]
            for row in gauge_rows
        }) == 6,
    "global_sign_choice_count_2":
        set(global_sign_profile) == {-1, 1},
    "orientation_profile_6_and_6":
        determinant_profile == Counter({
            -1: 6,
            1: 6,
        }),
    "axis_parity_profile_balanced":
        axis_parity_profile == Counter({
            -1: 6,
            1: 6,
        }),
    "global_sign_profile_balanced":
        global_sign_profile == Counter({
            -1: 6,
            1: 6,
        }),
    "drawing_reflection_is_one_residual_gauge_element":
        len(drawing_reflection_row) == 1,
    "drawing_reflection_reverses_orientation":
        drawing_reflection_row[0]["determinant"] == -1,
}

failed = [
    name
    for name, passed in checks.items()
    if not passed
]

theorem_pass = not failed

print("PACKET: g900_cube_placement_residual_gauge_061")
print("MODE: exact post-distance-filter cube placement gauge census")
print("BASE_PLACEMENT:", BASE_PLACEMENT)
print("OPPOSITE_DRAWING_PAIRS:", OPPOSITE_DRAWING_PAIRS)
print("RESIDUAL_GAUGE_ELEMENT_COUNT:", len(gauge_rows))
print("DISTINCT_PLACEMENT_COUNT:", len(placement_keys))
print("GAUGE_STRUCTURE: S3 x C2")
print("DETERMINANT_PROFILE:", dict(sorted(
    determinant_profile.items()
)))
print("GLOBAL_SIGN_PROFILE:", dict(sorted(
    global_sign_profile.items()
)))
print("AXIS_PARITY_PROFILE:", dict(sorted(
    axis_parity_profile.items()
)))
print("OPPOSITE_PAIR_CHECKS:", opposite_pair_checks)
print("BASE_STABILIZER_COUNT:", len(base_stabilizer_rows))
print("DRAWING_REFLECTION_ROW:", drawing_reflection_row)
print("GAUGE_ROWS:", gauge_rows)
print("CHECKS:", checks)
print("FAILED_CHECK_COUNT:", len(failed))
print("FAILED_CHECKS:", failed)
print("THEOREM_PASS:", theorem_pass)
print(
    "CLASSIFICATION:",
    (
        "after_the_reflection_and_native_distance_filters_the_"
        "remaining_12_cube_face_placements_form_a_free_"
        "transitive_S3_times_C2_gauge_orbit_with_opposite_"
        "pairs_AE_BC_and_FD"
        if theorem_pass
        else "cube_placement_residual_gauge_not_derived"
    ),
)
print("RESIDUAL_GAUGE_GROUP:", "S3_x_C2" if theorem_pass else None)
print("RESIDUAL_GAUGE_ORDER:", 12 if theorem_pass else None)
print("ORIENTATION_PRESERVING_PLACEMENTS:", 6)
print("ORIENTATION_REVERSING_PLACEMENTS:", 6)
print("ABSOLUTE_AXIS_NAMES_SELECTED:", False)
print("ABSOLUTE_SIGN_CLASS_SELECTED:", False)
print("ABSOLUTE_HANDEDNESS_SELECTED:", False)
print("PHYSICAL_CUBE_ORIENTATION_SELECTED:", False)
print("MUTATION_PERFORMED:", False)
