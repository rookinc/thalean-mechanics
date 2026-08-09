#!/usr/bin/env python3

import json
import pathlib
from collections import Counter, deque

SOURCE = pathlib.Path(
    "/data/data/com.termux/files/home/dev/cori/research/"
    "mathematics/41-order-4-dodecahedral-residue/"
    "artifacts/json/intrinsic_g15_line_petersen_audit_015.json"
)

data = json.loads(SOURCE.read_text(encoding="utf-8"))

def edge(left, right):
    return tuple(sorted((left, right)))

native_edges = {
    edge(*row["quotient_edge"])
    for row in data["measurements"]["quotient_edges"]
}

native_vertices = tuple(range(15))

native_adjacency = {
    vertex: {
        other
        for pair in native_edges
        if vertex in pair
        for other in pair
        if other != vertex
    }
    for vertex in native_vertices
}

def distances_from(start):
    distances = {start: 0}
    queue = deque([start])

    while queue:
        current = queue.popleft()
        for neighbor in native_adjacency[current]:
            if neighbor not in distances:
                distances[neighbor] = distances[current] + 1
                queue.append(neighbor)

    return distances

native_distances = {
    vertex: distances_from(vertex)
    for vertex in native_vertices
}

drawing_vertices = ("A", "B", "C", "D", "E", "F")
left_part = {"A", "B", "F"}
right_part = {"C", "D", "E"}

k33_edges = {
    edge(left, right)
    for left in left_part
    for right in right_part
}

k33_nonedges = {
    edge(left, right)
    for index, left in enumerate(drawing_vertices)
    for right in drawing_vertices[index + 1:]
    if edge(left, right) not in k33_edges
}

cycle_order = ("A", "B", "E", "F", "C")
native_cycle = (13, 14, 7, 6, 10)

cycle_maps = []

for orientation, base in (
    ("forward", native_cycle),
    ("reverse", tuple(reversed(native_cycle))),
):
    for shift in range(5):
        target = base[shift:] + base[:shift]
        cycle_maps.append({
            "orientation": orientation,
            "shift": shift,
            "mapping": dict(zip(cycle_order, target)),
        })

rows = []

for cycle_row in cycle_maps:
    used = set(cycle_row["mapping"].values())

    for native_D in native_vertices:
        if native_D in used:
            continue

        mapping = {
            **cycle_row["mapping"],
            "D": native_D,
        }

        desired_distance_profile = Counter(
            native_distances[mapping[left]][mapping[right]]
            for left, right in k33_edges
        )

        desired_native_edges = {
            pair
            for pair in k33_edges
            if edge(mapping[pair[0]], mapping[pair[1]])
            in native_edges
        }

        preserved_nonedges = {
            pair
            for pair in k33_nonedges
            if edge(mapping[pair[0]], mapping[pair[1]])
            not in native_edges
        }

        induced_mismatch_count = (
            len(k33_edges - desired_native_edges)
            + len(k33_nonedges - preserved_nonedges)
        )

        D_neighbor_images = tuple(sorted(
            mapping[neighbor]
            for neighbor in ("A", "B", "F")
            if edge(native_D, mapping[neighbor]) in native_edges
        ))

        rows.append({
            "orientation": cycle_row["orientation"],
            "shift": cycle_row["shift"],
            "native_D": native_D,
            "mapping": mapping,
            "preserved_K33_edge_count":
                len(desired_native_edges),
            "preserved_K33_nonedge_count":
                len(preserved_nonedges),
            "desired_distance_profile":
                dict(sorted(desired_distance_profile.items())),
            "induced_mismatch_count":
                induced_mismatch_count,
            "D_to_A_B_F_adjacency_count":
                len(D_neighbor_images),
            "D_neighbor_images":
                D_neighbor_images,
        })

rows.sort(key=lambda row: (
    row["induced_mismatch_count"],
    -row["preserved_K33_edge_count"],
    -row["preserved_K33_nonedge_count"],
    row["orientation"],
    row["shift"],
    row["native_D"],
))

best_mismatch = rows[0]["induced_mismatch_count"]
best_rows = [
    row for row in rows
    if row["induced_mismatch_count"] == best_mismatch
]

exact_edge_homomorphisms = [
    row for row in rows
    if row["preserved_K33_edge_count"] == 9
]

exact_induced_embeddings = [
    row for row in rows
    if row["induced_mismatch_count"] == 0
]

D_three_neighbor_rows = [
    row for row in rows
    if row["D_to_A_B_F_adjacency_count"] == 3
]

checks = {
    "source_audit_pass":
        data.get("audit_pass") is True,
    "native_g15_vertex_count_15":
        len(native_vertices) == 15,
    "native_g15_edge_count_30":
        len(native_edges) == 30,
    "cycle_registration_count_10":
        len(cycle_maps) == 10,
    "tested_mapping_count_100":
        len(rows) == 100,
    "no_exact_induced_K33_embedding":
        len(exact_induced_embeddings) == 0,
    "no_exact_K33_edge_homomorphism":
        len(exact_edge_homomorphisms) == 0,
    "no_native_D_adjacent_to_all_A_B_F_images":
        len(D_three_neighbor_rows) == 0,
    "best_rows_exist":
        len(best_rows) > 0,
}

failed = [
    name
    for name, passed in checks.items()
    if not passed
]

theorem_pass = not failed

print("PACKET: g900_k33_to_native_g15_projection_distortion_043b")
print("MODE: exhaustive cycle-registered six-point projection test")
print("TESTED_MAPPING_COUNT:", len(rows))
print("EXACT_EDGE_HOMOMORPHISM_COUNT:",
      len(exact_edge_homomorphisms))
print("EXACT_INDUCED_EMBEDDING_COUNT:",
      len(exact_induced_embeddings))
print("D_THREE_NEIGHBOR_ROW_COUNT:",
      len(D_three_neighbor_rows))
print("BEST_MISMATCH_COUNT:", best_mismatch)
print("BEST_ROW_COUNT:", len(best_rows))
print("BEST_ROWS:", best_rows)
print("GLOBAL_PRESERVED_EDGE_PROFILE:",
      dict(Counter(
          row["preserved_K33_edge_count"]
          for row in rows
      )))
print("CHECKS:", checks)
print("FAILED_CHECK_COUNT:", len(failed))
print("FAILED_CHECKS:", failed)
print("THEOREM_PASS:", theorem_pass)
print(
    "CLASSIFICATION:",
    (
        "the_cycle_registered_K3_3_frame_has_no_"
        "adjacency_faithful_embedding_into_native_G15_"
        "and_requires_a_genuinely_nonfaithful_projection"
        if theorem_pass
        else "unexpected_faithful_K3_3_projection_found"
    ),
)
print("CUBE_FRAME_IS_NATIVE_G15_SUBGRAPH:", False)
print("PROJECTION_DISTORTION_MEASURED:", theorem_pass)
print("PHYSICAL_CLAIM:", False)
print("MUTATION_PERFORMED:", False)
