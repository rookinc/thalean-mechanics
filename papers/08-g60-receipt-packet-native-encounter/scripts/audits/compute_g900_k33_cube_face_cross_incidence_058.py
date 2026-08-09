#!/usr/bin/env python3

import itertools
from collections import Counter

DRAWING_LEFT = ("A", "B", "F")
DRAWING_RIGHT = ("C", "D", "E")

AXES = ("x", "y", "z")
SIGNS = (1, -1)

CUBE_FACES = tuple(
    (axis, sign)
    for axis in AXES
    for sign in SIGNS
)

POSITIVE_FACES = tuple(
    (axis, 1)
    for axis in AXES
)

NEGATIVE_FACES = tuple(
    (axis, -1)
    for axis in AXES
)

def edge(left, right):
    return tuple(sorted((left, right)))

def cube_faces_adjacent(left, right):
    return left[0] != right[0]

def cube_faces_opposite(left, right):
    return (
        left[0] == right[0]
        and left[1] == -right[1]
    )

cube_face_adjacency_edges = {
    edge(left, right)
    for left, right in itertools.combinations(CUBE_FACES, 2)
    if cube_faces_adjacent(left, right)
}

cube_opposite_pairs = {
    edge((axis, 1), (axis, -1))
    for axis in AXES
}

cross_sign_edges = {
    edge(positive, negative)
    for positive in POSITIVE_FACES
    for negative in NEGATIVE_FACES
}

cross_adjacent_edges = {
    pair
    for pair in cross_sign_edges
    if cube_faces_adjacent(*pair)
}

cross_opposite_edges = {
    pair
    for pair in cross_sign_edges
    if cube_faces_opposite(*pair)
}

same_sign_adjacency_edges = (
    cube_face_adjacency_edges - cross_adjacent_edges
)

drawing_edges = {
    edge(left, right)
    for left in DRAWING_LEFT
    for right in DRAWING_RIGHT
}

labeling_rows = []

for sign_assignment in (
    ("positive", "negative"),
    ("negative", "positive"),
):
    target_left = (
        POSITIVE_FACES
        if sign_assignment[0] == "positive"
        else NEGATIVE_FACES
    )
    target_right = (
        NEGATIVE_FACES
        if sign_assignment[1] == "negative"
        else POSITIVE_FACES
    )

    for left_order in itertools.permutations(target_left):
        for right_order in itertools.permutations(target_right):
            mapping = dict(zip(DRAWING_LEFT, left_order))
            mapping.update(zip(DRAWING_RIGHT, right_order))

            mapped_edges = {
                edge(mapping[left], mapping[right])
                for left, right in drawing_edges
            }

            labeling_rows.append({
                "left_sign": sign_assignment[0],
                "right_sign": sign_assignment[1],
                "mapping": mapping,
                "mapped_edges_equal_cross_sign_relation":
                    mapped_edges == cross_sign_edges,
            })

valid_labelings = tuple(
    row
    for row in labeling_rows
    if row["mapped_edges_equal_cross_sign_relation"]
)

relation_type_profile = Counter(
    "opposite"
    if pair in cross_opposite_edges
    else "adjacent"
    for pair in cross_sign_edges
)

checks = {
    "cube_face_count_6":
        len(CUBE_FACES) == 6,
    "cube_face_adjacency_edge_count_12":
        len(cube_face_adjacency_edges) == 12,
    "cube_opposite_pair_count_3":
        len(cube_opposite_pairs) == 3,
    "cross_sign_relation_is_K33_edge_count_9":
        len(cross_sign_edges) == 9,
    "cross_sign_adjacent_count_6":
        len(cross_adjacent_edges) == 6,
    "cross_sign_opposite_count_3":
        len(cross_opposite_edges) == 3,
    "cross_relation_partitions_6_plus_3":
        cross_adjacent_edges.isdisjoint(cross_opposite_edges)
        and cross_adjacent_edges | cross_opposite_edges
        == cross_sign_edges,
    "omitted_same_sign_cube_adjacencies_count_6":
        len(same_sign_adjacency_edges) == 6,
    "K33_is_not_cube_face_adjacency_graph":
        cross_sign_edges != cube_face_adjacency_edges,
    "K33_is_complete_positive_negative_face_relation":
        cross_sign_edges == {
            edge(positive, negative)
            for positive in POSITIVE_FACES
            for negative in NEGATIVE_FACES
        },
    "drawing_partition_has_72_signed_axis_labelings":
        len(valid_labelings) == 72,
    "no_unique_cube_face_labeling":
        len(valid_labelings) > 1,
}

failed = [
    name
    for name, passed in checks.items()
    if not passed
]

theorem_pass = not failed

print("PACKET: g900_k33_cube_face_cross_incidence_058")
print("MODE: exact signed-axis cube-face relation scout")
print("CUBE_FACES:", CUBE_FACES)
print("POSITIVE_FACES:", POSITIVE_FACES)
print("NEGATIVE_FACES:", NEGATIVE_FACES)
print("CUBE_FACE_ADJACENCY_EDGE_COUNT:", len(
    cube_face_adjacency_edges
))
print("CUBE_OPPOSITE_PAIRS:", tuple(sorted(cube_opposite_pairs)))
print("CROSS_SIGN_EDGE_COUNT:", len(cross_sign_edges))
print("CROSS_ADJACENT_EDGES:", tuple(sorted(cross_adjacent_edges)))
print("CROSS_OPPOSITE_EDGES:", tuple(sorted(cross_opposite_edges)))
print(
    "SAME_SIGN_ADJACENCY_EDGES_OMITTED:",
    tuple(sorted(same_sign_adjacency_edges)),
)
print(
    "CROSS_RELATION_TYPE_PROFILE:",
    dict(sorted(relation_type_profile.items())),
)
print("VALID_CUBE_FACE_LABELING_COUNT:", len(valid_labelings))
print("LABELING_PREVIEW:", valid_labelings[:10])
print("CHECKS:", checks)
print("FAILED_CHECK_COUNT:", len(failed))
print("FAILED_CHECKS:", failed)
print("THEOREM_PASS:", theorem_pass)
print(
    "CLASSIFICATION:",
    (
        "K3_3_is_exactly_the_complete_cross_incidence_relation_"
        "between_the_three_positive_and_three_negative_signed_"
        "axis_faces_of_a_cube_with_six_adjacent_and_three_"
        "opposite_face_relations"
        if theorem_pass
        else "K3_3_cube_face_cross_incidence_not_derived"
    ),
)
print("ABF_AND_CDE_MODEL_OPPOSITE_SIGN_CLASSES:", theorem_pass)
print("CUBE_FACE_PLACEMENT_COUNT:", len(valid_labelings))
print("CANONICAL_CUBE_FACE_PLACEMENT_SELECTED:", False)
print("K33_EQUALS_CUBE_FACE_ADJACENCY_GRAPH:", False)
print("ABSTRACT_CUBE_FACE_PROJECTION_AVAILABLE:", theorem_pass)
print("PHYSICAL_CUBE_CLAIM:", False)
print("MUTATION_PERFORMED:", False)
