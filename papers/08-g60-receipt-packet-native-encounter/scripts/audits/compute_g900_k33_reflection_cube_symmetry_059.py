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

def opposite(face):
    return (face[0], -face[1])

def adjacent(left, right):
    return left[0] != right[0]

def cycle_partition(permutation, objects):
    seen = set()
    cycles = []

    for start in objects:
        if start in seen:
            continue

        cycle = []
        current = start

        while current not in seen:
            seen.add(current)
            cycle.append(current)
            current = permutation[current]

        cycles.append(tuple(cycle))

    return tuple(sorted(cycles, key=lambda row: (len(row), row)))

labeling_rows = []

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
                adjacent(left, right)
                == adjacent(
                    induced_face_action[left],
                    induced_face_action[right],
                )
                for left, right in itertools.combinations(FACES, 2)
            )

            fixed_faces = tuple(sorted(
                face
                for face in FACES
                if induced_face_action[face] == face
            ))

            moved_face_pairs = tuple(
                cycle
                for cycle in cycle_partition(
                    induced_face_action,
                    FACES,
                )
                if len(cycle) == 2
            )

            D_face = drawing_to_face["D"]
            F_face = drawing_to_face["F"]

            labeling_rows.append({
                "sign_assignment": sign_assignment,
                "drawing_to_face": drawing_to_face,
                "induced_face_action": induced_face_action,
                "preserves_opposites": preserves_opposites,
                "preserves_adjacency": preserves_adjacency,
                "D_and_F_are_opposite":
                    D_face == opposite(F_face),
                "fixed_faces": fixed_faces,
                "moved_face_pairs": moved_face_pairs,
                "cycle_profile": tuple(sorted(
                    len(cycle)
                    for cycle in cycle_partition(
                        induced_face_action,
                        FACES,
                    )
                )),
            })

cube_symmetry_rows = tuple(
    row
    for row in labeling_rows
    if row["preserves_opposites"]
    and row["preserves_adjacency"]
)

incompatible_rows = tuple(
    row
    for row in labeling_rows
    if row not in cube_symmetry_rows
)

cycle_profile = Counter(
    row["cycle_profile"]
    for row in cube_symmetry_rows
)

fixed_face_count_profile = Counter(
    len(row["fixed_faces"])
    for row in cube_symmetry_rows
)

checks = {
    "initial_cube_face_labeling_count_72":
        len(labeling_rows) == 72,
    "cube_reflection_compatible_count_24":
        len(cube_symmetry_rows) == 24,
    "incompatible_count_48":
        len(incompatible_rows) == 48,
    "every_compatible_action_preserves_opposites":
        all(
            row["preserves_opposites"]
            for row in cube_symmetry_rows
        ),
    "every_compatible_action_preserves_face_adjacency":
        all(
            row["preserves_adjacency"]
            for row in cube_symmetry_rows
        ),
    "D_and_F_are_opposite_in_every_compatible_placement":
        all(
            row["D_and_F_are_opposite"]
            for row in cube_symmetry_rows
        ),
    "compatible_reflection_cycle_profile_1_1_2_2":
        cycle_profile == Counter({
            (1, 1, 2, 2): 24,
        }),
    "compatible_reflection_fixes_two_faces":
        fixed_face_count_profile == Counter({2: 24}),
    "drawing_reflection_not_enough_for_unique_placement":
        len(cube_symmetry_rows) > 1,
}

failed = [
    name
    for name, passed in checks.items()
    if not passed
]

theorem_pass = not failed

print("PACKET: g900_k33_reflection_cube_symmetry_059")
print("MODE: signed-axis placement and drawing-reflection join")
print("INITIAL_CUBE_FACE_LABELING_COUNT:", len(labeling_rows))
print("CUBE_SYMMETRY_COMPATIBLE_COUNT:", len(cube_symmetry_rows))
print("INCOMPATIBLE_COUNT:", len(incompatible_rows))
print(
    "COMPATIBLE_CYCLE_PROFILE:",
    dict(cycle_profile),
)
print(
    "FIXED_FACE_COUNT_PROFILE:",
    dict(fixed_face_count_profile),
)
print("COMPATIBLE_PREVIEW:", cube_symmetry_rows[:10])
print("CHECKS:", checks)
print("FAILED_CHECK_COUNT:", len(failed))
print("FAILED_CHECKS:", failed)
print("THEOREM_PASS:", theorem_pass)
print(
    "CLASSIFICATION:",
    (
        "the_drawing_reflection_reduces_the_72_signed_axis_"
        "cube_face_placements_to_24_cube_symmetry_compatible_"
        "placements_and_forces_D_and_F_to_be_opposite_faces"
        if theorem_pass
        else "drawing_reflection_cube_symmetry_join_not_derived"
    ),
)
print("D_AND_F_OPPOSITE_CUBE_FACES:", theorem_pass)
print("A_B_AND_C_E_EXCHANGED_BY_ONE_CUBE_REFLECTION:", theorem_pass)
print("CUBE_PLACEMENT_COUNT_AFTER_REFLECTION:", len(
    cube_symmetry_rows
))
print("CANONICAL_CUBE_PLACEMENT_SELECTED:", False)
print("PHYSICAL_CUBE_ORIENTATION_SELECTED:", False)
print("MUTATION_PERFORMED:", False)
