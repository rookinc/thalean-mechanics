#!/usr/bin/env python3

import json
import pathlib
from collections import Counter

SOURCE_015 = pathlib.Path(
    "/data/data/com.termux/files/home/dev/cori/research/"
    "mathematics/41-order-4-dodecahedral-residue/"
    "artifacts/json/intrinsic_g15_line_petersen_audit_015.json"
)

SOURCE_019 = pathlib.Path(
    "/data/data/com.termux/files/home/dev/cori/research/"
    "mathematics/41-order-4-dodecahedral-residue/"
    "artifacts/json/a5_v4_k22_four_slot_alignment_audit_019.json"
)

audit015 = json.loads(SOURCE_015.read_text(encoding="utf-8"))
audit019 = json.loads(SOURCE_019.read_text(encoding="utf-8"))

def edge(left, right):
    return tuple(sorted((int(left), int(right))))

def cycle_edges(order):
    return tuple(
        edge(order[index], order[(index + 1) % 5])
        for index in range(5)
    )

native_edges = {
    edge(*row["quotient_edge"])
    for row in audit015["measurements"]["quotient_edges"]
}

alignment_rows = audit019["measurements"]["alignment_rows"]

alignment_by_state = {
    int(row["native_g15_state"]): row
    for row in alignment_rows
}

OUTER_ORDER = (0, 4, 3, 2, 1)
INNER_ORDER = (13, 14, 7, 6, 10)
SPOKES = (11, 9, 12, 5, 8)

outer_edges = cycle_edges(OUTER_ORDER)
inner_edges = cycle_edges(INNER_ORDER)

outer_index = {
    pair: index
    for index, pair in enumerate(outer_edges)
}

inner_index = {
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

    outer_pair = edge(*outer_neighbors)
    inner_pair = edge(*inner_neighbors)

    carrier_pair = tuple(
        int(value)
        for value in alignment_by_state[spoke][
            "pentagram_twist_multipliers"
        ]
    )

    bridge_rows.append({
        "spoke_D": spoke,
        "outer_edge": outer_pair,
        "outer_edge_index": outer_index[outer_pair],
        "inner_edge": inner_pair,
        "inner_edge_index": inner_index[inner_pair],
        "pentagram_twist_multipliers": carrier_pair,
        "contains_forward_multiplier_2":
            2 in carrier_pair,
        "contains_inverse_multiplier_3":
            3 in carrier_pair,
    })

bridge_rows.sort(key=lambda row: row["inner_edge_index"])

inner_to_outer = tuple(
    row["outer_edge_index"]
    for row in bridge_rows
)

bridge_rows_by_outer = sorted(
    bridge_rows,
    key=lambda row: row["outer_edge_index"],
)

outer_to_inner = tuple(
    row["inner_edge_index"]
    for row in bridge_rows_by_outer
)

spoke_carrier_pairs = tuple(
    row["pentagram_twist_multipliers"]
    for row in bridge_rows
)

spoke_pair_profile = Counter(spoke_carrier_pairs)

spoke_multiplier_occurrences = Counter(
    multiplier
    for pair in spoke_carrier_pairs
    for multiplier in pair
)

spoke_multiplier_support = {
    multiplier: tuple(
        row["spoke_D"]
        for row in bridge_rows
        if multiplier in row["pentagram_twist_multipliers"]
    )
    for multiplier in (2, 3)
}

spoke_common_multiplier_set = set(
    spoke_carrier_pairs[0]
)

for pair in spoke_carrier_pairs[1:]:
    spoke_common_multiplier_set.intersection_update(pair)

inner_carrier_pairs = tuple(
    tuple(
        int(value)
        for value in alignment_by_state[state][
            "pentagram_twist_multipliers"
        ]
    )
    for state in INNER_ORDER
)

outer_carrier_pairs = tuple(
    tuple(
        int(value)
        for value in alignment_by_state[state][
            "pentagram_twist_multipliers"
        ]
    )
    for state in OUTER_ORDER
)

checks = {
    "audit015_pass":
        audit015.get("audit_pass") is True,
    "audit019_pass":
        audit019.get("audit_pass") is True,
    "alignment_row_count_15":
        len(alignment_rows) == 15,
    "spoke_row_count_5":
        len(bridge_rows) == 5,
    "inner_to_outer_is_2i_plus_1":
        inner_to_outer == tuple(
            (2 * index + 1) % 5
            for index in range(5)
        ),
    "outer_to_inner_is_3j_plus_2":
        outer_to_inner == tuple(
            (3 * index + 2) % 5
            for index in range(5)
        ),
    "every_spoke_carrier_pair_contains_inverse_3":
        all(
            row["contains_inverse_multiplier_3"]
            for row in bridge_rows
        ),
    "not_every_spoke_carrier_pair_contains_forward_2":
        not all(
            row["contains_forward_multiplier_2"]
            for row in bridge_rows
        ),
    "spoke_common_multiplier_is_exactly_3":
        spoke_common_multiplier_set == {3},
    "all_inner_states_contain_multiplier_3":
        all(3 in pair for pair in inner_carrier_pairs),
    "outer_states_do_not_all_contain_multiplier_3":
        not all(3 in pair for pair in outer_carrier_pairs),
}

failed = [
    name
    for name, passed in checks.items()
    if not passed
]

theorem_pass = not failed

print("PACKET: g900_spoke_twist_carrier_direction_join_049")
print("MODE: frozen native-label bridge and carrier join")
print("INNER_TO_OUTER_INDEX_MAP:", inner_to_outer)
print("INNER_TO_OUTER_AFFINE_LAW: j = 2*i + 1 mod 5")
print("OUTER_TO_INNER_INDEX_MAP:", outer_to_inner)
print("OUTER_TO_INNER_AFFINE_LAW: i = 3*j + 2 mod 5")
print("BRIDGE_ROWS:", bridge_rows)
print("SPOKE_CARRIER_PAIR_PROFILE:", dict(spoke_pair_profile))
print(
    "SPOKE_MULTIPLIER_OCCURRENCES:",
    dict(sorted(spoke_multiplier_occurrences.items())),
)
print(
    "SPOKE_MULTIPLIER_SUPPORT:",
    spoke_multiplier_support,
)
print(
    "SPOKE_COMMON_MULTIPLIER_SET:",
    tuple(sorted(spoke_common_multiplier_set)),
)
print("INNER_CARRIER_PAIRS:", inner_carrier_pairs)
print("OUTER_CARRIER_PAIRS:", outer_carrier_pairs)
print("CHECKS:", checks)
print("FAILED_CHECK_COUNT:", len(failed))
print("FAILED_CHECKS:", failed)
print("THEOREM_PASS:", theorem_pass)
print(
    "CLASSIFICATION:",
    (
        "in_the_frozen_native_C5_coordinates_the_universal_"
        "spoke_carrier_multiplier_3_equals_the_outer_to_inner_"
        "inverse_affine_bridge_multiplier"
        if theorem_pass
        else "spoke_carrier_directional_join_not_derived"
    ),
)
print("UNIVERSAL_SPOKE_CARRIER_MULTIPLIER:", 3 if theorem_pass else None)
print("MATCHED_BRIDGE_DIRECTION:", "outer_to_inner" if theorem_pass else None)
print("FORWARD_MULTIPLIER_UNIVERSAL_ON_SPOKES:", False)
print("ABSOLUTE_ORIENTATION_SELECTED:", False)
print("ANGLE_180_DERIVED:", False)
print("PHYSICAL_ROTATION_CLAIM:", False)
print("MUTATION_PERFORMED:", False)
