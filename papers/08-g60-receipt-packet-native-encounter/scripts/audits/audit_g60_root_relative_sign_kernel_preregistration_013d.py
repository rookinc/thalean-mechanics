#!/usr/bin/env python3

import hashlib
import json
import pathlib
import subprocess
import sys

project = pathlib.Path(sys.argv[1]).resolve()
maker = pathlib.Path(sys.argv[2]).resolve()
candidate = pathlib.Path(sys.argv[3]).resolve()

expected_head = (
    "0843940 Add finite receipt manuscript sprint artifacts"
)
expected_maker_hash = (
    "06513e043949d6f1a230d142061e88b3afc4b996158776d5dcd6e95901b6e303"
)
expected_candidate_hash = (
    "215bc072c1fc34a287e80cdd4a97050ae15507e913d13a2a803467d962014d93"
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
data = json.loads(candidate.read_text(encoding="utf-8"))

checks = []

def check(name, passed):
    checks.append((name, bool(passed)))

check("head", head == expected_head)
check("maker_hash", sha256(maker) == expected_maker_hash)
check(
    "candidate_hash",
    sha256(candidate) == expected_candidate_hash,
)
check(
    "packet",
    data.get("packet")
    == "g60_root_relative_sign_kernel_preregistration_013d",
)
check("locked_head", data.get("locked_head") == expected_head)
check("authority_count", len(data.get("authorities", {})) == 3)

for label, row in sorted(data["authorities"].items()):
    path = pathlib.Path(row["path"])
    check(label + "_exists", path.is_file())
    check(
        label + "_hash",
        path.is_file() and sha256(path) == row["sha256"],
    )

obj = data["object_under_test"]
check("carrier", obj["carrier"] == "twenty_orientation_roots")
check("supporting_character", obj["supporting_full_A_character"] == "p+n")
check("absolute_sign_false", obj["absolute_sign_selected"] is False)

pred = data["predictions"]
check("two_bridges", pred["bridge_count"] == 2)
check("twenty_rows", pred["bridge_row_count_each"] == 20)
check("twenty_roots", pred["root_count_each"] == 20)
check(
    "epsilon_profile",
    pred["epsilon_profile_each"] == {"0": 10, "1": 10},
)
check("equal_root_sets", pred["root_sets_equal"] is True)
check(
    "exact_complements",
    pred["bridge_signings_are_exact_complements"] is True,
)
check(
    "equal_kernels",
    pred["relative_sign_kernels_equal"] is True,
)
check("same_pairs_200", pred["same_sign_ordered_pair_count"] == 200)
check(
    "opposite_pairs_200",
    pred["opposite_sign_ordered_pair_count"] == 200,
)
check("rank_one", pred["kernel_rank"] == 1)
check("trace_twenty", pred["kernel_trace"] == 20)
check(
    "row_sums_zero",
    pred["kernel_row_sum_profile"] == {"0": 20},
)
check(
    "inverse_pairs_opposed",
    pred["inverse_root_pairs_have_opposite_sign"] is True,
)
check("required_test_count", len(data["required_tests"]) == 14)
check(
    "classification",
    data["predicted_classification"]
    == "twenty_root_orientation_carrier_has_canonical_relative_sign_kernel_without_absolute_sign_or_spherical_embedding",
)
check(
    "all_boundaries_false",
    all(value is False for value in data["boundary"].values()),
)
check("candidate_only", data["promotion"]["candidate_only"] is True)
check(
    "census_not_performed",
    data["promotion"]["census_performed"] is False,
)
check("not_promoted", data["promotion"]["promoted"] is False)

status_after = git("status", "--short")
check("repository_status_preserved", status_after == status_before)

failed = [name for name, passed in checks if not passed]

print("== G60 ROOT RELATIVE-SIGN KERNEL PREREGISTRATION GUARD 013d ==")
print("CHECK_COUNT:", len(checks))
print("FAILED_CHECK_COUNT:", len(failed))
for name, passed in checks:
    print("CHECK", name + ":", str(passed).lower())
print("GUARD_PASS:", str(not failed).lower())
print("FAILED_CHECKS:", failed)
print("CANDIDATE_PROMOTED: false")
print("PROJECT_MUTATION_PERFORMED: false")

if failed:
    raise SystemExit(1)
