#!/usr/bin/env python3
import hashlib
import json
import pathlib
import subprocess
import sys

root = pathlib.Path(sys.argv[1]).resolve()
candidate_path = pathlib.Path(sys.argv[2]).resolve()

orientation_path = root / "artifacts/json/g60_full_A_orientation_character_extension_census_011o.v1.json"
update_path = root / "artifacts/json/g60_gauge_covariant_update_census_012a.v1.json"
comparison_path = root / "artifacts/json/g60_binary_torsor_action_character_probe_012c.v1.json"

def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

with candidate_path.open() as handle:
    data = json.load(handle)

checks = []

def check(name, passed):
    checks.append((name, bool(passed)))

head = subprocess.check_output(
    ["git", "--no-pager", "show", "-s", "--format=%h %s", "HEAD"],
    cwd=root,
    text=True,
).strip()

check("head", head == "dc85e32 Lock G60 binary torsor character comparison")
check("candidate_hash", digest(candidate_path) == "16ece0c496bfa2021e60e3c36df523825efbd8db13bcc6b0871fd903da6c50aa")
check("orientation_hash", digest(orientation_path) == data["authorities"]["orientation_011o_sha256"])
check("update_hash", digest(update_path) == data["authorities"]["update_012a_sha256"])
check("comparison_hash", digest(comparison_path) == data["authorities"]["torsor_comparison_012c_sha256"])
check("packet", data["packet"] == "g60_local_D8_inversion_variance_preregistration_012d")
check("mode", data["mode"] == "frozen_predictions_before_local_inversion_variance_census")

p = data["frozen_predictions"]
expected = {
    "presentation_count": 2,
    "local_group_order_each": 8,
    "local_group_nonabelian_each": True,
    "unique_inverse_exists_for_every_element_each": True,
    "inversion_is_involutive_each": True,
    "inversion_fixed_point_count_each": 6,
    "order_four_elements_each": [2, 3],
    "inversion_exchanges_order_four_pair_each": True,
    "ordinary_homomorphism_failure_count_positive_each": True,
    "anti_homomorphism_failure_count_each": 0,
    "inversion_is_local_automorphism_each": False,
    "inversion_is_present_in_Aut_D8_rows_each": False,
    "right_update_to_left_inverse_update_failure_count_each": 0,
    "right_update_to_right_inverse_update_failure_count_positive_each": True,
    "double_inversion_restores_original_element_each": True,
    "predicted_classification": "local_D8_inversion_is_opposite_law_isomorphism_not_Aut_D8_character"
}

for key, value in expected.items():
    check("prediction_" + key, p.get(key) == value)

o = data["orientation_bridge_prediction"]
check("sheet_equals_root_inverse", o["011o_sheet_reversal_equals_target_root_inversion"] is True)
check("restriction_to_D8", o["target_root_inversion_restricts_to_each_native_D8_subgroup"] is True)
check("restriction_anti", o["restriction_is_anti_automorphic_not_Aut_D8"] is True)
check("not_instruction_character", o["orientation_torsor_is_instruction_character"] is False)
check("not_chart_character", o["orientation_torsor_is_chart_character"] is False)
check("not_product_character", o["orientation_torsor_is_product_character"] is False)
check("variance_candidate", o["orientation_torsor_as_opposite_law_variance_candidate"] is True)

check("required_test_count", len(data["required_tests"]) == 9)
check("all_boundaries_false", all(value is False for value in data["boundary"].values()))
check("repository_no_mutation", data["repository_mutation_performed"] is False)

failed = [name for name, passed in checks if not passed]

print("== G60 LOCAL D8 INVERSION VARIANCE PREREGISTRATION GUARD 012d ==")
print("CHECK_COUNT:", len(checks))
print("FAILED_CHECK_COUNT:", len(failed))
for name, passed in checks:
    print("CHECK", name + ":", str(passed).lower())
print("GUARD_PASS:", str(not failed).lower())
print("FAILED_CHECKS:", failed)
print("CANDIDATE_PROMOTED: false")
print("PROJECT_MUTATION_PERFORMED: false")

if failed:
    raise SystemExit(1)
