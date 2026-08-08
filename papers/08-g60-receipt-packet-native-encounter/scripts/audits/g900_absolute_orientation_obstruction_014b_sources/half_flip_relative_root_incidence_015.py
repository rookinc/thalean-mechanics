#!/usr/bin/env python3

import hashlib
import json
import pathlib
import sys
from collections import Counter

p08 = pathlib.Path(sys.argv[1]).resolve()
p41 = pathlib.Path(sys.argv[2]).resolve()
p42 = pathlib.Path(sys.argv[3]).resolve()

sys.path.insert(0, str(p41))

from scripts.lib.project41_native import load_native_source_layer

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

def invert(permutation):
    inverse = [-1] * len(permutation)

    for source, target in enumerate(permutation):
        if inverse[target] != -1:
            raise ValueError("not injective")
        inverse[target] = source

    if any(value < 0 for value in inverse):
        raise ValueError("not surjective")

    return tuple(inverse)

def edge(left, right):
    return tuple(sorted((int(left), int(right))))

layer = load_native_source_layer(p41)
source_checks = layer.validate()

action = json.loads(action_path.read_text(encoding="utf-8"))
bridge = json.loads(bridge_path.read_text(encoding="utf-8"))

permutations = {
    int(row["actual_index"]):
        tuple(int(value) for value in row["actual_permutation"])
    for row in action["mapping_rows"]
}

indices = sorted(permutations)
permutation_to_index = {
    permutation: index
    for index, permutation in permutations.items()
}

inverse_indices = {
    index: permutation_to_index[invert(permutation)]
    for index, permutation in permutations.items()
}

half_flip = tuple(int(value) for value in layer.half_flip)
identity = tuple(range(60))

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
    conjugated = compose(
        permutations[group_index],
        compose(
            permutations[root_index],
            permutations[inverse_indices[group_index]],
        ),
    )
    return permutation_to_index.get(conjugated)

half_flip_order_two = (
    compose(half_flip, half_flip) == identity
)

half_flip_fixed_points = [
    state
    for state, target in enumerate(half_flip)
    if state == target
]

local_edges = {
    edge(left, right)
    for left, right in layer.g60_edges
}

half_flip_edge_image = {
    edge(half_flip[left], half_flip[right])
    for left, right in local_edges
}

half_flip_preserves_local_graph = (
    half_flip_edge_image == local_edges
)

centralizer = [
    index
    for index in indices
    if compose(permutations[index], half_flip)
       == compose(half_flip, permutations[index])
]

state_rows = []
root_agreement_states = {
    root: []
    for root in roots
}

for state in range(60):
    half_target = half_flip[state]

    matching_roots = [
        root
        for root in roots
        if permutations[root][state] == half_target
    ]

    for root in matching_roots:
        root_agreement_states[root].append(state)

    state_rows.append({
        "state": state,
        "half_target": half_target,
        "matching_roots": matching_roots,
        "match_count": len(matching_roots),
    })

state_match_profile = dict(sorted(Counter(
    row["match_count"]
    for row in state_rows
).items()))

unique_at_every_state = all(
    row["match_count"] == 1
    for row in state_rows
)

candidate_mapping = None
root_fiber_profile = {}
duad_fiber_profile = {}
centralizer_covariance_failures = []

if unique_at_every_state:
    candidate_mapping = tuple(
        row["matching_roots"][0]
        for row in state_rows
    )

    root_fiber_profile = dict(sorted(Counter(
        candidate_mapping
    ).items()))

    duad_fiber_profile = dict(sorted(Counter(
        str(root_to_duad[root])
        for root in candidate_mapping
    ).items()))

    for group_index in centralizer:
        for state in range(60):
            left = candidate_mapping[
                permutations[group_index][state]
            ]

            right = conjugate_index(
                group_index,
                candidate_mapping[state],
            )

            if left != right:
                centralizer_covariance_failures.append({
                    "group_index": group_index,
                    "state": state,
                    "left": left,
                    "right": right,
                })

                if len(centralizer_covariance_failures) >= 20:
                    break

        if centralizer_covariance_failures:
            break

root_agreement_profile = dict(sorted(Counter(
    len(states)
    for states in root_agreement_states.values()
).items()))

fixed_slots = {6, 12, 13}
fixed_slot_carrier_rows = []

for row in layer.carrier_edges:
    if row.slot_u in fixed_slots or row.slot_v in fixed_slots:
        fixed_slot_carrier_rows.append({
            "slot_u": int(row.slot_u),
            "slot_v": int(row.slot_v),
            "sign": int(row.sign),
        })

fixed_slot_sign_profiles = {}

for slot in sorted(fixed_slots):
    signs = []

    for row in layer.carrier_edges:
        if row.slot_u == slot or row.slot_v == slot:
            signs.append(int(row.sign))

    fixed_slot_sign_profiles[slot] = dict(sorted(Counter(
        signs
    ).items()))

checks = {
    "source_layer_valid":
        all(source_checks.values()),
    "H60_order_480":
        len(indices) == 480,
    "orientation_root_count_20":
        len(roots) == 20,
    "half_flip_is_permutation":
        sorted(half_flip) == list(range(60)),
    "half_flip_order_two":
        half_flip_order_two,
    "half_flip_fixed_point_free":
        len(half_flip_fixed_points) == 0,
    "root_action_closed":
        all(
            conjugate_index(group_index, root) in roots
            for group_index in indices
            for root in roots
        ),
}

failed = [
    name
    for name, passed in checks.items()
    if not passed
]

if unique_at_every_state and not centralizer_covariance_failures:
    classification = (
        "half_flip_selects_unique_orientation_root_"
        "at_every_local_state"
    )
elif state_match_profile == {0: 60}:
    classification = (
        "half_flip_has_no_pointwise_orientation_root_agreement"
    )
else:
    classification = (
        "half_flip_relative_root_incidence_nonfunctional"
    )

print("== G900 HALF-FLIP-RELATIVE ROOT INCIDENCE AUDIT 015 ==")
print("ACTION_SHA256:", sha256(action_path))
print("BRIDGE_SHA256:", sha256(bridge_path))
print("SOURCE_LAYER_CHECKS:", source_checks)
print("H60_ORDER:", len(indices))
print("ORIENTATION_ROOT_COUNT:", len(roots))
print("HALF_FLIP_IN_H60:", half_flip in permutation_to_index)
print("HALF_FLIP_ORDER_TWO:", half_flip_order_two)
print("HALF_FLIP_FIXED_POINT_COUNT:", len(half_flip_fixed_points))
print(
    "HALF_FLIP_PRESERVES_LOCAL_G60_GRAPH:",
    half_flip_preserves_local_graph,
)
print("H60_HALF_FLIP_CENTRALIZER_ORDER:", len(centralizer))
print("STATE_MATCH_COUNT_PROFILE:", state_match_profile)
print("ROOT_AGREEMENT_SIZE_PROFILE:", root_agreement_profile)
print(
    "TOTAL_ROOT_STATE_AGREEMENTS:",
    sum(len(states) for states in root_agreement_states.values()),
)
print("UNIQUE_ROOT_AT_EVERY_STATE:", unique_at_every_state)

print()
print("== ROOT AGREEMENT STATES ==")

for root in roots:
    print(
        "ROOT",
        root,
        "DUAD",
        list(root_to_duad[root]),
        "AGREEMENT_COUNT",
        len(root_agreement_states[root]),
        "STATES",
        root_agreement_states[root],
    )

print()
print("== STATE INCIDENCE ROWS ==")

for row in state_rows:
    print(
        "STATE",
        row["state"],
        "HALF_TARGET",
        row["half_target"],
        "MATCH_COUNT",
        row["match_count"],
        "ROOTS",
        row["matching_roots"],
    )

if candidate_mapping is not None:
    print()
    print("CANDIDATE_VERTEX_TO_ROOT_MAP:", list(candidate_mapping))
    print(
        "ROOT_FIBER_SIZE_PROFILE:",
        dict(sorted(Counter(
            root_fiber_profile.values()
        ).items())),
    )
    print(
        "DUAD_FIBER_SIZE_PROFILE:",
        dict(sorted(Counter(
            duad_fiber_profile.values()
        ).items())),
    )
    print(
        "CENTRALIZER_COVARIANCE_FAILURE_COUNT:",
        len(centralizer_covariance_failures),
    )
    print(
        "CENTRALIZER_COVARIANCE_FAILURES:",
        centralizer_covariance_failures,
    )

print()
print("== FIXED-SLOT CARRIER DATA ==")
print("FIXED_SLOT_SIGN_PROFILES:", fixed_slot_sign_profiles)

for row in sorted(
    fixed_slot_carrier_rows,
    key=lambda item: (
        item["slot_u"],
        item["slot_v"],
        item["sign"],
    ),
):
    print(
        "CARRIER",
        row["slot_u"],
        row["slot_v"],
        "SIGN",
        row["sign"],
    )

print()
print("CHECKS:", checks)
print("FAILED_CHECK_COUNT:", len(failed))
print("FAILED_CHECKS:", failed)
print("AUDIT_PASS:", not failed)
print("CLASSIFICATION:", classification)
print(
    "CARRIER_RELATIVE_ROOT_MAP_PROVED:",
    unique_at_every_state
    and not centralizer_covariance_failures,
)
print("EPSILON_SELECTED: false")
print("ABSOLUTE_ORIENTATION_SELECTED: false")
print("PHYSICAL_CLAIM: false")
print("PROJECT_MUTATION_PERFORMED: false")

if failed:
    raise SystemExit(1)
