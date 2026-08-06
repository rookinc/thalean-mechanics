#!/usr/bin/env python3

from __future__ import annotations

import argparse
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

BLIND = (
    TARGET
    / "artifacts/receipts"
    / "g60_native_semiregular_receipt_action_census_002_mac.txt"
)

ADJUDICATION = (
    TARGET
    / "artifacts/receipts"
    / "g60_blind_receipt_action_adjudication_003.txt"
)

UNBLINDING = (
    TARGET
    / "artifacts/receipts"
    / "g60_normal_binary_deck_unblinding_004.txt"
)

VOLTAGE = (
    TARGET
    / "artifacts/receipts"
    / "g60_native_binary_voltage_holonomy_005.txt"
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

ARTIFACT = (
    TARGET
    / "artifacts/json"
    / "g60_receipt_packet_native_encounter_theorem_006.v1.json"
)

NOTE = (
    TARGET
    / "notes"
    / "g60_receipt_packet_native_encounter_theorem_006.md"
)

EXPECTED_HASHES = {
    "paper7": "09fd36fa74dd5868549349a5edd82d16c80b9efafa72561f53e69001235d3bda",
    "blind_receipt": "9d0f1ef5975cd8cd2575192012c8bfeefe15c2856d6646e827ffc4ada851f383",
    "adjudication_receipt": "f49281a06fd90336e4bae5ca9221ee9457e76399ccb2e890b9794887f242ec14",
    "unblinding_receipt": "339058c1fe40c50577eafcad3bda2ded753cbca7137a31c9aa7dbe5023f042c7",
    "voltage_receipt": "fd57c49e368b5e1927e37bae7d8104a16c5fca5e4e64c554e9d70cde2b14ce2b",
    "automorphism_action": "b37313b135495752b11e525bb61979163fdf54aec4be4f5d027dcee64c9efc21",
    "quotient_certificate": "acaf79c52d5d83915afc425ba5b2e0547f168b73d1db7f144898599d30654822",
    "g60_edges": "c700a185fab6a5f434da09b7acb716b96c76170774bee946af8ea907e4fe7f9f",
}

SOURCE_PATHS = {
    "paper7": PAPER7,
    "blind_receipt": BLIND,
    "adjudication_receipt": ADJUDICATION,
    "unblinding_receipt": UNBLINDING,
    "voltage_receipt": VOLTAGE,
    "automorphism_action": ACTION,
    "quotient_certificate": QUOTIENT,
    "g60_edges": G60_EDGES,
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_status(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(root), "status", "--short"],
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line]


def expected_artifact() -> dict:
    return {
        "artifact_id": "g60_receipt_packet_native_encounter_theorem_006",
        "schema": "thalean_mechanics.g60_receipt_packet_native_encounter_theorem.v1",
        "status": "conditional_native_graph_encounter_theorem",
        "source_locks": EXPECTED_HASHES,
        "declared_selection_premises": {
            "receipt_group_is_binary": True,
            "receipt_action_is_semiregular": True,
            "receipt_action_is_invariant_under_full_native_automorphism_group": True,
            "orientation_selected": False,
            "physical_interpretation_claimed": False,
        },
        "blind_census": {
            "full_automorphism_group_order": 480,
            "fixed_point_free_nonidentity_element_count": 354,
            "semiregular_subgroup_count": 198,
            "semiregular_subgroup_conjugacy_class_count": 22,
            "cover_admissible_class_count": 22,
            "edge_inverting_class_count": 0,
            "blind_outcome": "multiple",
            "binary_conjugacy_class_count": 3,
            "binary_conjugacy_orbit_sizes": [1, 2, 15],
        },
        "normal_binary_selection": {
            "normal_binary_class_count": 1,
            "selected_class_index": 22,
            "selected_generator_index": 326,
            "selected_group": "C2",
            "selection_is_unique_given_declared_premises": True,
            "selection_is_unique_without_declared_premises": False,
        },
        "post_registered_unblinding": {
            "historical_involution_name": "a",
            "permutation_domain_size": 60,
            "permutation_disagreement_count": 0,
            "fiber_count": 30,
            "fiber_disagreement_count": 0,
            "vertex_map_failure_count": 0,
            "quotient_vertex_count": 30,
            "quotient_edge_count": 60,
            "quotient_edge_disagreement_count": 0,
            "exact_historical_deck_action_recovered": True,
        },
        "native_voltage_construction": {
            "receipt_group": "C2",
            "section_rule": "minimum_labeled_vertex_in_each_fiber_is_sheet0",
            "base_vertex_count": 30,
            "base_edge_count": 60,
            "lift_vertex_count": 60,
            "lift_edge_count": 120,
            "voltage_edge_count": 60,
            "voltage_value_counts": {"0": 32, "1": 28},
            "canonical_voltage_assignment_sha256": "0156b176cd72d105fd39dd23d23ec21be694a91da6357fe97d7426194412bb9e",
            "reconstruction_missing_edge_count": 0,
            "reconstruction_extra_edge_count": 0,
            "exact_G60_reconstruction": True,
        },
        "gauge_and_holonomy": {
            "base_cycle_rank": 31,
            "spanning_tree_edge_count": 29,
            "fundamental_chord_count": 31,
            "fundamental_holonomy_value_counts": {"0": 11, "1": 20},
            "holonomy_image": [0, 1],
            "holonomy_surjective_to_C2": True,
            "lift_connected": True,
            "single_vertex_gauge_test_count": 30,
            "gauge_normal_form_failure_count": 0,
            "normalized_voltage_assignment_sha256": "1a791769f546d3640ddc44a224ba8da261688fe652bd63c42cdbbd65e7ff533b",
        },
        "theorem": (
            "Among native semiregular automorphism actions on G60, exactly "
            "one binary action is invariant under the full native "
            "automorphism group. It is exactly the preserved G60-to-G30 "
            "deck involution. A deterministic section of its fibers derives "
            "a C2 edge-voltage assignment on G30 whose regular lift "
            "reconstructs G60 exactly and whose holonomy image is all of C2."
        ),
        "boundary": {
            "all_22_native_action_classes_remain_valid": True,
            "binary_receipt_not_derived_from_unlabeled_G60_alone": True,
            "full_automorphism_covariance_is_a_declared_premise": True,
            "section_dependent_voltage_values_are_not_canonical": True,
            "gauge_class_is_canonical_given_selected_cover": True,
            "orientation_claim": False,
            "physics_claim": False,
            "electron_claim": False,
            "gravity_claim": False,
            "radiation_claim": False,
        },
        "verdict": (
            "G60_is_the_exact_connected_regular_C2_receipt_lift_of_G30_"
            "selected_uniquely_by_binary_full_automorphism_covariance"
        ),
        "keeper": (
            "The abstract packet met the raw graph. G60 returned its "
            "fully symmetric binary cover, its voltage, and its receipt."
        ),
    }


def expected_note() -> str:
    return """# G60 Receipt-Packet Native Encounter Theorem 006

## Result

The abstract finite receipt algebra was applied to raw G60 without first
selecting a receipt group, quotient, orientation, or preferred subgroup.
The blind native census found 198 semiregular subgroups in 22 conjugacy
classes. All 22 classes define cover-admissible actions, so the blind
outcome is multiple rather than unique.

Within the binary subspectrum there are three C2 conjugacy classes. Their
conjugacy-orbit sizes are 15, 2, and 1. Therefore exactly one binary action
is normal under the full native automorphism group. It is blind class 22,
represented by automorphism index 326.

## Post-registered identification

Only after the blind result and its adjudication were hash-locked was the
historical G60-to-G30 quotient certificate opened. The class-22
permutation agrees with the historical deck involution a on all 60
vertices. Its 30 two-point orbits equal the historical fibers exactly.
The induced vertex projection and all 60 quotient edges also agree
exactly.

Thus the blind process independently recovered the preserved G60-to-G30
deck action.

## Native receipt voltage

Choose the minimum-labeled member of each two-point fiber as sheet zero.
Every edge of G30 then receives the C2 voltage determined by the sheet of
the lifted endpoint reached from the selected section.

The resulting voltage assignment is defined on all 60 G30 edges. Its
regular lift reconstructs all 60 vertices and all 120 edges of G60 with
no missing or extra edge.

The raw section contains 32 zero-voltage edges and 28 one-voltage edges.
These individual values depend on the chosen section.

## Gauge class and holonomy

A deterministic spanning tree of G30 has 29 edges, leaving 31 fundamental
chords. Tree normalization sends every tree voltage to zero. The 31
fundamental circuit receipts consist of 11 zeros and 20 ones, so the
holonomy image is all of C2.

The normalized voltage assignment is unchanged under all 30 tested
single-vertex basis gauge transformations. The surjective holonomy
certifies that the regular binary lift is connected.

## Exact theorem

Among native semiregular automorphism actions on G60, exactly one binary
action is invariant under the full native automorphism group. It is
exactly the preserved G60-to-G30 deck involution. A deterministic section
of its fibers derives a C2 edge-voltage assignment on G30 whose regular
lift reconstructs G60 exactly and whose holonomy image is all of C2.

## Boundary

The raw graph admits 22 cover-admissible action classes. It does not
select the binary class without the declared premises that the receipt is
binary and that its action is invariant under the full native
automorphism group.

The section-dependent edge values are not canonical. Their gauge class
and holonomy image are canonical once the binary cover is selected.

No orientation, electron, gravity, radiation, or other physical claim is
made.

## Keeper

The abstract packet met the raw graph. G60 returned its fully symmetric
binary cover, its voltage, and its receipt.
"""


def contains_all(path: Path, markers: list[str]) -> bool:
    text = path.read_text(encoding="utf-8")
    return all(marker in text for marker in markers)


parser = argparse.ArgumentParser()
parser.add_argument("--write", action="store_true")
args = parser.parse_args()

if args.write:
    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    NOTE.parent.mkdir(parents=True, exist_ok=True)

    ARTIFACT.write_text(
        json.dumps(expected_artifact(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    NOTE.write_text(expected_note(), encoding="utf-8")

    print("OUT ==")
    print("PACKET: g60_receipt_packet_native_encounter_theorem_006")
    print("ACTION: write deterministic theorem package")
    print(f"FILE: wrote {ARTIFACT.relative_to(TARGET)}")
    print(f"FILE: wrote {NOTE.relative_to(TARGET)}")
    print("MUTATION_PERFORMED: true")
    raise SystemExit(0)

roots = [TARGET, MATH42, PHYSICS]
status_before = {str(root): git_status(root) for root in roots}

actual_hashes = {
    name: sha256(path)
    for name, path in SOURCE_PATHS.items()
}

print("OUT ==")
print("PACKET: g60_receipt_packet_native_encounter_theorem_006")
print("MODE: read-only theorem package audit")
print(f"TARGET: {TARGET}")
print("REPOSITORY_MUTATION: none")

print()
print("== SOURCE LOCK ==")
for name in SOURCE_PATHS:
    print(f"{name.upper()}_SHA256: {actual_hashes[name]}")
    print(
        f"CHECK_{name.upper()}_HASH:",
        str(actual_hashes[name] == EXPECTED_HASHES[name]).lower(),
    )

artifact_exists = ARTIFACT.is_file()
note_exists = NOTE.is_file()

artifact_exact = (
    artifact_exists
    and json.loads(ARTIFACT.read_text(encoding="utf-8"))
    == expected_artifact()
)

note_exact = (
    note_exists
    and NOTE.read_text(encoding="utf-8") == expected_note()
)

prior_checks = {
    "blind_census_locked": contains_all(
        BLIND,
        [
            "SEMIREGULAR_SUBGROUP_COUNT: 198",
            "SEMIREGULAR_SUBGROUP_CONJUGACY_CLASS_COUNT: 22",
            "COVER_ADMISSIBLE_CLASS_COUNT: 22",
            "EDGE_INVERTING_CLASS_COUNT: 0",
        ],
    ),
    "blind_adjudication_locked": contains_all(
        ADJUDICATION,
        [
            "BLIND_OUTCOME: multiple",
            "NORMAL_BINARY_CLASS_COUNT: 1",
            "NORMAL_BINARY_CLASS_INDEX: 22",
            "FAILED_CHECKS: []",
        ],
    ),
    "exact_unblinding_locked": contains_all(
        UNBLINDING,
        [
            "PERMUTATION_DISAGREEMENT_COUNT: 0",
            "CHECK_BLIND_ORBITS_EQUAL_HISTORICAL_FIBERS: true",
            "CHECK_DERIVED_QUOTIENT_EDGES_EQUAL_CERTIFICATE: true",
            "FAILED_CHECKS: []",
        ],
    ),
    "native_voltage_locked": contains_all(
        VOLTAGE,
        [
            "CANONICAL_VOLTAGE_ASSIGNMENT_SHA256: 0156b176cd72d105fd39dd23d23ec21be694a91da6357fe97d7426194412bb9e",
            "CHECK_RECONSTRUCTED_G60_EQUALS_RAW_G60: true",
            "HOLONOMY_IMAGE: [0, 1]",
            "NORMALIZED_VOLTAGE_ASSIGNMENT_SHA256: 1a791769f546d3640ddc44a224ba8da261688fe652bd63c42cdbbd65e7ff533b",
            "THEOREM_PASS: true",
            "FAILED_CHECKS: []",
        ],
    ),
}

artifact = (
    json.loads(ARTIFACT.read_text(encoding="utf-8"))
    if artifact_exists
    else {}
)

checks = {
    "all_source_hashes_locked": actual_hashes == EXPECTED_HASHES,
    **prior_checks,
    "artifact_exists": artifact_exists,
    "note_exists": note_exists,
    "artifact_exact": artifact_exact,
    "note_exact": note_exact,
    "blind_outcome_remains_multiple": (
        artifact.get("blind_census", {}).get("blind_outcome") == "multiple"
    ),
    "selection_is_conditional": (
        artifact.get("normal_binary_selection", {}).get(
            "selection_is_unique_given_declared_premises"
        ) is True
        and artifact.get("normal_binary_selection", {}).get(
            "selection_is_unique_without_declared_premises"
        ) is False
    ),
    "exact_reconstruction_recorded": (
        artifact.get("native_voltage_construction", {}).get(
            "exact_G60_reconstruction"
        ) is True
    ),
    "surjective_holonomy_recorded": (
        artifact.get("gauge_and_holonomy", {}).get(
            "holonomy_image"
        ) == [0, 1]
    ),
    "no_orientation_claim": (
        artifact.get("boundary", {}).get("orientation_claim") is False
    ),
    "no_physics_claim": (
        artifact.get("boundary", {}).get("physics_claim") is False
    ),
}

print()
print("== THEOREM PACKAGE ==")
print(f"ARTIFACT_EXISTS: {str(artifact_exists).lower()}")
print(f"NOTE_EXISTS: {str(note_exists).lower()}")
print(f"ARTIFACT_EXACT: {str(artifact_exact).lower()}")
print(f"NOTE_EXACT: {str(note_exact).lower()}")

print()
print("== THEOREM CHECKS ==")
for name, value in checks.items():
    print(f"CHECK_{name.upper()}: {str(value).lower()}")

failed_checks = [name for name, value in checks.items() if not value]
print(f"FAILED_CHECKS: {json.dumps(failed_checks)}")

status_after = {str(root): git_status(root) for root in roots}
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
    raise RuntimeError("encounter theorem audit failed")

print()
print("THEOREM_PASS: true")
print(
    "VERDICT:",
    expected_artifact()["verdict"],
)
print(
    "FINAL_CLASSIFICATION:",
    "native_G60_receipt_packet_encounter_theorem_locked_and_reproducible",
)
print(
    "BOUNDARY:",
    "The theorem uniquely selects the G60-to-G30 cover only after binary "
    "receipt and full-automorphism covariance are declared. The complete "
    "blind spectrum remains 22 classes. No orientation or physics claim "
    "is made."
)
print(
    "KEEPER:",
    expected_artifact()["keeper"],
)
print("MUTATION_PERFORMED: false")
