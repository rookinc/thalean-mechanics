import hashlib
import json
from pathlib import Path

project = Path(__file__).resolve().parents[2]

json_path = project / "artifacts/json/g60_upper_central_receipt_tower_unblinding_010c.v1.json"
raw_receipt = project / "artifacts/receipts/g60_upper_central_receipt_tower_unblinding_010c_raw_run.txt"
note_path = project / "notes/g60_upper_central_receipt_tower_unblinding_010c.md"
compute_path = project / "scripts/audits/compute_g60_upper_central_receipt_tower_unblinding_010c.py"

expected_script_sha = "1b9430e13e4ecf74f38b3f5183c1801ba90eba33270154e37254944d17bd38dc"
expected_candidate_json_sha = "629ca0d60be2bcd3bc27afedfee65f358e20dd4cc7d7e392737c6679a08a071c"
expected_raw_receipt_sha = "ae987a2fad038af4c8f2f120999fdbd420f1c1b7fe7429667906b01ba50ae07d"
expected_phase_a_sha = "6c69d4e6c6a5eca1c5b7d15840a8958cc93eff5a13c1fe62a8840fe2bf0e8f26"
expected_tower_sha = "894831f19bcdcc289f30cee96cdef51a4d0e5990b171cf0eed7355c9d6a254d4"

def sha256_file(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

record = json.loads(json_path.read_text(encoding="utf-8"))
phase_a = record["frozen_phase_a"]
prior = record["unblinded_prior_chain"]
equalities = record["exact_subgroup_equalities"]
quotients = record["quotient_transfer"]
voltages = record["voltage_transfer"]
selector = record["selector_accounting"]
boundary = record["boundary"]
promotion = record["promotion"]

checks = {
    "packet_name": record["packet"] == "g60_upper_central_receipt_tower_unblinding_010c",
    "mode_frozen_phase_b": record["mode"] == "frozen_phase_b_unblinding",
    "phase_a_hash": record["authorities"]["phase_a_010b"]["sha256"] == expected_phase_a_sha,
    "tower_009_hash": record["authorities"]["receipt_tower_009"]["sha256"] == expected_tower_sha,
    "candidate_json_provenance": promotion["candidate_json_sha256"] == expected_candidate_json_sha,
    "compute_script_hash": sha256_file(compute_path) == expected_script_sha,
    "raw_receipt_hash": sha256_file(raw_receipt) == expected_raw_receipt_sha,
    "candidate_checks_all_pass": all(record["checks"].values()),
    "candidate_failed_check_count_zero": record["failed_check_count"] == 0,
    "candidate_audit_pass": record["audit_pass"] is True,
    "Z1_order_2": phase_a["Z1_order"] == 2,
    "Z1_members": phase_a["Z1_member_indices"] == [0, 326],
    "prior_C2_class_22": prior["normal_C2_blind_class_index"] == 22,
    "prior_C2_members": prior["normal_C2_member_indices"] == [0, 326],
    "Z1_exact_C2_equality": equalities["Z1_equals_blind_class_22_C2"] is True,
    "Z2_order_4": phase_a["Z2_order"] == 4,
    "Z2_members": phase_a["Z2_member_indices"] == [0, 65, 124, 326],
    "prior_V4_class_20": prior["normal_V4_blind_class_index"] == 20,
    "prior_V4_members": prior["normal_V4_member_indices"] == [0, 65, 124, 326],
    "Z2_exact_V4_equality": equalities["Z2_equals_blind_class_20_V4"] is True,
    "Z1_proper_subset_Z2": equalities["Z1_proper_subset_Z2"] is True,
    "Z3_equals_Z2": equalities["Z3_equals_Z2"] is True,
    "Z1_exact_G30": quotients["Z1_exact_labeled_G30"] is True,
    "Z2_exact_G15": quotients["Z2_exact_labeled_G15"] is True,
    "tower_factor_exact": quotients["induced_G30_to_G15_factor_exact"] is True,
    "Z1_binary_voltage": voltages["Z1_binary_voltage_compatible"] is True,
    "Z1_holonomy_C2": voltages["Z1_holonomy_image"] == "C2",
    "Z2_v4_voltage": voltages["Z2_v4_voltage_compatible"] is True,
    "Z2_holonomy_V4": voltages["Z2_holonomy_image"] == "V4",
    "certificate033_identity_chart": voltages["Z2_certificate033_identity_chart_match"] is True,
    "uses_center": selector["uses_center"] is True,
    "uses_second_center": selector["uses_second_center"] is True,
    "uses_upper_central_series": selector["uses_upper_central_series"] is True,
    "uses_inclusion": selector["uses_subgroup_inclusion"] is True,
    "no_smallest_order": selector["uses_smallest_order"] is False,
    "no_additional_selector": selector["uses_additional_selector"] is False,
    "no_replacement_selector": selector["replacement_selector_searched"] is False,
    "classification_exact": record["classification"] == "upper_central_series_exactly_selects_certified_C2_V4_receipt_tower",
    "phase_b_frozen": boundary["phase_b_result_frozen"] is True,
    "canonical_one_tower": boundary["canonical_filtration_selects_one_nested_tower"] is True,
    "not_every_receipt_unique": boundary["claims_every_receipt_action_uniquely_selected"] is False,
    "blind_spectrum_22": boundary["blind_spectrum_class_count"] == 22,
    "theorem_claim": boundary["theorem_claim"] is True,
    "no_manuscript_mutation": boundary["manuscript_mutated"] is False,
    "no_orientation_claim": boundary["orientation_claim"] is False,
    "no_geometry_claim": boundary["geometry_claim"] is False,
    "no_physical_claim": boundary["physical_claim"] is False,
    "promotion_result_unchanged": promotion["mathematical_result_fields_changed"] is False,
    "note_exists": note_path.is_file(),
}

failed = [name for name, passed in checks.items() if not passed]

print("== G60 UPPER-CENTRAL RECEIPT TOWER AUDIT 010c ==")
print("PACKET:", record["packet"])
print("MODE:", record["mode"])
print("JSON_SHA256:", sha256_file(json_path))
print("NOTE_SHA256:", sha256_file(note_path))
print("COMPUTATION_SCRIPT_SHA256:", sha256_file(compute_path))
print("RAW_RUN_RECEIPT_SHA256:", sha256_file(raw_receipt))
print("PHASE_A_010B_SHA256:", record["authorities"]["phase_a_010b"]["sha256"])
print("TOWER_009_SHA256:", record["authorities"]["receipt_tower_009"]["sha256"])
print("Z1_MEMBER_INDICES:", phase_a["Z1_member_indices"])
print("CLASS_22_C2_MEMBER_INDICES:", prior["normal_C2_member_indices"])
print("Z1_EQUALS_CLASS_22_C2:", str(equalities["Z1_equals_blind_class_22_C2"]).lower())
print("Z2_MEMBER_INDICES:", phase_a["Z2_member_indices"])
print("CLASS_20_V4_MEMBER_INDICES:", prior["normal_V4_member_indices"])
print("Z2_EQUALS_CLASS_20_V4:", str(equalities["Z2_equals_blind_class_20_V4"]).lower())
print("Z1_PROPER_SUBSET_Z2:", str(equalities["Z1_proper_subset_Z2"]).lower())
print("Z3_EQUALS_Z2:", str(equalities["Z3_equals_Z2"]).lower())
print("Z1_EXACT_LABELED_G30:", str(quotients["Z1_exact_labeled_G30"]).lower())
print("Z2_EXACT_LABELED_G15:", str(quotients["Z2_exact_labeled_G15"]).lower())
print("TOWER_FACTORIZATION_EXACT:", str(quotients["induced_G30_to_G15_factor_exact"]).lower())
print("Z1_BINARY_VOLTAGE_COMPATIBLE:", str(voltages["Z1_binary_voltage_compatible"]).lower())
print("Z1_HOLONOMY_IMAGE:", voltages["Z1_holonomy_image"])
print("Z2_V4_VOLTAGE_COMPATIBLE:", str(voltages["Z2_v4_voltage_compatible"]).lower())
print("Z2_HOLONOMY_IMAGE:", voltages["Z2_holonomy_image"])
print("USES_CENTER:", str(selector["uses_center"]).lower())
print("USES_SECOND_CENTER:", str(selector["uses_second_center"]).lower())
print("USES_SMALLEST_ORDER:", str(selector["uses_smallest_order"]).lower())
print("USES_ADDITIONAL_SELECTOR:", str(selector["uses_additional_selector"]).lower())
print("BLIND_SPECTRUM_CLASS_COUNT:", boundary["blind_spectrum_class_count"])
print("CHECK_COUNT:", len(checks))
print("FAILED_CHECK_COUNT:", len(failed))
for name, passed in checks.items():
    print("CHECK", name + ":", str(passed).lower())
print("AUDIT_PASS:", str(not failed).lower())
print("FAILED_CHECKS:", failed)
print("CLASSIFICATION:", record["classification"])
print("THEOREM_STATEMENT:", record["theorem_statement"])
print("MANUSCRIPT_MUTATED:", str(boundary["manuscript_mutated"]).lower())
