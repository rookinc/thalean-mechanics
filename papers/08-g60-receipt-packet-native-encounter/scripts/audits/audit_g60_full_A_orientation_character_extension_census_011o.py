#!/usr/bin/env python3
import hashlib
import json
import subprocess
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
JSON_PATH = PROJECT / "artifacts/json/g60_full_A_orientation_character_extension_census_011o.v1.json"
RAW_PATH = PROJECT / "artifacts/receipts/g60_full_A_orientation_character_extension_census_011o_raw_run.txt"
NOTE_PATH = PROJECT / "notes/g60_full_A_orientation_character_extension_census_011o.md"
COMPUTE_PATH = PROJECT / "scripts/audits/compute_g60_full_A_orientation_character_extension_census_011o.py"

EXPECTED_JSON_HASH = "ad684db8bb65c5eb731c972d33e685ffc18a947f63c9ba4e9758f815821f0941"
EXPECTED_RAW_HASH = "83e5c75e98f4c4c676cbdac9ef522e516604bac8520f3429563c8f1d7c2bdc28"
EXPECTED_NOTE_HASH = "5df67d21baaf1f392d3b3a2ff0194bc16d1d7f3980cc93564f29e28b829caac4"
EXPECTED_COMPUTE_HASH = "98356ac2b2b0f19b6d8ec6d8f79056877d63b3d0981e4140ac966dd6805cc695"
EXPECTED_CANDIDATE_HASH = "4a33590b9585a782ea4ae073afb0b778f39c4323e70ff606ab3d12ba66099f21"
LOCKED_HEAD = "dfd715e Preregister G60 full-A orientation character test"

EXPECTED_MAP_HASHES = [
    "782dbcb9dae045cfc5dadd1b81f51895e447e981491263e09514c9077dfe1728",
    "bb61e5018270d8954e8115bb9c1fbbcfb07f360ba307c451cb16103ef7336c01",
]

EXPECTED_ALPHA_0_HASH = "21c95a566c02c8de63c4f0158d468948b86e0c1c91a611c672615d15b3b7e79a"
EXPECTED_ALPHA_1_HASH = "3d057f3e36004b4c59aa2754220cf4987587bf0e58ea3492e88f88a31515f39c"
EXPECTED_N_HASH = "f6a65aae2e49825862966b14b59df5a648114838213651b418b1022c25564f70"

def sha256_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def git(*args):
    return subprocess.run(
        ["git", *args],
        cwd=PROJECT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    ).stdout.strip()

data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
group = data["group_reconstruction"]
characters = data["character_census"]
actions = data["full_actions"]
alpha_0 = actions["alpha_0"]
alpha_1 = actions["alpha_1"]
bridges = data["bridge_census"]
anchors = data["anchor_ablation"]
boundary = data["boundary"]
promotion = data["promotion"]
provenance = data["candidate_provenance"]
repository = data["repository"]
authorities = data["authorities"]

head = git("show", "-s", "--format=%h %s", "HEAD")

expected_residual_rows = [
    {"element_index": 0, "p": 0, "n": 0, "alpha_0": 0, "alpha_1": 0},
    {"element_index": 65, "p": 0, "n": 1, "alpha_0": 0, "alpha_1": 1},
    {"element_index": 124, "p": 0, "n": 1, "alpha_0": 0, "alpha_1": 1},
    {"element_index": 326, "p": 0, "n": 0, "alpha_0": 0, "alpha_1": 0},
]

checks = [
    ("packet", data.get("packet") == "g60_full_A_orientation_character_extension_census_011o"),
    ("mode", data.get("mode") == "frozen_complete_full_A_character_extension_census"),
    ("locked_head", data.get("locked_head") == LOCKED_HEAD and head == LOCKED_HEAD),
    ("result_frozen", data.get("result_frozen") is True),
    ("audit_pass_recorded", data.get("audit_pass") is True),
    ("json_hash", sha256_file(JSON_PATH) == EXPECTED_JSON_HASH),
    ("raw_hash", sha256_file(RAW_PATH) == EXPECTED_RAW_HASH),
    ("note_hash", sha256_file(NOTE_PATH) == EXPECTED_NOTE_HASH),
    ("compute_hash", sha256_file(COMPUTE_PATH) == EXPECTED_COMPUTE_HASH),
    ("candidate_hash", provenance.get("candidate_json_sha256") == EXPECTED_CANDIDATE_HASH),
    ("candidate_promoted", promotion.get("candidate_promoted_without_recomputation") is True),
    ("raw_copied", promotion.get("raw_run_receipt_copied_byte_for_byte") is True),
    ("compute_copied", promotion.get("computation_script_copied_byte_for_byte") is True),
    ("syntax_failed_build_not_promoted", promotion.get("syntax_failed_preliminary_build_promoted") is False),
    ("promotion_no_manuscript", promotion.get("manuscript_mutated") is False),
    ("authority_count", len(authorities) == 7),
    ("authority_hashes", all(row.get("hash_match") is True for row in authorities.values())),
    ("group_480", group.get("group_order") == 480),
    ("identity_0", group.get("identity_index") == 0),
    ("closure_zero", group.get("closure_failure_count") == 0),
    ("inverse_zero", group.get("inverse_failure_count") == 0),
    ("operation_ok", group.get("operation_ok") is True),
    ("N_240", group.get("canonical_N_order") == 240),
    ("generator_count_4", characters.get("generator_count") == 4),
    ("greedy_generators", characters.get("greedy_generators") == [1, 2, 3, 8]),
    ("assignment_count_16", characters.get("assignment_count") == 16),
    ("character_row_count_16", len(characters.get("character_rows", [])) == 16),
    ("valid_binary_characters_4", characters.get("valid_binary_character_count") == 4),
    ("p_homomorphism", characters.get("p_homomorphism_failure_count") == 0),
    ("n_homomorphism", characters.get("n_homomorphism_failure_count") == 0),
    ("alpha_0_homomorphism", characters.get("alpha_0_homomorphism_failure_count") == 0),
    ("alpha_1_homomorphism", characters.get("alpha_1_homomorphism_failure_count") == 0),
    ("p_hash", characters.get("p_sha256") == EXPECTED_ALPHA_0_HASH),
    ("alpha_0_hash", characters.get("alpha_0_sha256") == EXPECTED_ALPHA_0_HASH),
    ("alpha_1_hash", characters.get("alpha_1_sha256") == EXPECTED_ALPHA_1_HASH),
    ("n_hash", characters.get("n_sha256") == EXPECTED_N_HASH),
    ("extension_count_2", characters.get("extension_count") == 2),
    ("extensions_exact", characters.get("extensions_exactly_alpha_0_alpha_1") is True),
    ("extension_hashes", characters.get("extension_sha256s") == [EXPECTED_ALPHA_0_HASH, EXPECTED_ALPHA_1_HASH]),
    ("declared_extension_hashes", characters.get("declared_extension_sha256s") == [EXPECTED_ALPHA_0_HASH, EXPECTED_ALPHA_1_HASH]),
    ("residual_rows", characters.get("residual_character_rows") == expected_residual_rows),
    ("alpha_0_formula", alpha_0.get("formula") == "p"),
    ("alpha_1_formula", alpha_1.get("formula") == "p+n"),
    ("alpha_0_valid", alpha_0.get("action_valid") is True),
    ("alpha_1_valid", alpha_1.get("action_valid") is True),
    ("alpha_0_identity_zero", alpha_0.get("identity_failure_count") == 0),
    ("alpha_1_identity_zero", alpha_1.get("identity_failure_count") == 0),
    ("alpha_0_closure_zero", alpha_0.get("closure_failure_count") == 0),
    ("alpha_1_closure_zero", alpha_1.get("closure_failure_count") == 0),
    ("alpha_0_transitive", alpha_0.get("transitive") is True and alpha_0.get("orbit_size_profile") == [20]),
    ("alpha_1_transitive", alpha_1.get("transitive") is True and alpha_1.get("orbit_size_profile") == [20]),
    ("alpha_0_kernel_V4", alpha_0.get("pointwise_kernel") == [0, 65, 124, 326]),
    ("alpha_1_kernel_Z1", alpha_1.get("pointwise_kernel") == [0, 326]),
    ("alpha_0_stabilizer_failures_40", alpha_0.get("stabilizer_match_failure_count") == 40),
    ("alpha_1_stabilizer_failures_zero", alpha_1.get("stabilizer_match_failure_count") == 0),
    ("alpha_0_bridge_zero", bridges.get("alpha_0_bridge_count") == 0),
    ("alpha_0_maps_empty", bridges.get("alpha_0_map_sha256s") == []),
    ("alpha_0_conflict_roots_20", len(bridges.get("alpha_0_rejected_conflict_roots", [])) == 20),
    ("alpha_1_bridge_two", bridges.get("alpha_1_bridge_count") == 2),
    ("alpha_1_map_hashes", bridges.get("alpha_1_map_sha256s") == EXPECTED_MAP_HASHES),
    ("locked_011m_map_hashes", bridges.get("locked_011m_map_sha256s") == EXPECTED_MAP_HASHES),
    ("alpha_1_maps_equal_011m", bridges.get("alpha_1_maps_equal_011m") is True),
    ("reversal_failure_zero", bridges.get("reversal_failure_count") == 0),
    ("reversal_row_count_2", len(bridges.get("reversal_rows", [])) == 2),
    ("reversal_verified", bridges.get("reversal_verified") is True),
    ("reversal_rows_exact", all(
        row.get("reversal_changes_map") is True
        and row.get("sheet_reversal_equals_root_inversion") is True
        for row in bridges.get("reversal_rows", [])
    )),
    ("anchors_40", anchors.get("compatible_anchor_count") == 40),
    ("anchor_rows_40", len(anchors.get("anchor_rows", [])) == 40),
    ("anchor_profile_one", anchors.get("anchor_bridge_count_profile") == {"1": 40}),
    ("all_anchor_rows_unique", all(row.get("bridge_count") == 1 for row in anchors.get("anchor_rows", []))),
    ("anchors_select_unique", anchors.get("all_compatible_anchors_select_unique_bridge") is True),
    ("without_anchor_two", anchors.get("without_anchor_bridge_count") == 2),
    ("classification", data.get("classification") == "p_plus_n_unique_full_A_extension_supports_two_bridges"),
    ("prediction_matches", data.get("prediction_matches") is True),
    ("full_A_source_constructed", boundary.get("full_A_source_action_constructed") is True),
    ("unique_character", boundary.get("unique_supporting_character_identified") is True),
    ("bounded_anchor", boundary.get("bounded_anchor_sufficiency") is True),
    ("no_unanchored_orientation", boundary.get("orientation_selected_without_anchor") is False),
    ("no_global_minimality", boundary.get("global_minimality_claim") is False),
    ("no_manuscript", boundary.get("manuscript_mutated") is False),
    ("no_geometry", boundary.get("geometry_claim") is False),
    ("no_physical_direction", boundary.get("physical_direction_claim") is False),
    ("no_physics", boundary.get("physical_claim") is False),
    ("repository_preserved", repository.get("status_preserved") is True),
    ("candidate_no_project_mutation", repository.get("project_mutation_performed") is False),
    ("earned_statement_present", isinstance(data.get("earned_statement"), str) and len(data["earned_statement"]) > 100),
    ("note_exists", NOTE_PATH.is_file()),
]

failed = [name for name, passed in checks if not passed]

print("== G60 FULL-A ORIENTATION CHARACTER-EXTENSION CENSUS AUDIT 011o ==")
print("PACKET:", data.get("packet"))
print("MODE:", data.get("mode"))
print("JSON_SHA256:", sha256_file(JSON_PATH))
print("NOTE_SHA256:", sha256_file(NOTE_PATH))
print("COMPUTATION_SCRIPT_SHA256:", sha256_file(COMPUTE_PATH))
print("RAW_RUN_RECEIPT_SHA256:", sha256_file(RAW_PATH))
print("VALID_BINARY_CHARACTER_COUNT:", characters.get("valid_binary_character_count"))
print("EXTENSION_COUNT:", characters.get("extension_count"))
print("ALPHA_0_POINTWISE_KERNEL:", alpha_0.get("pointwise_kernel"))
print("ALPHA_1_POINTWISE_KERNEL:", alpha_1.get("pointwise_kernel"))
print("ALPHA_0_BRIDGE_COUNT:", bridges.get("alpha_0_bridge_count"))
print("ALPHA_1_BRIDGE_COUNT:", bridges.get("alpha_1_bridge_count"))
print("ALPHA_1_MAP_SHA256S:", bridges.get("alpha_1_map_sha256s"))
print("REVERSAL_VERIFIED:", str(bridges.get("reversal_verified")).lower())
print("ANCHOR_BRIDGE_COUNT_PROFILE:", anchors.get("anchor_bridge_count_profile"))
print("CLASSIFICATION:", data.get("classification"))
print("CHECK_COUNT:", len(checks))
print("FAILED_CHECK_COUNT:", len(failed))

for name, passed in checks:
    print("CHECK", name + ":", str(bool(passed)).lower())

print("AUDIT_PASS:", str(not failed).lower())
print("FAILED_CHECKS:", failed)
print("EARNED_STATEMENT:", data.get("earned_statement"))
print("FULL_A_SOURCE_ACTION_CONSTRUCTED:", str(boundary.get("full_A_source_action_constructed")).lower())
print("ORIENTATION_SELECTED_WITHOUT_ANCHOR:", str(boundary.get("orientation_selected_without_anchor")).lower())
print("MANUSCRIPT_MUTATED:", str(boundary.get("manuscript_mutated")).lower())
print("PHYSICAL_CLAIM:", str(boundary.get("physical_claim")).lower())

if failed:
    raise SystemExit(1)
