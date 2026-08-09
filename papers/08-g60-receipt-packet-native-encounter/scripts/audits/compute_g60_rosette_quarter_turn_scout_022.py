#!/usr/bin/env python3

from collections import Counter

I = ((1, 0), (0, 1))
R = ((0, -1), (1, 0))
R2 = ((-1, 0), (0, -1))
R3 = ((0, 1), (-1, 0))
S = ((1, 0), (0, -1))

def mul(a, b):
    return tuple(
        tuple(
            sum(a[i][k] * b[k][j] for k in range(2))
            for j in range(2)
        )
        for i in range(2)
    )

def power(a, n):
    out = I
    for _ in range(n):
        out = mul(out, a)
    return out

def order(a):
    for n in range(1, 9):
        if power(a, n) == I:
            return n
    return None

def det(a):
    return a[0][0] * a[1][1] - a[0][1] * a[1][0]

def trace(a):
    return a[0][0] + a[1][1]

rotations = (I, R, R2, R3)
reflections = tuple(mul(power(R, k), S) for k in range(4))
GRID_D8 = tuple(dict.fromkeys(rotations + reflections))

profile = Counter(order(g) for g in GRID_D8)
order4 = tuple(g for g in GRID_D8 if order(g) == 4)
quarter_turn_images = tuple(
    (
        g,
        (
            g[0][0] * 1 + g[0][1] * 0,
            g[1][0] * 1 + g[1][1] * 0,
        ),
    )
    for g in order4
)

directions = ((1, 0), (0, 1), (-1, 0), (0, -1))
r_orbit = []
v = (1, 0)
for _ in range(4):
    r_orbit.append(v)
    v = (
        R[0][0] * v[0] + R[0][1] * v[1],
        R[1][0] * v[0] + R[1][1] * v[1],
    )

# An abstract D8 isomorphism to the grid is determined by:
# one of two order-four images for r, and one of four reflections for s.
faithful_grid_identification_count = (
    len(order4) * len(reflections)
)

checks = {
    "grid_symmetry_group_order_8": len(GRID_D8) == 8,
    "grid_group_order_profile_D8": dict(profile) == {
        1: 1,
        2: 5,
        4: 2,
    },
    "exactly_two_order_four_elements": len(order4) == 2,
    "order_four_elements_orientation_preserving": all(
        det(g) == 1 for g in order4
    ),
    "order_four_elements_trace_zero": all(
        trace(g) == 0 for g in order4
    ),
    "order_four_elements_are_inverse_pair": (
        mul(order4[0], order4[1]) == I
    ),
    "quarter_turn_direction_orbit_size_4": (
        len(set(r_orbit)) == 4
    ),
    "quarter_turn_visits_grid_axes": (
        set(r_orbit) == set(directions)
    ),
    "faithful_grid_identification_count_8": (
        faithful_grid_identification_count == 8
    ),
}

failed = [
    name for name, passed in checks.items()
    if not passed
]

theorem_pass = not failed

print("PACKET: g900_rosette_quarter_turn_probe_022")
print("MODE: exact square-grid orthogonal realization probe")
print("GRID_D8_ORDER:", len(GRID_D8))
print("GRID_D8_ORDER_PROFILE:", dict(sorted(profile.items())))
print("ORDER4_ELEMENT_COUNT:", len(order4))
print("ORDER4_DETERMINANTS:", [det(g) for g in order4])
print("ORDER4_TRACES:", [trace(g) for g in order4])
print("ORDER4_IMAGES_OF_EAST:", quarter_turn_images)
print("QUARTER_TURN_DIRECTION_ORBIT:", r_orbit)
print(
    "FAITHFUL_GRID_IDENTIFICATION_COUNT:",
    faithful_grid_identification_count,
)
print("CHECKS:", checks)
print("FAILED_CHECK_COUNT:", len(failed))
print("FAILED_CHECKS:", failed)
print("THEOREM_PASS:", theorem_pass)
print(
    "CLASSIFICATION:",
    (
        "faithful_square_grid_realization_forces_"
        "the_two_order4_elements_to_be_opposite_quarter_turns"
        if theorem_pass
        else "quarter_turn_geometry_not_forced"
    ),
)
print("NINETY_DEGREE_ORBIT_SPACING_DERIVED:", theorem_pass)
print("CIRCULAR_ARC_SHAPE_DERIVED:", False)
print("CLOCKWISE_ORIENTATION_SELECTED:", False)
print("ABSOLUTE_ARC_LABELING_SELECTED:", False)
print("NULL_CENTER_IDENTIFIED:", False)
print("MUTATION_PERFORMED:", False)
