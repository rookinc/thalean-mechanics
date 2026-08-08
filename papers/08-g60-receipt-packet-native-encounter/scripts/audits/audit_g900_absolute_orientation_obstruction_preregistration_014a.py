#!/usr/bin/env python3
"""Audit the frozen G900 absolute-orientation obstruction preregistration."""

from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess

PROJECT = pathlib.Path(__file__).resolve().parents[2]

JSON_PATH = (
    PROJECT
    / "artifacts/json"
    / "g900_absolute_orientation_obstruction_"
      "preregistration_014a.v1.json"
)
NOTE_PATH = (
    PROJECT
    / "notes"
    / "g900_absolute_orientation_obstruction_"
      "preregistration_014a.md"
)
RECEIPT_PATH = (
    PROJECT
    / "artifacts/receipts"
    / "g900_absolute_orientation_obstruction_"
      "preregistration_014a.txt"
)
COMPUTE_PATH = (
    PROJECT
    / "scripts/audits"
    / "compute_g900_absolute_orientation_obstruction_"
      "preregistration_014a.py"
)

EXPECTED_HASHES = {
    JSON_PATH:
        "0a43dc5524b6564e8de2656391fe71059f7193c294e70d550f61ff6917c44ca5",
    NOTE_PATH:
        "b7dbfddce142f77893ef1c88da5acecb6eb1cde8e4c529b4dd9c1c6ed03db96f",
    RECEIPT_PATH:
        "567b7d29120631773544b0326a3ae8bce8137a787a556222e1f2e965eab90e12",
    COMPUTE_PATH:
        "1e53a104c3021f19abe325d1b22bc5cdc9318740fedce9c2a9ba2254d8b5939f",
}

EXPECTED_CLAIMS = [
    "tricycle_sheet_V4_aligns_with_native_V4",
    "transverse_V4_is_excluded_from_the_tricycle_extension",
    "native_and_transverse_V4_generate_A60",
    "surface_orientation_character_is_a_nonparity_H60_character",
    "surface_character_does_not_extend_through_S60_closure",
    "full_G900_automorphism_group_has_order_2",
    "fixed_slots_are_6_12_13",
    "slot_6_is_the_unique_mixed_fixed_hinge",
    "no_H60_equivariant_vertex_to_root_map_exists",
    "direct_half_flip_root_incidence_is_nonfunctional",
    "nearest_root_relation_is_inversion_covariant",
    "no_ball_radius_0_through_6_closes_root_selection",
    "epsilon_is_not_selected",
    "absolute_positive_sheet_is_not_selected",
]

A60_ORDER = (
    "4160493556370695072138170591611682190377086303180622976224638848204800000000000000"
)

def sha256(path: pathlib.Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for block in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(block)

    return digest.hexdigest()

def git(*arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments],
        cwd=PROJECT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    ).stdout.rstrip()

data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
note = NOTE_PATH.read_text(encoding="utf-8")
receipt = RECEIPT_PATH.read_text(encoding="utf-8")

contract = data["theorem_contract"]
expected = contract["expected_exact_values"]
boundary = data["boundary"]
repository = data["repository"]

file_hash_checks = {
    path.name:
        path.is_file()
        and sha256(path) == expected_hash
    for path, expected_hash in EXPECTED_HASHES.items()
}

authority_rows = data["authorities"]
source_rows = data["temporary_source_candidates"]

checks = {
    "all_frozen_file_hashes_match":
        all(file_hash_checks.values()),
    "packet_name":
        data.get("packet")
        == "g900_absolute_orientation_obstruction_"
           "preregistration_014a",
    "mode":
        data.get("mode")
        == "retrospective_promotion_preregistration_"
           "frozen_before_consolidated_recomputation",
    "locked_head":
        data.get("locked_head")
        == "2a8efc9 Lock G60 H3 triality-Galois ledge",
    "expected_head":
        data.get("expected_head")
        == "2a8efc9 Lock G60 H3 triality-Galois ledge",
    "retrospective_disclosure":
        data.get("exploratory_results_already_observed") is True
        and data.get("blind_preregistration_claim") is False,
    "authority_count_11":
        len(authority_rows) == 11,
    "all_authority_hashes_match":
        all(
            row.get("hash_match") is True
            for row in authority_rows.values()
        ),
    "source_candidate_count_8":
        len(source_rows) == 8,
    "all_source_candidate_hashes_match":
        all(
            row.get("hash_match") is True
            for row in source_rows.values()
        ),
    "claim_contract_exact":
        contract.get("claims_to_recompute")
        == EXPECTED_CLAIMS,
    "A60_order_exact":
        expected.get("A60_order") == A60_ORDER,
    "surface_character_counts":
        expected.get("surface_character_counts")
        == {
            "preserving": 240,
            "reversing": 240,
            "parity_agreement": 240,
            "parity_disagreement": 240,
        },
    "G900_automorphism_order_2":
        expected.get("G900_automorphism_group_order") == 2,
    "fixed_locus_exact":
        expected.get("fixed_slots") == [6, 12, 13]
        and expected.get("fixed_vertex_count") == 180,
    "fixed_hinge_profiles_exact":
        expected.get("fixed_slot_sign_profiles")
        == {
            "6": {"0": 2, "1": 2},
            "12": {"0": 4},
            "13": {"0": 4},
        },
    "vertex_root_obstruction_exact":
        expected.get("vertex_stabilizer_order") == 8
        and expected.get(
            "vertex_stabilizer_fixed_root_count"
        ) == 0,
    "half_flip_centralizer_exact":
        expected.get(
            "half_flip_H60_centralizer_order"
        ) == 1,
    "direct_incidence_profile_exact":
        expected.get("direct_incidence_state_profile")
        == {"0": 40, "1": 20},
    "nearest_root_profile_exact":
        expected.get("nearest_root_minimizer_profile")
        == {"1": 38, "2": 20, "8": 2},
    "half_orbit_profile_exact":
        expected.get("half_orbit_candidate_duad_profile")
        == {"1": 19, "2": 10, "4": 1},
    "radial_unique_counts_exact":
        expected.get("radial_unique_state_counts")
        == {
            "0": 38,
            "1": 42,
            "2": 50,
            "3": 50,
            "4": 45,
            "5": 36,
            "6": 0,
        },
    "radius_6_profile_exact":
        expected.get("radius_6_minimizer_profile")
        == {"4": 60},
    "intended_classification":
        data.get("intended_classification")
        == "canonical_G900_orientation_hinge_with_"
           "unanchored_absolute_orientation_obstruction",
    "tested_families_closed":
        boundary.get("tested_character_family_closed") is True
        and boundary.get(
            "tested_equivariant_map_family_closed"
        ) is True
        and boundary.get(
            "tested_radial_hinge_germ_family_closed"
        ) is True,
    "global_boundary_preserved":
        boundary.get(
            "global_impossibility_for_every_conceivable_selector"
        ) is False,
    "orientation_not_selected":
        boundary.get("absolute_orientation_selected") is False
        and boundary.get("epsilon_selected") is False,
    "no_physical_claims":
        all(
            boundary.get(key) is False
            for key in (
                "physical_orientation_claim",
                "force_claim",
                "energy_claim",
                "spacetime_claim",
                "quantum_claim",
            )
        ),
    "preregistration_frozen":
        data.get("preregistration_frozen") is True,
    "computation_not_performed":
        data.get(
            "consolidated_computation_performed"
        ) is False,
    "result_not_frozen":
        data.get("result_frozen") is False,
    "generation_checks_clean":
        data.get("failed_check_count") == 0
        and data.get("failed_checks") == [],
    "untracked_013e_preserved":
        repository.get("untracked_013e_preserved") is True,
    "no_commit_or_push":
        repository.get("commit_performed") is False
        and repository.get("push_performed") is False,
    "note_discloses_retrospective_status":
        "retrospective promotion preregistration" in note
        and "No blind-preregistration claim is made." in note,
    "note_preserves_scope":
        "not a theorem against every conceivable"
        in note
        and "physical orientation" in note,
    "receipt_freeze_exact":
        "PREREGISTRATION_FROZEN: true" in receipt
        and "RESULT_FROZEN: false" in receipt
        and "ABSOLUTE_ORIENTATION_SELECTED: false"
            in receipt,
}

failed = [
    name
    for name, passed in checks.items()
    if not passed
]

status = git("status", "--short", "--", ".")

print(
    "== G900 ABSOLUTE-ORIENTATION "
    "PREREGISTRATION AUDIT 014A =="
)
print("PACKET:", data.get("packet"))
print("MODE:", data.get("mode"))
print("JSON_SHA256:", sha256(JSON_PATH))
print("NOTE_SHA256:", sha256(NOTE_PATH))
print("RECEIPT_SHA256:", sha256(RECEIPT_PATH))
print("COMPUTE_SHA256:", sha256(COMPUTE_PATH))
print("AUTHORITY_COUNT:", len(authority_rows))
print("SOURCE_CANDIDATE_COUNT:", len(source_rows))
print(
    "CLAIM_CONTRACT_COUNT:",
    len(contract.get("claims_to_recompute", [])),
)
print(
    "RADIAL_UNIQUE_STATE_COUNTS:",
    expected.get("radial_unique_state_counts"),
)
print(
    "INTENDED_CLASSIFICATION:",
    data.get("intended_classification"),
)
print("CHECK_COUNT:", len(checks))
print("FAILED_CHECK_COUNT:", len(failed))
print("FAILED_CHECKS:", failed)
print("AUDIT_PASS:", not failed)
print(
    "PREREGISTRATION_FROZEN:",
    data.get("preregistration_frozen"),
)
print(
    "CONSOLIDATED_COMPUTATION_PERFORMED:",
    data.get("consolidated_computation_performed"),
)
print("RESULT_FROZEN:", data.get("result_frozen"))
print("ABSOLUTE_ORIENTATION_SELECTED: false")
print("PHYSICAL_CLAIM: false")
print("COMMIT_PERFORMED: false")
print("PUSH_PERFORMED: false")
print("UNTRACKED_013E_PRESENT:", (
    "?? scripts/audits/"
    "compute_g60_root_relative_sign_kernel_census_013e.py"
    in status
))
print("REPOSITORY_MUTATION_PERFORMED: false")

if failed:
    raise SystemExit(1)
