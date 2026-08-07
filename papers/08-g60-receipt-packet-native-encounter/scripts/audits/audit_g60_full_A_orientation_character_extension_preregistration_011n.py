#!/usr/bin/env python3

import hashlib
import json
import subprocess
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
JSON_PATH = PROJECT / "artifacts/json/g60_full_A_orientation_character_extension_preregistration_011n.v1.json"
NOTE_PATH = PROJECT / "notes/g60_full_A_orientation_character_extension_preregistration_011n.md"

EXPECTED_JSON_HASH = "ce0671b9d0ad33880c8b3d043878366abe885438976481f6fef3fbde16c21097"
EXPECTED_NOTE_HASH = "c151a8da092897830661a0e99bad2d2b6cc9590d181e36af1260664b41580a07"
LOCKED_HEAD = "dcefe45 Lock G60 parity-twisted orientation bridge"

def sha256_file(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
known = data["known_structure"]
characters = data["preregistered_characters"]
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
    ("packet", data.get("packet") == "g60_full_A_orientation_character_extension_preregistration_011n"),
    ("mode", data.get("mode") == "post_twisted_N_bridge_character_extension_preregistration"),
    ("frozen", data.get("status") == "frozen_before_computation"),
    ("head", data.get("locked_head") == LOCKED_HEAD and head == LOCKED_HEAD),
    ("json_hash", sha256_file(JSON_PATH) == EXPECTED_JSON_HASH),
    ("note_hash", sha256_file(NOTE_PATH) == EXPECTED_NOTE_HASH),
    ("authority_count", len(data.get("authorities", {})) == 4),
    ("authority_hashes", all(x.get("hash_match") is True for x in data["authorities"].values())),
    ("authorities_tracked", all(x.get("git_tracked") is True for x in data["authorities"].values())),
    ("group_480", known.get("full_group_order") == 480),
    ("N_240", known.get("canonical_N_order") == 240),
    ("N_index_two", known.get("canonical_N_index") == 2),
    ("N_normal", known.get("canonical_N_normal") is True),
    ("kernel_V4", known.get("five_point_kernel_indices") == [0, 65, 124, 326]),
    ("root_kernel_Z1", known.get("root_action_kernel_indices") == [0, 326]),
    ("residual_elements", known.get("residual_sheet_exchangers") == [65, 124]),
    ("locked_N_bridges", known.get("twisted_N_bridge_count") == 2),
    ("characters_p_n", set(characters) >= {"p", "n", "alpha_0", "alpha_1"}),
    ("alpha_0_p", characters["alpha_0"].get("formula") == "p"),
    ("alpha_1_p_plus_n", characters["alpha_1"].get("formula") == "p+n"),
    ("declared_extensions_two", characters.get("declared_extension_count") == 2),
    ("no_character_computation", characters.get("character_values_computed") is False),
    ("no_homomorphism_test", characters.get("character_homomorphisms_verified") is False),
    ("no_actions", characters.get("full_actions_constructed") is False),
    ("no_bridges", characters.get("bridge_enumeration_performed") is False),
    ("no_anchor_ablation", characters.get("anchor_ablation_performed") is False),
    ("prediction_declared", prediction.get("prediction_declared_before_computation") is True),
    ("prediction_not_blind", prediction.get("prediction_blind") is False),
    ("predict_two_extensions", prediction.get("extension_count") == 2),
    ("predict_both_valid", prediction.get("alpha_0_action_valid") is True and prediction.get("alpha_1_action_valid") is True),
    ("predict_both_transitive", prediction.get("alpha_0_action_transitive") is True and prediction.get("alpha_1_action_transitive") is True),
    ("predict_alpha_0_V4", prediction.get("alpha_0_pointwise_kernel") == "Z2(A)=V4"),
    ("predict_alpha_1_Z1", prediction.get("alpha_1_pointwise_kernel") == "Z1(A)=C2"),
    ("predict_residual_split", prediction.get("alpha_0_residual_elements_fix_sheets") == [65, 124] and prediction.get("alpha_1_residual_elements_exchange_sheets") == [65, 124]),
    ("predict_alpha_0_zero", prediction.get("alpha_0_full_A_bridge_count") == 0),
    ("predict_alpha_1_two", prediction.get("alpha_1_full_A_bridge_count") == 2),
    ("predict_maps_equal_011m", prediction.get("alpha_1_bridge_sha256s_equal_011m") is True),
    ("predict_inversion", prediction.get("alpha_1_two_bridges_inversion_related") is True),
    ("predict_anchor_one", prediction.get("alpha_1_compatible_anchor_selects_unique_bridge") is True),
    ("predict_no_anchor_two", prediction.get("alpha_1_without_anchor_bridge_count") == 2),
    ("predict_unique_character", prediction.get("unique_supporting_character") == "alpha_1=p+n"),
    ("nineteen_tests", len(data.get("required_tests", [])) == 19),
    ("fourteen_outcomes", len(data.get("outcome_order", [])) == 14),
    ("eight_falsifiers", len(data.get("falsifiers", [])) == 8),
    ("no_verified_characters", withheld.get("characters_verified") is False),
    ("no_full_A_source", withheld.get("full_A_source_action_constructed") is False),
    ("no_unique_character_claim", withheld.get("unique_supporting_character_identified") is False),
    ("no_bridge_claim", withheld.get("full_A_equivariant_bridge_exists") is False),
    ("no_count_claim", withheld.get("bridge_count_is_two") is False),
    ("no_anchor_claim", withheld.get("anchor_sufficiency_extended_to_full_A") is False),
    ("no_orientation", withheld.get("orientation_selected") is False),
    ("bounded_test", boundary.get("bounded_two_character_extension_test") is True),
    ("no_replacement_search", boundary.get("replacement_character_search_beyond_p_and_p_plus_n") is False),
    ("no_global_minimality", boundary.get("global_minimality_claim") is False),
    ("no_manuscript", boundary.get("manuscript_mutated") is False),
    ("no_geometry", boundary.get("geometry_claim") is False),
    ("no_physics", boundary.get("physical_claim") is False),
    ("note_exists", NOTE_PATH.is_file()),
]

failed = [name for name, passed in checks if not passed]

print("== G60 FULL-A ORIENTATION CHARACTER-EXTENSION PREREGISTRATION AUDIT 011n ==")
print("PACKET:", data.get("packet"))
print("MODE:", data.get("mode"))
print("JSON_SHA256:", sha256_file(JSON_PATH))
print("NOTE_SHA256:", sha256_file(NOTE_PATH))
print("LOCKED_HEAD:", data.get("locked_head"))
print("DECLARED_EXTENSIONS:", ["alpha_0=p", "alpha_1=p+n"])
print("PREDICTED_ALPHA_0_BRIDGE_COUNT:", prediction.get("alpha_0_full_A_bridge_count"))
print("PREDICTED_ALPHA_1_BRIDGE_COUNT:", prediction.get("alpha_1_full_A_bridge_count"))
print("PREDICTED_UNIQUE_CHARACTER:", prediction.get("unique_supporting_character"))
print("PREDICTION_BLIND:", str(prediction.get("prediction_blind")).lower())
print("FULL_ACTIONS_CONSTRUCTED:", str(characters.get("full_actions_constructed")).lower())
print("BRIDGE_ENUMERATION_PERFORMED:", str(characters.get("bridge_enumeration_performed")).lower())
print("OUTCOME_ORDER:", data.get("outcome_order"))
print("CHECK_COUNT:", len(checks))
print("FAILED_CHECK_COUNT:", len(failed))

for name, passed in checks:
    print(f"CHECK {name}: {str(passed).lower()}")

print("PREREGISTRATION_PASS:", str(not failed).lower())
print("FAILED_CHECKS:", failed)
print("ORIENTATION_SELECTED:", str(withheld.get("orientation_selected")).lower())
print("MANUSCRIPT_MUTATED:", str(boundary.get("manuscript_mutated")).lower())
print("PHYSICAL_CLAIM:", str(boundary.get("physical_claim")).lower())

if failed:
    raise SystemExit(1)
