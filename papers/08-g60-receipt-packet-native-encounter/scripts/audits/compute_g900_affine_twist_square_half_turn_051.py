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

def compose(left, right):
    return tuple(
        left[right[index]]
        for index in range(len(left))
    )

def power(permutation, exponent):
    result = tuple(range(len(permutation)))

    for _ in range(exponent):
        result = compose(permutation, result)

    return result

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

    affine = tuple(
        (multiplier, offset)
        for multiplier in range(5)
        for offset in range(5)
        if all(
            permutation[index]
            == (multiplier * index + offset) % 5
            for index in range(5)
        )
    )

    multiplier, offset = affine[0]

    fixed_index = next(
        index
        for index, image in enumerate(permutation)
        if index == image
    )

    centered = tuple(
        (
            permutation[(index + fixed_index) % 5]
            - fixed_index
        ) % 5
        for index in range(5)
    )

    square = power(centered, 2)
    cube = power(centered, 3)
    fourth = power(centered, 4)

    rows.append({
        "multiplier": multiplier,
        "offset": offset,
        "fixed_index": fixed_index,
        "centered_twist": centered,
        "square": square,
        "square_cycles": cycle_partition(square),
        "cube": cube,
        "fourth": fourth,
    })

identity = (0, 1, 2, 3, 4)
negation = (0, 4, 3, 2, 1)
expected_half_turn_cycles = (
    (0,),
    (1, 4),
    (2, 3),
)

square_profile = Counter(
    row["square"]
    for row in rows
)

square_cycle_profile = Counter(
    row["square_cycles"]
    for row in rows
)

checks = {
    "source_audit_pass":
        data.get("audit_pass") is True,
    "gauge_pair_count_100":
        len(rows) == 100,
    "all_centered_twists_are_multiply_2_or_3":
        all(
            row["centered_twist"] in {
                (0, 2, 4, 1, 3),
                (0, 3, 1, 4, 2),
            }
            for row in rows
        ),
    "every_square_is_negation_mod5":
        all(
            row["square"] == negation
            for row in rows
        ),
    "every_square_has_one_fixed_and_two_pairs":
        all(
            row["square_cycles"] == expected_half_turn_cycles
            for row in rows
        ),
    "every_fourth_power_is_identity":
        all(
            row["fourth"] == identity
            for row in rows
        ),
    "square_independent_of_orientation":
        square_profile == Counter({negation: 100}),
    "square_cycle_partition_independent_of_orientation":
        square_cycle_profile
        == Counter({expected_half_turn_cycles: 100}),
}

failed = [
    name
    for name, passed in checks.items()
    if not passed
]

theorem_pass = not failed

print("PACKET: g900_affine_twist_square_half_turn_051")
print("MODE: centered order-four power and involution census")
print("GAUGE_PAIR_COUNT:", len(rows))
print("CENTERED_FORWARD_TWIST:", (0, 2, 4, 1, 3))
print("CENTERED_INVERSE_TWIST:", (0, 3, 1, 4, 2))
print("COMMON_SQUARE:", negation)
print("COMMON_SQUARE_CYCLES:", expected_half_turn_cycles)
print("COMMON_FOURTH_POWER:", identity)
print("SQUARE_PROFILE:", dict(square_profile))
print("SQUARE_CYCLE_PROFILE:", dict(square_cycle_profile))
print("ROW_PREVIEW:", rows[:10])
print("CHECKS:", checks)
print("FAILED_CHECK_COUNT:", len(failed))
print("FAILED_CHECKS:", failed)
print("THEOREM_PASS:", theorem_pass)
print(
    "CLASSIFICATION:",
    (
        "the_two_oriented_native_affine_twists_have_the_same_"
        "square_x_maps_to_minus_x_modulo_5_fixing_the_centered_"
        "bridge_and_exchanging_two_pairs_of_moving_roles"
        if theorem_pass
        else "native_affine_twist_square_half_turn_not_derived"
    ),
)
print("COMMON_ORIENTATION_FREE_SQUARE_DERIVED:", theorem_pass)
print("SQUARE_IS_NEGATION_MOD5:", theorem_pass)
print("SQUARE_ROLE_PROFILE:", (1, 2, 2))
print("ORDER_FOUR_ORIENTATION_PAIR_COLLAPSES_AT_SQUARE:", theorem_pass)
print("NUMERIC_180_DEGREES_DERIVED_FROM_GRAPH:", False)
print("HALF_TURN_UNDER_FAITHFUL_SQUARE_GRID_REALIZATION:", theorem_pass)
print("PHYSICAL_ROTATION_CLAIM:", False)
print("MUTATION_PERFORMED:", False)
