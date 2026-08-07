#!/usr/bin/env python3
import hashlib
import json
import subprocess
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
JSON_PATH = PROJECT / "artifacts/json/g60_local_global_side_obstruction_census_011s.v1.json"
RAW_PATH = PROJECT / "artifacts/receipts/g60_local_global_side_obstruction_census_011s_raw_run.txt"
NOTE_PATH = PROJECT / "notes/g60_local_global_side_obstruction_census_011s.md"
COMPUTE_PATH = PROJECT / "scripts/audits/compute_g60_local_global_side_obstruction_census_011s.py"

EXPECTED_JSON_HASH = "d50e3a7d83e9bff2a1dc7c97516e3c7c670528f34b704cf58a9d3f05e40d95b0"
EXPECTED_RAW_HASH = "4f998141d0dd973fce233d234a5dce04728be29a645aac281da153eb2410e2f7"
EXPECTED_NOTE_HASH = "1e031d6be32e830d2d9f829ab13e471fdc613be8c07413a52bc9dd7ff273938e"
EXPECTED_COMPUTE_HASH = "d4b5e9d988405f63e51916cde168e78eb8d1f4364b3d0b0d4945ae830921e00e"
EXPECTED_CANDIDATE_HASH = "968268859ed369da18d103e3e1986d2ad0c6b36ccc308a017de2cdfe63ff56a9"
LOCKED_HEAD = "1aaaadf Preregister G60 local-global side obstruction test"
EXPECTED_CLASSIFICATION = "native_center_kernel_obstructs_direct_side_identification"

EXPECTED_REPRESENTATIVE_HASHES = [
    "45f386719813421e4d395b88a498b4982201d7af5e4b761fe1d6baeef10fef63",
    "0bca8a34381bf7990bccc78994be5f491b9630513a054d24fcf598d7260fc78a",
]
EXPECTED_DIFFERENCE = [0, 1, 1, 1, 0, 1, 1, 1, 0]

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
indices = data["native_index_identification"]
native = data["native_D8"]
selected = data["selected_extensions"]
comparison = data["marked_action_comparison"]
boundary = data["boundary"]
repository = data["repository"]
authorities = data["authorities"]
promotion = data["promotion"]
provenance = data["candidate_provenance"]

representatives = selected.get("representative_rows", [])
head = git("show", "-s", "--format=%h %s", "HEAD")

checks = [
    ("packet", data.get("packet") == "g60_local_global_side_obstruction_census_011s"),
    ("mode", data.get("mode") == "frozen_complete_marked_action_census"),
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
    ("label_failure_preserved", promotion.get("native_square_label_failure_preserved") is True),
    ("label_failure_not_promoted", promotion.get("native_square_label_failure_promoted") is False),
    ("guard_failure_preserved", promotion.get("classifier_guard_failure_preserved") is True),
    ("guard_failure_not_promoted", promotion.get("classifier_guard_failure_promoted") is False),
    ("promotion_no_manuscript", promotion.get("manuscript_mutated") is False),
    ("failed_label_script_hash", provenance.get("failed_native_square_label_script_sha256") == "572498a4d35d5d1989e350a42656a78ff93ba9f611ffc7cd1e72328946b2885d"),
    ("failed_label_json_hash", provenance.get("failed_native_square_label_json_sha256") == "743da70de7691c90c1ec1da1656e29cf9ee490fa2796aeb001defa5720ac25bd"),
    ("failed_label_report_hash", provenance.get("failed_native_square_label_report_sha256") == "db3efe13d30457fa863ba40e8fb5bc90be9edd4b4c151555f2b7c60bfaa19b30"),
    ("failed_guard_script_hash", provenance.get("failed_classifier_guard_script_sha256") == "27acee2d3afbc038e3ac431a328ced75aa154cc3e0c16a17ba8b3a99ec52d1ea"),
    ("failed_guard_json_hash", provenance.get("failed_classifier_guard_json_sha256") == "449302395d63834d2b6d1a9c0f425a1b4f5a4c8c8e420d4fbdf5b717ba6e00d2"),
    ("failed_guard_report_hash", provenance.get("failed_classifier_guard_report_sha256") == "6a7c9320a66ff752a1c900ad5b1c6c282433fff181027cccb123082dc9e76791"),
    ("authority_count", len(authorities) == 7),
    ("authority_hashes", all(row.get("hash_match") is True for row in authorities.values())),
    ("native_indices", indices.get("native_V4_indices") == {"1": 0, "a": 326, "b": 124, "ab": 65}),
    ("expected_native_indices", indices.get("expected_native_V4_indices") == {"1": 0, "a": 326, "b": 124, "ab": 65}),
    ("index_identification_ok", indices.get("index_identification_ok") is True),
    ("alpha_restriction", indices.get("011o_alpha_1_restriction") == {"1": 0, "a": 0, "b": 1, "ab": 1}),
    ("expected_alpha_restriction", indices.get("expected_011o_alpha_1_restriction") == {"1": 0, "a": 0, "b": 1, "ab": 1}),
    ("alpha_restriction_ok", indices.get("alpha_restriction_ok") is True),
    ("native_group_D8", native.get("group_profile", {}).get("group_type") == "D8"),
    ("native_group_order_8", native.get("group_profile", {}).get("order") == 8),
    ("native_identity_0", native.get("group_profile", {}).get("identity_index") == 0),
    ("native_center_indices", native.get("group_profile", {}).get("center_indices") == [0, 7]),
    ("native_center_order_2", native.get("group_profile", {}).get("center_order") == 2),
    ("native_order_profile", native.get("group_profile", {}).get("element_order_profile") == {"1": 1, "2": 5, "4": 2}),
    ("native_closure_zero", native.get("closure_failure_count") == 0),
    ("native_named_indices", native.get("named_group_indices") == {"1": 0, "a": 7, "b": 2, "ab": 5}),
    ("native_a_index_7", native.get("native_a_group_index") == 7),
    ("native_nonidentity_center", native.get("nonidentity_center_indices") == [7]),
    ("native_center_is_a", native.get("native_center_is_a") is True),
    ("representative_count_2", selected.get("representative_count") == 2 and len(representatives) == 2),
    ("representative_hashes", [row.get("cocycle_sha256") for row in representatives] == EXPECTED_REPRESENTATIVE_HASHES),
    ("representatives_gauge_related", selected.get("representatives_gauge_related") is True),
    ("representative_difference", selected.get("representative_difference") == EXPECTED_DIFFERENCE),
    ("local_groups_D8", all(row.get("local_group_profile", {}).get("group_type") == "D8" for row in representatives)),
    ("local_group_orders_8", all(row.get("local_group_profile", {}).get("order") == 8 for row in representatives)),
    ("local_centers_2", all(row.get("local_group_profile", {}).get("center_order") == 2 for row in representatives)),
    ("local_operations_valid", all(
        row.get("local_group_profile", {}).get("element_order_profile") == {"1": 1, "2": 5, "4": 2}
        for row in representatives
    )),
    ("local_central_flip_index_1", all(row.get("local_central_flip_index") == 1 for row in representatives)),
    ("local_side_delta_each", all(row.get("local_side_delta_profile") == {"1": 8} for row in representatives)),
    ("eight_isomorphisms_each", [row.get("isomorphism_count") for row in representatives] == [8, 8]),
    ("eight_isomorphism_rows_each", all(len(row.get("isomorphism_rows", [])) == 8 for row in representatives)),
    ("representative_center_maps", all(row.get("all_isomorphisms_map_center_to_native_a") is True for row in representatives)),
    ("representative_direct_counts_zero", all(row.get("direct_marked_side_identification_count") == 0 for row in representatives)),
    ("all_isomorphism_center_names_a", all(
        iso.get("native_center_image_name") == "a"
        for row in representatives
        for iso in row.get("isomorphism_rows", [])
    )),
    ("all_isomorphism_local_delta_1", all(
        iso.get("local_side_delta") == 1
        for row in representatives
        for iso in row.get("isomorphism_rows", [])
    )),
    ("all_isomorphism_global_delta_0", all(
        iso.get("011o_sheet_delta") == 0
        for row in representatives
        for iso in row.get("isomorphism_rows", [])
    )),
    ("no_compatible_isomorphism_rows", all(
        iso.get("direct_marked_side_compatible") is False
        for row in representatives
        for iso in row.get("isomorphism_rows", [])
    )),
    ("isomorphism_counts", comparison.get("isomorphism_count_per_representative") == [8, 8]),
    ("total_isomorphisms_16", comparison.get("total_isomorphism_count") == 16),
    ("center_mapping_failures_zero", comparison.get("center_mapping_failure_count") == 0),
    ("all_centers_map_a", comparison.get("all_isomorphisms_map_local_center_to_native_a") is True),
    ("local_delta_profile", comparison.get("local_side_delta_profile") == {"1": 16}),
    ("global_delta_profile", comparison.get("011o_sheet_delta_profile") == {"0": 16}),
    ("local_center_flips", comparison.get("local_center_flips_side") is True),
    ("native_center_preserves_sheet", comparison.get("native_center_preserves_011o_sheet") is True),
    ("direct_identifications_zero", comparison.get("direct_marked_side_identification_count") == 0),
    ("direct_obstruction", comparison.get("direct_side_identification_obstructed") is True),
    ("classification", data.get("classification") == EXPECTED_CLASSIFICATION),
    ("prediction_matches", data.get("prediction_matches") is True),
    ("bounded_comparison", boundary.get("bounded_marked_D8_comparison_complete") is True),
    ("boundary_obstruction", boundary.get("direct_side_identification_obstructed") is True),
    ("no_sheet_identity", boundary.get("local_side_equals_011o_orientation_sheet") is False),
    ("no_bridge", boundary.get("intermediate_bridge_constructed") is False),
    ("broader_relation_open", boundary.get("broader_local_global_relation_ruled_out") is False),
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
    ("earned_statement_present", isinstance(data.get("earned_statement"), str) and len(data["earned_statement"]) > 200),
    ("note_exists", NOTE_PATH.is_file()),
]

failed = [name for name, passed in checks if not passed]

print("== G60 LOCAL/GLOBAL SIDE OBSTRUCTION CENSUS AUDIT 011s ==")
print("PACKET:", data.get("packet"))
print("MODE:", data.get("mode"))
print("JSON_SHA256:", sha256_file(JSON_PATH))
print("NOTE_SHA256:", sha256_file(NOTE_PATH))
print("COMPUTATION_SCRIPT_SHA256:", sha256_file(COMPUTE_PATH))
print("RAW_RUN_RECEIPT_SHA256:", sha256_file(RAW_PATH))
print("NATIVE_V4_INDICES:", indices.get("native_V4_indices"))
print("ALPHA_1_RESTRICTION:", indices.get("011o_alpha_1_restriction"))
print("NATIVE_GROUP_PROFILE:", native.get("group_profile"))
print("ISOMORPHISM_COUNTS:", comparison.get("isomorphism_count_per_representative"))
print("TOTAL_ISOMORPHISM_COUNT:", comparison.get("total_isomorphism_count"))
print("LOCAL_SIDE_DELTA_PROFILE:", comparison.get("local_side_delta_profile"))
print("011O_SHEET_DELTA_PROFILE:", comparison.get("011o_sheet_delta_profile"))
print("DIRECT_MARKED_SIDE_IDENTIFICATION_COUNT:", comparison.get("direct_marked_side_identification_count"))
print("CLASSIFICATION:", data.get("classification"))
print("CHECK_COUNT:", len(checks))
print("FAILED_CHECK_COUNT:", len(failed))

for name, passed in checks:
    print("CHECK", name + ":", str(bool(passed)).lower())

print("AUDIT_PASS:", str(not failed).lower())
print("FAILED_CHECKS:", failed)
print("EARNED_STATEMENT:", data.get("earned_statement"))
print("DIRECT_SIDE_IDENTIFICATION_OBSTRUCTED:", str(boundary.get("direct_side_identification_obstructed")).lower())
print("LOCAL_SIDE_EQUALS_011O_ORIENTATION_SHEET:", str(boundary.get("local_side_equals_011o_orientation_sheet")).lower())
print("INTERMEDIATE_BRIDGE_CONSTRUCTED:", str(boundary.get("intermediate_bridge_constructed")).lower())
print("MECHANICS_STATE_CELL_ESTABLISHED:", str(boundary.get("mechanics_state_cell_established")).lower())
print("MANUSCRIPT_MUTATED:", str(boundary.get("manuscript_mutated")).lower())
print("PHYSICAL_CLAIM:", str(boundary.get("physical_claim")).lower())

if failed:
    raise SystemExit(1)
