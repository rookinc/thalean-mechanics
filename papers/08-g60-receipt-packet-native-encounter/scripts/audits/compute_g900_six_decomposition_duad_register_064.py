#!/usr/bin/env python3

import itertools
import json
import pathlib
from collections import Counter, defaultdict

SOURCE = pathlib.Path(
    "/data/data/com.termux/files/home/dev/cori/research/"
    "mathematics/41-order-4-dodecahedral-residue/"
    "artifacts/json/intrinsic_g15_line_petersen_audit_015.json"
)

data = json.loads(SOURCE.read_text(encoding="utf-8"))

def edge(left, right):
    return tuple(sorted((int(left), int(right))))

native_edges = frozenset(
    edge(*row["quotient_edge"])
    for row in data["measurements"]["quotient_edges"]
)

state_to_root_edge = {
    int(row["g15_state"]): edge(*row["root_edge"])
    for row in data["measurements"]["g15_state_to_root_edge"]
}

vertices = frozenset(state_to_root_edge)

root_edges = frozenset(state_to_root_edge.values())

root_vertices = frozenset(
    vertex
    for pair in root_edges
    for vertex in pair
)

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

def induced_edges(selected):
    selected = frozenset(selected)

    return frozenset(
        pair
        for pair in native_edges
        if pair[0] in selected and pair[1] in selected
    )

def is_induced_c5(selected):
    selected = frozenset(selected)

    if len(selected) != 5:
        return False

    local_edges = induced_edges(selected)

    if len(local_edges) != 5:
        return False

    return Counter(
        sum(vertex in pair for pair in local_edges)
        for vertex in selected
    ) == Counter({2: 5})

def root_degree_profile(root_edge_set):
    degrees = Counter()

    for left, right in root_edge_set:
        degrees[left] += 1
        degrees[right] += 1

    return Counter(degrees.values())

def root_connected(root_edge_set):
    local = defaultdict(set)

    for left, right in root_edge_set:
        local[left].add(right)
        local[right].add(left)

    used_vertices = set(local)

    if not used_vertices:
        return True

    start = min(used_vertices)
    seen = {start}
    stack = [start]

    while stack:
        current = stack.pop()

        for neighbor in local[current]:
            if neighbor not in seen:
                seen.add(neighbor)
                stack.append(neighbor)

    return seen == used_vertices

def root_is_c5(state_set):
    root_edge_set = {
        state_to_root_edge[state]
        for state in state_set
    }

    used_vertices = {
        vertex
        for pair in root_edge_set
        for vertex in pair
    }

    return (
        len(root_edge_set) == 5
        and len(used_vertices) == 5
        and root_degree_profile(root_edge_set)
        == Counter({2: 5})
        and root_connected(root_edge_set)
    )

def root_is_perfect_matching(state_set):
    root_edge_set = {
        state_to_root_edge[state]
        for state in state_set
    }

    return (
        len(root_edge_set) == 5
        and {
            vertex
            for pair in root_edge_set
            for vertex in pair
        } == set(root_vertices)
        and root_degree_profile(root_edge_set)
        == Counter({1: 10})
    )

c5_sets = tuple(
    frozenset(candidate)
    for candidate in itertools.combinations(sorted(vertices), 5)
    if is_induced_c5(candidate)
)

solutions = []

for left_index, left in enumerate(c5_sets):
    for right in c5_sets[left_index + 1:]:
        if left & right:
            continue

        spokes = vertices - left - right

        if len(spokes) != 5:
            continue

        if induced_edges(spokes):
            continue

        if any(
            edge(left_vertex, right_vertex) in native_edges
            for left_vertex in left
            for right_vertex in right
        ):
            continue

        bridge_valid = True

        for spoke in spokes:
            left_neighbors = adjacency[spoke] & left
            right_neighbors = adjacency[spoke] & right

            if len(left_neighbors) != 2:
                bridge_valid = False
                break

            if len(right_neighbors) != 2:
                bridge_valid = False
                break

            if edge(*left_neighbors) not in native_edges:
                bridge_valid = False
                break

            if edge(*right_neighbors) not in native_edges:
                bridge_valid = False
                break

        if not bridge_valid:
            continue

        solutions.append({
            "cycles": tuple(sorted((
                tuple(sorted(left)),
                tuple(sorted(right)),
            ))),
            "spokes": tuple(sorted(spokes)),
        })

solutions = tuple(sorted(
    solutions,
    key=lambda row: (
        row["spokes"],
        row["cycles"],
    ),
))

decomposition_rows = []

for decomposition_id, solution in enumerate(solutions):
    left_cycle = frozenset(solution["cycles"][0])
    right_cycle = frozenset(solution["cycles"][1])
    spokes = frozenset(solution["spokes"])

    decomposition_rows.append({
        "decomposition_id": decomposition_id,
        "cycle_0": tuple(sorted(left_cycle)),
        "cycle_1": tuple(sorted(right_cycle)),
        "spokes": tuple(sorted(spokes)),
        "root_cycle_0_edges": tuple(sorted(
            state_to_root_edge[state]
            for state in left_cycle
        )),
        "root_cycle_1_edges": tuple(sorted(
            state_to_root_edge[state]
            for state in right_cycle
        )),
        "root_matching_edges": tuple(sorted(
            state_to_root_edge[state]
            for state in spokes
        )),
        "cycle_0_is_root_C5": root_is_c5(left_cycle),
        "cycle_1_is_root_C5": root_is_c5(right_cycle),
        "spokes_are_root_perfect_matching":
            root_is_perfect_matching(spokes),
    })

spoke_sets = tuple(
    frozenset(row["spokes"])
    for row in decomposition_rows
)

pair_intersection_rows = []

for left_id, right_id in itertools.combinations(
    range(len(spoke_sets)),
    2,
):
    intersection = tuple(sorted(
        spoke_sets[left_id] & spoke_sets[right_id]
    ))

    pair_intersection_rows.append({
        "decomposition_pair": (left_id, right_id),
        "intersection": intersection,
        "intersection_size": len(intersection),
    })

state_to_decomposition_pair = {}

for row in pair_intersection_rows:
    if row["intersection_size"] == 1:
        state = row["intersection"][0]
        state_to_decomposition_pair[state] = (
            row["decomposition_pair"]
        )

decomposition_pair_to_state = {
    row["decomposition_pair"]: row["intersection"][0]
    for row in pair_intersection_rows
    if row["intersection_size"] == 1
}

state_spoke_membership = {
    state: tuple(
        decomposition_id
        for decomposition_id, spoke_set in enumerate(spoke_sets)
        if state in spoke_set
    )
    for state in sorted(vertices)
}

duad_rows = tuple({
    "native_g15_state": state,
    "root_petersen_edge": state_to_root_edge[state],
    "decomposition_duad":
        state_to_decomposition_pair.get(state),
    "spoke_membership":
        state_spoke_membership[state],
} for state in sorted(vertices))

all_decomposition_pairs = set(
    itertools.combinations(range(len(solutions)), 2)
)

observed_decomposition_pairs = set(
    decomposition_pair_to_state
)

all_pair_intersections = [
    row["intersection_size"]
    for row in pair_intersection_rows
]

checks = {
    "source_audit_pass":
        data.get("audit_pass") is True,
    "native_G15_vertex_count_15":
        len(vertices) == 15,
    "root_Petersen_vertex_count_10":
        len(root_vertices) == 10,
    "root_Petersen_edge_count_15":
        len(root_edges) == 15,
    "decomposition_count_6":
        len(solutions) == 6,
    "all_twelve_cycle_registers_are_root_C5s":
        all(
            row["cycle_0_is_root_C5"]
            and row["cycle_1_is_root_C5"]
            for row in decomposition_rows
        ),
    "all_six_spoke_registers_are_root_perfect_matchings":
        all(
            row["spokes_are_root_perfect_matching"]
            for row in decomposition_rows
        ),
    "decomposition_pair_count_15":
        len(pair_intersection_rows) == 15,
    "every_two_spoke_registers_intersect_once":
        Counter(all_pair_intersections) == Counter({1: 15}),
    "pair_intersections_cover_all_G15_states_once":
        len(state_to_decomposition_pair) == 15
        and set(state_to_decomposition_pair) == set(vertices),
    "all_six_choose_two_duads_realized":
        observed_decomposition_pairs
        == all_decomposition_pairs,
    "each_G15_state_has_exactly_two_spoke_memberships":
        Counter(
            len(memberships)
            for memberships in state_spoke_membership.values()
        ) == Counter({2: 15}),
    "state_duad_map_is_bijection":
        len(set(state_to_decomposition_pair.values())) == 15,
}

failed = [
    name
    for name, passed in checks.items()
    if not passed
]

theorem_pass = not failed

print("PACKET: g900_six_decomposition_duad_register_064")
print("MODE: intrinsic root-Petersen matching and duad incidence test")
print("DECOMPOSITION_COUNT:", len(solutions))
print("ROOT_PETERSEN_VERTEX_COUNT:", len(root_vertices))
print("ROOT_PETERSEN_EDGE_COUNT:", len(root_edges))
print("DECOMPOSITION_ROWS:", decomposition_rows)
print("PAIR_INTERSECTION_ROWS:", pair_intersection_rows)
print(
    "PAIR_INTERSECTION_SIZE_PROFILE:",
    dict(sorted(Counter(all_pair_intersections).items())),
)
print(
    "STATE_SPOKE_MEMBERSHIP_PROFILE:",
    dict(sorted(Counter(
        len(value)
        for value in state_spoke_membership.values()
    ).items())),
)
print("DUAD_ROWS:", duad_rows)
print(
    "DECOMPOSITION_PAIR_TO_G15_STATE:",
    dict(sorted(decomposition_pair_to_state.items())),
)
print("CHECKS:", checks)
print("FAILED_CHECK_COUNT:", len(failed))
print("FAILED_CHECKS:", failed)
print("THEOREM_PASS:", theorem_pass)
print(
    "CLASSIFICATION:",
    (
        "the_six_intrinsic_double_C5_decompositions_are_"
        "exactly_the_six_root_Petersen_perfect_matchings_"
        "and_their_pairwise_singleton_intersections_give_"
        "a_bijection_between_native_G15_states_and_the_"
        "fifteen_duads_of_the_six_decomposition_register"
        if theorem_pass
        else
        "six_decomposition_duad_register_not_derived"
    ),
)
print(
    "SIX_PERFECT_MATCHING_REGISTER_DERIVED:",
    theorem_pass,
)
print(
    "NATIVE_G15_STATE_TO_SIX_REGISTER_DUAD_DERIVED:",
    theorem_pass,
)
print("HAND_DRAWING_LABELS_USED:", False)
print("AUTOMORPHISM_ORBIT_DERIVED:", False)
print("CANONICAL_DECOMPOSITION_SELECTED:", False)
print("K33_PROJECTION_DERIVED:", False)
print("PHYSICAL_CLAIM:", False)
print("MUTATION_PERFORMED:", False)
