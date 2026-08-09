#!/usr/bin/env python3

import itertools
from collections import Counter

VERTICES = ("A", "B", "C", "D", "E", "F")

def edge(left, right):
    return tuple(sorted((left, right)))

K33_EDGES = {
    edge(left, right)
    for left in ("A", "B", "F")
    for right in ("C", "D", "E")
}

INTERIOR_FIVE = (
    edge("A", "D"),
    edge("A", "E"),
    edge("B", "C"),
    edge("B", "D"),
    edge("D", "F"),
)

BOUNDARY_FOUR = (
    edge("A", "C"),
    edge("B", "E"),
    edge("C", "F"),
    edge("E", "F"),
)

CLOSURE_EDGE = edge("A", "B")

CLOSED_BOUNDARY_FIVE = (
    CLOSURE_EDGE,
    edge("A", "C"),
    edge("C", "F"),
    edge("E", "F"),
    edge("B", "E"),
)

REFLECTION = {
    "A": "B",
    "B": "A",
    "C": "E",
    "E": "C",
    "D": "D",
    "F": "F",
}

def reflect_edge(pair):
    return edge(
        REFLECTION[pair[0]],
        REFLECTION[pair[1]],
    )

def induced_permutation(objects, transform):
    index = {
        value: position
        for position, value in enumerate(objects)
    }

    return tuple(
        index[transform(value)]
        for value in objects
    )

def cycle_partition(permutation):
    seen = set()
    cycles = []

    for start in range(len(permutation)):
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

def equivariant_bijections(source_action, target_action):
    size = len(source_action)
    rows = []

    for mapping in itertools.permutations(range(size)):
        exact = all(
            mapping[source_action[index]]
            == target_action[mapping[index]]
            for index in range(size)
        )

        if exact:
            rows.append(mapping)

    return tuple(rows)

interior_action = induced_permutation(
    INTERIOR_FIVE,
    reflect_edge,
)

boundary_action = induced_permutation(
    BOUNDARY_FOUR,
    reflect_edge,
)

closed_boundary_action = induced_permutation(
    CLOSED_BOUNDARY_FIVE,
    reflect_edge,
)

AFFINE_HALF_TURN_FIVE = (0, 4, 3, 2, 1)
AFFINE_HALF_TURN_MOVING_FOUR = (3, 2, 1, 0)

interior_equivariant_maps = equivariant_bijections(
    interior_action,
    AFFINE_HALF_TURN_FIVE,
)

closed_boundary_equivariant_maps = equivariant_bijections(
    closed_boundary_action,
    AFFINE_HALF_TURN_FIVE,
)

boundary_equivariant_maps = equivariant_bijections(
    boundary_action,
    AFFINE_HALF_TURN_MOVING_FOUR,
)

interior_fixed_edges = tuple(
    INTERIOR_FIVE[index]
    for index, image in enumerate(interior_action)
    if index == image
)

closed_boundary_fixed_edges = tuple(
    CLOSED_BOUNDARY_FIVE[index]
    for index, image in enumerate(closed_boundary_action)
    if index == image
)

checks = {
    "k33_edge_count_9":
        len(K33_EDGES) == 9,
    "interior_edge_count_5":
        len(INTERIOR_FIVE) == 5,
    "boundary_edge_count_4":
        len(BOUNDARY_FOUR) == 4,
    "five_plus_four_partition_is_K33":
        set(INTERIOR_FIVE).isdisjoint(BOUNDARY_FOUR)
        and set(INTERIOR_FIVE) | set(BOUNDARY_FOUR)
        == K33_EDGES,
    "closure_adds_one_edge":
        CLOSURE_EDGE not in K33_EDGES,
    "closed_boundary_edge_count_5":
        len(CLOSED_BOUNDARY_FIVE) == 5,
    "reflection_preserves_interior_five":
        set(map(reflect_edge, INTERIOR_FIVE))
        == set(INTERIOR_FIVE),
    "reflection_preserves_boundary_four":
        set(map(reflect_edge, BOUNDARY_FOUR))
        == set(BOUNDARY_FOUR),
    "reflection_preserves_closed_boundary_five":
        set(map(reflect_edge, CLOSED_BOUNDARY_FIVE))
        == set(CLOSED_BOUNDARY_FIVE),
    "interior_reflection_profile_1_2_2":
        tuple(sorted(map(len, cycle_partition(interior_action))))
        == (1, 2, 2),
    "closed_boundary_reflection_profile_1_2_2":
        tuple(sorted(map(
            len,
            cycle_partition(closed_boundary_action),
        ))) == (1, 2, 2),
    "boundary_four_reflection_profile_2_2":
        tuple(sorted(map(len, cycle_partition(boundary_action))))
        == (2, 2),
    "interior_unique_fixed_edge_is_DF":
        interior_fixed_edges == (edge("D", "F"),),
    "closed_boundary_unique_fixed_edge_is_AB":
        closed_boundary_fixed_edges == (CLOSURE_EDGE,),
    "interior_matches_affine_half_turn":
        len(interior_equivariant_maps) == 8,
    "closed_boundary_matches_affine_half_turn":
        len(closed_boundary_equivariant_maps) == 8,
    "boundary_four_matches_moving_half_turn":
        len(boundary_equivariant_maps) == 8,
}

failed = [
    name
    for name, passed in checks.items()
    if not passed
]

theorem_pass = not failed

print("PACKET: g900_k33_five_four_half_turn_join_056")
print("MODE: projected edge split and affine-square action join")
print("K33_EDGE_COUNT:", len(K33_EDGES))
print("INTERIOR_FIVE:", INTERIOR_FIVE)
print("BOUNDARY_FOUR:", BOUNDARY_FOUR)
print("CLOSURE_EDGE:", CLOSURE_EDGE)
print("CLOSED_BOUNDARY_FIVE:", CLOSED_BOUNDARY_FIVE)
print("INTERIOR_REFLECTION_ACTION:", interior_action)
print("INTERIOR_REFLECTION_CYCLES:", cycle_partition(interior_action))
print("BOUNDARY_REFLECTION_ACTION:", boundary_action)
print("BOUNDARY_REFLECTION_CYCLES:", cycle_partition(boundary_action))
print(
    "CLOSED_BOUNDARY_REFLECTION_ACTION:",
    closed_boundary_action,
)
print(
    "CLOSED_BOUNDARY_REFLECTION_CYCLES:",
    cycle_partition(closed_boundary_action),
)
print("AFFINE_HALF_TURN_FIVE:", AFFINE_HALF_TURN_FIVE)
print(
    "AFFINE_HALF_TURN_MOVING_FOUR:",
    AFFINE_HALF_TURN_MOVING_FOUR,
)
print(
    "INTERIOR_EQUIVARIANT_BIJECTION_COUNT:",
    len(interior_equivariant_maps),
)
print(
    "CLOSED_BOUNDARY_EQUIVARIANT_BIJECTION_COUNT:",
    len(closed_boundary_equivariant_maps),
)
print(
    "BOUNDARY_EQUIVARIANT_BIJECTION_COUNT:",
    len(boundary_equivariant_maps),
)
print("INTERIOR_FIXED_EDGES:", interior_fixed_edges)
print(
    "CLOSED_BOUNDARY_FIXED_EDGES:",
    closed_boundary_fixed_edges,
)
print("CHECKS:", checks)
print("FAILED_CHECK_COUNT:", len(failed))
print("FAILED_CHECKS:", failed)
print("THEOREM_PASS:", theorem_pass)
print(
    "CLASSIFICATION:",
    (
        "the_projected_K3_3_edge_split_is_five_interior_plus_"
        "four_boundary_and_frame_closure_promotes_the_boundary_"
        "four_to_a_second_five_set_whose_reflection_action_"
        "matches_the_native_affine_half_turn_profile_1_2_2"
        if theorem_pass
        else "projected_five_four_half_turn_join_not_derived"
    ),
)
print("EDGE_FIVE_FOUR_SPLIT_DERIVED:", theorem_pass)
print("INTERIOR_FIXED_EDGE:", "DF" if theorem_pass else None)
print("CLOSED_BOUNDARY_FIXED_EDGE:", "AB" if theorem_pass else None)
print("COMMON_INVOLUTION_PROFILE:", (1, 2, 2))
print("CANONICAL_EQUIVARIANT_LABELING_SELECTED:", False)
print("NUMERIC_ANGLE_VALUES_DERIVED:", False)
print("PHYSICAL_CLAIM:", False)
print("MUTATION_PERFORMED:", False)
