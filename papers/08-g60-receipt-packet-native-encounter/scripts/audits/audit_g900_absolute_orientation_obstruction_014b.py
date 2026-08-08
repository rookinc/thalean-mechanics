#!/usr/bin/env python3
"""Independently audit and freeze the G900 014B obstruction result."""

from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess


PROJECT = pathlib.Path(__file__).resolve().parents[2]

JSON_PATH = (
    PROJECT
    / "artifacts/json"
    / "g900_absolute_orientation_obstruction_014b.v1.json"
)
NOTE_PATH = (
    PROJECT
    / "notes"
    / "g900_absolute_orientation_obstruction_014b.md"
)
RECEIPT_PATH = (
    PROJECT
    / "artifacts/receipts"
    / "g900_absolute_orientation_obstruction_014b.txt"
)
RUN_DIR = (
    PROJECT
    / "artifacts/receipts"
    / "g900_absolute_orientation_obstruction_014b_runs"
)
SOURCE_DIR = (
    PROJECT
    / "scripts/audits"
    / "g900_absolute_orientation_obstruction_014b_sources"
)
DRIVER_PATH = (
    PROJECT
    / "scripts/audits"
    / "compute_g900_absolute_orientation_obstruction_014b.py"
)
PREREG_PATH = (
    PROJECT
    / "artifacts/json"
    / "g900_absolute_orientation_obstruction_preregistration_014a.v1.json"
)

EXPECTED_HEAD = "d6e4c9d"
EXPECTED_CLASSIFICATION = (
    "canonical_G900_orientation_hinge_with_"
    "unanchored_absolute_orientation_obstruction"
)

EXPECTED_HASHES = {
    "json":
        "7d08c51d7d0fa52c7cbcf09b34baf65d06b97c280247f74155210b4dc43eb984",
    "note":
        "81033756aa8db85679c0bea02fa05994d4980893ab645e1dcd0b013f5a98da5e",
    "receipt":
        "fd37933874e4fd339e9e3ce1d44098b9d3a5f29dbe930cbafaa871bc7e138c1c",
    "driver":
        "e458d2b51cbe6cc73953289b2e9590776283d051cee8f7f49a05dd0a807ae8fe",
    "preregistration":
        "0a43dc5524b6564e8de2656391fe71059f7193c294e70d550f61ff6917c44ca5",
}

EXPECTED_SOURCES = {
    "absolute_orientation_character_011.py":
        "b2a39e05fa64f37aab281b8dacb7de196d7fcc4ece7a545c349a46126b5c3f30",
    "half_flip_nearest_root_016.py":
        "eb2c74b82e35630a55fad345023da68acc332fbfa965f4d2a3fa6f0f813647f7",
    "half_flip_relative_root_incidence_015.py":
        "95e211068305a6831b18f5938353237524d0baccd218254c0b0db95ef668ee37",
    "half_flip_root_germ_017.py":
        "df109d2347b7e6c52ccca1f4ee30f7695d3c1d19af44567bc4a08105d46e4d7e",
    "transverse_v4_exact_order_010.py":
        "1d575e2e00af0677ce8c2024501ad21ffc18de043e7f1695964821c3896ff1d7",
    "tricycle_extension_membership_008.py":
        "17b641f90a5ed0a615565765c9c9a2a1a168e94d4c772c8a25ac86b2f3866b3a",
    "tricycle_v4_alignment_004.py":
        "ba495c8266002cab382d9fd0e228f81ac7763675d2ee4c56357d40d11fb1c5a8",
    "vertex_orientation_root_bridge_014.py":
        "49606d2670b8180b0326a35b48b0352cc3f4816a8bf3d762523234a3dea3aa4a",
}

EXPECTED_RUNS = {
    "004_v4_alignment.txt":
        "22c4ab3ab510274e253dc836087518984a9f52e5985ca74a410cb573b3a68cc4",
    "008_extension_membership.txt":
        "271bd7419ce8faf3158fefa32942041d4e75658c03d2634c9d1a5b2d9d852c0f",
    "010_exact_A60.txt":
        "d68a42bc186873743a17e5d8894cffad07af9990b6bda201a3aa04b9a7492609",
    "011_absolute_character.txt":
        "ce9d873c4263b9a093336b167bbd38d26f5a2a6138d0d2ea7c2ffd72d578b75b",
    "014_vertex_root_bridge.txt":
        "d87232b0f23f709caba31b3d17c8d056b8367733708c409852697524b1af0f73",
    "015_half_flip_incidence.txt":
        "a8bfee166817647c30223ed109d384bbfa58fb10269b279a12aa2a072cf493d5",
    "016_nearest_root.txt":
        "65d5a985f70def44fa0a2ad26b7f9ad148b820142908604930c5ea84f648b1d2",
    "017_root_germ.txt":
        "bc2d9fcf983d39a1682892f2d3385790a9591f4599ed39894deccd39a3744156",
}

EXPECTED_RUN_IDS = {
    name.removesuffix(".txt")
    for name in EXPECTED_RUNS
}

EXPECTED_A60_ORDER = (
    "416049355637069507213817059161168219037708630318062297622463884820"
    "4800000000000000"
)


def sha256(path: pathlib.Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=PROJECT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout.strip()


checks: dict[str, bool] = {}


def check(name: str, value) -> None:
    checks[name] = bool(value)


head = git("rev-parse", "--short", "HEAD")
status_before = git("status", "--short", "--", ".")
status_lines = status_before.splitlines()

check("head_is_preregistered_commit", head == EXPECTED_HEAD)
check(
    "untracked_013e_preserved",
    (
        "?? scripts/audits/"
        "compute_g60_root_relative_sign_kernel_census_013e.py"
    ) in status_lines,
)

check("json_hash", sha256(JSON_PATH) == EXPECTED_HASHES["json"])
check("note_hash", sha256(NOTE_PATH) == EXPECTED_HASHES["note"])
check(
    "consolidated_receipt_hash",
    sha256(RECEIPT_PATH) == EXPECTED_HASHES["receipt"],
)
check("driver_hash", sha256(DRIVER_PATH) == EXPECTED_HASHES["driver"])
check(
    "preregistration_hash",
    sha256(PREREG_PATH) == EXPECTED_HASHES["preregistration"],
)

source_files = sorted(SOURCE_DIR.glob("*.py"))
check("source_count_8", len(source_files) == 8)
check(
    "source_name_set_exact",
    {path.name for path in source_files} == set(EXPECTED_SOURCES),
)
check(
    "all_source_hashes_exact",
    all(
        sha256(SOURCE_DIR / name) == expected
        for name, expected in EXPECTED_SOURCES.items()
    ),
)

run_files = sorted(RUN_DIR.glob("*.txt"))
check("raw_run_count_8", len(run_files) == 8)
check(
    "raw_run_name_set_exact",
    {path.name for path in run_files} == set(EXPECTED_RUNS),
)
check(
    "all_raw_run_hashes_exact",
    all(
        sha256(RUN_DIR / name) == expected
        for name, expected in EXPECTED_RUNS.items()
    ),
)

data = json.loads(JSON_PATH.read_text(encoding="utf-8"))

check(
    "packet",
    data.get("packet")
    == "g900_absolute_orientation_obstruction_014b",
)
check(
    "mode",
    data.get("mode")
    == "permanent_preregistered_consolidated_recomputation",
)
check("consonance_scalar", data.get("consonance_scalar") == "G900")
check(
    "locked_commit",
    data.get("locked_preregistration_commit") == EXPECTED_HEAD,
)
check("audit_pass", data.get("audit_pass") is True)
check(
    "classification",
    data.get("classification") == EXPECTED_CLASSIFICATION,
)
check("failed_claim_count_zero", data.get("failed_claim_count") == 0)
check("failed_claims_empty", data.get("failed_claims") == [])
check(
    "all_claim_checks_true",
    len(data.get("claim_checks", {})) == 14
    and all(data["claim_checks"].values()),
)
check(
    "all_preflight_checks_true",
    data.get("preflight_checks")
    and all(data["preflight_checks"].values()),
)

authority_rows = data.get("authorities", [])
check("authority_count_11", len(authority_rows) == 11)
check(
    "authority_rows_self_consistent",
    all(
        row.get("exists") is True
        and row.get("hash_match") is True
        and row.get("actual_sha256") == row.get("expected_sha256")
        and sha256(pathlib.Path(row["path"]))
            == row.get("expected_sha256")
        for row in authority_rows
    ),
)

custody_rows = data.get("permanent_source_custody", [])
check("custody_row_count_8", len(custody_rows) == 8)
check(
    "custody_rows_exact",
    all(
        row.get("exists") is True
        and row.get("hash_match") is True
        and row.get("actual_sha256") == row.get("expected_sha256")
        and sha256(PROJECT / row["path"])
            == row.get("expected_sha256")
        for row in custody_rows
    ),
)

source_runs = data.get("source_runs", [])
check("source_run_count_8", len(source_runs) == 8)
check(
    "source_run_ids_exact",
    {
        row.get("audit_id")
        for row in source_runs
    } == EXPECTED_RUN_IDS,
)
check(
    "source_runs_pass",
    all(
        row.get("return_code") == 0
        and row.get("passed") is True
        and row.get("missing_markers") == []
        and row.get("required_marker_count", 0) > 0
        for row in source_runs
    ),
)
check(
    "source_run_output_hashes_match_receipts",
    all(
        row.get("output_sha256")
        == sha256(PROJECT / row["receipt"])
        for row in source_runs
    ),
)

derived = data.get("derived_results", {})
check(
    "v4_alignment",
    derived.get("tricycle_v4_alignment_proved") is True,
)
check(
    "transverse_v4_excluded",
    derived.get("tricycle_extension_excludes_transverse_v4")
    is True,
)
check(
    "exact_A60",
    derived.get("transverse_v4_pair_generates_A60") is True
    and derived.get("generated_group_order") == EXPECTED_A60_ORDER,
)
check(
    "surface_character",
    derived.get("surface_character_is_homomorphism") is True
    and derived.get("surface_character_differs_from_parity") is True,
)
check(
    "S60_closure_obstruction",
    derived.get("closure_from_A60_and_H60") == "S60"
    and derived.get("relative_character_extends") is False
    and derived.get("external_anchor_required") is True,
)
check(
    "no_vertex_root_map",
    derived.get("vertex_root_equivariant_map_count") == 0,
)
check(
    "half_flip_centralizer",
    derived.get("half_flip_centralizer_order_in_H60") == 1,
)
check(
    "half_flip_incidence_profile",
    derived.get("half_flip_state_match_count_profile")
    == {"0": 40, "1": 20},
)
check(
    "canonical_mixed_hinge",
    derived.get("fixed_slots") == [6, 12, 13]
    and derived.get("mixed_fixed_slots") == [6],
)
check(
    "nearest_root_profile",
    derived.get("nearest_root_minimizer_count_profile")
    == {"1": 38, "2": 20, "8": 2},
)
check(
    "radial_profile",
    derived.get("radial_unique_state_counts")
    == {
        "0": 38,
        "1": 42,
        "2": 50,
        "3": 50,
        "4": 45,
        "5": 36,
        "6": 0,
    },
)
check(
    "half_flip_orbit_profile",
    derived.get("half_flip_orbit_count") == 30
    and derived.get("half_orbit_duad_count_profile")
        == {"1": 19, "2": 10, "4": 1}
    and derived.get("radius_zero_inversion_covariance") is True,
)

boundary = data.get("boundary", {})
check(
    "canonical_hinge_boundary",
    boundary.get("canonical_orientation_hinge_proved") is True,
)
check(
    "tested_families_closed",
    boundary.get("tested_selector_families_closed") is True,
)
check(
    "no_global_impossibility_overclaim",
    boundary.get(
        "global_impossibility_over_all_graph_definable_selectors"
    ) is False,
)
check(
    "no_unanchored_absolute_orientation",
    boundary.get("absolute_orientation_selected_without_anchor")
    is False,
)
check(
    "no_physical_claims",
    all(
        boundary.get(name) is False
        for name in (
            "physical_claim",
            "force_claim",
            "energy_claim",
            "spacetime_claim",
            "quantum_claim",
        )
    ),
)

promotion = data.get("promotion", {})
check(
    "candidate_promotion_state",
    promotion.get("consolidated_computation_performed") is True
    and promotion.get("result_candidate_written") is True
    and promotion.get("independent_guard_performed") is False
    and promotion.get("result_frozen") is False
    and promotion.get("commit_performed") is False
    and promotion.get("push_performed") is False,
)

repository = data.get("repository", {})
check(
    "repository_boundary",
    repository.get("untracked_013e_preserved") is True
    and repository.get("preexisting_out_of_scope_status") == [
        "?? scripts/audits/"
        "compute_g60_root_relative_sign_kernel_census_013e.py"
    ],
)

note_text = NOTE_PATH.read_text(encoding="utf-8")
note_words = " ".join(note_text.split())
receipt_text = RECEIPT_PATH.read_text(encoding="utf-8")

check(
    "note_boundary_language",
    "absolute orientation requires an added anchor" in note_words
    and "not a proof that every conceivable graph-definable selector"
        in note_words
    and "Physical claim: `false`" in note_words,
)
check(
    "receipt_boundary_language",
    f"CLASSIFICATION: {EXPECTED_CLASSIFICATION}" in receipt_text
    and "FAILED_CHECK_COUNT: 0" in receipt_text
    and "AUDIT_PASS: True" in receipt_text
    and "ABSOLUTE_ORIENTATION_SELECTED: false" in receipt_text
    and "GLOBAL_SELECTOR_IMPOSSIBILITY_CLAIM: false"
        in receipt_text
    and "PHYSICAL_CLAIM: false" in receipt_text,
)

status_after = git("status", "--short", "--", ".")
check("repository_not_mutated_by_guard", status_after == status_before)

failed = [
    name
    for name, passed in checks.items()
    if not passed
]
audit_pass = not failed

print("== G900 ABSOLUTE-ORIENTATION OBSTRUCTION AUDIT 014B ==")
print("PACKET:", data.get("packet"))
print("HEAD:", head)
print("JSON_SHA256:", sha256(JSON_PATH))
print("NOTE_SHA256:", sha256(NOTE_PATH))
print("RECEIPT_SHA256:", sha256(RECEIPT_PATH))
print("DRIVER_SHA256:", sha256(DRIVER_PATH))
print("SOURCE_COUNT:", len(source_files))
print("RAW_RUN_RECEIPT_COUNT:", len(run_files))
print("AUTHORITY_COUNT:", len(authority_rows))
print("CLAIM_CHECK_COUNT:", len(data.get("claim_checks", {})))
print(
    "RADIAL_UNIQUE_STATE_COUNTS:",
    derived.get("radial_unique_state_counts"),
)
print("CLASSIFICATION:", data.get("classification"))
print("CHECK_COUNT:", len(checks))
print("FAILED_CHECK_COUNT:", len(failed))
print("FAILED_CHECKS:", failed)

for name, passed in checks.items():
    print("CHECK", name + ":", str(passed).lower())

print("AUDIT_PASS:", audit_pass)
print(
    "INDEPENDENT_GUARD_PERFORMED:",
    str(audit_pass).lower(),
)
print("RESULT_FROZEN:", str(audit_pass).lower())
print("ABSOLUTE_ORIENTATION_SELECTED: false")
print("GLOBAL_SELECTOR_IMPOSSIBILITY_CLAIM: false")
print("PHYSICAL_CLAIM: false")
print("COMMIT_PERFORMED: false")
print("PUSH_PERFORMED: false")
print("UNTRACKED_013E_PRESERVED:", checks["untracked_013e_preserved"])
print("REPOSITORY_MUTATION_PERFORMED: false")

if not audit_pass:
    raise SystemExit(1)
