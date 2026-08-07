#!/usr/bin/env python3

import hashlib
import json
import pathlib
import subprocess
import sys

project = pathlib.Path(sys.argv[1]).resolve()
output_path = pathlib.Path(sys.argv[2]).resolve()

locked_head = "9f0a1f5 Lock G60 local D8 inversion variance"

authority_specs = {
    "012c": (
        project / "artifacts/json/"
        "g60_binary_torsor_action_character_probe_012c.v1.json",
        "b08d3012ed20301897baa771ed99ecd6a859b8e7d1ef5b31c497652287962d76",
    ),
    "012e": (
        project / "artifacts/json/"
        "g60_local_D8_inversion_variance_census_012e.v1.json",
        "a42aed2a1b56144285fd0b2e575a7f932eb7de93b636e49b55cb9a7bd498328a",
    ),
    "011w": (
        project / "artifacts/json/"
        "g60_native_d8_chart_coherence_census_011w.v1.json",
        "e5630a02b4e4c28caac017906aebae10b00c5b1a8e1ccdf640a414c1174f6919",
    ),
    "011y": (
        project / "artifacts/json/"
        "g60_native_d8_outer_c2_selector_census_011y.v1.json",
        "d5a9036cf96aa97dd8848cd947bff4d07c711db0db2e3dca3ad13ec1c9cdfdab",
    ),
    "012a": (
        project / "artifacts/json/"
        "g60_gauge_covariant_update_census_012a.v1.json",
        "4e6936b9b48c6f033b826df7c3ad4ac70ec3480129c5c73ec6a24630077096d2",
    ),
    "011o": (
        project / "artifacts/json/"
        "g60_full_A_orientation_character_extension_census_011o.v1.json",
        "ad684db8bb65c5eb731c972d33e685ffc18a947f63c9ba4e9758f815821f0941",
    ),
}

def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

def git(*args):
    return subprocess.check_output(
        ["git", "--no-pager", *args],
        cwd=project,
        text=True,
    ).strip()

head = git("show", "-s", "--format=%h %s", "HEAD")
if head != locked_head:
    raise SystemExit("locked HEAD mismatch: " + head)

expected_status = {
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
if status != expected_status:
    raise SystemExit("unexpected scoped repository status")

authorities = {}
for name, (path, expected_hash) in authority_specs.items():
    if not path.is_file():
        raise SystemExit("missing authority: " + str(path))
    actual_hash = sha256_file(path)
    if actual_hash != expected_hash:
        raise SystemExit("authority hash mismatch: " + str(path))
    authorities[str(path)] = {
        "role": name,
        "expected_sha256": expected_hash,
        "sha256": actual_hash,
        "hash_match": True,
    }

payload = {
    "packet": "g60_variance_completed_chart_preregistration_012f",
    "mode": "temporary_read_only_variance_completed_chart_preregistration",
    "locked_head": locked_head,
    "authorities": authorities,
    "research_question": (
        "Does adjoining local inversion produce a gauge-compatible "
        "Aut(D8) x C2 variance-completed chart system, and do the "
        "instruction, chart-orbit, and variance pairs remain distinct "
        "equivariant C2 torsors?"
    ),
    "definitions": {
        "local_inversion": "iota(x) = inverse(x)",
        "ordinary_chart": "c(x*y) = c(x)c(y)",
        "opposite_chart": "c_minus = c composed with iota",
        "opposite_chart_law": (
            "c_minus(x*y) = c_minus(y)c_minus(x)"
        ),
        "opposite_domain_form": (
            "c_minus is a homomorphism D8_op -> native D8 subgroup"
        ),
        "extended_local_symmetry": (
            "Aut_plusminus(D8) = Aut(D8) x C2_variance"
        ),
        "chart_character": (
            "chi_chart(phi,epsilon) = chi_chart(phi)"
        ),
        "variance_character": (
            "chi_variance(phi,epsilon) = epsilon"
        ),
        "instruction_character": (
            "chi_instruction_plusminus(phi,epsilon) = "
            "chi_instruction(phi) XOR epsilon"
        ),
    },
    "predictions": {
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
    },
    "required_tests": [
        "reconstruct both locked local multiplication tables",
        "reconstruct all eight automorphisms in each presentation",
        "reconstruct all eighty ordinary charts in each presentation",
        "construct every opposite chart by precomposition with inversion",
        "measure ordinary and anti-homomorphism failures for every chart",
        "prove ordinary and opposite chart sets are disjoint",
        "enumerate the sixteen automorphism-variance transformations",
        "verify the direct-product composition law",
        "compute instruction, chart, and variance permutation characters",
        "compute their kernels, joint image, and joint kernel",
        "test all pairwise equivariant bijections",
        "test all four locked presentation gauge maps",
        "retain 011o orientation as an unlinked comparison authority",
    ],
    "predicted_classification": (
        "variance_completed_local_chart_system_has_three_independent_"
        "binary_characters_without_canonical_torsor_collapse"
    ),
    "boundary": {
        "variance_completed_census_performed": False,
        "opposite_chart_bundle_constructed": False,
        "orientation_to_local_variance_identified": False,
        "instruction_selected": False,
        "chart_orbit_selected": False,
        "orientation_selected": False,
        "autonomous_native_update_law_constructed": False,
        "mechanics_state_cell_established": False,
        "manuscript_mutated": False,
        "geometry_claim": False,
        "physical_claim": False,
    },
    "repository_mutation_performed": False,
}

output_path.write_text(
    json.dumps(payload, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

print("PACKET:", payload["packet"])
print("LOCKED_HEAD:", payload["locked_head"])
print("AUTHORITY_COUNT:", len(authorities))
print("REQUIRED_TEST_COUNT:", len(payload["required_tests"]))
print("PREDICTED_CLASSIFICATION:",
      payload["predicted_classification"])
print("PROJECT_MUTATION_PERFORMED: false")
