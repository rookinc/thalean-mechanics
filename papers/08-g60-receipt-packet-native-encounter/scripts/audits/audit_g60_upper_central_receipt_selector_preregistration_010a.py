import hashlib
import json
from pathlib import Path

project = Path(__file__).resolve().parents[2]
json_path = project / "artifacts/json/g60_upper_central_receipt_selector_preregistration_010a.v1.json"
note_path = project / "notes/g60_upper_central_receipt_selector_preregistration_010a.md"

def sha256_file(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

record = json.loads(json_path.read_text(encoding="utf-8"))

checks = {
    "packet_name": record["packet"] == "g60_upper_central_receipt_selector_preregistration_010a",
    "action_hash_match": record["authorities"]["action"]["hash_match"] is True,
    "edge_hash_match": record["authorities"]["raw_edges"]["hash_match"] is True,
    "mapping_row_count_480": record["authorities"]["action"]["mapping_row_count"] == 480,
    "permutation_degree_60": record["authorities"]["action"]["permutation_degree"] == 60,
    "edge_row_count_120": record["authorities"]["raw_edges"]["edge_row_count"] == 120,
    "phase_a_blind": record["blindness_contract"]["phase"] == "A",
    "historical_fields_unused": record["blindness_contract"]["historical_reference_fields_used"] is False,
    "prior_indices_unused": record["blindness_contract"]["prior_class_member_indices_used"] is False,
    "central_series_not_precomputed": record["blindness_contract"]["central_series_computed_before_preregistration"] is False,
    "member_indices_not_preregistered": record["blindness_contract"]["member_indices_named_in_outcome_predicates"] is False,
    "five_outcomes_frozen": set(record["outcome_predicates"]) == {
        "exact_target",
        "center_only",
        "larger_second_center",
        "unexpected_center",
        "computation_failure",
    },
    "composition_frozen": "p[q[v]]" in record["frozen_group_conventions"]["composition"],
    "commutator_frozen": "inverse(g)*inverse(h)*g*h" in record["frozen_group_conventions"]["commutator"],
    "phase_b_gated": record["phase_b_gate"]["allowed_only_after_phase_a_report_hashed"] is True,
    "no_replacement_selector": record["phase_a_execution_contract"]["replacement_selector_search_in_same_packet"] is False,
    "no_smallest_order_selector": record["interpretive_boundary"]["smallest_order_selector_allowed"] is False,
    "blind_spectrum_preserved": record["interpretive_boundary"]["blind_spectrum_retains_22_admissible_classes"] is True,
    "no_orientation_claim": record["interpretive_boundary"]["orientation_claim"] is False,
    "no_physical_claim": record["interpretive_boundary"]["physical_claim"] is False,
    "no_manuscript_mutation": record["interpretive_boundary"]["manuscript_mutation_allowed"] is False,
    "status_frozen": record["preregistration_status"] == "frozen_before_central_computation",
    "final_freeze_status_present": "status_short_at_final_preregistration_freeze" in record["repository_baseline"],
    "misleading_pre_preregistration_key_absent": "status_short_before_preregistration" not in record["repository_baseline"],
    "status_not_used_as_clean_worktree_claim": record["repository_baseline"]["used_as_clean_worktree_claim"] is False,
    "metadata_only_correction": record["metadata_correction"]["mathematical_predicates_changed"] is False,
    "central_series_not_computed_before_correction": record["metadata_correction"]["central_series_computed_before_correction"] is False,
    "note_exists": note_path.is_file(),
}

failed = [name for name, passed in checks.items() if not passed]

print("== G60 UPPER-CENTRAL PREREGISTRATION AUDIT 010a ==")
print("PACKET:", record["packet"])
print("MODE:", record["mode"])
print("JSON_SHA256:", sha256_file(json_path))
print("NOTE_SHA256:", sha256_file(note_path))
print("ACTION_SHA256:", record["authorities"]["action"]["sha256"])
print("RAW_EDGE_SHA256:", record["authorities"]["raw_edges"]["sha256"])
print("MAPPING_ROW_COUNT:", record["authorities"]["action"]["mapping_row_count"])
print("PERMUTATION_DEGREE:", record["authorities"]["action"]["permutation_degree"])
print("RAW_EDGE_ROW_COUNT:", record["authorities"]["raw_edges"]["edge_row_count"])
print("CENTRAL_SERIES_COMPUTED:", str(record["blindness_contract"]["central_series_computed_before_preregistration"]).lower())
print("HISTORICAL_REFERENCE_FIELDS_USED:", str(record["blindness_contract"]["historical_reference_fields_used"]).lower())
print("PRIOR_CLASS_MEMBER_INDICES_USED:", str(record["blindness_contract"]["prior_class_member_indices_used"]).lower())
print("OUTCOME_ORDER:", record["frozen_outcome_order"])
print("OUTCOME_COUNT:", len(record["outcome_predicates"]))
print("COMPOSITION:", record["frozen_group_conventions"]["composition"])
print("COMMUTATOR:", record["frozen_group_conventions"]["commutator"])
print("PHASE_B_ALLOWED_NOW: false")
print("REPOSITORY_STATUS_SNAPSHOT:", "status_short_at_final_preregistration_freeze")
print("STATUS_USED_AS_CLEAN_WORKTREE_CLAIM:", str(record["repository_baseline"]["used_as_clean_worktree_claim"]).lower())
print("METADATA_CORRECTION_ONLY:", str(not record["metadata_correction"]["mathematical_predicates_changed"]).lower())
print("SMALLEST_ORDER_SELECTOR_ALLOWED:", str(record["interpretive_boundary"]["smallest_order_selector_allowed"]).lower())
print("MANUSCRIPT_MUTATION_ALLOWED:", str(record["interpretive_boundary"]["manuscript_mutation_allowed"]).lower())
print("CHECK_COUNT:", len(checks))
print("FAILED_CHECK_COUNT:", len(failed))
for name, passed in checks.items():
    print("CHECK", name + ":", str(passed).lower())
print("PREREGISTRATION_PASS:", str(not failed).lower())
print("FAILED_CHECKS:", failed)
print("MUTATION_SCOPE: preregistration_packet_only")
print("GROUP_COMPUTATION_PERFORMED: false")
