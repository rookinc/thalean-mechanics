#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from itertools import combinations
from pathlib import Path

HOME = Path.home()

PROJECT = HOME / "dev/cori/research/thalean_mechanics/papers/08-g60-receipt-packet-native-encounter"
PAPER7 = HOME / "dev/cori/research/thalean_mechanics/papers/07-finite-covariant-receipt-algebra-on-graphs"
PROJECT42 = HOME / "dev/cori/research/mathematics/42-graph-automorphism-groups"
ELECTRON = HOME / "dev/cori/research/physics/quantum_mechanics/01-the-electron-spins-twice"

ROOTS = [PAPER7, PROJECT42, ELECTRON]

PAPER7_ARTIFACT = (
    PAPER7
    / "artifacts/json/finite_covariant_receipt_algebra_on_graphs_theorem_001.v1.json"
)

EXACT_NAMES = [
    "g60_local_edges.csv",
    "native_g60_full_automorphism_group_042.json",
    "native_g60_lifted_automorphism_group_040.json",
    "native_g60_lifted_group_extension_type_041.json",
    "native_g60_full_group_fiber_product_043.json",
    "native_g60_fiber_product_isomorphism_044.json",
    "project42_g60_to_g30_a_quotient_certificate_035.json",
]

EXPECTED_PAPER7_VERDICT = (
    "finite_regular_graph_lifts_are_classified_by_holonomy_representations_"
    "and_decompose_by_the_index_of_the_holonomy_subgroup"
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_status(root: Path) -> list[str]:
    if not (root / ".git").exists():
        return []
    result = subprocess.run(
        ["git", "status", "--short"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    return result.stdout.splitlines()


def find_exact(name: str) -> list[Path]:
    found = []
    for root in ROOTS:
        if not root.exists():
            continue
        found.extend(path for path in root.rglob(name) if path.is_file())
    return sorted(set(found))


def json_walk(value, path="$"):
    yield path, value
    if isinstance(value, dict):
        for key, child in value.items():
            yield from json_walk(child, path + "." + str(key))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from json_walk(child, path + "[" + str(index) + "]")


def json_profile(path: Path) -> dict:
    value = json.loads(path.read_text())
    top_keys = sorted(value.keys()) if isinstance(value, dict) else []

    permutation_paths = []
    relevant_scalars = []

    for json_path, item in json_walk(value):
        if (
            isinstance(item, list)
            and len(item) == 60
            and all(isinstance(x, int) for x in item)
            and sorted(item) == list(range(60))
        ):
            permutation_paths.append(json_path)

        leaf = json_path.rsplit(".", 1)[-1].lower()
        if not isinstance(item, (dict, list)) and any(
            term in leaf
            for term in (
                "order",
                "automorphism",
                "vertex_count",
                "edge_count",
                "degree",
                "verdict",
                "schema",
            )
        ):
            relevant_scalars.append((json_path, item))

    return {
        "top_keys": top_keys,
        "permutation_path_count": len(permutation_paths),
        "permutation_paths_preview": permutation_paths[:12],
        "relevant_scalars_preview": relevant_scalars[:30],
    }


def csv_profile(path: Path) -> dict:
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fields = reader.fieldnames or []

    endpoint_candidates = []

    for left, right in combinations(fields, 2):
        pairs = []
        valid = True

        for row in rows:
            a = row.get(left)
            b = row.get(right)
            if a in (None, "") or b in (None, ""):
                valid = False
                break
            pairs.append((str(a), str(b)))

        if not valid:
            continue

        vertices = sorted({item for pair in pairs for item in pair})
        self_loop_count = sum(a == b for a, b in pairs)
        undirected_edges = {tuple(sorted((a, b))) for a, b in pairs}

        if len(vertices) == 60 and self_loop_count == 0:
            endpoint_candidates.append(
                {
                    "left": left,
                    "right": right,
                    "vertex_count": len(vertices),
                    "row_count": len(pairs),
                    "undirected_edge_count": len(undirected_edges),
                    "duplicate_undirected_row_count": len(pairs) - len(undirected_edges),
                }
            )

    return {
        "field_count": len(fields),
        "fields": fields,
        "row_count": len(rows),
        "endpoint_candidates": endpoint_candidates,
    }


print("OUT ==")
print("PACKET: g60_receipt_packet_encounter_source_lock_001")
print("MODE: read-only source authority lock")
print("TARGET:", PROJECT)
print("REPOSITORY_MUTATION: none")
print()

status_before = {
    str(root): git_status(root)
    for root in ROOTS
    if root.exists()
}

print("== ROOTS ==")
for root in ROOTS:
    print(
        "ROOT:",
        json.dumps(
            {
                "path": str(root),
                "exists": root.exists(),
                "git_status_before": status_before.get(str(root), []),
            },
            sort_keys=True,
        ),
    )

print()
print("== PAPER 7 ALGEBRA LOCK ==")

paper7_exists = PAPER7_ARTIFACT.exists()
paper7_hash = sha256_file(PAPER7_ARTIFACT) if paper7_exists else None
paper7_value = json.loads(PAPER7_ARTIFACT.read_text()) if paper7_exists else {}
paper7_verdict = paper7_value.get("verdict")

print("PAPER7_ARTIFACT:", PAPER7_ARTIFACT)
print("PAPER7_EXISTS:", str(paper7_exists).lower())
print("PAPER7_SHA256:", paper7_hash)
print("PAPER7_STATUS:", paper7_value.get("status"))
print("PAPER7_VERDICT:", paper7_verdict)
print(
    "CHECK_PAPER7_PACKET_LOCKED:",
    str(paper7_exists and paper7_verdict == EXPECTED_PAPER7_VERDICT).lower(),
)

print()
print("== EXACT SOURCE CENSUS ==")

matches_by_name = {}

for name in EXACT_NAMES:
    matches = find_exact(name)
    matches_by_name[name] = matches
    print("SOURCE_NAME:", name)
    print("SOURCE_MATCH_COUNT:", len(matches))

    for path in matches:
        print(
            "SOURCE_MATCH:",
            json.dumps(
                {
                    "name": name,
                    "path": str(path),
                    "sha256": sha256_file(path),
                    "bytes": path.stat().st_size,
                },
                sort_keys=True,
            ),
        )

payload_matches = matches_by_name["g60_local_edges.csv"]
automorphism_matches = matches_by_name[
    "native_g60_full_automorphism_group_042.json"
]

print()
print("== G60 EDGE PAYLOAD PROFILE ==")

payload_profiles = []

for path in payload_matches:
    profile = csv_profile(path)
    payload_profiles.append((path, profile))
    print(
        "G60_EDGE_PROFILE:",
        json.dumps(
            {
                "path": str(path),
                **profile,
            },
            sort_keys=True,
        ),
    )

payload_has_60_vertex_candidate = any(
    profile["endpoint_candidates"]
    for _, profile in payload_profiles
)

print(
    "CHECK_G60_PAYLOAD_HAS_60_VERTEX_ENDPOINT_CANDIDATE:",
    str(payload_has_60_vertex_candidate).lower(),
)

print()
print("== AUTOMORPHISM AUTHORITY PROFILE ==")

automorphism_profiles = []

for path in automorphism_matches:
    profile = json_profile(path)
    automorphism_profiles.append((path, profile))
    print(
        "AUTOMORPHISM_PROFILE:",
        json.dumps(
            {
                "path": str(path),
                **profile,
            },
            sort_keys=True,
            default=str,
        ),
    )

print(
    "CHECK_AUTOMORPHISM_AUTHORITY_PRESENT:",
    str(bool(automorphism_matches)).lower(),
)

print()
print("== RELATED AUTHORITY PROFILES ==")

for name in EXACT_NAMES[2:]:
    for path in matches_by_name[name]:
        if path.suffix == ".json":
            print(
                "RELATED_PROFILE:",
                json.dumps(
                    {
                        "name": name,
                        "path": str(path),
                        **json_profile(path),
                    },
                    sort_keys=True,
                    default=str,
                ),
            )

print()
print("== STATUS PRESERVATION ==")

all_status_preserved = True

for root in ROOTS:
    if not root.exists():
        continue
    before = status_before.get(str(root), [])
    after = git_status(root)
    preserved = before == after
    all_status_preserved = all_status_preserved and preserved
    print(
        "STATUS_CHECK:",
        json.dumps(
            {
                "root": str(root),
                "before": before,
                "after": after,
                "preserved": preserved,
            },
            sort_keys=True,
        ),
    )

print(
    "CHECK_ALL_REPOSITORY_STATUS_PRESERVED:",
    str(all_status_preserved).lower(),
)

paper7_locked = (
    paper7_exists
    and paper7_verdict == EXPECTED_PAPER7_VERDICT
)
payload_locked = (
    len(payload_matches) >= 1
    and payload_has_60_vertex_candidate
)
automorphism_locked = len(automorphism_matches) >= 1

source_lock_pass = (
    paper7_locked
    and payload_locked
    and automorphism_locked
    and all_status_preserved
)

print()
print("== FINAL GATES ==")
print("CHECK_PAPER7_ALGEBRA_AUTHORITY_LOCKED:", str(paper7_locked).lower())
print("CHECK_G60_EDGE_AUTHORITY_LOCKED:", str(payload_locked).lower())
print("CHECK_G60_AUTOMORPHISM_AUTHORITY_LOCKED:", str(automorphism_locked).lower())
print("CHECK_SOURCE_LOCK_PASS:", str(source_lock_pass).lower())

if source_lock_pass:
    classification = "source_authorities_locked_for_native_G60_receipt_packet_encounter"
    next_gate = (
        "Parse the exact native G60 permutation action and enumerate "
        "semiregular subgroup conjugacy classes without assuming a receipt group."
    )
else:
    classification = "source_authority_lock_incomplete"
    next_gate = (
        "Resolve the missing Paper7, G60 edge, or G60 automorphism authority "
        "before enumerating native receipt actions."
    )

print()
print("FINAL_CLASSIFICATION:", classification)
print(
    "BOUNDARY:",
    "This packet locks candidate authorities only. It does not select a "
    "receipt group, quotient, projection, edge voltage, or orientation.",
)
print("NEXT_GATE:", next_gate)
print(
    "KEEPER:",
    "The packet is locked. G60 has not yet answered.",
)
print("MUTATION_PERFORMED: false")
