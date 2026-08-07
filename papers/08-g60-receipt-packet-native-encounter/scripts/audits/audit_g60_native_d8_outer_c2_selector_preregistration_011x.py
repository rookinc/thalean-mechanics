#!/usr/bin/env python3
import hashlib
import json
import subprocess
from pathlib import Path

project = Path(__file__).resolve().parents[2]
json_path = project / "artifacts/json/g60_native_d8_outer_c2_selector_preregistration_011x.v1.json"
note_path = project / "notes/g60_native_d8_outer_c2_selector_preregistration_011x.md"

def sha256_file(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()

def git(*args):
    result = subprocess.run(
        ["git", *args],
        cwd=project,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout.strip()

data = json.loads(json_path.read_text(encoding="utf-8"))
pred = data["predictions"]
locked = data["locked_input_surface"]
boundary = data["boundary"]

checks = []
def check(name, value):
    checks.append((name, bool(value)))

check("packet", data["packet"] == "g60_native_d8_outer_c2_selector_preregistration_011x")
check("mode", data["mode"] == "post_chart_coherence_outer_C2_selector_preregistration")
check("status", data["status"] == "frozen_before_local_D8_automorphism_enumeration")
check("head", git("show", "-s", "--format=%h %s", "HEAD") ==
      "18ae44f Lock G60 native D8 chart coherence obstruction")
check("authority_count", len(data["authorities"]) == 8)
check("authority_hashes", all(
    Path(path).is_file()
    and row["hash_match"] is True
    and sha256_file(Path(path)) == row["expected_sha256"] == row["sha256"]
    for path, row in data["authorities"].items()
))
check("note_exists", note_path.is_file())
check("note_hash", sha256_file(note_path) ==
      data["companion_files"]["note_sha256"])
check("group_480", locked["full_group_order"] == 480)
check("subgroups_10", locked["native_D8_subgroup_count"] == 10)
check("presentations_2", locked["local_presentation_count"] == 2)
check("charts_80", locked["chart_count_per_presentation"] == 80)
check("charts_160", locked["total_chart_count"] == 160)
check("orbits_40_40", locked["chart_orbit_profile_per_presentation"] == [40, 40])
check("fiber_8", locked["fiber_size"] == 8)
check("fiber_orbits_4_4", locked["fiber_orbit_profile"] == [4, 4])
check("inner_image_4", locked["normalizer_fiber_image_order"] == 4)
check("image_inner", locked["normalizer_image_equals_inner_automorphisms"] is True)
check("residual_C2", locked["residual_outer_gauge_group"] == "C2")
check("alpha_character", locked["alpha_1_character"] ==
      {"1": 0, "a": 0, "b": 1, "ab": 1})
check("q_signature", locked["q_axis_signature"] ==
      {"a": 1, "b": 0, "ab": 0})
check("alpha_constant_locked", locked["alpha_1_constant_across_outer_orbits"] is True)
check("q_constant_locked", locked["q_axis_signature_constant_across_outer_orbits"] is True)
check("gauge_maps_4", locked["presentation_gauge_map_count"] == 4)
check("gauge_preserves_orbits", locked["presentation_gauge_maps_preserve_orbit_classes"] is True)
check("sections_zero", locked["strict_equivariant_section_count_per_presentation"] == [0, 0])
check("predict_aut_8", pred["local_D8_automorphism_group_order"] == 8)
check("predict_inner_4", pred["local_D8_inner_automorphism_group_order"] == 4)
check("predict_outer_2", pred["local_D8_outer_automorphism_group_order"] == 2)
check("predict_inner_count_4", pred["inner_automorphism_count"] == 4)
check("predict_outer_count_4", pred["outer_automorphism_count"] == 4)
check("predict_inner_preserves", pred["inner_automorphisms_preserve_each_fiber_orbit"] is True)
check("predict_outer_fiber_exchange", pred["outer_automorphisms_exchange_fiber_orbits"] is True)
check("predict_outer_global_exchange", pred["outer_automorphisms_exchange_global_chart_orbits"] is True)
check("predict_global_outer_4", pred["global_outer_involution_count_per_presentation"] == 4)
check("predict_extended_order_960", pred["extended_chart_action_order_per_presentation"] == 960)
check("predict_extended_orbit_80", pred["extended_chart_orbit_profile_per_presentation"] == [80])
check("predict_extended_stabilizer_12", pred["extended_chart_stabilizer_order"] == 12)
check("predict_selector_zero", pred["strict_outer_gauge_invariant_orbit_selector_count"] == 0)
check("predict_choices_two", pred["full_A_invariant_orbit_choices_before_outer_quotient"] == 2)
check("predict_torsor_two", pred["minimal_extra_torsor_cardinality"] == 2)
check("predict_binary_one", pred["minimal_extra_binary_choice_count"] == 1)
check("predict_alpha_constant", pred["alpha_1_constant_under_outer_exchange"] is True)
check("predict_q_constant", pred["q_axis_signature_constant_under_outer_exchange"] is True)
check("predict_gauge_equivalent", pred["gauge_related_presentations_have_equivalent_outer_C2_torsors"] is True)
check("predict_no_absolute", pred["absolute_orbit_selected_by_locked_data"] is False)
check("classification", pred["predicted_classification"] ==
      "native_D8_chart_orbit_selection_requires_one_external_outer_C2_torsor_choice")
check("required_tests", len(data["required_tests"]) == 22)
check("outcomes", len(data["outcome_order"]) == 14)
check("falsifiers", len(data["falsifiers"]) == 13)
check("bounded", boundary["bounded_native_D8_chart_model_only"] is True)
check("no_census", boundary["outer_selector_census_performed"] is False)
check("no_automorphisms", boundary["local_D8_automorphisms_enumerated"] is False)
check("no_exchange_claim", boundary["outer_C2_exchange_verified"] is False)
check("no_necessity_claim", boundary["extra_binary_datum_proved_necessary"] is False)
check("no_orbit_selected", boundary["absolute_chart_orbit_selected"] is False)
check("no_chart_selected", boundary["strict_equivariant_chart_selected"] is False)
check("bundle_locked", boundary["gauge_covariant_bundle_already_classified"] is True)
check("no_update", boundary["native_update_law_constructed"] is False)
check("no_cell", boundary["mechanics_state_cell_established"] is False)
check("no_side_identity", boundary["local_side_equals_011o_orientation_sheet"] is False)
check("no_orientation", boundary["orientation_selected"] is False)
check("no_global_minimality", boundary["global_minimality_claim"] is False)
check("no_manuscript", boundary["manuscript_mutated"] is False)
check("no_geometry", boundary["geometry_claim"] is False)
check("no_direction", boundary["physical_direction_claim"] is False)
check("no_physics", boundary["physical_claim"] is False)

failed = [name for name, passed in checks if not passed]

print("== G60 NATIVE D8 OUTER-C2 SELECTOR PREREGISTRATION AUDIT 011x ==")
print("PACKET:", data["packet"])
print("MODE:", data["mode"])
print("JSON_SHA256:", sha256_file(json_path))
print("NOTE_SHA256:", sha256_file(note_path))
print("LOCKED_HEAD:", data["locked_head"])
print("PREDICTED_AUT_D8_ORDER:", pred["local_D8_automorphism_group_order"])
print("PREDICTED_INNER_D8_ORDER:", pred["local_D8_inner_automorphism_group_order"])
print("PREDICTED_OUTER_D8_ORDER:", pred["local_D8_outer_automorphism_group_order"])
print("PREDICTED_EXTENDED_CHART_ORBIT_PROFILE:",
      pred["extended_chart_orbit_profile_per_presentation"])
print("PREDICTED_OUTER_INVARIANT_SELECTOR_COUNT:",
      pred["strict_outer_gauge_invariant_orbit_selector_count"])
print("PREDICTED_MINIMAL_TORSOR_CARDINALITY:",
      pred["minimal_extra_torsor_cardinality"])
print("PREDICTED_CLASSIFICATION:", pred["predicted_classification"])
print("OUTER_SELECTOR_CENSUS_PERFORMED: false")
print("CHECK_COUNT:", len(checks))
print("FAILED_CHECK_COUNT:", len(failed))
for name, passed in checks:
    print("CHECK", name + ":", str(passed).lower())
print("PREREGISTRATION_PASS:", str(not failed).lower())
print("FAILED_CHECKS:", failed)
print("EXTRA_BINARY_DATUM_PROVED_NECESSARY: false")
print("ABSOLUTE_CHART_ORBIT_SELECTED: false")
print("NATIVE_UPDATE_LAW_CONSTRUCTED: false")
print("MECHANICS_STATE_CELL_ESTABLISHED: false")
print("MANUSCRIPT_MUTATED: false")
print("PHYSICAL_CLAIM: false")
