#!/usr/bin/env python3

import itertools
import json

P08 = (
    "/data/data/com.termux/files/home/dev/cori/research/"
    "thalean_mechanics/papers/"
    "08-g60-receipt-packet-native-encounter"
)
SOURCE = P08 + (
    "/artifacts/json/"
    "g60_native_rosette_pipe_null_corollary_025.v1.json"
)
source = json.load(open(SOURCE))

I = ((1, 0), (0, 1))
R = ((0, -1), (1, 0))
R2 = ((-1, 0), (0, -1))
R3 = ((0, 1), (-1, 0))
S = ((1, 0), (0, -1))
D1 = ((0, 1), (1, 0))
D2 = ((0, -1), (-1, 0))

def mmul(a, b):
    return tuple(
        tuple(
            sum(a[i][k] * b[k][j] for k in range(2))
            for j in range(2)
        )
        for i in range(2)
    )

def apply(a, v):
    return (
        a[0][0] * v[0] + a[0][1] * v[1],
        a[1][0] * v[0] + a[1][1] * v[1],
    )

GRID_D8 = tuple(dict.fromkeys(
    (I, R, R2, R3) +
    tuple(mmul(m, S) for m in (I, R, R2, R3))
))

DIAMOND = (
    (0, 1),
    (1, 0),
    (0, -1),
    (-1, 0),
)

def matrix_permutation(matrix):
    return tuple(
        DIAMOND.index(apply(matrix, point))
        for point in DIAMOND
    )

grid_action = {
    matrix_permutation(matrix)
    for matrix in GRID_D8
}
grid_v4 = {
    matrix_permutation(matrix)
    for matrix in (I, R2, D1, D2)
}

V4 = ((0, 0), (1, 0), (0, 1), (1, 1))

def add(left, right):
    return (
        left[0] ^ right[0],
        left[1] ^ right[1],
    )

def phi(v):
    x, y = v
    return (x ^ y, y)

def leaf_action(element):
    shift, side = element
    return tuple(
        V4.index(add(shift, phi(v) if side else v))
        for v in V4
    )

ABSTRACT_D8 = tuple(
    (v, side)
    for side in (0, 1)
    for v in V4
)
abstract_action = {
    leaf_action(g)
    for g in ABSTRACT_D8
}
abstract_v4 = {
    leaf_action((v, 0))
    for v in V4
}

def conjugate(p, labeling):
    inverse = [0] * 4
    for source_index, target_index in enumerate(labeling):
        inverse[target_index] = source_index
    return tuple(
        labeling[p[inverse[target_index]]]
        for target_index in range(4)
    )

equivariant_labelings = []
for labeling in itertools.permutations(range(4)):
    transported_full = {
        conjugate(p, labeling)
        for p in abstract_action
    }
    transported_v4 = {
        conjugate(p, labeling)
        for p in abstract_v4
    }
    if (
        transported_full == grid_action
        and transported_v4 == grid_v4
    ):
        equivariant_labelings.append(labeling)

full_orbit = {
    p[0]
    for p in grid_action
}
point_stabilizer = {
    p for p in grid_action
    if p[0] == 0
}

v4_orbit = {
    p[0]
    for p in grid_v4
}
v4_nonidentity_fixed_counts = sorted(
    sum(p[i] == i for i in range(4))
    for p in grid_v4
    if p != tuple(range(4))
)

ARCS = tuple(
    (leaf, side)
    for side in (0, 1)
    for leaf in V4
)
projection_fibers = {
    leaf: tuple(
        arc for arc in ARCS
        if arc[0] == leaf
    )
    for leaf in V4
}

section_0 = {
    (leaf, 0) for leaf in V4
}
section_1 = {
    (leaf, 1) for leaf in V4
}
projected_0 = {
    arc[0] for arc in section_0
}
projected_1 = {
    arc[0] for arc in section_1
}

checks = {
    "source_025_audit_pass": source["audit_pass"] is True,
    "diamond_vertex_count_4": len(DIAMOND) == 4,
    "diamond_full_action_order_8": len(grid_action) == 8,
    "diamond_full_action_transitive": len(full_orbit) == 4,
    "diamond_point_stabilizer_order_2": (
        len(point_stabilizer) == 2
    ),
    "diamond_not_regular_D8_set": (
        len(full_orbit) == 4
        and len(point_stabilizer) == 2
    ),
    "diamond_v4_action_order_4": len(grid_v4) == 4,
    "diamond_v4_action_transitive": len(v4_orbit) == 4,
    "diamond_v4_action_free": (
        v4_nonidentity_fixed_counts == [0, 0, 0]
    ),
    "abstract_leaf_action_is_D8_order_8": (
        len(abstract_action) == 8
    ),
    "abstract_leaf_v4_order_4": len(abstract_v4) == 4,
    "named_action_equivariant_labeling_exists": (
        len(equivariant_labelings) > 0
    ),
    "eight_arcs_project_two_to_one_to_leaves": all(
        len(fiber) == 2
        for fiber in projection_fibers.values()
    ),
    "both_sections_have_same_diamond_projection": (
        projected_0 == projected_1 == set(V4)
    ),
    "diamond_cannot_select_arc_side": (
        projected_0 == projected_1
    ),
}

failed = [
    name for name, passed in checks.items()
    if not passed
]
theorem_pass = not failed

print("PACKET: g900_pink_diamond_role_probe_026")
print("MODE: four-vertex orbit and side-forgetting quotient test")
print("DIAMOND_VERTICES:", DIAMOND)
print("DIAMOND_D8_ACTION_ORDER:", len(grid_action))
print("DIAMOND_ORBIT_SIZE:", len(full_orbit))
print("DIAMOND_POINT_STABILIZER_ORDER:", len(point_stabilizer))
print("DIAMOND_V4_ACTION_ORDER:", len(grid_v4))
print("DIAMOND_V4_ORBIT_SIZE:", len(v4_orbit))
print(
    "DIAMOND_V4_NONIDENTITY_FIXED_COUNTS:",
    v4_nonidentity_fixed_counts,
)
print(
    "EQUIVARIANT_LEAF_DIAMOND_LABELING_COUNT:",
    len(equivariant_labelings),
)
print("PROJECTION_FIBER_SIZES:", {
    str(k): len(v)
    for k, v in projection_fibers.items()
})
print("SECTION_PROJECTIONS_EQUAL:", projected_0 == projected_1)
print("CHECKS:", checks)
print("FAILED_CHECK_COUNT:", len(failed))
print("FAILED_CHECKS:", failed)
print("THEOREM_PASS:", theorem_pass)
print(
    "CLASSIFICATION:",
    (
        "pink_diamond_is_the_four_leaf_side_forgetting_"
        "quotient_of_the_eight_arc_rosette_not_the_full_"
        "eight_chart_fiber_or_an_absolute_section"
        if theorem_pass
        else "pink_diamond_role_not_identified"
    ),
)
print("PINK_DIAMOND_IS_FULL_EIGHT_CHART_FIBER:", False)
print("PINK_DIAMOND_SELECTS_ONE_SECTION:", False)
print("PINK_DIAMOND_IS_FOUR_LEAF_QUOTIENT:", theorem_pass)
print("ABSOLUTE_VERTEX_LABELING_SELECTED:", False)
print("PHYSICAL_CLAIM:", False)
print("MUTATION_PERFORMED:", False)
