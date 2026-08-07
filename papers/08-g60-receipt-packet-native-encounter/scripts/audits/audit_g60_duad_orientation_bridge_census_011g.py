#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

project = Path(__file__).resolve().parents[2]
json_path = project / "artifacts/json/g60_duad_orientation_bridge_census_011g.v1.json"
raw_path = project / "artifacts/receipts/g60_duad_orientation_bridge_census_011g_raw_run.txt"
note_path = project / "notes/g60_duad_orientation_bridge_census_011g.md"
compute_path = project / "scripts/audits/compute_g60_duad_orientation_bridge_census_011g.py"

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

record = json.loads(json_path.read_text(encoding="utf-8"))
checks = {}

checks["packet"] = record["packet"] == "g60_duad_orientation_bridge_census_011g"
checks["mode_frozen"] = record["mode"] == "frozen_complete_finite_action_census"
checks["head_locked"] = record["locked_head"] == "b0353ef Preregister G60 duad orientation bridge test"
checks["result_frozen"] = record["result_frozen"] is True
checks["audit_pass_recorded"] = record["audit_pass"] is True
checks["candidate_hash"] = record["promotion"]["candidate_json_sha256"] == "2890a55548f2f4077a2ee736ad4991d267cc470725e47c46350c30305a4900a0"
checks["raw_hash"] = sha256(raw_path) == "a544c3ebe80ce4aeccf17beecde468bb1dd14804f1783863c3babf1a6120a0c0"
checks["compute_hash"] = sha256(compute_path) == "c8b19325654e4eddb612e0a5d8dee372838d1f563e80074b066dcc0fdaee645b"
checks["raw_copied"] = record["promotion"]["raw_run_receipt_copied_byte_for_byte"] is True
checks["compute_copied"] = record["promotion"]["computation_script_copied_byte_for_byte"] is True

group = record["group_reconstruction"]
checks["group_order_480"] = group["group_order"] == 480
checks["identity_0"] = group["identity_index"] == 0
checks["closure_zero"] = group["closure_failure_count"] == 0
checks["inverse_zero"] = group["inverse_failure_count"] == 0
checks["operation_ok"] = group["operation_ok"] is True
checks["block_action_consistent"] = group["block_action_consistency_failure_count"] == 0
checks["root_action_closed"] = group["root_action_failure_count"] == 0

sets = record["A_sets"]
checks["ordered_20_transitive"] = sets["ordered_duads"]["count"] == 20 and sets["ordered_duads"]["orbit_count"] == 1
checks["unordered_10_transitive"] = sets["unordered_duads"]["count"] == 10 and sets["unordered_duads"]["orbit_count"] == 1
checks["roots_20_transitive"] = sets["orientation_roots"]["count"] == 20 and sets["orientation_roots"]["orbit_count"] == 1
checks["pairs_10_transitive"] = sets["inverse_root_pairs"]["count"] == 10 and sets["inverse_root_pairs"]["orbit_count"] == 1
checks["ordered_kernel_Z2"] = sets["ordered_duads"]["pointwise_kernel_indices"] == [0,65,124,326]
checks["unordered_kernel_Z2"] = sets["unordered_duads"]["pointwise_kernel_indices"] == [0,65,124,326]
checks["root_kernel_Z1"] = sets["orientation_roots"]["pointwise_kernel_indices"] == [0,326]
checks["pair_kernel_Z2"] = sets["inverse_root_pairs"]["pointwise_kernel_indices"] == [0,65,124,326]

kernel = record["kernel_action"]
checks["kernel_obstruction"] = kernel["kernel_obstruction_verified"] is True
checks["inversion_equivariance"] = kernel["inversion_equivariance_failure_count"] == 0
checks["duad_reversal_equivariance"] = kernel["duad_reversal_equivariance_failure_count"] == 0

rows = {row["element_index"]: row for row in kernel["root_action_rows"]}
checks["identity_fixes_roots"] = rows[0]["fixed_root_count"] == 20
checks["tau_fixes_roots"] = rows[326]["fixed_root_count"] == 20
checks["65_inverts_roots"] = rows[65]["inverse_root_count"] == 20
checks["124_inverts_roots"] = rows[124]["inverse_root_count"] == 20
checks["no_other_root_actions"] = all(row["other_root_count"] == 0 for row in rows.values())

bridges = record["equivariant_bridges"]
ordered = bridges["ordered_to_roots"]
unordered = bridges["unordered_to_inverse_pairs"]
checks["ordered_stabilizer_24"] = ordered["source_stabilizer_order"] == 24
checks["ordered_fixed_targets_zero"] = ordered["fixed_target_candidate_count"] == 0
checks["ordered_bridge_zero"] = ordered["bridge_count"] == 0
checks["unordered_stabilizer_48"] = unordered["source_stabilizer_order"] == 48
checks["unordered_fixed_target_one"] = unordered["fixed_target_candidate_count"] == 1
checks["unordered_bridge_one"] = unordered["bridge_count"] == 1
checks["unordered_mapping_row_count_10"] = len(unordered["rows"]) == 10

expected_mapping = {
    (0,1): (13,400),
    (0,2): (354,477),
    (0,3): (209,331),
    (0,4): (37,247),
    (1,2): (88,370),
    (1,3): (67,126),
    (1,4): (270,420),
    (2,3): (230,457),
    (2,4): (68,121),
    (3,4): (198,314),
}
actual_mapping = {
    tuple(row["unordered_duad"]): tuple(row["inverse_pair"])
    for row in unordered["rows"]
}
checks["mapping_exact"] = actual_mapping == expected_mapping
checks["classification"] = record["classification"] == "unique_unordered_bridge_with_oriented_kernel_obstruction"
checks["prediction_matches"] = record["prediction"]["prediction_matches"] is True
checks["predicted_counts_match"] = (
    record["prediction"]["actual_ordered_bridge_count"] == 0
    and record["prediction"]["actual_unordered_bridge_count"] == 1
)

boundary = record["boundary"]
checks["orientation_not_selected"] = boundary["orientation_selected"] is False
checks["minimal_datum_not_identified"] = boundary["minimal_directional_datum_identified"] is False
checks["no_larger_carrier"] = boundary["larger_carrier_constructed"] is False
checks["no_replacement"] = boundary["replacement_selector_used"] is False
checks["no_manuscript"] = boundary["manuscript_mutated"] is False
checks["no_geometry"] = boundary["geometry_claim"] is False
checks["no_physics"] = boundary["physical_claim"] is False
checks["repository_preserved"] = record["repository"]["status_preserved"] is True
checks["note_exists"] = note_path.exists()

failed = [key for key, value in checks.items() if not value]

print("== G60 DUAD ORIENTATION BRIDGE CENSUS AUDIT 011g ==")
print("PACKET:", record["packet"])
print("MODE:", record["mode"])
print("JSON_SHA256:", sha256(json_path))
print("NOTE_SHA256:", sha256(note_path))
print("COMPUTATION_SCRIPT_SHA256:", sha256(compute_path))
print("RAW_RUN_RECEIPT_SHA256:", sha256(raw_path))
print("ORDERED_DUAD_KERNEL:", sets["ordered_duads"]["pointwise_kernel_indices"])
print("ROOT_KERNEL:", sets["orientation_roots"]["pointwise_kernel_indices"])
print("INVERSE_PAIR_KERNEL:", sets["inverse_root_pairs"]["pointwise_kernel_indices"])
print("ORDERED_BRIDGE_COUNT:", ordered["bridge_count"])
print("UNORDERED_BRIDGE_COUNT:", unordered["bridge_count"])
print("KERNEL_OBSTRUCTION_VERIFIED:", str(kernel["kernel_obstruction_verified"]).lower())
print("CLASSIFICATION:", record["classification"])
print("CHECK_COUNT:", len(checks))
print("FAILED_CHECK_COUNT:", len(failed))
for key, value in checks.items():
    print("CHECK", key + ":", str(value).lower())
print("AUDIT_PASS:", str(not failed).lower())
print("FAILED_CHECKS:", failed)
print("EARNED_STATEMENT:", record["earned_statement"])
print("ORIENTATION_SELECTED: false")
print("MINIMAL_DIRECTIONAL_DATUM_IDENTIFIED: false")
print("MANUSCRIPT_MUTATED: false")
print("PHYSICAL_CLAIM: false")
