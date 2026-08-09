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
    audit_dir / "compute_g60_pink_diamond_role_scout_026.py",
    audit_dir / (
        "compute_g60_registration_signature_"
        "dominance_scout_027.py"
    ),
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
    "scout_count_2": len(runs) == 2,
    "all_scouts_return_zero": all(
        row["returncode"] == 0 for row in runs
    ),
    "all_scouts_theorem_pass": all(
        row["theorem_pass"] == "True" for row in runs
    ),
    "all_scouts_zero_failures": all(
        row["failed_check_count"] == "0" for row in runs
    ),
    "pink_diamond_quotient_identified": (
        runs[0]["classification"] ==
        "pink_diamond_is_the_four_leaf_side_forgetting_"
        "quotient_of_the_eight_arc_rosette_not_the_full_"
        "eight_chart_fiber_or_an_absolute_section"
    ),
    "dominance_obstruction_identified": (
        runs[1]["classification"] ==
        "native_outer_C2_forbids_absolute_registration_"
        "signature_dominance_but_allows_an_externally_"
        "oriented_covariant_pair"
    ),
}

failed = [
    name for name, passed in checks.items()
    if not passed
]
audit_pass = not failed

result = {
    "packet": "g60_rosette_diamond_dominance_corollary_028",
    "mode": "post_scout_corollary_consolidation",
    "created_at": datetime.now().astimezone().isoformat(),
    "audit_pass": audit_pass,
    "classification": (
        "pink_diamond_side_forgetting_quotient_and_"
        "registration_signature_outer_C2_obstruction_passed"
        if audit_pass
        else "diamond_dominance_corollary_not_promoted"
    ),
    "checks": checks,
    "failed_checks": failed,
    "runs": runs,
    "earned_statement": (
        "The pink diamond is the four-leaf quotient of the "
        "eight-arc rosette obtained by forgetting the binary arc "
        "side. It is neither the full eight-chart fiber nor one "
        "absolute four-chart section. No native outer-C2-invariant "
        "binary observable separates the two four-chart sections. "
        "Registration-dominant and signature-dominant roles are "
        "available only as a covariant exchanged pair, and an "
        "external C2 registration bit is required to name them."
    ),
    "diagram_rule": {
        "pink_diamond_role": "four_leaf_side_forgetting_quotient",
        "fixed_left_right_dominance_labels_allowed": False,
        "covariant_role_pair": [
            "registration_dominant",
            "signature_dominant",
        ],
        "external_bit_rule": {
            "r_0": {
                "E": "registration_dominant",
                "E_inverse": "signature_dominant",
            },
            "r_1": {
                "E": "signature_dominant",
                "E_inverse": "registration_dominant",
            },
        },
    },
    "boundary": {
        "post_scout_not_blinded": True,
        "pink_diamond_is_full_eight_chart_fiber": False,
        "pink_diamond_selects_absolute_section": False,
        "absolute_vertex_labeling_selected": False,
        "native_registration_dominant_section_selected": False,
        "native_signature_dominant_section_selected": False,
        "external_C2_bit_required": True,
        "physical_dominance_claim": False,
        "physical_claim": False,
    },
    "repository_mutation": {
        "artifact_write_requested": str(output_path),
        "permanent_artifact_written": is_permanent_output,
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
