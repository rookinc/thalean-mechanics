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

PAPER7 = (
    HOME
    / "dev/cori/research/thalean_mechanics/papers"
    / "07-finite-covariant-receipt-algebra-on-graphs"
    / "artifacts/json"
    / "finite_covariant_receipt_algebra_on_graphs_theorem_001.v1.json"
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

UNBLINDING = (
    TARGET
    / "artifacts/receipts"
    / "g60_normal_binary_deck_unblinding_004.txt"
)

QUOTIENT = (
    MATH42
    / "sources/project42_g60_to_g30_a_quotient_certificate_035.json"
)

G60_EDGES = PHYSICS / "paper/data/g60_local_edges.csv"

EXPECTED_HASHES = {
    "paper7": "09fd36fa74dd5868549349a5edd82d16c80b9efafa72561f53e69001235d3bda",
    "unblinding": "339058c1fe40c50577eafcad3bda2ded753cbca7137a31c9aa7dbe5023f042c7",
    "quotient": "acaf79c52d5d83915afc425ba5b2e0547f168b73d1db7f144898599d30654822",
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


def norm_edge(u: int, v: int) -> tuple[int, int]:
    return (u, v) if u <= v else (v, u)


def edge_from_record(record) -> tuple[int, int]:
    if isinstance(record, (list, tuple)) and len(record) >= 2:
        return norm_edge(int(record[0]), int(record[1]))

    if isinstance(record, dict):
        for left, right in [
            ("u", "v"),
            ("source", "target"),
            ("from", "to"),
            ("g30_u", "g30_v"),
            ("local_u", "local_v"),
        ]:
            if left in record and right in record:
                return norm_edge(int(record[left]), int(record[right]))

        for key in ["edge", "vertices", "endpoints"]:
            value = record.get(key)
            if isinstance(value, (list, tuple)) and len(value) >= 2:
                return norm_edge(int(value[0]), int(value[1]))

    raise RuntimeError(f"unrecognized edge record: {record!r}")


def graph_connected(vertices, edges) -> bool:
    adjacency = {vertex: set() for vertex in vertices}
    for u, v in edges:
        adjacency[u].add(v)
        adjacency[v].add(u)

    root = min(vertices)
    seen = {root}
    queue = deque([root])

    while queue:
        u = queue.popleft()
        for v in adjacency[u]:
            if v not in seen:
                seen.add(v)
                queue.append(v)

    return seen == set(vertices)


roots = [TARGET, MATH42, PHYSICS]
status_before = {str(root): status(root) for root in roots}

paths = {
    "paper7": PAPER7,
    "unblinding": UNBLINDING,
    "quotient": QUOTIENT,
    "g60_edges": G60_EDGES,
}
actual_hashes = {name: sha256(path) for name, path in paths.items()}

print("OUT ==")
print("PACKET: g60_native_binary_voltage_holonomy_005")
print("MODE: read-only native C2 voltage and holonomy construction")
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

unblinding_text = UNBLINDING.read_text(encoding="utf-8")
quotient = json.loads(QUOTIENT.read_text(encoding="utf-8"))

with G60_EDGES.open(newline="", encoding="utf-8") as handle:
    reader = csv.DictReader(handle)
    raw_edges = {
        norm_edge(int(row["local_u"]), int(row["local_v"]))
        for row in reader
    }

g60_vertices = sorted({value for edge in raw_edges for value in edge})

base_edges = {
    edge_from_record(record)
    for record in quotient["quotient_edges"]
}
base_vertices = sorted({value for edge in base_edges for value in edge})

vertex_to_base = {
    int(key): int(value)
    for key, value in quotient["g60_vertex_to_g30_vertex"].items()
}

deck = {
    int(key): int(value)
    for key, value in quotient["involution_a"].items()
}

fiber_rows = sorted(
    quotient["g30_fibers_from_g60"],
    key=lambda row: int(row["g30_vertex"]),
)

lift_vertex = {}
sheet_of_vertex = {}
section = {}

for row in fiber_rows:
    base = int(row["g30_vertex"])
    fiber = sorted(int(value) for value in row["g60_vertices"])

    if len(fiber) != 2:
        raise RuntimeError(f"nonbinary fiber at base vertex {base}")

    section[base] = fiber[0]
    lift_vertex[(base, 0)] = fiber[0]
    lift_vertex[(base, 1)] = fiber[1]
    sheet_of_vertex[fiber[0]] = 0
    sheet_of_vertex[fiber[1]] = 1

print()
print("== NATIVE COVER PROFILE ==")
print(f"G60_VERTEX_COUNT: {len(g60_vertices)}")
print(f"G60_EDGE_COUNT: {len(raw_edges)}")
print(f"G30_VERTEX_COUNT: {len(base_vertices)}")
print(f"G30_EDGE_COUNT: {len(base_edges)}")
print(f"FIBER_COUNT: {len(fiber_rows)}")
print("SECTION_RULE: minimum labeled vertex in each fiber is sheet0")
print(
    "CHECK_G60_CONNECTED:",
    str(graph_connected(g60_vertices, raw_edges)).lower(),
)
print(
    "CHECK_G30_CONNECTED:",
    str(graph_connected(base_vertices, base_edges)).lower(),
)

deck_sheet_flip_failures = []
for vertex in g60_vertices:
    partner = deck[vertex]
    if vertex_to_base[vertex] != vertex_to_base[partner]:
        deck_sheet_flip_failures.append(vertex)
    elif sheet_of_vertex[vertex] == sheet_of_vertex[partner]:
        deck_sheet_flip_failures.append(vertex)

print(f"DECK_SHEET_FLIP_FAILURE_COUNT: {len(deck_sheet_flip_failures)}")

lifts_by_base_edge = {edge: [] for edge in base_edges}

for edge in raw_edges:
    u, v = edge
    base_edge = norm_edge(vertex_to_base[u], vertex_to_base[v])

    if base_edge not in lifts_by_base_edge:
        raise RuntimeError(f"raw edge projects outside quotient: {edge}")

    lifts_by_base_edge[base_edge].append(edge)

lift_count_profile = Counter(
    len(rows) for rows in lifts_by_base_edge.values()
)

voltage = {}
voltage_consistency_failures = []

for base_edge in sorted(base_edges):
    u, v = base_edge
    lifted_edges = lifts_by_base_edge[base_edge]

    edge_voltages = {
        sheet_of_vertex[x] ^ sheet_of_vertex[y]
        for x, y in lifted_edges
    }

    section_u = section[u]
    section_targets = [
        y if x == section_u else x
        for x, y in lifted_edges
        if x == section_u or y == section_u
    ]
    section_targets = [
        target
        for target in section_targets
        if vertex_to_base[target] == v
    ]

    if len(edge_voltages) != 1 or len(section_targets) != 1:
        voltage_consistency_failures.append(base_edge)
        continue

    edge_voltage = next(iter(edge_voltages))
    section_voltage = sheet_of_vertex[section_targets[0]]

    if edge_voltage != section_voltage:
        voltage_consistency_failures.append(base_edge)
        continue

    voltage[base_edge] = edge_voltage

print()
print("== NATIVE EDGE VOLTAGE ==")
print(
    "LIFT_COUNT_PER_BASE_EDGE_PROFILE:",
    json.dumps(dict(sorted(lift_count_profile.items()))),
)
print(f"VOLTAGE_EDGE_COUNT: {len(voltage)}")
print(
    "VOLTAGE_VALUE_COUNTS:",
    json.dumps(dict(sorted(Counter(voltage.values()).items()))),
)
print(
    "VOLTAGE_CONSISTENCY_FAILURE_COUNT:",
    len(voltage_consistency_failures),
)

voltage_rows = [
    [u, v, voltage[(u, v)]]
    for u, v in sorted(base_edges)
]

voltage_sha256 = hashlib.sha256(
    json.dumps(
        voltage_rows,
        separators=(",", ":"),
    ).encode("utf-8")
).hexdigest()

print(f"CANONICAL_VOLTAGE_ASSIGNMENT_SHA256: {voltage_sha256}")

for u, v, value in voltage_rows:
    print(
        "VOLTAGE_ROW:",
        json.dumps(
            {"u": u, "v": v, "voltage": value},
            sort_keys=True,
            separators=(",", ":"),
        ),
    )

reconstructed_edges = set()

for u, v in sorted(base_edges):
    a = voltage[(u, v)]
    for sheet in [0, 1]:
        x = lift_vertex[(u, sheet)]
        y = lift_vertex[(v, sheet ^ a)]
        reconstructed_edges.add(norm_edge(x, y))

missing_edges = sorted(raw_edges - reconstructed_edges)
extra_edges = sorted(reconstructed_edges - raw_edges)

print()
print("== EXACT G60 RECONSTRUCTION ==")
print(f"RECONSTRUCTED_VERTEX_COUNT: {len(lift_vertex)}")
print(f"RECONSTRUCTED_EDGE_COUNT: {len(reconstructed_edges)}")
print(f"MISSING_EDGE_COUNT: {len(missing_edges)}")
print(f"EXTRA_EDGE_COUNT: {len(extra_edges)}")
print(
    "CHECK_RECONSTRUCTED_G60_EQUALS_RAW_G60:",
    str(reconstructed_edges == raw_edges).lower(),
)

base_adjacency = {vertex: set() for vertex in base_vertices}
for u, v in base_edges:
    base_adjacency[u].add(v)
    base_adjacency[v].add(u)

root = min(base_vertices)
parent = {root: None}
depth = {root: 0}
tree_edges = set()
queue = deque([root])

while queue:
    u = queue.popleft()
    for v in sorted(base_adjacency[u]):
        if v in parent:
            continue
        parent[v] = u
        depth[v] = depth[u] + 1
        tree_edges.add(norm_edge(u, v))
        queue.append(v)

chord_edges = sorted(base_edges - tree_edges)
cycle_rank = len(base_edges) - len(base_vertices) + 1

potential = {root: 0}
for vertex in sorted(
    (v for v in base_vertices if v != root),
    key=lambda v: depth[v],
):
    p = parent[vertex]
    potential[vertex] = potential[p] ^ voltage[norm_edge(p, vertex)]

normalized_voltage = {
    edge: voltage[edge] ^ potential[edge[0]] ^ potential[edge[1]]
    for edge in base_edges
}

tree_nonzero_count = sum(
    normalized_voltage[edge] for edge in tree_edges
)

fundamental_holonomy = {
    edge: normalized_voltage[edge]
    for edge in chord_edges
}

holonomy_value_counts = Counter(fundamental_holonomy.values())
holonomy_image = sorted({0, *fundamental_holonomy.values()})

normalized_rows = [
    [u, v, normalized_voltage[(u, v)]]
    for u, v in sorted(base_edges)
]

normalized_sha256 = hashlib.sha256(
    json.dumps(
        normalized_rows,
        separators=(",", ":"),
    ).encode("utf-8")
).hexdigest()

print()
print("== SPANNING TREE NORMAL FORM ==")
print(f"ROOT_VERTEX: {root}")
print(f"TREE_EDGE_COUNT: {len(tree_edges)}")
print(f"CHORD_EDGE_COUNT: {len(chord_edges)}")
print(f"BASE_CYCLE_RANK: {cycle_rank}")
print(f"TREE_NONZERO_VOLTAGE_COUNT: {tree_nonzero_count}")
print(
    "FUNDAMENTAL_HOLONOMY_VALUE_COUNTS:",
    json.dumps(dict(sorted(holonomy_value_counts.items()))),
)
print(f"HOLONOMY_IMAGE: {holonomy_image}")
print(f"NORMALIZED_VOLTAGE_ASSIGNMENT_SHA256: {normalized_sha256}")

for edge in chord_edges:
    print(
        "HOLONOMY_ROW:",
        json.dumps(
            {
                "chord": list(edge),
                "holonomy": fundamental_holonomy[edge],
            },
            sort_keys=True,
            separators=(",", ":"),
        ),
    )

gauge_normal_form_failures = 0

for gauge_vertex in base_vertices:
    transformed = {
        edge: (
            voltage[edge]
            ^ int(edge[0] == gauge_vertex)
            ^ int(edge[1] == gauge_vertex)
        )
        for edge in base_edges
    }

    transformed_potential = {root: 0}
    for vertex in sorted(
        (v for v in base_vertices if v != root),
        key=lambda v: depth[v],
    ):
        p = parent[vertex]
        transformed_potential[vertex] = (
            transformed_potential[p]
            ^ transformed[norm_edge(p, vertex)]
        )

    transformed_normal = {
        edge: (
            transformed[edge]
            ^ transformed_potential[edge[0]]
            ^ transformed_potential[edge[1]]
        )
        for edge in base_edges
    }

    if transformed_normal != normalized_voltage:
        gauge_normal_form_failures += 1

print()
print("== GAUGE COVARIANCE ==")
print(f"SINGLE_VERTEX_GAUGE_TEST_COUNT: {len(base_vertices)}")
print(
    "GAUGE_NORMAL_FORM_FAILURE_COUNT:",
    gauge_normal_form_failures,
)
print(
    "CHECK_TREE_NORMAL_FORM_GAUGE_INVARIANT:",
    str(gauge_normal_form_failures == 0).lower(),
)

checks = {
    "source_hashes_locked": actual_hashes == EXPECTED_HASHES,
    "unblinding_theorem_locked": (
        "FINAL_CLASSIFICATION: "
        "blind_unique_full_automorphism_normal_C2_action_is_exactly_"
        "the_historical_G60_to_G30_deck_involution"
        in unblinding_text
    ),
    "native_profile_60_120_to_30_60": (
        len(g60_vertices) == 60
        and len(raw_edges) == 120
        and len(base_vertices) == 30
        and len(base_edges) == 60
    ),
    "both_graphs_connected": (
        graph_connected(g60_vertices, raw_edges)
        and graph_connected(base_vertices, base_edges)
    ),
    "thirty_binary_fibers": (
        len(fiber_rows) == 30
        and len(lift_vertex) == 60
    ),
    "deck_flips_every_sheet": len(deck_sheet_flip_failures) == 0,
    "two_lifts_per_base_edge": lift_count_profile == Counter({2: 60}),
    "voltage_defined_on_all_edges": len(voltage) == 60,
    "voltage_consistent": not voltage_consistency_failures,
    "reconstruction_exact": reconstructed_edges == raw_edges,
    "tree_has_29_edges": len(tree_edges) == 29,
    "cycle_rank_is_31": cycle_rank == 31,
    "tree_normalized_to_zero": tree_nonzero_count == 0,
    "fundamental_holonomy_count_31": len(fundamental_holonomy) == 31,
    "holonomy_image_is_C2": holonomy_image == [0, 1],
    "gauge_normal_form_exact": gauge_normal_form_failures == 0,
}

print()
print("== THEOREM CHECKS ==")
for name, value in checks.items():
    print(f"CHECK_{name.upper()}: {str(value).lower()}")

failed_checks = [name for name, value in checks.items() if not value]
print(f"FAILED_CHECKS: {json.dumps(failed_checks)}")

status_after = {str(root_path): status(root_path) for root_path in roots}
status_preserved = status_before == status_after

print()
print("== STATUS PRESERVATION ==")
for root_path in roots:
    key = str(root_path)
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
    raise RuntimeError("native voltage construction failed")

print()
print(
    "THEOREM_PASS: true"
)
print(
    "FINAL_CLASSIFICATION:",
    "recovered_normal_binary_action_constructs_the_exact_native_"
    "G60_over_G30_C2_voltage_lift_with_surjective_holonomy",
)
print(
    "THEOREM:",
    "Using the minimum-labeled section of the independently recovered "
    "normal binary quotient, every G30 edge receives a native C2 voltage. "
    "The resulting regular lift reconstructs all 60 G60 vertices and all "
    "120 G60 edges exactly. Its fundamental circuit receipts generate C2, "
    "so the lift is connected."
)
print(
    "BOUNDARY:",
    "The edge-voltage values depend on the chosen section, while their "
    "gauge class and holonomy image do not. Binary receipt and full-"
    "automorphism covariance remain declared premises for selecting this "
    "cover from the complete 22-class native spectrum. No orientation or "
    "physical interpretation is claimed."
)
print(
    "NEXT_GATE:",
    "Package the blind census, normal-binary recovery, exact quotient "
    "unblinding, native voltage reconstruction, and surjective holonomy "
    "as the G60 receipt-packet encounter theorem."
)
print(
    "KEEPER:",
    "The quotient names the circuit. The voltage records which sheet "
    "the circuit brings home."
)
print("MUTATION_PERFORMED: false")
