#!/usr/bin/env python3

import hashlib
import json
import pathlib
import subprocess
import sys
from datetime import datetime

project = pathlib.Path(sys.argv[1]).resolve()
output_path = pathlib.Path(sys.argv[2]).resolve()
is_permanent_output = project in output_path.parents
audit_dir = project / "scripts" / "audits"

scouts = [
    audit_dir / "compute_g60_native_eight_arc_rosette_scout_021.py",
    audit_dir / "compute_g60_rosette_quarter_turn_scout_022.py",
    audit_dir / "compute_g60_rosette_four_lane_pipe_scout_023.py",
    audit_dir / "compute_g60_rosette_null_center_scout_024.py",
]

def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1048576), b""):
            digest.update(block)
    return digest.hexdigest()

def parse_fields(text):
    fields = {}
    for line in text.splitlines():
        if ": " in line:
            key, value = line.split(": ", 1)
            fields[key.strip()] = value.strip()
    return fields

runs = []
for path in scouts:
    completed = subprocess.run(
        [sys.executable, str(path)],
        cwd=project,
        text=True,
        capture_output=True,
        check=False,
    )
    fields = parse_fields(completed.stdout)
    runs.append({
        "script": str(path.relative_to(project)),
        "script_sha256": sha256_file(path),
        "returncode": completed.returncode,
        "packet": fields.get("PACKET"),
        "theorem_pass": fields.get("THEOREM_PASS"),
        "failed_check_count": fields.get("FAILED_CHECK_COUNT"),
        "classification": fields.get("CLASSIFICATION"),
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    })

checks = {
    "scout_count_4": len(runs) == 4,
    "all_scouts_return_zero": all(
        row["returncode"] == 0 for row in runs
    ),
    "all_scouts_theorem_pass": all(
        row["theorem_pass"] == "True" for row in runs
    ),
    "all_scouts_zero_failures": all(
        row["failed_check_count"] == "0" for row in runs
    ),
    "rosette_equivariant_identification_pass": (
        runs[0]["classification"] ==
        "native_eight_chart_fiber_is_D8_equivariantly_"
        "isomorphic_to_four_leaf_eight_arc_rosette"
    ),
    "quarter_turn_geometry_pass": (
        runs[1]["classification"] ==
        "faithful_square_grid_realization_forces_"
        "the_two_order4_elements_to_be_opposite_quarter_turns"
    ),
    "four_lane_pipe_join_pass": (
        runs[2]["classification"] ==
        "every_g15_transport_edge_has_a_four_lane_"
        "g60_pipe_equivariantly_modeled_by_the_four_rosette_leaves"
    ),
    "null_center_quotient_pass": (
        runs[3]["classification"] ==
        "rosette_has_a_unique_D8_fixed_null_center_"
        "representing_the_one_point_quotient_without_"
        "adding_a_lane_or_chart"
    ),
}

failed = [
    name for name, passed in checks.items()
    if not passed
]
audit_pass = not failed

result = {
    "packet": "g60_native_rosette_pipe_null_corollary_025",
    "mode": "post_scout_corollary_consolidation",
    "created_at": datetime.now().astimezone().isoformat(),
    "audit_pass": audit_pass,
    "classification": (
        "native_D8_eight_chart_rosette_quarter_turn_"
        "four_lane_pipe_and_fixed_null_center_corollary_passed"
        if audit_pass
        else "rosette_pipe_null_corollary_not_promoted"
    ),
    "checks": checks,
    "failed_checks": failed,
    "runs": runs,
    "earned_statement": (
        "Every tested native eight-chart fiber is noncanonically "
        "D8-equivariantly isomorphic to a four-leaf eight-arc "
        "rosette. In a faithful square-grid realization, the two "
        "order-four elements act as opposite quarter-turns. Every "
        "G15 transport edge has a four-lane G60 lift torsor "
        "equivariantly modeled by the four leaves. The planar "
        "realization has a unique D8-fixed center representing the "
        "one-class quotient without adding a lane, chart, G60 "
        "state, or G15 edge."
    ),
    "interpretation": (
        "The null is the structured omission at G15 resolution "
        "of the transverse V4 lane coordinate resolved by G60."
    ),
    "boundary": {
        "post_scout_not_blinded": True,
        "canonical_arc_labeling_selected": False,
        "canonical_lane_labeling_selected": False,
        "clockwise_orientation_selected": False,
        "circular_arc_shape_derived": False,
        "pink_diamond_identified": False,
        "registration_signature_dominance_derived": False,
        "null_is_extra_g60_state": False,
        "null_is_extra_g15_edge": False,
        "physical_pipe_claim": False,
        "physical_flow_claim": False,
        "gravity_claim": False,
    },
    "repository_mutation": {
        "artifact_write_requested": str(output_path),
        "commit_performed": False,
        "push_performed": False,
    },
}

output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(
    json.dumps(result, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

print("PACKET:", result["packet"])
print("MODE:", result["mode"])
for row in runs:
    print(
        "SCOUT:",
        row["packet"],
        "RC=" + str(row["returncode"]),
        "PASS=" + str(row["theorem_pass"]),
        "FAILURES=" + str(row["failed_check_count"]),
    )
print("CHECKS:", checks)
print("FAILED_CHECK_COUNT:", len(failed))
print("FAILED_CHECKS:", failed)
print("AUDIT_PASS:", audit_pass)
print("CLASSIFICATION:", result["classification"])
print("OUTPUT:", output_path)
print("PERMANENT_ARTIFACT_WRITTEN:", is_permanent_output)
print("COMMIT_PERFORMED:", False)
print("PUSH_PERFORMED:", False)
