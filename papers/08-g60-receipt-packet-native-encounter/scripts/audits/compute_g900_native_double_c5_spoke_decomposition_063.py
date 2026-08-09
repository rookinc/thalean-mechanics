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

KNOWN_OUTER = frozenset((0, 1, 2, 3, 4))
KNOWN_INNER = frozenset((6, 7, 10, 13, 14))
KNOWN_SPOKES = frozenset((5, 8, 9, 11, 12))

data = json.loads(SOURCE.read_text(encoding="utf-8"))

def edge(left, right):
    return tuple(sorted((int(left), int(right))))

native_edges = frozenset(
    edge(*row["quotient_edge"])
    for row in data["measurements"]["quotient_edges"]
)

vertices = frozenset(
    vertex
    for pair in native_edges
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

    local_degrees = Counter(
        sum(vertex in pair for pair in local_edges)
        for vertex in selected
    )

    if local_degrees != Counter({2: 5}):
        return False

    start = min(selected)
    seen = {start}
    stack = [start]

    while stack:
        current = stack.pop()

        for neighbor in adjacency[current] & selected:
            if neighbor not in seen:
                seen.add(neighbor)
                stack.append(neighbor)

    return seen == set(selected)

def canonical_cycle_order(selected):
    selected = frozenset(selected)
    start = min(selected)
    neighbors = sorted(adjacency[start] & selected)

    candidates = []

    for first in neighbors:
        order = [start, first]
        previous = start
        current = first

        while len(order) < 5:
            next_vertices = sorted(
                (adjacency[current] & selected) - {previous}
            )

            next_vertex = next(
                vertex
                for vertex in next_vertices
                if vertex not in order
            )

            order.append(next_vertex)
            previous, current = current, next_vertex

        if edge(order[-1], order[0]) in native_edges:
            candidates.append(tuple(order))

    return min(candidates)

def partition_key(left, right, spokes):
    cycles = tuple(sorted(
        (
            tuple(sorted(left)),
            tuple(sorted(right)),
        )
    ))

    return cycles + (tuple(sorted(spokes)),)

c5_sets = tuple(
    frozenset(candidate)
    for candidate in itertools.combinations(sorted(vertices), 5)
    if is_induced_c5(candidate)
)

c5_index = {
    cycle: index
    for index, cycle in enumerate(c5_sets)
}

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

        bridge_rows = []
        valid = True

        for spoke in sorted(spokes):
            left_neighbors = tuple(sorted(adjacency[spoke] & left))
            right_neighbors = tuple(sorted(adjacency[spoke] & right))

            if len(left_neighbors) != 2:
                valid = False
                break

            if len(right_neighbors) != 2:
                valid = False
                break

            left_base = edge(*left_neighbors)
            right_base = edge(*right_neighbors)

            if left_base not in native_edges:
                valid = False
                break

            if right_base not in native_edges:
                valid = False
                break

            bridge_rows.append({
                "spoke": spoke,
                "left_base_edge": left_base,
                "right_base_edge": right_base,
                "left_triangle": tuple(sorted(
                    left_neighbors + (spoke,)
                )),
                "right_triangle": tuple(sorted(
                    right_neighbors + (spoke,)
                )),
            })

        if not valid:
            continue

        left_bases = {
            row["left_base_edge"]
            for row in bridge_rows
        }

        right_bases = {
            row["right_base_edge"]
            for row in bridge_rows
        }

        if left_bases != set(induced_edges(left)):
            continue

        if right_bases != set(induced_edges(right)):
            continue

        solutions.append({
            "cycle_left": tuple(sorted(left)),
            "cycle_right": tuple(sorted(right)),
            "spokes": tuple(sorted(spokes)),
            "cycle_left_order": canonical_cycle_order(left),
            "cycle_right_order": canonical_cycle_order(right),
            "bridge_rows": tuple(bridge_rows),
            "partition_key": partition_key(left, right, spokes),
        })

solution_keys = {
    row["partition_key"]
    for row in solutions
}

known_key = partition_key(
    KNOWN_OUTER,
    KNOWN_INNER,
    KNOWN_SPOKES,
)

cycle_membership_count = Counter()
spoke_membership_count = Counter()

for row in solutions:
    for cycle in (
        row["cycle_left"],
        row["cycle_right"],
    ):
        for vertex in cycle:
            cycle_membership_count[vertex] += 1

    for vertex in row["spokes"]:
        spoke_membership_count[vertex] += 1

unique_spoke_registers = {
    row["spokes"]
    for row in solutions
}

unique_cycle_pairs = {
    tuple(sorted((
        row["cycle_left"],
        row["cycle_right"],
    )))
    for row in solutions
}

checks = {
    "source_audit_pass":
        data.get("audit_pass") is True,
    "native_vertex_count_15":
        len(vertices) == 15,
    "native_edge_count_30":
        len(native_edges) == 30,
    "native_degree_profile_4_to_15":
        Counter(
            len(adjacency[vertex])
            for vertex in vertices
        ) == Counter({4: 15}),
    "induced_C5_sets_found":
        len(c5_sets) > 0,
    "intrinsic_double_C5_spoke_solution_exists":
        len(solutions) > 0,
    "known_register_partition_recovered":
        known_key in solution_keys,
    "every_solution_has_two_disjoint_C5s":
        all(
            set(row["cycle_left"]).isdisjoint(
                row["cycle_right"]
            )
            for row in solutions
        ),
    "every_solution_has_independent_spokes":
        all(
            not induced_edges(row["spokes"])
            for row in solutions
        ),
    "every_solution_partitions_all_15_vertices":
        all(
            set(row["cycle_left"])
            | set(row["cycle_right"])
            | set(row["spokes"])
            == set(vertices)
            for row in solutions
        ),
    "every_spoke_completes_two_native_triangles":
        all(
            len(row["bridge_rows"]) == 5
            for row in solutions
        ),
}

failed = [
    name
    for name, passed in checks.items()
    if not passed
]

theorem_pass = not failed

print("PACKET: g900_native_double_c5_spoke_decomposition_063")
print("MODE: exhaustive native G15 unlabeled decomposition search")
print("NATIVE_VERTEX_COUNT:", len(vertices))
print("NATIVE_EDGE_COUNT:", len(native_edges))
print("INDUCED_C5_COUNT:", len(c5_sets))
print("INDUCED_C5_SETS:", tuple(
    tuple(sorted(cycle))
    for cycle in c5_sets
))
print("SOLUTION_COUNT:", len(solutions))
print("UNIQUE_CYCLE_PAIR_COUNT:", len(unique_cycle_pairs))
print("UNIQUE_SPOKE_REGISTER_COUNT:", len(unique_spoke_registers))
print("KNOWN_PARTITION_RECOVERED:", known_key in solution_keys)
print(
    "CYCLE_MEMBERSHIP_COUNT_PROFILE:",
    dict(sorted(Counter(
        cycle_membership_count.values()
    ).items())),
)
print(
    "SPOKE_MEMBERSHIP_COUNT_PROFILE:",
    dict(sorted(Counter(
        spoke_membership_count.values()
    ).items())),
)
print("SOLUTION_PREVIEW:", solutions[:20])
print("CHECKS:", checks)
print("FAILED_CHECK_COUNT:", len(failed))
print("FAILED_CHECKS:", failed)
print("THEOREM_PASS:", theorem_pass)
print(
    "CLASSIFICATION:",
    (
        "native_G15_intrinsically_admits_unlabeled_partitions_"
        "into_two_induced_C5_registers_and_one_independent_"
        "five_spoke_register_with_each_spoke_completing_one_"
        "native_triangle_on_each_C5"
        if theorem_pass
        else
        "native_double_C5_spoke_decomposition_not_recovered"
    ),
)
print("HAND_DRAWING_LABELS_USED_IN_SEARCH:", False)
print("KNOWN_REGISTER_USED_ONLY_FOR_POST_SEARCH_CHECK:", True)
print("UNIQUE_NATIVE_PARTITION_DERIVED:", len(solutions) == 1)
print("AUTOMORPHISM_ORBIT_CLASSIFICATION_DERIVED:", False)
print("K33_PROJECTION_DERIVED:", False)
print("PHYSICAL_CUBE_CLAIM:", False)
print("MUTATION_PERFORMED:", False)
