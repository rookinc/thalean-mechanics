#!/usr/bin/env python3

import hashlib
import json
import pathlib
import subprocess
from collections import Counter

project = pathlib.Path(__file__).resolve().parents[2]

json_path = project / "artifacts/json/g60_gauge_covariant_update_census_012a.v1.json"
raw_path = project / "artifacts/receipts/g60_gauge_covariant_update_census_012a_raw_run.txt"
note_path = project / "notes/g60_gauge_covariant_update_census_012a.md"
compute_path = project / "scripts/audits/compute_g60_gauge_covariant_update_census_012a.py"

EXPECTED_JSON_HASH = "4e6936b9b48c6f033b826df7c3ad4ac70ec3480129c5c73ec6a24630077096d2"
EXPECTED_RAW_HASH = "6090c7e61e616931af20fa55ed1a03ac5cb63c1203f095c14a95a177694b5a22"
EXPECTED_NOTE_HASH = "c7d7f620ae67ffb646b9ef717a7915d0b36dd2451e625eddc94897efbdb84f20"
EXPECTED_COMPUTE_HASH = "9f1b83513933001f5dd2abdfac48351d8d8093cf70fa795cf6c124e8409ef034"
EXPECTED_CANDIDATE_HASH = "d8aadf42cba3669498fd5076b86285a1c65b7d9200a1448750e4fc6db6440761"
EXPECTED_GUARD_SCRIPT_HASH = "ff827015e9c0ae54d31c34b366d61fc5522c7c64454a39d8eaacb3d735a5aa94"
EXPECTED_GUARD_REPORT_HASH = "d6b0b474ad8cf41ab93b48201b9dd04e54eedd8af42101c2df20c7d739a5cae2"
LOCKED_HEAD = "8fe832f Preregister G60 gauge-covariant update descent"

def sha256_file(path):
    h = hashlib.sha256()
    with pathlib.Path(path).open("rb") as handle:
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

descent = data["chart_decorated_update_descent"]
summaries = descent["presentation_summaries"]
quotient_groups = descent["quotient_rows_by_presentation"]
local_rows = data["local_reconstruction"]["presentation_rows"]
gauge = data["presentation_gauge_comparison"]
selector = data["selector_boundary"]
boundary = data["boundary"]
promotion = data["promotion"]
provenance = data["candidate_provenance"]
prediction = data["preregistration_comparison"]

subgroup_profiles = []
duplicate_counts = []
native_product_failure_counts = []

native_action_path = next(
    pathlib.Path(path)
    for path in data["authorities"]
    if path.endswith("native_g60_fiber_product_isomorphism_044.json")
)

with native_action_path.open() as handle:
    native = json.load(handle)

mapping_rows = sorted(
    native["mapping_rows"],
    key=lambda row: int(row["actual_index"]),
)
permutations = [
    tuple(int(x) for x in row["actual_permutation"])
    for row in mapping_rows
]
lookup = {
    permutation: index
    for index, permutation in enumerate(permutations)
}

def compose(left, right):
    return tuple(
        left[right[index]]
        for index in range(len(left))
    )

def multiply(left, right):
    return lookup[compose(permutations[left], permutations[right])]

for rows in quotient_groups:
    subgroup_counts = Counter(
        int(row["subgroup_index"])
        for row in rows
    )
    subgroup_profiles.append(
        dict(sorted(Counter(subgroup_counts.values()).items()))
    )

    relation = [
        (
            int(row["subgroup_index"]),
            int(row["native_state_index"]),
            int(row["native_instruction_index"]),
            int(row["native_next_state_index"]),
        )
        for row in rows
    ]
    duplicate_counts.append(len(relation) - len(set(relation)))
    native_product_failure_counts.append(sum(
        multiply(state, instruction) != next_state
        for _, state, instruction, next_state in relation
    ))

checks = [
    ("packet", data["packet"] == "g60_gauge_covariant_update_census_012a"),
    ("mode", data["mode"] == "frozen_complete_gauge_covariant_update_descent_census"),
    ("locked_head", data["locked_head"] == LOCKED_HEAD),
    ("current_head", git_head() == LOCKED_HEAD),
    ("result_frozen", data["result_frozen"] is True),
    ("audit_pass_recorded", data["audit_pass"] is True),
    ("json_hash", sha256_file(json_path) == EXPECTED_JSON_HASH),
    ("raw_hash", sha256_file(raw_path) == EXPECTED_RAW_HASH),
    ("note_hash", sha256_file(note_path) == EXPECTED_NOTE_HASH),
    ("compute_hash", sha256_file(compute_path) == EXPECTED_COMPUTE_HASH),
    ("candidate_hash", provenance["candidate_json_sha256"] == EXPECTED_CANDIDATE_HASH),
    ("guard_script_hash", provenance["promotion_guard_script_sha256"] == EXPECTED_GUARD_SCRIPT_HASH),
    ("guard_report_hash", provenance["promotion_guard_report_sha256"] == EXPECTED_GUARD_REPORT_HASH),
    ("candidate_promoted", promotion["candidate_promoted_without_recomputation"] is True),
    ("guard_passed", promotion["promotion_guard_passed"] is True),
    ("candidate_no_mutation", promotion["candidate_project_mutation_performed"] is False),
    ("promotion_no_manuscript", promotion["manuscript_mutated"] is False),
    ("authority_count", len(data["authorities"]) == 4),
    ("authority_hashes", all(
        row["hash_match"]
        and sha256_file(pathlib.Path(path)) == row["expected_sha256"]
        and row["sha256"] == row["expected_sha256"]
        for path, row in data["authorities"].items()
    )),
    ("native_group_480", len(mapping_rows) == 480),
    ("native_indices", [int(row["actual_index"]) for row in mapping_rows] == list(range(480))),
    ("identity_0", lookup.get(tuple(range(60))) == 0),
    ("presentations_2", len(local_rows) == 2),
    ("charts_80", [row["chart_count"] for row in local_rows] == [80, 80]),
    ("chart_failures_zero", [row["chart_homomorphism_failure_count"] for row in local_rows] == [0, 0]),
    ("automorphisms_8", [row["automorphism_count"] for row in local_rows] == [8, 8]),
    ("aut_profiles", [row["automorphism_order_profile"] for row in local_rows] == [{"1": 1, "2": 5, "4": 2}, {"1": 1, "2": 5, "4": 2}]),
    ("element_profiles", [row["element_order_profile"] for row in local_rows] == [{"1": 1, "2": 5, "4": 2}, {"1": 1, "2": 5, "4": 2}]),
    ("element_orbits", [row["element_orbit_size_profile"] for row in local_rows] == [[1, 1, 2, 4], [1, 1, 2, 4]]),
    ("order4_elements", [row["order_four_elements"] for row in local_rows] == [[2, 3], [2, 3]]),
    ("order4_invariant_zero", [row["Aut_D8_invariant_order_four_singletons"] for row in local_rows] == [[], []]),
    ("decorated_rows_10240", descent["decorated_update_row_count_both_presentations"] == 10240),
    ("quotient_orbits_1280", descent["gauge_orbit_count_both_presentations"] == 1280),
    ("quotient_groups_2", len(quotient_groups) == 2),
    ("quotient_rows_640", [len(rows) for rows in quotient_groups] == [640, 640]),
    ("orbit_sizes_8", all(all(int(row["orbit_size"]) == 8 for row in rows) for rows in quotient_groups)),
    ("subgroup_profiles", subgroup_profiles == [{64: 10}, {64: 10}]),
    ("no_duplicate_rows", duplicate_counts == [0, 0]),
    ("native_products", native_product_failure_counts == [0, 0]),
    ("summary_decorated", [row["decorated_update_row_count"] for row in summaries] == [5120, 5120]),
    ("summary_orbits", [row["gauge_orbit_count"] for row in summaries] == [640, 640]),
    ("summary_orbit_profiles", [row["gauge_orbit_size_profile"] for row in summaries] == [{"8": 640}, {"8": 640}]),
    ("summary_well_defined", all(row["quotient_evaluation_well_defined"] for row in summaries)),
    ("summary_bijective", all(row["quotient_evaluation_bijective"] for row in summaries)),
    ("summary_no_missing", [row["missing_native_relation_row_count"] for row in summaries] == [0, 0]),
    ("summary_no_extra", [row["extra_native_relation_row_count"] for row in summaries] == [0, 0]),
    ("relations_equal", descent["presentation_quotient_relations_equal"] is True),
    ("presentation_isomorphisms_8", gauge["local_presentation_isomorphism_count"] == 8),
    ("gauge_maps_4", gauge["locked_gauge_map_count"] == 4),
    ("matched_gauge_4", gauge["matched_gauge_intertwiner_count"] == 4),
    ("gauge_rows_4", len(gauge["matched_gauge_rows"]) == 4),
    ("gauge_failures_zero", [row["update_intertwining_failure_count"] for row in gauge["matched_gauge_rows"]] == [0, 0, 0, 0]),
    ("gauge_intertwines", gauge["all_locked_gauge_maps_intertwine_update"] is True),
    ("selector_candidates_2", selector["q_axis_order_four_instruction_candidate_counts"] == [2, 2]),
    ("selector_invariant_zero", selector["Aut_D8_invariant_q_axis_order_four_singleton_counts"] == [0, 0]),
    ("no_autonomous_instruction", selector["autonomous_noncentral_instruction_selected"] is False),
    ("no_torsor_identity", selector["order_four_instruction_pair_identified_with_outer_C2_torsor"] is False),
    ("prediction_matches", prediction["prediction_matches"] is True),
    ("prediction_checks", all(prediction["prediction_checks"].values())),
    ("classification", data["classification"] == "gauge_covariant_instruction_parametrized_D8_update_descends_without_autonomous_instruction_selection"),
    ("earned_statement", bool(data["earned_statement"])),
    ("census_performed", boundary["update_census_performed"] is True),
    ("aut_recomputed", boundary["local_automorphism_action_recomputed"] is True),
    ("rows_enumerated", boundary["chart_decorated_update_rows_enumerated"] is True),
    ("quotient_computed", boundary["gauge_quotient_computed"] is True),
    ("covariant_update", boundary["gauge_covariant_instruction_parametrized_update_constructed"] is True),
    ("no_native_update_law", boundary["native_update_law_constructed"] is False),
    ("no_absolute_chart", boundary["absolute_chart_orbit_selected"] is False),
    ("no_strict_chart", boundary["strict_equivariant_chart_selected"] is False),
    ("no_cell", boundary["mechanics_state_cell_established"] is False),
    ("no_side_identity", boundary["local_side_equals_011o_orientation_sheet"] is False),
    ("no_orientation", boundary["orientation_selected"] is False),
    ("no_global_minimality", boundary["global_minimality_claim"] is False),
    ("no_manuscript", boundary["manuscript_mutated"] is False),
    ("no_geometry", boundary["geometry_claim"] is False),
    ("no_direction", boundary["physical_direction_claim"] is False),
    ("no_physics", boundary["physical_claim"] is False),
    ("note_exists", note_path.is_file()),
]

failed = [name for name, passed in checks if not passed]

print("== G60 GAUGE-COVARIANT UPDATE CENSUS AUDIT 012a ==")
print("PACKET:", data["packet"])
print("MODE:", data["mode"])
print("JSON_SHA256:", sha256_file(json_path))
print("NOTE_SHA256:", sha256_file(note_path))
print("COMPUTATION_SCRIPT_SHA256:", sha256_file(compute_path))
print("RAW_RUN_RECEIPT_SHA256:", sha256_file(raw_path))
print("ELEMENT_ORBIT_PROFILES:",
      [row["element_orbit_size_profile"] for row in local_rows])
print("DECORATED_UPDATE_ROW_COUNTS:",
      [row["decorated_update_row_count"] for row in summaries])
print("GAUGE_ORBIT_COUNTS:",
      [row["gauge_orbit_count"] for row in summaries])
print("MATCHED_GAUGE_INTERTWINER_COUNT:",
      gauge["matched_gauge_intertwiner_count"])
print("CLASSIFICATION:", data["classification"])
print("CHECK_COUNT:", len(checks))
print("FAILED_CHECK_COUNT:", len(failed))
for name, passed in checks:
    print("CHECK", name + ":", str(passed).lower())
print("AUDIT_PASS:", str(not failed).lower())
print("FAILED_CHECKS:", failed)
print("EARNED_STATEMENT:", data["earned_statement"])
print("GAUGE_COVARIANT_INSTRUCTION_PARAMETRIZED_UPDATE_CONSTRUCTED:",
      str(boundary["gauge_covariant_instruction_parametrized_update_constructed"]).lower())
print("AUTONOMOUS_NATIVE_UPDATE_INSTRUCTION_SELECTED: false")
print("NATIVE_UPDATE_LAW_CONSTRUCTED: false")
print("MECHANICS_STATE_CELL_ESTABLISHED: false")
print("MANUSCRIPT_MUTATED: false")
print("PHYSICAL_CLAIM: false")

if failed:
    raise SystemExit(1)
