#!/usr/bin/env python3

import hashlib
import json
import pathlib
import sys

project = pathlib.Path(sys.argv[1]).resolve()
output = pathlib.Path(sys.argv[2]).resolve()

locked_head = "0843940 Add finite receipt manuscript sprint artifacts"

authorities = {
    "011g": project / "artifacts/json/g60_duad_orientation_bridge_census_011g.v1.json",
    "011m": project / "artifacts/json/g60_parity_twisted_duad_cover_census_011m.v1.json",
    "011o": project / "artifacts/json/g60_full_A_orientation_character_extension_census_011o.v1.json",
}

def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1048576), b""):
            digest.update(block)
    return digest.hexdigest()

packet = {
    "packet":
        "g60_root_relative_sign_kernel_preregistration_013d",
    "mode":
        "temporary_read_only_preregistration",
    "locked_head": locked_head,
    "authorities": {
        label: {
            "path": str(path),
            "sha256": sha256(path),
        }
        for label, path in authorities.items()
    },
    "object_under_test": {
        "carrier": "twenty_orientation_roots",
        "source": "twenty_unordered_duad_epsilon_objects",
        "supporting_full_A_character": "p+n",
        "bridge_count": 2,
        "absolute_sign_selected": False,
        "kernel_definition":
            "K(r,s)=(-1)^(epsilon(r)+epsilon(s))",
    },
    "predictions": {
        "bridge_count": 2,
        "bridge_row_count_each": 20,
        "root_count_each": 20,
        "epsilon_profile_each": {
            "0": 10,
            "1": 10,
        },
        "root_sets_equal": True,
        "bridge_signings_are_exact_complements": True,
        "relative_sign_kernels_equal": True,
        "same_sign_ordered_pair_count": 200,
        "opposite_sign_ordered_pair_count": 200,
        "kernel_rank": 1,
        "kernel_trace": 20,
        "kernel_row_sum_profile": {
            "0": 20,
        },
        "inverse_root_pairs_have_opposite_sign": True,
    },
    "required_tests": [
        "authority_hashes_match",
        "two_bridges",
        "twenty_rows_each",
        "twenty_distinct_roots_each",
        "balanced_epsilon_profiles",
        "equal_root_sets",
        "exact_global_complement",
        "identical_relative_kernels",
        "ordered_pair_profile_200_200",
        "kernel_rank_one",
        "kernel_trace_twenty",
        "kernel_row_sums_zero",
        "inverse_pairs_are_sign_opposed",
        "repository_status_preserved",
    ],
    "predicted_classification":
        "twenty_root_orientation_carrier_has_canonical_relative_sign_kernel_without_absolute_sign_or_spherical_embedding",
    "boundary": {
        "absolute_root_sign_selected": False,
        "anchor_selected": False,
        "spherical_embedding_supplied": False,
        "character_channel_identified_with_CMB": False,
        "cmb_data_accessed": False,
        "cosmological_model_constructed": False,
        "physical_claim": False,
        "manuscript_mutated": False,
        "project_mutated": False,
    },
    "promotion": {
        "candidate_only": True,
        "census_performed": False,
        "promoted": False,
    },
}

output.write_text(
    json.dumps(packet, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

print("PACKET:", packet["packet"])
print("LOCKED_HEAD:", locked_head)
print("AUTHORITY_COUNT:", len(authorities))
print("REQUIRED_TEST_COUNT:", len(packet["required_tests"]))
print(
    "PREDICTED_CLASSIFICATION:",
    packet["predicted_classification"],
)
print("CENSUS_PERFORMED: false")
print("PROJECT_MUTATION_PERFORMED: false")
