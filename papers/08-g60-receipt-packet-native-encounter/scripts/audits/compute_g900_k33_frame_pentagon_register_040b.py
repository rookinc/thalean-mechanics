#!/usr/bin/env python3

from collections import Counter, defaultdict, deque

vertices = ("A", "B", "C", "D", "E", "F")
left_part = {"A", "B", "F"}
right_part = {"C", "D", "E"}

def edge(left, right):
    return tuple(sorted((left, right)))

k33_edges = {
    edge(left, right)
    for left in left_part
    for right in right_part
}

interior_edges = {
    edge("A", "D"),
    edge("A", "E"),
    edge("B", "C"),
    edge("B", "D"),
    edge("D", "F"),
}

boundary_edges = {
    edge("A", "C"),
    edge("C", "F"),
    edge("E", "F"),
    edge("B", "E"),
}

frame_closure = edge("A", "B")
boundary_cycle_edges = boundary_edges | {frame_closure}
boundary_cycle_order = ("A", "B", "E", "F", "C")

reflection = {
    "A": "B",
    "B": "A",
    "C": "E",
    "E": "C",
    "D": "D",
    "F": "F",
}

angle_word = (180, 90, 90, 90, 90)

native_pentagram_order = (13, 14, 7, 6, 10)

def mapped_edge(pair, mapping):
    return edge(mapping[pair[0]], mapping[pair[1]])

def degrees(selected_vertices, selected_edges):
    return Counter(
        sum(vertex in pair for pair in selected_edges)
        for vertex in selected_vertices
    )

def connected(selected_vertices, selected_edges):
    selected_vertices = set(selected_vertices)
    adjacency = defaultdict(set)

    for left, right in selected_edges:
        adjacency[left].add(right)
        adjacency[right].add(left)

    start = next(iter(selected_vertices))
    seen = {start}
    queue = deque([start])

    while queue:
        current = queue.popleft()
        for neighbor in adjacency[current]:
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)

    return seen == selected_vertices

def cycle_edges(order):
    return {
        edge(order[index], order[(index + 1) % len(order)])
        for index in range(len(order))
    }

reflection_interior = {
    mapped_edge(pair, reflection)
    for pair in interior_edges
}

reflection_boundary = {
    mapped_edge(pair, reflection)
    for pair in boundary_edges
}

reflection_cycle = {
    mapped_edge(pair, reflection)
    for pair in boundary_cycle_edges
}

native_cycle_edges = cycle_edges(native_pentagram_order)

cycle_isomorphisms = []

for shift in range(5):
    forward = native_pentagram_order[
        shift:
    ] + native_pentagram_order[
        :shift
    ]

    reverse_base = tuple(reversed(native_pentagram_order))
    reverse = reverse_base[
        shift:
    ] + reverse_base[
        :shift
    ]

    for orientation, target_order in (
        ("forward", forward),
        ("reverse", reverse),
    ):
        mapping = dict(zip(boundary_cycle_order, target_order))

        mapped = {
            edge(mapping[pair[0]], mapping[pair[1]])
            for pair in boundary_cycle_edges
        }

        if mapped == native_cycle_edges:
            cycle_isomorphisms.append({
                "shift": shift,
                "orientation": orientation,
                "mapping": mapping,
                "image_of_flat_edge_AB":
                    edge(mapping["A"], mapping["B"]),
            })

checks = {
    "k33_vertex_count_6":
        len(vertices) == 6,
    "k33_edge_count_9":
        len(k33_edges) == 9,
    "k33_degree_profile_3_to_6":
        degrees(vertices, k33_edges) == Counter({3: 6}),
    "five_plus_four_partition_exact":
        len(interior_edges) == 5
        and len(boundary_edges) == 4
        and interior_edges.isdisjoint(boundary_edges)
        and interior_edges | boundary_edges == k33_edges,
    "interior_is_six_vertex_tree":
        connected(vertices, interior_edges)
        and len(interior_edges) == len(vertices) - 1,
    "interior_tree_degree_profile":
        degrees(vertices, interior_edges)
        == Counter({1: 3, 2: 2, 3: 1}),
    "D_is_unique_tree_root_of_degree_3":
        sum("D" in pair for pair in interior_edges) == 3
        and all(
            sum(vertex in pair for pair in interior_edges) < 3
            for vertex in set(vertices) - {"D"}
        ),
    "boundary_is_path_A_C_F_E_B":
        boundary_edges
        == {
            edge("A", "C"),
            edge("C", "F"),
            edge("F", "E"),
            edge("E", "B"),
        },
    "frame_AB_closes_boundary_to_C5":
        boundary_cycle_edges
        == cycle_edges(boundary_cycle_order),
    "D_is_excluded_from_boundary_C5":
        "D" not in boundary_cycle_order
        and set(boundary_cycle_order)
        == set(vertices) - {"D"},
    "angle_word_profile_one_180_four_90":
        Counter(angle_word) == Counter({90: 4, 180: 1}),
    "angle_word_sum_is_pentagon_540":
        sum(angle_word) == 540,
    "reflection_is_involution":
        all(
            reflection[reflection[vertex]] == vertex
            for vertex in vertices
        ),
    "reflection_preserves_K33":
        {
            mapped_edge(pair, reflection)
            for pair in k33_edges
        } == k33_edges,
    "reflection_preserves_interior_tree":
        reflection_interior == interior_edges,
    "reflection_preserves_boundary_path":
        reflection_boundary == boundary_edges,
    "reflection_preserves_closed_C5":
        reflection_cycle == boundary_cycle_edges,
    "reflection_fixes_D_and_F":
        reflection["D"] == "D"
        and reflection["F"] == "F",
    "native_pentagram_cycle_isomorphism_count_10":
        len(cycle_isomorphisms) == 10,
    "no_unique_native_cycle_labeling":
        len(cycle_isomorphisms) > 1,
}

failed = [
    name
    for name, passed in checks.items()
    if not passed
]

theorem_pass = not failed

print("PACKET: g900_k33_frame_pentagon_register_probe_040b")
print("MODE: exact projected carrier and frame-closure scout")
print("K33_PARTS:", (tuple(sorted(left_part)),
                     tuple(sorted(right_part))))
print("INTERIOR_FIVE_EDGES:", tuple(sorted(interior_edges)))
print("BOUNDARY_FOUR_EDGES:", tuple(sorted(boundary_edges)))
print("BOUNDARY_C5_ORDER:", boundary_cycle_order)
print("ANGLE_WORD:", angle_word)
print("ANGLE_SUM:", sum(angle_word))
print("REFLECTION:", reflection)
print("NATIVE_PENTAGRAM_ORDER:", native_pentagram_order)
print("NATIVE_CYCLE_ISOMORPHISM_COUNT:",
      len(cycle_isomorphisms))
print("NATIVE_CYCLE_ISOMORPHISMS:", cycle_isomorphisms)
print("CHECKS:", checks)
print("FAILED_CHECK_COUNT:", len(failed))
print("FAILED_CHECKS:", failed)
print("THEOREM_PASS:", theorem_pass)
print(
    "CLASSIFICATION:",
    (
        "the_projected_K3_3_splits_into_a_reflection_"
        "invariant_five_edge_rooted_tree_and_four_edge_"
        "boundary_path_whose_frame_closure_is_a_C5_with_"
        "angle_word_180_90_90_90_90"
        if theorem_pass
        else "K3_3_frame_pentagon_register_failed"
    ),
)
print("UNIQUE_NATIVE_C5_LABELING_SELECTED:", False)
print("D_TO_Y1_DIRECTED_RULE_DERIVED:", False)
print("Y1_TO_D_NAN_DERIVED:", False)
print("CUBE_PROJECTION_PHYSICAL:", False)
print("MUTATION_PERFORMED:", False)
