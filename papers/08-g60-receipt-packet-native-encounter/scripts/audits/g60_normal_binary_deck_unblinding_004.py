#!/usr/bin/env python3

from __future__ import annotations

import csv
import hashlib
import json
import subprocess
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

BLIND_RECEIPT = (
    TARGET
    / "artifacts/receipts"
    / "g60_native_semiregular_receipt_action_census_002_mac.txt"
)

ADJUDICATION_RECEIPT = (
    TARGET
    / "artifacts/receipts"
    / "g60_blind_receipt_action_adjudication_003.txt"
)

ACTION = (
    MATH42
    / "artifacts/json/native_g60_fiber_product_isomorphism_044.json"
)

QUOTIENT = (
    MATH42
    / "sources/project42_g60_to_g30_a_quotient_certificate_035.json"
)

G60_EDGES = PHYSICS / "paper/data/g60_local_edges.csv"

EXPECTED_HASHES = {
    "blind_receipt": (
        "9d0f1ef5975cd8cd2575192012c8bfeefe15c2856d6646e827ffc4ada851f383"
    ),
    "adjudication_receipt": (
        "f49281a06fd90336e4bae5ca9221ee9457e76399ccb2e890b9794887f242ec14"
    ),
    "action": (
        "b37313b135495752b11e525bb61979163fdf54aec4be4f5d027dcee64c9efc21"
    ),
    "quotient": (
        "acaf79c52d5d83915afc425ba5b2e0547f168b73d1db7f144898599d30654822"
    ),
    "g60_edges": (
        "c700a185fab6a5f434da09b7acb716b96c76170774bee946af8ea907e4fe7f9f"
    ),
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
        key_pairs = [
            ("u", "v"),
            ("source", "target"),
            ("from", "to"),
            ("g30_u", "g30_v"),
            ("local_u", "local_v"),
        ]
        for left, right in key_pairs:
            if left in record and right in record:
                return norm_edge(int(record[left]), int(record[right]))

        for key in ["edge", "vertices", "endpoints"]:
            value = record.get(key)
            if isinstance(value, (list, tuple)) and len(value) >= 2:
                return norm_edge(int(value[0]), int(value[1]))

    raise RuntimeError(f"unrecognized edge record: {record!r}")


roots = [TARGET, MATH42, PHYSICS]
status_before = {str(root): status(root) for root in roots}

print("OUT ==")
print("PACKET: g60_normal_binary_deck_unblinding_004")
print("MODE: read-only post-registered unblinding comparison")
print(f"TARGET: {TARGET}")
print("REPOSITORY_MUTATION: none")

paths = {
    "blind_receipt": BLIND_RECEIPT,
    "adjudication_receipt": ADJUDICATION_RECEIPT,
    "action": ACTION,
    "quotient": QUOTIENT,
    "g60_edges": G60_EDGES,
}

actual_hashes = {name: sha256(path) for name, path in paths.items()}

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

blind_text = BLIND_RECEIPT.read_text(encoding="utf-8")
adjudication_text = ADJUDICATION_RECEIPT.read_text(encoding="utf-8")

classes = []
for line in blind_text.splitlines():
    prefix = "RECEIPT_ACTION_CLASS: "
    if line.startswith(prefix):
        classes.append(json.loads(line[len(prefix):]))

normal_binary_classes = [
    row
    for row in classes
    if row["group_order"] == 2
    and row["group_label"] == "C2"
    and row["conjugate_subgroup_count"] == 1
]

if len(normal_binary_classes) != 1:
    raise RuntimeError("blind receipt does not contain one normal binary class")

selected = normal_binary_classes[0]
generator_indices = selected["generator_indices"]

if len(generator_indices) != 1:
    raise RuntimeError("normal binary class does not have one generator")

generator_index = generator_indices[0]

print()
print("== PRE-UNBLINDING SELECTION LOCK ==")
print(f"BLIND_CLASS_COUNT: {len(classes)}")
print(f"BLIND_NORMAL_BINARY_CLASS_COUNT: {len(normal_binary_classes)}")
print(f"BLIND_SELECTED_CLASS_INDEX: {selected['class_index']}")
print(f"BLIND_SELECTED_GENERATOR_INDEX: {generator_index}")
print(
    "CHECK_ADJUDICATION_PRECEDES_UNBLINDING:",
    str(
        "BLIND_OUTCOME: multiple" in adjudication_text
        and "NORMAL_BINARY_CLASS_INDEX: 22" in adjudication_text
        and "historical G60 deck action" in adjudication_text
    ).lower(),
)

action = json.loads(ACTION.read_text(encoding="utf-8"))
quotient = json.loads(QUOTIENT.read_text(encoding="utf-8"))

mapping_rows = action["mapping_rows"]
selected_row = mapping_rows[generator_index]
blind_permutation = [int(value) for value in selected_row["actual_permutation"]]

historical_involution = {
    int(key): int(value)
    for key, value in quotient["involution_a"].items()
}
historical_permutation = [
    historical_involution[index] for index in range(60)
]

disagreement_vertices = [
    index
    for index in range(60)
    if blind_permutation[index] != historical_permutation[index]
]

print()
print("== EXACT PERMUTATION UNBLINDING ==")
print(f"ACTION_MAPPING_ROW_COUNT: {len(mapping_rows)}")
print(f"SELECTED_ROW_ACTUAL_INDEX: {selected_row['actual_index']}")
print(f"SELECTED_ROW_ACTUAL_ORDER: {selected_row['actual_order']}")
print(f"PERMUTATION_DOMAIN_SIZE: {len(blind_permutation)}")
print(f"PERMUTATION_DISAGREEMENT_COUNT: {len(disagreement_vertices)}")
print(f"PERMUTATION_DISAGREEMENT_VERTICES: {disagreement_vertices}")
print(
    "CHECK_BLIND_GENERATOR_EQUALS_HISTORICAL_INVOLUTION_A:",
    str(blind_permutation == historical_permutation).lower(),
)

blind_orbits = []
seen = set()

for vertex in range(60):
    if vertex in seen:
        continue
    partner = blind_permutation[vertex]
    orbit = tuple(sorted((vertex, partner)))
    blind_orbits.append(orbit)
    seen.update(orbit)

blind_orbits = sorted(set(blind_orbits))

historical_fiber_rows = quotient["g30_fibers_from_g60"]
historical_orbits = sorted(
    tuple(sorted(int(value) for value in row["g60_vertices"]))
    for row in historical_fiber_rows
)

print()
print("== FIBER UNBLINDING ==")
print(f"BLIND_ORBIT_COUNT: {len(blind_orbits)}")
print(f"HISTORICAL_FIBER_COUNT: {len(historical_orbits)}")
print(
    "CHECK_ALL_BLIND_ORBITS_HAVE_SIZE2:",
    str(all(len(set(orbit)) == 2 for orbit in blind_orbits)).lower(),
)
print(
    "CHECK_BLIND_ORBITS_EQUAL_HISTORICAL_FIBERS:",
    str(blind_orbits == historical_orbits).lower(),
)

historical_vertex_map = {
    int(key): int(value)
    for key, value in quotient["g60_vertex_to_g30_vertex"].items()
}

fiber_map_failure_count = 0
for row in historical_fiber_rows:
    g30_vertex = int(row["g30_vertex"])
    for g60_vertex in row["g60_vertices"]:
        if historical_vertex_map[int(g60_vertex)] != g30_vertex:
            fiber_map_failure_count += 1

involution_map_failure_count = sum(
    1
    for vertex in range(60)
    if historical_vertex_map[vertex]
    != historical_vertex_map[blind_permutation[vertex]]
)

print()
print("== QUOTIENT MAP ==")
print(f"G60_VERTEX_MAP_COUNT: {len(historical_vertex_map)}")
print(f"FIBER_MAP_FAILURE_COUNT: {fiber_map_failure_count}")
print(f"INVOLUTION_MAP_FAILURE_COUNT: {involution_map_failure_count}")
print(
    "CHECK_BLIND_INVOLUTION_PRESERVES_EACH_G30_FIBER:",
    str(involution_map_failure_count == 0).lower(),
)

with G60_EDGES.open(newline="", encoding="utf-8") as handle:
    reader = csv.DictReader(handle)
    raw_edges = {
        norm_edge(int(row["local_u"]), int(row["local_v"]))
        for row in reader
    }

derived_quotient_edges = {
    norm_edge(
        historical_vertex_map[u],
        historical_vertex_map[v],
    )
    for u, v in raw_edges
}

certificate_quotient_edges = {
    edge_from_record(record)
    for record in quotient["quotient_edges"]
}

print()
print("== QUOTIENT EDGE RECONSTRUCTION ==")
print(f"RAW_G60_EDGE_COUNT: {len(raw_edges)}")
print(f"DERIVED_G30_EDGE_COUNT: {len(derived_quotient_edges)}")
print(f"CERTIFICATE_G30_EDGE_COUNT: {len(certificate_quotient_edges)}")
print(
    "CHECK_DERIVED_QUOTIENT_EDGES_EQUAL_CERTIFICATE:",
    str(derived_quotient_edges == certificate_quotient_edges).lower(),
)
print(
    "CHECK_QUOTIENT_HAS_30_VERTICES_60_EDGES:",
    str(
        len(set(historical_vertex_map.values())) == 30
        and len(derived_quotient_edges) == 60
    ).lower(),
)

checks = {
    "all_hashes_locked": actual_hashes == EXPECTED_HASHES,
    "blind_outcome_pre_registered": (
        "BLIND_OUTCOME: multiple" in adjudication_text
    ),
    "unique_normal_binary_pre_registered": (
        len(normal_binary_classes) == 1
        and selected["class_index"] == 22
        and generator_index == 326
    ),
    "selected_row_index_exact": (
        int(selected_row["actual_index"]) == generator_index
    ),
    "selected_row_order2": int(selected_row["actual_order"]) == 2,
    "permutation_domain60": len(blind_permutation) == 60,
    "permutation_exact_match": (
        blind_permutation == historical_permutation
    ),
    "orbit_count30": len(blind_orbits) == 30,
    "orbits_equal_historical_fibers": (
        blind_orbits == historical_orbits
    ),
    "vertex_map_exact_on_fibers": fiber_map_failure_count == 0,
    "blind_involution_preserves_vertex_map": (
        involution_map_failure_count == 0
    ),
    "quotient_edges_exact": (
        derived_quotient_edges == certificate_quotient_edges
    ),
    "quotient_profile_30_60": (
        len(set(historical_vertex_map.values())) == 30
        and len(derived_quotient_edges) == 60
    ),
    "certificate_names_involution_a": (
        quotient["quotient_involution"] == "a"
    ),
}

print()
print("== UNBLINDING CHECKS ==")
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
    raise RuntimeError("unblinding comparison failed")

print()
print(
    "FINAL_CLASSIFICATION:",
    "blind_unique_full_automorphism_normal_C2_action_is_exactly_"
    "the_historical_G60_to_G30_deck_involution",
)
print(
    "BOUNDARY:",
    "The blind census did not select a unique receipt action among all "
    "22 classes. It did independently recover a unique C2 action normal "
    "under the full native automorphism group. Post-registration "
    "unblinding proves that its 60-point permutation, 30 fibers, vertex "
    "projection, and 60 quotient edges equal the preserved historical "
    "G60-to-G30 quotient exactly. This does not select C2 unless binary "
    "receipt and full-automorphism covariance are declared premises."
)
print(
    "NEXT_GATE:",
    "Derive the native binary edge-voltage assignment from a section of "
    "the recovered quotient, reconstruct G60 as the corresponding regular "
    "C2 lift, and compute its circuit holonomy image."
)
print(
    "KEEPER:",
    "G60 offered many covers. Its unique fully symmetric binary cover "
    "was the old deck cover waiting under a new name."
)
print("MUTATION_PERFORMED: false")
