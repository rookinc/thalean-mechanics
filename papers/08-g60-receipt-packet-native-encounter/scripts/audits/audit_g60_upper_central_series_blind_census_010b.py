import hashlib
import json
from pathlib import Path

project = Path(__file__).resolve().parents[2]

json_path = project / "artifacts/json/g60_upper_central_series_blind_census_010b.v1.json"
raw_receipt = project / "artifacts/receipts/g60_upper_central_series_blind_census_010b_raw_run.txt"
note_path = project / "notes/g60_upper_central_series_blind_census_010b.md"
compute_path = project / "scripts/audits/compute_g60_upper_central_series_blind_census_010b.py"

expected_action_sha = "b37313b135495752b11e525bb61979163fdf54aec4be4f5d027dcee64c9efc21"
expected_edge_sha = "c700a185fab6a5f434da09b7acb716b96c76170774bee946af8ea907e4fe7f9f"
expected_prereg_sha = "f43a9d1b3e97133d62d6f1b193409617226c63caba304e7613de4745182be2ea"
expected_candidate_json_sha = "47373c2ba46b6d78b5497bbadf9be5482b674f1aa9d34cd55652980ee12e9ab8"
expected_script_sha = "7216e04fabceaaa97ce7423a54cb7e65b619c4e666153fe4996efb058b049f76"
expected_raw_receipt_sha = "90006795538194dede0fbdde40a5a279ec14402041a1e390e5c1c51bb16d8c70"

def sha256_file(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

record = json.loads(json_path.read_text(encoding="utf-8"))
group = record["group_reconstruction"]
central = record["central_series"]
native = record["native_graph_action"]
profiles = native["central_layer_profiles"]
boundary = record["boundary"]
promotion = record["promotion"]

z1 = profiles["Z1"]
z2 = profiles["Z2"]
z3 = profiles["Z3"]

checks = {
    "packet_name": record["packet"] == "g60_upper_central_series_blind_census_010b",
    "mode_frozen_blind_phase_a": record["mode"] == "frozen_blind_phase_a",
    "action_hash": record["authorities"]["action_sha256"] == expected_action_sha,
    "raw_edge_hash": record["authorities"]["raw_edge_sha256"] == expected_edge_sha,
    "preregistration_hash": record["authorities"]["preregistration_sha256"] == expected_prereg_sha,
    "candidate_json_provenance": promotion["candidate_json_sha256"] == expected_candidate_json_sha,
    "computation_script_hash": sha256_file(compute_path) == expected_script_sha,
    "raw_receipt_hash": sha256_file(raw_receipt) == expected_raw_receipt_sha,
    "mapping_rows_480": group["mapping_row_count"] == 480,
    "group_order_480": group["group_order"] == 480,
    "identity_index_present": group["identity_candidate_count"] == 1,
    "closure_zero": group["closure_failure_count"] == 0,
    "inverse_zero": group["inverse_failure_count"] == 0,
    "multiplication_consistency_zero": group["multiplication_consistency_failure_count"] == 0,
    "declared_order_consistency_zero": group["declared_order_consistency_failure_count"] == 0,
    "operation_reconstruction_ok": group["operation_reconstruction_ok"] is True,
    "center_order_2": central["center_order"] == 2,
    "center_members_frozen": central["center_member_indices"] == [0, 326],
    "second_center_order_4": central["second_center_order"] == 4,
    "second_center_members_frozen": central["second_center_member_indices"] == [0, 65, 124, 326],
    "third_center_equals_second": central["third_center_member_indices"] == central["second_center_member_indices"],
    "Z1_subset_Z2": central["Z1_subset_Z2"] is True,
    "Z2_subset_Z3": central["Z2_subset_Z3"] is True,
    "full_action_preserves_graph": native["full_action_graph_automorphism_failure_count"] == 0,
    "Z1_semiregular": z1["semiregular"] is True,
    "Z1_vertex_orbits_30": z1["vertex_orbit_count"] == 30,
    "Z1_vertex_orbit_sizes": z1["vertex_orbit_size_profile"] == {"2": 30},
    "Z1_edge_orbits_60": z1["edge_orbit_count"] == 60,
    "Z1_no_edge_inversion": z1["edge_inversion_failure_member_count"] == 0,
    "Z1_quotient_30_60": z1["quotient_vertex_count"] == 30 and z1["quotient_edge_count"] == 60,
    "Z1_local_covering": z1["local_covering_failure_count"] == 0,
    "Z2_semiregular": z2["semiregular"] is True,
    "Z2_vertex_orbits_15": z2["vertex_orbit_count"] == 15,
    "Z2_vertex_orbit_sizes": z2["vertex_orbit_size_profile"] == {"4": 15},
    "Z2_edge_orbits_30": z2["edge_orbit_count"] == 30,
    "Z2_no_edge_inversion": z2["edge_inversion_failure_member_count"] == 0,
    "Z2_quotient_15_30": z2["quotient_vertex_count"] == 15 and z2["quotient_edge_count"] == 30,
    "Z2_local_covering": z2["local_covering_failure_count"] == 0,
    "Z3_profile_equals_Z2": z3["member_indices"] == z2["member_indices"],
    "central_action_checks_pass": native["central_action_checks_pass"] is True,
    "outcome_exact_target": record["classification"]["preregistered_outcome"] == "exact_target",
    "no_replacement_selector": record["classification"]["replacement_selector_searched"] is False,
    "no_smallest_order_selector": record["classification"]["smallest_order_selector_used"] is False,
    "repository_preserved": record["repository_preservation"]["repository_status_preserved"] is True,
    "candidate_hashes_preserved": promotion["mathematical_result_fields_changed"] is False,
    "phase_a_frozen": boundary["phase_a_result_frozen"] is True,
    "phase_b_requires_commit": boundary["phase_b_requires_010b_commit"] is True,
    "phase_b_not_yet_allowed": boundary["phase_b_allowed_now"] is False,
    "no_unblinding": boundary["unblinding_performed"] is False,
    "no_historical_comparison": boundary["historical_tower_comparison_performed"] is False,
    "no_theorem_claim": boundary["theorem_claim"] is False,
    "note_exists": note_path.is_file(),
}

failed = [name for name, passed in checks.items() if not passed]

print("== G60 UPPER-CENTRAL BLIND CENSUS AUDIT 010b ==")
print("PACKET:", record["packet"])
print("MODE:", record["mode"])
print("JSON_SHA256:", sha256_file(json_path))
print("NOTE_SHA256:", sha256_file(note_path))
print("COMPUTATION_SCRIPT_SHA256:", sha256_file(compute_path))
print("RAW_RUN_RECEIPT_SHA256:", sha256_file(raw_receipt))
print("ACTION_SHA256:", record["authorities"]["action_sha256"])
print("RAW_EDGE_SHA256:", record["authorities"]["raw_edge_sha256"])
print("PREREGISTRATION_SHA256:", record["authorities"]["preregistration_sha256"])
print("GROUP_ORDER:", group["group_order"])
print("IDENTITY_INDEX:", group["identity_index"])
print("CLOSURE_FAILURE_COUNT:", group["closure_failure_count"])
print("INVERSE_FAILURE_COUNT:", group["inverse_failure_count"])
print("MULTIPLICATION_CONSISTENCY_FAILURE_COUNT:", group["multiplication_consistency_failure_count"])
print("CENTER_ORDER:", central["center_order"])
print("CENTER_MEMBER_INDICES:", central["center_member_indices"])
print("SECOND_CENTER_ORDER:", central["second_center_order"])
print("SECOND_CENTER_MEMBER_INDICES:", central["second_center_member_indices"])
print("THIRD_CENTER_ORDER:", central["third_center_order"])
print("THIRD_CENTER_MEMBER_INDICES:", central["third_center_member_indices"])
print("Z1_SEMIREGULAR:", str(z1["semiregular"]).lower())
print("Z1_VERTEX_ORBIT_PROFILE:", z1["vertex_orbit_size_profile"])
print("Z1_EDGE_ORBIT_PROFILE:", z1["edge_orbit_size_profile"])
print("Z1_LOCAL_COVERING_FAILURE_COUNT:", z1["local_covering_failure_count"])
print("Z2_SEMIREGULAR:", str(z2["semiregular"]).lower())
print("Z2_VERTEX_ORBIT_PROFILE:", z2["vertex_orbit_size_profile"])
print("Z2_EDGE_ORBIT_PROFILE:", z2["edge_orbit_size_profile"])
print("Z2_LOCAL_COVERING_FAILURE_COUNT:", z2["local_covering_failure_count"])
print("PREREGISTERED_OUTCOME:", record["classification"]["preregistered_outcome"])
print("REPOSITORY_STATUS_PRESERVED:", str(record["repository_preservation"]["repository_status_preserved"]).lower())
print("PHASE_A_RESULT_FROZEN:", str(boundary["phase_a_result_frozen"]).lower())
print("PHASE_B_ALLOWED_NOW:", str(boundary["phase_b_allowed_now"]).lower())
print("UNBLINDING_PERFORMED:", str(boundary["unblinding_performed"]).lower())
print("CHECK_COUNT:", len(checks))
print("FAILED_CHECK_COUNT:", len(failed))
for name, passed in checks.items():
    print("CHECK", name + ":", str(passed).lower())
print("AUDIT_PASS:", str(not failed).lower())
print("FAILED_CHECKS:", failed)
print("THEOREM_CLAIM: false")
