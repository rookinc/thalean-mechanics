#!/usr/bin/env python3

import itertools
import json
import pathlib
from collections import Counter, defaultdict, deque

SOURCE = pathlib.Path(
    "/data/data/com.termux/files/home/dev/cori/research/"
    "mathematics/41-order-4-dodecahedral-residue/"
    "artifacts/json/intrinsic_g15_line_petersen_audit_015.json"
)

data = json.loads(SOURCE.read_text(encoding="utf-8"))

def edge(left, right):
    return tuple(sorted((left, right)))

def degree_profile(vertices, edges):
    degrees = Counter()

    for vertex in vertices:
        degrees[sum(vertex in pair for pair in edges)] += 1

    return dict(sorted(degrees.items()))

def connected(vertices, edges):
    adjacency = defaultdict(set)

    for left, right in edges:
        adjacency[left].add(right)
        adjacency[right].add(left)

    start = next(iter(vertices))
    seen = {start}
    queue = deque([start])

    while queue:
        current = queue.popleft()

        for neighbor in adjacency[current]:
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)

    return seen == set(vertices)

LEFT = ("A", "B", "F")
RIGHT = ("C", "D", "E")
K33_VERTICES = LEFT + RIGHT

K33_EDGES = tuple(sorted(
    edge(left, right)
    for left in LEFT
    for right in RIGHT
))

INTERIOR_FIVE = {
    edge("A", "D"),
    edge("A", "E"),
    edge("B", "C"),
    edge("B", "D"),
    edge("D", "F"),
}

BOUNDARY_FOUR = set(K33_EDGES) - INTERIOR_FIVE

midpoint_by_edge = {
    pair: "M_" + pair[0] + pair[1]
    for pair in K33_EDGES
}

MIDPOINT_VERTICES = tuple(
    midpoint_by_edge[pair]
    for pair in K33_EDGES
)

SUBDIVISION_VERTICES = K33_VERTICES + MIDPOINT_VERTICES

SUBDIVISION_EDGES = tuple(sorted(
    edge(endpoint, midpoint_by_edge[pair])
    for pair in K33_EDGES
    for endpoint in pair
))

line_graph_edges = tuple(sorted(
    edge(
        midpoint_by_edge[left],
        midpoint_by_edge[right],
    )
    for left, right in itertools.combinations(K33_EDGES, 2)
    if set(left) & set(right)
))

native_edges = {
    edge(
        str(row["quotient_edge"][0]),
        str(row["quotient_edge"][1]),
    )
    for row in data["measurements"]["quotient_edges"]
}

native_vertices = tuple(
    str(index)
    for index in range(15)
)

subdivision_degree_profile = degree_profile(
    SUBDIVISION_VERTICES,
    SUBDIVISION_EDGES,
)

line_graph_degree_profile = degree_profile(
    MIDPOINT_VERTICES,
    line_graph_edges,
)

native_degree_profile = degree_profile(
    native_vertices,
    native_edges,
)

interior_midpoints = tuple(sorted(
    midpoint_by_edge[pair]
    for pair in INTERIOR_FIVE
))

boundary_midpoints = tuple(sorted(
    midpoint_by_edge[pair]
    for pair in BOUNDARY_FOUR
))

checks = {
    "source_audit_pass":
        data.get("audit_pass") is True,
    "k33_vertex_count_6":
        len(K33_VERTICES) == 6,
    "k33_edge_count_9":
        len(K33_EDGES) == 9,
    "edge_midpoint_count_9":
        len(MIDPOINT_VERTICES) == 9,
    "barycentric_vertex_count_15":
        len(SUBDIVISION_VERTICES) == 15,
    "barycentric_edge_count_18":
        len(SUBDIVISION_EDGES) == 18,
    "barycentric_degree_profile_3x6_2x9":
        subdivision_degree_profile == {2: 9, 3: 6},
    "barycentric_subdivision_connected":
        connected(SUBDIVISION_VERTICES, SUBDIVISION_EDGES),
    "midpoints_split_five_plus_four":
        len(interior_midpoints) == 5
        and len(boundary_midpoints) == 4,
    "midpoint_line_graph_vertex_count_9":
        len(MIDPOINT_VERTICES) == 9,
    "midpoint_line_graph_edge_count_18":
        len(line_graph_edges) == 18,
    "midpoint_line_graph_degree_profile_4x9":
        line_graph_degree_profile == {4: 9},
    "native_G15_vertex_count_15":
        len(native_vertices) == 15,
    "native_G15_edge_count_30":
        len(native_edges) == 30,
    "native_G15_degree_profile_4x15":
        native_degree_profile == {4: 15},
    "barycentric_and_G15_same_vertex_count":
        len(SUBDIVISION_VERTICES) == len(native_vertices),
    "barycentric_graph_not_isomorphic_to_G15_by_degree":
        subdivision_degree_profile != native_degree_profile,
}

failed = [
    name
    for name, passed in checks.items()
    if not passed
]

theorem_pass = not failed

print("PACKET: g900_k33_six_nine_barycentric_shadow_057")
print("MODE: exact six-vertex nine-midpoint incidence census")
print("K33_VERTICES:", K33_VERTICES)
print("K33_EDGES:", K33_EDGES)
print("MIDPOINT_VERTICES:", MIDPOINT_VERTICES)
print("INTERIOR_MIDPOINTS:", interior_midpoints)
print("BOUNDARY_MIDPOINTS:", boundary_midpoints)
print("SUBDIVISION_VERTEX_COUNT:", len(SUBDIVISION_VERTICES))
print("SUBDIVISION_EDGE_COUNT:", len(SUBDIVISION_EDGES))
print("SUBDIVISION_DEGREE_PROFILE:", subdivision_degree_profile)
print("MIDPOINT_LINE_GRAPH_EDGE_COUNT:", len(line_graph_edges))
print("MIDPOINT_LINE_GRAPH_DEGREE_PROFILE:", line_graph_degree_profile)
print("NATIVE_G15_VERTEX_COUNT:", len(native_vertices))
print("NATIVE_G15_EDGE_COUNT:", len(native_edges))
print("NATIVE_G15_DEGREE_PROFILE:", native_degree_profile)
print("CHECKS:", checks)
print("FAILED_CHECK_COUNT:", len(failed))
print("FAILED_CHECKS:", failed)
print("THEOREM_PASS:", theorem_pass)
print(
    "CLASSIFICATION:",
    (
        "the_projected_K3_3_has_an_exact_six_original_vertex_"
        "plus_nine_edge_midpoint_barycentric_shadow_of_total_"
        "size_fifteen_but_it_is_not_graph_isomorphic_to_native_"
        "G15"
        if theorem_pass
        else "K3_3_six_nine_barycentric_shadow_not_derived"
    ),
)
print("VERTEX_SIX_NINE_INTERPRETATION_DERIVED:", theorem_pass)
print("TOTAL_ROLE_COUNT_15:", theorem_pass)
print("NINE_MIDPOINTS_SPLIT_FIVE_FOUR:", theorem_pass)
print("BARYCENTRIC_SHADOW_EQUALS_NATIVE_G15_GRAPH:", False)
print("PROJECTION_OR_CORRESPONDENCE_STILL_REQUIRED:", True)
print("PHYSICAL_CUBE_CLAIM:", False)
print("MUTATION_PERFORMED:", False)
