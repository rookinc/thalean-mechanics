#!/usr/bin/env python3
import hashlib
import json
import subprocess
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
JSON_PATH = PROJECT / "artifacts/json/g60_native_d8_chart_coherence_preregistration_011v.v1.json"
NOTE_PATH = PROJECT / "notes/g60_native_d8_chart_coherence_preregistration_011v.md"

EXPECTED_JSON_HASH = "916a39858e97a64763b7dc35b1731e51362276934051a893a5548294fd16ea6c"
EXPECTED_NOTE_HASH = "b148343c2ada46e512b3001ff5391c6f624a83ce34b3d71c4ee98bc950291473"
LOCKED_HEAD = "7e43c41 Lock G60 center-quotient character bridge"

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
surface = data["registered_surface"]
predictions = data["predictions"]
boundary = data["boundary"]
authorities = data["authorities"]
head = git("show", "-s", "--format=%h %s", "HEAD")

checks = [
    ("packet", data.get("packet") == "g60_native_d8_chart_coherence_preregistration_011v"),
    ("mode", data.get("mode") == "post_center_quotient_bridge_native_chart_coherence_preregistration"),
    ("status", data.get("status") == "frozen_before_chart_orbit_census"),
    ("head", data.get("locked_head") == LOCKED_HEAD and head == LOCKED_HEAD),
    ("json_hash", sha256_file(JSON_PATH) == EXPECTED_JSON_HASH),
    ("note_hash", sha256_file(NOTE_PATH) == EXPECTED_NOTE_HASH),
    ("authority_count", len(authorities) == 6),
    ("authority_hashes", all(row.get("hash_match") is True for row in authorities.values())),
    ("group_480", surface.get("full_group_order") == 480),
    ("base_count_10", surface.get("base_object_count") == 10),
    ("presentations_2", surface.get("local_presentation_count") == 2),
    ("charts_each_8", surface.get("charts_per_presentation_subgroup_pair") == 8),
    ("pairs_20", surface.get("presentation_subgroup_pair_count") == 20),
    ("charts_total_160", surface.get("total_chart_count_both_presentations") == 160),
    ("prediction_declared", predictions.get("prediction_declared_before_computation") is True),
    ("prediction_not_blind", predictions.get("prediction_blind") is False),
    ("predict_subgroups_10", predictions.get("native_D8_subgroup_count") == 10),
    ("predict_base_transitive", predictions.get("base_action_transitive") is True),
    ("predict_base_stabilizer_48", predictions.get("base_stabilizer_order") == 48),
    ("predict_charts_80", predictions.get("chart_count_per_presentation") == 80),
    ("predict_charts_160", predictions.get("chart_count_both_presentations") == 160),
    ("predict_aut_D8_8", predictions.get("automorphism_group_order_D8") == 8),
    ("predict_inner_4", predictions.get("inner_automorphism_group_order_D8") == 4),
    ("predict_outer_2", predictions.get("outer_automorphism_group_order_D8") == 2),
    ("predict_chart_stabilizer_12", predictions.get("chart_stabilizer_order") == 12),
    ("predict_two_orbits", predictions.get("chart_orbit_count_per_presentation") == 2),
    ("predict_40_40", predictions.get("chart_orbit_size_profile_per_presentation") == [40, 40]),
    ("predict_four_total_orbits", predictions.get("chart_orbit_count_both_presentations") == 4),
    ("predict_total_profile", predictions.get("chart_orbit_size_profile_both_presentations") == [40, 40, 40, 40]),
    ("predict_fiber_image_4", predictions.get("normalizer_fiber_action_order") == 4),
    ("predict_fiber_two_orbits", predictions.get("normalizer_fiber_orbit_count") == 2),
    ("predict_fiber_profile", predictions.get("normalizer_fiber_orbit_size_profile") == [4, 4]),
    ("predict_inner_action", predictions.get("normalizer_fiber_action_equals_inner_automorphisms") is True),
    ("predict_outer_gauge", predictions.get("outer_C2_is_residual_chart_gauge") is True),
    ("predict_section_zero", predictions.get("equivariant_one_chart_per_subgroup_section_count") == 0),
    ("predict_no_section", predictions.get("strict_equivariant_chart_selection_exists") is False),
    ("predict_alpha_constant", predictions.get("alpha_1_character_constant_across_chart_orbits") is True),
    ("predict_q_constant", predictions.get("q_axis_signature_constant_across_chart_orbits") is True),
    ("predict_no_locked_selection", predictions.get("locked_character_data_selects_one_outer_orbit") is False),
    ("predict_gauge_equivalent", predictions.get("gauge_related_presentations_have_equivalent_chart_bundles") is True),
    ("predict_bundle_classifiable", predictions.get("gauge_covariant_D8_chart_bundle_classifiable") is True),
    ("predict_no_update", predictions.get("native_update_law_predicted") is False),
    ("required_tests", len(data.get("required_tests", [])) == 17),
    ("outcomes", len(data.get("outcome_order", [])) == 13),
    ("falsifiers", len(data.get("falsifiers", [])) == 12),
    ("no_orbit_claim", boundary.get("chart_orbit_census_performed") is False),
    ("no_section_test", boundary.get("equivariant_section_test_performed") is False),
    ("no_bundle_classification", boundary.get("gauge_covariant_bundle_classified") is False),
    ("no_chart_selected", boundary.get("strict_equivariant_chart_selected") is False),
    ("no_update_law", boundary.get("native_update_law_constructed") is False),
    ("no_mechanics_cell", boundary.get("mechanics_state_cell_established") is False),
    ("no_orientation", boundary.get("orientation_selected") is False),
    ("no_side_identity", boundary.get("local_side_equals_011o_orientation_sheet") is False),
    ("no_global_minimality", boundary.get("global_minimality_claim") is False),
    ("no_manuscript", boundary.get("manuscript_mutated") is False),
    ("no_geometry", boundary.get("geometry_claim") is False),
    ("no_physical_direction", boundary.get("physical_direction_claim") is False),
    ("no_physics", boundary.get("physical_claim") is False),
    ("note_exists", NOTE_PATH.is_file()),
]

failed = [name for name, passed in checks if not passed]

print("== G60 NATIVE D8 CHART-COHERENCE PREREGISTRATION AUDIT 011v ==")
print("PACKET:", data.get("packet"))
print("MODE:", data.get("mode"))
print("JSON_SHA256:", sha256_file(JSON_PATH))
print("NOTE_SHA256:", sha256_file(NOTE_PATH))
print("LOCKED_HEAD:", data.get("locked_head"))
print("PREDICTED_CHART_ORBITS_PER_PRESENTATION:", predictions.get("chart_orbit_size_profile_per_presentation"))
print("PREDICTED_CHART_STABILIZER_ORDER:", predictions.get("chart_stabilizer_order"))
print("PREDICTED_EQUIVARIANT_SECTION_COUNT:", predictions.get("equivariant_one_chart_per_subgroup_section_count"))
print("PREDICTED_CLASSIFICATION:", predictions.get("predicted_classification"))
print("CHART_ORBIT_CENSUS_PERFORMED: false")
print("CHECK_COUNT:", len(checks))
print("FAILED_CHECK_COUNT:", len(failed))

for name, passed in checks:
    print("CHECK", name + ":", str(bool(passed)).lower())

print("PREREGISTRATION_PASS:", str(not failed).lower())
print("FAILED_CHECKS:", failed)
print("GAUGE_COVARIANT_BUNDLE_CLASSIFIED: false")
print("STRICT_EQUIVARIANT_CHART_SELECTED: false")
print("NATIVE_UPDATE_LAW_CONSTRUCTED: false")
print("MECHANICS_STATE_CELL_ESTABLISHED: false")
print("MANUSCRIPT_MUTATED: false")
print("PHYSICAL_CLAIM: false")

if failed:
    raise SystemExit(1)
