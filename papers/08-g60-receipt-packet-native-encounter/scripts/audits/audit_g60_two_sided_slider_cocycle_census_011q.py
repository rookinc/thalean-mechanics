#!/usr/bin/env python3
import hashlib
import json
import subprocess
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
JSON_PATH = PROJECT / "artifacts/json/g60_two_sided_slider_cocycle_census_011q.v1.json"
RAW_PATH = PROJECT / "artifacts/receipts/g60_two_sided_slider_cocycle_census_011q_raw_run.txt"
NOTE_PATH = PROJECT / "notes/g60_two_sided_slider_cocycle_census_011q.md"
COMPUTE_PATH = PROJECT / "scripts/audits/compute_g60_two_sided_slider_cocycle_census_011q.py"

EXPECTED_JSON_HASH = "63034d0c0fe4a35480bf879209a1da5dae0d5a581eeef063e489d8be1be2459e"
EXPECTED_RAW_HASH = "80a211d001e162059328b5cca7c8a81cb445bcac748ecb14eb0e8572c12abe64"
EXPECTED_NOTE_HASH = "29d7aa584a6e76c75bc28cac452211986dc0142de333d799858c07d5633f0d47"
EXPECTED_COMPUTE_HASH = "e59520d11362c5684a57edbcb5f2224624d5dbb95bdf2359a142f52fca7b3c6b"
EXPECTED_CANDIDATE_HASH = "32612473622fe94010a6cfec95d5634e2d5385c3f699ff5ff1d9bf70e2c07935"
LOCKED_HEAD = "449c222 Preregister G60 two-sided slider cocycle test"

EXPECTED_CLASSIFICATION = (
    "unique_native_axis_D8_class_separates_AB_BA_"
    "without_orientation_sheet_identification"
)
EXPECTED_TYPE_PROFILE = {
    "C2_x_C2_x_C2": 1,
    "C4_x_C2": 3,
    "D8": 3,
    "Q8": 1,
}
EXPECTED_ROUTE_PROFILE = {"D8": 3, "Q8": 1}
EXPECTED_CLASS_HASH = (
    "79f20a7d4c6593e5ff144216a6e41aee5338c22d9c4d8935322877c6b18cfc3b"
)
EXPECTED_REPRESENTATIVE_HASHES = [
    "45f386719813421e4d395b88a498b4982201d7af5e4b761fe1d6baeef10fef63",
    "0bca8a34381bf7990bccc78994be5f491b9630513a054d24fcf598d7260fc78a",
]
EXPECTED_COBOUNDARY_HASHES = [
    "2ec39b8e5281419b8e38ee0825032600b5f9708a1c3289347a7e3507991facae",
    "9803d28903a9f89a9c997b9c76f1a8f100a2ffa4a9e4f57c922fb3281d7eb3b3",
]

def sha256_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def git(*args):
    return subprocess.run(
        ["git", *args],
        cwd=PROJECT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    ).stdout.strip()

data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
base = data["base_register"]
cochains = data["cochain_enumeration"]
cohomology = data["cohomology"]
routes = data["route_test"]
native = data["native_filter"]
prediction = data["prediction_comparison"]
boundary = data["boundary"]
promotion = data["promotion"]
provenance = data["candidate_provenance"]
repository = data["repository"]
authorities = data["authorities"]

selected_classes = native.get("selected_class_rows", [])
selected_class = selected_classes[0] if len(selected_classes) == 1 else {}
selected_cocycles = native.get("selected_cocycle_rows", [])
head = git("show", "-s", "--format=%h %s", "HEAD")

checks = [
    ("packet", data.get("packet") == "g60_two_sided_slider_cocycle_census_011q"),
    ("mode", data.get("mode") == "frozen_complete_normalized_cocycle_census"),
    ("locked_head", data.get("locked_head") == LOCKED_HEAD and head == LOCKED_HEAD),
    ("result_frozen", data.get("result_frozen") is True),
    ("audit_pass_recorded", data.get("audit_pass") is True),
    ("json_hash", sha256_file(JSON_PATH) == EXPECTED_JSON_HASH),
    ("raw_hash", sha256_file(RAW_PATH) == EXPECTED_RAW_HASH),
    ("note_hash", sha256_file(NOTE_PATH) == EXPECTED_NOTE_HASH),
    ("compute_hash", sha256_file(COMPUTE_PATH) == EXPECTED_COMPUTE_HASH),
    ("candidate_hash", provenance.get("candidate_json_sha256") == EXPECTED_CANDIDATE_HASH),
    ("candidate_promoted", promotion.get("candidate_promoted_without_recomputation") is True),
    ("raw_copied", promotion.get("raw_run_receipt_copied_byte_for_byte") is True),
    ("compute_copied", promotion.get("computation_script_copied_byte_for_byte") is True),
    ("failed_run_preserved", promotion.get("failed_profile_uniform_run_preserved") is True),
    ("failed_run_not_promoted", promotion.get("failed_profile_uniform_run_promoted") is False),
    ("gauge_correction", promotion.get("gauge_invariant_profile_correction_applied") is True),
    ("promotion_no_manuscript", promotion.get("manuscript_mutated") is False),
    ("failed_script_hash", provenance.get("failed_profile_uniform_script_sha256") == "5cb15da661a4c255d1d8eb8d7b12a5f66d0b7be87e2e3521a9df89d5f98483c1"),
    ("failed_json_hash", provenance.get("failed_profile_uniform_json_sha256") == "cc3eca8b31f896421548038e9f9895d5ce759ca19ef790178fc0fcdde5683559"),
    ("failed_report_hash", provenance.get("failed_profile_uniform_report_sha256") == "78b97c4ef311630c055b44ba7914969be271d87ca0bebefe313ea5fe840f5792"),
    ("authority_count", len(authorities) == 6),
    ("authority_hashes", all(row.get("hash_match") is True for row in authorities.values())),
    ("base_group_V4", base.get("group") == "V4"),
    ("base_count_4", base.get("visible_state_count") == 4),
    ("base_operation_xor", base.get("operation") == "bitwise_xor"),
    ("base_labels", base.get("labels") == {"0": "1", "1": "a", "2": "b", "3": "ab"}),
    ("native_visible_V4", base.get("native_visible_V4_match") is True),
    ("normalized_functions_512", cochains.get("normalized_function_count") == 512),
    ("normalized_cocycles_16", cochains.get("normalized_cocycle_count") == 16),
    ("normalized_one_cochains_8", cochains.get("normalized_one_cochain_count") == 8),
    ("coboundaries_2", cochains.get("distinct_normalized_coboundary_count") == 2),
    ("cocycle_rows_16", len(cochains.get("cocycle_rows", [])) == 16),
    ("coboundary_rows_2", len(cochains.get("coboundary_rows", [])) == 2),
    ("pair_order_9", len(cochains.get("normalized_pair_order", [])) == 9),
    ("cocycle_bits_9", all(len(row.get("bits", [])) == 9 for row in cochains.get("cocycle_rows", []))),
    ("coboundary_hashes", [row.get("sha256") for row in cochains.get("coboundary_rows", [])] == EXPECTED_COBOUNDARY_HASHES),
    ("class_count_8", cohomology.get("class_count") == 8),
    ("class_rows_8", len(cohomology.get("class_rows", [])) == 8),
    ("class_indices", [row.get("class_index") for row in cohomology.get("class_rows", [])] == list(range(8))),
    ("two_representatives_each", cohomology.get("all_classes_have_two_representatives") is True),
    ("representative_counts", all(row.get("representative_count") == 2 for row in cohomology.get("class_rows", []))),
    ("profiles_uniform", all(row.get("profile_uniform") is True for row in cohomology.get("class_rows", []))),
    ("operations_valid", cohomology.get("all_extension_operations_valid") is True),
    ("operation_failures_zero", all(
        row.get("associativity_failure_count") == 0
        and row.get("identity_failure_count") == 0
        and row.get("inverse_failure_count") == 0
        for row in cohomology.get("class_rows", [])
    )),
    ("extension_type_profile", cohomology.get("extension_type_class_profile") == EXPECTED_TYPE_PROFILE),
    ("route_pair", routes.get("route_pair") == ["A_then_B", "B_then_A"]),
    ("visible_endpoint_ab", routes.get("visible_endpoint") == "ab"),
    ("route_cocycles_8", routes.get("route_separating_cocycle_count") == 8),
    ("route_classes_4", routes.get("route_separating_class_count") == 4),
    ("route_indices", routes.get("route_separating_class_indices") == [2, 3, 6, 7]),
    ("route_type_profile", routes.get("route_separating_type_profile") == EXPECTED_ROUTE_PROFILE),
    ("route_classes_nonabelian", routes.get("all_route_separating_classes_nonabelian") is True),
    ("native_type_D8", native.get("native_authority_group_type") == "D8"),
    ("native_order_profile", native.get("native_authority_order_profile") == {"1": 1, "2": 5, "4": 2}),
    ("native_center_2", native.get("native_authority_center_order") == 2),
    ("declared_signature", native.get("declared_axis_square_signature") == {"a": 1, "b": 0, "ab": 0}),
    ("native_D8_match", native.get("native_abstract_D8_match") is True),
    ("selected_class_count_1", native.get("selected_class_count") == 1 and len(selected_classes) == 1),
    ("selected_cocycle_count_2", native.get("selected_cocycle_count") == 2 and len(selected_cocycles) == 2),
    ("selected_class_index_6", selected_class.get("class_index") == 6),
    ("selected_class_hash", selected_class.get("class_sha256") == EXPECTED_CLASS_HASH),
    ("selected_class_D8", selected_class.get("group_type") == "D8"),
    ("selected_order_profile", selected_class.get("order_profile") == {"1": 1, "2": 5, "4": 2}),
    ("selected_center_2", selected_class.get("center_order") == 2),
    ("selected_central_flip", selected_class.get("central_flip_in_center") is True),
    ("selected_signature", selected_class.get("square_signature") == {"a": 1, "b": 0, "ab": 0}),
    ("selected_profile_uniform", selected_class.get("profile_uniform") is True),
    ("selected_same_endpoint", selected_class.get("same_visible_endpoint") is True),
    ("selected_side_discrepancy_1", selected_class.get("side_discrepancy") == 1),
    ("selected_opposite_sides", selected_class.get("opposite_central_sides") is True),
    ("selected_representative_hashes", selected_class.get("representative_sha256s") == EXPECTED_REPRESENTATIVE_HASHES),
    ("selected_cocycle_hashes", [row.get("cocycle_sha256") for row in selected_cocycles] == EXPECTED_REPRESENTATIVE_HASHES),
    ("selected_cocycle_endpoints", all(
        row.get("AB", [None])[0] == 3
        and row.get("BA", [None])[0] == 3
        for row in selected_cocycles
    )),
    ("selected_cocycle_opposite_sides", all(
        row.get("AB", [None, None])[1] != row.get("BA", [None, None])[1]
        and row.get("side_discrepancy") == 1
        for row in selected_cocycles
    )),
    ("selected_gauge_related", native.get("selected_representatives_gauge_related") is True),
    ("selected_separates_AB_BA", native.get("selected_class_separates_AB_BA") is True),
    ("counts_match", prediction.get("counts_match") is True),
    ("type_profile_matches", prediction.get("extension_type_profile_matches") is True),
    ("route_counts_match", prediction.get("route_counts_match") is True),
    ("native_selection_matches", prediction.get("native_selection_matches") is True),
    ("prediction_comparison", prediction.get("prediction_matches") is True),
    ("prediction_matches", data.get("prediction_matches") is True),
    ("classification", data.get("classification") == EXPECTED_CLASSIFICATION),
    ("slider_constructed", boundary.get("two_sided_slider_cocycle_constructed") is True),
    ("native_class_selected", boundary.get("native_axis_class_selected") is True),
    ("AB_BA_distinguished", boundary.get("AB_BA_distinguished_in_selected_class") is True),
    ("finite_extension_candidate", boundary.get("finite_central_extension_theorem_candidate") is True),
    ("no_unique_representative", boundary.get("unique_cocycle_representative_selected") is False),
    ("no_sheet_identification", boundary.get("local_side_equals_011o_orientation_sheet") is False),
    ("no_local_global_map", boundary.get("local_to_global_side_map_constructed") is False),
    ("no_update_law", boundary.get("native_update_law_constructed") is False),
    ("no_mechanics_cell", boundary.get("mechanics_state_cell_established") is False),
    ("no_orientation", boundary.get("orientation_selected") is False),
    ("no_global_minimality", boundary.get("global_minimality_claim") is False),
    ("no_manuscript", boundary.get("manuscript_mutated") is False),
    ("no_geometry", boundary.get("geometry_claim") is False),
    ("no_physical_direction", boundary.get("physical_direction_claim") is False),
    ("no_physics", boundary.get("physical_claim") is False),
    ("repository_preserved", repository.get("status_preserved") is True),
    ("candidate_no_project_mutation", repository.get("project_mutation_performed") is False),
    ("earned_statement_present", isinstance(data.get("earned_statement"), str) and len(data["earned_statement"]) > 200),
    ("note_exists", NOTE_PATH.is_file()),
]

failed = [name for name, passed in checks if not passed]

print("== G60 TWO-SIDED SLIDER COCYCLE CENSUS AUDIT 011q ==")
print("PACKET:", data.get("packet"))
print("MODE:", data.get("mode"))
print("JSON_SHA256:", sha256_file(JSON_PATH))
print("NOTE_SHA256:", sha256_file(NOTE_PATH))
print("COMPUTATION_SCRIPT_SHA256:", sha256_file(COMPUTE_PATH))
print("RAW_RUN_RECEIPT_SHA256:", sha256_file(RAW_PATH))
print("NORMALIZED_FUNCTION_COUNT:", cochains.get("normalized_function_count"))
print("NORMALIZED_COCYCLE_COUNT:", cochains.get("normalized_cocycle_count"))
print("COHOMOLOGY_CLASS_COUNT:", cohomology.get("class_count"))
print("EXTENSION_TYPE_CLASS_PROFILE:", cohomology.get("extension_type_class_profile"))
print("ROUTE_SEPARATING_CLASS_COUNT:", routes.get("route_separating_class_count"))
print("NATIVE_SELECTED_CLASS_COUNT:", native.get("selected_class_count"))
print("NATIVE_SELECTED_COCYCLE_COUNT:", native.get("selected_cocycle_count"))
print("SELECTED_CLASS_SHA256:", selected_class.get("class_sha256"))
print("SELECTED_REPRESENTATIVE_SHA256S:", selected_class.get("representative_sha256s"))
print("SELECTED_CLASS_SEPARATES_AB_BA:", str(native.get("selected_class_separates_AB_BA")).lower())
print("CLASSIFICATION:", data.get("classification"))
print("CHECK_COUNT:", len(checks))
print("FAILED_CHECK_COUNT:", len(failed))

for name, passed in checks:
    print("CHECK", name + ":", str(bool(passed)).lower())

print("AUDIT_PASS:", str(not failed).lower())
print("FAILED_CHECKS:", failed)
print("EARNED_STATEMENT:", data.get("earned_statement"))
print("LOCAL_SIDE_EQUALS_011O_ORIENTATION_SHEET:", str(boundary.get("local_side_equals_011o_orientation_sheet")).lower())
print("NATIVE_UPDATE_LAW_CONSTRUCTED:", str(boundary.get("native_update_law_constructed")).lower())
print("MECHANICS_STATE_CELL_ESTABLISHED:", str(boundary.get("mechanics_state_cell_established")).lower())
print("MANUSCRIPT_MUTATED:", str(boundary.get("manuscript_mutated")).lower())
print("PHYSICAL_CLAIM:", str(boundary.get("physical_claim")).lower())

if failed:
    raise SystemExit(1)
