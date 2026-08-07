#!/usr/bin/env python3

import hashlib
import json
import subprocess
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
JSON_PATH = PROJECT / "artifacts/json/g60_parity_twisted_duad_cover_preregistration_011l.v1.json"
NOTE_PATH = PROJECT / "notes/g60_parity_twisted_duad_cover_preregistration_011l.md"

EXPECTED_JSON_HASH = "b576049b323ba72ffcd069070f0941b134241595fad954a3c59d37fa2e57d7a2"
EXPECTED_NOTE_HASH = "53f92b53071b8c5135c1edb9a1c9367350d3733a64a4c686b4e8258db56d55a9"
LOCKED_HEAD = "e5d6876 Lock G60 root stabilizer embedding obstruction"

def sha256_file(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
known = data["known_structure"]
source = data["preregistered_source_action"]
prediction = data["predictions"]
withheld = data["claims_withheld"]
boundary = data["boundary"]

head = subprocess.run(
    ["git", "--no-pager", "show", "-s", "--format=%h %s", "HEAD"],
    cwd=PROJECT,
    check=True,
    capture_output=True,
    text=True,
).stdout.strip()

checks = [
    ("packet", data.get("packet") == "g60_parity_twisted_duad_cover_preregistration_011l"),
    ("mode", data.get("mode") == "post_stabilizer_embedding_preregistration"),
    ("frozen", data.get("status") == "frozen_before_computation"),
    ("head", head == LOCKED_HEAD and data.get("locked_head") == LOCKED_HEAD),
    ("json_hash", sha256_file(JSON_PATH) == EXPECTED_JSON_HASH),
    ("note_hash", sha256_file(NOTE_PATH) == EXPECTED_NOTE_HASH),
    ("authority_count", len(data.get("authorities", {})) == 4),
    ("authority_hashes", all(x.get("hash_match") is True for x in data["authorities"].values())),
    ("authorities_tracked", all(x.get("git_tracked") is True for x in data["authorities"].values())),
    ("group_480", known.get("full_group_order") == 480),
    ("N_240", known.get("canonical_N_order") == 240),
    ("N_index_two", known.get("canonical_N_index_in_A") == 2),
    ("N_normal", known.get("canonical_N_normal") is True),
    ("N_image_S5", known.get("canonical_N_five_point_image") == "S5"),
    ("N_kernel_Z1", known.get("canonical_N_kernel_indices") == [0, 326]),
    ("known_counts", known.get("unordered_duad_count") == 10 and known.get("orientation_root_count") == 20),
    ("source_named", source.get("name") == "parity_twisted_unordered_duad_double_cover"),
    ("source_count_20", source.get("declared_object_count") == 20),
    ("sheet_C2", source.get("sheet_group") == "C2" and source.get("epsilon_values") == [0, 1]),
    ("not_endpoint_ordering", source.get("ordinary_endpoint_ordering_used") is False),
    ("ordered_action_not_reused", source.get("ordered_duad_action_reused") is False),
    ("no_source_construction", source.get("source_action_constructed") is False),
    ("no_source_validation", source.get("source_action_validated") is False),
    ("no_bridge_enumeration", source.get("bridge_enumeration_performed") is False),
    ("no_anchor_ablation", source.get("anchor_ablation_performed") is False),
    ("prediction_declared", prediction.get("prediction_declared_before_computation") is True),
    ("prediction_not_blind", prediction.get("prediction_blind") is False),
    ("predict_transitive", prediction.get("source_action_transitive") is True),
    ("predict_stabilizer_12", prediction.get("source_point_stabilizer_order_in_N") == 12),
    ("predict_even_S3", prediction.get("source_point_stabilizer_image_type") == "all_even_S3"),
    ("predict_orbits_2_3", prediction.get("source_point_stabilizer_orbit_profile") == [2, 3]),
    ("predict_exact_stabilizers", prediction.get("root_and_source_stabilizers_exactly_equal") is True),
    ("predict_two_bridges", prediction.get("unanchored_N_equivariant_bridge_count") == 2),
    ("predict_sheet_reversal", prediction.get("two_bridges_related_by_global_sheet_reversal") is True),
    ("predict_root_inversion", prediction.get("two_bridges_related_by_root_inversion") is True),
    ("predict_anchor_one", prediction.get("anchored_bridge_count") == 1),
    ("predict_without_anchor_two", prediction.get("without_anchor_bridge_count") == 2),
    ("predict_no_complement_choice", prediction.get("complement_choice_required") is False),
    ("fourteen_tests", len(data.get("required_tests", [])) == 14),
    ("eleven_outcomes", len(data.get("outcome_order", [])) == 11),
    ("falsifiers_present", len(data.get("falsifiers", [])) == 7),
    ("no_source_claim", withheld.get("source_action_is_valid") is False),
    ("no_bridge_claim", withheld.get("equivariant_bridge_exists") is False),
    ("no_count_claim", withheld.get("bridge_count_is_two") is False),
    ("no_anchor_claim", withheld.get("anchor_is_sufficient") is False),
    ("no_minimal_datum", withheld.get("minimal_directional_datum_identified") is False),
    ("no_orientation", withheld.get("orientation_selected") is False),
    ("no_replacement_A_set", withheld.get("replacement_source_A_set_constructed") is False),
    ("bounded_test", boundary.get("bounded_test_of_one_preregistered_replacement_source_action") is True),
    ("no_global_minimality", boundary.get("global_minimality_claim") is False),
    ("no_replacement_selector", boundary.get("replacement_selector_searched") is False),
    ("no_manuscript", boundary.get("manuscript_mutated") is False),
    ("no_geometry", boundary.get("geometry_claim") is False),
    ("no_physics", boundary.get("physical_claim") is False),
    ("note_exists", NOTE_PATH.is_file()),
]

failed = [name for name, passed in checks if not passed]

print("== G60 PARITY-TWISTED DUAD COVER PREREGISTRATION AUDIT 011l ==")
print("PACKET:", data.get("packet"))
print("MODE:", data.get("mode"))
print("JSON_SHA256:", sha256_file(JSON_PATH))
print("NOTE_SHA256:", sha256_file(NOTE_PATH))
print("LOCKED_HEAD:", data.get("locked_head"))
print("SOURCE_ACTION:", source.get("name"))
print("DECLARED_OBJECT_COUNT:", source.get("declared_object_count"))
print("PREDICTED_BRIDGE_COUNT:", prediction.get("unanchored_N_equivariant_bridge_count"))
print("PREDICTED_ANCHORED_BRIDGE_COUNT:", prediction.get("anchored_bridge_count"))
print("PREDICTION_BLIND:", str(prediction.get("prediction_blind")).lower())
print("SOURCE_ACTION_CONSTRUCTED:", str(source.get("source_action_constructed")).lower())
print("BRIDGE_ENUMERATION_PERFORMED:", str(source.get("bridge_enumeration_performed")).lower())
print("OUTCOME_ORDER:", data.get("outcome_order"))
print("CHECK_COUNT:", len(checks))
print("FAILED_CHECK_COUNT:", len(failed))

for name, passed in checks:
    print(f"CHECK {name}: {str(passed).lower()}")

print("PREREGISTRATION_PASS:", str(not failed).lower())
print("FAILED_CHECKS:", failed)
print("ORIENTATION_SELECTED:", str(withheld.get("orientation_selected")).lower())
print("MINIMAL_DIRECTIONAL_DATUM_IDENTIFIED:", str(withheld.get("minimal_directional_datum_identified")).lower())
print("MANUSCRIPT_MUTATED:", str(boundary.get("manuscript_mutated")).lower())
print("PHYSICAL_CLAIM:", str(boundary.get("physical_claim")).lower())

if failed:
    raise SystemExit(1)
