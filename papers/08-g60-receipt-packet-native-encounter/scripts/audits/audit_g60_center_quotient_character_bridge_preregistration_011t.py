#!/usr/bin/env python3
import hashlib
import json
import subprocess
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
JSON_PATH = PROJECT / "artifacts/json/g60_center_quotient_character_bridge_preregistration_011t.v1.json"
NOTE_PATH = PROJECT / "notes/g60_center_quotient_character_bridge_preregistration_011t.md"

EXPECTED_JSON_HASH = "002c78d86b0477aef0b351260c894e40f493d5d3f6f2b2cfa118f6b2f2b011b7"
EXPECTED_NOTE_HASH = "37313967a66630d6f8f5fafb0bb340b86f35ce4d0612df08e1387b3e66bf3d2f"
LOCKED_HEAD = "1424fec Lock G60 local-global side obstruction"

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
known = data["known_structure"]
predictions = data["predictions"]
withheld = data["claims_withheld"]
boundary = data["boundary"]
authorities = data["authorities"]
head = git("show", "-s", "--format=%h %s", "HEAD")

checks = [
    ("packet", data.get("packet") == "g60_center_quotient_character_bridge_preregistration_011t"),
    ("mode", data.get("mode") == "post_direct_side_obstruction_center_quotient_bridge_preregistration"),
    ("status", data.get("status") == "frozen_before_center_quotient_character_census"),
    ("head", data.get("locked_head") == LOCKED_HEAD and head == LOCKED_HEAD),
    ("json_hash", sha256_file(JSON_PATH) == EXPECTED_JSON_HASH),
    ("note_hash", sha256_file(NOTE_PATH) == EXPECTED_NOTE_HASH),
    ("authority_count", len(authorities) == 7),
    ("authority_hashes", all(row.get("hash_match") is True for row in authorities.values())),
    ("group_480", known.get("full_group_order") == 480),
    ("quotient_S5", known.get("five_point_quotient") == "S5"),
    ("transpositions_10", known.get("five_point_transposition_count") == 10),
    ("native_indices", known.get("native_V4_indices") == {"1": 0, "a": 326, "b": 124, "ab": 65}),
    ("alpha_restriction", known.get("011o_alpha_1_restriction_to_native_V4") == {"1": 0, "a": 0, "b": 1, "ab": 1}),
    ("selected_D8", known.get("selected_011q_extension_type") == "D8"),
    ("selected_representatives_2", known.get("selected_011q_representative_count") == 2),
    ("selected_center_2", known.get("selected_011q_center_order") == 2),
    ("selected_signature", known.get("selected_011q_square_signature") == {"q(a)": 1, "q(b)": 0, "q(ab)": 0}),
    ("obstruction_locked", known.get("direct_side_identification_obstructed_by_011s") is True),
    ("locked_isomorphisms_16", known.get("011s_isomorphism_count") == 16),
    ("prediction_declared", predictions.get("prediction_declared_before_center_quotient_census") is True),
    ("prediction_not_blind", predictions.get("prediction_blind") is False),
    ("predict_lifts_40", predictions.get("transposition_lift_element_count") == 40),
    ("predict_subgroups_10", predictions.get("native_D8_subgroup_count") == 10),
    ("predict_four_lifts", predictions.get("transposition_lifts_per_native_D8_subgroup") == 4),
    ("predict_presentations_2", predictions.get("presentation_count") == 2),
    ("predict_eight_isomorphisms", predictions.get("isomorphism_count_per_presentation_subgroup_pair") == 8),
    ("predict_pairs_20", predictions.get("presentation_subgroup_pair_count") == 20),
    ("predict_comparisons_160", predictions.get("total_isomorphism_character_comparison_count") == 160),
    ("predict_center_killed", predictions.get("all_pulled_back_characters_kill_local_center") is True),
    ("predict_all_descend", predictions.get("all_characters_descend_to_visible_V4") is True),
    ("predict_unique_character", predictions.get("distinct_descended_character_count") == 1),
    ("predict_character_profile", predictions.get("unique_descended_character") == {"1": 0, "a": 0, "b": 1, "ab": 1}),
    ("predict_kernel", predictions.get("descended_character_kernel") == ["1", "a"]),
    ("predict_q_axis", predictions.get("descended_kernel_equals_q_distinguished_axis") is True),
    ("predict_kernel_C4", predictions.get("pulled_back_kernel_group_type") == "C4"),
    ("predict_same_gauge", predictions.get("both_gauge_presentations_give_same_character") is True),
    ("predict_bridge", predictions.get("center_quotient_character_bridge_constructed_if_prediction_passes") is True),
    ("predict_no_side_identity", predictions.get("local_side_identified_with_011o_sheet") is False),
    ("predict_classification", predictions.get("predicted_classification") == "unique_center_quotient_character_bridge"),
    ("required_test_count", len(data.get("required_tests", [])) == 18),
    ("outcome_count", len(data.get("outcome_order", [])) == 12),
    ("falsifier_count", len(data.get("falsifiers", [])) == 12),
    ("no_subgroup_claim", withheld.get("native_D8_subgroups_enumerated") is False),
    ("no_census_claim", withheld.get("isomorphism_character_census_performed") is False),
    ("no_bridge_claim", withheld.get("center_quotient_character_bridge_constructed") is False),
    ("no_unique_claim", withheld.get("unique_descended_character_verified") is False),
    ("no_side_identity", withheld.get("local_side_identified_with_011o_orientation_sheet") is False),
    ("no_update_law", withheld.get("native_update_law_constructed") is False),
    ("no_mechanics_cell", withheld.get("mechanics_state_cell_established") is False),
    ("no_orientation", withheld.get("orientation_selected") is False),
    ("bounded_test", boundary.get("bounded_center_quotient_character_test_only") is True),
    ("quotient_forgets_side", boundary.get("local_route_side_preserved_by_quotient") is False),
    ("obstruction_not_reversed", boundary.get("direct_side_obstruction_reversed") is False),
    ("no_global_minimality", boundary.get("global_minimality_claim") is False),
    ("no_manuscript", boundary.get("manuscript_mutated") is False),
    ("no_geometry", boundary.get("geometry_claim") is False),
    ("no_physical_direction", boundary.get("physical_direction_claim") is False),
    ("no_physics", boundary.get("physical_claim") is False),
    ("note_exists", NOTE_PATH.is_file()),
]

failed = [name for name, passed in checks if not passed]

print("== G60 CENTER-QUOTIENT CHARACTER BRIDGE PREREGISTRATION AUDIT 011t ==")
print("PACKET:", data.get("packet"))
print("MODE:", data.get("mode"))
print("JSON_SHA256:", sha256_file(JSON_PATH))
print("NOTE_SHA256:", sha256_file(NOTE_PATH))
print("LOCKED_HEAD:", data.get("locked_head"))
print("PREDICTED_NATIVE_D8_SUBGROUP_COUNT:", predictions.get("native_D8_subgroup_count"))
print("PREDICTED_TOTAL_COMPARISON_COUNT:", predictions.get("total_isomorphism_character_comparison_count"))
print("PREDICTED_UNIQUE_CHARACTER:", predictions.get("unique_descended_character"))
print("PREDICTED_CLASSIFICATION:", predictions.get("predicted_classification"))
print("CENTER_QUOTIENT_CENSUS_PERFORMED: false")
print("CHECK_COUNT:", len(checks))
print("FAILED_CHECK_COUNT:", len(failed))

for name, passed in checks:
    print("CHECK", name + ":", str(bool(passed)).lower())

print("PREREGISTRATION_PASS:", str(not failed).lower())
print("FAILED_CHECKS:", failed)
print("CENTER_QUOTIENT_CHARACTER_BRIDGE_CONSTRUCTED: false")
print("LOCAL_SIDE_EQUALS_011O_ORIENTATION_SHEET: false")
print("NATIVE_UPDATE_LAW_CONSTRUCTED: false")
print("MECHANICS_STATE_CELL_ESTABLISHED: false")
print("MANUSCRIPT_MUTATED: false")
print("PHYSICAL_CLAIM: false")

if failed:
    raise SystemExit(1)
