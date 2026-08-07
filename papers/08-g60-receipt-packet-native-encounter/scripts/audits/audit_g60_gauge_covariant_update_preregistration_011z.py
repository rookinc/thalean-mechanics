#!/usr/bin/env python3

import hashlib
import json
import pathlib
import subprocess

project = pathlib.Path(__file__).resolve().parents[2]
json_path = project / "artifacts/json/g60_gauge_covariant_update_preregistration_011z.v1.json"
note_path = project / "notes/g60_gauge_covariant_update_preregistration_011z.md"

EXPECTED_JSON_HASH = "63b669fcbd75d29bc6e81fa624e427da91d9eb9013d881e7e511889c648e17f4"
EXPECTED_NOTE_HASH = "9cdb713446a37bf9b654964dec8f1c932105cf59ab4ec2623a612cb5a6d64b63"
LOCKED_HEAD = "f3ee198 Lock G60 outer-C2 chart selector obstruction"

def sha256_file(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def git_head():
    return subprocess.check_output(
        ["git", "--no-pager", "show", "-s", "--format=%h %s", "HEAD"],
        cwd=project,
        text=True,
    ).strip()

with json_path.open() as handle:
    data = json.load(handle)

pred = data["predictions"]
bound = data["boundary"]

checks = [
    ("packet", data["packet"] == "g60_gauge_covariant_update_preregistration_011z"),
    ("mode", data["mode"] == "post_outer_C2_obstruction_gauge_covariant_update_preregistration"),
    ("status", data["status"] == "preregistered_before_update_census"),
    ("locked_head", data["locked_head"] == LOCKED_HEAD),
    ("current_head", git_head() == LOCKED_HEAD),
    ("json_hash", sha256_file(json_path) == EXPECTED_JSON_HASH),
    ("note_hash", sha256_file(note_path) == EXPECTED_NOTE_HASH),
    ("authority_count", len(data["authorities"]) == 6),
    ("authority_hashes", all(
        row["hash_match"]
        and sha256_file(pathlib.Path(path)) == row["expected_sha256"]
        and row["sha256"] == row["expected_sha256"]
        for path, row in data["authorities"].items()
    )),
    ("presentations_2", pred["presentation_count"] == 2),
    ("subgroups_10", pred["native_D8_subgroup_count"] == 10),
    ("charts_per_subgroup_8", pred["chart_count_per_subgroup"] == 8),
    ("charts_per_presentation_80", pred["chart_count_per_presentation"] == 80),
    ("states_8", pred["local_state_count"] == 8),
    ("instructions_8", pred["local_instruction_count"] == 8),
    ("local_rows_64", pred["local_update_row_count_per_chart"] == 64),
    ("decorated_subgroup_512", pred["chart_decorated_update_row_count_per_subgroup"] == 512),
    ("decorated_presentation_5120", pred["chart_decorated_update_row_count_per_presentation"] == 5120),
    ("decorated_total_10240", pred["chart_decorated_update_row_count_both_presentations"] == 10240),
    ("aut_order_8", pred["automorphism_group_order"] == 8),
    ("element_orbits", pred["local_element_orbit_size_profile"] == [1, 1, 2, 4]),
    ("q_candidates_2", pred["q_axis_order_four_instruction_candidate_count"] == 2),
    ("q_invariant_zero", pred["Aut_D8_invariant_q_axis_order_four_singleton_count"] == 0),
    ("free_action", pred["gauge_action_free_on_chart_decorated_rows"] is True),
    ("quotient_subgroup_64", pred["gauge_orbit_count_per_subgroup"] == 64),
    ("quotient_presentation_640", pred["gauge_orbit_count_per_presentation"] == 640),
    ("quotient_total_1280", pred["gauge_orbit_count_both_presentations"] == 1280),
    ("native_subgroup_64", pred["native_multiplication_row_count_per_subgroup"] == 64),
    ("native_presentation_640", pred["native_multiplication_row_count_per_presentation"] == 640),
    ("descent_well_defined", pred["quotient_evaluation_well_defined"] is True),
    ("descent_bijective", pred["quotient_evaluation_bijective"] is True),
    ("presentations_equal", pred["presentation_quotient_relations_equal"] is True),
    ("gauge_maps_4", pred["presentation_gauge_intertwiner_count"] == 4),
    ("gauge_intertwines", pred["all_presentation_gauge_maps_intertwine_update"] is True),
    ("covariant_constructible", pred["gauge_covariant_instruction_parametrized_update_constructible"] is True),
    ("no_autonomous_instruction", pred["autonomous_noncentral_instruction_selected"] is False),
    ("no_absolute_chart", pred["absolute_chart_selected"] is False),
    ("no_unary_law", pred["native_unary_evolution_law_constructed"] is False),
    ("classification", pred["predicted_classification"] == "gauge_covariant_instruction_parametrized_D8_update_descends_without_autonomous_instruction_selection"),
    ("required_tests_20", len(data["required_tests"]) == 20),
    ("falsifiers_9", len(data["falsifiers"]) == 9),
    ("finite_test", bound["finite_instruction_parametrized_update_test_only"] is True),
    ("no_census", bound["update_census_performed"] is False),
    ("no_aut_recompute", bound["local_automorphism_action_recomputed"] is False),
    ("no_update_rows", bound["chart_decorated_update_rows_enumerated"] is False),
    ("no_quotient", bound["gauge_quotient_computed"] is False),
    ("no_constructed_update", bound["gauge_covariant_instruction_parametrized_update_constructed"] is False),
    ("no_autonomous_native_instruction", bound["autonomous_native_update_instruction_selected"] is False),
    ("no_native_update_law", bound["native_update_law_constructed"] is False),
    ("no_absolute_orbit", bound["absolute_chart_orbit_selected"] is False),
    ("no_strict_chart", bound["strict_equivariant_chart_selected"] is False),
    ("no_torsor_identification", bound["order_four_instruction_pair_identified_with_outer_C2_torsor"] is False),
    ("no_cell", bound["mechanics_state_cell_established"] is False),
    ("no_side_identity", bound["local_side_equals_011o_orientation_sheet"] is False),
    ("no_orientation", bound["orientation_selected"] is False),
    ("no_global_minimality", bound["global_minimality_claim"] is False),
    ("no_manuscript", bound["manuscript_mutated"] is False),
    ("no_geometry", bound["geometry_claim"] is False),
    ("no_direction", bound["physical_direction_claim"] is False),
    ("no_physics", bound["physical_claim"] is False),
    ("note_exists", note_path.is_file()),
]

failed = [name for name, passed in checks if not passed]

print("== G60 GAUGE-COVARIANT UPDATE PREREGISTRATION AUDIT 011z ==")
print("PACKET:", data["packet"])
print("MODE:", data["mode"])
print("JSON_SHA256:", sha256_file(json_path))
print("NOTE_SHA256:", sha256_file(note_path))
print("LOCKED_HEAD:", LOCKED_HEAD)
print("PREDICTED_DECORATED_ROWS_PER_PRESENTATION:",
      pred["chart_decorated_update_row_count_per_presentation"])
print("PREDICTED_GAUGE_ORBITS_PER_PRESENTATION:",
      pred["gauge_orbit_count_per_presentation"])
print("PREDICTED_LOCAL_ELEMENT_ORBITS:",
      pred["local_element_orbit_size_profile"])
print("PREDICTED_Q_AXIS_ORDER4_CANDIDATES:",
      pred["q_axis_order_four_instruction_candidate_count"])
print("PREDICTED_CLASSIFICATION:",
      pred["predicted_classification"])
print("UPDATE_CENSUS_PERFORMED:",
      str(bound["update_census_performed"]).lower())
print("CHECK_COUNT:", len(checks))
print("FAILED_CHECK_COUNT:", len(failed))
for name, passed in checks:
    print("CHECK", name + ":", str(passed).lower())
print("PREREGISTRATION_PASS:", str(not failed).lower())
print("FAILED_CHECKS:", failed)
print("GAUGE_COVARIANT_INSTRUCTION_PARAMETRIZED_UPDATE_CONSTRUCTED: false")
print("AUTONOMOUS_NATIVE_UPDATE_INSTRUCTION_SELECTED: false")
print("NATIVE_UPDATE_LAW_CONSTRUCTED: false")
print("MECHANICS_STATE_CELL_ESTABLISHED: false")
print("MANUSCRIPT_MUTATED: false")
print("PHYSICAL_CLAIM: false")

if failed:
    raise SystemExit(1)
