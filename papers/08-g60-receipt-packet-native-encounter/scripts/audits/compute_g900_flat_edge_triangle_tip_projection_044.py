#!/usr/bin/env python3

import json
import pathlib
from collections import Counter, deque

SOURCE = pathlib.Path(
    "/data/data/com.termux/files/home/dev/cori/research/"
    "mathematics/41-order-4-dodecahedral-residue/"
    "artifacts/json/intrinsic_g15_line_petersen_audit_015.json"
)

data = json.loads(SOURCE.read_text(encoding="utf-8"))

def edge(left, right):
    return tuple(sorted((left, right)))

native_edges = {
    edge(*row["quotient_edge"])
    for row in data["measurements"]["quotient_edges"]
}

native_vertices = set(range(15))

adjacency = {
    vertex: {
        other
        for pair in native_edges
        if vertex in pair
        for other in pair
        if other != vertex
    }
    for vertex in native_vertices
}

def distance(left, right):
    distances = {left: 0}
    queue = deque([left])

    while queue:
        current = queue.popleft()

        if current == right:
            return distances[current]

        for neighbor in adjacency[current]:
            if neighbor not in distances:
                distances[neighbor] = distances[current] + 1
                queue.append(neighbor)

    raise RuntimeError("Disconnected native graph")

cycle_order = ("A", "B", "E", "F", "C")
native_pentagram_cycle = (13, 14, 7, 6, 10)
native_spoke_register = {11, 9, 12, 5, 8}

edge_roles = {
    "boundary_AC": edge("A", "C"),
    "boundary_CF": edge("C", "F"),
    "boundary_FE": edge("F", "E"),
    "boundary_EB": edge("E", "B"),
    "root_AD": edge("A", "D"),
    "root_BD": edge("B", "D"),
    "crossed_AE": edge("A", "E"),
    "crossed_BC": edge("B", "C"),
    "axis_DF": edge("D", "F"),
}

expected_role_distances = {
    "boundary_AC": 1,
    "boundary_CF": 1,
    "boundary_FE": 1,
    "boundary_EB": 1,
    "root_AD": 1,
    "root_BD": 1,
    "crossed_AE": 2,
    "crossed_BC": 2,
    "axis_DF": 3,
}

registration_rows = []

for orientation, base in (
    ("forward", native_pentagram_cycle),
    ("reverse", tuple(reversed(native_pentagram_cycle))),
):
    for shift in range(5):
        target = base[shift:] + base[:shift]
        mapping = dict(zip(cycle_order, target))

        A_image = mapping["A"]
        B_image = mapping["B"]

        triangle_tips = tuple(sorted(
            (
                adjacency[A_image]
                & adjacency[B_image]
            )
            - set(mapping.values())
        ))

        if len(triangle_tips) != 1:
            D_image = None
            role_distances = {}
        else:
            D_image = triangle_tips[0]
            mapping["D"] = D_image

            role_distances = {
                role: distance(
                    mapping[pair[0]],
                    mapping[pair[1]],
                )
                for role, pair in edge_roles.items()
            }

        registration_rows.append({
            "orientation": orientation,
            "shift": shift,
            "flat_edge_AB":
                edge(A_image, B_image),
            "triangle_tips": triangle_tips,
            "D_image": D_image,
            "mapping": mapping,
            "role_distances": role_distances,
            "distance_profile":
                dict(Counter(role_distances.values())),
            "role_pattern_exact":
                role_distances
                == expected_role_distances,
        })

D_images = {
    row["D_image"]
    for row in registration_rows
    if row["D_image"] is not None
}

flat_edge_to_D = {}

for row in registration_rows:
    flat_edge_to_D.setdefault(
        row["flat_edge_AB"],
        set(),
    ).add(row["D_image"])

checks = {
    "source_audit_pass":
        data.get("audit_pass") is True,
    "registration_count_10":
        len(registration_rows) == 10,
    "every_flat_edge_has_unique_triangle_tip":
        all(
            len(row["triangle_tips"]) == 1
            for row in registration_rows
        ),
    "orientation_pair_has_same_D_for_each_flat_edge":
        all(
            len(values) == 1
            for values in flat_edge_to_D.values()
        ),
    "five_flat_edges_found":
        len(flat_edge_to_D) == 5,
    "D_images_equal_native_spoke_register":
        D_images == native_spoke_register,
    "every_registration_has_6_2_1_distance_profile":
        all(
            row["distance_profile"]
            == {1: 6, 2: 2, 3: 1}
            for row in registration_rows
        ),
    "every_registration_has_exact_named_role_pattern":
        all(
            row["role_pattern_exact"]
            for row in registration_rows
        ),
    "boundary_four_are_all_native_edges":
        all(
            all(
                row["role_distances"][role] == 1
                for role in (
                    "boundary_AC",
                    "boundary_CF",
                    "boundary_FE",
                    "boundary_EB",
                )
            )
            for row in registration_rows
        ),
    "D_adjacent_exactly_to_A_and_B_among_cycle_roles":
        all(
            row["role_distances"]["root_AD"] == 1
            and row["role_distances"]["root_BD"] == 1
            and row["role_distances"]["crossed_AE"] > 1
            and row["role_distances"]["crossed_BC"] > 1
            and row["role_distances"]["axis_DF"] > 1
            for row in registration_rows
        ),
}

failed = [
    name
    for name, passed in checks.items()
    if not passed
]

theorem_pass = not failed

print("PACKET: g900_flat_edge_triangle_tip_projection_044")
print("MODE: native triangle completion and distance-role test")
print("EXPECTED_ROLE_DISTANCES:",
      expected_role_distances)
print("REGISTRATION_ROWS:",
      registration_rows)
print("FLAT_EDGE_TO_D:",
      {
          str(key): sorted(value)
          for key, value in flat_edge_to_D.items()
      })
print("D_IMAGE_SET:", sorted(D_images))
print("NATIVE_SPOKE_REGISTER:",
      sorted(native_spoke_register))
print("CHECKS:", checks)
print("FAILED_CHECK_COUNT:", len(failed))
print("FAILED_CHECKS:", failed)
print("THEOREM_PASS:", theorem_pass)
print(
    "CLASSIFICATION:",
    (
        "each_registered_flat_pentagram_edge_has_a_"
        "unique_native_triangle_tip_D_in_the_spoke_"
        "register_and_the_projected_K3_3_edges_have_"
        "exact_native_distance_roles_1x6_2x2_3x1"
        if theorem_pass
        else "flat_edge_triangle_tip_projection_failed"
    ),
)
print("D_IS_UNIQUE_TRIANGLE_COMPLETION:", theorem_pass)
print("D_IMAGES_EXACTLY_SPOKE_REGISTER:", theorem_pass)
print("Y1_IS_FORMAL_MIDPOINT_OF_FLAT_EDGE:", True)
print("D_TO_Y1_180_REQUIRES_REGISTERED_PULLBACK:", True)
print("PHYSICAL_GEOMETRY_CLAIM:", False)
print("MUTATION_PERFORMED:", False)
