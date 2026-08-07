import hashlib
import json
from pathlib import Path

project = Path(__file__).resolve().parents[2]
json_path = project / "artifacts/json/g60_native_evolver_census_011c.v1.json"
raw_receipt = project / "artifacts/receipts/g60_native_evolver_census_011c_raw_run.txt"
note_path = project / "notes/g60_native_evolver_census_011c.md"
compute_path = project / "scripts/audits/compute_g60_native_evolver_census_011c.py"

expected_script_sha = "10fad018817ac365ee4ea67346d7180677143e07f353a7bc72b245d088a02ec1"
expected_candidate_json_sha = "7f5935ad9124662bf7314590193f08552135b42bef37d25cb91411f89cda3461"
expected_raw_receipt_sha = "33307657c39ee8d22a282683a18605d19bc32303e2e75da7853a7cf9afe0d493"
expected_prereg_sha = "ee8ed4313bdbb18081a85f9de1e648536106b16fbeee7e49a6a482889d18100a"

def sha256_file(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

record = json.loads(json_path.read_text(encoding="utf-8"))
group = record["group_reconstruction"]
tower = record["native_tower"]
census = record["candidate_census"]
reversal = record["reversal_witness_census"]
classification = record["classification"]
boundary = record["boundary"]
promotion = record["promotion"]

checks = {
    "packet_name": record["packet"] == "g60_native_evolver_census_011c",
    "mode_frozen": record["mode"] == "frozen_native_evolver_census",
    "preregistration_hash": record["authorities"]["prereg"]["actual_sha256"] == expected_prereg_sha,
    "candidate_json_provenance": promotion["candidate_json_sha256"] == expected_candidate_json_sha,
    "compute_script_hash": sha256_file(compute_path) == expected_script_sha,
    "raw_receipt_hash": sha256_file(raw_receipt) == expected_raw_receipt_sha,
    "all_authority_hashes": all(row["hash_match"] for row in record["authorities"].values()),
    "group_order_480": group["group_order"] == 480,
    "identity_index_0": group["identity_index"] == 0,
    "closure_zero": group["closure_failure_count"] == 0,
    "inverse_zero": group["inverse_failure_count"] == 0,
    "order_failures_zero": group["declared_order_failure_count"] == 0,
    "operation_ok": group["operation_ok"] is True,
    "Z1_exact": tower["Z1_member_indices"] == [0, 326],
    "Z2_exact": tower["Z2_member_indices"] == [0, 65, 124, 326],
    "tau_326": tower["tau_index"] == 326,
    "outer_pair_exact": tower["outer_pair_indices"] == [65, 124],
    "U0_empty": census["U0_count"] == 0 and census["U0_member_indices"] == [],
    "U1_empty": census["U1_count"] == 0 and census["U1_member_indices"] == [],
    "U2_empty": census["U2_count"] == 0 and census["U2_member_indices"] == [],
    "no_inverse_pairs": census["U2_inverse_pair_count"] == 0,
    "no_reversal_claim": reversal["local_reversal_obstruction_verified"] is False,
    "classification_no_candidate": classification["frozen_outcome"] == "no_exact_evolver_candidate",
    "primary_family_remains_U2": classification["primary_family"] == "U2",
    "no_fallback": classification["fallback_to_U0_or_U1_used"] is False,
    "no_replacement_selector": classification["replacement_selector_used"] is False,
    "repository_preserved": record["repository_preservation"]["repository_status_preserved"] is True,
    "result_frozen": boundary["result_frozen"] is True,
    "carrier_obstruction": boundary["carrier_obstruction_on_native_60_vertex_action"] is True,
    "larger_carrier_not_constructed": boundary["larger_lifted_carrier_constructed"] is False,
    "orientation_not_selected": boundary["native_evolver_uniquely_selected"] is False,
    "minimal_datum_not_identified": boundary["minimal_directional_datum_identified"] is False,
    "no_manuscript_mutation": boundary["manuscript_mutated"] is False,
    "no_geometry_claim": boundary["geometry_claim"] is False,
    "no_physical_claim": boundary["physical_claim"] is False,
    "promotion_result_unchanged": promotion["mathematical_result_fields_changed"] is False,
    "note_exists": note_path.is_file(),
}

failed = [name for name, passed in checks.items() if not passed]

print("== G60 NATIVE EVOLVER CENSUS AUDIT 011c ==")
print("PACKET:", record["packet"])
print("MODE:", record["mode"])
print("JSON_SHA256:", sha256_file(json_path))
print("NOTE_SHA256:", sha256_file(note_path))
print("COMPUTATION_SCRIPT_SHA256:", sha256_file(compute_path))
print("RAW_RUN_RECEIPT_SHA256:", sha256_file(raw_receipt))
print("PREREGISTRATION_SHA256:", record["authorities"]["prereg"]["actual_sha256"])
print("GROUP_ORDER:", group["group_order"])
print("CLOSURE_FAILURE_COUNT:", group["closure_failure_count"])
print("INVERSE_FAILURE_COUNT:", group["inverse_failure_count"])
print("TAU_INDEX:", tower["tau_index"])
print("U0_COUNT:", census["U0_count"])
print("U1_COUNT:", census["U1_count"])
print("U2_COUNT:", census["U2_count"])
print("U2_INVERSE_PAIR_COUNT:", census["U2_inverse_pair_count"])
print("LOCAL_REVERSAL_OBSTRUCTION_VERIFIED:", str(reversal["local_reversal_obstruction_verified"]).lower())
print("CLASSIFICATION:", classification["frozen_outcome"])
print("FALLBACK_USED:", str(classification["fallback_to_U0_or_U1_used"]).lower())
print("CARRIER_OBSTRUCTION:", str(boundary["carrier_obstruction_on_native_60_vertex_action"]).lower())
print("LARGER_CARRIER_CONSTRUCTED:", str(boundary["larger_lifted_carrier_constructed"]).lower())
print("CHECK_COUNT:", len(checks))
print("FAILED_CHECK_COUNT:", len(failed))
for name, passed in checks.items():
    print("CHECK", name + ":", str(passed).lower())
print("AUDIT_PASS:", str(not failed).lower())
print("FAILED_CHECKS:", failed)
print("EARNED_STATEMENT:", record["earned_statement"])
print("MANUSCRIPT_MUTATED:", str(boundary["manuscript_mutated"]).lower())
print("PHYSICAL_CLAIM:", str(boundary["physical_claim"]).lower())
