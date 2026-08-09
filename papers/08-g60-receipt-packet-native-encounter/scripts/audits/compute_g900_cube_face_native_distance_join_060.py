#!/usr/bin/env python3

import itertools
from collections import Counter

LEFT = ("A", "B", "F")
RIGHT = ("C", "D", "E")
DRAWING_VERTICES = LEFT + RIGHT

REFLECTION = {
    "A": "B",
    "B": "A",
    "C": "E",
    "E": "C",
    "D": "D",
    "F": "F",
}

AXES = ("x", "y", "z")

POSITIVE = tuple(
    (axis, 1)
    for axis in AXES
)

NEGATIVE = tuple(
    (axis, -1)
    for axis in AXES
)

FACES = POSITIVE + NEGATIVE

def edge(left, right):
    return tuple(sorted((left, right)))

def opposite(face):
    return (face[0], -face[1])

def cube_adjacent(left, right):
    return left[0] != right[0]

def cube_opposite(left, right):
    return (
        left[0] == right[0]
        and left[1] == -right[1]
    )

K33_EDGES = {
    edge(left, right)
    for left in LEFT
    for right in RIGHT
}

NATIVE_DISTANCE_1_ROLES = {
    edge("A", "C"),
    edge("C", "F"),
    edge("E", "F"),
    edge("B", "E"),
    edge("A", "D"),
    edge("B", "D"),
}

NATIVE_DISTANCE_2_ROLES = {
    edge("A", "E"),
    edge("B", "C"),
}

NATIVE_DISTANCE_3_ROLES = {
    edge("D", "F"),
}

NATIVE_NONUNIT_ROLES = (
    NATIVE_DISTANCE_2_ROLES
    | NATIVE_DISTANCE_3_ROLES
)

rows = []

for left_faces, right_faces, sign_assignment in (
    (POSITIVE, NEGATIVE, ("positive", "negative")),
    (NEGATIVE, POSITIVE, ("negative", "positive")),
):
    for left_order in itertools.permutations(left_faces):
        for right_order in itertools.permutations(right_faces):
            drawing_to_face = dict(zip(LEFT, left_order))
            drawing_to_face.update(zip(RIGHT, right_order))

            face_to_drawing = {
                face: vertex
                for vertex, face in drawing_to_face.items()
            }

            induced_face_action = {
                face: drawing_to_face[
                    REFLECTION[face_to_drawing[face]]
                ]
                for face in FACES
            }

            preserves_opposites = all(
                induced_face_action[opposite(face)]
                == opposite(induced_face_action[face])
                for face in FACES
            )

            preserves_adjacency = all(
                cube_adjacent(left, right)
                == cube_adjacent(
                    induced_face_action[left],
                    induced_face_action[right],
                )
                for left, right in itertools.combinations(FACES, 2)
            )

            if not preserves_opposites or not preserves_adjacency:
                continue

            drawing_cube_adjacent_roles = {
                pair
                for pair in K33_EDGES
                if cube_adjacent(
                    drawing_to_face[pair[0]],
                    drawing_to_face[pair[1]],
                )
            }

            drawing_cube_opposite_roles = {
                pair
                for pair in K33_EDGES
                if cube_opposite(
                    drawing_to_face[pair[0]],
                    drawing_to_face[pair[1]],
                )
            }

            exact_distance_join = (
                drawing_cube_adjacent_roles
                == NATIVE_DISTANCE_1_ROLES
                and drawing_cube_opposite_roles
                == NATIVE_NONUNIT_ROLES
            )

            rows.append({
                "sign_assignment": sign_assignment,
                "drawing_to_face": drawing_to_face,
                "cube_adjacent_roles":
                    tuple(sorted(drawing_cube_adjacent_roles)),
                "cube_opposite_roles":
                    tuple(sorted(drawing_cube_opposite_roles)),
                "distance_join_exact":
                    exact_distance_join,
            })

exact_rows = tuple(
    row
    for row in rows
    if row["distance_join_exact"]
)

opposite_role_profile = Counter(
    row["cube_opposite_roles"]
    for row in rows
)

exact_axis_profile = Counter(
    (
        row["drawing_to_face"]["D"][0],
        row["drawing_to_face"]["D"][1],
    )
    for row in exact_rows
)

checks = {
    "reflection_compatible_row_count_24":
        len(rows) == 24,
    "two_opposite_role_patterns":
        len(opposite_role_profile) == 2,
    "each_opposite_pattern_occurs_12_times":
        set(opposite_role_profile.values()) == {12},
    "exact_distance_join_count_12":
        len(exact_rows) == 12,
    "exact_rows_put_AE_BC_DF_on_opposite_faces":
        all(
            set(row["cube_opposite_roles"])
            == NATIVE_NONUNIT_ROLES
            for row in exact_rows
        ),
    "exact_rows_put_six_distance1_roles_on_adjacent_faces":
        all(
            set(row["cube_adjacent_roles"])
            == NATIVE_DISTANCE_1_ROLES
            for row in exact_rows
        ),
    "DF_is_always_the_distance3_opposite_axis":
        all(
            edge("D", "F")
            in row["cube_opposite_roles"]
            for row in exact_rows
        ),
    "AE_and_BC_are_the_distance2_opposite_pairs":
        all(
            NATIVE_DISTANCE_2_ROLES
            <= set(row["cube_opposite_roles"])
            for row in exact_rows
        ),
    "placement_remains_noncanonical":
        len(exact_rows) > 1,
}

failed = [
    name
    for name, passed in checks.items()
    if not passed
]

theorem_pass = not failed

print("PACKET: g900_cube_face_native_distance_join_060")
print("MODE: reflection-compatible cube placement distance-role filter")
print("REFLECTION_COMPATIBLE_COUNT:", len(rows))
print(
    "OPPOSITE_ROLE_PROFILE:",
    dict(opposite_role_profile),
)
print("NATIVE_DISTANCE_1_ROLES:", tuple(sorted(
    NATIVE_DISTANCE_1_ROLES
)))
print("NATIVE_DISTANCE_2_ROLES:", tuple(sorted(
    NATIVE_DISTANCE_2_ROLES
)))
print("NATIVE_DISTANCE_3_ROLES:", tuple(sorted(
    NATIVE_DISTANCE_3_ROLES
)))
print("EXACT_DISTANCE_JOIN_COUNT:", len(exact_rows))
print("EXACT_ROW_PREVIEW:", exact_rows[:12])
print("EXACT_D_AXIS_PROFILE:", dict(sorted(
    exact_axis_profile.items()
)))
print("CHECKS:", checks)
print("FAILED_CHECK_COUNT:", len(failed))
print("FAILED_CHECKS:", failed)
print("THEOREM_PASS:", theorem_pass)
print(
    "CLASSIFICATION:",
    (
        "among_the_24_reflection_compatible_cube_face_"
        "placements_exactly_12_identify_the_six_cube_adjacent_"
        "K3_3_relations_with_native_distance_1_and_the_three_"
        "opposite_face_relations_with_AE_BC_distance_2_and_"
        "DF_distance_3"
        if theorem_pass
        else "cube_face_native_distance_join_not_derived"
    ),
)
print("CUBE_ADJACENCY_EQUALS_NATIVE_DISTANCE1_ROLES:", theorem_pass)
print("CUBE_OPPOSITES_EQUAL_NATIVE_NONUNIT_ROLES:", theorem_pass)
print("DISTANCE2_OPPOSITE_PAIRS:", ("AE", "BC"))
print("DISTANCE3_OPPOSITE_AXIS:", "DF")
print("CUBE_PLACEMENT_COUNT_AFTER_DISTANCE_FILTER:", len(exact_rows))
print("CANONICAL_CUBE_PLACEMENT_SELECTED:", False)
print("PHYSICAL_DISTANCE_CLAIM:", False)
print("MUTATION_PERFORMED:", False)
