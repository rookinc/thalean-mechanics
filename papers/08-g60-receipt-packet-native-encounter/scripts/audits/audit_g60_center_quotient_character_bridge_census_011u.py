#!/usr/bin/env python3
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
JSON_PATH = PROJECT / "artifacts/json/g60_center_quotient_character_bridge_census_011u.v1.json"
RAW_PATH = PROJECT / "artifacts/receipts/g60_center_quotient_character_bridge_census_011u_raw_run.txt"
NOTE_PATH = PROJECT / "notes/g60_center_quotient_character_bridge_census_011u.md"
COMPUTE_PATH = PROJECT / "scripts/audits/compute_g60_center_quotient_character_bridge_census_011u.py"

EXPECTED_JSON_HASH = "9d5163f4c56ed1309a73902b8327e7747adcfa1cbef1566838af56c2768f90a7"
EXPECTED_RAW_HASH = "4a5011e882a370fc9e24ad282d906e67d1147f0f3381b251c051aff30e5b6041"
EXPECTED_NOTE_HASH = "da1d0f55120fa0bedb3f2b2f95feb3dc71f7858a5b31153ac8abb4300ebe6a63"
EXPECTED_COMPUTE_HASH = "23ff65af37e14cff328dcf6014c72b5ffd0e39bdeb0a917d6f152fefe079bd69"
EXPECTED_CANDIDATE_HASH = "a0b18041c7ee12d8c1e3474c78f1d14c8d85cb26dc751b9c583ad8e42149f5b8"
EXPECTED_GUARD_HASH = "6c8402a49fbd6eda60f7ac93992b6b6f881d952e5283bc0521446a9456ab5ee9"
EXPECTED_FAILED_SCRIPT_HASH = "15cf149db20bd5f8ed8bc78cc72dbd44967cc32948811313b8c9ccee2cc84d7e"
EXPECTED_FAILED_JSON_HASH = "71df35a76482007b39b3868bbd6717157e0c4cdac9c5abb3382f722fc9b64bac"
EXPECTED_FAILED_REPORT_HASH = "f3a52520eeb998b03b69a3d42369b629d47eba6c196e2fc16f3aeedbcf3c4e3c"
EXPECTED_ALPHA_1_HASH = "3d057f3e36004b4c59aa2754220cf4987587bf0e58ea3492e88f88a31515f39c"
EXPECTED_N_HASH = "f6a65aae2e49825862966b14b59df5a648114838213651b418b1022c25564f70"
LOCKED_HEAD = "9aafeab Preregister G60 center-quotient character bridge"

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
subgroups = data["native_D8_subgroup_census"]
presentations = data["local_presentations"]
comparisons = data["marked_comparison_census"]
bridge = data["center_quotient_character_bridge"]
prediction = data["prediction_comparison"]
promotion = data["promotion"]
provenance = data["candidate_provenance"]
excluded = data["excluded_wrong_character_run"]
alpha_validation = data["alpha_1_validation"]
boundary = data["boundary"]
repository = data["repository"]
rows = comparisons["comparison_rows"]

head = git("show", "-s", "--format=%h %s", "HEAD")

character_profile = Counter(
    tuple(
        row["quotient_character"][name]
        for name in ("1", "a", "b", "ab")
    )
    for row in rows
)
kernel_profile = Counter(
    (
        tuple(row["quotient_kernel"]),
        row["kernel_group_type"],
        tuple(sorted(row["kernel_element_order_profile"].items())),
    )
    for row in rows
)

checks = [
    ("packet", data.get("packet") == "g60_center_quotient_character_bridge_census_011u"),
    ("mode", data.get("mode") == "frozen_complete_center_quotient_character_bridge_census"),
    ("locked_head", data.get("locked_head") == LOCKED_HEAD and head == LOCKED_HEAD),
    ("result_frozen", data.get("result_frozen") is True),
    ("audit_pass_recorded", data.get("audit_pass") is True),
    ("json_hash", sha256_file(JSON_PATH) == EXPECTED_JSON_HASH),
    ("raw_hash", sha256_file(RAW_PATH) == EXPECTED_RAW_HASH),
    ("note_hash", sha256_file(NOTE_PATH) == EXPECTED_NOTE_HASH),
    ("compute_hash", sha256_file(COMPUTE_PATH) == EXPECTED_COMPUTE_HASH),
    ("candidate_hash", provenance.get("candidate_json_sha256") == EXPECTED_CANDIDATE_HASH),
    ("guard_hash", provenance.get("promotion_guard_sha256") == EXPECTED_GUARD_HASH),
    ("candidate_promoted", promotion.get("candidate_promoted_without_recomputation") is True),
    ("raw_copied", promotion.get("raw_run_receipt_copied_byte_for_byte") is True),
    ("compute_copied", promotion.get("computation_script_copied_byte_for_byte") is True),
    ("wrong_run_preserved", promotion.get("wrong_character_run_preserved") is True),
    ("wrong_run_not_promoted", promotion.get("wrong_character_run_promoted") is False),
    ("alpha_correction", promotion.get("alpha_1_character_correction_applied") is True),
    ("promotion_no_manuscript", promotion.get("manuscript_mutated") is False),
    ("failed_script_hash", excluded.get("script_sha256") == EXPECTED_FAILED_SCRIPT_HASH),
    ("failed_json_hash", excluded.get("candidate_json_sha256") == EXPECTED_FAILED_JSON_HASH),
    ("failed_report_hash", excluded.get("raw_report_sha256") == EXPECTED_FAILED_REPORT_HASH),
    ("failed_not_promoted", excluded.get("promoted") is False),
    ("failed_wrong_character", excluded.get("classification") == "quotient_character_not_unique_or_mismatch"),
    ("alpha_formula", alpha_validation.get("reference_formula") == "d8_flip"),
    ("alpha_hash", alpha_validation.get("reconstructed_sha256") == EXPECTED_ALPHA_1_HASH),
    ("alpha_locked_hash", alpha_validation.get("locked_011o_sha256") == EXPECTED_ALPHA_1_HASH),
    ("alpha_hash_match", alpha_validation.get("hash_match") is True),
    ("wrong_formula", alpha_validation.get("wrong_formula") == "p xor d8_flip"),
    ("wrong_reconstructs_n", alpha_validation.get("wrong_formula_reconstructs") == "n"),
    ("n_hash", alpha_validation.get("locked_n_sha256") == EXPECTED_N_HASH),
    ("authority_count", len(data.get("authorities", {})) == 8),
    ("authority_hashes", all(row.get("hash_match") is True for row in data["authorities"].values())),
    ("group_480", group.get("group_order") == 480),
    ("identity_0", group.get("identity_index") == 0),
    ("native_indices", group.get("native_v4_indices") == {"1": 0, "a": 326, "ab": 65, "b": 124}),
    ("native_index_ok", group.get("native_index_identification_ok") is True),
    ("alpha_restriction", group.get("alpha_1_restriction") == {"1": 0, "a": 0, "ab": 1, "b": 1}),
    ("expected_alpha", group.get("expected_alpha_1_restriction") == {"1": 0, "a": 0, "ab": 1, "b": 1}),
    ("transpositions_10", group.get("transposition_count") == 10),
    ("lifts_40", group.get("transposition_lift_count") == 40),
    ("subgroups_10", subgroups.get("subgroup_count") == 10),
    ("subgroup_rows_10", len(subgroups.get("subgroup_rows", [])) == 10),
    ("transposition_rows_10", len(subgroups.get("transposition_rows", [])) == 10),
    ("all_subgroups_D8", subgroups.get("all_subgroups_D8") is True),
    ("all_subgroups_center_a", subgroups.get("all_subgroups_centered_on_native_a") is True),
    ("each_subgroup_D8", all(row["profile"]["group_type"] == "D8" for row in subgroups["subgroup_rows"])),
    ("each_subgroup_order_8", all(row["profile"]["order"] == 8 for row in subgroups["subgroup_rows"])),
    ("each_subgroup_center_2", all(row["profile"]["center_order"] == 2 for row in subgroups["subgroup_rows"])),
    ("each_subgroup_center_a", all(row["native_center_is_a"] is True for row in subgroups["subgroup_rows"])),
    ("each_subgroup_four_lifts", all(row["lift_count"] == 4 for row in subgroups["subgroup_rows"])),
    ("each_transposition_four_lifts", all(row["lift_count"] == 4 for row in subgroups["transposition_rows"])),
    ("presentations_2", presentations.get("presentation_count") == 2),
    ("presentation_rows_2", len(presentations.get("presentation_rows", [])) == 2),
    ("presentations_D8", all(row["profile"]["group_type"] == "D8" for row in presentations["presentation_rows"])),
    ("presentations_signature", all(row["square_signature"] == {"a": 1, "ab": 0, "b": 0} for row in presentations["presentation_rows"])),
    ("presentations_gauge_related", presentations.get("representatives_gauge_related") is True),
    ("pairs_20", comparisons.get("presentation_subgroup_pair_count") == 20),
    ("pair_rows_20", len(comparisons.get("pair_rows", [])) == 20),
    ("eight_each", comparisons.get("all_eight_isomorphisms_per_pair") is True),
    ("pair_counts_eight", all(row["isomorphism_count"] == 8 and row["comparison_count"] == 8 for row in comparisons["pair_rows"])),
    ("isomorphisms_160", comparisons.get("total_isomorphism_count") == 160),
    ("comparisons_160", comparisons.get("comparison_count") == 160 and len(rows) == 160),
    ("centers_map_a", comparisons.get("all_centers_map_to_native_a") is True),
    ("centers_killed", comparisons.get("all_centers_killed_by_alpha_1") is True),
    ("homomorphisms", comparisons.get("all_pulled_characters_are_homomorphisms") is True),
    ("row_center_a", all(row["local_center_image_name"] == "a" and row["local_center_image_index"] == 326 for row in rows)),
    ("row_center_killed", all(row["center_killed_by_alpha_1"] is True for row in rows)),
    ("row_descends", all(row["descends_to_visible_V4"] is True and row["descent_failure_count"] == 0 for row in rows)),
    ("row_homomorphism", all(row["homomorphism_failure_count"] == 0 for row in rows)),
    ("character_profile", character_profile == {(0, 0, 1, 1): 160}),
    ("kernel_profile", kernel_profile == {(("1", "a"), "C4", (("1", 1), ("2", 1), ("4", 2))): 160}),
    ("all_descend", bridge.get("all_characters_descend") is True),
    ("unique_character_count_1", bridge.get("unique_quotient_character_count") == 1),
    ("unique_character", bridge.get("unique_quotient_characters") == [{"1": 0, "a": 0, "ab": 1, "b": 1}]),
    ("expected_character", bridge.get("expected_unique_character") == {"1": 0, "a": 0, "ab": 1, "b": 1}),
    ("all_match_expected", bridge.get("all_match_expected_character") is True),
    ("kernel_axis", bridge.get("quotient_kernel") == ["1", "a"]),
    ("all_kernel_axis", bridge.get("all_kernels_equal_q_distinguished_axis") is True),
    ("kernel_type_C4", bridge.get("pulled_back_kernel_group_type") == "C4"),
    ("all_kernel_C4", bridge.get("all_pulled_back_kernels_are_C4") is True),
    ("gauge_agreement", bridge.get("gauge_representatives_agree") is True),
    ("quotient_forgets_side", bridge.get("quotient_forgets_local_central_side") is True),
    ("obstruction_not_reversed", bridge.get("direct_side_obstruction_reversed") is False),
    ("prediction_matches", prediction.get("prediction_matches") is True),
    ("classification", data.get("classification") == "unique_center_quotient_character_bridge"),
    ("bridge_constructed", boundary.get("center_quotient_character_bridge_constructed") is True),
    ("bounded_comparison", boundary.get("bounded_center_quotient_comparison") is True),
    ("obstruction_preserved", boundary.get("direct_side_identification_obstruction_preserved") is True),
    ("no_side_identity", boundary.get("local_side_equals_011o_orientation_sheet") is False),
    ("no_update_law", boundary.get("native_update_law_constructed") is False),
    ("no_mechanics_cell", boundary.get("mechanics_state_cell_established") is False),
    ("no_orientation", boundary.get("orientation_selected") is False),
    ("no_global_minimality", boundary.get("global_minimality_claim") is False),
    ("no_manuscript", boundary.get("manuscript_mutated") is False),
    ("no_geometry", boundary.get("geometry_claim") is False),
    ("no_physical_direction", boundary.get("physical_direction_claim") is False),
    ("no_physics", boundary.get("physical_claim") is False),
    ("repository_preserved", repository.get("status_preserved") is True),
    ("candidate_no_project_mutation", repository.get("project_mutation_performed") is False),
    ("earned_statement", isinstance(data.get("earned_statement"), str) and len(data["earned_statement"]) > 200),
    ("note_exists", NOTE_PATH.is_file()),
]

failed = [name for name, passed in checks if not passed]

print("== G60 CENTER-QUOTIENT CHARACTER BRIDGE CENSUS AUDIT 011u ==")
print("PACKET:", data.get("packet"))
print("MODE:", data.get("mode"))
print("JSON_SHA256:", sha256_file(JSON_PATH))
print("NOTE_SHA256:", sha256_file(NOTE_PATH))
print("COMPUTATION_SCRIPT_SHA256:", sha256_file(COMPUTE_PATH))
print("RAW_RUN_RECEIPT_SHA256:", sha256_file(RAW_PATH))
print("RECONSTRUCTED_ALPHA_1_SHA256:", alpha_validation.get("reconstructed_sha256"))
print("NATIVE_D8_SUBGROUP_COUNT:", subgroups.get("subgroup_count"))
print("TOTAL_ISOMORPHISM_COUNT:", comparisons.get("total_isomorphism_count"))
print("TOTAL_COMPARISON_COUNT:", comparisons.get("comparison_count"))
print("UNIQUE_QUOTIENT_CHARACTERS:", bridge.get("unique_quotient_characters"))
print("QUOTIENT_KERNEL:", bridge.get("quotient_kernel"))
print("PULLED_BACK_KERNEL_GROUP_TYPE:", bridge.get("pulled_back_kernel_group_type"))
print("CLASSIFICATION:", data.get("classification"))
print("CHECK_COUNT:", len(checks))
print("FAILED_CHECK_COUNT:", len(failed))

for name, passed in checks:
    print("CHECK", name + ":", str(bool(passed)).lower())

print("AUDIT_PASS:", str(not failed).lower())
print("FAILED_CHECKS:", failed)
print("EARNED_STATEMENT:", data.get("earned_statement"))
print("CENTER_QUOTIENT_CHARACTER_BRIDGE_CONSTRUCTED:", str(boundary.get("center_quotient_character_bridge_constructed")).lower())
print("LOCAL_SIDE_EQUALS_011O_ORIENTATION_SHEET:", str(boundary.get("local_side_equals_011o_orientation_sheet")).lower())
print("NATIVE_UPDATE_LAW_CONSTRUCTED:", str(boundary.get("native_update_law_constructed")).lower())
print("MECHANICS_STATE_CELL_ESTABLISHED:", str(boundary.get("mechanics_state_cell_established")).lower())
print("MANUSCRIPT_MUTATED:", str(boundary.get("manuscript_mutated")).lower())
print("PHYSICAL_CLAIM:", str(boundary.get("physical_claim")).lower())

if failed:
    raise SystemExit(1)
