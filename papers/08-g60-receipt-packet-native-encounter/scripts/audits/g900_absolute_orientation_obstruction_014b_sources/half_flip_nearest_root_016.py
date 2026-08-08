#!/usr/bin/env python3

import hashlib
import json
import pathlib
import sys
from collections import Counter, deque

p08 = pathlib.Path(sys.argv[1]).resolve()
p41 = pathlib.Path(sys.argv[2]).resolve()
p42 = pathlib.Path(sys.argv[3]).resolve()
p45 = pathlib.Path(sys.argv[4]).resolve()

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

slot_path = (
    p45
    / "artifacts/json"
    / "g900_residual_involution_slot_maps_022.json"
)

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def all_distances(vertex_count, edges):
    adjacency = {
        vertex: []
        for vertex in range(vertex_count)
    }

    for left, right in edges:
        adjacency[int(left)].append(int(right))
        adjacency[int(right)].append(int(left))

    distances = []

    for source in range(vertex_count):
        row = [-1] * vertex_count
        row[source] = 0
        queue = deque([source])

        while queue:
            current = queue.popleft()

            for target in adjacency[current]:
                if row[target] == -1:
                    row[target] = row[current] + 1
                    queue.append(target)

        distances.append(row)

    return distances

layer = load_native_source_layer(p41)
source_checks = layer.validate()

action = json.loads(action_path.read_text(encoding="utf-8"))
bridge = json.loads(bridge_path.read_text(encoding="utf-8"))
slot_data = json.loads(slot_path.read_text(encoding="utf-8"))

permutations = {
    int(row["actual_index"]):
        tuple(int(value) for value in row["actual_permutation"])
    for row in action["mapping_rows"]
}

half_flip = tuple(int(value) for value in layer.half_flip)

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

inverse_root = {}

for left, right in inverse_pairs:
    inverse_root[left] = right
    inverse_root[right] = left

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

distances = all_distances(
    60,
    layer.g60_edges,
)

distance_failures = sum(
    value < 0
    for row in distances
    for value in row
)

state_rows = []

for state in range(60):
    half_target = half_flip[state]

    root_distances = {
        root: distances[
            permutations[root][state]
        ][
            half_target
        ]
        for root in roots
    }

    minimum = min(root_distances.values())

    minimizers = sorted(
        root
        for root, distance in root_distances.items()
        if distance == minimum
    )

    second_distance = min(
        (
            distance
            for root, distance in root_distances.items()
            if root not in minimizers
        ),
        default=None,
    )

    state_rows.append({
        "state": state,
        "half_target": half_target,
        "minimum_distance": minimum,
        "minimizers": minimizers,
        "minimizer_count": len(minimizers),
        "second_distance": second_distance,
        "gap": (
            None
            if second_distance is None
            else second_distance - minimum
        ),
        "root_distances": root_distances,
    })

minimum_distance_profile = dict(sorted(Counter(
    row["minimum_distance"]
    for row in state_rows
).items()))

minimizer_count_profile = dict(sorted(Counter(
    row["minimizer_count"]
    for row in state_rows
).items()))

gap_profile = dict(sorted(Counter(
    row["gap"]
    for row in state_rows
).items()))

unique_at_every_state = all(
    row["minimizer_count"] == 1
    for row in state_rows
)

unique_state_count = sum(
    row["minimizer_count"] == 1
    for row in state_rows
)

candidate_mapping = None
root_fiber_size_profile = {}
duad_fiber_size_profile = {}
inverse_direction_profile = {}

if unique_at_every_state:
    candidate_mapping = tuple(
        row["minimizers"][0]
        for row in state_rows
    )

    root_counts = Counter(candidate_mapping)
    duad_counts = Counter(
        str(root_to_duad[root])
        for root in candidate_mapping
    )

    root_fiber_size_profile = dict(sorted(Counter(
        root_counts.values()
    ).items()))

    duad_fiber_size_profile = dict(sorted(Counter(
        duad_counts.values()
    ).items()))

    inverse_direction_profile = dict(sorted(Counter(
        distances[
            permutations[
                inverse_root[candidate_mapping[state]]
            ][state]
        ][half_flip[state]]
        -
        distances[
            permutations[candidate_mapping[state]][state]
        ][half_flip[state]]
        for state in range(60)
    ).items()))

fixed_slots = sorted(
    int(row["slot"])
    for row in slot_data["slot_rows"]
    if row["target_slots"] == [int(row["slot"])]
)

slot_sign_profiles = {}

for slot in range(15):
    signs = []

    for row in layer.carrier_edges:
        if row.slot_u == slot or row.slot_v == slot:
            signs.append(int(row.sign))

    slot_sign_profiles[slot] = dict(sorted(Counter(signs).items()))

fixed_slot_sign_profiles = {
    slot: slot_sign_profiles[slot]
    for slot in fixed_slots
}

mixed_fixed_slots = [
    slot
    for slot in fixed_slots
    if slot_sign_profiles[slot] == {0: 2, 1: 2}
]

pure_identity_fixed_slots = [
    slot
    for slot in fixed_slots
    if slot_sign_profiles[slot] == {0: 4}
]

checks = {
    "source_layer_valid":
        all(source_checks.values()),
    "H60_order_480":
        len(permutations) == 480,
    "orientation_root_count_20":
        len(roots) == 20,
    "native_g60_connected":
        distance_failures == 0,
    "three_residual_fixed_slots":
        fixed_slots == [6, 12, 13],
    "slot_6_unique_mixed_fixed_hinge":
        mixed_fixed_slots == [6],
    "slots_12_13_pure_identity":
        pure_identity_fixed_slots == [12, 13],
}

failed = [
    name
    for name, passed in checks.items()
    if not passed
]

if unique_at_every_state:
    classification = (
        "unique_half_flip_nearest_orientation_root_"
        "at_every_local_state"
    )
elif unique_state_count == 0:
    classification = (
        "nearest_orientation_root_tied_at_every_local_state"
    )
else:
    classification = (
        "half_flip_nearest_root_rule_partially_unique"
    )

print("== G900 HALF-FLIP NEAREST-ROOT AUDIT 016 ==")
print("ACTION_SHA256:", sha256(action_path))
print("BRIDGE_SHA256:", sha256(bridge_path))
print("SLOT_MAP_SHA256:", sha256(slot_path))
print("SOURCE_LAYER_CHECKS:", source_checks)
print("FIXED_SLOTS:", fixed_slots)
print("FIXED_SLOT_SIGN_PROFILES:", fixed_slot_sign_profiles)
print("MIXED_FIXED_SLOTS:", mixed_fixed_slots)
print("PURE_IDENTITY_FIXED_SLOTS:", pure_identity_fixed_slots)
print("MINIMUM_DISTANCE_PROFILE:", minimum_distance_profile)
print("MINIMIZER_COUNT_PROFILE:", minimizer_count_profile)
print("GAP_PROFILE:", gap_profile)
print("UNIQUE_STATE_COUNT:", unique_state_count)
print("UNIQUE_ROOT_AT_EVERY_STATE:", unique_at_every_state)

print()
print("== NEAREST-ROOT STATE ROWS ==")

for row in state_rows:
    print(
        "STATE",
        row["state"],
        "HALF_TARGET",
        row["half_target"],
        "MIN_DISTANCE",
        row["minimum_distance"],
        "MINIMIZER_COUNT",
        row["minimizer_count"],
        "ROOTS",
        row["minimizers"],
        "SECOND_DISTANCE",
        row["second_distance"],
        "GAP",
        row["gap"],
    )

if candidate_mapping is not None:
    print()
    print("CANDIDATE_VERTEX_TO_ROOT_MAP:", list(candidate_mapping))
    print(
        "ROOT_FIBER_SIZE_PROFILE:",
        root_fiber_size_profile,
    )
    print(
        "DUAD_FIBER_SIZE_PROFILE:",
        duad_fiber_size_profile,
    )
    print(
        "INVERSE_ROOT_DISTANCE_MARGIN_PROFILE:",
        inverse_direction_profile,
    )

print()
print("CHECKS:", checks)
print("FAILED_CHECK_COUNT:", len(failed))
print("FAILED_CHECKS:", failed)
print("AUDIT_PASS:", not failed)
print("CLASSIFICATION:", classification)
print(
    "NEAREST_ROOT_MAP_PROVED:",
    unique_at_every_state,
)
print(
    "UNIQUE_FIXED_HINGE_PROVED:",
    mixed_fixed_slots == [6],
)
print("EPSILON_SELECTED: false")
print("ABSOLUTE_ORIENTATION_SELECTED: false")
print("PHYSICAL_CLAIM: false")
print("PROJECT_MUTATION_PERFORMED: false")

if failed:
    raise SystemExit(1)
