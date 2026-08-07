#!/usr/bin/env python3
import hashlib
import json
import subprocess
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
JSON_PATH = PROJECT / "artifacts/json/g60_two_sided_slider_cocycle_preregistration_011p.v1.json"
NOTE_PATH = PROJECT / "notes/g60_two_sided_slider_cocycle_preregistration_011p.md"

EXPECTED_JSON_HASH = "5c09a3f307b05bf25c8ed11606ee3c58a93da16a973699b3905fa03c1b51b7bf"
EXPECTED_NOTE_HASH = "6f6db963cb65eefa6712dc7ba3e6162b14dd63b38cc1e4adb41b5cd842778f0d"
LOCKED_HEAD = "656c767 Lock G60 full-A orientation character bridge"

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
model = data["declared_two_sided_model"]
pred = data["predictions"]
withheld = data["claims_withheld"]
boundary = data["boundary"]
authorities = data["authorities"]
head = git("show", "-s", "--format=%h %s", "HEAD")

checks = [
    ("packet", data.get("packet") == "g60_two_sided_slider_cocycle_preregistration_011p"),
    ("mode", data.get("mode") == "post_full_A_bridge_two_sided_slider_cocycle_preregistration"),
    ("status", data.get("status") == "frozen_before_cocycle_enumeration"),
    ("head", data.get("locked_head") == LOCKED_HEAD and head == LOCKED_HEAD),
    ("json_hash", sha256_file(JSON_PATH) == EXPECTED_JSON_HASH),
    ("note_hash", sha256_file(NOTE_PATH) == EXPECTED_NOTE_HASH),
    ("authority_count", len(authorities) == 5),
    ("authority_hashes", all(row.get("hash_match") is True for row in authorities.values())),
    ("visible_V4", known.get("visible_state_register") == "V4={1,a,b,ab}"),
    ("visible_count_4", known.get("visible_state_count") == 4),
    ("native_V4_verified", known.get("native_v4_verified") is True),
    ("native_commutative", known.get("native_ab_equals_ba") is True),
    ("native_D8", known.get("native_local_structure_group") == "D8"),
    ("native_D8_order_8", known.get("native_local_structure_group_order") == 8),
    ("native_center_2", known.get("native_local_structure_group_center_order") == 2),
    ("native_order_profile", known.get("native_local_structure_group_element_order_profile") == {"1": 1, "2": 5, "4": 2}),
    ("native_axis_swap", known.get("native_axis_swap") == {"1": "1", "a": "a", "b": "ab", "ab": "b"}),
    ("native_carrier_a", known.get("native_carrier_axis") == "a"),
    ("native_no_global_trivialization", known.get("native_b_ab_global_trivialization_exists") is False),
    ("native_triangle_holonomy", known.get("native_triangle_holonomy_nontrivial") is True),
    ("model_base_V4", model.get("base_group") == "V4"),
    ("model_side_C2", model.get("side_group") == "C2"),
    ("model_count_8", model.get("lifted_object_count") == 8),
    ("model_normalized", model.get("normalization") == "omega(1,x)=omega(x,1)=0"),
    ("no_cocycle_enumeration", model.get("cocycle_enumeration_performed") is False),
    ("no_cohomology", model.get("cohomology_quotient_computed") is False),
    ("no_classification", model.get("extension_types_classified") is False),
    ("no_native_filter", model.get("native_axis_filter_applied") is False),
    ("no_AB_BA_test", model.get("ab_ba_test_performed") is False),
    ("no_sheet_comparison", model.get("orientation_sheet_comparison_performed") is False),
    ("prediction_declared", pred.get("prediction_declared_before_computation") is True),
    ("prediction_not_blind", pred.get("prediction_blind") is False),
    ("predict_functions_512", pred.get("normalized_function_count") == 512),
    ("predict_cocycles_16", pred.get("normalized_cocycle_count") == 16),
    ("predict_coboundaries_2", pred.get("distinct_normalized_coboundary_count") == 2),
    ("predict_classes_8", pred.get("cohomology_class_count") == 8),
    ("predict_two_per_class", pred.get("cocycle_representatives_per_class") == 2),
    ("predict_type_profile", pred.get("extension_type_class_profile") == {"C2_x_C2_x_C2": 1, "C4_x_C2": 3, "D8": 3, "Q8": 1}),
    ("predict_route_cocycles_8", pred.get("route_separating_cocycle_count") == 8),
    ("predict_route_classes_4", pred.get("route_separating_class_count") == 4),
    ("predict_route_nonabelian", pred.get("all_route_separating_classes_nonabelian") is True),
    ("predict_signature", pred.get("native_axis_square_signature") == {"q(a)": 1, "q(b)": 0, "q(ab)": 0}),
    ("predict_selected_class_1", pred.get("native_axis_selected_class_count") == 1),
    ("predict_selected_cocycles_2", pred.get("native_axis_selected_cocycle_count") == 2),
    ("predict_selected_D8", pred.get("native_axis_selected_extension_type") == "D8"),
    ("predict_separates", pred.get("native_axis_selected_class_separates_AB_BA") is True),
    ("predict_same_endpoint", pred.get("AB_BA_same_visible_endpoint") is True),
    ("predict_opposite_sides", pred.get("AB_BA_opposite_central_sides") is True),
    ("predict_not_unique_representative", pred.get("unique_cocycle_representative_predicted") is False),
    ("predict_gauge_pair", pred.get("two_representatives_are_gauge_related") is True),
    ("no_sheet_identification_prediction", pred.get("orientation_sheet_identification_predicted") is False),
    ("required_test_count", len(data.get("required_tests", [])) == 20),
    ("outcome_count", len(data.get("outcome_order", [])) == 10),
    ("falsifier_count", len(data.get("falsifiers", [])) == 8),
    ("no_slider_claim", withheld.get("two_sided_slider_cocycle_constructed") is False),
    ("no_native_selection_claim", withheld.get("native_class_selected") is False),
    ("no_AB_BA_claim", withheld.get("AB_BA_distinguished") is False),
    ("no_local_global_claim", withheld.get("local_side_equals_011o_orientation_sheet") is False),
    ("no_update_law", withheld.get("native_update_law_constructed") is False),
    ("no_mechanics_cell", withheld.get("mechanics_state_cell_established") is False),
    ("no_orientation", withheld.get("orientation_selected") is False),
    ("bounded_test", boundary.get("finite_central_extension_test_only") is True),
    ("no_unique_representative", boundary.get("unique_representative_claim") is False),
    ("no_sheet_identity", boundary.get("local_global_sheet_identification_claim") is False),
    ("no_global_minimality", boundary.get("global_minimality_claim") is False),
    ("no_manuscript", boundary.get("manuscript_mutated") is False),
    ("no_geometry", boundary.get("geometry_claim") is False),
    ("no_physical_direction", boundary.get("physical_direction_claim") is False),
    ("no_physics", boundary.get("physical_claim") is False),
    ("note_exists", NOTE_PATH.is_file()),
]

failed = [name for name, passed in checks if not passed]

print("== G60 TWO-SIDED SLIDER COCYCLE PREREGISTRATION AUDIT 011p ==")
print("PACKET:", data.get("packet"))
print("MODE:", data.get("mode"))
print("JSON_SHA256:", sha256_file(JSON_PATH))
print("NOTE_SHA256:", sha256_file(NOTE_PATH))
print("LOCKED_HEAD:", data.get("locked_head"))
print("PREDICTED_NORMALIZED_COCYCLE_COUNT:", pred.get("normalized_cocycle_count"))
print("PREDICTED_COHOMOLOGY_CLASS_COUNT:", pred.get("cohomology_class_count"))
print("PREDICTED_EXTENSION_TYPE_PROFILE:", pred.get("extension_type_class_profile"))
print("PREDICTED_ROUTE_SEPARATING_CLASS_COUNT:", pred.get("route_separating_class_count"))
print("PREDICTED_NATIVE_SELECTED_CLASS_COUNT:", pred.get("native_axis_selected_class_count"))
print("PREDICTED_NATIVE_EXTENSION_TYPE:", pred.get("native_axis_selected_extension_type"))
print("COCYCLE_ENUMERATION_PERFORMED:", str(model.get("cocycle_enumeration_performed")).lower())
print("CHECK_COUNT:", len(checks))
print("FAILED_CHECK_COUNT:", len(failed))

for name, passed in checks:
    print("CHECK", name + ":", str(bool(passed)).lower())

print("PREREGISTRATION_PASS:", str(not failed).lower())
print("FAILED_CHECKS:", failed)
print("AB_BA_DISTINGUISHED:", str(withheld.get("AB_BA_distinguished")).lower())
print("LOCAL_SIDE_EQUALS_011O_ORIENTATION_SHEET:", str(withheld.get("local_side_equals_011o_orientation_sheet")).lower())
print("MANUSCRIPT_MUTATED:", str(boundary.get("manuscript_mutated")).lower())
print("PHYSICAL_CLAIM:", str(boundary.get("physical_claim")).lower())

if failed:
    raise SystemExit(1)
