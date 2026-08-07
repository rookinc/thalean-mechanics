#!/usr/bin/env python3
import hashlib
import json
import math
import subprocess
from pathlib import Path

project = Path(__file__).resolve().parents[2]
json_path = project / "artifacts/json/g60_native_d8_outer_c2_selector_census_011y.v1.json"
raw_path = project / "artifacts/receipts/g60_native_d8_outer_c2_selector_census_011y_raw_run.txt"
note_path = project / "notes/g60_native_d8_outer_c2_selector_census_011y.md"
compute_path = project / "scripts/audits/compute_g60_native_d8_outer_c2_selector_census_011y.py"

EXPECTED_JSON = "d5a9036cf96aa97dd8848cd947bff4d07c711db0db2e3dca3ad13ec1c9cdfdab"
EXPECTED_RAW = "4ceed9abb77444fea6af5fb60e2e47a2d8832af0d9dc5a1c6b2dc3610fd6f0a9"
EXPECTED_NOTE = "d44a51547334f9a192354ede6f78e07e7c2ad9ff6f215cbc026978f0cfb9e927"
EXPECTED_COMPUTE = "c3753ebc61d8f81c70f39454fa630d28a225d192d49e3309a30ca22f0b52230a"
EXPECTED_CANDIDATE = "a5b4fe24225705b8fd75b9c02eefd801e3bfb1455ebc1a9f7b072c771ed7a8e9"
EXPECTED_GUARD_SCRIPT = "a87ca600ba9762f50e6315f91e2e3b1f8f49a427de93d0df0a8b9b770637259d"
EXPECTED_GUARD_REPORT = "e951183c4451537d24429d766f74c0acf107583dd5141b8e2f62b2f58148b594"
EXPECTED_FAILED_SCRIPT = "f1d8a8ebb77be0ce0f7441795d78bc71b5496a2c6d42d65375f87db1e78b3dbc"
EXPECTED_FAILED_JSON = "6d3c3dfc03249a5c971ca495d8ae5a315c1f496bd56f5c43990e65266ba6dffd"
EXPECTED_FAILED_REPORT = "a9429754429e041a7ec54208a54670bf91b23e45c4d9128d51981919551a3d38"

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

def permutation_order(mapping):
    seen = set()
    result = 1
    for start in range(len(mapping)):
        if start in seen:
            continue
        current = start
        length = 0
        while current not in seen:
            seen.add(current)
            current = mapping[current]
            length += 1
        if length:
            result = math.lcm(result, length)
    return result

data = json.loads(json_path.read_text(encoding="utf-8"))
local = data["local_automorphism_census"]
native = data["native_chart_action_reconstruction"]
extensions = data["outer_involution_extensions"]
selector = data["selector_result"]
observables = data["locked_observable_comparison"]
gauge = data["presentation_gauge_torsor_comparison"]
promotion = data["promotion"]
boundary = data["boundary"]

checks = []
def check(name, value):
    checks.append((name, bool(value)))

check("packet", data["packet"] ==
      "g60_native_d8_outer_c2_selector_census_011y")
check("mode", data["mode"] ==
      "frozen_complete_native_D8_outer_C2_selector_census")
check("locked_head", data["locked_head"] ==
      "fe5a31e Correct G60 outer-C2 selector preregistration")
check("current_head", git("show", "-s", "--format=%h %s", "HEAD") ==
      data["locked_head"])
check("result_frozen", data["result_frozen"] is True)
check("audit_pass_recorded", data["audit_pass"] is True)
check("json_hash", sha256_file(json_path) == EXPECTED_JSON)
check("raw_hash", sha256_file(raw_path) == EXPECTED_RAW)
check("note_hash", sha256_file(note_path) == EXPECTED_NOTE)
check("compute_hash", sha256_file(compute_path) == EXPECTED_COMPUTE)
check("candidate_hash", promotion["candidate_sha256"] == EXPECTED_CANDIDATE)
check("guard_script_hash",
      promotion["promotion_guard_script_sha256"] == EXPECTED_GUARD_SCRIPT)
check("guard_report_hash",
      promotion["promotion_guard_report_sha256"] == EXPECTED_GUARD_REPORT)
check("failed_script_hash",
      promotion["failed_run"]["script_sha256"] == EXPECTED_FAILED_SCRIPT)
check("failed_json_hash",
      promotion["failed_run"]["candidate_json_sha256"] == EXPECTED_FAILED_JSON)
check("failed_report_hash",
      promotion["failed_run"]["raw_report_sha256"] == EXPECTED_FAILED_REPORT)
check("candidate_promoted",
      promotion["candidate_promoted_without_recomputation"] is True)
check("raw_copied",
      promotion["raw_receipt_copied_without_recomputation"] is True)
check("compute_copied",
      promotion["compute_script_copied_without_recomputation"] is True)
check("guard_passed", promotion["promotion_guard_passed"] is True)
check("failure_preserved",
      promotion["effective_vs_abstract_failure_preserved"] is True)
check("failure_not_promoted", promotion["failed_run_promoted"] is False)
check("semantic_correction",
      promotion["abstract_effective_semantic_correction_applied"] is True)
check("promotion_no_manuscript", promotion["manuscript_mutated"] is False)
check("authority_count", len(data["authorities"]) == 5)
check("authority_hashes", all(
    Path(path).is_file()
    and row["hash_match"] is True
    and sha256_file(Path(path)) ==
        row["expected_sha256"] ==
        row["sha256"]
    for path, row in data["authorities"].items()
))
check("presentations_two", local["presentation_count"] == 2)
check("eight_automorphisms_each", all(
    len(rows) == 8
    for rows in local["automorphism_rows_by_presentation"]
))
check("mapping_orders", all(
    permutation_order(tuple(row["mapping"])) == row["order"]
    for rows in local["automorphism_rows_by_presentation"]
    for row in rows
))
check("aut_profiles", all(
    row["automorphism_order_profile"] ==
        {"1": 1, "2": 5, "4": 2}
    for row in local["presentation_rows"]
))
check("inner_profiles", all(
    row["inner_automorphism_order_profile"] ==
        {"1": 1, "2": 3}
    for row in local["presentation_rows"]
))
check("outer_profiles", all(
    row["outer_coset_order_profile"] ==
        {"2": 2, "4": 2}
    for row in local["presentation_rows"]
))
check("outer_involutions_two", all(
    row["outer_involution_count"] == 2
    for row in local["presentation_rows"]
))
check("outer_order4_two", all(
    row["outer_order_four_count"] == 2
    for row in local["presentation_rows"]
))
check("inner_preserves", all(
    row["all_inner_preserve_global_orbits"]
    and row["all_inner_preserve_fiber_orbits"]
    for row in local["presentation_rows"]
))
check("outer_exchanges", all(
    row["all_outer_exchange_global_orbits"]
    and row["all_outer_exchange_fiber_orbits"]
    for row in local["presentation_rows"]
))
check("fiber_failures_zero", all(
    row["fiber_failure_count"] == 0
    for row in local["presentation_rows"]
))
check("abstract_native_480",
      native["abstract_full_group_order"] == 480)
check("effective_native_240",
      native["effective_action_image_orders"] == [240, 240])
check("native_kernel_two",
      native["action_kernel_orders"] == [2, 2])
check("native_kernel_indices",
      native["action_kernel_indices_by_presentation"] ==
      [[0, 326], [0, 326]])
check("native_kernel_names",
      native["action_kernel_names"] == ["1", "a"])
check("native_action_valid",
      native["action_failure_counts"] == [0, 0])
check("native_orbits",
      native["orbit_profiles"] == [[40, 40], [40, 40]])
check("extension_rows_four", extensions["row_count"] == 4)
check("abstract_extensions_960", all(
    row["abstract_extended_group_order"] == 960
    for row in extensions["rows"]
))
check("effective_extensions_480", all(
    row["effective_extended_action_image_order"] == 480
    for row in extensions["rows"]
))
check("extension_kernel_two", all(
    row["extended_action_kernel_order"] == 2
    for row in extensions["rows"]
))
check("extension_commutes", all(
    row["commutation_failure_count"] == 0
    for row in extensions["rows"]
))
check("extension_orbits_80", all(
    row["extended_orbit_profile"] == [80]
    for row in extensions["rows"]
))
check("effective_stabilizers_6", all(
    row["effective_extended_stabilizer_order_profile"] ==
        {"6": 80}
    for row in extensions["rows"]
))
check("abstract_stabilizers_12", all(
    row["abstract_extended_stabilizer_order_profile"] ==
        {"12": 80}
    for row in extensions["rows"]
))
check("order4_rows_four",
      len(extensions["order_four_measurements_not_preregistered"]) == 4)
check("order4_abstract_1920", all(
    row["measured_abstract_generated_group_order"] == 1920
    for row in extensions["order_four_measurements_not_preregistered"]
))
check("order4_effective_960", all(
    row["measured_effective_action_image_order"] == 960
    for row in extensions["order_four_measurements_not_preregistered"]
))
check("alpha_constant",
      observables["alpha_1_constant_under_outer_exchange"] is True)
check("q_constant",
      observables["q_axis_signature_constant_under_outer_exchange"] is True)
check("gauge_maps_four", gauge["gauge_map_count"] == 4)
check("gauge_equivalent",
      gauge["gauge_related_presentations_have_equivalent_outer_C2_torsors"]
      is True)
check("full_A_choices_two",
      selector["full_A_invariant_single_orbit_choice_count"] == 2)
check("outer_selector_zero",
      selector["outer_gauge_invariant_single_orbit_selector_count"] == 0)
check("torsor_two", selector["minimal_extra_torsor_cardinality"] == 2)
check("binary_one", selector["minimal_extra_binary_choice_count"] == 1)
check("bounded_necessity",
      selector["bounded_model_necessity_established"] is True)
check("no_absolute_orbit", selector["absolute_orbit_selected"] is False)
check("prediction_matches", data["prediction_matches"] is True)
check("classification", data["classification"] ==
      "native_D8_chart_orbit_selection_requires_one_external_outer_C2_torsor_choice")
check("repository_preserved", data["repository"]["status_preserved"] is True)
check("candidate_no_project_mutation",
      data["repository"]["project_mutation_performed"] is False)
check("earned_statement", bool(data["earned_statement"]))
check("bounded_boundary",
      boundary["bounded_native_D8_chart_model_only"] is True)
check("census_performed",
      boundary["outer_selector_census_performed"] is True)
check("outer_exchange_verified",
      boundary["outer_C2_exchange_verified"] is True)
check("bounded_binary_necessity",
      boundary["extra_binary_datum_proved_necessary_within_bounded_model"]
      is True)
check("no_global_minimality",
      boundary["global_minimality_claim"] is False)
check("no_chart_selected",
      boundary["absolute_chart_orbit_selected"] is False)
check("no_update", boundary["native_update_law_constructed"] is False)
check("no_cell", boundary["mechanics_state_cell_established"] is False)
check("no_side_identity",
      boundary["local_side_equals_011o_orientation_sheet"] is False)
check("no_orientation", boundary["orientation_selected"] is False)
check("no_manuscript", boundary["manuscript_mutated"] is False)
check("no_geometry", boundary["geometry_claim"] is False)
check("no_direction", boundary["physical_direction_claim"] is False)
check("no_physics", boundary["physical_claim"] is False)
check("note_exists", note_path.is_file())

failed = [name for name, passed in checks if not passed]

print("== G60 NATIVE D8 OUTER-C2 SELECTOR CENSUS AUDIT 011y ==")
print("PACKET:", data["packet"])
print("MODE:", data["mode"])
print("JSON_SHA256:", sha256_file(json_path))
print("NOTE_SHA256:", sha256_file(note_path))
print("COMPUTATION_SCRIPT_SHA256:", sha256_file(compute_path))
print("RAW_RUN_RECEIPT_SHA256:", sha256_file(raw_path))
print("AUTOMORPHISM_ORDER_PROFILES:",
      [row["automorphism_order_profile"]
       for row in local["presentation_rows"]])
print("FULL_A_ABSTRACT_GROUP_ORDER:",
      native["abstract_full_group_order"])
print("FULL_A_EFFECTIVE_IMAGE_ORDERS:",
      native["effective_action_image_orders"])
print("FULL_A_ACTION_KERNEL_INDICES:",
      native["action_kernel_indices_by_presentation"])
print("OUTER_INVOLUTION_ABSTRACT_GROUP_ORDERS:",
      [row["abstract_extended_group_order"]
       for row in extensions["rows"]])
print("OUTER_INVOLUTION_EFFECTIVE_IMAGE_ORDERS:",
      [row["effective_extended_action_image_order"]
       for row in extensions["rows"]])
print("OUTER_GAUGE_INVARIANT_SELECTOR_COUNT:",
      selector["outer_gauge_invariant_single_orbit_selector_count"])
print("MINIMAL_EXTRA_TORSOR_CARDINALITY:",
      selector["minimal_extra_torsor_cardinality"])
print("CLASSIFICATION:", data["classification"])
print("CHECK_COUNT:", len(checks))
print("FAILED_CHECK_COUNT:", len(failed))
for name, passed in checks:
    print("CHECK", name + ":", str(passed).lower())
print("AUDIT_PASS:", str(not failed).lower())
print("FAILED_CHECKS:", failed)
print("EARNED_STATEMENT:", data["earned_statement"])
print("EXTRA_BINARY_DATUM_PROVED_NECESSARY_WITHIN_BOUNDED_MODEL: true")
print("ABSOLUTE_CHART_ORBIT_SELECTED: false")
print("NATIVE_UPDATE_LAW_CONSTRUCTED: false")
print("MECHANICS_STATE_CELL_ESTABLISHED: false")
print("MANUSCRIPT_MUTATED: false")
print("PHYSICAL_CLAIM: false")
