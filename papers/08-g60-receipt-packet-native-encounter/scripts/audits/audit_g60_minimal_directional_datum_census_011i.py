#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

project = Path(__file__).resolve().parents[2]
json_path = project / "artifacts/json/g60_minimal_directional_datum_census_011i.v1.json"
raw_path = project / "artifacts/receipts/g60_minimal_directional_datum_census_011i_raw_run.txt"
note_path = project / "notes/g60_minimal_directional_datum_census_011i.md"
compute_path = project / "scripts/audits/compute_g60_minimal_directional_datum_census_011i.py"

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

record = json.loads(json_path.read_text(encoding="utf-8"))
checks = {}

checks["packet"] = record["packet"] == "g60_minimal_directional_datum_census_011i"
checks["mode"] = record["mode"] == "frozen_complete_minimal_datum_ladder_census"
checks["head"] = record["locked_head"] == "0f46105 Preregister G60 minimal directional datum test"
checks["result_frozen"] = record["result_frozen"] is True
checks["candidate_hash"] = record["promotion"]["candidate_json_sha256"] == "a675028bb99413429583343662b7d19cbf83f812f27508830c73060b38836d59"
checks["raw_hash"] = sha256(raw_path) == "ffdcb95f0a7ad27147efa020119411d6b5347f12b9ed2be7b6ebdfeaa9d5991f"
checks["compute_hash"] = sha256(compute_path) == "1fabafd5b7fa10334030a3872163e9e33339ae447a2186d5fed5d708cb328319"
checks["raw_copied"] = record["promotion"]["raw_run_receipt_copied_byte_for_byte"] is True
checks["compute_copied"] = record["promotion"]["computation_script_copied_byte_for_byte"] is True

group = record["group_reconstruction"]
checks["group_480"] = group["group_order"] == 480
checks["identity_0"] = group["identity_index"] == 0
checks["closure_zero"] = group["closure_failure_count"] == 0
checks["inverse_zero"] = group["inverse_failure_count"] == 0
checks["block_consistent"] = group["block_action_consistency_failure_count"] == 0
checks["operation_ok"] = group["operation_ok"] is True

comp = record["complement_reconstruction"]
checks["transposition_lifts_4"] = comp["transposition_lift_count"] == 4
checks["five_cycle_lifts_4"] = comp["five_cycle_lift_count"] == 4
checks["lift_pairs_16"] = comp["lift_pair_count"] == 16
checks["complements_2"] = comp["complement_count"] == 2
checks["complement_action_closed"] = comp["complement_conjugacy_action_failure_count"] == 0
checks["normalizers_240"] = all(row["normalizer_order"] == 240 for row in comp["complement_rows"])

N = record["canonical_propagation_subgroup"]
checks["N_exists"] = N["exists"] is True
checks["N_order_240"] = N["order"] == 240
checks["N_index_2"] = N["index_in_A"] == 2
checks["N_normal"] = N["is_normal"] is True
checks["N_subgroup"] = N["is_subgroup"] is True
checks["normalizers_equal"] = N["normalizers_equal"] is True
checks["family_kernel_equals_N"] = N["family_kernel_equals_common_normalizer"] is True
checks["N_intersection_Z2_is_Z1"] = N["intersection_Z2"] == [0,326]

bridges = record["bridge_counts"]
checks["full_A_zero"] = bridges["full_A"]["bridge_count"] == 0
checks["N_zero"] = bridges["canonical_N"]["bridge_count"] == 0
checks["N_stabilizer_12"] = bridges["canonical_N"]["source_stabilizer_order"] == 12
checks["N_fixed_targets_zero"] = bridges["canonical_N"]["fixed_target_count"] == 0
checks["two_complement_rows"] = len(bridges["complements"]) == 2
checks["complements_zero"] = all(row["bridge_count"] == 0 for row in bridges["complements"])
checks["complement_stabilizers_6"] = all(row["source_stabilizer_order"] == 6 for row in bridges["complements"])
checks["complement_fixed_targets_zero"] = all(row["fixed_target_count"] == 0 for row in bridges["complements"])
checks["complement_map_sets_identical"] = bridges["complement_map_sets_identical"] is True
checks["complement_maps_equal_N"] = bridges["complement_maps_equal_N"] is True
checks["not_inverse_pair_of_maps"] = bridges["two_N_maps_inverse_related"] is False
checks["reversal_failures_zero"] = bridges["reversal_inversion_failure_count"] == 0

anchor = record["anchor_ablation"]
checks["anchors_40"] = anchor["compatible_anchor_count"] == 40
checks["anchor_profile_all_zero"] = anchor["N_anchor_bridge_count_profile"] == {"0":40}
checks["complement_anchor_profiles_zero"] = all(profile == {"0":40} for profile in anchor["complement_anchor_bridge_count_profiles"])
checks["anchors_not_unique"] = anchor["all_compatible_anchors_select_unique_bridge"] is False
checks["without_anchor_zero"] = anchor["without_anchor_N_bridge_count"] == 0
checks["one_bit_not_earned"] = anchor["one_bit_description_earned"] is False

checks["prediction_failed"] = record["prediction"]["prediction_matches"] is False
checks["classification"] = record["classification"] == "canonical_subgroup_has_no_oriented_bridge"

boundary = record["boundary"]
checks["bounded_scope"] = boundary["minimality_scope"] == "frozen_D0_to_D4_candidate_ladder_only"
checks["no_global_minimality"] = boundary["global_information_theoretic_minimality"] is False
checks["local_anchor_names_root"] = boundary["local_anchor_names_one_local_root"] is True
checks["anchor_not_global"] = boundary["local_anchor_propagates_globally"] is False
checks["no_minimal_datum"] = boundary["minimal_directional_datum_identified"] is False
checks["no_replacement"] = boundary["replacement_datum_searched"] is False
checks["no_physical_direction"] = boundary["physical_direction_claim"] is False
checks["no_manuscript"] = boundary["manuscript_mutated"] is False
checks["no_geometry"] = boundary["geometry_claim"] is False
checks["no_physics"] = boundary["physical_claim"] is False
checks["repository_preserved"] = record["repository"]["status_preserved"] is True
checks["note_exists"] = note_path.exists()

failed = [key for key, value in checks.items() if not value]

print("== G60 MINIMAL DIRECTIONAL DATUM CENSUS AUDIT 011i ==")
print("PACKET:", record["packet"])
print("MODE:", record["mode"])
print("JSON_SHA256:", sha256(json_path))
print("NOTE_SHA256:", sha256(note_path))
print("COMPUTATION_SCRIPT_SHA256:", sha256(compute_path))
print("RAW_RUN_RECEIPT_SHA256:", sha256(raw_path))
print("COMPLEMENT_COUNT:", comp["complement_count"])
print("CANONICAL_N_ORDER:", N["order"])
print("N_SOURCE_STABILIZER_ORDER:", bridges["canonical_N"]["source_stabilizer_order"])
print("N_FIXED_TARGET_COUNT:", bridges["canonical_N"]["fixed_target_count"])
print("N_BRIDGE_COUNT:", bridges["canonical_N"]["bridge_count"])
print("COMPLEMENT_BRIDGE_COUNTS:", [row["bridge_count"] for row in bridges["complements"]])
print("ANCHOR_COUNT:", anchor["compatible_anchor_count"])
print("ANCHOR_BRIDGE_PROFILE:", anchor["N_anchor_bridge_count_profile"])
print("ONE_BIT_DESCRIPTION_EARNED:", str(anchor["one_bit_description_earned"]).lower())
print("CLASSIFICATION:", record["classification"])
print("CHECK_COUNT:", len(checks))
print("FAILED_CHECK_COUNT:", len(failed))
for key, value in checks.items():
    print("CHECK", key + ":", str(value).lower())
print("AUDIT_PASS:", str(not failed).lower())
print("FAILED_CHECKS:", failed)
print("EARNED_STATEMENT:", record["earned_statement"])
print("MINIMAL_DIRECTIONAL_DATUM_IDENTIFIED: false")
print("REPLACEMENT_DATUM_SEARCHED: false")
print("MANUSCRIPT_MUTATED: false")
print("PHYSICAL_CLAIM: false")
