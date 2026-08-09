#!/usr/bin/env python3

import json
import pathlib

SOURCE = pathlib.Path(
    "/data/data/com.termux/files/home/dev/cori/research/"
    "mathematics/41-order-4-dodecahedral-residue/"
    "artifacts/json/intrinsic_g15_line_petersen_audit_015.json"
)

data = json.loads(SOURCE.read_text(encoding="utf-8"))

def edge(left, right):
    return tuple(sorted((int(left), int(right))))

native_edges = {
    edge(*row["quotient_edge"])
    for row in data["measurements"]["quotient_edges"]
}

INNER_ORDER = (13, 14, 7, 6, 10)
SPOKES = (11, 9, 12, 5, 8)

inner_edges = tuple(
    edge(
        INNER_ORDER[index],
        INNER_ORDER[(index + 1) % 5],
    )
    for index in range(5)
)

midpoint_by_edge = {
    pair: "Y_" + str(index)
    for index, pair in enumerate(inner_edges)
}

rows = []

for spoke in SPOKES:
    inner_neighbors = tuple(sorted(
        vertex
        for vertex in INNER_ORDER
        if edge(spoke, vertex) in native_edges
    ))

    inner_pair = edge(*inner_neighbors)
    midpoint = midpoint_by_edge[inner_pair]

    rows.append({
        "spoke_D": spoke,
        "inner_edge": inner_pair,
        "formal_midpoint_Y": midpoint,
        "triangle": tuple(sorted((
            spoke,
            inner_pair[0],
            inner_pair[1],
        ))),
    })

D_to_Y = {
    row["spoke_D"]: row["formal_midpoint_Y"]
    for row in rows
}

Y_to_D = {
    row["formal_midpoint_Y"]: row["spoke_D"]
    for row in rows
}

D_to_edge = {
    row["spoke_D"]: row["inner_edge"]
    for row in rows
}

edge_to_D = {
    row["inner_edge"]: row["spoke_D"]
    for row in rows
}

round_trip_D = {
    spoke: Y_to_D[D_to_Y[spoke]]
    for spoke in SPOKES
}

round_trip_Y = {
    midpoint: D_to_Y[Y_to_D[midpoint]]
    for midpoint in sorted(Y_to_D)
}

checks = {
    "source_audit_pass":
        data.get("audit_pass") is True,
    "inner_edge_count_5":
        len(inner_edges) == 5,
    "spoke_count_5":
        len(SPOKES) == 5,
    "one_inner_edge_per_spoke":
        len(D_to_edge) == 5,
    "one_spoke_per_inner_edge":
        len(edge_to_D) == 5,
    "D_to_Y_is_bijection":
        len(D_to_Y) == 5
        and len(set(D_to_Y.values())) == 5,
    "Y_to_D_inverse_exists":
        len(Y_to_D) == 5,
    "D_round_trip_identity":
        round_trip_D == {
            spoke: spoke
            for spoke in SPOKES
        },
    "Y_round_trip_identity":
        round_trip_Y == {
            midpoint: midpoint
            for midpoint in sorted(Y_to_D)
        },
    "all_spoke_edge_pairs_are_native_triangles":
        all(
            edge(row["spoke_D"], endpoint) in native_edges
            for row in rows
            for endpoint in row["inner_edge"]
        ),
}

failed = [
    name
    for name, passed in checks.items()
    if not passed
]

theorem_pass = not failed

print("PACKET: g900_spoke_midpoint_invertibility_053")
print("MODE: native triangle-tip to formal-edge-midpoint correspondence")
print("INNER_EDGE_ORDER:", inner_edges)
print("ROWS:", rows)
print("D_TO_Y:", D_to_Y)
print("Y_TO_D:", Y_to_D)
print("D_TO_EDGE:", D_to_edge)
print("EDGE_TO_D:", edge_to_D)
print("ROUND_TRIP_D:", round_trip_D)
print("ROUND_TRIP_Y:", round_trip_Y)
print("CHECKS:", checks)
print("FAILED_CHECK_COUNT:", len(failed))
print("FAILED_CHECKS:", failed)
print("THEOREM_PASS:", theorem_pass)
print(
    "CLASSIFICATION:",
    (
        "the_native_spoke_to_inner_edge_midpoint_"
        "correspondence_is_bijective_and_has_an_exact_inverse"
        if theorem_pass
        else "native_spoke_midpoint_invertibility_not_derived"
    ),
)
print("NATIVE_D_TO_Y_DEFINED:", theorem_pass)
print("NATIVE_Y_TO_D_DEFINED:", theorem_pass)
print("NATIVE_Y_TO_D_IS_NAN:", False)
print("TYPED_PARTIAL_D_TO_Y_RULE_MAY_HIDE_INVERSE:", theorem_pass)
print("DIRECTED_ARROW_SELECTED_BY_NATIVE_GRAPH:", False)
print("ANGLE_VALUE_TRANSPORTED:", False)
print("PHYSICAL_CLAIM:", False)
print("MUTATION_PERFORMED:", False)
