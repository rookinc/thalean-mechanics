#!/usr/bin/env python3

import hashlib
import json
import pathlib
import subprocess
import sys

P08 = pathlib.Path(sys.argv[1]).resolve()
OUTPUT = pathlib.Path(sys.argv[2]).resolve()

P41 = pathlib.Path(
    "/data/data/com.termux/files/home/dev/cori/research/"
    "mathematics/41-order-4-dodecahedral-residue"
)

SOURCE_015 = (
    P41
    / "artifacts/json/intrinsic_g15_line_petersen_audit_015.json"
)

SOURCE_019 = (
    P41
    / "artifacts/json/a5_v4_k22_four_slot_alignment_audit_019.json"
)

SCOUTS = (
    (
        "g900_native_g15_edge_bisector_bridge_038b",
        pathlib.Path(
            "/data/data/com.termux/files/home/tmp/"
            "probe-g900-native-g15-edge-bisector-bridge-038b.py"
        ),
    ),
    (
        "g900_k33_frame_pentagon_register_probe_040b",
        pathlib.Path(
            "/data/data/com.termux/files/home/tmp/"
            "probe-g900-k33-frame-pentagon-register-040b.py"
        ),
    ),
    (
        "g900_k33_to_native_g15_projection_distortion_043b",
        pathlib.Path(
            "/data/data/com.termux/files/home/tmp/"
            "probe-g900-k33-to-native-g15-projection-distortion-043b.py"
        ),
    ),
    (
        "g900_flat_edge_triangle_tip_projection_044",
        pathlib.Path(
            "/data/data/com.termux/files/home/tmp/"
            "probe-g900-flat-edge-triangle-tip-projection-044.py"
        ),
    ),
    (
        "g900_native_double_triangle_spoke_bridge_045",
        pathlib.Path(
            "/data/data/com.termux/files/home/tmp/"
            "probe-g900-native-double-triangle-spoke-bridge-045.py"
        ),
    ),
    (
        "g900_native_c5_edge_affine_twist_046",
        pathlib.Path(
            "/data/data/com.termux/files/home/tmp/"
            "probe-g900-native-c5-edge-affine-twist-046.py"
        ),
    ),
    (
        "g900_native_c5_affine_twist_gauge_census_047",
        pathlib.Path(
            "/data/data/com.termux/files/home/tmp/"
            "probe-g900-native-c5-affine-twist-gauge-census-047.py"
        ),
    ),
    (
        "g900_spoke_twist_carrier_direction_join_049",
        pathlib.Path(
            "/data/data/com.termux/files/home/tmp/"
            "probe-g900-spoke-twist-carrier-direction-join-049.py"
        ),
    ),
    (
        "g900_affine_twist_one_four_angle_role_050",
        pathlib.Path(
            "/data/data/com.termux/files/home/tmp/"
            "probe-g900-affine-twist-one-four-angle-role-050.py"
        ),
    ),
    (
        "g900_affine_twist_square_half_turn_051",
        pathlib.Path(
            "/data/data/com.termux/files/home/tmp/"
            "probe-g900-affine-twist-square-half-turn-051.py"
        ),
    ),
    (
        "g900_twist_invariant_angle_placement_052",
        pathlib.Path(
            "/data/data/com.termux/files/home/tmp/"
            "probe-g900-twist-invariant-angle-placement-052.py"
        ),
    ),
    (
        "g900_spoke_midpoint_invertibility_053",
        pathlib.Path(
            "/data/data/com.termux/files/home/tmp/"
            "probe-g900-spoke-midpoint-invertibility-053.py"
        ),
    ),
    (
        "g900_midpoint_quotient_reverse_obstruction_054",
        pathlib.Path(
            "/data/data/com.termux/files/home/tmp/"
            "probe-g900-midpoint-quotient-reverse-obstruction-054.py"
        ),
    ),
    (
        "g900_five_bridge_affine_group_055",
        pathlib.Path(
            "/data/data/com.termux/files/home/tmp/"
            "probe-g900-five-bridge-affine-group-055.py"
        ),
    ),
    (
        "g900_k33_five_four_half_turn_join_056",
        pathlib.Path(
            "/data/data/com.termux/files/home/tmp/"
            "probe-g900-k33-five-four-half-turn-join-056.py"
        ),
    ),
    (
        "g900_k33_six_nine_barycentric_shadow_057",
        pathlib.Path(
            "/data/data/com.termux/files/home/tmp/"
            "probe-g900-k33-six-nine-barycentric-shadow-057.py"
        ),
    ),
    (
        "g900_k33_cube_face_cross_incidence_058",
        pathlib.Path(
            "/data/data/com.termux/files/home/tmp/"
            "probe-g900-k33-cube-face-cross-incidence-058.py"
        ),
    ),
    (
        "g900_k33_reflection_cube_symmetry_059",
        pathlib.Path(
            "/data/data/com.termux/files/home/tmp/"
            "probe-g900-k33-reflection-cube-symmetry-059.py"
        ),
    ),
    (
        "g900_cube_face_native_distance_join_060",
        pathlib.Path(
            "/data/data/com.termux/files/home/tmp/"
            "probe-g900-cube-face-native-distance-join-060.py"
        ),
    ),
    (
        "g900_cube_placement_residual_gauge_061",
        pathlib.Path(
            "/data/data/com.termux/files/home/tmp/"
            "probe-g900-cube-placement-residual-gauge-061.py"
        ),
    ),
)


def permanent_scout_name(path):
    name = path.name

    if name.startswith("probe-g900-"):
        name = "compute_g900_" + name[len("probe-g900-"):]

    return name.replace("-", "_")


SCOUTS = tuple(
    (
        packet,
        P08 / "scripts/audits" / permanent_scout_name(script),
    )
    for packet, script in SCOUTS
)

def sha256(path):
    digest = hashlib.sha256()

    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1048576), b""):
            digest.update(block)

    return digest.hexdigest()

def parse_scalar(stdout, field):
    prefix = field + ":"

    for line in stdout.splitlines():
        if line.startswith(prefix):
            return line[len(prefix):].strip()

    return None

def parse_bool(value):
    if value == "True":
        return True
    if value == "False":
        return False
    return None

source015 = json.loads(SOURCE_015.read_text(encoding="utf-8"))
source019 = json.loads(SOURCE_019.read_text(encoding="utf-8"))

runs = []

for expected_packet, script in SCOUTS:
    if not script.is_file():
        runs.append({
            "expected_packet": expected_packet,
            "script": str(script),
            "script_exists": False,
            "returncode": None,
            "packet": None,
            "theorem_pass": False,
            "failed_check_count": None,
            "classification": None,
            "stdout": "",
            "stderr": "script missing",
        })
        continue

    completed = subprocess.run(
        [sys.executable, str(script)],
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )

    stdout = completed.stdout
    stderr = completed.stderr

    packet = parse_scalar(stdout, "PACKET")
    theorem_value = (
        parse_scalar(stdout, "THEOREM_PASS")
        or parse_scalar(stdout, "SCHEMA_PASS")
    )

    failed_value = parse_scalar(
        stdout,
        "FAILED_CHECK_COUNT",
    )

    runs.append({
        "expected_packet": expected_packet,
        "script": str(script),
        "script_exists": True,
        "script_sha256": sha256(script),
        "returncode": completed.returncode,
        "packet": packet,
        "packet_matches_expected":
            packet == expected_packet,
        "theorem_pass": parse_bool(theorem_value),
        "failed_check_count":
            int(failed_value)
            if failed_value is not None
            else None,
        "classification":
            parse_scalar(stdout, "CLASSIFICATION"),
        "stdout": stdout,
        "stderr": stderr,
    })

checks = {
    "source015_exists":
        SOURCE_015.is_file(),
    "source019_exists":
        SOURCE_019.is_file(),
    "source015_audit_pass":
        source015.get("audit_pass") is True,
    "source019_audit_pass":
        source019.get("audit_pass") is True,
    "scout_count_20":
        len(runs) == 20,
    "all_scout_scripts_exist":
        all(row["script_exists"] for row in runs),
    "all_scouts_return_zero":
        all(row["returncode"] == 0 for row in runs),
    "all_packet_names_match":
        all(
            row.get("packet_matches_expected") is True
            for row in runs
        ),
    "all_scouts_theorem_pass":
        all(row["theorem_pass"] is True for row in runs),
    "all_scouts_zero_failures":
        all(row["failed_check_count"] == 0 for row in runs),
    "native_bisector_bridge_pass":
        runs[0]["theorem_pass"] is True,
    "projection_is_nonfaithful_pass":
        runs[2]["theorem_pass"] is True,
    "native_distance_roles_pass":
        runs[3]["theorem_pass"] is True,
    "affine_twist_pass":
        runs[5]["theorem_pass"] is True,
    "affine_gauge_pass":
        runs[6]["theorem_pass"] is True,
    "common_half_turn_pass":
        runs[9]["theorem_pass"] is True,
    "angle_placement_pass":
        runs[10]["theorem_pass"] is True,
    "native_midpoint_inverse_pass":
        runs[11]["theorem_pass"] is True,
    "quotient_reverse_obstruction_pass":
        runs[12]["theorem_pass"] is True,
    "AGL15_register_algebra_pass":
        runs[13]["theorem_pass"] is True,
    "five_four_edge_split_pass":
        runs[14]["theorem_pass"] is True,
    "six_nine_shadow_pass":
        runs[15]["theorem_pass"] is True,
    "cube_face_cross_incidence_pass":
        runs[16]["theorem_pass"] is True,
    "cube_reflection_pass":
        runs[17]["theorem_pass"] is True,
    "cube_native_distance_join_pass":
        runs[18]["theorem_pass"] is True,
    "residual_cube_gauge_pass":
        runs[19]["theorem_pass"] is True,
}

failed = [
    name
    for name, passed in checks.items()
    if not passed
]

audit_pass = not failed

is_permanent_output = (
    OUTPUT.parent == P08 / "artifacts/json"
)

result = {
    "packet":
        "g900_native_k33_cube_affine_capstone_062",
    "mode":
        "post_scout_capstone_consolidation",
    "audit_pass":
        audit_pass,
    "classification": (
        "native_G15_K3_3_signed_axis_cube_projection_"
        "affine_twist_midpoint_quotient_capstone_passed"
        if audit_pass
        else "native_K3_3_cube_affine_capstone_failed"
    ),
    "earned_statement": (
        "The projected carrier is K3,3 with six vertices and "
        "nine edges split into five interior and four boundary "
        "roles. Its native G15 bridge pairs the inner and outer "
        "C5 edge registers by an order-four affine twist. "
        "Together with C5 rotation this induces AGL(1,5), whose "
        "orientation-free square is negation and whose fixed-plus-"
        "four-moving orbit structure uniquely places the registered "
        "180/90 angle multiset. Native spoke-to-midpoint incidence "
        "is invertible before quotienting; collapsing five midpoint "
        "sections to one point preserves forward descent but leaves "
        "no invariant reverse section. The six K3,3 vertices admit "
        "a signed-axis cube-face realization in which the six cube-"
        "adjacent relations are exactly the native distance-one "
        "roles and AE, BC, DF are the three opposite-face relations "
        "of native distances two, two, and three. The twelve "
        "surviving placements form a free transitive S3 x C2 gauge "
        "orbit."
    ),
    "interpretation": (
        "The drawing is a nonfaithful but exact signed-axis "
        "cube-face projection of native G15 distance roles. "
        "Its null reverse is a quotient-section obstruction, "
        "not a failure of native spoke-midpoint invertibility."
    ),
    "measurements": {
        "K33_vertex_count": 6,
        "K33_edge_count": 9,
        "interior_edge_count": 5,
        "boundary_edge_count": 4,
        "barycentric_role_count": 15,
        "native_G15_vertex_count": 15,
        "native_G15_edge_count": 30,
        "affine_multiplier_pair": [2, 3],
        "affine_twist_order": 4,
        "affine_square_role_profile": [1, 2, 2],
        "affine_group": "AGL(1,5)",
        "affine_group_order": 20,
        "midpoint_section_count": 5,
        "invariant_midpoint_section_count": 0,
        "initial_cube_placement_count": 72,
        "reflection_compatible_cube_placement_count": 24,
        "distance_compatible_cube_placement_count": 12,
        "residual_cube_gauge": "S3 x C2",
        "residual_cube_gauge_order": 12,
        "cube_adjacent_native_distance_profile": {
            "1": 6,
        },
        "cube_opposite_native_distance_profile": {
            "2": 2,
            "3": 1,
        },
        "cube_opposite_drawing_pairs": [
            ["A", "E"],
            ["B", "C"],
            ["D", "F"],
        ],
    },
    "checks": checks,
    "failed_checks": failed,
    "sources": {
        "intrinsic_g15_line_petersen_audit_015": {
            "path": str(SOURCE_015),
            "sha256": sha256(SOURCE_015),
            "audit_pass": source015.get("audit_pass"),
        },
        "a5_v4_k22_four_slot_alignment_audit_019": {
            "path": str(SOURCE_019),
            "sha256": sha256(SOURCE_019),
            "audit_pass": source019.get("audit_pass"),
        },
    },
    "scout_runs": runs,
    "boundary": {
        "post_scout_not_blinded": True,
        "native_G15_automorphism_group_claim": False,
        "barycentric_shadow_equals_native_G15": False,
        "projection_is_adjacency_faithful": False,
        "numeric_angle_multiset_derived_from_graph": False,
        "absolute_axis_names_selected": False,
        "absolute_sign_class_selected": False,
        "absolute_handedness_selected": False,
        "canonical_cube_placement_selected": False,
        "physical_cube_claim": False,
        "physical_distance_claim": False,
        "physical_rotation_claim": False,
        "force_claim": False,
        "gravity_claim": False,
    },
    "repository_mutation": {
        "artifact_write_requested": str(OUTPUT),
        "permanent_artifact_written": is_permanent_output,
        "commit_performed": False,
        "push_performed": False,
    },
}

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_text(
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
print("OUTPUT:", OUTPUT)
print("PERMANENT_ARTIFACT_WRITTEN:", is_permanent_output)
print("COMMIT_PERFORMED:", False)
print("PUSH_PERFORMED:", False)
