#!/usr/bin/env python3

import hashlib
import json
import pathlib
import subprocess
import sys

project = pathlib.Path(sys.argv[1]).resolve()
source = pathlib.Path(sys.argv[2]).resolve()
raw = pathlib.Path(sys.argv[3]).resolve()
firm = pathlib.Path(sys.argv[4]).resolve()
packet = pathlib.Path(sys.argv[5]).resolve()

expected_hashes = {
    source: (
        "49363d7a4893416e02edad7ef1558fdc30f9f957e"
        "ea0cb7043908c517b60e617"
    ),
    raw: (
        "ad4b1be4d6f7a5d7e61a7f31792dc119fbe0d1b"
        "0aed9b85ceff81c212b029272"
    ),
    firm: (
        "60b925d715c645df52f368bda442d7ab5bc102391"
        "552049d68afd415bd5d5d72"
    ),
    packet: (
        "11b4e1b1b9ef2126fe61a9a0f43dde07e41505d3"
        "cadafc4e9149c893e3b83c58"
    ),
}

expected_head = (
    "814a6d4 Preregister G60 root relative-sign kernel"
)

def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1048576), b""):
            digest.update(block)
    return digest.hexdigest()

def git(*args):
    return subprocess.check_output(
        ["git", "--no-pager", *args],
        cwd=project,
        text=True,
    ).strip()

status_before = git("status", "--short")
head = git("show", "-s", "--format=%h %s", "HEAD")

data = json.loads(packet.read_text(encoding="utf-8"))
receipt = raw.read_text(encoding="utf-8")

checks = []

def check(name, passed):
    checks.append((name, bool(passed)))

check("head", head == expected_head)

for path, expected in expected_hashes.items():
    check(path.name + "_exists", path.is_file())
    check(path.name + "_hash", sha256(path) == expected)

check(
    "packet_name",
    data["packet"] == "g60_h3_triality_galois_ledge",
)
check("packet_version", data["version"] == 1)
check(
    "packet_mode",
    data["mode"] == "temporary_consolidated_theorem_candidate",
)
check("candidate_pass", data["candidate_pass"] is True)
check("candidate_not_frozen", data["candidate_frozen"] is False)
check("candidate_not_promoted", data["candidate_promoted"] is False)
check("packet_check_count", data["check_count"] == 62)
check("packet_failed_zero", data["failed_check_count"] == 0)
check("packet_failed_empty", data["failed_checks"] == [])

theorem = data["theorem"]
check("carrier_size_60", theorem["carrier_size"] == 60)
check(
    "projective_line_count_30",
    theorem["projective_line_count"] == 30,
)
check(
    "presentation_count_3",
    theorem["spherical_presentation_count"] == 3,
)
check(
    "presentation_triality",
    theorem["presentation_symmetry"] == "S3_triality",
)
check(
    "sheet_kernel_v4",
    theorem["orientation_sheet_kernel"] == "V4",
)
check(
    "sheet_extension_s4",
    theorem["orientation_sheet_extension"] == "S4",
)
check(
    "kernel_a5_times_v4",
    theorem["common_presentation_kernel"] == "A5_times_V4",
)
check(
    "kernel_order_240",
    theorem["common_presentation_kernel_order"] == 240,
)
check(
    "full_order_1440",
    theorem["full_extension_order"] == 1440,
)
check(
    "full_group_structure",
    theorem["full_group_structure"] == "A5_semidirect_S4",
)
check(
    "cycler_inner",
    theorem["triality_cycler_action_on_A5"] == "inner",
)
check(
    "reverser_outer",
    theorem["triality_reverser_action_on_A5"] == "outer",
)

galois = theorem["golden_galois_action"]
check(
    "galois_field_map",
    galois["field_map"] == "sqrt5_maps_to_minus_sqrt5",
)
check(
    "galois_presentation_action",
    galois["presentation_permutation"] == [1, 0, 2],
)
check(
    "galois_matches_reverser",
    galois["matches_triality_reverser"] is True,
)

refinement = data["refined_negative_result"]
check(
    "early_probe_false_preserved",
    refinement["early_direction_audit_passed"] is False,
)
check(
    "refinement_passed",
    refinement["refinement_passed"] is True,
)

for name, value in data["boundary"].items():
    check("boundary_" + name, value is False)

required_receipt_lines = [
    "LONGITUDINAL_IS_EXACT_ROOT_PAIR_BISECTOR: True",
    "PRESENTATION_S3_ACTION_PROVED: True",
    "DIRECTION_AUDIT_PASS: False",
    "ORIENTATION_SHEET_CENSUS_PASS: True",
    "ORIENTATION_SHEET_V4_PROVED: True",
    "ORIENTATION_SHEET_S4_PROVED: True",
    "KERNEL_A5_TIMES_V4_PROVED: True",
    "FULL_ORDER_1440_EXTENSION_PROVED: True",
    "C_ACTION_IS_INNER: True",
    "R_ACTION_IS_OUTER: True",
    "GOLDEN_GALOIS_MATCHES_R_COLOR_ACTION: True",
    "GOLDEN_GALOIS_OUTER_AUTOMORPHISM_PROVED: True",
]

for line in required_receipt_lines:
    check(
        "receipt_" + line.lower().replace(" ", "_"),
        line in receipt,
    )

promoted = [
    str(path.relative_to(project))
    for path in project.rglob("*g60_h3_triality_galois_ledge*")
]

check("nothing_promoted", promoted == [])

status_after = git("status", "--short")
check(
    "repository_status_preserved",
    status_after == status_before,
)

failed = [
    name
    for name, passed in checks
    if not passed
]

print("== G60 H3 TRIALITY-GALOIS INDEPENDENT GUARD ==")
print("CHECK_COUNT:", len(checks))
print("FAILED_CHECK_COUNT:", len(failed))

for name, passed in checks:
    print("CHECK", name + ":", str(passed).lower())

print("FAILED_CHECKS:", failed)
print("GUARD_PASS:", not failed)
print("CANDIDATE_FROZEN: false")
print("CANDIDATE_PROMOTED: false")
print("PROJECT_MUTATION_PERFORMED: false")

if failed:
    raise SystemExit(1)
