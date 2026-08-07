#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

project = Path(__file__).resolve().parents[2]
json_path = project / "artifacts/json/g60_minimal_directional_datum_preregistration_011h.v1.json"
note_path = project / "notes/g60_minimal_directional_datum_preregistration_011h.md"

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

record = json.loads(json_path.read_text(encoding="utf-8"))
checks = {}

checks["packet"] = record["packet"] == "g60_minimal_directional_datum_preregistration_011h"
checks["mode"] = record["mode"] == "post_obstruction_minimal_datum_preregistration"
checks["frozen"] = record["status"] == "frozen_before_complement_normalizer_and_anchor_census"
checks["head"] = record["locked_head"] == "fdfc28b Lock G60 duad orientation kernel obstruction"
checks["authority_count"] = len(record["authorities"]) == 5
checks["authority_hashes"] = all(x["hash_match"] for x in record["authorities"].values())

known = record["known_before_test"]
checks["group_480"] = known["full_group_order"] == 480
checks["Z1"] = known["Z1_indices"] == [0,326]
checks["Z2"] = known["Z2_indices"] == [0,65,124,326]
checks["full_A_obstruction"] = known["full_A_ordered_bridge_count"] == 0
checks["full_A_unordered_unique"] = known["full_A_unordered_bridge_count"] == 1
checks["two_complements_known"] = known["S5_complement_count_reported_by_079"] == 2
checks["no_census"] = known["minimal_datum_census_performed"] is False
checks["no_map_comparison"] = known["complement_map_sets_compared"] is False
checks["no_anchor_ablation"] = known["anchor_ablation_performed"] is False

checks["five_ladder_levels"] = [x["level"] for x in record["candidate_datum_ladder"]] == ["D0","D1","D2","D3","D4"]
checks["test_count_11"] = len(record["frozen_tests"]) == 11

prediction = record["structural_prediction"]
checks["prediction_not_blind"] = prediction["not_blind"] is True
checks["prediction_declared"] = prediction["declared_before_computation"] is True
checks["predict_two_complements"] = prediction["predicted_complement_count"] == 2
checks["predict_N_240"] = prediction["predicted_common_normalizer_order"] == 240
checks["predict_N_two_maps"] = prediction["predicted_N_bridge_count"] == 2
checks["predict_each_complement_two"] = prediction["predicted_bridge_count_per_complement"] == 2
checks["predict_same_maps"] = prediction["predicted_complement_map_sets_identical"] is True
checks["predict_anchor_one"] = prediction["predicted_bridge_count_per_compatible_anchor"] == 1
checks["predict_ablation_two"] = prediction["predicted_anchor_ablation_bridge_count"] == 2
checks["prediction_not_result"] = prediction["prediction_is_not_a_result"] is True

checks["nine_outcomes"] = len(record["outcome_order"]) == 9
checks["all_outcomes_defined"] = set(record["outcome_order"]) == set(record["outcome_predicates"])

boundary = record["minimality_boundary"]
checks["bounded_minimality"] = boundary["minimality_claim_scope"] == "only_the_frozen_candidate_datum_ladder"
checks["no_global_minimality"] = boundary["global_information_theoretic_minimality_claim"] is False
checks["complement_not_prejudged"] = boundary["complement_choice_not_declared_unnecessary_before_test"] is True
checks["anchor_not_prejudged"] = boundary["anchor_not_declared_sufficient_before_test"] is True
checks["orientation_not_selected"] = boundary["orientation_selected_now"] is False
checks["no_physical_direction"] = boundary["physical_direction_claim"] is False
checks["no_manuscript"] = boundary["manuscript_mutation_allowed"] is False
checks["no_geometry"] = boundary["geometry_claim"] is False
checks["no_physics"] = boundary["physical_claim"] is False
checks["note_exists"] = note_path.exists()

failed = [key for key, value in checks.items() if not value]

print("== G60 MINIMAL DIRECTIONAL DATUM PREREGISTRATION AUDIT 011h ==")
print("PACKET:", record["packet"])
print("MODE:", record["mode"])
print("JSON_SHA256:", sha256(json_path))
print("NOTE_SHA256:", sha256(note_path))
print("LOCKED_HEAD:", record["locked_head"])
print("LADDER_LEVELS:", [x["level"] for x in record["candidate_datum_ladder"]])
print("PREDICTED_COMPLEMENT_COUNT: 2")
print("PREDICTED_COMMON_NORMALIZER_ORDER: 240")
print("PREDICTED_N_BRIDGE_COUNT: 2")
print("PREDICTED_ANCHORED_BRIDGE_COUNT: 1")
print("PREDICTION_BLIND: false")
print("MINIMAL_DATUM_CENSUS_PERFORMED: false")
print("OUTCOME_ORDER:", record["outcome_order"])
print("CHECK_COUNT:", len(checks))
print("FAILED_CHECK_COUNT:", len(failed))
for key, value in checks.items():
    print("CHECK", key + ":", str(value).lower())
print("PREREGISTRATION_PASS:", str(not failed).lower())
print("FAILED_CHECKS:", failed)
print("ORIENTATION_SELECTED: false")
print("MANUSCRIPT_MUTATED: false")
print("PHYSICAL_CLAIM: false")
