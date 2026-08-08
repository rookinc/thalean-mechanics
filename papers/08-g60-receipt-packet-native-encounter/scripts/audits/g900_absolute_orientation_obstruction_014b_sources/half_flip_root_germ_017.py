#!/usr/bin/env python3

import hashlib
import json
import pathlib
import sys
from collections import Counter, deque

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

def graph_data(vertex_count, edges):
    adjacency = {
        vertex: set()
        for vertex in range(vertex_count)
    }

    for left, right in edges:
        left = int(left)
        right = int(right)
        adjacency[left].add(right)
        adjacency[right].add(left)

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

    return adjacency, distances

layer = load_native_source_layer(p41)
source_checks = layer.validate()

action = json.loads(action_path.read_text(encoding="utf-8"))
bridge = json.loads(bridge_path.read_text(encoding="utf-8"))

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

adjacency, distances = graph_data(
    60,
    layer.g60_edges,
)

diameter = max(
    max(row)
    for row in distances
)

def ball(center, radius):
    return tuple(
        vertex
        for vertex in range(60)
        if distances[center][vertex] <= radius
    )

def energy(state, root, radius):
    return sum(
        distances[
            permutations[root][vertex]
        ][
            half_flip[vertex]
        ]
        for vertex in ball(state, radius)
    )

radius_rows = {}

for radius in range(diameter + 1):
    rows = []

    for state in range(60):
        energies = {
            root: energy(state, root, radius)
            for root in roots
        }

        minimum = min(energies.values())

        minimizers = sorted(
            root
            for root, value in energies.items()
            if value == minimum
        )

        second = min(
            (
                value
                for root, value in energies.items()
                if root not in minimizers
            ),
            default=None,
        )

        rows.append({
            "state": state,
            "ball_size": len(ball(state, radius)),
            "minimum_energy": minimum,
            "minimizers": minimizers,
            "minimizer_count": len(minimizers),
            "second_energy": second,
            "gap": (
                None
                if second is None
                else second - minimum
            ),
        })

    radius_rows[radius] = rows

radius_profiles = {}

for radius, rows in radius_rows.items():
    radius_profiles[radius] = {
        "ball_size_profile": dict(sorted(Counter(
            row["ball_size"]
            for row in rows
        ).items())),
        "minimum_energy_profile": dict(sorted(Counter(
            row["minimum_energy"]
            for row in rows
        ).items())),
        "minimizer_count_profile": dict(sorted(Counter(
            row["minimizer_count"]
            for row in rows
        ).items())),
        "gap_profile": dict(sorted(Counter(
            row["gap"]
            for row in rows
        ).items())),
        "unique_state_count": sum(
            row["minimizer_count"] == 1
            for row in rows
        ),
    }

radius_zero = radius_rows[0]
radius_one = radius_rows[1]

radius_zero_by_state = {
    row["state"]: row
    for row in radius_zero
}

half_orbit_rows = []
seen = set()
inversion_covariance_failures = []

for state in range(60):
    if state in seen:
        continue

    partner = half_flip[state]
    seen.add(state)
    seen.add(partner)

    left_roots = set(
        radius_zero_by_state[state]["minimizers"]
    )

    right_roots = set(
        radius_zero_by_state[partner]["minimizers"]
    )

    expected_right = {
        inverse_root[root]
        for root in left_roots
    }

    covariance = right_roots == expected_right

    if not covariance:
        inversion_covariance_failures.append({
            "state": state,
            "partner": partner,
            "left_roots": sorted(left_roots),
            "right_roots": sorted(right_roots),
            "expected_right": sorted(expected_right),
        })

    candidate_duads = sorted({
        root_to_duad[root]
        for root in left_roots | right_roots
    })

    half_orbit_rows.append({
        "orbit": sorted((state, partner)),
        "left_roots": sorted(left_roots),
        "right_roots": sorted(right_roots),
        "candidate_duads": [
            list(duad)
            for duad in candidate_duads
        ],
        "candidate_duad_count":
            len(candidate_duads),
        "inversion_covariant":
            covariance,
    })

half_orbit_duad_count_profile = dict(sorted(Counter(
    row["candidate_duad_count"]
    for row in half_orbit_rows
).items()))

radius_one_unique = all(
    row["minimizer_count"] == 1
    for row in radius_one
)

radius_one_mapping = None
radius_one_root_fiber_profile = {}
radius_one_duad_fiber_profile = {}

if radius_one_unique:
    radius_one_mapping = tuple(
        row["minimizers"][0]
        for row in radius_one
    )

    root_counts = Counter(radius_one_mapping)
    duad_counts = Counter(
        str(root_to_duad[root])
        for root in radius_one_mapping
    )

    radius_one_root_fiber_profile = dict(sorted(Counter(
        root_counts.values()
    ).items()))

    radius_one_duad_fiber_profile = dict(sorted(Counter(
        duad_counts.values()
    ).items()))

checks = {
    "source_layer_valid":
        all(source_checks.values()),
    "H60_order_480":
        len(permutations) == 480,
    "orientation_root_count_20":
        len(roots) == 20,
    "g60_degree_4":
        {len(adjacency[x]) for x in adjacency} == {4},
    "half_flip_orbit_count_30":
        len(half_orbit_rows) == 30,
    "radius_zero_profile_reproduced":
        radius_profiles[0][
            "minimizer_count_profile"
        ] == {1: 38, 2: 20, 8: 2},
    "radius_zero_inversion_covariant":
        not inversion_covariance_failures,
}

failed = [
    name
    for name, passed in checks.items()
    if not passed
]

if radius_one_unique:
    classification = (
        "first_order_hinge_germ_selects_unique_"
        "orientation_root_at_every_state"
    )
elif radius_profiles[1]["unique_state_count"] > 38:
    classification = (
        "first_order_hinge_germ_reduces_but_"
        "does_not_close_root_ambiguity"
    )
else:
    classification = (
        "first_order_hinge_germ_does_not_improve_"
        "root_selection"
    )

print("== G900 HALF-FLIP ROOT-GERM AUDIT 017 ==")
print("ACTION_SHA256:", sha256(action_path))
print("BRIDGE_SHA256:", sha256(bridge_path))
print("SOURCE_LAYER_CHECKS:", source_checks)
print("G60_DIAMETER:", diameter)

print()
print("== RADIUS PROFILES ==")

for radius in sorted(radius_profiles):
    print(
        "RADIUS",
        radius,
        "PROFILE",
        radius_profiles[radius],
    )

print()
print("== HALF-FLIP ORBIT QUOTIENT ==")
print("HALF_FLIP_ORBIT_COUNT:", len(half_orbit_rows))
print(
    "HALF_ORBIT_DUAD_COUNT_PROFILE:",
    half_orbit_duad_count_profile,
)
print(
    "INVERSION_COVARIANCE_FAILURE_COUNT:",
    len(inversion_covariance_failures),
)
print(
    "INVERSION_COVARIANCE_FAILURES:",
    inversion_covariance_failures,
)

for row in half_orbit_rows:
    print(
        "ORBIT",
        row["orbit"],
        "LEFT_ROOTS",
        row["left_roots"],
        "RIGHT_ROOTS",
        row["right_roots"],
        "DUADS",
        row["candidate_duads"],
        "INVERSION_COVARIANT",
        row["inversion_covariant"],
    )

print()
print("== RADIUS-ONE STATE ROWS ==")

for row in radius_one:
    print(
        "STATE",
        row["state"],
        "BALL_SIZE",
        row["ball_size"],
        "MIN_ENERGY",
        row["minimum_energy"],
        "MINIMIZER_COUNT",
        row["minimizer_count"],
        "ROOTS",
        row["minimizers"],
        "SECOND_ENERGY",
        row["second_energy"],
        "GAP",
        row["gap"],
    )

if radius_one_mapping is not None:
    print()
    print(
        "RADIUS_ONE_VERTEX_TO_ROOT_MAP:",
        list(radius_one_mapping),
    )
    print(
        "RADIUS_ONE_ROOT_FIBER_PROFILE:",
        radius_one_root_fiber_profile,
    )
    print(
        "RADIUS_ONE_DUAD_FIBER_PROFILE:",
        radius_one_duad_fiber_profile,
    )

print()
print("CHECKS:", checks)
print("FAILED_CHECK_COUNT:", len(failed))
print("FAILED_CHECKS:", failed)
print("AUDIT_PASS:", not failed)
print("CLASSIFICATION:", classification)
print(
    "RADIUS_ONE_ROOT_MAP_PROVED:",
    radius_one_unique,
)
print(
    "RADIUS_ZERO_INVERSION_COVARIANCE_PROVED:",
    not inversion_covariance_failures,
)
print("EPSILON_SELECTED: false")
print("ABSOLUTE_ORIENTATION_SELECTED: false")
print("PHYSICAL_CLAIM: false")
print("PROJECT_MUTATION_PERFORMED: false")

if failed:
    raise SystemExit(1)
