#!/usr/bin/env python3

import hashlib
import json
import pathlib
import sys
from collections import Counter

p08 = pathlib.Path(sys.argv[1]).resolve()
p42 = pathlib.Path(sys.argv[2]).resolve()

action_path = (
    p42
    / "artifacts/json"
    / "native_g60_fiber_product_isomorphism_044.json"
)

bridge_path = (
    p08
    / "artifacts/json"
    / "g60_duad_orientation_bridge_census_011g.v1.json"
)

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def compose(left, right):
    return tuple(
        left[right[index]]
        for index in range(len(left))
    )

def inverse(permutation):
    result = [-1] * len(permutation)

    for source, target in enumerate(permutation):
        if result[target] != -1:
            raise ValueError("permutation is not injective")
        result[target] = source

    if any(value < 0 for value in result):
        raise ValueError("permutation is not surjective")

    return tuple(result)

action = json.loads(action_path.read_text(encoding="utf-8"))
bridge = json.loads(bridge_path.read_text(encoding="utf-8"))

permutations = {
    int(row["actual_index"]):
        tuple(int(value) for value in row["actual_permutation"])
    for row in action["mapping_rows"]
}

indices = sorted(permutations)
degree = len(permutations[indices[0]])
identity_permutation = tuple(range(degree))

permutation_to_index = {
    permutation: index
    for index, permutation in permutations.items()
}

identity_indices = [
    index
    for index, permutation in permutations.items()
    if permutation == identity_permutation
]

inverse_indices = {}
inverse_failures = []

for index in indices:
    inverse_permutation = inverse(permutations[index])
    inverse_index = permutation_to_index.get(inverse_permutation)

    if inverse_index is None:
        inverse_failures.append(index)
    else:
        inverse_indices[index] = inverse_index

closure_failures = []

for left in indices:
    for right in indices:
        product = compose(
            permutations[left],
            permutations[right],
        )

        if product not in permutation_to_index:
            closure_failures.append([left, right])
            if len(closure_failures) >= 20:
                break

    if closure_failures:
        break

inverse_pairs = tuple(
    tuple(int(value) for value in pair)
    for pair in bridge[
        "A_sets"
    ][
        "inverse_root_pairs"
    ][
        "pairs"
    ]
)

roots = tuple(sorted({
    root
    for pair in inverse_pairs
    for root in pair
}))

root_to_duad = {}

for row in bridge[
    "equivariant_bridges"
][
    "unordered_to_inverse_pairs"
][
    "rows"
]:
    duad = tuple(int(value) for value in row["unordered_duad"])

    for root in row["inverse_pair"]:
        root_to_duad[int(root)] = duad

def conjugate_index(group_index, root_index):
    inverse_index = inverse_indices[group_index]

    conjugated = compose(
        permutations[group_index],
        compose(
            permutations[root_index],
            permutations[inverse_index],
        ),
    )

    return permutation_to_index.get(conjugated)

root_action_failures = []

for group_index in indices:
    for root in roots:
        image = conjugate_index(group_index, root)

        if image not in roots:
            root_action_failures.append({
                "group_index": group_index,
                "root": root,
                "image": image,
            })

            if len(root_action_failures) >= 20:
                break

    if root_action_failures:
        break

base_vertex = 0

vertex_stabilizer = tuple(
    index
    for index in indices
    if permutations[index][base_vertex] == base_vertex
)

vertex_orbit = sorted({
    permutations[index][base_vertex]
    for index in indices
})

root_orbit = sorted({
    conjugate_index(index, roots[0])
    for index in indices
})

root_stabilizer_orders = {
    root: sum(
        conjugate_index(index, root) == root
        for index in indices
    )
    for root in roots
}

fixed_roots = [
    root
    for root in roots
    if all(
        conjugate_index(index, root) == root
        for index in vertex_stabilizer
    )
]

candidate_maps = []
construction_conflicts = []

for base_root in fixed_roots:
    mapping = {}
    conflicts = []

    for group_index in indices:
        vertex = permutations[group_index][base_vertex]
        image_root = conjugate_index(group_index, base_root)

        if vertex in mapping and mapping[vertex] != image_root:
            conflicts.append({
                "group_index": group_index,
                "vertex": vertex,
                "existing_root": mapping[vertex],
                "new_root": image_root,
            })
        else:
            mapping[vertex] = image_root

    if conflicts:
        construction_conflicts.append({
            "base_root": base_root,
            "conflict_count": len(conflicts),
            "first_conflicts": conflicts[:10],
        })
        continue

    equivariance_failures = []

    for group_index in indices:
        for vertex in range(degree):
            left = mapping[
                permutations[group_index][vertex]
            ]
            right = conjugate_index(
                group_index,
                mapping[vertex],
            )

            if left != right:
                equivariance_failures.append({
                    "group_index": group_index,
                    "vertex": vertex,
                    "left": left,
                    "right": right,
                })

                if len(equivariance_failures) >= 10:
                    break

        if equivariance_failures:
            break

    root_fiber_profile = dict(sorted(Counter(
        mapping[vertex]
        for vertex in range(degree)
    ).items()))

    duad_fiber_profile = dict(sorted(Counter(
        str(root_to_duad[mapping[vertex]])
        for vertex in range(degree)
    ).items()))

    signature = tuple(
        mapping[vertex]
        for vertex in range(degree)
    )

    candidate_maps.append({
        "base_root": base_root,
        "mapping": signature,
        "image_size": len(set(signature)),
        "root_fiber_size_profile": dict(sorted(Counter(
            root_fiber_profile.values()
        ).items())),
        "duad_fiber_size_profile": dict(sorted(Counter(
            duad_fiber_profile.values()
        ).items())),
        "equivariance_failure_count":
            len(equivariance_failures),
        "first_equivariance_failures":
            equivariance_failures,
        "sha256": hashlib.sha256(
            ",".join(
                str(value)
                for value in signature
            ).encode("ascii")
        ).hexdigest(),
    })

valid_maps = [
    row
    for row in candidate_maps
    if row["equivariance_failure_count"] == 0
]

distinct_signatures = {
    row["mapping"]
    for row in valid_maps
}

checks = {
    "group_order_480":
        len(indices) == 480,
    "degree_60":
        degree == 60,
    "identity_unique":
        len(identity_indices) == 1,
    "inverse_closure":
        not inverse_failures,
    "multiplication_closure":
        not closure_failures,
    "root_count_20":
        len(roots) == 20,
    "root_indices_are_group_elements":
        all(root in permutations for root in roots),
    "root_action_closed":
        not root_action_failures,
    "vertex_action_transitive":
        len(vertex_orbit) == 60,
    "root_action_transitive":
        len(root_orbit) == 20,
    "vertex_stabilizer_order_8":
        len(vertex_stabilizer) == 8,
    "root_stabilizer_order_24":
        set(root_stabilizer_orders.values()) == {24},
    "candidate_construction_conflict_free":
        not construction_conflicts,
}

failed = [
    name
    for name, passed in checks.items()
    if not passed
]

if len(distinct_signatures) == 0:
    classification = (
        "no_H60_equivariant_vertex_to_orientation_root_map"
    )
elif len(distinct_signatures) == 1:
    classification = (
        "unique_H60_equivariant_three_to_one_"
        "vertex_to_orientation_root_map"
    )
else:
    classification = (
        "multiple_H60_equivariant_vertex_to_orientation_root_maps"
    )

print("== G60 VERTEX-TO-ORIENTATION-ROOT BRIDGE AUDIT 014 ==")
print("ACTION_PATH:", action_path)
print("ACTION_SHA256:", sha256(action_path))
print("BRIDGE_PATH:", bridge_path)
print("BRIDGE_SHA256:", sha256(bridge_path))
print("H60_ORDER:", len(indices))
print("PERMUTATION_DEGREE:", degree)
print("IDENTITY_INDICES:", identity_indices)
print("ORIENTATION_ROOT_COUNT:", len(roots))
print("ORIENTATION_ROOTS:", list(roots))
print("VERTEX_ORBIT_SIZE:", len(vertex_orbit))
print("ROOT_ORBIT_SIZE:", len(root_orbit))
print("BASE_VERTEX:", base_vertex)
print("VERTEX_STABILIZER_ORDER:", len(vertex_stabilizer))
print(
    "ROOT_STABILIZER_ORDER_PROFILE:",
    dict(sorted(Counter(
        root_stabilizer_orders.values()
    ).items())),
)
print(
    "VERTEX_STABILIZER_FIXED_ROOT_COUNT:",
    len(fixed_roots),
)
print(
    "VERTEX_STABILIZER_FIXED_ROOTS:",
    fixed_roots,
)
print(
    "CONSTRUCTION_CONFLICT_COUNT:",
    len(construction_conflicts),
)
print(
    "VALID_EQUIVARIANT_MAP_COUNT:",
    len(valid_maps),
)
print(
    "DISTINCT_EQUIVARIANT_MAP_COUNT:",
    len(distinct_signatures),
)

for map_index, row in enumerate(valid_maps):
    print()
    print("MAP_INDEX:", map_index)
    print("BASE_ROOT:", row["base_root"])
    print("MAP_SHA256:", row["sha256"])
    print("IMAGE_SIZE:", row["image_size"])
    print(
        "ROOT_FIBER_SIZE_PROFILE:",
        row["root_fiber_size_profile"],
    )
    print(
        "DUAD_FIBER_SIZE_PROFILE:",
        row["duad_fiber_size_profile"],
    )
    print(
        "VERTEX_TO_ROOT_MAP:",
        list(row["mapping"]),
    )

print()
print("CHECKS:", checks)
print("FAILED_CHECK_COUNT:", len(failed))
print("FAILED_CHECKS:", failed)
print("AUDIT_PASS:", not failed)
print("CLASSIFICATION:", classification)
print(
    "VERTEX_ROOT_CROSSWALK_PROVED:",
    len(distinct_signatures) == 1,
)
print("EPSILON_CROSSWALK_PROVED: false")
print("ABSOLUTE_ORIENTATION_SELECTED: false")
print("PHYSICAL_CLAIM: false")
print("PROJECT_MUTATION_PERFORMED: false")

if failed:
    raise SystemExit(1)
