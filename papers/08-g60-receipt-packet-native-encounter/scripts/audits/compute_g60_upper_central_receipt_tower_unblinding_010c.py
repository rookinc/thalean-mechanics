import hashlib
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

project = Path(sys.argv[1]).resolve()
output_path = Path(sys.argv[2]).resolve()

phase_a_path = (
    project
    / "artifacts/json"
    / "g60_upper_central_series_blind_census_010b.v1.json"
)
tower_path = (
    project
    / "artifacts/json"
    / "g60_native_receipt_tower_theorem_009.v1.json"
)

action_path = Path(
    "/data/data/com.termux/files/home/dev/cori/research/mathematics/"
    "42-graph-automorphism-groups/artifacts/json/"
    "native_g60_fiber_product_isomorphism_044.json"
)
edge_path = Path(
    "/data/data/com.termux/files/home/dev/cori/research/physics/"
    "quantum_mechanics/01-the-electron-spins-twice/paper/data/"
    "g60_local_edges.csv"
)

expected_hashes = {
    "phase_a_010b": (
        "6c69d4e6c6a5eca1c5b7d15840a8958cc93eff5a13c1fe62a8840fe2bf0e8f26"
    ),
    "tower_009": (
        "894831f19bcdcc289f30cee96cdef51a4d0e5990b171cf0eed7355c9d6a254d4"
    ),
    "action": (
        "b37313b135495752b11e525bb61979163fdf54aec4be4f5d027dcee64c9efc21"
    ),
    "edges": (
        "c700a185fab6a5f434da09b7acb716b96c76170774bee946af8ea907e4fe7f9f"
    ),
}

receipt_authorities = {
    "blind_census_002": {
        "path": project / (
            "artifacts/receipts/"
            "g60_native_semiregular_receipt_action_census_002_mac.txt"
        ),
        "sha256": (
            "9d0f1ef5975cd8cd2575192012c8bfeefe15c2856d6646e827ffc4ada851f383"
        ),
    },
    "blind_adjudication_003": {
        "path": project / (
            "artifacts/receipts/"
            "g60_blind_receipt_action_adjudication_003.txt"
        ),
        "sha256": (
            "f49281a06fd90336e4bae5ca9221ee9457e76399ccb2e890b9794887f242ec14"
        ),
    },
    "binary_unblinding_004": {
        "path": project / (
            "artifacts/receipts/"
            "g60_normal_binary_deck_unblinding_004.txt"
        ),
        "sha256": (
            "339058c1fe40c50577eafcad3bda2ded753cbca7137a31c9aa7dbe5023f042c7"
        ),
    },
    "binary_voltage_005": {
        "path": project / (
            "artifacts/receipts/"
            "g60_native_binary_voltage_holonomy_005.txt"
        ),
        "sha256": (
            "fd57c49e368b5e1927e37bae7d8104a16c5fca5e4e64c554e9d70cde2b14ce2b"
        ),
    },
    "v4_unblinding_007": {
        "path": project / (
            "artifacts/receipts/"
            "g60_normal_v4_g15_quotient_unblinding_007.txt"
        ),
        "sha256": (
            "0a5f257592d3ce6d9553c0f6b9ef529282fbe5ede3bdac557e3658ff8d002f17"
        ),
    },
    "v4_voltage_008": {
        "path": project / (
            "artifacts/receipts/"
            "g60_native_v4_voltage_certificate_comparison_008.txt"
        ),
        "sha256": (
            "08b67ac74e0cf88b80a27ce0021200c1c2566b046e294bf72bfb85dd14c3eaa0"
        ),
    },
}

def sha256_file(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def git_output(*args):
    result = subprocess.run(
        ["git", "-C", str(project), *args],
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout.rstrip("\n")

def status_hash(text):
    return hashlib.sha256((text + "\n").encode("utf-8")).hexdigest()

status_before = git_output("status", "--short")
head_before = git_output("--no-pager", "show", "-s", "--oneline", "HEAD")

phase_a_sha = sha256_file(phase_a_path)
tower_sha = sha256_file(tower_path)
action_sha = sha256_file(action_path)
edge_sha = sha256_file(edge_path)

phase_a = json.loads(phase_a_path.read_text(encoding="utf-8"))
tower = json.loads(tower_path.read_text(encoding="utf-8"))

receipt_hash_results = {}
for name, authority in receipt_authorities.items():
    path = authority["path"]
    actual = sha256_file(path) if path.is_file() else None
    receipt_hash_results[name] = {
        "path": str(path),
        "expected_sha256": authority["sha256"],
        "actual_sha256": actual,
        "exists": path.is_file(),
        "hash_match": actual == authority["sha256"],
    }

identity_index = phase_a["group_reconstruction"]["identity_index"]
z1_members = phase_a["central_series"]["center_member_indices"]
z2_members = phase_a["central_series"]["second_center_member_indices"]
z3_members = phase_a["central_series"]["third_center_member_indices"]

chain = tower["normal_subgroup_chain"]
prior_c2 = chain["C2"]
prior_v4 = chain["V4"]

prior_c2_members = prior_c2.get(
    "member_indices",
    [identity_index, prior_c2["generator_index"]],
)
prior_c2_members = sorted(prior_c2_members)
prior_v4_members = sorted(prior_v4["member_indices"])

binary_quotient = tower["quotient_tower"]["binary_quotient"]
v4_quotient = tower["quotient_tower"]["v4_quotient"]
intermediate = tower["quotient_tower"]["intermediate_factor"]

binary_voltage = tower["voltage_and_holonomy"]["G60_over_G30"]
v4_voltage = tower["voltage_and_holonomy"]["G60_over_G15"]

phase_a_z1 = phase_a["native_graph_action"]["central_layer_profiles"]["Z1"]
phase_a_z2 = phase_a["native_graph_action"]["central_layer_profiles"]["Z2"]

checks = {
    "phase_a_head_locked": head_before.startswith("0be43e1 "),
    "phase_a_json_hash": phase_a_sha == expected_hashes["phase_a_010b"],
    "tower_009_json_hash": tower_sha == expected_hashes["tower_009"],
    "action_hash": action_sha == expected_hashes["action"],
    "raw_edge_hash": edge_sha == expected_hashes["edges"],
    "all_prior_receipt_hashes": all(
        row["hash_match"] for row in receipt_hash_results.values()
    ),
    "phase_a_frozen": phase_a["boundary"]["phase_a_result_frozen"] is True,
    "phase_a_was_blind": phase_a["boundary"]["unblinding_performed"] is False,
    "phase_a_exact_target": (
        phase_a["classification"]["preregistered_outcome"] == "exact_target"
    ),
    "tower_009_audit_pass": tower["audit_pass"] is True,
    "tower_009_all_checks_pass": all(tower["checks"].values()),
    "Z1_equals_prior_C2": sorted(z1_members) == prior_c2_members,
    "Z2_equals_prior_V4": sorted(z2_members) == prior_v4_members,
    "Z1_proper_subset_Z2": (
        set(z1_members) < set(z2_members)
    ),
    "upper_central_series_stabilizes_at_Z2": (
        sorted(z3_members) == sorted(z2_members)
    ),
    "prior_C2_class_is_22": prior_c2["blind_class_index"] == 22,
    "prior_V4_class_is_20": prior_v4["blind_class_index"] == 20,
    "prior_C2_normal": (
        prior_c2["normal_under_full_automorphism_group"] is True
    ),
    "prior_V4_normal": (
        prior_v4["normal_under_full_automorphism_group"] is True
    ),
    "prior_C2_inside_V4": chain["C2_is_subgroup_of_V4"] is True,
    "normal_C2_unique": tower["checks"]["normal_c2_unique"] is True,
    "normal_V4_unique": tower["checks"]["normal_v4_unique"] is True,
    "Z1_semiregular": phase_a_z1["semiregular"] is True,
    "Z1_free_30_orbits": (
        phase_a_z1["vertex_orbit_count"] == 30
        and phase_a_z1["vertex_orbit_size_profile"] == {"2": 30}
    ),
    "Z1_no_edge_inversion": (
        phase_a_z1["edge_inversion_failure_member_count"] == 0
    ),
    "Z1_local_covering": (
        phase_a_z1["local_covering_failure_count"] == 0
    ),
    "Z2_semiregular": phase_a_z2["semiregular"] is True,
    "Z2_free_15_orbits": (
        phase_a_z2["vertex_orbit_count"] == 15
        and phase_a_z2["vertex_orbit_size_profile"] == {"4": 15}
    ),
    "Z2_no_edge_inversion": (
        phase_a_z2["edge_inversion_failure_member_count"] == 0
    ),
    "Z2_local_covering": (
        phase_a_z2["local_covering_failure_count"] == 0
    ),
    "Z1_quotient_counts_30_60": (
        phase_a_z1["quotient_vertex_count"] == 30
        and phase_a_z1["quotient_edge_count"] == 60
    ),
    "Z2_quotient_counts_15_30": (
        phase_a_z2["quotient_vertex_count"] == 15
        and phase_a_z2["quotient_edge_count"] == 30
    ),
    "Z1_exact_labeled_G30_transfer": (
        sorted(z1_members) == prior_c2_members
        and binary_quotient["exact_historical_match"] is True
        and binary_quotient["vertex_count"] == 30
        and binary_quotient["edge_count"] == 60
        and binary_quotient["fiber_size"] == 2
        and tower["checks"]["c2_exact_g30_quotient"] is True
    ),
    "Z2_exact_labeled_G15_transfer": (
        sorted(z2_members) == prior_v4_members
        and v4_quotient["exact_labeled_historical_match"] is True
        and v4_quotient["vertex_count"] == 15
        and v4_quotient["edge_count"] == 30
        and v4_quotient["fiber_size"] == 4
        and tower["checks"]["v4_exact_g15_quotient"] is True
    ),
    "induced_G30_to_G15_factor_exact": (
        intermediate["edge_factorization_exact"] is True
        and intermediate["fiber_size"] == 2
        and intermediate["quotient_group"] == "V4_over_C2"
        and tower["checks"]["tower_factorization_exact"] is True
    ),
    "Z1_binary_voltage_exact_reconstruction_transfer": (
        sorted(z1_members) == prior_c2_members
        and binary_voltage["receipt_group"] == "C2"
        and binary_voltage["exact_reconstruction"] is True
        and binary_voltage["connected"] is True
        and binary_voltage["holonomy_image"] == "C2"
        and tower["checks"]["c2_exact_reconstruction"] is True
        and tower["checks"]["c2_surjective_holonomy"] is True
    ),
    "Z2_v4_voltage_exact_reconstruction_transfer": (
        sorted(z2_members) == prior_v4_members
        and v4_voltage["receipt_group"] == "V4"
        and v4_voltage["exact_reconstruction"] is True
        and v4_voltage["connected"] is True
        and v4_voltage["holonomy_image"] == "V4"
        and tower["checks"]["v4_exact_reconstruction"] is True
        and tower["checks"]["v4_surjective_holonomy"] is True
    ),
    "Z2_certificate033_identity_chart_transfer": (
        sorted(z2_members) == prior_v4_members
        and v4_voltage["certificate033_match"]
            == "exact_in_identity_label_basis_and_zero_gauge"
        and tower["checks"]["v4_certificate_match"] is True
        and tower["checks"]["v4_identity_chart_match"] is True
    ),
    "blind_spectrum_still_22": (
        tower["blind_native_spectrum"]["conjugacy_class_count"] == 22
    ),
    "no_smallest_order_selector": True,
    "no_replacement_selector": True,
}

failed_checks = [
    name for name, passed in checks.items()
    if not passed
]

classification = (
    "upper_central_series_exactly_selects_certified_C2_V4_receipt_tower"
    if not failed_checks
    else "upper_central_receipt_tower_unblinding_failed_or_weakened"
)

status_after = git_output("status", "--short")
head_after = git_output("--no-pager", "show", "-s", "--oneline", "HEAD")
repository_preserved = (
    status_before == status_after
    and head_before == head_after
)

result = {
    "packet": "g60_upper_central_receipt_tower_unblinding_010c",
    "version": 1,
    "created_at": datetime.now().astimezone().isoformat(),
    "mode": "read_only_phase_b_unblinding_candidate",
    "authorities": {
        "phase_a_010b": {
            "path": str(phase_a_path),
            "sha256": phase_a_sha,
            "expected_sha256": expected_hashes["phase_a_010b"],
            "hash_match": phase_a_sha == expected_hashes["phase_a_010b"],
        },
        "receipt_tower_009": {
            "path": str(tower_path),
            "sha256": tower_sha,
            "expected_sha256": expected_hashes["tower_009"],
            "hash_match": tower_sha == expected_hashes["tower_009"],
        },
        "action_sha256": action_sha,
        "raw_edge_sha256": edge_sha,
        "prior_receipts": receipt_hash_results,
    },
    "frozen_phase_a": {
        "identity_index": identity_index,
        "Z1_order": len(z1_members),
        "Z1_member_indices": z1_members,
        "Z2_order": len(z2_members),
        "Z2_member_indices": z2_members,
        "Z3_order": len(z3_members),
        "Z3_member_indices": z3_members,
        "preregistered_outcome": (
            phase_a["classification"]["preregistered_outcome"]
        ),
    },
    "unblinded_prior_chain": {
        "normal_C2_blind_class_index": prior_c2["blind_class_index"],
        "normal_C2_member_indices": prior_c2_members,
        "normal_V4_blind_class_index": prior_v4["blind_class_index"],
        "normal_V4_member_indices": prior_v4_members,
        "C2_is_subgroup_of_V4": chain["C2_is_subgroup_of_V4"],
    },
    "exact_subgroup_equalities": {
        "Z1_equals_blind_class_22_C2": (
            sorted(z1_members) == prior_c2_members
            and prior_c2["blind_class_index"] == 22
        ),
        "Z2_equals_blind_class_20_V4": (
            sorted(z2_members) == prior_v4_members
            and prior_v4["blind_class_index"] == 20
        ),
        "Z1_proper_subset_Z2": set(z1_members) < set(z2_members),
        "Z3_equals_Z2": sorted(z3_members) == sorted(z2_members),
    },
    "quotient_transfer": {
        "logical_basis": (
            "Exact subgroup equality transfers the previously certified "
            "orbit partitions and labeled quotient maps to Z1 and Z2."
        ),
        "Z1_exact_labeled_G30": checks["Z1_exact_labeled_G30_transfer"],
        "Z2_exact_labeled_G15": checks["Z2_exact_labeled_G15_transfer"],
        "induced_G30_to_G15_factor_exact": (
            checks["induced_G30_to_G15_factor_exact"]
        ),
        "Z1_quotient_vertex_count": phase_a_z1["quotient_vertex_count"],
        "Z1_quotient_edge_count": phase_a_z1["quotient_edge_count"],
        "Z2_quotient_vertex_count": phase_a_z2["quotient_vertex_count"],
        "Z2_quotient_edge_count": phase_a_z2["quotient_edge_count"],
    },
    "voltage_transfer": {
        "logical_basis": (
            "Exact subgroup equality transfers the certified binary and "
            "V4 voltage constructions to the upper-central layers."
        ),
        "Z1_binary_voltage_compatible": (
            checks["Z1_binary_voltage_exact_reconstruction_transfer"]
        ),
        "Z1_holonomy_image": binary_voltage["holonomy_image"],
        "Z2_v4_voltage_compatible": (
            checks["Z2_v4_voltage_exact_reconstruction_transfer"]
        ),
        "Z2_holonomy_image": v4_voltage["holonomy_image"],
        "Z2_certificate033_identity_chart_match": (
            checks["Z2_certificate033_identity_chart_transfer"]
        ),
    },
    "selector_accounting": {
        "uses_center": True,
        "uses_second_center": True,
        "uses_upper_central_series": True,
        "uses_subgroup_inclusion": True,
        "uses_third_center_as_stabilization_check": True,
        "uses_smallest_order": False,
        "uses_additional_selector": False,
        "replacement_selector_searched": False,
    },
    "checks": checks,
    "failed_check_count": len(failed_checks),
    "failed_checks": failed_checks,
    "audit_pass": not failed_checks and repository_preserved,
    "classification": classification,
    "theorem_statement_candidate": (
        "The raw native graph determines its full automorphism group. "
        "The first two terms of the upper-central series of that group "
        "are exactly the previously recovered normal C2 and V4 receipt "
        "actions. Their orbit quotients reproduce the exact "
        "G60 -> G30 -> G15 tower."
    ),
    "boundary": {
        "blind_spectrum_class_count": 22,
        "claims_every_receipt_action_uniquely_selected": False,
        "canonical_filtration_selects_one_nested_tower": not failed_checks,
        "phase_b_candidate_only": True,
        "phase_b_result_frozen": False,
        "manuscript_mutated": False,
        "orientation_claim": False,
        "geometry_claim": False,
        "physical_claim": False,
    },
    "repository_preservation": {
        "head_before": head_before,
        "head_after": head_after,
        "status_before_sha256": status_hash(status_before),
        "status_after_sha256": status_hash(status_after),
        "repository_status_preserved": repository_preserved,
        "project_mutation_performed": False,
    },
}

output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(
    json.dumps(result, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

print("== G60 UPPER-CENTRAL RECEIPT TOWER UNBLINDING 010c ==")
print("MODE: read-only Phase B candidate")
print("PHASE_A_HEAD:", head_before)
print("PHASE_A_JSON_SHA256:", phase_a_sha)
print("TOWER_009_JSON_SHA256:", tower_sha)
print("ALL_PRIOR_RECEIPT_HASHES_MATCH:", str(checks["all_prior_receipt_hashes"]).lower())
print("FROZEN_Z1_MEMBER_INDICES:", z1_members)
print("PRIOR_CLASS_22_C2_MEMBER_INDICES:", prior_c2_members)
print("Z1_EQUALS_BLIND_CLASS_22_C2:", str(checks["Z1_equals_prior_C2"]).lower())
print("FROZEN_Z2_MEMBER_INDICES:", z2_members)
print("PRIOR_CLASS_20_V4_MEMBER_INDICES:", prior_v4_members)
print("Z2_EQUALS_BLIND_CLASS_20_V4:", str(checks["Z2_equals_prior_V4"]).lower())
print("Z1_PROPER_SUBSET_Z2:", str(checks["Z1_proper_subset_Z2"]).lower())
print("Z3_EQUALS_Z2:", str(checks["upper_central_series_stabilizes_at_Z2"]).lower())
print("Z1_SEMIREGULAR:", str(checks["Z1_semiregular"]).lower())
print("Z1_FREE_30_ORBITS:", str(checks["Z1_free_30_orbits"]).lower())
print("Z1_NO_EDGE_INVERSION:", str(checks["Z1_no_edge_inversion"]).lower())
print("Z1_LOCAL_COVERING:", str(checks["Z1_local_covering"]).lower())
print("Z2_SEMIREGULAR:", str(checks["Z2_semiregular"]).lower())
print("Z2_FREE_15_ORBITS:", str(checks["Z2_free_15_orbits"]).lower())
print("Z2_NO_EDGE_INVERSION:", str(checks["Z2_no_edge_inversion"]).lower())
print("Z2_LOCAL_COVERING:", str(checks["Z2_local_covering"]).lower())
print("Z1_EXACT_LABELED_G30:", str(checks["Z1_exact_labeled_G30_transfer"]).lower())
print("Z2_EXACT_LABELED_G15:", str(checks["Z2_exact_labeled_G15_transfer"]).lower())
print("INDUCED_G30_TO_G15_FACTOR_EXACT:", str(checks["induced_G30_to_G15_factor_exact"]).lower())
print("Z1_BINARY_VOLTAGE_COMPATIBLE:", str(checks["Z1_binary_voltage_exact_reconstruction_transfer"]).lower())
print("Z1_HOLONOMY_IMAGE:", binary_voltage["holonomy_image"])
print("Z2_V4_VOLTAGE_COMPATIBLE:", str(checks["Z2_v4_voltage_exact_reconstruction_transfer"]).lower())
print("Z2_HOLONOMY_IMAGE:", v4_voltage["holonomy_image"])
print("Z2_CERTIFICATE033_IDENTITY_CHART_MATCH:", str(checks["Z2_certificate033_identity_chart_transfer"]).lower())
print("USES_CENTER: true")
print("USES_SECOND_CENTER: true")
print("USES_UPPER_CENTRAL_SERIES: true")
print("USES_SUBGROUP_INCLUSION: true")
print("USES_SMALLEST_ORDER: false")
print("USES_ADDITIONAL_SELECTOR: false")
print("BLIND_SPECTRUM_CLASS_COUNT:", tower["blind_native_spectrum"]["conjugacy_class_count"])
print("CHECK_COUNT:", len(checks))
print("FAILED_CHECK_COUNT:", len(failed_checks))
for name, passed in checks.items():
    print("CHECK", name + ":", str(passed).lower())
print("REPOSITORY_STATUS_PRESERVED:", str(repository_preserved).lower())
print("AUDIT_PASS:", str(not failed_checks and repository_preserved).lower())
print("CLASSIFICATION:", classification)
print("PHASE_B_RESULT_FROZEN: false")
print("MANUSCRIPT_MUTATED: false")
print("ORIENTATION_CLAIM: false")
print("PHYSICAL_CLAIM: false")
print("CANDIDATE_JSON:", output_path)
print("CANDIDATE_JSON_SHA256:", sha256_file(output_path))
