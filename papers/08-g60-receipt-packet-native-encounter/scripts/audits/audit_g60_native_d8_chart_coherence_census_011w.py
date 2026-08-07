#!/usr/bin/env python3
import hashlib
import json
import subprocess
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
JSON_PATH = PROJECT / "artifacts/json/g60_native_d8_chart_coherence_census_011w.v1.json"
RAW_PATH = PROJECT / "artifacts/receipts/g60_native_d8_chart_coherence_census_011w_raw_run.txt"
NOTE_PATH = PROJECT / "notes/g60_native_d8_chart_coherence_census_011w.md"
COMPUTE_PATH = PROJECT / "scripts/audits/compute_g60_native_d8_chart_coherence_census_011w.py"

EXPECTED_JSON_HASH = "e5630a02b4e4c28caac017906aebae10b00c5b1a8e1ccdf640a414c1174f6919"
EXPECTED_RAW_HASH = "8cabab601fd45b9f66dd16c0cc95ecfedb9c277c21e9fb55e5589624ca2d1d05"
EXPECTED_NOTE_HASH = "729e331ff35563fd710dd1cbd55346ee72b6045ad529fc39b528a02aef35e0b8"
EXPECTED_COMPUTE_HASH = "329824bc477fff56531f232da711638bce048967b77d04b80bf94b48c83dab13"
EXPECTED_CANDIDATE_HASH = "0491603f8f7fe82d79309e32ecabdbae0eff4b10aca8a8dd37aa76de8990ec3f"
EXPECTED_GUARD_HASH = "a720d6eacca49c8307a488d09a0c1477334df2f87e2d94191936fecd6c111d2f"
LOCKED_HEAD = "f43e86b Preregister G60 native D8 chart coherence test"

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
charts = data["chart_reconstruction"]
base = data["base_action"]
action = data["chart_action"]
normalizers = data["normalizer_fiber_action"]
gauge = data["gauge_presentation_comparison"]
invariants = data["locked_invariant_comparison"]
prediction = data["prediction_comparison"]
promotion = data["promotion"]
provenance = data["candidate_provenance"]
boundary = data["boundary"]
repository = data["repository"]

chart_rows = charts["chart_rows"]
orbit_rows = action["orbit_rows_by_presentation"]
normalizer_rows = normalizers["rows_by_presentation"]
gauge_rows = gauge["gauge_rows"]

head = git("show", "-s", "--format=%h %s", "HEAD")

all_chart_rows_exact = all(
    len(chart["images"]) == 8
    and len(set(chart["images"])) == 8
    and chart["subgroup_index"] in range(10)
    for presentation in chart_rows
    for chart in presentation["charts"]
)

all_orbit_rows_exact = all(
    row["orbit_size"] == 40
    and len(row["chart_indices"]) == 40
    and row["base_subgroup_count"] == 10
    and row["base_multiplicity_profile"] == {"4": 10}
    and row["is_strict_equivariant_section"] is False
    and row["alpha_1_character"] == {
        "1": 0, "a": 0, "ab": 1, "b": 1
    }
    and row["q_axis_signature"] == {
        "a": 1, "ab": 0, "b": 0
    }
    for rows in orbit_rows
    for row in rows
)

all_normalizer_rows_exact = all(
    row["normalizer_order"] == 48
    and row["fiber_size"] == 8
    and row["normalizer_fiber_image_order"] == 4
    and row["inner_fiber_image_order"] == 4
    and row["normalizer_image_equals_inner_image"] is True
    and row["fiber_orbit_count"] == 2
    and row["fiber_orbit_size_profile"] == [4, 4]
    and row["chart_stabilizer_order_profile"] == {"12": 8}
    for rows in normalizer_rows
    for row in rows
)

all_gauge_rows_exact = all(
    row["induced_chart_bijection_is_permutation"] is True
    and row["intertwining_failure_count"] == 0
    and len(row["orbit_map"]) == 2
    and all(
        len(orbit["target_orbit_indices"]) == 1
        for orbit in row["orbit_map"]
    )
    for row in gauge_rows
)

checks = [
    ("packet", data.get("packet") == "g60_native_d8_chart_coherence_census_011w"),
    ("mode", data.get("mode") == "frozen_complete_native_D8_chart_coherence_census"),
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
    ("guard_passed", promotion.get("promotion_guard_passed") is True),
    ("path_failures_not_promoted", promotion.get("path_invocation_failures_promoted") is False),
    ("promotion_no_manuscript", promotion.get("manuscript_mutated") is False),
    ("authority_count", len(data.get("authorities", {})) == 7),
    ("authority_hashes", all(row.get("hash_match") is True for row in data["authorities"].values())),
    ("group_480", group.get("group_order") == 480),
    ("identity_0", group.get("identity_index") == 0),
    ("native_indices", group.get("native_V4_indices") == {"1": 0, "a": 326, "ab": 65, "b": 124}),
    ("subgroups_10", group.get("native_D8_subgroup_count") == 10),
    ("subgroup_rows_10", len(group.get("native_D8_subgroups", [])) == 10),
    ("presentations_2", charts.get("presentation_count") == 2),
    ("presentation_rows_2", len(charts.get("presentation_rows", [])) == 2),
    ("chart_counts", charts.get("chart_counts") == [80, 80]),
    ("total_charts_160", charts.get("total_chart_count") == 160),
    ("chart_groups_2", len(chart_rows) == 2),
    ("chart_rows_80_each", [len(row["charts"]) for row in chart_rows] == [80, 80]),
    ("chart_rows_exact", all_chart_rows_exact),
    ("base_failures_zero", base.get("action_failure_count") == 0),
    ("base_orbit_one", base.get("orbit_count") == 1),
    ("base_orbit_size_10", base.get("orbit_size_profile") == [10]),
    ("base_stabilizers_48", base.get("stabilizer_order_profile") == {"48": 10}),
    ("action_failures_zero", action.get("action_failure_counts") == [0, 0]),
    ("identity_failures_zero", action.get("identity_failure_counts") == [0, 0]),
    ("closure_failures_zero", action.get("closure_failure_counts") == [0, 0]),
    ("orbit_profiles", action.get("orbit_profiles") == [[40, 40], [40, 40]]),
    ("combined_orbits", action.get("combined_orbit_profile") == [40, 40, 40, 40]),
    ("orbit_row_groups_2", [len(rows) for rows in orbit_rows] == [2, 2]),
    ("orbit_rows_exact", all_orbit_rows_exact),
    ("section_counts_zero", action.get("strict_equivariant_section_counts") == [0, 0]),
    ("no_strict_section", action.get("strict_equivariant_chart_selection_exists") is False),
    ("normalizer_groups", [len(rows) for rows in normalizer_rows] == [10, 10]),
    ("normalizer_rows_exact", all_normalizer_rows_exact),
    ("all_normalizers_48", normalizers.get("all_normalizers_order_48") is True),
    ("all_stabilizers_12", normalizers.get("all_chart_stabilizers_order_12") is True),
    ("all_fiber_images_4", normalizers.get("all_fiber_images_order_4") is True),
    ("all_fiber_profiles", normalizers.get("all_fiber_orbit_profiles_4_4") is True),
    ("all_images_inner", normalizers.get("all_normalizer_images_equal_inner_images") is True),
    ("outer_C2", normalizers.get("residual_outer_gauge_group") == "C2"),
    ("gauge_count_4", gauge.get("gauge_isomorphism_count") == 4),
    ("gauge_rows_4", len(gauge_rows) == 4),
    ("gauge_rows_exact", all_gauge_rows_exact),
    ("gauge_equivalent", gauge.get("bundles_equivalent") is True),
    ("alpha_constant", invariants.get("alpha_1_character_constant_across_all_chart_orbits") is True),
    ("alpha_character", invariants.get("alpha_1_character") == {"1": 0, "a": 0, "ab": 1, "b": 1}),
    ("q_constant", invariants.get("q_axis_signature_constant_across_all_chart_orbits") is True),
    ("q_signature", invariants.get("q_axis_signature") == {"a": 1, "ab": 0, "b": 0}),
    ("no_outer_selection", invariants.get("locked_character_data_selects_one_outer_orbit") is False),
    ("prediction_matches", prediction.get("prediction_matches") is True),
    ("classification", data.get("classification") == "native_D8_chart_bundle_has_exact_outer_C2_obstruction_to_equivariant_section"),
    ("bundle_classified", boundary.get("gauge_covariant_bundle_classified") is True),
    ("orbit_census", boundary.get("chart_orbit_census_performed") is True),
    ("section_test", boundary.get("equivariant_section_test_performed") is True),
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
    ("repository_preserved", repository.get("status_preserved") is True),
    ("candidate_no_project_mutation", repository.get("project_mutation_performed") is False),
    ("earned_statement", isinstance(data.get("earned_statement"), str) and len(data["earned_statement"]) > 300),
    ("note_exists", NOTE_PATH.is_file()),
]

failed = [name for name, passed in checks if not passed]

print("== G60 NATIVE D8 CHART-COHERENCE CENSUS AUDIT 011w ==")
print("PACKET:", data.get("packet"))
print("MODE:", data.get("mode"))
print("JSON_SHA256:", sha256_file(JSON_PATH))
print("NOTE_SHA256:", sha256_file(NOTE_PATH))
print("COMPUTATION_SCRIPT_SHA256:", sha256_file(COMPUTE_PATH))
print("RAW_RUN_RECEIPT_SHA256:", sha256_file(RAW_PATH))
print("BASE_ORBIT_SIZE_PROFILE:", base.get("orbit_size_profile"))
print("BASE_STABILIZER_ORDER_PROFILE:", base.get("stabilizer_order_profile"))
print("CHART_ORBIT_PROFILES:", action.get("orbit_profiles"))
print("STRICT_EQUIVARIANT_SECTION_COUNTS:", action.get("strict_equivariant_section_counts"))
print("GAUGE_ISOMORPHISM_COUNT:", gauge.get("gauge_isomorphism_count"))
print("RESIDUAL_OUTER_GAUGE_GROUP:", normalizers.get("residual_outer_gauge_group"))
print("CLASSIFICATION:", data.get("classification"))
print("CHECK_COUNT:", len(checks))
print("FAILED_CHECK_COUNT:", len(failed))

for name, passed in checks:
    print("CHECK", name + ":", str(bool(passed)).lower())

print("AUDIT_PASS:", str(not failed).lower())
print("FAILED_CHECKS:", failed)
print("EARNED_STATEMENT:", data.get("earned_statement"))
print("GAUGE_COVARIANT_BUNDLE_CLASSIFIED:", str(boundary.get("gauge_covariant_bundle_classified")).lower())
print("STRICT_EQUIVARIANT_CHART_SELECTED:", str(boundary.get("strict_equivariant_chart_selected")).lower())
print("NATIVE_UPDATE_LAW_CONSTRUCTED:", str(boundary.get("native_update_law_constructed")).lower())
print("MECHANICS_STATE_CELL_ESTABLISHED:", str(boundary.get("mechanics_state_cell_established")).lower())
print("MANUSCRIPT_MUTATED:", str(boundary.get("manuscript_mutated")).lower())
print("PHYSICAL_CLAIM:", str(boundary.get("physical_claim")).lower())

if failed:
    raise SystemExit(1)
