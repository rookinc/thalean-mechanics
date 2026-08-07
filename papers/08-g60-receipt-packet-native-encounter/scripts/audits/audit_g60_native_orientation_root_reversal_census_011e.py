import hashlib
import json
from pathlib import Path

project = Path(__file__).resolve().parents[2]
j = project / "artifacts/json/g60_native_orientation_root_reversal_census_011e.v1.json"
raw = project / "artifacts/receipts/g60_native_orientation_root_reversal_census_011e_raw_run.txt"
compute = project / "scripts/audits/compute_g60_native_orientation_root_reversal_census_011e.py"
note = project / "notes/g60_native_orientation_root_reversal_census_011e.md"

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

r = json.loads(j.read_text(encoding="utf-8"))
roots = r["orientation_root_set"]
w = r["reversal_witnesses"]
b = r["boundary"]

checks = {
    "packet": r["packet"] == "g60_native_orientation_root_reversal_census_011e",
    "mode": r["mode"] == "frozen_native_orientation_root_reversal_census",
    "compute_hash": sha(compute) == "5c703ea99d73cf1cdbc3ba196c96a52636790c6ddd4beeca10dec7c75c659bf4",
    "raw_hash": sha(raw) == "3ec6eaa00e6725b3c6a1f64a9ceaeb26bc4901b1f76f50701820cb52c6d08a50",
    "authorities": all(r["authorities"][key] for key in ("action_hash_match", "absence_hash_match")),
    "operation": r["group_reconstruction"]["operation_ok"] is True,
    "root_count_20": roots["root_count"] == 20,
    "square_failures_zero": roots["square_failure_count"] == 0,
    "order_failures_zero": roots["order_failure_count"] == 0,
    "inverse_closed": roots["inverse_closure_failure_count"] == 0,
    "no_self_inverse": roots["self_inverse_root_count"] == 0,
    "ten_pairs": roots["inverse_pair_count"] == 10,
    "one_element_orbit": roots["element_conjugacy_orbit_count"] == 1,
    "one_pair_orbit": roots["pair_conjugacy_orbit_count"] == 1,
    "all_reversed": w["all_roots_have_involutive_reverser"] is True,
    "no_missing_witness": w["missing_witness_count"] == 0,
    "all_D8": w["generated_subgroup_order_profile"] == {"8": 320},
    "obstruction": r["reversal_obstruction_verified_on_orientation_root_layer"] is True,
    "classification": r["classification"] == "multiple_reversal_orbits",
    "not_H": b["roots_relabelled_as_absent_H"] is False,
    "orientation_not_selected": b["orientation_selected"] is False,
    "result_frozen": b["result_frozen"] is True,
    "no_larger_carrier": b["larger_carrier_constructed"] is False,
    "no_manuscript": b["manuscript_mutated"] is False,
    "no_physics": b["physical_claim"] is False,
    "promotion_unchanged": r["promotion"]["mathematical_result_fields_changed"] is False,
    "note": note.is_file(),
}
failed = [name for name, passed in checks.items() if not passed]

print("== G60 NATIVE ORIENTATION-ROOT REVERSAL AUDIT 011e ==")
print("JSON_SHA256:", sha(j))
print("NOTE_SHA256:", sha(note))
print("COMPUTATION_SCRIPT_SHA256:", sha(compute))
print("RAW_RUN_RECEIPT_SHA256:", sha(raw))
print("ROOT_COUNT:", roots["root_count"])
print("INVERSE_PAIR_COUNT:", roots["inverse_pair_count"])
print("ELEMENT_CONJUGACY_ORBIT_COUNT:", roots["element_conjugacy_orbit_count"])
print("PAIR_CONJUGACY_ORBIT_COUNT:", roots["pair_conjugacy_orbit_count"])
print("ALL_ROOTS_HAVE_INVOLUTIVE_REVERSER:", str(w["all_roots_have_involutive_reverser"]).lower())
print("GENERATED_SUBGROUP_ORDER_PROFILE:", w["generated_subgroup_order_profile"])
print("CLASSIFICATION:", r["classification"])
print("CHECK_COUNT:", len(checks))
print("FAILED_CHECK_COUNT:", len(failed))
for name, passed in checks.items():
    print("CHECK", name + ":", str(passed).lower())
print("AUDIT_PASS:", str(not failed).lower())
print("FAILED_CHECKS:", failed)
print("EARNED_STATEMENT:", r["earned_statement"])
