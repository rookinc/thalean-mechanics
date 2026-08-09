#!/usr/bin/env python3

import json
import pathlib
from collections import Counter

J015 = pathlib.Path(
    "/data/data/com.termux/files/home/dev/cori/research/"
    "mathematics/41-order-4-dodecahedral-residue/"
    "artifacts/json/intrinsic_g15_line_petersen_audit_015.json"
)

J019 = pathlib.Path(
    "/data/data/com.termux/files/home/dev/cori/research/"
    "mathematics/41-order-4-dodecahedral-residue/"
    "artifacts/json/a5_v4_k22_four_slot_alignment_audit_019.json"
)

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def edge(left, right):
    return tuple(sorted((int(left), int(right))))

def walk(value, path="$"):
    yield path, value

    if isinstance(value, dict):
        for key, child in value.items():
            yield from walk(child, path + "." + str(key))

    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk(child, path + "[" + str(index) + "]")

a015 = load(J015)
a019 = load(J019)

alignment_candidates = []
for path, value in walk(a019):
    if (
        isinstance(value, list)
        and len(value) == 15
        and all(
            isinstance(row, dict)
            and "native_g15_state" in row
            and "standard_petersen_edge" in row
            for row in value
        )
    ):
        alignment_candidates.append((path, value))

if len(alignment_candidates) != 1:
    raise RuntimeError(
        "Expected one alignment table, found "
        + str(len(alignment_candidates))
    )

alignment_path, alignment_rows = alignment_candidates[0]

standard_edge_to_native = {
    edge(*row["standard_petersen_edge"]):
        int(row["native_g15_state"])
    for row in alignment_rows
}

native_to_standard_edge = {
    int(row["native_g15_state"]):
        edge(*row["standard_petersen_edge"])
    for row in alignment_rows
}

outer_edges = {
    "O" + str(i): edge(i, (i + 1) % 5)
    for i in range(5)
}

spoke_edges = {
    "S" + str(i): edge(i, 5 + i)
    for i in range(5)
}

inner_edges = {
    "I" + str(i):
        edge(5 + i, 5 + ((i + 2) % 5))
    for i in range(5)
}

bisector_edges = {
    **outer_edges,
    **spoke_edges,
    **inner_edges,
}

bisector_to_native = {
    name: standard_edge_to_native[source_edge]
    for name, source_edge in bisector_edges.items()
}

expected_native_edges = {
    edge(
        standard_edge_to_native[left_edge],
        standard_edge_to_native[right_edge],
    )
    for index, left_edge in enumerate(
        sorted(standard_edge_to_native)
    )
    for right_edge in sorted(standard_edge_to_native)[index + 1:]
    if set(left_edge) & set(right_edge)
}

native_quotient_rows = (
    a015["measurements"]["quotient_edges"]
)

native_quotient_edges = {
    edge(*row["quotient_edge"])
    for row in native_quotient_rows
}

native_edge_candidates = [
    (
        "$.measurements.quotient_edges",
        native_quotient_edges,
    )
]

native_candidate_paths = [
    path for path, candidate in native_edge_candidates
]

native_candidate_match_count = sum(
    candidate == expected_native_edges
    for path, candidate in native_edge_candidates
)

outer_native = tuple(
    bisector_to_native["O" + str(i)]
    for i in range(5)
)

spoke_native = tuple(
    bisector_to_native["S" + str(i)]
    for i in range(5)
)

inner_native = tuple(
    bisector_to_native["I" + str(i)]
    for i in range(5)
)

def induced_edges(vertices):
    selected = set(vertices)
    return {
        pair
        for pair in expected_native_edges
        if pair[0] in selected and pair[1] in selected
    }

outer_induced = induced_edges(outer_native)
spoke_induced = induced_edges(spoke_native)
inner_induced = induced_edges(inner_native)

def induced_degree_profile(vertices, edges):
    return Counter(
        sum(vertex in pair for pair in edges)
        for vertex in vertices
    )

checks = {
    "audit015_pass":
        a015.get("audit_pass") is True,
    "audit019_pass":
        a019.get("audit_pass") is True,
    "one_alignment_table_found":
        len(alignment_candidates) == 1,
    "alignment_row_count_15":
        len(alignment_rows) == 15,
    "standard_edge_map_is_bijection":
        len(standard_edge_to_native) == 15
        and set(standard_edge_to_native.values()) == set(range(15)),
    "bisector_label_count_15":
        len(bisector_to_native) == 15,
    "bisector_native_map_is_bijection":
        set(bisector_to_native.values()) == set(range(15)),
    "expected_native_edge_count_30":
        len(expected_native_edges) == 30,
    "native_adjacency_candidate_found":
        len(native_edge_candidates) >= 1,
    "all_native_adjacency_candidates_match":
        len(native_edge_candidates) >= 1
        and native_candidate_match_count
        == len(native_edge_candidates),
    "outer_register_is_native_C5":
        len(outer_induced) == 5
        and induced_degree_profile(
            outer_native, outer_induced
        ) == Counter({2: 5}),
    "pentagram_register_is_native_C5":
        len(inner_induced) == 5
        and induced_degree_profile(
            inner_native, inner_induced
        ) == Counter({2: 5}),
    "spoke_register_is_native_independent_set":
        len(spoke_induced) == 0,
    "registers_partition_native_G15":
        set(outer_native).isdisjoint(spoke_native)
        and set(outer_native).isdisjoint(inner_native)
        and set(spoke_native).isdisjoint(inner_native)
        and set(
            outer_native + spoke_native + inner_native
        ) == set(range(15)),
}

failed = [
    name
    for name, passed in checks.items()
    if not passed
]

theorem_pass = not failed

print("PACKET: g900_native_g15_edge_bisector_bridge_038b")
print("MODE: exact standard-Petersen-edge to native-G15 bridge")
print("ALIGNMENT_PATH:", alignment_path)
print("NATIVE_EDGE_CANDIDATE_PATHS:", native_candidate_paths)
print("NATIVE_EDGE_CANDIDATE_COUNT:",
      len(native_edge_candidates))
print("NATIVE_EDGE_MATCH_COUNT:",
      native_candidate_match_count)
print("BISECTOR_TO_NATIVE:", bisector_to_native)
print("OUTER_C5_NATIVE_ORDER:", outer_native)
print("PENTAGRAM_C5_NATIVE_ORDER:", inner_native)
print("SPOKE_NATIVE_REGISTER:", spoke_native)
print("EXPECTED_NATIVE_EDGE_COUNT:",
      len(expected_native_edges))
print("CHECKS:", checks)
print("FAILED_CHECK_COUNT:", len(failed))
print("FAILED_CHECKS:", failed)
print("THEOREM_PASS:", theorem_pass)
print(
    "CLASSIFICATION:",
    (
        "the_standard_Petersen_edge_bisectors_map_"
        "bijectively_to_native_G15_and_preserve_all_"
        "thirty_line_graph_adjacencies_with_exact_"
        "outer_C5_pentagram_C5_and_spoke_registers"
        if theorem_pass
        else "native_G15_edge_bisector_bridge_failed"
    ),
)
print("STANDARD_PETERSEN_LABELING_USED:", True)
print("CUBE_PROJECTION_IDENTIFIED:", False)
print("ABSOLUTE_CUBE_PLACEMENT_SELECTED:", False)
print("PHYSICAL_CLAIM:", False)
print("MUTATION_PERFORMED:", False)
