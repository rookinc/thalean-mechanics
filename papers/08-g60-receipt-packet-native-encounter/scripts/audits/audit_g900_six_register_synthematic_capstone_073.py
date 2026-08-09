#!/usr/bin/env python3

import hashlib
import json
import pathlib
import re
import subprocess
import sys

project = pathlib.Path(sys.argv[1]).resolve()
output = pathlib.Path(sys.argv[2]).resolve()
audit = project / "scripts" / "audits"
is_permanent_output = (
    output.parent == project / "artifacts" / "json"
)

specs = (
    (
        "compute_g900_native_double_c5_spoke_decomposition_063.py",
        "g900_native_double_c5_spoke_decomposition_063",
        True,
        0,
        (
            "SOLUTION_COUNT: 6",
            "KNOWN_PARTITION_RECOVERED: True",
        ),
    ),
    (
        "compute_g900_six_decomposition_duad_register_064.py",
        "g900_six_decomposition_duad_register_064",
        True,
        0,
        (
            "DECOMPOSITION_COUNT: 6",
            "NATIVE_G15_STATE_TO_SIX_REGISTER_DUAD_DERIVED: True",
        ),
    ),
    (
        "compute_g900_petersen_six_register_stabilizer_065.py",
        "g900_petersen_six_register_stabilizer_065",
        True,
        0,
        (
            "ROOT_AUTOMORPHISM_GROUP_ORDER: 120",
            "CAPSTONE_STABILIZER_IS_AGL15: True",
        ),
    ),
    (
        "compute_g900_six_register_pair_orbit_reconstruction_066.py",
        "g900_six_register_pair_orbit_reconstruction_066",
        True,
        0,
        (
            "PAIR_ORBIT_SIZE_PROFILE: {15: 1, 30: 1, 60: 1}",
            "G15_DISTANCE_PARTITION_FROM_PAIR_ORBITS_DERIVED: True",
        ),
    ),
    (
        "compute_g900_six_register_synthematic_total_067.py",
        "g900_six_register_synthematic_total_067",
        True,
        0,
        (
            "NATIVE_SYNTHEMATIC_TOTAL_DERIVED: True",
            "DIRECT_SIX_POINT_G15_METRIC_RULE_DERIVED: True",
        ),
    ),
    (
        "compute_g900_six_register_k33_cross_duad_family_068.py",
        "g900_six_register_k33_cross_duad_family_068",
        True,
        0,
        (
            "THREE_PLUS_THREE_SPLIT_COUNT: 10",
            "INTRINSIC_K33_CROSS_DUAD_FAMILY_DERIVED: True",
        ),
    ),
    (
        "compute_g900_k33_closure_syntheme_reflection_069.py",
        "g900_k33_closure_syntheme_reflection_069",
        True,
        0,
        (
            "DECORATED_FRAME_COUNT: 60",
            "DRAWING_REFLECTION_DERIVED: True",
        ),
    ),
    (
        "compute_g900_k33_five_four_frame_torsor_falsifier_070.py",
        "g900_k33_five_four_frame_torsor_070",
        False,
        3,
        (
            "CLASSIFICATION: complete_K3_3_five_four_frame_torsor_not_derived",
            "COMPLETE_FRAME_IS_NATIVE_SYMMETRY_TORSOR: False",
        ),
    ),
    (
        "compute_g900_k33_five_four_frame_double_cover_070b.py",
        "g900_k33_five_four_frame_double_cover_070b",
        True,
        0,
        (
            "ORBIT_SIZE_PROFILE: {60: 2}",
            "TWO_NATIVE_FRAME_SHEETS_DERIVED: True",
        ),
    ),
    (
        "compute_g900_k33_sheet_synthematic_completion_071.py",
        "g900_k33_sheet_synthematic_completion_071",
        True,
        0,
        (
            "REFLECTION_CLASS_COUNT: 2",
            "FRAME_SHEET_BIT_DERIVED: True",
        ),
    ),
    (
        "compute_g900_sheet_affine_square_root_join_072.py",
        "g900_sheet_affine_square_root_join_072",
        True,
        0,
        (
            "SHEET_AND_AFFINE_ORIENTATION_ARE_INDEPENDENT: True",
            "CHOICES_PER_BASE_FRAME: 4",
        ),
    ),
)

def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1048576), b""):
            digest.update(block)
    return digest.hexdigest()

def field(stdout, name):
    match = re.search(
        rf"^{re.escape(name)}:\s*(.+)$",
        stdout,
        flags=re.MULTILINE,
    )
    return match.group(1).strip() if match else None

runs = []

for filename, expected_packet, expected_pass, expected_failures, markers in specs:
    script = audit / filename

    if script.is_file():
        process = subprocess.run(
            [sys.executable, str(script)],
            cwd=project,
            text=True,
            capture_output=True,
            check=False,
        )
        stdout = process.stdout
        stderr = process.stderr
        packet = field(stdout, "PACKET")
        theorem_text = field(stdout, "THEOREM_PASS")
        failures_text = field(stdout, "FAILED_CHECK_COUNT")
        theorem_pass = theorem_text == "True"

        try:
            failure_count = int(failures_text)
        except (TypeError, ValueError):
            failure_count = None
    else:
        process = None
        stdout = ""
        stderr = ""
        packet = None
        theorem_pass = None
        failure_count = None

    marker_checks = {
        marker: marker in stdout
        for marker in markers
    }

    runs.append(
        {
            "script": str(script),
            "script_exists": script.is_file(),
            "sha256": sha256(script) if script.is_file() else None,
            "returncode": process.returncode if process else None,
            "packet": packet,
            "expected_packet": expected_packet,
            "theorem_pass": theorem_pass,
            "expected_theorem_pass": expected_pass,
            "failed_check_count": failure_count,
            "expected_failed_check_count": expected_failures,
            "marker_checks": marker_checks,
            "stderr": stderr,
        }
    )

checks = {
    "scout_count_11": len(runs) == 11,
    "all_scripts_exist": all(row["script_exists"] for row in runs),
    "all_return_zero": all(row["returncode"] == 0 for row in runs),
    "all_packet_names_match": all(
        row["packet"] == row["expected_packet"]
        for row in runs
    ),
    "all_expected_theorem_statuses_match": all(
        row["theorem_pass"] == row["expected_theorem_pass"]
        for row in runs
    ),
    "all_expected_failure_counts_match": all(
        row["failed_check_count"] == row["expected_failed_check_count"]
        for row in runs
    ),
    "all_required_markers_present": all(
        all(row["marker_checks"].values())
        for row in runs
    ),
    "torsor_070_falsified_exactly": (
        runs[7]["theorem_pass"] is False
        and runs[7]["failed_check_count"] == 3
    ),
    "double_cover_070b_passed": (
        runs[8]["theorem_pass"] is True
        and runs[8]["failed_check_count"] == 0
    ),
    "sheet_completion_071_passed": (
        runs[9]["theorem_pass"] is True
        and runs[9]["failed_check_count"] == 0
    ),
    "sheet_affine_independence_072_passed": (
        runs[10]["theorem_pass"] is True
        and runs[10]["failed_check_count"] == 0
    ),
}

failed = [
    name
    for name, passed in checks.items()
    if not passed
]

audit_pass = not failed

result = {
    "packet": "g900_six_register_synthematic_capstone_073",
    "mode": "post_scout_intrinsic_six_register_capstone",
    "audit_pass": audit_pass,
    "classification": (
        "native_G15_six_register_synthematic_K3_3_"
        "double_sheet_affine_root_capstone_passed"
        if audit_pass
        else
        "native_G15_six_register_capstone_failed"
    ),
    "earned_statement": (
        "Native G15 intrinsically determines six double-C5 "
        "decompositions corresponding to the six perfect matchings "
        "of its Petersen root. Pairwise intersections identify the "
        "fifteen G15 states with the fifteen duads of a six-point "
        "register. A native synthematic total reconstructs the full "
        "G15 distance metric on those duads. The ten three-plus-three "
        "splits of the register produce ten intrinsic abstract K3,3 "
        "cross-duad carriers, each with a six same-side plus nine "
        "cross-duad partition. Adding a same-side closure produces "
        "sixty reflection frames. Their one hundred twenty complete "
        "five-four placements do not form one native torsor: they "
        "split into two native sheets of sixty, exactly the two "
        "reflection-invariant synthematic-total completions of "
        "AB, CE, DF. Each base frame also has two inverse centered "
        "order-four square roots of its reflection. The completion "
        "sheet and affine-root orientation are independent binary "
        "choices, yielding four choices per base frame."
    ),
    "interpretation": (
        "The order-four root supplies the intrinsic combinatorial "
        "notion of one step and its repeated step. Under an explicitly "
        "chosen faithful square-grid or inner-product realization, "
        "these may be read as orthogonal once and orthogonal again. "
        "The graph alone derives the order-four action and its "
        "involutive square, not numerical 90-degree or 180-degree "
        "angles."
    ),
    "derived": {
        "native_G15_state_count": 15,
        "six_register_point_count": 6,
        "duad_count": 15,
        "intrinsic_decomposition_count": 6,
        "root_automorphism_group_order": 120,
        "capstone_stabilizer": "AGL(1,5)",
        "capstone_stabilizer_order": 20,
        "syntheme_count": 5,
        "three_plus_three_split_count": 10,
        "K33_cross_duad_count_per_split": 9,
        "same_side_duad_count_per_split": 6,
        "base_reflection_frame_count": 60,
        "complete_five_four_frame_count": 120,
        "native_completion_sheet_count": 2,
        "native_completion_sheet_size": 60,
        "centered_affine_roots_per_frame": 2,
        "choices_per_base_frame": 4,
        "distance_rule": {
            "1": "disjoint_duads_in_different_synthemes",
            "2": "duads_intersect_in_one_register_point",
            "3": "disjoint_duads_in_the_same_syntheme",
        },
        "orthogonal_language": {
            "one_step": "orthogonal_once_under_faithful_metric_realization",
            "repeated_step": (
                "orthogonal_again_under_faithful_metric_realization"
            ),
        },
    },
    "checks": checks,
    "failed_checks": failed,
    "scout_runs": runs,
    "boundary": {
        "expected_falsifier_070_preserved": True,
        "single_120_frame_torsor_claim": False,
        "canonical_decomposition_selected": False,
        "canonical_K33_split_selected": False,
        "canonical_frame_selected": False,
        "canonical_completion_sheet_selected": False,
        "absolute_affine_orientation_selected": False,
        "sheet_equals_affine_orientation": False,
        "numeric_angle_values_derived_from_graph": False,
        "orthogonality_is_unconditional_graph_claim": False,
        "physical_cube_claim": False,
        "physical_distance_claim": False,
        "physical_rotation_claim": False,
        "force_claim": False,
        "gravity_claim": False,
    },
    "repository_mutation": {
        "artifact_write_requested": str(output),
        "permanent_artifact_written": is_permanent_output,
        "staging_performed": False,
        "commit_performed": False,
        "push_performed": False,
    },
}

output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(
    json.dumps(result, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

print("PACKET:", result["packet"])
print("MODE:", result["mode"])

for row in runs:
    print(
        "SCOUT:",
        row["expected_packet"],
        "EXISTS=" + str(row["script_exists"]),
        "RC=" + str(row["returncode"]),
        "PASS=" + str(row["theorem_pass"]),
        "FAILURES=" + str(row["failed_check_count"]),
    )

print("CHECKS:", checks)
print("FAILED_CHECK_COUNT:", len(failed))
print("FAILED_CHECKS:", failed)
print("AUDIT_PASS:", audit_pass)
print("CLASSIFICATION:", result["classification"])
print("OUTPUT:", output)
print("PERMANENT_ARTIFACT_WRITTEN:", is_permanent_output)
print("STAGING_PERFORMED:", False)
print("COMMIT_PERFORMED:", False)
print("PUSH_PERFORMED:", False)
