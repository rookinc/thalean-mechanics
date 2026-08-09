#!/usr/bin/env python3

import contextlib
import io
import itertools
import pathlib
import runpy
from collections import Counter, deque

SOURCE_066 = (
    pathlib.Path(__file__).resolve().parent
    / "compute_g900_six_register_pair_orbit_reconstruction_066.py"
)

capture = io.StringIO()

with contextlib.redirect_stdout(capture):
    namespace = runpy.run_path(str(SOURCE_066))

data = namespace["data"]
vertices = tuple(namespace["vertices"])
native_edges = namespace["native_edges"]
adjacency = namespace["adjacency"]
state_to_duad = namespace["state_to_duad"]
graph_distance = namespace["graph_distance"]

six_points = tuple(sorted({
    point
    for duad in state_to_duad.values()
    for point in duad
}))

distance_three_edges = frozenset(
    tuple(sorted((left, right)))
    for left, right in itertools.combinations(vertices, 2)
    if graph_distance(left, right) == 3
)

distance_three_adjacency = {
    vertex: frozenset(
        other
        for pair in distance_three_edges
        if vertex in pair
        for other in pair
        if other != vertex
    )
    for vertex in vertices
}

unseen = set(vertices)
components = []

while unseen:
    start = min(unseen)
    component = {start}
    queue = deque([start])

    while queue:
        current = queue.popleft()

        for neighbor in distance_three_adjacency[current]:
            if neighbor not in component:
                component.add(neighbor)
                queue.append(neighbor)

    components.append(tuple(sorted(component)))
    unseen -= component

components = tuple(sorted(components))

syntheme_rows = []

for syntheme_id, component in enumerate(components):
    component_duads = tuple(
        state_to_duad[state]
        for state in component
    )

    duad_pairs_disjoint = all(
        set(left_duad).isdisjoint(right_duad)
        for left_duad, right_duad
        in itertools.combinations(component_duads, 2)
    )

    point_multiplicity = Counter(
        point
        for duad in component_duads
        for point in duad
    )

    induced_distance_three_edges = tuple(sorted(
        pair
        for pair in distance_three_edges
        if pair[0] in component and pair[1] in component
    ))

    syntheme_rows.append({
        "syntheme_id": syntheme_id,
        "native_states": component,
        "duads": component_duads,
        "distance_three_edges":
            induced_distance_three_edges,
        "duads_pairwise_disjoint":
            duad_pairs_disjoint,
        "duads_partition_six_points":
            point_multiplicity == Counter({
                point: 1
                for point in six_points
            }),
    })

state_to_syntheme = {
    state: row["syntheme_id"]
    for row in syntheme_rows
    for state in row["native_states"]
}

pair_rule_rows = []

for left, right in itertools.combinations(vertices, 2):
    left_duad = state_to_duad[left]
    right_duad = state_to_duad[right]

    intersection_size = len(
        set(left_duad) & set(right_duad)
    )

    same_syntheme = (
        state_to_syntheme[left]
        == state_to_syntheme[right]
    )

    if intersection_size == 1:
        predicted_distance = 2
        rule = "duads_intersect_once"
    elif same_syntheme:
        predicted_distance = 3
        rule = "disjoint_duads_same_syntheme"
    else:
        predicted_distance = 1
        rule = "disjoint_duads_different_synthemes"

    actual_distance = graph_distance(left, right)

    pair_rule_rows.append({
        "state_pair": (left, right),
        "duad_pair": (left_duad, right_duad),
        "intersection_size": intersection_size,
        "same_syntheme": same_syntheme,
        "rule": rule,
        "predicted_distance": predicted_distance,
        "actual_distance": actual_distance,
        "matches": predicted_distance == actual_distance,
    })

rule_count_profile = Counter(
    row["rule"]
    for row in pair_rule_rows
)

predicted_distance_profile = Counter(
    row["predicted_distance"]
    for row in pair_rule_rows
)

actual_distance_profile = Counter(
    row["actual_distance"]
    for row in pair_rule_rows
)

syntheme_state_union = {
    state
    for row in syntheme_rows
    for state in row["native_states"]
}

syntheme_duad_union = {
    duad
    for row in syntheme_rows
    for duad in row["duads"]
}

all_six_duads = {
    tuple(pair)
    for pair in itertools.combinations(six_points, 2)
}

checks = {
    "source_066_exists":
        SOURCE_066.is_file(),
    "source_audit_pass":
        data.get("audit_pass") is True,
    "six_register_point_count_6":
        len(six_points) == 6,
    "native_state_count_15":
        len(vertices) == 15,
    "native_states_are_all_six_choose_two_duads":
        set(state_to_duad.values()) == all_six_duads,
    "distance_three_edge_count_15":
        len(distance_three_edges) == 15,
    "distance_three_degree_profile_2_to_15":
        Counter(
            len(distance_three_adjacency[state])
            for state in vertices
        ) == Counter({2: 15}),
    "distance_three_component_count_5":
        len(components) == 5,
    "every_distance_three_component_is_K3":
        all(
            len(row["native_states"]) == 3
            and len(row["distance_three_edges"]) == 3
            for row in syntheme_rows
        ),
    "every_component_is_a_syntheme":
        all(
            row["duads_pairwise_disjoint"]
            and row["duads_partition_six_points"]
            for row in syntheme_rows
        ),
    "five_synthemes_partition_all_15_states":
        syntheme_state_union == set(vertices)
        and sum(
            len(row["native_states"])
            for row in syntheme_rows
        ) == 15,
    "five_synthemes_partition_all_15_duads":
        syntheme_duad_union == all_six_duads
        and sum(
            len(row["duads"])
            for row in syntheme_rows
        ) == 15,
    "direct_duad_syntheme_rule_recovers_all_distances":
        all(row["matches"] for row in pair_rule_rows),
    "direct_rule_distance_profile_30_60_15":
        predicted_distance_profile
        == Counter({1: 30, 2: 60, 3: 15}),
    "predicted_and_actual_profiles_match":
        predicted_distance_profile == actual_distance_profile,
}

failed = [
    name
    for name, passed in checks.items()
    if not passed
]

theorem_pass = not failed

print("PACKET: g900_six_register_synthematic_total_067")
print("MODE: exact duad syntheme and native distance reconstruction")
print("SIX_REGISTER_POINTS:", six_points)
print("STATE_TO_DUAD:", dict(sorted(state_to_duad.items())))
print("DISTANCE_THREE_COMPONENTS:", components)
print("SYNTHEME_ROWS:", syntheme_rows)
print("STATE_TO_SYNTHEME:", dict(sorted(
    state_to_syntheme.items()
)))
print("RULE_COUNT_PROFILE:", dict(sorted(
    rule_count_profile.items()
)))
print("PREDICTED_DISTANCE_PROFILE:", dict(sorted(
    predicted_distance_profile.items()
)))
print("ACTUAL_DISTANCE_PROFILE:", dict(sorted(
    actual_distance_profile.items()
)))
print("PAIR_RULE_PREVIEW:", pair_rule_rows[:30])
print("CHECKS:", checks)
print("FAILED_CHECK_COUNT:", len(failed))
print("FAILED_CHECKS:", failed)
print("THEOREM_PASS:", theorem_pass)
print(
    "CLASSIFICATION:",
    (
        "the_native_distance_three_relation_is_exactly_five_"
        "disjoint_K3_components_whose_three_duads_partition_"
        "the_six_decomposition_points_so_they_form_a_"
        "synthematic_total_and_the_duad_intersection_plus_"
        "syntheme_rule_reconstructs_the_full_G15_metric"
        if theorem_pass
        else
        "six_register_synthematic_total_not_derived"
    ),
)
print("NATIVE_SYNTHEMATIC_TOTAL_DERIVED:", theorem_pass)
print("DIRECT_SIX_POINT_G15_METRIC_RULE_DERIVED:", theorem_pass)
print("DISTANCE_1_RULE:",
      "disjoint_duads_in_different_synthemes")
print("DISTANCE_2_RULE:",
      "duads_intersect_in_one_register_point")
print("DISTANCE_3_RULE:",
      "disjoint_duads_in_the_same_syntheme")
print("SIX_PLUS_NINE_K33_GATE_OPEN:", theorem_pass)
print("K33_PROJECTION_DERIVED:", False)
print("HAND_DRAWING_LABELS_USED:", False)
print("PHYSICAL_CLAIM:", False)
print("MUTATION_PERFORMED:", False)
