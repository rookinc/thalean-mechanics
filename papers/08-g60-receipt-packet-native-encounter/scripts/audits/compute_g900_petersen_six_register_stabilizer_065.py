#!/usr/bin/env python3

import itertools
import json
import pathlib
from collections import Counter

SOURCE = pathlib.Path(
    "/data/data/com.termux/files/home/dev/cori/research/"
    "mathematics/41-order-4-dodecahedral-residue/"
    "artifacts/json/intrinsic_g15_line_petersen_audit_015.json"
)

KNOWN_SPOKES = frozenset((5, 8, 9, 11, 12))

data = json.loads(SOURCE.read_text(encoding="utf-8"))

def edge(left, right):
    return tuple(sorted((int(left), int(right))))

state_to_root_edge = {
    int(row["g15_state"]): edge(*row["root_edge"])
    for row in data["measurements"]["g15_state_to_root_edge"]
}

root_edge_to_state = {
    root_edge: state
    for state, root_edge in state_to_root_edge.items()
}

root_edges = frozenset(state_to_root_edge.values())

root_vertices = tuple(sorted({
    vertex
    for pair in root_edges
    for vertex in pair
}))

root_adjacency = {
    vertex: frozenset(
        other
        for pair in root_edges
        if vertex in pair
        for other in pair
        if other != vertex
    )
    for vertex in root_vertices
}

def is_perfect_matching(edge_set):
    if len(edge_set) != 5:
        return False

    endpoint_counts = Counter(
        vertex
        for pair in edge_set
        for vertex in pair
    )

    return (
        set(endpoint_counts) == set(root_vertices)
        and Counter(endpoint_counts.values())
        == Counter({1: 10})
    )

root_matchings = tuple(sorted(
    (
        frozenset(candidate)
        for candidate in itertools.combinations(
            sorted(root_edges),
            5,
        )
        if is_perfect_matching(candidate)
    ),
    key=lambda matching: tuple(sorted(matching)),
))

matching_state_sets = tuple(
    frozenset(
        root_edge_to_state[root_edge]
        for root_edge in matching
    )
    for matching in root_matchings
)

matching_id_by_edges = {
    matching: matching_id
    for matching_id, matching in enumerate(root_matchings)
}

matching_id_by_states = {
    states: matching_id
    for matching_id, states in enumerate(matching_state_sets)
}

known_matching_id = matching_id_by_states.get(KNOWN_SPOKES)

automorphisms = []

def extend_automorphism(mapping, used_targets):
    if len(mapping) == len(root_vertices):
        automorphisms.append(tuple(
            mapping[vertex]
            for vertex in root_vertices
        ))
        return

    unassigned_sources = [
        vertex
        for vertex in root_vertices
        if vertex not in mapping
    ]

    source = max(
        unassigned_sources,
        key=lambda vertex: (
            sum(
                neighbor in mapping
                for neighbor in root_adjacency[vertex]
            ),
            -vertex,
        ),
    )

    for target in root_vertices:
        if target in used_targets:
            continue

        consistent = True

        for assigned_source, assigned_target in mapping.items():
            source_adjacent = (
                assigned_source in root_adjacency[source]
            )
            target_adjacent = (
                assigned_target in root_adjacency[target]
            )

            if source_adjacent != target_adjacent:
                consistent = False
                break

        if not consistent:
            continue

        mapping[source] = target
        used_targets.add(target)

        extend_automorphism(mapping, used_targets)

        used_targets.remove(target)
        del mapping[source]

extend_automorphism({}, set())

def automorphism_map(automorphism):
    return {
        root_vertices[index]: automorphism[index]
        for index in range(len(root_vertices))
    }

def image_root_edge(root_edge, mapping):
    return edge(
        mapping[root_edge[0]],
        mapping[root_edge[1]],
    )

def permutation_order(permutation):
    identity = tuple(range(len(permutation)))
    current = identity

    for exponent in range(1, 1001):
        current = tuple(
            permutation[value]
            for value in current
        )

        if current == identity:
            return exponent

    return None

def fixed_point_count(permutation):
    return sum(
        index == image
        for index, image in enumerate(permutation)
    )

six_register_actions = []
state_actions = []

for automorphism in automorphisms:
    mapping = automorphism_map(automorphism)

    matching_permutation = tuple(
        matching_id_by_edges[frozenset(
            image_root_edge(root_edge, mapping)
            for root_edge in matching
        )]
        for matching in root_matchings
    )

    state_permutation = tuple(
        root_edge_to_state[
            image_root_edge(
                state_to_root_edge[state],
                mapping,
            )
        ]
        for state in sorted(state_to_root_edge)
    )

    six_register_actions.append(matching_permutation)
    state_actions.append(state_permutation)

distinct_six_actions = set(six_register_actions)
distinct_state_actions = set(state_actions)

six_orbit = {
    permutation[0]
    for permutation in distinct_six_actions
}

six_action_kernel = {
    automorphisms[index]
    for index, permutation in enumerate(six_register_actions)
    if permutation == tuple(range(6))
}

known_stabilizer_indices = tuple(
    index
    for index, permutation in enumerate(six_register_actions)
    if permutation[known_matching_id] == known_matching_id
)

known_spokes = tuple(sorted(KNOWN_SPOKES))

spoke_local_index = {
    state: index
    for index, state in enumerate(known_spokes)
}

spoke_actions = []

for automorphism_index in known_stabilizer_indices:
    state_permutation = state_actions[automorphism_index]

    spoke_permutation = tuple(
        spoke_local_index[state_permutation[state]]
        for state in known_spokes
    )

    spoke_actions.append(spoke_permutation)

distinct_spoke_actions = set(spoke_actions)

spoke_order_profile = Counter(
    permutation_order(permutation)
    for permutation in distinct_spoke_actions
)

spoke_fixed_point_profile = Counter(
    fixed_point_count(permutation)
    for permutation in distinct_spoke_actions
)

ordered_pair_image_counts = Counter()

for left in range(5):
    for right in range(5):
        if left == right:
            continue

        images = {
            (
                permutation[left],
                permutation[right],
            )
            for permutation in distinct_spoke_actions
        }

        ordered_pair_image_counts[len(images)] += 1

matching_rows = tuple({
    "decomposition_id": matching_id,
    "spoke_states": tuple(sorted(matching_state_sets[matching_id])),
    "root_perfect_matching": tuple(sorted(matching)),
    "is_known_capstone_register":
        matching_id == known_matching_id,
} for matching_id, matching in enumerate(root_matchings))

six_action_order_profile = Counter(
    permutation_order(permutation)
    for permutation in distinct_six_actions
)

six_action_fixed_profile = Counter(
    fixed_point_count(permutation)
    for permutation in distinct_six_actions
)

checks = {
    "source_audit_pass":
        data.get("audit_pass") is True,
    "root_Petersen_vertex_count_10":
        len(root_vertices) == 10,
    "root_Petersen_edge_count_15":
        len(root_edges) == 15,
    "root_Petersen_degree_profile_3_to_10":
        Counter(
            len(root_adjacency[vertex])
            for vertex in root_vertices
        ) == Counter({3: 10}),
    "perfect_matching_count_6":
        len(root_matchings) == 6,
    "root_automorphism_group_order_120":
        len(automorphisms) == 120,
    "all_root_automorphisms_induce_distinct_G15_actions":
        len(distinct_state_actions) == 120,
    "six_register_action_is_faithful":
        len(distinct_six_actions) == 120
        and len(six_action_kernel) == 1,
    "six_register_action_is_transitive":
        six_orbit == set(range(6)),
    "known_capstone_spoke_register_found":
        known_matching_id is not None,
    "known_register_stabilizer_order_20":
        len(known_stabilizer_indices) == 20,
    "stabilizer_action_on_five_spokes_is_faithful":
        len(distinct_spoke_actions) == 20,
    "spoke_action_order_profile_matches_AGL15":
        spoke_order_profile
        == Counter({1: 1, 2: 5, 4: 10, 5: 4}),
    "spoke_action_fixed_profile_matches_AGL15":
        spoke_fixed_point_profile
        == Counter({5: 1, 1: 15, 0: 4}),
    "spoke_action_is_sharply_two_transitive":
        ordered_pair_image_counts == Counter({20: 20}),
}

failed = [
    name
    for name, passed in checks.items()
    if not passed
]

theorem_pass = not failed

print("PACKET: g900_petersen_six_register_stabilizer_065")
print("MODE: exact root automorphism and decomposition stabilizer census")
print("ROOT_AUTOMORPHISM_GROUP_ORDER:", len(automorphisms))
print("PERFECT_MATCHING_COUNT:", len(root_matchings))
print("MATCHING_ROWS:", matching_rows)
print("KNOWN_MATCHING_ID:", known_matching_id)
print("DISTINCT_SIX_REGISTER_ACTION_COUNT:", len(
    distinct_six_actions
))
print("SIX_REGISTER_ORBIT:", tuple(sorted(six_orbit)))
print("SIX_REGISTER_KERNEL_ORDER:", len(six_action_kernel))
print(
    "SIX_ACTION_ORDER_PROFILE:",
    dict(sorted(six_action_order_profile.items())),
)
print(
    "SIX_ACTION_FIXED_POINT_PROFILE:",
    dict(sorted(six_action_fixed_profile.items())),
)
print("KNOWN_REGISTER_STABILIZER_ORDER:", len(
    known_stabilizer_indices
))
print("DISTINCT_SPOKE_ACTION_COUNT:", len(
    distinct_spoke_actions
))
print(
    "SPOKE_ACTION_ORDER_PROFILE:",
    dict(sorted(spoke_order_profile.items())),
)
print(
    "SPOKE_ACTION_FIXED_POINT_PROFILE:",
    dict(sorted(spoke_fixed_point_profile.items())),
)
print(
    "ORDERED_PAIR_IMAGE_COUNT_PROFILE:",
    dict(sorted(ordered_pair_image_counts.items())),
)
print("SPOKE_ACTIONS:", tuple(sorted(distinct_spoke_actions)))
print("CHECKS:", checks)
print("FAILED_CHECK_COUNT:", len(failed))
print("FAILED_CHECKS:", failed)
print("THEOREM_PASS:", theorem_pass)
print(
    "CLASSIFICATION:",
    (
        "the_full_order_120_root_Petersen_automorphism_group_"
        "acts_faithfully_and_transitively_on_the_six_intrinsic_"
        "double_C5_decompositions_and_the_order_20_stabilizer_"
        "of_the_capstone_decomposition_acts_faithfully_and_"
        "sharply_two_transitively_on_its_five_spokes_as_"
        "AGL_1_5"
        if theorem_pass
        else
        "six_register_stabilizer_AGL15_identification_failed"
    ),
)
print("FULL_NATIVE_SYMMETRY_ORDER_120_DERIVED:", theorem_pass)
print("SIX_REGISTER_OUTER_ACTION_DERIVED:", theorem_pass)
print("CAPSTONE_STABILIZER_IS_AGL15:", theorem_pass)
print("CAPSTONE_AFFINE_GROUP_IS_INTRINSIC_STABILIZER:", theorem_pass)
print("CANONICAL_DECOMPOSITION_SELECTED:", False)
print("HAND_DRAWING_LABELS_USED_IN_AUTOMORPHISM_SEARCH:", False)
print("PHYSICAL_CLAIM:", False)
print("MUTATION_PERFORMED:", False)
