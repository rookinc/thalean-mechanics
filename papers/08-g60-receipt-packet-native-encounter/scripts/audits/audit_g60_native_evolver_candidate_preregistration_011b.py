import hashlib
import json
from pathlib import Path

project = Path(__file__).resolve().parents[2]
json_path = project / "artifacts/json/g60_native_evolver_candidate_preregistration_011b.v1.json"
note_path = project / "notes/g60_native_evolver_candidate_preregistration_011b.md"

def sha256_file(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

record = json.loads(json_path.read_text(encoding="utf-8"))
authority = record["authority_conclusion"]
family = record["primary_candidate_family"]
ablations = record["frozen_ablation_families"]
boundary = record["interpretive_boundary"]

checks = {
    "packet_name": record["packet"] == "g60_native_evolver_candidate_preregistration_011b",
    "head_b2541d0": record["locked_head"].startswith("b2541d0 "),
    "required_sources_tracked": all(
        row["git_tracked"]
        for row in record["sources"].values()
        if row["authority_role"] == "required"
    ),
    "all_source_hashes_match": all(
        row["hash_match"] for row in record["sources"].values()
    ),
    "paper03_untracked": record["sources"]["orientation_tower_03_advisory_only"]["git_tracked"] is False,
    "paper03_excluded": authority["paper03_used_as_authority"] is False,
    "no_existing_native_H": authority["locked_native_evolver_permutation_already_available"] is False,
    "bridge_test_required": authority["bridge_test_required"] is True,
    "primary_family_U2": family["name"] == "native_order8_receipt_evolver_family_U2",
    "five_primary_requirements": len(family["requirements"]) == 5,
    "candidate_adopted_before_counting": family["adopted_before_element_counting"] is True,
    "three_ablation_families": set(ablations) >= {"U0", "U1", "U2"},
    "no_ablation_fallback": ablations["U0_or_U1_may_not_replace_U2_after_inspection"] is True,
    "complete_reversal_search": record["reversal_witness_search"]["complete_search_required"] is True,
    "six_classification_rules": len(record["classification_rules"]) == 6,
    "U2_not_claimed_nonempty": boundary["U2_nonempty_claim"] is False,
    "evolver_not_selected": boundary["native_evolver_selected"] is False,
    "orientation_not_selected": boundary["orientation_selected"] is False,
    "obstruction_not_verified": boundary["reversal_obstruction_verified"] is False,
    "paper03_not_promoted": boundary["paper03_promoted_to_authority"] is False,
    "fallback_forbidden": boundary["fallback_to_U0_or_U1_allowed"] is False,
    "minimal_datum_search_paused": boundary["minimal_directional_datum_search_allowed"] is False,
    "no_manuscript_mutation": boundary["manuscript_mutation_allowed"] is False,
    "no_geometry_claim": boundary["geometry_claim"] is False,
    "no_physical_claim": boundary["physical_claim"] is False,
    "status_frozen": record["preregistration_status"] == "frozen_before_native_element_census",
    "note_exists": note_path.is_file(),
}

failed = [name for name, passed in checks.items() if not passed]

print("== G60 NATIVE EVOLVER CANDIDATE PREREGISTRATION AUDIT 011b ==")
print("PACKET:", record["packet"])
print("JSON_SHA256:", sha256_file(json_path))
print("NOTE_SHA256:", sha256_file(note_path))
print("LOCKED_HEAD:", record["locked_head"])
for name, row in record["sources"].items():
    print("SOURCE", name + ":", row["sha256"], "tracked=" + str(row["git_tracked"]).lower(), "role=" + row["authority_role"])
print("PRIMARY_FAMILY:", family["name"])
print("PRIMARY_REQUIREMENT_COUNT:", len(family["requirements"]))
print("ABLATION_FAMILIES:", ["U0", "U1", "U2"])
print("ELEMENT_CENSUS_PERFORMED: false")
print("U2_NONEMPTY_CLAIM: false")
print("NATIVE_EVOLVER_SELECTED: false")
print("ORIENTATION_SELECTED: false")
print("CHECK_COUNT:", len(checks))
print("FAILED_CHECK_COUNT:", len(failed))
for name, passed in checks.items():
    print("CHECK", name + ":", str(passed).lower())
print("PREREGISTRATION_PASS:", str(not failed).lower())
print("FAILED_CHECKS:", failed)
print("MANUSCRIPT_MUTATED: false")
print("PHYSICAL_CLAIM: false")
