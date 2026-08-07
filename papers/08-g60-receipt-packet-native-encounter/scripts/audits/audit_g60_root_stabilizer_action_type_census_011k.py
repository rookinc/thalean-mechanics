#!/usr/bin/env python3

import hashlib
import json
import subprocess
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
JSON_PATH = PROJECT / "artifacts/json/g60_root_stabilizer_action_type_census_011k.v1.json"
RAW_PATH = PROJECT / "artifacts/receipts/g60_root_stabilizer_action_type_census_011k_raw_run.txt"
NOTE_PATH = PROJECT / "notes/g60_root_stabilizer_action_type_census_011k.md"
COMPUTE_PATH = PROJECT / "scripts/audits/compute_g60_root_stabilizer_action_type_census_011k.py"

EXPECTED_JSON_HASH = "6685932b584a9784410ed57eabe7cfab27de43365ac74bc844c166f375b31574"
EXPECTED_RAW_HASH = "087bf2aed6bbf869d32f497a1c8c94120a313bfdf08dd80d94908eacd9239ffd"
EXPECTED_NOTE_HASH = "4f0c002e51f4a7f0e9a4f4252ac6320eb823dfaf09d18a332cf51ca977d6dc65"
EXPECTED_COMPUTE_HASH = "df5f1fa8de373033bd7cf6bee5489f04844440cc592b11cc630ca9abe913877c"
EXPECTED_CANDIDATE_HASH = "f361ff1f1a91950677a5ef441ea2feece43b165635376756219e675b371907ef"

def sha256_file(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
group = data["group_reconstruction"]
profiles = data["uniform_profiles"]
census = data["stabilizer_census"]
comparison = data["exact_even_duad_comparison"]
boundary = data["boundary"]
promotion = data["promotion"]
provenance = data["candidate_provenance"]

root_profile = {
    "cycle_type_profile": {
        "1,1,1,1,1": 1,
        "2,2,1": 3,
        "3,1,1": 2,
    },
    "element_order_profile": {"1": 1, "2": 3, "3": 2},
    "orbit_size_profile": [2, 3],
    "order": 6,
    "parity_profile": {"even": 6},
}

ordered_profile = {
    "cycle_type_profile": {
        "1,1,1,1,1": 1,
        "2,1,1,1": 3,
        "3,1,1": 2,
    },
    "element_order_profile": {"1": 1, "2": 3, "3": 2},
    "orbit_size_profile": [1, 1, 3],
    "order": 6,
    "parity_profile": {"even": 3, "odd": 3},
}

head = subprocess.run(
    ["git", "--no-pager", "show", "-s", "--format=%h %s", "HEAD"],
    cwd=PROJECT,
    check=True,
    capture_output=True,
    text=True,
).stdout.strip()

checks = [
    ("packet", data.get("packet") == "g60_root_stabilizer_action_type_census_011k"),
    ("mode_frozen", data.get("mode") == "frozen_complete_stabilizer_action_type_census"),
    ("locked_head_recorded", data.get("locked_head") == "ea06a19 Preregister G60 root stabilizer action type"),
    ("head_still_locked", head == "ea06a19 Preregister G60 root stabilizer action type"),
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
    ("authority_count", len(data.get("authorities", {})) == 5),
    ("authority_hashes", all(x.get("hash_match") is True for x in data.get("authorities", {}).values())),
    ("group_order_480", group.get("group_order") == 480),
    ("identity_0", group.get("identity_index") == 0),
    ("closure_zero", group.get("closure_failure_count") == 0),
    ("inverse_zero", group.get("inverse_failure_count") == 0),
    ("operation_ok", group.get("operation_ok") is True),
    ("five_point_image_120", group.get("five_point_image_order") == 120),
    ("root_uniform", profiles.get("root_profile_uniform") is True),
    ("ordered_uniform", profiles.get("ordered_duad_profile_uniform") is True),
    ("even_duad_uniform", profiles.get("even_duad_profile_uniform") is True),
    ("root_profile_exact", profiles.get("root_profile") == root_profile),
    ("ordered_profile_exact", profiles.get("ordered_duad_profile") == ordered_profile),
    ("even_profile_equals_root", profiles.get("even_duad_profile") == root_profile),
    ("same_abstract_profile", profiles.get("same_abstract_element_order_profile") is True),
    ("not_conjugate_in_S5", profiles.get("root_and_ordered_stabilizers_conjugate_in_S5") is False),
    ("N_root_rows_20", census.get("N_root_row_count") == 20 and len(census.get("N_root_rows", [])) == 20),
    ("N_ordered_rows_20", census.get("N_ordered_duad_row_count") == 20 and len(census.get("N_ordered_rows", [])) == 20),
    ("complement_root_rows_40", census.get("complement_root_row_count") == 40 and len(census.get("complement_root_rows", [])) == 40),
    ("complement_ordered_rows_40", census.get("complement_ordered_duad_row_count") == 40 and len(census.get("complement_ordered_rows", [])) == 40),
    ("even_duad_rows_10", len(census.get("even_duad_rows", [])) == 10),
    ("distinct_N_root_10", census.get("distinct_N_root_image_count") == 10),
    ("distinct_N_ordered_10", census.get("distinct_N_ordered_image_count") == 10),
    ("distinct_complement_root_10", census.get("distinct_complement_root_image_count") == 10),
    ("distinct_complement_ordered_10", census.get("distinct_complement_ordered_image_count") == 10),
    ("distinct_even_duad_10", census.get("distinct_even_duad_image_count") == 10),
    ("N_match_failures_zero", comparison.get("N_exact_match_failure_count") == 0),
    ("N_failure_rows_empty", comparison.get("N_exact_match_failures") == []),
    ("complement_match_failures_zero", comparison.get("complement_exact_match_failure_count") == 0),
    ("complement_failure_rows_empty", comparison.get("complement_exact_match_failures") == []),
    ("N_family_exact", comparison.get("N_root_image_family_equals_even_duad_family") is True),
    ("complement_family_exact", comparison.get("complement_root_image_family_equals_even_duad_family") is True),
    ("exact_even_match", comparison.get("exact_even_match") is True),
    ("prediction_matches", data.get("prediction_matches") is True),
    ("classification", data.get("classification") == "root_stabilizer_exactly_matches_even_duad_setwise_stabilizer"),
    ("classification_only", boundary.get("classification_only") is True),
    ("no_replacement_A_set", boundary.get("replacement_source_A_set_constructed") is False),
    ("no_new_selector", boundary.get("new_selector_searched") is False),
    ("no_minimal_datum", boundary.get("minimal_directional_datum_identified") is False),
    ("no_orientation", boundary.get("orientation_selected") is False),
    ("no_manuscript", boundary.get("manuscript_mutated") is False),
    ("no_geometry", boundary.get("geometry_claim") is False),
    ("no_physics", boundary.get("physical_claim") is False),
    ("promotion_no_manuscript", promotion.get("manuscript_mutated") is False),
    ("note_exists", NOTE_PATH.is_file()),
]

failed = [name for name, passed in checks if not passed]

print("== G60 ROOT STABILIZER ACTION-TYPE CENSUS AUDIT 011k ==")
print("PACKET:", data.get("packet"))
print("MODE:", data.get("mode"))
print("JSON_SHA256:", sha256_file(JSON_PATH))
print("NOTE_SHA256:", sha256_file(NOTE_PATH))
print("COMPUTATION_SCRIPT_SHA256:", sha256_file(COMPUTE_PATH))
print("RAW_RUN_RECEIPT_SHA256:", sha256_file(RAW_PATH))
print("ROOT_STABILIZER_PROFILE:", profiles.get("root_profile"))
print("ORDERED_DUAD_STABILIZER_PROFILE:", profiles.get("ordered_duad_profile"))
print("EVEN_DUAD_STABILIZER_PROFILE:", profiles.get("even_duad_profile"))
print("ROOT_AND_ORDERED_CONJUGATE_IN_S5:", str(profiles.get("root_and_ordered_stabilizers_conjugate_in_S5")).lower())
print("N_EXACT_MATCH_FAILURE_COUNT:", comparison.get("N_exact_match_failure_count"))
print("COMPLEMENT_EXACT_MATCH_FAILURE_COUNT:", comparison.get("complement_exact_match_failure_count"))
print("CLASSIFICATION:", data.get("classification"))
print("CHECK_COUNT:", len(checks))
print("FAILED_CHECK_COUNT:", len(failed))

for name, passed in checks:
    print(f"CHECK {name}: {str(passed).lower()}")

print("AUDIT_PASS:", str(not failed).lower())
print("FAILED_CHECKS:", failed)
print("EARNED_STATEMENT:", data.get("earned_statement"))
print("REPLACEMENT_SOURCE_A_SET_CONSTRUCTED:", str(boundary.get("replacement_source_A_set_constructed")).lower())
print("ORIENTATION_SELECTED:", str(boundary.get("orientation_selected")).lower())
print("MANUSCRIPT_MUTATED:", str(boundary.get("manuscript_mutated")).lower())
print("PHYSICAL_CLAIM:", str(boundary.get("physical_claim")).lower())

if failed:
    raise SystemExit(1)
