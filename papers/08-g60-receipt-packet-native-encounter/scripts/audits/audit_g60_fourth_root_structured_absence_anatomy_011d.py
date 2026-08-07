import hashlib
import json
from pathlib import Path

project = Path(__file__).resolve().parents[2]
json_path = project / "artifacts/json/g60_fourth_root_structured_absence_anatomy_011d.v1.json"
raw_path = project / "artifacts/receipts/g60_fourth_root_structured_absence_anatomy_011d_raw_run.txt"
note_path = project / "notes/g60_fourth_root_structured_absence_anatomy_011d.md"
compute_path = project / "scripts/audits/compute_g60_fourth_root_structured_absence_anatomy_011d.py"

expected_script = "149737b18adf7cfac32dcbb3d50b3a6bcb083892a5bb568c3506bef27bbe871b"
expected_candidate = "878d86a3a48df045f592306b00a0a88577bca143b0dfec442bcc8b0c0d3ce0d6"
expected_raw = "dd8c774b23d95d40b342753230dcfe7b0cd0db496824f3148bea3faafa6601ef"

def sha256_file(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

r = json.loads(json_path.read_text(encoding="utf-8"))
g = r["group"]
p = r["power_map_anatomy"]
t = r["observation_receipt_transversality"]
c = r["classification"]
b = r["boundary"]
promotion = r["promotion"]

checks = {
    "packet": r["packet"] == "g60_fourth_root_structured_absence_anatomy_011d",
    "mode_frozen": r["mode"] == "frozen_fourth_root_structured_absence_anatomy",
    "candidate_provenance": promotion["candidate_json_sha256"] == expected_candidate,
    "compute_hash": sha256_file(compute_path) == expected_script,
    "raw_hash": sha256_file(raw_path) == expected_raw,
    "authorities": all(row["hash_match"] for row in r["authorities"].values()),
    "operation_ok": g["operation_ok"] is True,
    "group_order_480": g["order"] == 480,
    "order_profile_exact": g["element_order_profile"] == {
        "1": 1, "2": 83, "3": 20, "4": 140,
        "5": 24, "6": 100, "10": 72, "12": 40,
    },
    "no_order8": g["order8_element_count"] == 0,
    "tau_square_roots_20": p["tau_square_root_count"] == 20,
    "tau_roots_order4": p["tau_square_root_order_profile"] == {"4": 20},
    "tau_roots_one_class": p["tau_square_root_conjugacy_orbit_count"] == 1,
    "all_second_stage_counts_zero": all(
        value == 0 for value in p["tau_square_roots_second_stage_root_counts"].values()
    ),
    "tau_fourth_roots_zero": p["tau_fourth_root_count"] == 0,
    "root_stage_classification": p["root_stage_classification"] == "tau_has_order4_square_roots_but_none_has_a_native_square_root",
    "outer_Z2_roots_zero": (
        len(p["Z2_square_root_fibers"]["65"]) == 0
        and len(p["Z2_square_root_fibers"]["124"]) == 0
    ),
    "transitive": t["full_action_transitive"] is True,
    "stabilizers_order8": t["vertex_stabilizer_order_profile"] == {"8": 60},
    "stabilizer_profile_D8": t["vertex_stabilizer_element_order_profile_counts"] == {
        '{"1": 1, "2": 5, "4": 2}': 60
    },
    "stabilizers_noncyclic": t["cyclic_order8_stabilizer_count"] == 0,
    "stabilizer_Z1_trivial": t["vertex_stabilizer_intersection_Z1_profile"] == {"(0,)": 60},
    "stabilizer_Z2_trivial": t["vertex_stabilizer_intersection_Z2_profile"] == {"(0,)": 60},
    "product_size32": t["vertex_stabilizer_product_Z2_size_profile"] == {"32": 60},
    "quotients_240_120": t["quotient_order_by_Z1"] == 240 and t["quotient_order_by_Z2"] == 120,
    "structured_absence": c["structured_absence_pass"] is True,
    "no_replacement": c["replacement_selector_searched"] is False,
    "larger_carrier_absent": c["larger_carrier_constructed"] is False,
    "result_frozen": b["result_frozen"] is True,
    "no_native_H": b["native_H_found"] is False,
    "orientation_not_instantiated": b["orientation_obstruction_instantiated"] is False,
    "no_manuscript": b["manuscript_mutated"] is False,
    "no_geometry": b["geometry_claim"] is False,
    "no_physics": b["physical_claim"] is False,
    "promotion_unchanged": promotion["mathematical_result_fields_changed"] is False,
    "note_exists": note_path.is_file(),
}

failed = [name for name, passed in checks.items() if not passed]

print("== G60 FOURTH-ROOT STRUCTURED ABSENCE AUDIT 011d ==")
print("PACKET:", r["packet"])
print("JSON_SHA256:", sha256_file(json_path))
print("NOTE_SHA256:", sha256_file(note_path))
print("COMPUTATION_SCRIPT_SHA256:", sha256_file(compute_path))
print("RAW_RUN_RECEIPT_SHA256:", sha256_file(raw_path))
print("ELEMENT_ORDER_PROFILE:", g["element_order_profile"])
print("ORDER8_ELEMENT_COUNT:", g["order8_element_count"])
print("TAU_SQUARE_ROOT_COUNT:", p["tau_square_root_count"])
print("TAU_SQUARE_ROOT_ORDER_PROFILE:", p["tau_square_root_order_profile"])
print("TAU_SQUARE_ROOT_CONJUGACY_ORBITS:", p["tau_square_root_conjugacy_orbit_count"])
print("TAU_FOURTH_ROOT_COUNT:", p["tau_fourth_root_count"])
print("ROOT_STAGE_CLASSIFICATION:", p["root_stage_classification"])
print("VERTEX_STABILIZER_GROUP_TYPE:", t["vertex_stabilizer_group_type"])
print("VERTEX_STABILIZER_ORDER_PROFILE:", t["vertex_stabilizer_order_profile"])
print("STABILIZER_INTERSECTION_Z2_PROFILE:", t["vertex_stabilizer_intersection_Z2_profile"])
print("STABILIZER_PRODUCT_Z2_SIZE_PROFILE:", t["vertex_stabilizer_product_Z2_size_profile"])
print("CHECK_COUNT:", len(checks))
print("FAILED_CHECK_COUNT:", len(failed))
for name, passed in checks.items():
    print("CHECK", name + ":", str(passed).lower())
print("AUDIT_PASS:", str(not failed).lower())
print("FAILED_CHECKS:", failed)
print("EARNED_STATEMENT:", r["earned_statement"])
print("MANUSCRIPT_MUTATED:", str(b["manuscript_mutated"]).lower())
print("PHYSICAL_CLAIM:", str(b["physical_claim"]).lower())
