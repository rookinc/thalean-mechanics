#!/usr/bin/env python3

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
        edge(order[index], order[(index + 1) % len(order)])
        for index in range(len(order))
    )

def permutation_order(permutation):
    current = tuple(range(len(permutation)))
    identity = current
    order = 0

    while True:
        current = tuple(permutation[value] for value in current)
        order += 1
        if current == identity:
            return order

def cycle_profile(permutation):
    seen = set()
    profile = []

    for start in range(len(permutation)):
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

OUTER_ORDER = (0, 4, 3, 2, 1)
INNER_ORDER = (13, 14, 7, 6, 10)
SPOKES = (11, 9, 12, 5, 8)

outer_edges = cycle_edges(OUTER_ORDER)
inner_edges = cycle_edges(INNER_ORDER)

outer_edge_index = {
    pair: index
    for index, pair in enumerate(outer_edges)
}

inner_edge_index = {
    pair: index
    for index, pair in enumerate(inner_edges)
}

bridge_rows = []

for spoke in SPOKES:
    outer_neighbors = tuple(sorted(
        vertex
        for vertex in OUTER_ORDER
        if edge(spoke, vertex) in native_edges
    ))
    inner_neighbors = tuple(sorted(
        vertex
        for vertex in INNER_ORDER
        if edge(spoke, vertex) in native_edges
    ))

    inner_pair = edge(*inner_neighbors)
    outer_pair = edge(*outer_neighbors)

    bridge_rows.append({
        "spoke_D": spoke,
        "inner_edge": inner_pair,
        "inner_edge_index": inner_edge_index[inner_pair],
        "outer_edge": outer_pair,
        "outer_edge_index": outer_edge_index[outer_pair],
    })

bridge_rows.sort(key=lambda row: row["inner_edge_index"])

edge_index_permutation = tuple(
    row["outer_edge_index"]
    for row in bridge_rows
)

affine_candidates = tuple(
    (multiplier, offset)
    for multiplier in range(5)
    for offset in range(5)
    if all(
        edge_index_permutation[index]
        == (multiplier * index + offset) % 5
        for index in range(5)
    )
)

inverse_permutation = tuple(
    edge_index_permutation.index(index)
    for index in range(5)
)

inverse_affine_candidates = tuple(
    (multiplier, offset)
    for multiplier in range(5)
    for offset in range(5)
    if all(
        inverse_permutation[index]
        == (multiplier * index + offset) % 5
        for index in range(5)
    )
)

fixed_indices = tuple(
    index
    for index, image in enumerate(edge_index_permutation)
    if image == index
)

forward_formula = tuple(
    (2 * index + 1) % 5
    for index in range(5)
)

inverse_formula = tuple(
    (3 * index + 2) % 5
    for index in range(5)
)

checks = {
    "source_audit_pass":
        data.get("audit_pass") is True,
    "outer_cycle_has_five_edges":
        len(outer_edges) == 5,
    "inner_cycle_has_five_edges":
        len(inner_edges) == 5,
    "bridge_row_count_5":
        len(bridge_rows) == 5,
    "edge_index_map_is_permutation":
        sorted(edge_index_permutation) == list(range(5)),
    "forward_affine_law_is_2i_plus_1":
        edge_index_permutation == forward_formula,
    "unique_forward_affine_description":
        affine_candidates == ((2, 1),),
    "inverse_affine_law_is_3i_plus_2":
        inverse_permutation == inverse_formula,
    "unique_inverse_affine_description":
        inverse_affine_candidates == ((3, 2),),
    "twist_permutation_order_4":
        permutation_order(edge_index_permutation) == 4,
    "twist_cycle_profile_1_4":
        cycle_profile(edge_index_permutation) == (1, 4),
    "unique_fixed_edge_index":
        fixed_indices == (4,),
    "multiplier_has_order_4_modulo_5":
        tuple(pow(2, exponent, 5) for exponent in range(1, 5))
        == (2, 4, 3, 1),
}

failed = [
    name
    for name, passed in checks.items()
    if not passed
]

theorem_pass = not failed

print("PACKET: g900_native_c5_edge_affine_twist_046")
print("MODE: exact inner-to-outer C5 edge-index correspondence")
print("OUTER_C5_ORDER:", OUTER_ORDER)
print("OUTER_EDGE_ORDER:", outer_edges)
print("INNER_C5_ORDER:", INNER_ORDER)
print("INNER_EDGE_ORDER:", inner_edges)
print("BRIDGE_ROWS:", bridge_rows)
print("EDGE_INDEX_PERMUTATION:", edge_index_permutation)
print("AFFINE_CANDIDATES:", affine_candidates)
print("INVERSE_PERMUTATION:", inverse_permutation)
print("INVERSE_AFFINE_CANDIDATES:", inverse_affine_candidates)
print("PERMUTATION_ORDER:", permutation_order(edge_index_permutation))
print("PERMUTATION_CYCLE_PROFILE:", cycle_profile(edge_index_permutation))
print("FIXED_EDGE_INDICES:", fixed_indices)
print("CHECKS:", checks)
print("FAILED_CHECK_COUNT:", len(failed))
print("FAILED_CHECKS:", failed)
print("THEOREM_PASS:", theorem_pass)
print(
    "CLASSIFICATION:",
    (
        "the_native_spoke_bridge_identifies_inner_and_outer_"
        "C5_edge_registers_by_the_order_four_affine_twist_"
        "j_equals_2i_plus_1_modulo_5"
        if theorem_pass
        else "native_C5_edge_affine_twist_not_derived"
    ),
)
print("ORDER_FOUR_PENTAGRAM_TWIST_DERIVED:", theorem_pass)
print("INVERSE_TWIST_MULTIPLIER:", 3 if theorem_pass else None)
print("ABSOLUTE_C5_ORIENTATION_SELECTED:", False)
print("ANGLE_180_DERIVED:", False)
print("PHYSICAL_ROTATION_CLAIM:", False)
print("MUTATION_PERFORMED:", False)
