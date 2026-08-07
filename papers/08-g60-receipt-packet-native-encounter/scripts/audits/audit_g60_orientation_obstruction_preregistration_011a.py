import hashlib
import json
from pathlib import Path

project = Path(__file__).resolve().parents[2]
json_path = project / "artifacts/json/g60_orientation_obstruction_preregistration_011a.v1.json"
note_path = project / "notes/g60_orientation_obstruction_preregistration_011a.md"

expected_tower_sha = "63fcdb0ff8e1d243eb5f44dd9cd630a361d777ef609c094a9009b8cc12029f2e"

def sha256_file(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

record = json.loads(json_path.read_text(encoding="utf-8"))
boundary = record["boundary"]
sequence = record["sequencing"]
minimal = record["minimal_additional_datum_standard"]

expected_outcomes = {
    "exact_reversal_obstruction",
    "unique_orientation_selected",
    "self_inverse_collapse",
    "multiple_reversal_orbits",
    "no_exact_evolver_candidate",
    "computation_failure",
}

checks = {
    "packet_name": record["packet"] == "g60_orientation_obstruction_preregistration_011a",
    "tower_hash": record["locked_input"]["sha256"] == expected_tower_sha,
    "tower_hash_match": record["locked_input"]["hash_match"] is True,
    "head_d01b068": record["locked_input"]["locked_commit"].startswith("d01b068 "),
    "six_outcomes_frozen": set(record["frozen_native_outcomes"]) == expected_outcomes,
    "general_theorem_has_five_hypotheses": len(record["general_obstruction_theorem"]["hypotheses"]) == 5,
    "conditional_boundary": record["general_obstruction_theorem"]["theorem_is_conditional_until_native_hypotheses_verified"] is True,
    "necessary_stabilizer_condition": "stabilizer" in minimal["necessary_condition"],
    "sufficiency_requires_unique_selection": "exactly one" in minimal["sufficiency_condition"],
    "minimality_requires_ablation": "ablation" in minimal["minimality_condition"],
    "no_preregistered_winner": minimal["winner_may_not_be_chosen_after_result_inspection"] is True,
    "obstruction_first": sequence["prove_general_obstruction_first"] is True,
    "inventory_second": sequence["inventory_native_evolver_authorities_second"] is True,
    "candidate_before_native_test": sequence["preregister_exact_candidate_before_native_test"] is True,
    "later_program_paused": sequence["extension_evolution_factorization_allowed_now"] is False,
    "orientation_not_selected": boundary["orientation_selected_now"] is False,
    "evolver_not_defined": boundary["exact_evolver_defined_now"] is False,
    "exchange_not_verified": boundary["native_exchange_symmetry_verified_now"] is False,
    "minimal_datum_not_identified": boundary["minimal_directional_datum_identified_now"] is False,
    "no_manuscript_mutation": boundary["manuscript_mutation_allowed"] is False,
    "no_geometry_claim": boundary["geometry_claim"] is False,
    "no_physical_claim": boundary["physical_claim"] is False,
    "status_frozen": record["preregistration_status"] == "frozen_before_evolver_authority_inspection",
    "note_exists": note_path.is_file(),
}

failed = [name for name, passed in checks.items() if not passed]

print("== G60 ORIENTATION OBSTRUCTION PREREGISTRATION AUDIT 011a ==")
print("PACKET:", record["packet"])
print("MODE:", record["mode"])
print("JSON_SHA256:", sha256_file(json_path))
print("NOTE_SHA256:", sha256_file(note_path))
print("LOCKED_TOWER_SHA256:", record["locked_input"]["sha256"])
print("LOCKED_HEAD:", record["locked_input"]["locked_commit"])
print("OUTCOME_ORDER:", record["outcome_priority"])
print("OUTCOME_COUNT:", len(record["frozen_native_outcomes"]))
print("GENERAL_OBSTRUCTION_CONDITIONAL: true")
print("EXACT_EVOLVER_DEFINED: false")
print("ORIENTATION_SELECTED: false")
print("NATIVE_EXCHANGE_SYMMETRY_VERIFIED: false")
print("MINIMAL_DIRECTIONAL_DATUM_IDENTIFIED: false")
print("CHECK_COUNT:", len(checks))
print("FAILED_CHECK_COUNT:", len(failed))
for name, passed in checks.items():
    print("CHECK", name + ":", str(passed).lower())
print("PREREGISTRATION_PASS:", str(not failed).lower())
print("FAILED_CHECKS:", failed)
print("MANUSCRIPT_MUTATED: false")
print("PHYSICAL_CLAIM: false")
