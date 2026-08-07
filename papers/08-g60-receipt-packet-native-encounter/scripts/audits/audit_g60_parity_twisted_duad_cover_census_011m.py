#!/usr/bin/env python3

import hashlib
import json
import subprocess
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
JSON_PATH = PROJECT / "artifacts/json/g60_parity_twisted_duad_cover_census_011m.v1.json"
RAW_PATH = PROJECT / "artifacts/receipts/g60_parity_twisted_duad_cover_census_011m_raw_run.txt"
NOTE_PATH = PROJECT / "notes/g60_parity_twisted_duad_cover_census_011m.md"
COMPUTE_PATH = PROJECT / "scripts/audits/compute_g60_parity_twisted_duad_cover_census_011m.py"

EXPECTED_JSON_HASH = "8c556050e4ea028cc41eca4514366c3a0d6baa83620831259151dbed0b046a7e"
EXPECTED_RAW_HASH = "af2ce125c4c3a2ae24c588366245db7e76cb5651630c709633525a48073edfee"
EXPECTED_NOTE_HASH = "88c697d5861e12bb8fa6de011da8f566170b059a0098803b8ff127c6a4294e5e"
EXPECTED_COMPUTE_HASH = "62c25f2195b3da0a3fb7280f8217221a358800bebf703ba63a5d137d2bf2ff81"
EXPECTED_CANDIDATE_HASH = "4ab4ca333fc0b9292cb021da7d4483911f50aa0f62fb176398164761d45ebbd2"
LOCKED_HEAD = "a392373 Preregister G60 parity-twisted duad cover"

def sha256_file(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
group = data["group_reconstruction"]
source = data["source_action"]
stabilizers = data["stabilizer_comparison"]
bridges = data["equivariant_bridges"]
anchors = data["anchor_ablation"]
boundary = data["boundary"]
promotion = data["promotion"]
provenance = data["candidate_provenance"]

head = subprocess.run(
    ["git", "--no-pager", "show", "-s", "--format=%h %s", "HEAD"],
    cwd=PROJECT,
    check=True,
    capture_output=True,
    text=True,
).stdout.strip()

expected_map_hashes = [
    "782dbcb9dae045cfc5dadd1b81f51895e447e981491263e09514c9077dfe1728",
    "bb61e5018270d8954e8115bb9c1fbbcfb07f360ba307c451cb16103ef7336c01",
]

checks = [
    ("packet", data.get("packet") == "g60_parity_twisted_duad_cover_census_011m"),
    ("mode", data.get("mode") == "frozen_complete_parity_twisted_duad_cover_census"),
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
    ("failed_run_not_promoted", promotion.get("failed_preliminary_run_promoted") is False),
    ("authority_count", len(data.get("authorities", {})) == 6),
    ("authority_hashes", all(x.get("hash_match") is True for x in data["authorities"].values())),
    ("group_480", group.get("group_order") == 480),
    ("identity_0", group.get("identity_index") == 0),
    ("closure_zero", group.get("closure_failure_count") == 0),
    ("inverse_zero", group.get("inverse_failure_count") == 0),
    ("operation_ok", group.get("operation_ok") is True),
    ("N_240", group.get("canonical_N_order") == 240),
    ("two_complements", group.get("complement_count") == 2),
    ("S5_120", group.get("five_point_image_order") == 120),
    ("source_name", source.get("name") == "parity_twisted_unordered_duad_double_cover"),
    ("source_count_20", source.get("object_count") == 20 and len(source.get("objects", [])) == 20),
    ("source_identity_zero", source.get("identity_failure_count") == 0),
    ("source_closure_zero", source.get("closure_failure_count") == 0),
    ("source_valid", source.get("action_valid") is True),
    ("source_one_orbit", source.get("orbit_count") == 1),
    ("source_orbit_20", source.get("orbit_size_profile") == [20]),
    ("source_transitive", source.get("transitive") is True),
    ("stabilizer_order_12", stabilizers.get("source_stabilizer_order_profile") == [12]),
    ("stabilizer_image_6", stabilizers.get("source_stabilizer_image_order_profile") == [6]),
    ("one_stabilizer_profile", stabilizers.get("source_stabilizer_image_profile_count") == 1),
    ("twenty_stabilizer_rows", len(stabilizers.get("rows", [])) == 20),
    ("stabilizer_failures_zero", stabilizers.get("exact_match_failure_count") == 0),
    ("stabilizer_failure_rows_empty", stabilizers.get("exact_match_failures") == []),
    ("stabilizers_exact", stabilizers.get("all_source_stabilizers_match_assigned_root_pair") is True),
    ("N_two_bridges", bridges.get("N_bridge_count") == 2),
    ("map_hashes_exact", bridges.get("N_map_sha256s") == expected_map_hashes),
    ("two_bridge_rows", len(bridges.get("N_bridge_rows", [])) == 2),
    ("no_rejected_incomplete", bridges.get("N_rejected_incomplete_roots") == []),
    ("no_rejected_nonbijective", bridges.get("N_rejected_nonbijective_roots") == []),
    ("no_rejected_equivariance", bridges.get("N_rejected_equivariance_rows") == []),
    ("complements_two_each", bridges.get("complement_bridge_counts") == [2, 2]),
    ("complement_maps_equal_N", bridges.get("complement_map_sets_equal_N") is True),
    ("sheet_reversal_zero", bridges.get("sheet_reversal_failure_count") == 0),
    ("root_inversion_zero", bridges.get("root_inversion_failure_count") == 0),
    ("reversal_verified", bridges.get("reversal_relation_verified") is True),
    ("two_reversal_rows", len(bridges.get("reversal_pair_rows", [])) == 2),
    ("anchors_40", anchors.get("compatible_anchor_count") == 40 and len(anchors.get("anchor_rows", [])) == 40),
    ("anchor_profile_one", anchors.get("anchor_bridge_count_profile") == {"1": 40}),
    ("anchors_unique", anchors.get("all_compatible_anchors_select_unique_bridge") is True),
    ("without_anchor_two", anchors.get("without_anchor_bridge_count") == 2),
    ("one_bit_sufficient", anchors.get("one_binary_sheet_choice_sufficient") is True),
    ("classification", data.get("classification") == "exactly_two_inversion_related_bridges_anchor_selects_one"),
    ("prediction_matches", data.get("prediction_matches") is True),
    ("replacement_N_set", boundary.get("replacement_source_N_set_constructed") is True),
    ("not_full_A_set", boundary.get("full_A_equivariant_source_set_constructed") is False),
    ("bounded_sufficiency", boundary.get("bounded_binary_datum_sufficient_within_preregistered_source_action") is True),
    ("no_global_minimality", boundary.get("global_minimality_claim") is False),
    ("no_unanchored_orientation", boundary.get("orientation_selected_without_anchor") is False),
    ("no_manuscript", boundary.get("manuscript_mutated") is False),
    ("no_geometry", boundary.get("geometry_claim") is False),
    ("no_physics", boundary.get("physical_claim") is False),
    ("note_exists", NOTE_PATH.is_file()),
]

failed = [name for name, passed in checks if not passed]

print("== G60 PARITY-TWISTED DUAD COVER CENSUS AUDIT 011m ==")
print("PACKET:", data.get("packet"))
print("MODE:", data.get("mode"))
print("JSON_SHA256:", sha256_file(JSON_PATH))
print("NOTE_SHA256:", sha256_file(NOTE_PATH))
print("COMPUTATION_SCRIPT_SHA256:", sha256_file(COMPUTE_PATH))
print("RAW_RUN_RECEIPT_SHA256:", sha256_file(RAW_PATH))
print("SOURCE_ACTION_VALID:", str(source.get("action_valid")).lower())
print("SOURCE_ORBIT_SIZE_PROFILE:", source.get("orbit_size_profile"))
print("STABILIZER_MATCH_FAILURE_COUNT:", stabilizers.get("exact_match_failure_count"))
print("N_BRIDGE_COUNT:", bridges.get("N_bridge_count"))
print("N_MAP_SHA256S:", bridges.get("N_map_sha256s"))
print("COMPLEMENT_BRIDGE_COUNTS:", bridges.get("complement_bridge_counts"))
print("REVERSAL_RELATION_VERIFIED:", str(bridges.get("reversal_relation_verified")).lower())
print("ANCHOR_BRIDGE_COUNT_PROFILE:", anchors.get("anchor_bridge_count_profile"))
print("CLASSIFICATION:", data.get("classification"))
print("CHECK_COUNT:", len(checks))
print("FAILED_CHECK_COUNT:", len(failed))

for name, passed in checks:
    print(f"CHECK {name}: {str(passed).lower()}")

print("AUDIT_PASS:", str(not failed).lower())
print("FAILED_CHECKS:", failed)
print("EARNED_STATEMENT:", data.get("earned_statement"))
print("REPLACEMENT_SOURCE_N_SET_CONSTRUCTED:", str(boundary.get("replacement_source_N_set_constructed")).lower())
print("ORIENTATION_SELECTED_WITHOUT_ANCHOR:", str(boundary.get("orientation_selected_without_anchor")).lower())
print("MANUSCRIPT_MUTATED:", str(boundary.get("manuscript_mutated")).lower())
print("PHYSICAL_CLAIM:", str(boundary.get("physical_claim")).lower())

if failed:
    raise SystemExit(1)
