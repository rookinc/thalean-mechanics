#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

project = Path(__file__).resolve().parents[2]
json_path = project / "artifacts/json/g60_duad_orientation_bridge_preregistration_011f.v1.json"
note_path = project / "notes/g60_duad_orientation_bridge_preregistration_011f.md"

expected = {
    "five_matching_partition_077": "7db5162f2dbd9d53b44e8a9716f097394e5a75040951eceb8ec1e6ddbbb372b0",
    "five_matching_equivariance_078": "db01304b44015a25e8f207d3fe869ad96ebcd82d3d2bd7017908a9ed7c843ec7",
    "s5_extension_splitting_079": "728071622f7a6a98042a8dd4d1a6fa01cdcc8a456bd2bd5b5aadcf22965f5221",
    "orientation_root_reversal_011e": "15ef444f6ed6bfbf0dc2611985edeffd0c38ec41142dfeb2f9ca53ef32813623",
}

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

record = json.loads(json_path.read_text(encoding="utf-8"))
checks = {}

checks["packet"] = record["packet"] == "g60_duad_orientation_bridge_preregistration_011f"
checks["mode_post_schema"] = record["mode"] == "structural_preregistration_after_authority_schema_inspection"
checks["status_frozen_before_computation"] = record["preregistration_status"] == "frozen_before_duad_root_action_computation"
checks["head_38155e3"] = record["locked_head"] == "38155e3 Lock native G60 orientation-root obstruction"

for key, digest in expected.items():
    source = record["authorities"][key]
    checks["hash_" + key] = source["sha256"] == digest and source["hash_match"] is True
    checks["tracked_" + key] = source["git_tracked"] is True

known = record["known_before_test"]
checks["five_blocks"] = known["five_matching_block_count"] == 5
checks["S5_order_120"] = known["five_point_image_order"] == 120
checks["kernel_V4"] = known["five_point_action_kernel"] == "native_V4"
checks["duad_counts_20_10"] = known["ordered_duad_count"] == 20 and known["unordered_duad_count"] == 10
checks["root_counts_20_10"] = known["orientation_root_count"] == 20 and known["inverse_root_pair_count"] == 10
checks["schema_inspected"] = known["schema_inspection_performed"] is True
checks["no_equality_test"] = known["duad_root_equality_test_performed"] is False
checks["no_bridge_count"] = known["equivariant_bridge_counted"] is False
checks["no_kernel_test"] = known["kernel_action_test_performed"] is False

prediction = record["structural_prediction"]
checks["prediction_declared"] = prediction["declared_before_computation"] is True
checks["prediction_not_blind"] = prediction["not_blind"] is True
checks["predicted_unordered_one"] = prediction["predicted_unordered_bridge_count"] == 1
checks["predicted_ordered_zero"] = prediction["predicted_ordered_bridge_count"] == 0
checks["prediction_not_result"] = prediction["prediction_is_not_a_result"] is True

expected_outcomes = [
    "computation_failure",
    "authority_failure",
    "oriented_bridge_exists",
    "no_equivariant_unordered_bridge",
    "unique_unordered_bridge_with_oriented_kernel_obstruction",
    "multiple_unordered_bridges_with_oriented_kernel_obstruction",
    "unordered_bridge_without_verified_kernel_obstruction",
]
checks["seven_outcomes"] = record["outcome_order"] == expected_outcomes
checks["all_outcomes_defined"] = set(record["outcome_predicates"]) == set(expected_outcomes)
checks["falsifiers_present"] = len(record["falsifiers"]) == 7

boundary = record["boundary"]
checks["no_unordered_claim"] = boundary["unordered_bridge_not_yet_proved"] is True
checks["no_oriented_exclusion_claim"] = boundary["oriented_bridge_not_yet_excluded_by_computation"] is True
checks["ordering_not_sufficient"] = boundary["ordering_a_visible_duad_not_claimed_sufficient"] is True
checks["no_minimal_datum"] = boundary["minimal_directional_datum_not_identified"] is True
checks["no_replacement"] = boundary["replacement_selector_forbidden"] is True
checks["no_manuscript"] = boundary["manuscript_mutation_allowed"] is False
checks["no_orientation"] = boundary["orientation_selected"] is False
checks["no_geometry"] = boundary["geometry_claim"] is False
checks["no_physics"] = boundary["physical_claim"] is False
checks["note_exists"] = note_path.exists()

failed = [key for key, value in checks.items() if not value]

print("== G60 DUAD ORIENTATION BRIDGE PREREGISTRATION AUDIT 011f ==")
print("PACKET:", record["packet"])
print("MODE:", record["mode"])
print("JSON_SHA256:", sha256(json_path))
print("NOTE_SHA256:", sha256(note_path))
print("LOCKED_HEAD:", record["locked_head"])
print("FIVE_POINT_IMAGE: S5")
print("FIVE_POINT_KERNEL: native_V4")
print("ORDERED_DUAD_COUNT: 20")
print("UNORDERED_DUAD_COUNT: 10")
print("ROOT_COUNT: 20")
print("INVERSE_PAIR_COUNT: 10")
print("PREDICTED_ORDERED_BRIDGE_COUNT: 0")
print("PREDICTED_UNORDERED_BRIDGE_COUNT: 1")
print("PREDICTION_BLIND: false")
print("BRIDGE_COMPUTATION_PERFORMED: false")
print("KERNEL_ACTION_COMPUTED: false")
print("OUTCOME_ORDER:", record["outcome_order"])
print("CHECK_COUNT:", len(checks))
print("FAILED_CHECK_COUNT:", len(failed))
for key, value in checks.items():
    print("CHECK", key + ":", str(value).lower())
print("PREREGISTRATION_PASS:", str(not failed).lower())
print("FAILED_CHECKS:", failed)
print("ORIENTATION_SELECTED: false")
print("MINIMAL_DIRECTIONAL_DATUM_IDENTIFIED: false")
print("MANUSCRIPT_MUTATED: false")
print("PHYSICAL_CLAIM: false")
