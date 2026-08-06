#!/usr/bin/env python3

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(
    "/data/data/com.termux/files/home/dev/cori/research/"
    "thalean_mechanics/papers/"
    "08-g60-receipt-packet-native-encounter"
)
GIT_ROOT = ROOT.parents[1]

PROJECT42 = Path(
    "/data/data/com.termux/files/home/dev/cori/research/"
    "mathematics/42-graph-automorphism-groups"
)
ELECTRON = Path(
    "/data/data/com.termux/files/home/dev/cori/research/"
    "physics/quantum_mechanics/01-the-electron-spins-twice"
)
PAPER7_ROOT = (
    ROOT.parent
    / "07-finite-covariant-receipt-algebra-on-graphs"
)

PAPER7 = (
    PAPER7_ROOT
    / "artifacts/json/"
    "finite_covariant_receipt_algebra_on_graphs_theorem_001.v1.json"
)
BLIND = (
    ROOT
    / "artifacts/receipts/"
    "g60_native_semiregular_receipt_action_census_002_mac.txt"
)
ADJUDICATION = (
    ROOT
    / "artifacts/receipts/"
    "g60_blind_receipt_action_adjudication_003.txt"
)
UNBLINDING = (
    ROOT
    / "artifacts/receipts/"
    "g60_normal_binary_deck_unblinding_004.txt"
)
C2_VOLTAGE = (
    ROOT
    / "artifacts/receipts/"
    "g60_native_binary_voltage_holonomy_005.txt"
)
THEOREM006 = (
    ROOT
    / "artifacts/json/"
    "g60_receipt_packet_native_encounter_theorem_006.v1.json"
)
PACKET007 = (
    ROOT
    / "artifacts/receipts/"
    "g60_normal_v4_g15_quotient_unblinding_007.txt"
)
PACKET008 = (
    ROOT
    / "artifacts/receipts/"
    "g60_native_v4_voltage_certificate_comparison_008.txt"
)

ACTION = (
    PROJECT42
    / "artifacts/json/"
    "native_g60_fiber_product_isomorphism_044.json"
)
G30_CERT = (
    PROJECT42
    / "sources/"
    "project42_g60_to_g30_a_quotient_certificate_035.json"
)
G15_CERT = (
    PROJECT42
    / "sources/project41-paper42/"
    "project42_native_voltage_derivation_certificate_033.json"
)
G60_EDGES = (
    ELECTRON
    / "paper/data/g60_local_edges.csv"
)

ARTIFACT = (
    ROOT
    / "artifacts/json/"
    "g60_native_receipt_tower_theorem_009.v1.json"
)
NOTE = (
    ROOT
    / "notes/"
    "g60_native_receipt_tower_theorem_009.md"
)

EXPECTED_HASHES = {
    PAPER7:
        "09fd36fa74dd5868549349a5edd82d16c80b9efafa72561f53e69001235d3bda",
    BLIND:
        "9d0f1ef5975cd8cd2575192012c8bfeefe15c2856d6646e827ffc4ada851f383",
    ADJUDICATION:
        "f49281a06fd90336e4bae5ca9221ee9457e76399ccb2e890b9794887f242ec14",
    UNBLINDING:
        "339058c1fe40c50577eafcad3bda2ded753cbca7137a31c9aa7dbe5023f042c7",
    C2_VOLTAGE:
        "fd57c49e368b5e1927e37bae7d8104a16c5fca5e4e64c554e9d70cde2b14ce2b",
    PACKET007:
        "0a5f257592d3ce6d9553c0f6b9ef529282fbe5ede3bdac557e3658ff8d002f17",
    ACTION:
        "b37313b135495752b11e525bb61979163fdf54aec4be4f5d027dcee64c9efc21",
    G30_CERT:
        "acaf79c52d5d83915afc425ba5b2e0547f168b73d1db7f144898599d30654822",
    G15_CERT:
        "9d5046dec7ea5d32f88782aa158a79082d4facf6f0b4fd4a7d3a3e4c552a0f70",
    G60_EDGES:
        "c700a185fab6a5f434da09b7acb716b96c76170774bee946af8ea907e4fe7f9f",
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_status(root):
    result = subprocess.run(
        ["git", "-C", str(root), "status", "--short"],
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout.splitlines()


def committed_exact(path, commit):
    relative = path.relative_to(GIT_ROOT).as_posix()
    result = subprocess.run(
        [
            "git",
            "-C",
            str(GIT_ROOT),
            "show",
            commit + ":" + relative,
        ],
        check=True,
        capture_output=True,
    )
    return result.stdout == path.read_bytes()


def sidecar_hash(path):
    sidecar = Path(str(path) + ".sha256")
    return sidecar.read_text().split()[0]


def contains(path, phrase):
    return phrase in path.read_text()


parser = argparse.ArgumentParser()
parser.add_argument("--write", action="store_true")
args = parser.parse_args()

status_roots = (ROOT, PROJECT42, ELECTRON, PAPER7_ROOT)
status_before = {
    str(root): git_status(root)
    for root in status_roots
}

source_hashes = {
    path.name: sha256(path)
    for path in EXPECTED_HASHES
}
packet008_hash = sha256(PACKET008)
theorem006_hash = sha256(THEOREM006)

checks = {}

for path, expected in EXPECTED_HASHES.items():
    checks["hash_" + path.name] = sha256(path) == expected

checks["packet008_sidecar_hash"] = (
    packet008_hash == sidecar_hash(PACKET008)
)
checks["packet007_committed_exact"] = (
    committed_exact(PACKET007, "bbae505")
)
checks["packet008_committed_exact"] = (
    committed_exact(PACKET008, "2675e5d")
)

checks["blind_outcome_multiple"] = contains(
    ADJUDICATION,
    "BLIND_OUTCOME: multiple",
)
checks["blind_class_count_22"] = contains(
    ADJUDICATION,
    "PARSED_CLASS_COUNT: 22",
)
checks["normal_c2_unique"] = contains(
    ADJUDICATION,
    "CHECK_UNIQUE_NORMAL_BINARY_CLASS: true",
)
checks["c2_exact_historical_deck"] = contains(
    UNBLINDING,
    "CHECK_BLIND_GENERATOR_EQUALS_HISTORICAL_INVOLUTION_A: true",
)
checks["c2_exact_g30_quotient"] = contains(
    UNBLINDING,
    "CHECK_DERIVED_QUOTIENT_EDGES_EQUAL_CERTIFICATE: true",
)
checks["c2_exact_reconstruction"] = contains(
    C2_VOLTAGE,
    "CHECK_RECONSTRUCTION_EXACT: true",
)
checks["c2_surjective_holonomy"] = contains(
    C2_VOLTAGE,
    "CHECK_HOLONOMY_IMAGE_IS_C2: true",
)
checks["theorem006_pass"] = contains(
    THEOREM006,
    "G60_is_the_exact_connected_regular_C2_receipt_lift_of_G30_"
    "selected_uniquely_by_binary_full_automorphism_covariance",
)

checks["normal_v4_unique"] = contains(
    PACKET007,
    "CHECK_UNIQUE_NORMAL_V4_PREREGISTERED: true",
)
checks["normal_c2_in_v4"] = contains(
    PACKET007,
    "CHECK_NORMAL_C2_CONTAINED_IN_V4: true",
)
checks["v4_exact_g15_quotient"] = contains(
    PACKET007,
    "CHECK_BLIND_QUOTIENT_MATCHES_HISTORICAL_G15: true",
)
checks["tower_factorization_exact"] = contains(
    PACKET007,
    "CHECK_TOWER_FACTORIZATION_EXACT: true",
)
checks["v4_exact_reconstruction"] = contains(
    PACKET008,
    "CHECK_EXACT_G60_RECONSTRUCTION: true",
)
checks["v4_surjective_holonomy"] = contains(
    PACKET008,
    "CHECK_V4_HOLONOMY_SURJECTIVE: true",
)
checks["v4_certificate_match"] = contains(
    PACKET008,
    "CHECK_CERTIFICATE033_GAUGE_EQUIVALENT: true",
)
checks["v4_identity_chart_match"] = (
    contains(PACKET008, "IDENTITY_MAPPING_MATCH_COUNT: 1")
    and contains(
        PACKET008,
        "CANONICAL_GL2_MATRIX: [[1,0],[0,1]]",
    )
    and contains(
        PACKET008,
        "CANONICAL_VERTEX_GAUGE: "
        "[[0,0],[0,0],[0,0],[0,0],[0,0],"
        "[0,0],[0,0],[0,0],[0,0],[0,0],"
        "[0,0],[0,0],[0,0],[0,0],[0,0]]",
    )
)

artifact_payload = {
    "artifact_id":
        "g60_native_receipt_tower_theorem_009",
    "artifact_type":
        "conditional_native_receipt_tower_theorem",
    "artifact_version": 1,
    "audit_pass": True,
    "abstract_algebra_authority": {
        "paper7_sha256": sha256(PAPER7),
        "statement":
            "Gauge classes of finite regular graph lifts are "
            "classified by holonomy representations.",
    },
    "blind_native_spectrum": {
        "semiregular_subgroup_count": 198,
        "conjugacy_class_count": 22,
        "cover_admissible_class_count": 22,
        "raw_graph_selects_unique_receipt_action": False,
    },
    "declared_selection_premises": {
        "binary_receipt": True,
        "v4_receipt": True,
        "full_automorphism_covariance": True,
        "derived_from_raw_graph_alone": False,
    },
    "normal_subgroup_chain": {
        "C2": {
            "blind_class_index": 22,
            "generator_index": 326,
            "order": 2,
            "normal_under_full_automorphism_group": True,
        },
        "V4": {
            "blind_class_index": 20,
            "generator_indices": [65, 124],
            "member_indices": [0, 65, 124, 326],
            "order": 4,
            "normal_under_full_automorphism_group": True,
        },
        "C2_is_subgroup_of_V4": True,
        "notation":
            "C2 normal in V4 normal in Aut(G60)",
    },
    "quotient_tower": {
        "top": {
            "name": "G60",
            "vertex_count": 60,
            "edge_count": 120,
        },
        "binary_quotient": {
            "name": "G30",
            "vertex_count": 30,
            "edge_count": 60,
            "fiber_size": 2,
            "deck_group": "C2",
            "exact_historical_match": True,
        },
        "v4_quotient": {
            "name": "G15",
            "vertex_count": 15,
            "edge_count": 30,
            "fiber_size": 4,
            "deck_group": "V4",
            "exact_labeled_historical_match": True,
        },
        "intermediate_factor": {
            "map": "G30_to_G15",
            "fiber_size": 2,
            "quotient_group": "V4_over_C2",
            "edge_factorization_exact": True,
        },
    },
    "voltage_and_holonomy": {
        "G60_over_G30": {
            "receipt_group": "C2",
            "exact_reconstruction": True,
            "holonomy_image": "C2",
            "connected": True,
        },
        "G60_over_G15": {
            "receipt_group": "V4",
            "exact_reconstruction": True,
            "holonomy_image": "V4",
            "connected": True,
            "certificate033_match":
                "exact_in_identity_label_basis_and_zero_gauge",
        },
    },
    "theorem_statement": (
        "For the native G60 graph, after binary receipt, V4 receipt, "
        "and covariance under the full automorphism group are declared, "
        "the blind action spectrum contains a unique normal C2 and a "
        "unique normal V4. They satisfy C2 <= V4. Their orbit quotients "
        "are exactly the preserved labeled graphs G30 and G15, and the "
        "induced quotient maps factor as G60 -> G30 -> G15. The native "
        "C2 and V4 voltages reconstruct G60 exactly and have surjective "
        "holonomy. The derived V4 voltage equals certificate033 already "
        "in the registered labeling, basis, and zero gauge."
    ),
    "verdict":
        "native_G60_G30_G15_receipt_tower_is_exact_connected_"
        "and_reproducible_under_declared_receipt_covariance_premises",
    "boundary": {
        "blind_outcome_remains_multiple": True,
        "receipt_group_selected_by_raw_graph_alone": False,
        "binary_and_v4_receipt_are_declared_premises": True,
        "full_automorphism_covariance_is_declared_premise": True,
        "orientation_claim": False,
        "physics_claim": False,
        "electron_claim": False,
        "gravity_claim": False,
        "radiation_claim": False,
    },
    "keeper": (
        "The packet met the graph twice. The binary receipt found G30. "
        "The V4 receipt found G15. Together they rebuilt G60 as one "
        "exact connected receipt tower."
    ),
    "sources": {
        "paper7": {
            "path": str(PAPER7),
            "sha256": sha256(PAPER7),
        },
        "blind_census": {
            "path": str(BLIND),
            "sha256": sha256(BLIND),
        },
        "adjudication003": {
            "path": str(ADJUDICATION),
            "sha256": sha256(ADJUDICATION),
        },
        "unblinding004": {
            "path": str(UNBLINDING),
            "sha256": sha256(UNBLINDING),
        },
        "c2_voltage005": {
            "path": str(C2_VOLTAGE),
            "sha256": sha256(C2_VOLTAGE),
        },
        "theorem006": {
            "path": str(THEOREM006),
            "sha256": theorem006_hash,
        },
        "v4_quotient007": {
            "path": str(PACKET007),
            "sha256": sha256(PACKET007),
            "locked_commit": "bbae505",
        },
        "v4_voltage008": {
            "path": str(PACKET008),
            "sha256": packet008_hash,
            "locked_commit": "2675e5d",
        },
        "automorphism_action044": {
            "path": str(ACTION),
            "sha256": sha256(ACTION),
        },
        "g30_certificate035": {
            "path": str(G30_CERT),
            "sha256": sha256(G30_CERT),
        },
        "g15_certificate033": {
            "path": str(G15_CERT),
            "sha256": sha256(G15_CERT),
        },
        "g60_edges": {
            "path": str(G60_EDGES),
            "sha256": sha256(G60_EDGES),
        },
    },
    "checks": {
        key: bool(value)
        for key, value in sorted(checks.items())
    },
}

artifact_text = (
    json.dumps(
        artifact_payload,
        indent=2,
        sort_keys=True,
    )
    + "\n"
)

note_text = """# Native G60 Receipt-Tower Theorem 009

## Result

Under the declared premises of binary receipt, V4 receipt, and
covariance under the full native automorphism group, the native graph
contains the unique normal chain

    C2 <= V4 <= Aut(G60).

The associated orbit quotients are exactly

    G60 -> G30 -> G15.

The C2 quotient has thirty two-state fibers. The V4 quotient has
fifteen four-state fibers, and every V4 fiber contains exactly two C2
fibers. The induced G30-to-G15 quotient agrees exactly with the direct
G60-to-G15 quotient.

## Voltage theorem

The recovered C2 voltage reconstructs all sixty G60 vertices and all
120 G60 edges from G30. Its circuit holonomy generates C2.

The recovered V4 voltage reconstructs the same sixty vertices and 120
edges from G15. Its circuit holonomy generates V4. In the registered
G15 labeling and the generator basis 65=(1,0), 124=(0,1), the voltage
equals certificate033 with the identity graph map, identity GL(2,2)
basis, and zero vertex gauge.

## Selection boundary

The blind native census contains 22 cover-admissible conjugacy classes.
The raw graph therefore does not select a unique receipt action.

Uniqueness is conditional:

- binary receipt plus full-automorphism covariance selects class 22;
- V4 receipt plus full-automorphism covariance selects class 20.

No receipt group is retrospectively derived from the raw graph alone.

## Theorem

For native G60, subject to the declared receipt-rank and covariance
premises, the normal C2 and V4 actions form an exact connected regular
receipt tower. Their quotients are the preserved labeled G30 and G15,
their voltages reconstruct G60 exactly, and their holonomy images are
surjective.

## Boundary

No orientation, electron, gravity, radiation, or physical claim is
made.

## Keeper

The packet met the graph twice. The binary receipt found G30. The V4
receipt found G15. Together they rebuilt G60 as one exact connected
receipt tower.
"""

if args.write:
    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    NOTE.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT.write_text(artifact_text)
    NOTE.write_text(note_text)

    print("OUT ==")
    print("PACKET: g60_native_receipt_tower_theorem_009")
    print("ACTION: write deterministic theorem package")
    print("FILE: wrote", ARTIFACT.relative_to(ROOT))
    print("FILE: wrote", NOTE.relative_to(ROOT))
    print("MUTATION_PERFORMED: true")
    raise SystemExit(0)

artifact_exists = ARTIFACT.exists()
note_exists = NOTE.exists()
artifact_exact = (
    artifact_exists
    and ARTIFACT.read_text() == artifact_text
)
note_exact = (
    note_exists
    and NOTE.read_text() == note_text
)

checks["artifact_exists"] = artifact_exists
checks["note_exists"] = note_exists
checks["artifact_exact"] = artifact_exact
checks["note_exact"] = note_exact
checks["all_locked_results_pass"] = all(
    checks[key]
    for key in (
        "blind_outcome_multiple",
        "blind_class_count_22",
        "normal_c2_unique",
        "c2_exact_historical_deck",
        "c2_exact_g30_quotient",
        "c2_exact_reconstruction",
        "c2_surjective_holonomy",
        "theorem006_pass",
        "normal_v4_unique",
        "normal_c2_in_v4",
        "v4_exact_g15_quotient",
        "tower_factorization_exact",
        "v4_exact_reconstruction",
        "v4_surjective_holonomy",
        "v4_certificate_match",
        "v4_identity_chart_match",
    )
)
checks["all_source_hashes_locked"] = all(
    checks["hash_" + path.name]
    for path in EXPECTED_HASHES
)
checks["no_orientation_claim"] = (
    artifact_payload["boundary"]["orientation_claim"] is False
)
checks["no_physics_claim"] = (
    artifact_payload["boundary"]["physics_claim"] is False
)

failed_checks = [
    key
    for key, value in sorted(checks.items())
    if not value
]

status_after = {
    str(root): git_status(root)
    for root in status_roots
}
status_preserved = status_before == status_after

print("OUT ==")
print("PACKET: g60_native_receipt_tower_theorem_009")
print("MODE: read-only deterministic theorem package audit")
print("TARGET:", ROOT)
print("REPOSITORY_MUTATION: none")
print()
print("== SOURCE LOCK ==")
print("PACKET007_SHA256:", sha256(PACKET007))
print("PACKET008_SHA256:", packet008_hash)
print(
    "CHECK_PACKET007_COMMITTED_EXACT:",
    str(checks["packet007_committed_exact"]).lower(),
)
print(
    "CHECK_PACKET008_COMMITTED_EXACT:",
    str(checks["packet008_committed_exact"]).lower(),
)
print()
print("== TOWER ==")
print("BLIND_CLASS_COUNT: 22")
print("NORMAL_C2_CLASS_INDEX: 22")
print("NORMAL_V4_CLASS_INDEX: 20")
print("NORMAL_CHAIN: C2 <= V4 <= Aut(G60)")
print("QUOTIENT_TOWER: G60 -> G30 -> G15")
print("C2_HOLONOMY_IMAGE: C2")
print("V4_HOLONOMY_IMAGE: V4")
print("C2_RECONSTRUCTS_G60: true")
print("V4_RECONSTRUCTS_G60: true")
print("V4_CERTIFICATE033_IDENTITY_CHART_MATCH: true")
print()
print("== PACKAGE ==")
print("ARTIFACT_EXISTS:", str(artifact_exists).lower())
print("NOTE_EXISTS:", str(note_exists).lower())
print("ARTIFACT_EXACT:", str(artifact_exact).lower())
print("NOTE_EXACT:", str(note_exact).lower())
print()
print("== THEOREM CHECKS ==")
for key in sorted(checks):
    print(key.upper() + ":", str(checks[key]).lower())
print("FAILED_CHECKS:", failed_checks)
print()
print("== STATUS PRESERVATION ==")
for root in status_roots:
    key = str(root)
    print(
        "STATUS_CHECK:",
        json.dumps(
            {
                "root": key,
                "before": status_before[key],
                "after": status_after[key],
                "preserved":
                    status_before[key] == status_after[key],
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
    raise RuntimeError("receipt-tower theorem audit failed")

print()
print("THEOREM_PASS: true")
print(
    "VERDICT:",
    artifact_payload["verdict"],
)
print(
    "FINAL_CLASSIFICATION:",
    "native_G60_G30_G15_receipt_tower_theorem_locked_"
    "exact_and_reproducible",
)
print(
    "BOUNDARY:",
    "The blind spectrum remains 22 classes. Uniqueness is conditional "
    "on declared binary or V4 receipt rank together with full-"
    "automorphism covariance. No orientation or physics claim is made."
)
print(
    "KEEPER:",
    artifact_payload["keeper"],
)
print("MUTATION_PERFORMED: false")
