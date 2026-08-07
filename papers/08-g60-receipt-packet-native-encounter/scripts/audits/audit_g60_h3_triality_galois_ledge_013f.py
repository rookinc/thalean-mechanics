#!/usr/bin/env python3

import hashlib
import json
import pathlib
import subprocess
import sys

project = pathlib.Path(sys.argv[1]).resolve()

paths = {
    "json": pathlib.Path(sys.argv[2]).resolve(),
    "source_candidate": pathlib.Path(sys.argv[3]).resolve(),
    "note": pathlib.Path(sys.argv[4]).resolve(),
    "derive": pathlib.Path(sys.argv[5]).resolve(),
    "firm": pathlib.Path(sys.argv[6]).resolve(),
    "candidate_guard": pathlib.Path(sys.argv[7]).resolve(),
    "raw_receipt": pathlib.Path(sys.argv[8]).resolve(),
    "guard_receipt": pathlib.Path(sys.argv[9]).resolve(),
}

expected_head = (
    "814a6d4 Preregister G60 root relative-sign kernel"
)

expected_hashes = {
    "source_candidate": (
        "11b4e1b1b9ef2126fe61a9a0f43dde07e41505d3"
        "cadafc4e9149c893e3b83c58"
    ),
    "note": (
        "2ef00d90e71a779160d2c6efde30d255954abdfba"
        "361f8df54f0e4cf9b4dae7e"
    ),
    "derive": (
        "49363d7a4893416e02edad7ef1558fdc30f9f957e"
        "ea0cb7043908c517b60e617"
    ),
    "firm": (
        "60b925d715c645df52f368bda442d7ab5bc102391"
        "552049d68afd415bd5d5d72"
    ),
    "candidate_guard": (
        "1f9aee99f2b74163a758517a56108e0d24195dbf"
        "8a3b9225aac44aefc897f346"
    ),
    "raw_receipt": (
        "ad4b1be4d6f7a5d7e61a7f31792dc119fbe0d1b"
        "0aed9b85ceff81c212b029272"
    ),
    "guard_receipt": (
        "284fec797694ac15179ca6632be010595c9da58e3"
        "1c1cc4245041ee55edc9a20"
    ),
}

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

status_before = git("status", "--short", "--", ".")
head = git("show", "-s", "--format=%h %s", "HEAD")

checks = []

def check(name, passed):
    checks.append((name, bool(passed)))

check("head", head == expected_head)

for label, path in paths.items():
    check(label + "_exists", path.is_file())

for label, expected in expected_hashes.items():
    check(label + "_hash", sha256(paths[label]) == expected)

data = json.loads(paths["json"].read_text(encoding="utf-8"))
candidate = json.loads(
    paths["source_candidate"].read_text(encoding="utf-8")
)
raw = paths["raw_receipt"].read_text(encoding="utf-8")
guard_receipt = paths["guard_receipt"].read_text(
    encoding="utf-8"
)
note = paths["note"].read_text(encoding="utf-8")

check(
    "packet",
    data["packet"] == "g60_h3_triality_galois_ledge_013f",
)
check(
    "mode",
    data["mode"] == "frozen_exact_h3_triality_galois_ledge",
)
check("audit_pass", data["audit_pass"] is True)
check("result_frozen", data["result_frozen"] is True)
check("candidate_frozen", data["candidate_frozen"] is True)
check("candidate_promoted", data["candidate_promoted"] is True)
check("failed_zero", data["failed_check_count"] == 0)
check("failed_empty", data["failed_checks"] == [])
check("earned_statement_present", bool(data["earned_statement"]))

check(
    "source_candidate_packet",
    candidate["packet"] == "g60_h3_triality_galois_ledge",
)
check("source_candidate_pass", candidate["candidate_pass"] is True)
check(
    "source_candidate_hash_recorded",
    data["authorities"]["source_candidate"]["sha256"]
    == expected_hashes["source_candidate"],
)
check(
    "source_candidate_path_permanent",
    pathlib.Path(
        data["authorities"]["source_candidate"]["path"]
    ).resolve()
    == paths["source_candidate"],
)

authority_map = {
    "exact_derivation_script": "derive",
    "raw_run_receipt": "raw_receipt",
    "consolidation_script": "firm",
    "independent_candidate_guard": "candidate_guard",
    "independent_guard_receipt": "guard_receipt",
    "source_candidate": "source_candidate",
}

for authority_name, path_label in authority_map.items():
    row = data["authorities"][authority_name]
    authority_path = pathlib.Path(row["path"]).resolve()

    check(
        "authority_" + authority_name + "_path",
        authority_path == paths[path_label],
    )
    check(
        "authority_" + authority_name + "_hash",
        row["sha256"] == sha256(paths[path_label]),
    )

theorem = data["theorem"]
check("carrier_size_60", theorem["carrier_size"] == 60)
check(
    "projective_lines_30",
    theorem["projective_line_count"] == 30,
)
check(
    "presentation_count_3",
    theorem["spherical_presentation_count"] == 3,
)
check(
    "triality_s3",
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
    "common_kernel",
    theorem["common_presentation_kernel"] == "A5_times_V4",
)
check(
    "common_kernel_order",
    theorem["common_presentation_kernel_order"] == 240,
)
check(
    "full_extension_order",
    theorem["full_extension_order"] == 1440,
)
check(
    "full_group",
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
    "galois_action",
    galois["presentation_permutation"] == [1, 0, 2],
)
check(
    "galois_matches_reverser",
    galois["matches_triality_reverser"] is True,
)

refined = data["refined_negative_result"]
check(
    "early_negative_preserved",
    refined["early_direction_audit_passed"] is False,
)
check(
    "refinement_passed",
    refined["refinement_passed"] is True,
)

for name, value in data["boundary"].items():
    check("boundary_" + name, value is False)

promotion = data["promotion"]
check(
    "promoted_without_recomputation",
    promotion["candidate_promoted_without_recomputation"]
    is True,
)
check(
    "candidate_checks_62",
    promotion["candidate_check_count"] == 62,
)
check(
    "guard_checks_54",
    promotion["guard_check_count"] == 54,
)
check("promotion_guard_passed", promotion["guard_passed"] is True)
check(
    "manuscript_not_mutated",
    promotion["manuscript_mutated"] is False,
)

required_raw = [
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
    "GOLDEN_GALOIS_OUTER_AUTOMORPHISM_PROVED: True",
]

for line in required_raw:
    check(
        "raw_" + line.lower().replace(" ", "_"),
        line in raw,
    )

check("candidate_guard_pass", "GUARD_PASS: True" in guard_receipt)
check(
    "candidate_guard_failed_zero",
    "FAILED_CHECK_COUNT: 0" in guard_receipt,
)

required_note = [
    "# G60 H3 triality-Galois ledge 013f",
    "The common presentation kernel is `A5 x V4`",
    "`A5 semidirect S4` extension",
    "`sqrt5 -> -sqrt5`",
    "does not select an absolute axis sign",
]

for phrase in required_note:
    check(
        "note_" + phrase.lower().replace(" ", "_"),
        phrase in note,
    )

status_after = git("status", "--short", "--", ".")
check(
    "repository_status_preserved",
    status_after == status_before,
)

failed = [
    name
    for name, passed in checks
    if not passed
]

print("== G60 H3 TRIALITY-GALOIS PERMANENT AUDIT 013f ==")
print("CHECK_COUNT:", len(checks))
print("FAILED_CHECK_COUNT:", len(failed))

for name, passed in checks:
    print("CHECK", name + ":", str(passed).lower())

print("FAILED_CHECKS:", failed)
print("AUDIT_PASS:", not failed)
print("RESULT_FROZEN:", data.get("result_frozen") is True)
print("PROJECT_MUTATION_PERFORMED: false")

if failed:
    raise SystemExit(1)
