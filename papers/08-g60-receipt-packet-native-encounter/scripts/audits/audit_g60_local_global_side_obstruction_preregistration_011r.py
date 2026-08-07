#!/usr/bin/env python3
import hashlib
import json
import subprocess
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
JSON_PATH = PROJECT / "artifacts/json/g60_local_global_side_obstruction_preregistration_011r.v1.json"
NOTE_PATH = PROJECT / "notes/g60_local_global_side_obstruction_preregistration_011r.md"

EXPECTED_JSON_HASH = "66156d68d525a45fa6e7800e3b6093f911306352080725e08249f25ffe69c59d"
EXPECTED_NOTE_HASH = "f7c7c149fa5a6cda4afa49acf021342a4e504ab1c8cecb3033476554c357a421"
LOCKED_HEAD = "7696ddb Lock G60 two-sided slider route witness"

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
known = data["known_marked_structures"]
predictions = data["predictions"]
withheld = data["claims_withheld"]
boundary = data["boundary"]
authorities = data["authorities"]
head = git("show", "-s", "--format=%h %s", "HEAD")

checks = [
    ("packet", data.get("packet") == "g60_local_global_side_obstruction_preregistration_011r"),
    ("mode", data.get("mode") == "post_two_sided_slider_marked_action_obstruction_preregistration"),
    ("status", data.get("status") == "frozen_before_marked_action_census"),
    ("head", data.get("locked_head") == LOCKED_HEAD and head == LOCKED_HEAD),
    ("json_hash", sha256_file(JSON_PATH) == EXPECTED_JSON_HASH),
    ("note_hash", sha256_file(NOTE_PATH) == EXPECTED_NOTE_HASH),
    ("authority_count", len(authorities) == 6),
    ("authority_hashes", all(row.get("hash_match") is True for row in authorities.values())),
    ("selected_D8", known.get("selected_011q_extension_type") == "D8"),
    ("selected_representatives_2", known.get("selected_011q_representative_count") == 2),
    ("selected_kernel_C2", known.get("selected_011q_central_kernel") == "C2"),
    ("selected_central_flip", known.get("selected_011q_central_flip") == [0, 1]),
    ("selected_signature", known.get("selected_011q_square_signature") == {"q(a)": 1, "q(b)": 0, "q(ab)": 0}),
    ("native_D8", known.get("native_local_group_type") == "D8"),
    ("native_order_8", known.get("native_local_group_order") == 8),
    ("native_center_2", known.get("native_local_center_order") == 2),
    ("native_axis_action", known.get("native_axis_action") == {"a": "a", "b": "ab", "ab": "b"}),
    ("native_indices", known.get("native_V4_indices") == {"1": 0, "a": 326, "b": 124, "ab": 65}),
    ("alpha_restriction", known.get("011o_alpha_1_restriction_to_native_V4") == {"1": 0, "a": 0, "b": 1, "ab": 1}),
    ("prediction_declared", predictions.get("prediction_declared_before_marked_action_census") is True),
    ("prediction_not_blind", predictions.get("prediction_blind") is False),
    ("predict_representatives_2", predictions.get("selected_cocycle_representative_count") == 2),
    ("predict_eight_each", predictions.get("isomorphism_count_per_representative") == 8),
    ("predict_total_16", predictions.get("total_isomorphism_count") == 16),
    ("predict_center_mapping", predictions.get("all_isomorphisms_map_local_center_to_native_a") is True),
    ("predict_local_delta_1", predictions.get("local_side_delta_under_central_flip") == 1),
    ("predict_global_delta_0", predictions.get("011o_sheet_delta_under_native_a") == 0),
    ("predict_identifications_0", predictions.get("direct_marked_side_identification_count") == 0),
    ("predict_same_obstruction", predictions.get("both_gauge_representatives_have_same_obstruction") is True),
    ("predict_classification", predictions.get("predicted_classification") == "native_center_kernel_obstructs_direct_side_identification"),
    ("predict_bridge_needed", predictions.get("intermediate_bridge_required_if_any_relation_exists") is True),
    ("required_test_count", len(data.get("required_tests", [])) == 16),
    ("outcome_count", len(data.get("outcome_order", [])) == 11),
    ("falsifier_count", len(data.get("falsifiers", [])) == 8),
    ("no_census_claim", withheld.get("complete_isomorphism_census_performed") is False),
    ("no_center_mapping_claim", withheld.get("center_mapping_verified_by_enumeration") is False),
    ("no_obstruction_claim", withheld.get("direct_side_identification_obstructed") is False),
    ("no_bridge", withheld.get("intermediate_bridge_constructed") is False),
    ("no_sheet_identity", withheld.get("local_side_identified_with_011o_orientation_sheet") is False),
    ("no_update_law", withheld.get("native_update_law_constructed") is False),
    ("no_mechanics_cell", withheld.get("mechanics_state_cell_established") is False),
    ("no_orientation", withheld.get("orientation_selected") is False),
    ("bounded_test", boundary.get("bounded_marked_D8_comparison_only") is True),
    ("broader_relation_open", boundary.get("broader_local_global_relation_ruled_out") is False),
    ("no_global_minimality", boundary.get("global_minimality_claim") is False),
    ("no_manuscript", boundary.get("manuscript_mutated") is False),
    ("no_geometry", boundary.get("geometry_claim") is False),
    ("no_physical_direction", boundary.get("physical_direction_claim") is False),
    ("no_physics", boundary.get("physical_claim") is False),
    ("note_exists", NOTE_PATH.is_file()),
]

failed = [name for name, passed in checks if not passed]

print("== G60 LOCAL/GLOBAL SIDE OBSTRUCTION PREREGISTRATION AUDIT 011r ==")
print("PACKET:", data.get("packet"))
print("MODE:", data.get("mode"))
print("JSON_SHA256:", sha256_file(JSON_PATH))
print("NOTE_SHA256:", sha256_file(NOTE_PATH))
print("LOCKED_HEAD:", data.get("locked_head"))
print("NATIVE_V4_INDICES:", known.get("native_V4_indices"))
print("ALPHA_1_RESTRICTION:", known.get("011o_alpha_1_restriction_to_native_V4"))
print("PREDICTED_ISOMORPHISM_COUNT_PER_REPRESENTATIVE:", predictions.get("isomorphism_count_per_representative"))
print("PREDICTED_TOTAL_ISOMORPHISM_COUNT:", predictions.get("total_isomorphism_count"))
print("PREDICTED_DIRECT_MARKED_SIDE_IDENTIFICATION_COUNT:", predictions.get("direct_marked_side_identification_count"))
print("PREDICTED_CLASSIFICATION:", predictions.get("predicted_classification"))
print("MARKED_ACTION_CENSUS_PERFORMED: false")
print("CHECK_COUNT:", len(checks))
print("FAILED_CHECK_COUNT:", len(failed))

for name, passed in checks:
    print("CHECK", name + ":", str(bool(passed)).lower())

print("PREREGISTRATION_PASS:", str(not failed).lower())
print("FAILED_CHECKS:", failed)
print("DIRECT_SIDE_IDENTIFICATION_OBSTRUCTED: false")
print("LOCAL_SIDE_EQUALS_011O_ORIENTATION_SHEET: false")
print("INTERMEDIATE_BRIDGE_CONSTRUCTED: false")
print("MANUSCRIPT_MUTATED: false")
print("PHYSICAL_CLAIM: false")

if failed:
    raise SystemExit(1)
