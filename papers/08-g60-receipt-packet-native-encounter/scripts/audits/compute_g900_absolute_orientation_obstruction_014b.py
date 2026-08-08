#!/usr/bin/env python3
"""Consolidate the preregistered G900 absolute-orientation obstruction audits."""

from __future__ import annotations

import ast
import hashlib
import json
import pathlib
import subprocess
import sys


PROJECT = pathlib.Path(__file__).resolve().parents[2]
RESEARCH = PROJECT.parents[2]
P41 = RESEARCH / "mathematics/41-order-4-dodecahedral-residue"
P42 = RESEARCH / "mathematics/42-graph-automorphism-groups"
P45 = RESEARCH / "mathematics/45-native-g60-surface-complex"

SOURCE_DIR = (
    PROJECT
    / "scripts/audits"
    / "g900_absolute_orientation_obstruction_014b_sources"
)
RUN_DIR = (
    PROJECT
    / "artifacts/receipts"
    / "g900_absolute_orientation_obstruction_014b_runs"
)
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
PREREG_PATH = (
    PROJECT
    / "artifacts/json"
    / "g900_absolute_orientation_obstruction_preregistration_014a.v1.json"
)
UNTRACKED_013E = (
    PROJECT
    / "scripts/audits"
    / "compute_g60_root_relative_sign_kernel_census_013e.py"
)

DERIVE = (
    PROJECT
    / "scripts/audits"
    / "derive_g60_h3_triality_galois_ledge_013f.py"
)
H60 = (
    P45
    / "artifacts/json"
    / "g60_generated_extension_group_016.json"
)
DUAD = (
    PROJECT
    / "artifacts/json"
    / "g60_duad_orientation_bridge_census_011g.v1.json"
)
SURFACE = (
    P45
    / "artifacts/json"
    / "native_g60_surface_orientation_004.json"
)

EXPECTED_HEAD = "d6e4c9d"
EXPECTED_PREREG_SHA256 = (
    "0a43dc5524b6564e8de2656391fe71059"
    "f7193c294e70d550f61ff6917c44ca5"
)

EXPECTED_AUTHORITIES = {
    PROJECT / "artifacts/json/g60_duad_orientation_bridge_census_011g.v1.json":
        "abc9e038b323fdd5af852a91b87aca4c5a1e35a6e484608af27a04a399c52e9c",
    PROJECT / "artifacts/json/g60_full_A_orientation_character_extension_census_011o.v1.json":
        "ad684db8bb65c5eb731c972d33e685ffc18a947f63c9ba4e9758f815821f0941",
    PROJECT / "artifacts/json/g60_h3_triality_galois_ledge_013f.v1.json":
        "920635dd384d4325d2f415945811a7c816b0df5d0d475e974367010110a7a923",
    P41 / "scripts/lib/project41_native.py":
        "b6e3df135c93b27dcc0a823eb7ab036f6740a82664c7502f420d2a76a2cb962a",
    P41 / "scripts/audit_external_carrier_native_frame_compatibility_030p.py":
        "deb534de0ec401a60ccaf80ce23b460c3c66b49436a6fdb3b7156d35afb08c7d",
    P42 / "artifacts/json/native_g60_fiber_product_isomorphism_044.json":
        "b37313b135495752b11e525bb61979163fdf54aec4be4f5d027dcee64c9efc21",
    P45 / "artifacts/json/native_g60_surface_orientation_004.json":
        "b7671045c8dee327d9f02d6a04c5707231f46815e05596b2b1074bed564b2ae8",
    P45 / "artifacts/json/g60_generated_extension_group_016.json":
        "87090707d5f018fbf9f4db5ad793fc6b492e9fd6fec3f3c54af89d985f2d5d63",
    P45 / "artifacts/json/g900_full_automorphism_group_census_021.json":
        "8f85f690366e283148feb49bdd00a836244c054a2a0ac55422e6ac568754b484",
    P45 / "artifacts/json/g900_residual_involution_slot_maps_022.json":
        "92d91c90dbf88127a5d2972d9445c29a4ed98e2f7dc67ee5b262b692463493a5",
    P45 / "artifacts/json/g900_projection_and_automorphism_wrapup_023.json":
        "c9186b3a5df08d1591691881ca375f4ede865aa0708a12a7374f03395333ee9c",
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

RUNS = [
    {
        "id": "004_v4_alignment",
        "source": "tricycle_v4_alignment_004.py",
        "args": [DERIVE, H60, DUAD],
        "markers": [
            "V4_ALIGNMENT_PROVED: True",
            "CLASSIFICATION: tricycle_sheet_V4_is_native_V4_under_each_spherical_to_native_G60_identification",
            "G900_GLOBAL_LIFT_TESTED: false",
        ],
    },
    {
        "id": "008_extension_membership",
        "source": "tricycle_extension_membership_008.py",
        "args": [DERIVE, H60, DUAD, P41],
        "markers": [
            "AUDIT_PASS: True",
            "CLASSIFICATION: transverse_V4_universally_excluded_from_tricycle_full_extension",
            "G900_GLOBAL_FIELD_SEARCHED: false",
        ],
    },
    {
        "id": "010_exact_A60",
        "source": "transverse_v4_exact_order_010.py",
        "args": [P41, H60, DUAD],
        "markers": [
            "ORDER_EQUALS_A60: True",
            "ORDER_EQUALS_S60: False",
            "AUDIT_PASS: True",
            "CLASSIFICATION: transverse_V4_pair_generates_exact_A60",
        ],
    },
    {
        "id": "011_absolute_character",
        "source": "absolute_orientation_character_011.py",
        "args": [P41, H60, SURFACE, DUAD],
        "markers": [
            "ORIENTATION_PRESERVING_COUNT: 240",
            "ORIENTATION_REVERSING_COUNT: 240",
            "SURFACE_CHARACTER_HOMOMORPHISM_FAILURE_COUNT: 0",
            "SURFACE_CHARACTER_IS_PARITY: False",
            "GENERATED_CLOSURE_FROM_A60_AND_H60: S60",
            "RELATIVE_ORIENTATION_CHARACTER_EXTENDS: False",
            "ABSOLUTE_POSITIVE_SHEET_SELECTED: false",
            "EXTERNAL_ANCHOR_REQUIRED: true",
            "AUDIT_PASS: True",
        ],
    },
    {
        "id": "014_vertex_root_bridge",
        "source": "vertex_orientation_root_bridge_014.py",
        "args": [PROJECT, P42],
        "markers": [
            "VERTEX_STABILIZER_FIXED_ROOT_COUNT: 0",
            "VALID_EQUIVARIANT_MAP_COUNT: 0",
            "CLASSIFICATION: no_H60_equivariant_vertex_to_orientation_root_map",
            "VERTEX_ROOT_CROSSWALK_PROVED: False",
            "AUDIT_PASS: True",
        ],
    },
    {
        "id": "015_half_flip_incidence",
        "source": "half_flip_relative_root_incidence_015.py",
        "args": [PROJECT, P41, P42],
        "markers": [
            "H60_HALF_FLIP_CENTRALIZER_ORDER: 1",
            "STATE_MATCH_COUNT_PROFILE: {0: 40, 1: 20}",
            "UNIQUE_ROOT_AT_EVERY_STATE: False",
            "CLASSIFICATION: half_flip_relative_root_incidence_nonfunctional",
            "CARRIER_RELATIVE_ROOT_MAP_PROVED: False",
            "AUDIT_PASS: True",
        ],
    },
    {
        "id": "016_nearest_root",
        "source": "half_flip_nearest_root_016.py",
        "args": [PROJECT, P41, P42, P45],
        "markers": [
            "FIXED_SLOTS: [6, 12, 13]",
            "MIXED_FIXED_SLOTS: [6]",
            "PURE_IDENTITY_FIXED_SLOTS: [12, 13]",
            "MINIMIZER_COUNT_PROFILE: {1: 38, 2: 20, 8: 2}",
            "UNIQUE_FIXED_HINGE_PROVED: True",
            "NEAREST_ROOT_MAP_PROVED: False",
            "AUDIT_PASS: True",
        ],
    },
    {
        "id": "017_root_germ",
        "source": "half_flip_root_germ_017.py",
        "args": [PROJECT, P41, P42],
        "markers": [
            "HALF_FLIP_ORBIT_COUNT: 30",
            "HALF_ORBIT_DUAD_COUNT_PROFILE: {1: 19, 2: 10, 4: 1}",
            "INVERSION_COVARIANCE_FAILURE_COUNT: 0",
            "CLASSIFICATION: first_order_hinge_germ_reduces_but_does_not_close_root_ambiguity",
            "RADIUS_ONE_ROOT_MAP_PROVED: False",
            "RADIUS_ZERO_INVERSION_COVARIANCE_PROVED: True",
            "AUDIT_PASS: True",
        ],
    },
]


def sha256_file(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=PROJECT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout.strip()


def scalar(text: str, name: str):
    prefix = name + ":"
    for line in text.splitlines():
        if line.startswith(prefix):
            return line[len(prefix):].strip()
    return None


def literal_scalar(text: str, name: str):
    value = scalar(text, name)
    if value is None:
        return None
    try:
        return ast.literal_eval(value)
    except (SyntaxError, ValueError):
        return value


def radius_unique_counts(text: str) -> dict[str, int]:
    counts = {}
    for line in text.splitlines():
        if not line.startswith("RADIUS ") or " PROFILE " not in line:
            continue
        prefix, profile_text = line.split(" PROFILE ", 1)
        radius = prefix.split()[1]
        profile = ast.literal_eval(profile_text)
        counts[radius] = int(profile["unique_state_count"])
    return counts


def run_source(row: dict[str, object]) -> dict[str, object]:
    run_id = str(row["id"])
    source_path = SOURCE_DIR / str(row["source"])
    command = [
        sys.executable,
        str(source_path),
        *[str(value) for value in row["args"]],
    ]

    print("RUN_STARTED:", run_id, flush=True)
    completed = subprocess.run(
        command,
        cwd=PROJECT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    output = completed.stdout
    output_path = RUN_DIR / f"{run_id}.txt"
    output_path.write_text(output, encoding="utf-8")

    missing_markers = [
        marker for marker in row["markers"]
        if marker not in output
    ]

    print("RUN_RC:", run_id, completed.returncode, flush=True)
    print(
        "RUN_MARKER_FAILURE_COUNT:",
        run_id,
        len(missing_markers),
        flush=True,
    )

    return {
        "audit_id": run_id,
        "source": str(source_path.relative_to(PROJECT)),
        "command_arguments": [
            str(value) for value in row["args"]
        ],
        "return_code": completed.returncode,
        "output_line_count": len(output.splitlines()),
        "output_sha256": sha256_text(output),
        "receipt": str(output_path.relative_to(PROJECT)),
        "required_marker_count": len(row["markers"]),
        "missing_markers": missing_markers,
        "passed": (
            completed.returncode == 0
            and not missing_markers
        ),
        "classification": scalar(output, "CLASSIFICATION"),
        "audit_pass": scalar(output, "AUDIT_PASS"),
        "_output": output,
    }


RUN_DIR.mkdir(parents=True, exist_ok=True)
JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
NOTE_PATH.parent.mkdir(parents=True, exist_ok=True)
RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)

head = git("rev-parse", "--short", "HEAD")
status_before = git("status", "--short", "--", ".")

authority_rows = []
for path, expected in EXPECTED_AUTHORITIES.items():
    exists = path.is_file()
    actual = sha256_file(path) if exists else None
    authority_rows.append({
        "path": str(path),
        "exists": exists,
        "expected_sha256": expected,
        "actual_sha256": actual,
        "hash_match": actual == expected,
    })

source_rows = []
for name, expected in sorted(EXPECTED_SOURCES.items()):
    path = SOURCE_DIR / name
    exists = path.is_file()
    actual = sha256_file(path) if exists else None
    source_rows.append({
        "path": str(path.relative_to(PROJECT)),
        "exists": exists,
        "expected_sha256": expected,
        "actual_sha256": actual,
        "hash_match": actual == expected,
    })

prereg_exists = PREREG_PATH.is_file()
prereg_actual = (
    sha256_file(PREREG_PATH)
    if prereg_exists
    else None
)
untracked_013e_status = (
    "?? scripts/audits/"
    "compute_g60_root_relative_sign_kernel_census_013e.py"
)
untracked_013e_preserved = (
    UNTRACKED_013E.is_file()
    and untracked_013e_status in status_before.splitlines()
)

preflight_checks = {
    "head_is_preregistered_commit":
        head == EXPECTED_HEAD,
    "preregistration_present":
        prereg_exists,
    "preregistration_hash_matches":
        prereg_actual == EXPECTED_PREREG_SHA256,
    "all_authorities_present":
        all(row["exists"] for row in authority_rows),
    "all_authority_hashes_match":
        all(row["hash_match"] for row in authority_rows),
    "eight_permanent_sources_present":
        len(source_rows) == 8
        and all(row["exists"] for row in source_rows),
    "all_permanent_source_hashes_match":
        all(row["hash_match"] for row in source_rows),
    "untracked_013e_preserved":
        untracked_013e_preserved,
}

if not all(preflight_checks.values()):
    print("== G900 ABSOLUTE-ORIENTATION CONSOLIDATION 014B ==")
    print("PREFLIGHT_PASS: False")
    print(
        "FAILED_PREFLIGHT_CHECKS:",
        [
            name for name, passed in preflight_checks.items()
            if not passed
        ],
    )
    print("CONSOLIDATED_COMPUTATION_PERFORMED: false")
    print("RESULT_FROZEN: false")
    raise SystemExit(1)

run_rows = [run_source(row) for row in RUNS]
outputs = {
    row["audit_id"]: row.pop("_output")
    for row in run_rows
}

radial_counts = radius_unique_counts(
    outputs["017_root_germ"]
)

derived = {
    "tricycle_v4_alignment_proved":
        scalar(
            outputs["004_v4_alignment"],
            "V4_ALIGNMENT_PROVED",
        ) == "True",
    "tricycle_extension_excludes_transverse_v4":
        scalar(
            outputs["008_extension_membership"],
            "CLASSIFICATION",
        ) == (
            "transverse_V4_universally_excluded_"
            "from_tricycle_full_extension"
        ),
    "transverse_v4_pair_generates_A60":
        scalar(
            outputs["010_exact_A60"],
            "ORDER_EQUALS_A60",
        ) == "True",
    "generated_group_order":
        scalar(
            outputs["010_exact_A60"],
            "GROUP_ORDER",
        ),
    "surface_character_is_homomorphism":
        scalar(
            outputs["011_absolute_character"],
            "SURFACE_CHARACTER_HOMOMORPHISM_FAILURE_COUNT",
        ) == "0",
    "surface_character_differs_from_parity":
        scalar(
            outputs["011_absolute_character"],
            "SURFACE_CHARACTER_IS_PARITY",
        ) == "False",
    "closure_from_A60_and_H60":
        scalar(
            outputs["011_absolute_character"],
            "GENERATED_CLOSURE_FROM_A60_AND_H60",
        ),
    "relative_character_extends":
        scalar(
            outputs["011_absolute_character"],
            "RELATIVE_ORIENTATION_CHARACTER_EXTENDS",
        ) == "True",
    "external_anchor_required":
        scalar(
            outputs["011_absolute_character"],
            "EXTERNAL_ANCHOR_REQUIRED",
        ) == "true",
    "vertex_root_equivariant_map_count":
        literal_scalar(
            outputs["014_vertex_root_bridge"],
            "VALID_EQUIVARIANT_MAP_COUNT",
        ),
    "half_flip_centralizer_order_in_H60":
        literal_scalar(
            outputs["015_half_flip_incidence"],
            "H60_HALF_FLIP_CENTRALIZER_ORDER",
        ),
    "half_flip_state_match_count_profile":
        literal_scalar(
            outputs["015_half_flip_incidence"],
            "STATE_MATCH_COUNT_PROFILE",
        ),
    "fixed_slots":
        literal_scalar(
            outputs["016_nearest_root"],
            "FIXED_SLOTS",
        ),
    "mixed_fixed_slots":
        literal_scalar(
            outputs["016_nearest_root"],
            "MIXED_FIXED_SLOTS",
        ),
    "nearest_root_minimizer_count_profile":
        literal_scalar(
            outputs["016_nearest_root"],
            "MINIMIZER_COUNT_PROFILE",
        ),
    "radial_unique_state_counts":
        radial_counts,
    "half_flip_orbit_count":
        literal_scalar(
            outputs["017_root_germ"],
            "HALF_FLIP_ORBIT_COUNT",
        ),
    "half_orbit_duad_count_profile":
        literal_scalar(
            outputs["017_root_germ"],
            "HALF_ORBIT_DUAD_COUNT_PROFILE",
        ),
    "radius_zero_inversion_covariance":
        scalar(
            outputs["017_root_germ"],
            "RADIUS_ZERO_INVERSION_COVARIANCE_PROVED",
        ) == "True",
}

claim_checks = {
    "all_eight_runs_pass":
        len(run_rows) == 8
        and all(row["passed"] for row in run_rows),
    "tricycle_v4_alignment":
        derived["tricycle_v4_alignment_proved"],
    "transverse_v4_excluded_from_tricycle_extension":
        derived["tricycle_extension_excludes_transverse_v4"],
    "transverse_v4_pair_generates_exact_A60":
        derived["transverse_v4_pair_generates_A60"],
    "surface_character_homomorphism":
        derived["surface_character_is_homomorphism"],
    "surface_character_not_permutation_parity":
        derived["surface_character_differs_from_parity"],
    "A60_H60_closure_is_S60":
        derived["closure_from_A60_and_H60"] == "S60",
    "surface_character_does_not_extend":
        derived["relative_character_extends"] is False,
    "external_anchor_required":
        derived["external_anchor_required"],
    "no_H60_equivariant_vertex_root_map":
        derived["vertex_root_equivariant_map_count"] == 0,
    "half_flip_centralizer_trivial":
        derived["half_flip_centralizer_order_in_H60"] == 1,
    "unique_mixed_fixed_hinge":
        derived["fixed_slots"] == [6, 12, 13]
        and derived["mixed_fixed_slots"] == [6],
    "radial_profile_exact":
        radial_counts == {
            "0": 38,
            "1": 42,
            "2": 50,
            "3": 50,
            "4": 45,
            "5": 36,
            "6": 0,
        },
    "radius_zero_inversion_covariant":
        derived["radius_zero_inversion_covariance"],
}

failed_claims = [
    name for name, passed in claim_checks.items()
    if not passed
]
audit_pass = not failed_claims

classification = (
    "canonical_G900_orientation_hinge_with_"
    "unanchored_absolute_orientation_obstruction"
    if audit_pass
    else "G900_absolute_orientation_consolidation_failed"
)

result = {
    "packet":
        "g900_absolute_orientation_obstruction_014b",
    "mode":
        "permanent_preregistered_consolidated_recomputation",
    "consonance_scalar": "G900",
    "locked_preregistration_commit": EXPECTED_HEAD,
    "preregistration": {
        "path": str(PREREG_PATH.relative_to(PROJECT)),
        "expected_sha256": EXPECTED_PREREG_SHA256,
        "actual_sha256": prereg_actual,
        "hash_match": prereg_actual == EXPECTED_PREREG_SHA256,
    },
    "authorities": authority_rows,
    "permanent_source_custody": source_rows,
    "preflight_checks": preflight_checks,
    "source_runs": run_rows,
    "derived_results": derived,
    "claim_checks": claim_checks,
    "failed_claim_count": len(failed_claims),
    "failed_claims": failed_claims,
    "audit_pass": audit_pass,
    "classification": classification,
    "earned_statement": (
        "The G900 consonance scalar contains a canonical mixed fixed "
        "hinge at slot 6. Its native tricycle V4 and half-flip-transverse "
        "V4 generate exact A60, while the oriented-surface character on "
        "H60 does not extend through the resulting S60 closure. No "
        "H60-equivariant vertex-to-root map exists, direct half-flip "
        "incidence is nonfunctional, and none of the tested radial "
        "hinge-germ rules selects a root at every local state. Thus an "
        "absolute orientation is not selected without an added anchor "
        "within the preregistered character, equivariant-map, incidence, "
        "nearest-root, and radial-germ families."
    ),
    "boundary": {
        "canonical_orientation_hinge_proved": audit_pass,
        "tested_selector_families_closed": audit_pass,
        "global_impossibility_over_all_graph_definable_selectors": False,
        "absolute_orientation_selected_without_anchor": False,
        "physical_claim": False,
        "force_claim": False,
        "energy_claim": False,
        "spacetime_claim": False,
        "quantum_claim": False,
    },
    "promotion": {
        "consolidated_computation_performed": True,
        "result_candidate_written": True,
        "independent_guard_performed": False,
        "result_frozen": False,
        "commit_performed": False,
        "push_performed": False,
    },
    "repository": {
        "untracked_013e_preserved": untracked_013e_preserved,
        "preexisting_out_of_scope_status": [untracked_013e_status],
    },
}

JSON_PATH.write_text(
    json.dumps(result, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

note = f"""# G900 absolute-orientation obstruction consolidation 014B

## Status

- Classification: `{classification}`
- Consolidated audit pass: `{str(audit_pass).lower()}`
- Absolute orientation selected without an anchor: `false`
- Independent result guard performed: `false`
- Result frozen: `false`
- Physical claim: `false`

## Earned result

The G900 consonance scalar has a canonical mixed fixed hinge at slot 6.
The aligned native tricycle V4 and the half-flip-transverse V4 generate
the exact alternating group A60. The oriented-surface character on H60
does not extend through the S60 closure generated by A60 and H60.

The preregistered selector families also fail to remove the remaining
binary orientation freedom: there is no H60-equivariant vertex-to-root
map, direct half-flip root incidence is nonfunctional, the nearest-root
rule is only partially unique, and the complete radius-zero through
radius-six hinge-germ census never selects a unique root at every state.

Accordingly, within the preregistered character, equivariant-map,
incidence, nearest-root, and radial-germ families, absolute orientation
requires an added anchor.

## Boundary

This is not a proof that every conceivable graph-definable selector is
impossible. It is a finite computational theorem for the exact frozen
G900 constructor and the explicitly preregistered selector families.
No physical force, energy, spacetime, or quantum claim is made.
"""
NOTE_PATH.write_text(note, encoding="utf-8")

receipt_lines = [
    "== G900 ABSOLUTE-ORIENTATION OBSTRUCTION CONSOLIDATION 014B ==",
    f"HEAD: {head}",
    f"PREREGISTRATION_SHA256: {prereg_actual}",
    f"AUTHORITY_COUNT: {len(authority_rows)}",
    f"PERMANENT_SOURCE_COUNT: {len(source_rows)}",
    f"SOURCE_RUN_COUNT: {len(run_rows)}",
]

for row in run_rows:
    receipt_lines.append(
        "RUN "
        + str(row["audit_id"])
        + " RC "
        + str(row["return_code"])
        + " MARKER_FAILURE_COUNT "
        + str(len(row["missing_markers"]))
        + " OUTPUT_SHA256 "
        + str(row["output_sha256"])
    )

receipt_lines.extend([
    f"RADIAL_UNIQUE_STATE_COUNTS: {radial_counts}",
    f"CHECK_COUNT: {len(claim_checks)}",
    f"FAILED_CHECK_COUNT: {len(failed_claims)}",
    f"FAILED_CHECKS: {failed_claims}",
    f"AUDIT_PASS: {audit_pass}",
    f"CLASSIFICATION: {classification}",
    "ABSOLUTE_ORIENTATION_SELECTED: false",
    "GLOBAL_SELECTOR_IMPOSSIBILITY_CLAIM: false",
    "PHYSICAL_CLAIM: false",
    "INDEPENDENT_GUARD_PERFORMED: false",
    "RESULT_FROZEN: false",
    "COMMIT_PERFORMED: false",
    "PUSH_PERFORMED: false",
    "UNTRACKED_013E_PRESERVED: true",
])
RECEIPT_PATH.write_text(
    "\n".join(receipt_lines) + "\n",
    encoding="utf-8",
)

status_after = git("status", "--short", "--", ".")

print()
print("== G900 ABSOLUTE-ORIENTATION CONSOLIDATION 014B ==")
print("HEAD:", head)
print("PREFLIGHT_PASS:", all(preflight_checks.values()))
print("SOURCE_RUN_COUNT:", len(run_rows))
print("SOURCE_RUN_PASS_COUNT:", sum(row["passed"] for row in run_rows))
print("RADIAL_UNIQUE_STATE_COUNTS:", radial_counts)
print("CHECK_COUNT:", len(claim_checks))
print("FAILED_CHECK_COUNT:", len(failed_claims))
print("FAILED_CHECKS:", failed_claims)
print("AUDIT_PASS:", audit_pass)
print("CLASSIFICATION:", classification)
print("ABSOLUTE_ORIENTATION_SELECTED: false")
print("GLOBAL_SELECTOR_IMPOSSIBILITY_CLAIM: false")
print("PHYSICAL_CLAIM: false")
print("INDEPENDENT_GUARD_PERFORMED: false")
print("RESULT_FROZEN: false")
print("UNTRACKED_013E_PRESERVED:", untracked_013e_preserved)
print("JSON:", JSON_PATH)
print("JSON_SHA256:", sha256_file(JSON_PATH))
print("NOTE:", NOTE_PATH)
print("NOTE_SHA256:", sha256_file(NOTE_PATH))
print("RECEIPT:", RECEIPT_PATH)
print("RECEIPT_SHA256:", sha256_file(RECEIPT_PATH))
print("REPOSITORY_STATUS_AFTER:")
for line in status_after.splitlines():
    print(line)
print("PROJECT_MUTATION_PERFORMED: true")
print("MUTATION_SCOPE: 014b_candidate_and_raw_run_receipts_only")

if not audit_pass:
    raise SystemExit(1)
