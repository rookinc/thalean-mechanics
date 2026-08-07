#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

project = Path(__file__).resolve().parents[2]
json_path = project / "artifacts/json/g60_root_stabilizer_action_type_preregistration_011j.v1.json"
note_path = project / "notes/g60_root_stabilizer_action_type_preregistration_011j.md"

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

record = json.loads(json_path.read_text(encoding="utf-8"))
checks = {}

checks["packet"] = record["packet"] == "g60_root_stabilizer_action_type_preregistration_011j"
checks["mode"] = record["mode"] == "post_obstruction_stabilizer_embedding_preregistration"
checks["frozen"] = record["status"] == "frozen_before_root_stabilizer_action_type_census"
checks["head"] = record["locked_head"] == "578325f Lock G60 minimal directional datum obstruction"
checks["authority_count"] = len(record["authorities"]) == 6
checks["authority_hashes"] = all(row["hash_match"] for row in record["authorities"].values())

known = record["known_before_test"]
checks["roots_20"] = known["root_count"] == 20
checks["duads_20"] = known["ordered_duad_count"] == 20
checks["N_240"] = known["N_order"] == 240
checks["two_complements"] = known["complement_count"] == 2
checks["known_stabilizer_orders"] = (
    known["N_ordered_duad_stabilizer_order"] == 12
    and known["complement_ordered_duad_stabilizer_order"] == 6
)
checks["known_fixed_roots_zero"] = known["fixed_root_count_for_these_stabilizers"] == 0
checks["no_census"] = known["root_stabilizer_action_type_computed"] is False
checks["no_replacement"] = known["replacement_source_action_constructed"] is False

checks["twelve_tests"] = len(record["frozen_census"]) == 12
prediction = record["structural_prediction"]
checks["prediction_not_blind"] = prediction["not_blind"] is True
checks["prediction_declared"] = prediction["declared_before_computation"] is True
checks["predict_same_abstract"] = prediction["predicted_same_abstract_type"] is True
checks["predict_nonconjugate"] = prediction["predicted_conjugate_in_S5"] is False
checks["predict_root_2_3"] = prediction["predicted_root_profile"] == "S3_all_even_orbits_2_3"
checks["predict_ordered_1_1_3"] = prediction["predicted_ordered_duad_profile"] == "S3_mixed_parity_orbits_1_1_3"
checks["prediction_not_result"] = prediction["prediction_is_not_a_result"] is True

checks["seven_outcomes"] = len(record["outcome_order"]) == 7
checks["all_outcomes_defined"] = set(record["outcome_order"]) == set(record["outcome_predicates"])

boundary = record["boundary"]
checks["classification_only"] = boundary["classification_only"] is True
checks["no_source_set"] = boundary["replacement_source_A_set_constructed"] is False
checks["no_selector"] = boundary["new_selector_searched"] is False
checks["no_minimal_datum"] = boundary["minimal_directional_datum_identified"] is False
checks["no_orientation"] = boundary["orientation_selected"] is False
checks["no_manuscript"] = boundary["manuscript_mutation_allowed"] is False
checks["no_geometry"] = boundary["geometry_claim"] is False
checks["no_physics"] = boundary["physical_claim"] is False
checks["note_exists"] = note_path.exists()

failed = [key for key, value in checks.items() if not value]

print("== G60 ROOT STABILIZER ACTION-TYPE PREREGISTRATION AUDIT 011j ==")
print("PACKET:", record["packet"])
print("MODE:", record["mode"])
print("JSON_SHA256:", sha256(json_path))
print("NOTE_SHA256:", sha256(note_path))
print("LOCKED_HEAD:", record["locked_head"])
print("PREDICTED_ROOT_PROFILE: S3 all-even, orbits 2+3")
print("PREDICTED_ORDERED_DUAD_PROFILE: S3 mixed-parity, orbits 1+1+3")
print("STABILIZER_CENSUS_PERFORMED: false")
print("OUTCOME_ORDER:", record["outcome_order"])
print("CHECK_COUNT:", len(checks))
print("FAILED_CHECK_COUNT:", len(failed))
for key, value in checks.items():
    print("CHECK", key + ":", str(value).lower())
print("PREREGISTRATION_PASS:", str(not failed).lower())
print("FAILED_CHECKS:", failed)
print("REPLACEMENT_SOURCE_A_SET_CONSTRUCTED: false")
print("ORIENTATION_SELECTED: false")
print("MANUSCRIPT_MUTATED: false")
print("PHYSICAL_CLAIM: false")
