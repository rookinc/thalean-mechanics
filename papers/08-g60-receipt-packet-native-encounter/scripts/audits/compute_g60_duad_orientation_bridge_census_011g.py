import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

project = Path(sys.argv[1]).resolve()
candidate_path = Path(sys.argv[2]).resolve()

action_path = Path("/data/data/com.termux/files/home/dev/cori/research/mathematics/42-graph-automorphism-groups/artifacts/json/native_g60_fiber_product_isomorphism_044.json")
partition_path = Path("/data/data/com.termux/files/home/dev/cori/research/mathematics/42-graph-automorphism-groups/artifacts/json/native_g60_five_petersen_matching_partition_theorem_077.json")
equivariance_path = Path("/data/data/com.termux/files/home/dev/cori/research/mathematics/42-graph-automorphism-groups/artifacts/json/native_g60_five_petersen_matching_equivariance_audit_078.json")
splitting_path = Path("/data/data/com.termux/files/home/dev/cori/research/mathematics/42-graph-automorphism-groups/artifacts/json/native_g60_s5_extension_splitting_audit_079.json")
roots_path = project / "artifacts/json/g60_native_orientation_root_reversal_census_011e.v1.json"
prereg_path = project / "artifacts/json/g60_duad_orientation_bridge_preregistration_011f.v1.json"

expected_hashes = {
    str(action_path): "b37313b135495752b11e525bb61979163fdf54aec4be4f5d027dcee64c9efc21",
    str(partition_path): "7db5162f2dbd9d53b44e8a9716f097394e5a75040951eceb8ec1e6ddbbb372b0",
    str(equivariance_path): "db01304b44015a25e8f207d3fe869ad96ebcd82d3d2bd7017908a9ed7c843ec7",
    str(splitting_path): "728071622f7a6a98042a8dd4d1a6fa01cdcc8a456bd2bd5b5aadcf22965f5221",
    str(roots_path): "15ef444f6ed6bfbf0dc2611985edeffd0c38ec41142dfeb2f9ca53ef32813623",
    str(prereg_path): "af7eda5bad497faf6f68d5225bce35c0f8184a577853d2b50ea055af4356aa37",
}

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def git(*args):
    return subprocess.run(
        ["git", *args],
        cwd=project,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    ).stdout.strip()

actual_hashes = {path: sha256(Path(path)) for path in expected_hashes}
hash_matches = {
    path: actual_hashes[path] == expected_hashes[path]
    for path in expected_hashes
}
all_hashes_match = all(hash_matches.values())

head = git("--no-pager", "show", "-s", "--format=%h %s", "HEAD")
status_before = git("status", "--short", "--", ".")

action_data = json.loads(action_path.read_text(encoding="utf-8"))
equivariance = json.loads(equivariance_path.read_text(encoding="utf-8"))
roots_data = json.loads(roots_path.read_text(encoding="utf-8"))
prereg = json.loads(prereg_path.read_text(encoding="utf-8"))

mapping_rows = action_data["mapping_rows"]
permutations = {}
declared_orders = {}
for row in mapping_rows:
    index = int(row["actual_index"])
    permutations[index] = tuple(int(x) for x in row["actual_permutation"])
    declared_orders[index] = int(row["actual_order"])

indices = sorted(permutations)
degree = len(permutations[indices[0]])
identity_perm = tuple(range(degree))
identity_candidates = [
    index for index in indices if permutations[index] == identity_perm
]
identity = identity_candidates[0] if len(identity_candidates) == 1 else None

perm_to_index = {perm: index for index, perm in permutations.items()}
dictionary_ok = len(perm_to_index) == len(indices) == 480

def compose(p, q):
    return tuple(p[q[v]] for v in range(degree))

print("== G60 DUAD ORIENTATION BRIDGE CENSUS 011g ==")
print("MODE: temporary read-only complete finite action census")
print("LOCKED_HEAD:", head)
print("ALL_AUTHORITY_HASHES_MATCH:", str(all_hashes_match).lower())
print("GROUP_ORDER:", len(indices))
print("IDENTITY_INDEX:", identity)
print()
print("MULTIPLICATION_BEGIN")

multiplication = [[None] * 480 for _ in range(480)]
closure_failures = []
for row_number, g in enumerate(indices):
    if row_number % 40 == 0:
        print("MULTIPLICATION_PROGRESS:", row_number, "/", len(indices))
    pg = permutations[g]
    for h in indices:
        product_perm = compose(pg, permutations[h])
        product = perm_to_index.get(product_perm)
        if product is None:
            closure_failures.append([g, h])
        else:
            multiplication[g][h] = product
print("MULTIPLICATION_PROGRESS:", len(indices), "/", len(indices))
print("MULTIPLICATION_END")

inverse = {}
inverse_failures = []
if identity is not None:
    for g in indices:
        candidates = [
            h for h in indices
            if multiplication[g][h] == identity
            and multiplication[h][g] == identity
        ]
        if len(candidates) == 1:
            inverse[g] = candidates[0]
        else:
            inverse_failures.append([g, candidates])

operation_ok = (
    all_hashes_match
    and dictionary_ok
    and identity is not None
    and not closure_failures
    and not inverse_failures
)

block_rows = {
    int(row["actual_index"]): tuple(int(x) for x in row["block_image"])
    for row in equivariance["action_rows"]
}
block_row_failure_count = len(set(indices) - set(block_rows))

block_action_consistency_failures = []
if operation_ok and not block_row_failure_count:
    for g in indices:
        for h in indices:
            gh = multiplication[g][h]
            expected = tuple(block_rows[g][block_rows[h][i]] for i in range(5))
            if block_rows[gh] != expected:
                block_action_consistency_failures.append([g, h])
                if len(block_action_consistency_failures) >= 20:
                    break
        if len(block_action_consistency_failures) >= 20:
            break

blocks = tuple(range(5))
ordered_duads = tuple((i, j) for i in blocks for j in blocks if i != j)
unordered_duads = tuple(
    (i, j) for i in blocks for j in blocks if i < j
)

root_indices = tuple(
    int(x) for x in roots_data["orientation_root_set"]["root_indices"]
)
tau = int(roots_data["orientation_root_set"]["tau_index"])

def act_ordered(g, pair):
    i, j = pair
    return (block_rows[g][i], block_rows[g][j])

def act_unordered(g, pair):
    i, j = pair
    return tuple(sorted((block_rows[g][i], block_rows[g][j])))

def conjugate(g, c):
    return multiplication[multiplication[g][c]][inverse[g]]

root_action = {}
root_action_failures = []
if operation_ok:
    root_set = set(root_indices)
    for g in indices:
        for c in root_indices:
            image = conjugate(g, c)
            root_action[(g, c)] = image
            if image not in root_set:
                root_action_failures.append([g, c, image])

inverse_pairs = tuple(sorted({
    tuple(sorted((c, inverse[c]))) for c in root_indices
}))

def act_root(g, c):
    return root_action[(g, c)]

def act_root_pair(g, pair):
    return tuple(sorted((act_root(g, pair[0]), act_root(g, pair[1]))))

def pointwise_kernel(objects, action):
    return [
        g for g in indices
        if all(action(g, obj) == obj for obj in objects)
    ]

def orbit(start, action):
    return {action(g, start) for g in indices}

def enumerate_equivariant_bijections(source, target, source_action, target_action):
    base = source[0]
    stabilizer = [g for g in indices if source_action(g, base) == base]
    fixed_targets = [
        y for y in target
        if all(target_action(g, y) == y for g in stabilizer)
    ]

    valid_maps = []
    rejected = []

    for y0 in fixed_targets:
        mapping = {}
        well_defined = True

        for x in source:
            images = {
                target_action(g, y0)
                for g in indices
                if source_action(g, base) == x
            }
            if len(images) != 1:
                rejected.append({
                    "base_target": y0,
                    "source": x,
                    "image_count": len(images),
                })
                well_defined = False
                break
            mapping[x] = next(iter(images))

        if not well_defined:
            continue
        if len(set(mapping.values())) != len(target):
            rejected.append({
                "base_target": y0,
                "reason": "not_bijective",
            })
            continue

        equivariance_failures = 0
        for g in indices:
            for x in source:
                if mapping[source_action(g, x)] != target_action(g, mapping[x]):
                    equivariance_failures += 1
                    break
            if equivariance_failures:
                break

        if equivariance_failures == 0:
            valid_maps.append({
                "base_source": base,
                "base_target": y0,
                "mapping": mapping,
            })

    return {
        "base": base,
        "stabilizer": stabilizer,
        "fixed_targets": fixed_targets,
        "valid_maps": valid_maps,
        "rejected": rejected,
    }

ordered_kernel = pointwise_kernel(ordered_duads, act_ordered)
unordered_kernel = pointwise_kernel(unordered_duads, act_unordered)
root_kernel = pointwise_kernel(root_indices, act_root)
pair_kernel = pointwise_kernel(inverse_pairs, act_root_pair)

ordered_orbit_count = len({
    tuple(sorted(orbit(x, act_ordered))) for x in ordered_duads
})
unordered_orbit_count = len({
    tuple(sorted(orbit(x, act_unordered))) for x in unordered_duads
})
root_orbit_count = len({
    tuple(sorted(orbit(x, act_root))) for x in root_indices
})
pair_orbit_count = len({
    tuple(sorted(orbit(x, act_root_pair))) for x in inverse_pairs
})

print()
print("EQUIVARIANT_ENUMERATION_BEGIN")
ordered_result = enumerate_equivariant_bijections(
    ordered_duads, root_indices, act_ordered, act_root
)
print("ORDERED_ENUMERATION_COMPLETE")
unordered_result = enumerate_equivariant_bijections(
    unordered_duads, inverse_pairs, act_unordered, act_root_pair
)
print("UNORDERED_ENUMERATION_COMPLETE")
print("EQUIVARIANT_ENUMERATION_END")

v4_root_action_rows = []
for k in ordered_kernel:
    fixed_count = 0
    inverse_count = 0
    other_count = 0
    for c in root_indices:
        image = act_root(k, c)
        if image == c:
            fixed_count += 1
        elif image == inverse[c]:
            inverse_count += 1
        else:
            other_count += 1
    v4_root_action_rows.append({
        "element_index": k,
        "fixed_root_count": fixed_count,
        "inverse_root_count": inverse_count,
        "other_root_count": other_count,
    })

inversion_equivariance_failures = []
for g in indices:
    for c in root_indices:
        if act_root(g, inverse[c]) != inverse[act_root(g, c)]:
            inversion_equivariance_failures.append([g, c])
            if len(inversion_equivariance_failures) >= 20:
                break
    if len(inversion_equivariance_failures) >= 20:
        break

duad_reversal_equivariance_failures = []
for g in indices:
    for pair in ordered_duads:
        reverse = (pair[1], pair[0])
        acted = act_ordered(g, pair)
        acted_reverse = (acted[1], acted[0])
        if act_ordered(g, reverse) != acted_reverse:
            duad_reversal_equivariance_failures.append([g, list(pair)])
            if len(duad_reversal_equivariance_failures) >= 20:
                break
    if len(duad_reversal_equivariance_failures) >= 20:
        break

kernel_obstruction_verified = (
    len(ordered_kernel) == 4
    and ordered_kernel == unordered_kernel
    and pair_kernel == ordered_kernel
    and len(root_kernel) < len(ordered_kernel)
    and any(
        row["inverse_root_count"] == 20
        for row in v4_root_action_rows
    )
    and all(
        row["other_root_count"] == 0
        for row in v4_root_action_rows
    )
)

ordered_bridge_count = len(ordered_result["valid_maps"])
unordered_bridge_count = len(unordered_result["valid_maps"])

authority_failure = (
    not all_hashes_match
    or head != "b0353ef Preregister G60 duad orientation bridge test"
    or prereg["preregistration_status"] != "frozen_before_duad_root_action_computation"
    or len(indices) != 480
    or identity != 0
    or block_row_failure_count != 0
    or block_action_consistency_failures
    or len(ordered_duads) != 20
    or len(unordered_duads) != 10
    or len(root_indices) != 20
    or len(inverse_pairs) != 10
)

computation_failure = (
    not operation_ok
    or root_action_failures
    or inversion_equivariance_failures
    or duad_reversal_equivariance_failures
)

if computation_failure:
    classification = "computation_failure"
elif authority_failure:
    classification = "authority_failure"
elif ordered_bridge_count > 0:
    classification = "oriented_bridge_exists"
elif unordered_bridge_count == 0:
    classification = "no_equivariant_unordered_bridge"
elif unordered_bridge_count == 1 and kernel_obstruction_verified:
    classification = "unique_unordered_bridge_with_oriented_kernel_obstruction"
elif unordered_bridge_count > 1 and kernel_obstruction_verified:
    classification = "multiple_unordered_bridges_with_oriented_kernel_obstruction"
else:
    classification = "unordered_bridge_without_verified_kernel_obstruction"

def map_rows(result, source_kind, target_kind):
    rows = []
    for map_index, entry in enumerate(result["valid_maps"]):
        for source in sorted(entry["mapping"]):
            target = entry["mapping"][source]
            rows.append({
                "map_index": map_index,
                source_kind: list(source) if isinstance(source, tuple) else source,
                target_kind: list(target) if isinstance(target, tuple) else target,
            })
    return rows

status_after = git("status", "--short", "--", ".")
repository_preserved = status_after == status_before

result = {
    "packet": "g60_duad_orientation_bridge_census_011g_candidate",
    "mode": "temporary_read_only_complete_finite_action_census",
    "locked_head": head,
    "authorities": {
        path: {
            "expected_sha256": expected_hashes[path],
            "sha256": actual_hashes[path],
            "hash_match": hash_matches[path],
        }
        for path in expected_hashes
    },
    "group_reconstruction": {
        "group_order": len(indices),
        "identity_index": identity,
        "permutation_dictionary_size": len(perm_to_index),
        "closure_failure_count": len(closure_failures),
        "inverse_failure_count": len(inverse_failures),
        "operation_ok": operation_ok,
        "block_action_consistency_failure_count": len(block_action_consistency_failures),
        "root_action_failure_count": len(root_action_failures),
    },
    "A_sets": {
        "ordered_duads": {
            "count": len(ordered_duads),
            "orbit_count": ordered_orbit_count,
            "pointwise_kernel_order": len(ordered_kernel),
            "pointwise_kernel_indices": ordered_kernel,
        },
        "unordered_duads": {
            "count": len(unordered_duads),
            "orbit_count": unordered_orbit_count,
            "pointwise_kernel_order": len(unordered_kernel),
            "pointwise_kernel_indices": unordered_kernel,
        },
        "orientation_roots": {
            "count": len(root_indices),
            "orbit_count": root_orbit_count,
            "pointwise_kernel_order": len(root_kernel),
            "pointwise_kernel_indices": root_kernel,
        },
        "inverse_root_pairs": {
            "count": len(inverse_pairs),
            "pairs": [list(pair) for pair in inverse_pairs],
            "orbit_count": pair_orbit_count,
            "pointwise_kernel_order": len(pair_kernel),
            "pointwise_kernel_indices": pair_kernel,
        },
    },
    "kernel_action": {
        "native_v4_indices_derived_as_duad_kernel": ordered_kernel,
        "root_action_rows": v4_root_action_rows,
        "kernel_obstruction_verified": kernel_obstruction_verified,
        "inversion_equivariance_failure_count": len(inversion_equivariance_failures),
        "duad_reversal_equivariance_failure_count": len(duad_reversal_equivariance_failures),
    },
    "equivariant_bridges": {
        "ordered_to_roots": {
            "source_stabilizer_order": len(ordered_result["stabilizer"]),
            "fixed_target_candidate_count": len(ordered_result["fixed_targets"]),
            "bridge_count": ordered_bridge_count,
            "rows": map_rows(ordered_result, "ordered_duad", "root_index"),
        },
        "unordered_to_inverse_pairs": {
            "source_stabilizer_order": len(unordered_result["stabilizer"]),
            "fixed_target_candidate_count": len(unordered_result["fixed_targets"]),
            "bridge_count": unordered_bridge_count,
            "rows": map_rows(unordered_result, "unordered_duad", "inverse_pair"),
        },
    },
    "classification": classification,
    "prediction": {
        "predicted_ordered_bridge_count": 0,
        "actual_ordered_bridge_count": ordered_bridge_count,
        "predicted_unordered_bridge_count": 1,
        "actual_unordered_bridge_count": unordered_bridge_count,
        "prediction_matches": (
            ordered_bridge_count == 0 and unordered_bridge_count == 1
        ),
    },
    "boundary": {
        "orientation_selected": False,
        "minimal_directional_datum_identified": False,
        "larger_carrier_constructed": False,
        "replacement_selector_used": False,
        "manuscript_mutated": False,
        "geometry_claim": False,
        "physical_claim": False,
    },
    "repository": {
        "status_before": status_before.splitlines(),
        "status_after": status_after.splitlines(),
        "status_preserved": repository_preserved,
        "project_mutation_performed": False,
    },
}

candidate_path.parent.mkdir(parents=True, exist_ok=True)
candidate_path.write_text(
    json.dumps(result, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

print()
print("== FINAL DUAD ORIENTATION BRIDGE REPORT ==")
print("OPERATION_OK:", str(operation_ok).lower())
print("CLOSURE_FAILURE_COUNT:", len(closure_failures))
print("INVERSE_FAILURE_COUNT:", len(inverse_failures))
print("BLOCK_ACTION_CONSISTENCY_FAILURE_COUNT:", len(block_action_consistency_failures))
print("ROOT_ACTION_FAILURE_COUNT:", len(root_action_failures))
print("ORDERED_DUAD_ORBIT_COUNT:", ordered_orbit_count)
print("UNORDERED_DUAD_ORBIT_COUNT:", unordered_orbit_count)
print("ROOT_ORBIT_COUNT:", root_orbit_count)
print("INVERSE_PAIR_ORBIT_COUNT:", pair_orbit_count)
print("ORDERED_DUAD_KERNEL_INDICES:", ordered_kernel)
print("UNORDERED_DUAD_KERNEL_INDICES:", unordered_kernel)
print("ROOT_KERNEL_INDICES:", root_kernel)
print("INVERSE_PAIR_KERNEL_INDICES:", pair_kernel)
print("NATIVE_V4_ROOT_ACTION_ROWS:", v4_root_action_rows)
print("KERNEL_OBSTRUCTION_VERIFIED:", str(kernel_obstruction_verified).lower())
print("ORDERED_SOURCE_STABILIZER_ORDER:", len(ordered_result["stabilizer"]))
print("ORDERED_FIXED_TARGET_CANDIDATE_COUNT:", len(ordered_result["fixed_targets"]))
print("ORDERED_BRIDGE_COUNT:", ordered_bridge_count)
print("UNORDERED_SOURCE_STABILIZER_ORDER:", len(unordered_result["stabilizer"]))
print("UNORDERED_FIXED_TARGET_CANDIDATE_COUNT:", len(unordered_result["fixed_targets"]))
print("UNORDERED_BRIDGE_COUNT:", unordered_bridge_count)
for row in map_rows(unordered_result, "unordered_duad", "inverse_pair"):
    print("UNORDERED_BRIDGE_ROW:", row)
print("INVERSION_EQUIVARIANCE_FAILURE_COUNT:", len(inversion_equivariance_failures))
print("DUAD_REVERSAL_EQUIVARIANCE_FAILURE_COUNT:", len(duad_reversal_equivariance_failures))
print("PREDICTION_MATCHES:", str(result["prediction"]["prediction_matches"]).lower())
print("CLASSIFICATION:", classification)
print("REPOSITORY_STATUS_PRESERVED:", str(repository_preserved).lower())
print("PROJECT_MUTATION_PERFORMED: false")
print("ORIENTATION_SELECTED: false")
print("MINIMAL_DIRECTIONAL_DATUM_IDENTIFIED: false")
print("MANUSCRIPT_MUTATED: false")
print("PHYSICAL_CLAIM: false")
print("CANDIDATE_JSON:", candidate_path)
print("CANDIDATE_JSON_SHA256:", sha256(candidate_path))
