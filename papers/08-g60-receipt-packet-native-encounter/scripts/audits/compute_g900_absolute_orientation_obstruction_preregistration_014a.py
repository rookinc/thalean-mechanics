#!/usr/bin/env python3
"""Freeze the retrospective G900 absolute-orientation promotion contract."""

from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
from datetime import datetime, timezone

PROJECT = pathlib.Path(__file__).resolve().parents[2]

P08 = PROJECT
P41 = pathlib.Path(
    "/data/data/com.termux/files/home/dev/cori/research/"
    "mathematics/41-order-4-dodecahedral-residue"
)
P42 = pathlib.Path(
    "/data/data/com.termux/files/home/dev/cori/research/"
    "mathematics/42-graph-automorphism-groups"
)
P45 = pathlib.Path(
    "/data/data/com.termux/files/home/dev/cori/research/"
    "mathematics/45-native-g60-surface-complex"
)
TMP = pathlib.Path(
    "/data/data/com.termux/files/home/tmp"
)

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

EXPECTED_HEAD = "2a8efc9 Lock G60 H3 triality-Galois ledge"

AUTHORITIES = {
    "p08_duad_orientation_bridge": {
        "path":
            P08 / "artifacts/json"
            / "g60_duad_orientation_bridge_census_011g.v1.json",
        "sha256":
            "abc9e038b323fdd5af852a91b87aca4c5a1e35a6e484608af27a04a399c52e9c",
    },
    "p08_full_A_orientation_extension": {
        "path":
            P08 / "artifacts/json"
            / "g60_full_A_orientation_character_extension_census_011o.v1.json",
        "sha256":
            "ad684db8bb65c5eb731c972d33e685ffc18a947f63c9ba4e9758f815821f0941",
    },
    "p08_triality_galois_ledge": {
        "path":
            P08 / "artifacts/json"
            / "g60_h3_triality_galois_ledge_013f.v1.json",
        "sha256":
            "920635dd384d4325d2f415945811a7c816b0df5d0d475e974367010110a7a923",
    },
    "p41_native_source_library": {
        "path":
            P41 / "scripts/lib/project41_native.py",
        "sha256":
            "b6e3df135c93b27dcc0a823eb7ab036f6740a82664c7502f420d2a76a2cb962a",
    },
    "p41_g900_constructor": {
        "path":
            P41 / "scripts"
            / "audit_external_carrier_native_frame_compatibility_030p.py",
        "sha256":
            "deb534de0ec401a60ccaf80ce23b460c3c66b49436a6fdb3b7156d35afb08c7d",
    },
    "p42_native_action": {
        "path":
            P42 / "artifacts/json"
            / "native_g60_fiber_product_isomorphism_044.json",
        "sha256":
            "b37313b135495752b11e525bb61979163fdf54aec4be4f5d027dcee64c9efc21",
    },
    "p45_native_surface_orientation": {
        "path":
            P45 / "artifacts/json"
            / "native_g60_surface_orientation_004.json",
        "sha256":
            "b7671045c8dee327d9f02d6a04c5707231f46815e05596b2b1074bed564b2ae8",
    },
    "p45_H60_group": {
        "path":
            P45 / "artifacts/json"
            / "g60_generated_extension_group_016.json",
        "sha256":
            "87090707d5f018fbf9f4db5ad793fc6b492e9fd6fec3f3c54af89d985f2d5d63",
    },
    "p45_full_g900_automorphism": {
        "path":
            P45 / "artifacts/json"
            / "g900_full_automorphism_group_census_021.json",
        "sha256":
            "8f85f690366e283148feb49bdd00a836244c054a2a0ac55422e6ac568754b484",
    },
    "p45_residual_slot_maps": {
        "path":
            P45 / "artifacts/json"
            / "g900_residual_involution_slot_maps_022.json",
        "sha256":
            "92d91c90dbf88127a5d2972d9445c29a4ed98e2f7dc67ee5b262b692463493a5",
    },
    "p45_g900_wrapup": {
        "path":
            P45 / "artifacts/json"
            / "g900_projection_and_automorphism_wrapup_023.json",
        "sha256":
            "c9186b3a5df08d1591691881ca375f4ede865aa0708a12a7374f03395333ee9c",
    },
}

SOURCE_CANDIDATES = {
    "004_v4_alignment": {
        "path":
            TMP / "test-g900-tricycle-v4-alignment-004.py",
        "sha256":
            "ba495c8266002cab382d9fd0e228f81ac7763675d2ee4c56357d40d11fb1c5a8",
    },
    "008_extension_membership": {
        "path":
            TMP / "audit-g900-tricycle-extension-membership-008.py",
        "sha256":
            "17b641f90a5ed0a615565765c9c9a2a1a168e94d4c772c8a25ac86b2f3866b3a",
    },
    "010_exact_A60": {
        "path":
            TMP / "audit-g900-transverse-v4-exact-order-010.py",
        "sha256":
            "1d575e2e00af0677ce8c2024501ad21ffc18de043e7f1695964821c3896ff1d7",
    },
    "011_absolute_character": {
        "path":
            TMP / "audit-g900-absolute-orientation-character-011.py",
        "sha256":
            "b2a39e05fa64f37aab281b8dacb7de196d7fcc4ece7a545c349a46126b5c3f30",
    },
    "014_vertex_root_bridge": {
        "path":
            TMP / "audit-g60-vertex-orientation-root-bridge-014.py",
        "sha256":
            "49606d2670b8180b0326a35b48b0352cc3f4816a8bf3d762523234a3dea3aa4a",
    },
    "015_half_flip_incidence": {
        "path":
            TMP / "audit-g900-half-flip-relative-root-incidence-015.py",
        "sha256":
            "95e211068305a6831b18f5938353237524d0baccd218254c0b0db95ef668ee37",
    },
    "016_nearest_root": {
        "path":
            TMP / "audit-g900-half-flip-nearest-root-016.py",
        "sha256":
            "eb2c74b82e35630a55fad345023da68acc332fbfa965f4d2a3fa6f0f813647f7",
    },
    "017_root_germ": {
        "path":
            TMP / "audit-g900-half-flip-root-germ-017.py",
        "sha256":
            "df109d2347b7e6c52ccca1f4ee30f7695d3c1d19af44567bc4a08105d46e4d7e",
    },
}

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

def inspect_rows(rows):
    output = {}

    for name, row in rows.items():
        path = row["path"]
        exists = path.is_file()
        actual = sha256(path) if exists else None

        output[name] = {
            "path": str(path),
            "exists": exists,
            "expected_sha256": row["sha256"],
            "actual_sha256": actual,
            "hash_match":
                exists and actual == row["sha256"],
        }

    return output

head = git(
    "--no-pager",
    "show",
    "-s",
    "--format=%h %s",
    "HEAD",
)
status_before = git("status", "--short", "--", ".")

authority_rows = inspect_rows(AUTHORITIES)
source_rows = inspect_rows(SOURCE_CANDIDATES)

all_authorities_match = all(
    row["hash_match"]
    for row in authority_rows.values()
)
all_sources_match = all(
    row["hash_match"]
    for row in source_rows.values()
)

untracked_013e_present = (
    "?? scripts/audits/"
    "compute_g60_root_relative_sign_kernel_census_013e.py"
    in status_before
)

checks = {
    "head_locked":
        head == EXPECTED_HEAD,
    "all_authority_hashes_match":
        all_authorities_match,
    "all_source_candidate_hashes_match":
        all_sources_match,
    "untracked_013e_present_and_out_of_scope":
        untracked_013e_present,
}

failed = [
    name
    for name, passed in checks.items()
    if not passed
]

preregistration_frozen = not failed

result = {
    "packet":
        "g900_absolute_orientation_obstruction_"
        "preregistration_014a",
    "mode":
        "retrospective_promotion_preregistration_"
        "frozen_before_consolidated_recomputation",
    "promotion_date_utc":
        "2026-08-07",
    "locked_head":
        head,
    "expected_head":
        EXPECTED_HEAD,
    "exploratory_results_already_observed":
        True,
    "blind_preregistration_claim":
        False,
    "authorities":
        authority_rows,
    "temporary_source_candidates":
        source_rows,
    "theorem_contract": {
        "carrier":
            "exact_source_native_G900_on_V_G15_times_V_G60",
        "orientation_root_set_size":
            20,
        "claims_to_recompute": [
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
        ],
        "expected_exact_values": {
            "A60_order":
                "4160493556370695072138170591611682190377086303180622976224638848204800000000000000",
            "surface_character_counts": {
                "preserving": 240,
                "reversing": 240,
                "parity_agreement": 240,
                "parity_disagreement": 240,
            },
            "G900_automorphism_group_order":
                2,
            "fixed_slots":
                [6, 12, 13],
            "fixed_vertex_count":
                180,
            "fixed_slot_sign_profiles": {
                "6": {"0": 2, "1": 2},
                "12": {"0": 4},
                "13": {"0": 4},
            },
            "vertex_stabilizer_order":
                8,
            "vertex_stabilizer_fixed_root_count":
                0,
            "half_flip_H60_centralizer_order":
                1,
            "direct_incidence_state_profile": {
                "0": 40,
                "1": 20,
            },
            "nearest_root_minimizer_profile": {
                "1": 38,
                "2": 20,
                "8": 2,
            },
            "half_orbit_candidate_duad_profile": {
                "1": 19,
                "2": 10,
                "4": 1,
            },
            "radial_unique_state_counts": {
                "0": 38,
                "1": 42,
                "2": 50,
                "3": 50,
                "4": 45,
                "5": 36,
                "6": 0,
            },
            "radius_6_minimizer_profile": {
                "4": 60,
            },
        },
        "success_condition":
            "all exact values reproduce and no tested family "
            "selects both a root and epsilon",
        "failure_condition":
            "any authority hash changes, any exact profile fails "
            "to reproduce, or a tested family selects an "
            "unanchored absolute sheet",
    },
    "intended_classification":
        "canonical_G900_orientation_hinge_with_"
        "unanchored_absolute_orientation_obstruction",
    "earned_statement_candidate":
        "The exact G900 carrier canonically locates a unique mixed "
        "orientation hinge, but the G60 surface character does not "
        "extend through the carrier closure, no H60-equivariant "
        "vertex-to-root map exists, and no native radial hinge-germ "
        "selector through the full G60 diameter selects a root at "
        "every state. The epsilon sheet and absolute positive "
        "orientation therefore remain unselected without a "
        "compatible pointed anchor.",
    "boundary": {
        "global_impossibility_for_every_conceivable_selector":
            False,
        "tested_character_family_closed":
            True,
        "tested_equivariant_map_family_closed":
            True,
        "tested_radial_hinge_germ_family_closed":
            True,
        "external_anchor_required_within_tested_families":
            True,
        "absolute_orientation_selected":
            False,
        "epsilon_selected":
            False,
        "physical_orientation_claim":
            False,
        "force_claim":
            False,
        "energy_claim":
            False,
        "spacetime_claim":
            False,
        "quantum_claim":
            False,
        "manuscript_mutated":
            False,
    },
    "repository": {
        "preexisting_out_of_scope_paths":
            ["scripts/audits/compute_g60_root_relative_sign_kernel_census_013e.py"],
        "untracked_013e_preserved":
            untracked_013e_present,
        "commit_performed":
            False,
        "push_performed":
            False,
    },
    "checks":
        checks,
    "failed_check_count":
        len(failed),
    "failed_checks":
        failed,
    "preregistration_frozen":
        preregistration_frozen,
    "consolidated_computation_performed":
        False,
    "result_frozen":
        False,
}

JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
NOTE_PATH.parent.mkdir(parents=True, exist_ok=True)
RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)

JSON_PATH.write_text(
    json.dumps(
        result,
        indent=2,
        sort_keys=True,
    )
    + "\n",
    encoding="utf-8",
)

note = """# G900 absolute-orientation obstruction preregistration 014a

## Status

This is a retrospective promotion preregistration. The exploratory
results were already observed. No blind-preregistration claim is made.

The purpose of this packet is to freeze the exact authorities, source
candidate hashes, theorem scope, expected profiles, failure conditions,
and claim boundaries before one independent consolidated recomputation.

## Frozen target

The consolidated computation must test the exact source-native G900
carrier and reproduce the following chain:

1. The tricycle sheet V4 aligns with the native G60 V4.
2. The transverse V4 is outside the tricycle extension.
3. The native and transverse V4 generate A60.
4. Adding the order-480 H60 action reaches S60.
5. The oriented-surface character is a valid H60 character but is not
   permutation parity and does not extend through S60.
6. No H60-equivariant map from the 60 local vertices to the twenty
   orientation roots exists.
7. The carrier has one unique mixed fixed hinge at slot 6.
8. Direct half-flip incidence and every radial hinge-germ radius from
   zero through the G60 diameter fail to select one root at every state.
9. Neither epsilon nor an absolute positive sheet is selected.

## Intended statement

The exact G900 carrier canonically locates the orientation hinge, but
does not generate an unanchored absolute orientation within the tested
character, equivariant-map, and radial hinge-germ families. A compatible
pointed anchor remains necessary.

## Boundary

This is not a theorem against every conceivable graph-definable
selector. It closes only the explicitly tested families. It makes no
physical orientation, force, energy, spacetime, or quantum claim.

The unrelated untracked 013e computation remains outside this packet.
"""

NOTE_PATH.write_text(
    note,
    encoding="utf-8",
)

receipt_lines = [
    "== G900 ABSOLUTE-ORIENTATION PREREGISTRATION 014A ==",
    "PACKET: " + result["packet"],
    "MODE: " + result["mode"],
    "HEAD: " + head,
    "EXPLORATORY_RESULTS_ALREADY_OBSERVED: true",
    "BLIND_PREREGISTRATION_CLAIM: false",
    "AUTHORITY_COUNT: " + str(len(authority_rows)),
    "SOURCE_CANDIDATE_COUNT: " + str(len(source_rows)),
    "ALL_AUTHORITY_HASHES_MATCH: "
        + str(all_authorities_match).lower(),
    "ALL_SOURCE_HASHES_MATCH: "
        + str(all_sources_match).lower(),
    "UNTRACKED_013E_PRESERVED: "
        + str(untracked_013e_present).lower(),
    "FAILED_CHECK_COUNT: " + str(len(failed)),
    "FAILED_CHECKS: " + repr(failed),
    "PREREGISTRATION_FROZEN: "
        + str(preregistration_frozen).lower(),
    "CONSOLIDATED_COMPUTATION_PERFORMED: false",
    "RESULT_FROZEN: false",
    "ABSOLUTE_ORIENTATION_SELECTED: false",
    "PHYSICAL_CLAIM: false",
    "COMMIT_PERFORMED: false",
    "PUSH_PERFORMED: false",
]

RECEIPT_PATH.write_text(
    "\n".join(receipt_lines) + "\n",
    encoding="utf-8",
)

print("\n".join(receipt_lines))
print("JSON:", JSON_PATH)
print("JSON_SHA256:", sha256(JSON_PATH))
print("NOTE:", NOTE_PATH)
print("NOTE_SHA256:", sha256(NOTE_PATH))
print("RECEIPT:", RECEIPT_PATH)
print("RECEIPT_SHA256:", sha256(RECEIPT_PATH))
print("PROJECT_MUTATION_PERFORMED: true")
print("MUTATION_SCOPE: preregistration_packet_only")

if failed:
    raise SystemExit(1)
