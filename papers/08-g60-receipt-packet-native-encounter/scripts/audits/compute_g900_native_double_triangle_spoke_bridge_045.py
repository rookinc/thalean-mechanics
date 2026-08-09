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

native_edges = {
    edge(*row["quotient_edge"])
    for row in data["measurements"]["quotient_edges"]
}

adjacency = {
    vertex: {
        other
        for pair in native_edges
        if vertex in pair
        for other in pair
        if other != vertex
    }
    for vertex in range(15)
}

outer_order = (0, 4, 3, 2, 1)
inner_order = (13, 14, 7, 6, 10)
spoke_register = (11, 9, 12, 5, 8)

def cycle_edges(order):
    return {
        edge(order[index], order[(index + 1) % len(order)])
        for index in range(len(order))
    }

outer_edges = cycle_edges(outer_order)
inner_edges = cycle_edges(inner_order)

bridge_rows = []

for spoke in spoke_register:
    outer_neighbors = tuple(sorted(
        adjacency[spoke] & set(outer_order)
    ))
    inner_neighbors = tuple(sorted(
        adjacency[spoke] & set(inner_order)
    ))

    outer_edge = (
        edge(*outer_neighbors)
        if len(outer_neighbors) == 2
        else None
    )

    inner_edge = (
        edge(*inner_neighbors)
        if len(inner_neighbors) == 2
        else None
    )

    outer_triangle = (
        tuple(sorted((*outer_neighbors, spoke)))
        if len(outer_neighbors) == 2
        else None
    )

    inner_triangle = (
        tuple(sorted((*inner_neighbors, spoke)))
        if len(inner_neighbors) == 2
        else None
    )

    bridge_rows.append({
        "spoke_D": spoke,
        "inner_edge": inner_edge,
        "outer_edge": outer_edge,
        "inner_triangle": inner_triangle,
        "outer_triangle": outer_triangle,
        "inner_edge_native":
            inner_edge in native_edges
            if inner_edge is not None else False,
        "outer_edge_native":
            outer_edge in native_edges
            if outer_edge is not None else False,
        "two_disjoint_base_edges":
            (
                inner_edge is not None
                and outer_edge is not None
                and set(inner_edge).isdisjoint(outer_edge)
            ),
    })

inner_edge_to_spoke = {
    row["inner_edge"]: row["spoke_D"]
    for row in bridge_rows
}

outer_edge_to_spoke = {
    row["outer_edge"]: row["spoke_D"]
    for row in bridge_rows
}

inner_to_outer = {
    row["inner_edge"]: row["outer_edge"]
    for row in bridge_rows
}

all_triangles = {
    row["inner_triangle"]
    for row in bridge_rows
} | {
    row["outer_triangle"]
    for row in bridge_rows
}

vertex_triangle_counts = Counter(
    vertex
    for triangle in all_triangles
    for vertex in triangle
)

checks = {
    "source_audit_pass":
        data.get("audit_pass") is True,
    "outer_register_is_C5":
        len(outer_edges) == 5
        and all(pair in native_edges for pair in outer_edges),
    "inner_register_is_C5":
        len(inner_edges) == 5
        and all(pair in native_edges for pair in inner_edges),
    "spoke_register_count_5":
        len(spoke_register) == 5,
    "every_spoke_has_two_outer_neighbors":
        all(
            len(adjacency[spoke] & set(outer_order)) == 2
            for spoke in spoke_register
        ),
    "every_spoke_has_two_inner_neighbors":
        all(
            len(adjacency[spoke] & set(inner_order)) == 2
            for spoke in spoke_register
        ),
    "every_outer_neighbor_pair_is_cycle_edge":
        all(
            row["outer_edge"] in outer_edges
            for row in bridge_rows
        ),
    "every_inner_neighbor_pair_is_cycle_edge":
        all(
            row["inner_edge"] in inner_edges
            for row in bridge_rows
        ),
    "inner_edges_used_exactly_once":
        set(inner_edge_to_spoke) == inner_edges
        and len(inner_edge_to_spoke) == 5,
    "outer_edges_used_exactly_once":
        set(outer_edge_to_spoke) == outer_edges
        and len(outer_edge_to_spoke) == 5,
    "inner_to_outer_is_bijection":
        len(inner_to_outer) == 5
        and set(inner_to_outer) == inner_edges
        and set(inner_to_outer.values()) == outer_edges,
    "ten_native_triangles_recovered":
        len(all_triangles) == 10,
    "each_spoke_lies_in_exactly_two_triangles":
        all(
            vertex_triangle_counts[spoke] == 2
            for spoke in spoke_register
        ),
    "each_cycle_vertex_lies_in_two_triangles":
        all(
            vertex_triangle_counts[vertex] == 2
            for vertex in set(outer_order) | set(inner_order)
        ),
    "base_edges_are_disjoint_across_each_spoke":
        all(
            row["two_disjoint_base_edges"]
            for row in bridge_rows
        ),
}

failed = [
    name
    for name, passed in checks.items()
    if not passed
]

theorem_pass = not failed

print("PACKET: g900_native_double_triangle_spoke_bridge_045")
print("MODE: exact inner-edge to spoke to outer-edge census")
print("OUTER_C5_ORDER:", outer_order)
print("INNER_C5_ORDER:", inner_order)
print("SPOKE_REGISTER:", spoke_register)
print("BRIDGE_ROWS:", bridge_rows)
print("INNER_EDGE_TO_SPOKE:", inner_edge_to_spoke)
print("OUTER_EDGE_TO_SPOKE:", outer_edge_to_spoke)
print("INNER_TO_OUTER_EDGE_BIJECTION:",
      inner_to_outer)
print("TRIANGLE_COUNT:", len(all_triangles))
print("VERTEX_TRIANGLE_COUNTS:",
      dict(sorted(vertex_triangle_counts.items())))
print("CHECKS:", checks)
print("FAILED_CHECK_COUNT:", len(failed))
print("FAILED_CHECKS:", failed)
print("THEOREM_PASS:", theorem_pass)
print(
    "CLASSIFICATION:",
    (
        "each_native_spoke_D_is_the_common_tip_of_one_"
        "inner_pentagram_triangle_and_one_outer_pentagon_"
        "triangle_giving_a_bijection_between_the_two_C5_"
        "edge_registers"
        if theorem_pass
        else "native_double_triangle_spoke_bridge_failed"
    ),
)
print("FORMAL_MIDPOINT_PAIR_PER_SPOKE:",
      theorem_pass)
print("MIDPOINT_PAIR_VALUE_180_DERIVED:", False)
print("PHYSICAL_FOLD_CLAIM:", False)
print("MUTATION_PERFORMED:", False)
