#!/usr/bin/env python3

import contextlib
import io
import itertools
import pathlib
import runpy
from collections import Counter, deque

SOURCE_065 = (
    pathlib.Path(__file__).resolve().parent
    / "compute_g900_petersen_six_register_stabilizer_065.py"
)

capture = io.StringIO()

with contextlib.redirect_stdout(capture):
    namespace = runpy.run_path(str(SOURCE_065))

data = namespace["data"]
vertices = tuple(sorted(namespace["state_to_root_edge"]))
native_edges = namespace["native_edges"] if "native_edges" in namespace else None
state_to_root_edge = namespace["state_to_root_edge"]
root_edge_to_state = namespace["root_edge_to_state"]
root_edges = namespace["root_edges"]
root_matchings = namespace["root_matchings"]
matching_state_sets = namespace["matching_state_sets"]
state_actions = tuple(namespace["distinct_state_actions"])

if native_edges is None:
    native_edges = frozenset(
        tuple(sorted((
            int(row["quotient_edge"][0]),
            int(row["quotient_edge"][1]),
        )))
        for row in data["measurements"]["quotient_edges"]
    )

def edge(left, right):
    return tuple(sorted((int(left), int(right))))

adjacency = {
    vertex: frozenset(
        other
        for pair in native_edges
        if vertex in pair
        for other in pair
        if other != vertex
    )
    for vertex in vertices
}

def graph_distance(source, target):
    if source == target:
        return 0

    seen = {source}
    queue = deque([(source, 0)])

    while queue:
        current, distance = queue.popleft()

        for neighbor in adjacency[current]:
            if neighbor == target:
                return distance + 1

            if neighbor not in seen:
                seen.add(neighbor)
                queue.append((neighbor, distance + 1))

    return None

state_to_duad = {
    state: tuple(
        matching_id
        for matching_id, matching_states
        in enumerate(matching_state_sets)
        if state in matching_states
    )
    for state in vertices
}

all_pairs = frozenset(
    edge(left, right)
    for left, right in itertools.combinations(vertices, 2)
)

def image_pair(pair, permutation):
    return edge(
        permutation[pair[0]],
        permutation[pair[1]],
    )

unclassified = set(all_pairs)
pair_orbits = []

while unclassified:
    seed = min(unclassified)

    orbit = frozenset(
        image_pair(seed, permutation)
        for permutation in state_actions
    )

    pair_orbits.append(orbit)
    unclassified -= orbit

pair_orbits = tuple(sorted(
    pair_orbits,
    key=lambda orbit: (
        len(orbit),
        tuple(sorted(orbit)),
    ),
))

orbit_rows = []

for orbit_id, orbit in enumerate(pair_orbits):
    distance_profile = Counter(
        graph_distance(*pair)
        for pair in orbit
    )

    duad_intersection_profile = Counter(
        len(
            set(state_to_duad[pair[0]])
            & set(state_to_duad[pair[1]])
        )
        for pair in orbit
    )

    duad_union_profile = Counter(
        len(
            set(state_to_duad[pair[0]])
            | set(state_to_duad[pair[1]])
        )
        for pair in orbit
    )

    native_edge_count = sum(
        pair in native_edges
        for pair in orbit
    )

    orbit_rows.append({
        "orbit_id": orbit_id,
        "orbit_size": len(orbit),
        "representative": min(orbit),
        "representative_duads": (
            state_to_duad[min(orbit)[0]],
            state_to_duad[min(orbit)[1]],
        ),
        "distance_profile":
            dict(sorted(distance_profile.items())),
        "native_edge_count": native_edge_count,
        "duad_intersection_profile":
            dict(sorted(duad_intersection_profile.items())),
        "duad_union_profile":
            dict(sorted(duad_union_profile.items())),
        "pair_preview": tuple(sorted(orbit))[:20],
    })

distance_pair_counts = Counter(
    graph_distance(*pair)
    for pair in all_pairs
)

native_adjacency_orbits = tuple(
    row["orbit_id"]
    for row in orbit_rows
    if row["native_edge_count"] == row["orbit_size"]
)

mixed_adjacency_orbits = tuple(
    row["orbit_id"]
    for row in orbit_rows
    if 0 < row["native_edge_count"] < row["orbit_size"]
)

orbit_size_profile = Counter(
    row["orbit_size"]
    for row in orbit_rows
)

checks = {
    "source_065_exists":
        SOURCE_065.is_file(),
    "source_audit_pass":
        data.get("audit_pass") is True,
    "native_vertex_count_15":
        len(vertices) == 15,
    "native_edge_count_30":
        len(native_edges) == 30,
    "six_perfect_matching_count":
        len(root_matchings) == 6,
    "state_to_duad_is_15_bijection":
        len(state_to_duad) == 15
        and len(set(state_to_duad.values())) == 15
        and Counter(
            len(duad)
            for duad in state_to_duad.values()
        ) == Counter({2: 15}),
    "automorphism_action_count_120":
        len(state_actions) == 120,
    "all_105_state_pairs_partitioned":
        sum(len(orbit) for orbit in pair_orbits) == 105
        and set().union(*pair_orbits) == set(all_pairs),
    "no_pair_orbit_mixes_native_adjacency":
        not mixed_adjacency_orbits,
    "native_adjacency_is_union_of_full_orbits":
        sum(
            row["orbit_size"]
            for row in orbit_rows
            if row["orbit_id"] in native_adjacency_orbits
        ) == 30,
    "every_pair_orbit_has_one_native_distance":
        all(
            len(row["distance_profile"]) == 1
            for row in orbit_rows
        ),
    "distance_pair_profile_is_30_60_15":
        distance_pair_counts
        == Counter({1: 30, 2: 60, 3: 15}),
}

failed = [
    name
    for name, passed in checks.items()
    if not passed
]

theorem_pass = not failed

print("PACKET: g900_six_register_pair_orbit_reconstruction_066")
print("MODE: intrinsic six-register pair-orbit and distance census")
print("STATE_TO_DUAD:", dict(sorted(state_to_duad.items())))
print("STATE_PAIR_COUNT:", len(all_pairs))
print("PAIR_ORBIT_COUNT:", len(pair_orbits))
print("PAIR_ORBIT_SIZE_PROFILE:", dict(sorted(
    orbit_size_profile.items()
)))
print("PAIR_ORBIT_ROWS:", orbit_rows)
print("NATIVE_DISTANCE_PAIR_PROFILE:", dict(sorted(
    distance_pair_counts.items()
)))
print("NATIVE_ADJACENCY_ORBITS:", native_adjacency_orbits)
print("MIXED_ADJACENCY_ORBITS:", mixed_adjacency_orbits)
print("CHECKS:", checks)
print("FAILED_CHECK_COUNT:", len(failed))
print("FAILED_CHECKS:", failed)
print("THEOREM_PASS:", theorem_pass)
print(
    "CLASSIFICATION:",
    (
        "the_order_120_six_register_action_partitions_all_"
        "one_hundred_five_native_G15_state_pairs_into_exact_"
        "distance_orbits_and_recovers_the_thirty_edge_native_"
        "adjacency_relation_as_a_full_pair_orbit"
        if theorem_pass
        else
        "six_register_pair_orbits_do_not_reconstruct_G15"
    ),
)
print("G15_ADJACENCY_FROM_SIX_REGISTER_ACTION_DERIVED:",
      theorem_pass)
print("G15_DISTANCE_PARTITION_FROM_PAIR_ORBITS_DERIVED:",
      theorem_pass)
print("FULL_S6_ACTION_CLAIM:", False)
print("ACTION_IS_EXCEPTIONAL_S5_ON_SIX_REGISTER:", theorem_pass)
print("HAND_DRAWING_LABELS_USED:", False)
print("PHYSICAL_CLAIM:", False)
print("MUTATION_PERFORMED:", False)
