#!/usr/bin/env python3

import hashlib
import json
import pathlib
import subprocess
import sys

project = pathlib.Path(sys.argv[1]).resolve()
maker_path = pathlib.Path(sys.argv[2]).resolve()
candidate_path = pathlib.Path(sys.argv[3]).resolve()

expected_head = "9f0a1f5 Lock G60 local D8 inversion variance"
expected_maker_hash = (
    "f9343daeadd980722d63915303a755a1029fe7e13e7ed8d18b9333d73505a36c"
)
expected_candidate_hash = (
    "61af21d541a2f7e47ea152fdd71620ac79fb8d0bfd3576b7629adf45b8eae5c8"
)

expected_authorities = {
    "g60_binary_torsor_action_character_probe_012c.v1.json":
        "b08d3012ed20301897baa771ed99ecd6a859b8e7d1ef5b31c497652287962d76",
    "g60_local_D8_inversion_variance_census_012e.v1.json":
        "a42aed2a1b56144285fd0b2e575a7f932eb7de93b636e49b55cb9a7bd498328a",
    "g60_native_d8_chart_coherence_census_011w.v1.json":
        "e5630a02b4e4c28caac017906aebae10b00c5b1a8e1ccdf640a414c1174f6919",
    "g60_native_d8_outer_c2_selector_census_011y.v1.json":
        "d5a9036cf96aa97dd8848cd947bff4d07c711db0db2e3dca3ad13ec1c9cdfdab",
    "g60_gauge_covariant_update_census_012a.v1.json":
        "4e6936b9b48c6f033b826df7c3ad4ac70ec3480129c5c73ec6a24630077096d2",
    "g60_full_A_orientation_character_extension_census_011o.v1.json":
        "ad684db8bb65c5eb731c972d33e685ffc18a947f63c9ba4e9758f815821f0941",
}

def sha256_file(path):
    digest = hashlib.sha256()
    with pathlib.Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

def git(*args):
    return subprocess.check_output(
        ["git", "--no-pager", *args],
        cwd=project,
        text=True,
    ).strip()

with candidate_path.open(encoding="utf-8") as handle:
    data = json.load(handle)

pred = data["predictions"]
defs = data["definitions"]
boundary = data["boundary"]
authorities = data["authorities"]

checks = []

def check(name, condition):
    checks.append((name, bool(condition)))

check("head", git("show", "-s", "--format=%h %s", "HEAD") == expected_head)
check("maker_hash", sha256_file(maker_path) == expected_maker_hash)
check("candidate_hash", sha256_file(candidate_path) == expected_candidate_hash)
check("packet", data["packet"] == "g60_variance_completed_chart_preregistration_012f")
check(
    "mode",
    data["mode"]
    == "temporary_read_only_variance_completed_chart_preregistration",
)
check("locked_head", data["locked_head"] == expected_head)
check("authority_count", len(authorities) == 6)

authority_names = {
    pathlib.Path(path).name
    for path in authorities
}
check("authority_names", authority_names == set(expected_authorities))

authority_hashes_ok = True
for path_string, row in authorities.items():
    path = pathlib.Path(path_string)
    name = path.name
    expected = expected_authorities.get(name)
    if (
        expected is None
        or not path.is_file()
        or sha256_file(path) != expected
        or row["expected_sha256"] != expected
        or row["sha256"] != expected
        or row["hash_match"] is not True
    ):
        authority_hashes_ok = False
check("authority_hashes", authority_hashes_ok)

check("ordinary_chart_definition", defs["ordinary_chart"] == "c(x*y) = c(x)c(y)")
check("opposite_chart_definition", defs["opposite_chart"] == "c_minus = c composed with iota")
check(
    "anti_law_definition",
    defs["opposite_chart_law"]
    == "c_minus(x*y) = c_minus(y)c_minus(x)",
)
check(
    "extended_symmetry_definition",
    defs["extended_local_symmetry"]
    == "Aut_plusminus(D8) = Aut(D8) x C2_variance",
)
check(
    "instruction_character_formula",
    "chi_instruction(phi) XOR epsilon"
    in defs["instruction_character"],
)

expected_predictions = {
    "presentation_count": 2,
    "ordinary_chart_count_each": 80,
    "opposite_chart_count_each": 80,
    "variance_completed_chart_count_each": 160,
    "opposite_charts_distinct_each": True,
    "ordinary_and_opposite_chart_sets_disjoint": True,
    "ordinary_chart_homomorphism_failures": 0,
    "opposite_chart_anti_homomorphism_failures": 0,
    "opposite_chart_ordinary_failure_count_each_chart": 24,
    "inversion_commutes_with_all_automorphisms": True,
    "local_automorphism_count_each": 8,
    "extended_transformation_count_each": 16,
    "extended_group_structure": "Aut(D8) x C2",
    "chart_variance_class_count_each": 4,
    "chart_variance_character_image": "C2xC2",
    "three_character_joint_image": "C2xC2xC2",
    "three_character_joint_kernel_order": 2,
    "three_local_binary_characters_pairwise_distinct": True,
    "pairwise_equivariant_bijection_count": 0,
    "locked_presentation_gauge_map_count": 4,
    "all_gauge_maps_commute_with_inversion": True,
    "all_gauge_maps_preserve_variance_sheet": True,
    "all_gauge_maps_preserve_character_decomposition": True,
    "orientation_bridge_common_action_established": False,
    "orientation_to_variance_canonical_map_established": False,
    "orientation_anchor_selects_instruction": False,
    "orientation_anchor_selects_chart_orbit": False,
}
for key, value in expected_predictions.items():
    check("prediction_" + key, pred.get(key) == value)

check("prediction_key_count", set(pred) == set(expected_predictions))
check("required_test_count", len(data["required_tests"]) == 13)
check(
    "classification",
    data["predicted_classification"]
    == (
        "variance_completed_local_chart_system_has_three_independent_"
        "binary_characters_without_canonical_torsor_collapse"
    ),
)
check("all_boundaries_false", all(value is False for value in boundary.values()))
check("repository_no_mutation", data["repository_mutation_performed"] is False)

expected_status = {
    "?? artifacts/json/g60_variance_completed_chart_preregistration_012f.v1.json",
    "?? artifacts/receipts/g60_variance_completed_chart_preregistration_012f.txt",
    "?? notes/g60_variance_completed_chart_preregistration_012f.md",
    "?? scripts/audits/audit_g60_variance_completed_chart_preregistration_012f.py",
    "?? scripts/audits/compute_g60_variance_completed_chart_preregistration_012f.py",
    "?? dist/a-blind-encounter-between-finite-receipt-algebra-and-the-native-g60-graph-overleaf.zip",
    "?? dist/a-blind-encounter-between-finite-receipt-algebra-and-the-native-g60-graph-overleaf.zip.sha256",
    "?? dist/g60-native-receipt-tower-overleaf.zip",
    "?? dist/g60-native-receipt-tower-overleaf.zip.sha256",
    "?? paper/",
    "?? scripts/zipit.sh",
}
status = set(
    line
    for line in git("status", "--short", "--", ".").splitlines()
    if line
)
check("scoped_status_preserved", status == expected_status)

failed = [name for name, passed in checks if not passed]

print("== G60 VARIANCE-COMPLETED CHART PREREGISTRATION GUARD 012f ==")
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
