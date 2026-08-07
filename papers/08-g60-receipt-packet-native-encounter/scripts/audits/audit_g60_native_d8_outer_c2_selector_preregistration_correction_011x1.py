#!/usr/bin/env python3
import hashlib
import json
import subprocess
from pathlib import Path

project = Path(__file__).resolve().parents[2]
json_path = project / "artifacts/json/g60_native_d8_outer_c2_selector_preregistration_correction_011x1.v1.json"
note_path = project / "notes/g60_native_d8_outer_c2_selector_preregistration_correction_011x1.md"

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
pred = data["corrected_predictions"]
boundary = data["boundary"]

checks = []
def check(name, value):
    checks.append((name, bool(value)))

check("packet", data["packet"] ==
      "g60_native_d8_outer_c2_selector_preregistration_correction_011x1")
check("mode", data["mode"] ==
      "pre_census_algebraic_correction_to_outer_C2_selector_preregistration")
check("status", data["status"] ==
      "frozen_before_local_D8_automorphism_enumeration")
check("head", git("show", "-s", "--format=%h %s", "HEAD") ==
      "ca9e015 Preregister G60 outer-C2 chart selector test")
check("corrects_packet", data["corrects_packet"] ==
      "g60_native_d8_outer_c2_selector_preregistration_011x")
check("corrects_commit", data["corrects_commit"] == "ca9e015")
check("authority_count", len(data["authorities"]) == 5)
check("authority_hashes", all(
    Path(path).is_file()
    and row["hash_match"] is True
    and sha256_file(Path(path)) == row["expected_sha256"] == row["sha256"]
    for path, row in data["authorities"].items()
))
check("note_exists", note_path.is_file())
check("note_hash", sha256_file(note_path) ==
      data["companion_files"]["note_sha256"])
check("no_census_source", data["reason_for_correction"]["census_result_used"] is False)
check("aut_order_8", pred["local_D8_automorphism_group_order"] == 8)
check("aut_profile", pred["local_D8_automorphism_order_profile"] ==
      {"1": 1, "2": 5, "4": 2})
check("inner_order_4", pred["inner_automorphism_group_order"] == 4)
check("inner_profile", pred["inner_automorphism_order_profile"] ==
      {"1": 1, "2": 3})
check("outer_group_C2", pred["outer_quotient_group"] == "C2")
check("outer_order_2", pred["outer_quotient_group_order"] == 2)
check("outer_coset_4", pred["outer_coset_size"] == 4)
check("outer_profile", pred["outer_coset_order_profile"] ==
      {"2": 2, "4": 2})
check("outer_involutions_2", pred["outer_involution_count"] == 2)
check("outer_order4_2", pred["outer_order_four_count"] == 2)
check("fiber_exchange", pred["all_outer_representatives_exchange_fiber_orbit_classes"] is True)
check("global_exchange", pred["all_outer_representatives_exchange_global_chart_orbits"] is True)
check("outer_class", pred["each_outer_representative_induces_nontrivial_outer_C2_class"] is True)
check("extended_count_2", pred["genuine_outer_involution_extended_action_count"] == 2)
check("extended_order_960", pred["extended_action_order_for_each_outer_involution"] == 960)
check("extended_orbit_80", pred["extended_orbit_profile_for_each_outer_involution"] == [80])
check("extended_stabilizer_12", pred["extended_stabilizer_order_for_each_outer_involution"] == 12)
check("no_order4_extension_prediction",
      pred["extended_action_order_for_order_four_representatives_preregistered"] is False)
check("alpha_constant", pred["alpha_1_constant_under_outer_exchange"] is True)
check("q_constant", pred["q_axis_signature_constant_under_outer_exchange"] is True)
check("gauge_equivalent", pred["gauge_related_presentations_have_equivalent_outer_C2_torsors"] is True)
check("selector_zero", pred["outer_gauge_invariant_single_orbit_selector_count"] == 0)
check("torsor_two", pred["minimal_extra_torsor_cardinality"] == 2)
check("binary_one", pred["minimal_extra_binary_choice_count"] == 1)
check("classification", pred["predicted_classification"] ==
      "native_D8_chart_orbit_selection_requires_one_external_outer_C2_torsor_choice")
check("superseded_fields_4", len(data["superseded_011x_fields"]) == 4)
check("required_tests_20", len(data["required_tests"]) == 20)
check("outcomes_14", len(data["outcome_order"]) == 14)
check("pre_census", boundary["correction_recorded_before_census"] is True)
check("no_census", boundary["outer_selector_census_performed"] is False)
check("no_enumeration", boundary["local_D8_automorphisms_enumerated"] is False)
check("no_profile_measurement", boundary["outer_coset_order_profile_measured"] is False)
check("no_exchange_claim", boundary["outer_exchange_verified"] is False)
check("no_necessity_claim", boundary["extra_binary_datum_proved_necessary"] is False)
check("no_orbit", boundary["absolute_chart_orbit_selected"] is False)
check("no_chart", boundary["strict_equivariant_chart_selected"] is False)
check("no_update", boundary["native_update_law_constructed"] is False)
check("no_cell", boundary["mechanics_state_cell_established"] is False)
check("no_side_identity", boundary["local_side_equals_011o_orientation_sheet"] is False)
check("no_orientation", boundary["orientation_selected"] is False)
check("bounded", boundary["bounded_native_D8_chart_model_only"] is True)
check("no_global_minimality", boundary["global_minimality_claim"] is False)
check("no_manuscript", boundary["manuscript_mutated"] is False)
check("no_geometry", boundary["geometry_claim"] is False)
check("no_direction", boundary["physical_direction_claim"] is False)
check("no_physics", boundary["physical_claim"] is False)

failed = [name for name, passed in checks if not passed]

print("== G60 OUTER-C2 SELECTOR PREREGISTRATION CORRECTION AUDIT 011x1 ==")
print("PACKET:", data["packet"])
print("MODE:", data["mode"])
print("JSON_SHA256:", sha256_file(json_path))
print("NOTE_SHA256:", sha256_file(note_path))
print("LOCKED_HEAD:", data["locked_head"])
print("AUT_D8_ORDER_PROFILE:", pred["local_D8_automorphism_order_profile"])
print("INNER_AUT_ORDER_PROFILE:", pred["inner_automorphism_order_profile"])
print("OUTER_COSET_ORDER_PROFILE:", pred["outer_coset_order_profile"])
print("OUTER_INVOLUTION_COUNT:", pred["outer_involution_count"])
print("OUTER_ORDER4_COUNT:", pred["outer_order_four_count"])
print("PREDICTED_CLASSIFICATION:", pred["predicted_classification"])
print("OUTER_SELECTOR_CENSUS_PERFORMED: false")
print("CHECK_COUNT:", len(checks))
print("FAILED_CHECK_COUNT:", len(failed))
for name, passed in checks:
    print("CHECK", name + ":", str(passed).lower())
print("CORRECTION_PASS:", str(not failed).lower())
print("FAILED_CHECKS:", failed)
print("EXTRA_BINARY_DATUM_PROVED_NECESSARY: false")
print("ABSOLUTE_CHART_ORBIT_SELECTED: false")
print("NATIVE_UPDATE_LAW_CONSTRUCTED: false")
print("MECHANICS_STATE_CELL_ESTABLISHED: false")
print("MANUSCRIPT_MUTATED: false")
print("PHYSICAL_CLAIM: false")
