#!/usr/bin/env python3

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from collections import Counter, deque
from pathlib import Path


HOME = Path.home()

TARGET = (
    HOME
    / "dev/cori/research/thalean_mechanics/papers"
    / "08-g60-receipt-packet-native-encounter"
)

MATH42 = (
    HOME
    / "dev/cori/research/mathematics"
    / "42-graph-automorphism-groups"
)

PHYSICS = (
    HOME
    / "dev/cori/research/physics/quantum_mechanics"
    / "01-the-electron-spins-twice"
)

BLIND = (
    TARGET
    / "artifacts/receipts"
    / "g60_native_semiregular_receipt_action_census_002_mac.txt"
)

ACTION = (
    MATH42
    / "artifacts/json/native_g60_fiber_product_isomorphism_044.json"
)

G15_CERT = (
    MATH42
    / "sources/project41-paper42"
    / "project42_native_voltage_derivation_certificate_033.json"
)

G30_CERT = (
    MATH42
    / "sources/project42_g60_to_g30_a_quotient_certificate_035.json"
)

G60_EDGES = PHYSICS / "paper/data/g60_local_edges.csv"

EXPECTED_HASHES = {
    "blind": "9d0f1ef5975cd8cd2575192012c8bfeefe15c2856d6646e827ffc4ada851f383",
    "action": "b37313b135495752b11e525bb61979163fdf54aec4be4f5d027dcee64c9efc21",
    "g15_certificate": "9d5046dec7ea5d32f88782aa158a79082d4facf6f0b4fd4a7d3a3e4c552a0f70",
    "g30_certificate": "acaf79c52d5d83915afc425ba5b2e0547f168b73d1db7f144898599d30654822",
    "g60_edges": "c700a185fab6a5f434da09b7acb716b96c76170774bee946af8ea907e4fe7f9f",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def status(path: Path) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(path), "status", "--short"],
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line]


def compose(p, q):
    return tuple(p[q[index]] for index in range(len(p)))


def norm_edge(u: int, v: int) -> tuple[int, int]:
    return (u, v) if u <= v else (v, u)


def permutation_order(permutation) -> int:
    identity = tuple(range(len(permutation)))
    current = identity
    for order in range(1, 1000):
        current = compose(permutation, current)
        if current == identity:
            return order
    raise RuntimeError("permutation order bound exceeded")


def subgroup_closure(identity, generators):
    subgroup = {identity}
    changed = True

    while changed:
        changed = False
        current = list(subgroup)
        for left in current + list(generators):
            for right in current + list(generators):
                product = compose(left, right)
                if product not in subgroup:
                    subgroup.add(product)
                    changed = True

    return subgroup


def vertex_orbits(subgroup, vertex_count):
    remaining = set(range(vertex_count))
    orbits = []

    while remaining:
        seed = min(remaining)
        orbit = tuple(sorted({permutation[seed] for permutation in subgroup}))
        orbits.append(orbit)
        remaining.difference_update(orbit)

    return sorted(orbits)


def graph_isomorphisms(source_vertices, source_edges, target_vertices, target_edges):
    source_adj = {vertex: set() for vertex in source_vertices}
    target_adj = {vertex: set() for vertex in target_vertices}

    for u, v in source_edges:
        source_adj[u].add(v)
        source_adj[v].add(u)

    for u, v in target_edges:
        target_adj[u].add(v)
        target_adj[v].add(u)

    mappings = []

    def recurse(mapping, used_targets):
        if len(mapping) == len(source_vertices):
            mappings.append(dict(mapping))
            return

        unmapped = [
            vertex
            for vertex in source_vertices
            if vertex not in mapping
        ]

        source = max(
            unmapped,
            key=lambda vertex: (
                sum(neighbor in mapping for neighbor in source_adj[vertex]),
                -vertex,
            ),
        )

        candidates = [
            target
            for target in target_vertices
            if target not in used_targets
            and len(source_adj[source]) == len(target_adj[target])
        ]

        for target in sorted(candidates):
            compatible = True

            for mapped_source, mapped_target in mapping.items():
                source_relation = mapped_source in source_adj[source]
                target_relation = mapped_target in target_adj[target]

                if source_relation != target_relation:
                    compatible = False
                    break

            if not compatible:
                continue

            mapping[source] = target
            used_targets.add(target)
            recurse(mapping, used_targets)
            used_targets.remove(target)
            del mapping[source]

    recurse({}, set())
    return mappings


roots = [TARGET, MATH42, PHYSICS]
status_before = {str(root): status(root) for root in roots}

paths = {
    "blind": BLIND,
    "action": ACTION,
    "g15_certificate": G15_CERT,
    "g30_certificate": G30_CERT,
    "g60_edges": G60_EDGES,
}

actual_hashes = {name: sha256(path) for name, path in paths.items()}

print("OUT ==")
print("PACKET: g60_normal_v4_g15_quotient_unblinding_007")
print("MODE: read-only preregistered normal-V4 quotient comparison")
print(f"TARGET: {TARGET}")
print("REPOSITORY_MUTATION: none")

print()
print("== SOURCE LOCK ==")
for name in paths:
    print(f"{name.upper()}_SHA256: {actual_hashes[name]}")
    print(
        f"CHECK_{name.upper()}_HASH:",
        str(actual_hashes[name] == EXPECTED_HASHES[name]).lower(),
    )

if actual_hashes != EXPECTED_HASHES:
    raise RuntimeError("source hash mismatch")

blind_text = BLIND.read_text(encoding="utf-8")
classes = []

for line in blind_text.splitlines():
    prefix = "RECEIPT_ACTION_CLASS: "
    if line.startswith(prefix):
        classes.append(json.loads(line[len(prefix):]))

normal_v4_classes = [
    row
    for row in classes
    if row["group_label"] == "V4"
    and row["group_order"] == 4
    and row["conjugate_subgroup_count"] == 1
]

normal_c2_classes = [
    row
    for row in classes
    if row["group_label"] == "C2"
    and row["group_order"] == 2
    and row["conjugate_subgroup_count"] == 1
]

if len(normal_v4_classes) != 1:
    raise RuntimeError("blind census does not contain one normal V4 class")

if len(normal_c2_classes) != 1:
    raise RuntimeError("blind census does not contain one normal C2 class")

selected_v4 = normal_v4_classes[0]
selected_c2 = normal_c2_classes[0]

print()
print("== PREREGISTERED BLIND SELECTION ==")
print(f"BLIND_CLASS_COUNT: {len(classes)}")
print(f"NORMAL_V4_CLASS_COUNT: {len(normal_v4_classes)}")
print(f"SELECTED_V4_CLASS_INDEX: {selected_v4['class_index']}")
print(f"SELECTED_V4_GENERATOR_INDICES: {selected_v4['generator_indices']}")
print(f"NORMAL_C2_CLASS_COUNT: {len(normal_c2_classes)}")
print(f"SELECTED_C2_CLASS_INDEX: {selected_c2['class_index']}")
print(f"SELECTED_C2_GENERATOR_INDICES: {selected_c2['generator_indices']}")

action = json.loads(ACTION.read_text(encoding="utf-8"))
rows = action["mapping_rows"]
permutations = [
    tuple(int(value) for value in row["actual_permutation"])
    for row in rows
]
permutation_to_index = {
    permutation: index
    for index, permutation in enumerate(permutations)
}

identity = tuple(range(60))
v4_generators = [
    permutations[index]
    for index in selected_v4["generator_indices"]
]
c2_generator = permutations[selected_c2["generator_indices"][0]]

v4 = subgroup_closure(identity, v4_generators)
v4_indices = sorted(permutation_to_index[value] for value in v4)
v4_order_profile = Counter(permutation_order(value) for value in v4)

print()
print("== NATIVE NORMAL V4 ==")
print(f"V4_SUBGROUP_ORDER: {len(v4)}")
print(f"V4_MEMBER_INDICES: {v4_indices}")
print(
    "V4_ELEMENT_ORDER_PROFILE:",
    json.dumps(dict(sorted(v4_order_profile.items()))),
)
print(f"NORMAL_C2_CONTAINED_IN_V4: {str(c2_generator in v4).lower()}")

with G60_EDGES.open(newline="", encoding="utf-8") as handle:
    reader = csv.DictReader(handle)
    raw_edges = {
        norm_edge(int(row["local_u"]), int(row["local_v"]))
        for row in reader
    }

v4_orbits = vertex_orbits(v4, 60)
v4_vertex_map = {
    vertex: orbit_index
    for orbit_index, orbit in enumerate(v4_orbits)
    for vertex in orbit
}

blind_quotient_edges = {
    norm_edge(v4_vertex_map[u], v4_vertex_map[v])
    for u, v in raw_edges
}

blind_loop_count = sum(1 for u, v in blind_quotient_edges if u == v)
blind_degree = Counter()

for u, v in blind_quotient_edges:
    if u != v:
        blind_degree[u] += 1
        blind_degree[v] += 1

lift_count_by_quotient_edge = Counter(
    norm_edge(v4_vertex_map[u], v4_vertex_map[v])
    for u, v in raw_edges
)

lift_count_profile = Counter(lift_count_by_quotient_edge.values())

print()
print("== BLIND V4 ORBIT QUOTIENT ==")
print(f"V4_ORBIT_COUNT: {len(v4_orbits)}")
print(
    "V4_ORBIT_SIZE_PROFILE:",
    json.dumps(dict(sorted(Counter(map(len, v4_orbits)).items()))),
)
print(f"BLIND_QUOTIENT_VERTEX_COUNT: {len(set(v4_vertex_map.values()))}")
print(f"BLIND_QUOTIENT_EDGE_COUNT: {len(blind_quotient_edges)}")
print(f"BLIND_QUOTIENT_LOOP_COUNT: {blind_loop_count}")
print(
    "BLIND_QUOTIENT_DEGREE_PROFILE:",
    json.dumps(dict(sorted(Counter(blind_degree.values()).items()))),
)
print(
    "G60_LIFTS_PER_QUOTIENT_EDGE_PROFILE:",
    json.dumps(dict(sorted(lift_count_profile.items()))),
)

for index, orbit in enumerate(v4_orbits):
    print(
        "V4_FIBER:",
        json.dumps(
            {"quotient_vertex": index, "g60_vertices": list(orbit)},
            sort_keys=True,
            separators=(",", ":"),
        ),
    )

g15 = json.loads(G15_CERT.read_text(encoding="utf-8"))
historical_g15_edges = {
    norm_edge(
        int(row["g15_edge"][0]),
        int(row["g15_edge"][1]),
    )
    for row in g15["edge_rows"]
}

historical_g15_vertices = sorted(
    {value for edge in historical_g15_edges for value in edge}
)

isomorphisms = graph_isomorphisms(
    list(range(len(v4_orbits))),
    blind_quotient_edges,
    historical_g15_vertices,
    historical_g15_edges,
)

identity_mapping = {
    vertex: vertex
    for vertex in range(15)
}

exact_labeled_match = blind_quotient_edges == historical_g15_edges
isomorphic_match = len(isomorphisms) > 0

canonical_mapping = None
if isomorphisms:
    canonical_mapping = min(
        isomorphisms,
        key=lambda mapping: tuple(mapping[index] for index in range(15)),
    )

print()
print("== POST-SELECTION G15 COMPARISON ==")
print(f"HISTORICAL_G15_VERTEX_COUNT: {len(historical_g15_vertices)}")
print(f"HISTORICAL_G15_EDGE_COUNT: {len(historical_g15_edges)}")
print(f"QUOTIENT_GRAPH_ISOMORPHISM_COUNT: {len(isomorphisms)}")
print(f"EXACT_LABELED_EDGE_MATCH: {str(exact_labeled_match).lower()}")
print(f"ISOMORPHIC_EDGE_MATCH: {str(isomorphic_match).lower()}")
print(
    "CANONICAL_QUOTIENT_TO_G15_MAP:",
    json.dumps(canonical_mapping, sort_keys=True),
)

c2 = {identity, c2_generator}
c2_orbits = vertex_orbits(c2, 60)
c2_vertex_map = {
    vertex: orbit_index
    for orbit_index, orbit in enumerate(c2_orbits)
    for vertex in orbit
}

c2_quotient_edges = {
    norm_edge(c2_vertex_map[u], c2_vertex_map[v])
    for u, v in raw_edges
}

c2_orbit_to_v4_orbit = {}

for c2_index, orbit in enumerate(c2_orbits):
    target_orbits = {v4_vertex_map[vertex] for vertex in orbit}
    if len(target_orbits) != 1:
        raise RuntimeError("one C2 orbit crosses V4 orbit boundaries")
    c2_orbit_to_v4_orbit[c2_index] = next(iter(target_orbits))

v4_orbit_c2_counts = Counter(c2_orbit_to_v4_orbit.values())

induced_edges = {
    norm_edge(
        c2_orbit_to_v4_orbit[u],
        c2_orbit_to_v4_orbit[v],
    )
    for u, v in c2_quotient_edges
}

print()
print("== INDUCED G30 TO V4-QUOTIENT TOWER ==")
print(f"C2_ORBIT_COUNT: {len(c2_orbits)}")
print(f"C2_QUOTIENT_EDGE_COUNT: {len(c2_quotient_edges)}")
print(
    "C2_ORBITS_PER_V4_ORBIT_PROFILE:",
    json.dumps(dict(sorted(Counter(v4_orbit_c2_counts.values()).items()))),
)
print(f"INDUCED_QUOTIENT_EDGE_COUNT: {len(induced_edges)}")
print(
    "CHECK_INDUCED_TOWER_EDGES_EQUAL_DIRECT_V4_QUOTIENT:",
    str(induced_edges == blind_quotient_edges).lower(),
)

checks = {
    "source_hashes_locked": actual_hashes == EXPECTED_HASHES,
    "unique_normal_v4_preregistered": (
        len(normal_v4_classes) == 1
        and selected_v4["class_index"] == 20
        and selected_v4["generator_indices"] == [65, 124]
    ),
    "unique_normal_c2_preregistered": (
        len(normal_c2_classes) == 1
        and selected_c2["class_index"] == 22
        and selected_c2["generator_indices"] == [326]
    ),
    "v4_subgroup_exact": (
        len(v4) == 4
        and v4_order_profile == Counter({2: 3, 1: 1})
    ),
    "normal_c2_contained_in_v4": c2_generator in v4,
    "fifteen_four_point_orbits": (
        len(v4_orbits) == 15
        and all(len(orbit) == 4 for orbit in v4_orbits)
    ),
    "quotient_profile_15_30_4regular": (
        len(blind_quotient_edges) == 30
        and blind_loop_count == 0
        and Counter(blind_degree.values()) == Counter({4: 15})
    ),
    "four_lifts_per_g15_edge": lift_count_profile == Counter({4: 30}),
    "historical_g15_authority_passes": (
        g15["audit_pass"] is True
        and g15["g15_vertex_count"] == 15
        and g15["g15_edge_count"] == 30
    ),
    "blind_quotient_matches_historical_g15": isomorphic_match,
    "two_c2_orbits_per_v4_orbit": (
        Counter(v4_orbit_c2_counts.values()) == Counter({2: 15})
    ),
    "tower_factorization_exact": induced_edges == blind_quotient_edges,
}

print()
print("== THEOREM CHECKS ==")
for name, value in checks.items():
    print(f"CHECK_{name.upper()}: {str(value).lower()}")

failed_checks = [name for name, value in checks.items() if not value]
print(f"FAILED_CHECKS: {json.dumps(failed_checks)}")

status_after = {str(root): status(root) for root in roots}
status_preserved = status_before == status_after

print()
print("== STATUS PRESERVATION ==")
for root in roots:
    key = str(root)
    print(
        "STATUS_CHECK:",
        json.dumps(
            {
                "root": key,
                "before": status_before[key],
                "after": status_after[key],
                "preserved": status_before[key] == status_after[key],
            },
            sort_keys=True,
            separators=(",", ":"),
        ),
    )

print(
    "CHECK_ALL_REPOSITORY_STATUS_PRESERVED:",
    str(status_preserved).lower(),
)

if failed_checks or not status_preserved:
    raise RuntimeError("normal V4 quotient audit failed")

print()
print("THEOREM_PASS: true")

if exact_labeled_match:
    classification = (
        "blind_unique_normal_V4_action_recovers_the_exact_labeled_G15_"
        "quotient_and_factors_the_G60_G30_G15_tower"
    )
else:
    classification = (
        "blind_unique_normal_V4_action_recovers_G15_up_to_canonical_"
        "graph_isomorphism_and_factors_the_G60_G30_G15_tower"
    )

print("FINAL_CLASSIFICATION:", classification)
print(
    "BOUNDARY:",
    "The blind census selected class 20 before G15 authority was consulted. "
    "The exact quotient-edge comparison occurs after the G15 schema was "
    "inspected. V4 receipt and full-automorphism covariance remain declared "
    "premises. The V4 voltage comparison is deferred to the next packet."
)
print(
    "NEXT_GATE:",
    "Compare the derived native V4 edge translations with certificate033 "
    "up to quotient relabeling, V4 basis change, and vertex gauge."
)
print(
    "KEEPER:",
    "The binary cover remembers the first sheet. The normal V4 quotient "
    "reveals the fifteen-state floor beneath it."
)
print("MUTATION_PERFORMED: false")
