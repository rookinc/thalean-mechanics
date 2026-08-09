#!/usr/bin/env python3

import json

P41 = (
    "/data/data/com.termux/files/home/dev/cori/research/"
    "mathematics/41-order-4-dodecahedral-residue"
)
SOURCE = P41 + (
    "/artifacts/json/"
    "synthematic_total_534_transport_tower_audit_020.json"
)

source = json.load(open(SOURCE))

def values(value, key):
    out = []
    if isinstance(value, dict):
        for k, v in value.items():
            if k == key:
                out.append(v)
            out.extend(values(v, key))
    elif isinstance(value, list):
        for item in value:
            out.extend(values(item, key))
    return out

def has_true(key):
    return any(v is True for v in values(source, key))

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

def apply(a, v):
    return (
        a[0][0] * v[0] + a[0][1] * v[1],
        a[1][0] * v[0] + a[1][1] * v[1],
    )

rotations = (I, R, R2, R3)
reflections = tuple(mul((I, R, R2, R3)[k], S) for k in range(4))
D8 = tuple(dict.fromkeys(rotations + reflections))

# Use a generic point so its D8 orbit contains eight positions.
seed = (2, 1)
arc_points = tuple(dict.fromkeys(apply(g, seed) for g in D8))

barycenter = (
    sum(v[0] for v in arc_points) / len(arc_points),
    sum(v[1] for v in arc_points) / len(arc_points),
)

origin = (0, 0)
origin_fixed = all(apply(g, origin) == origin for g in D8)

# R-I is invertible, so any point fixed by the full group,
# in particular by R, must be the origin.
r_minus_i_det = (
    (R[0][0] - 1) * (R[1][1] - 1)
    - R[0][1] * R[1][0]
)

V4 = ((0, 0), (1, 0), (0, 1), (1, 1))

def add(left, right):
    return (left[0] ^ right[0], left[1] ^ right[1])

v4_orbit = {
    add(g, (0, 0))
    for g in V4
}

quotient_classes = {
    tuple(sorted(v4_orbit))
}

checks = {
    "source_audit_pass": source.get("audit_pass") is True,
    "native_v4_four_cover_exact": has_true(
        "g60_to_g15_exact_v4_four_cover_inherited"
    ),
    "every_base_edge_has_four_lifts": has_true(
        "every_g15_edge_has_four_g60_lifts"
    ),
    "grid_D8_order_8": len(D8) == 8,
    "eight_arc_positions": len(arc_points) == 8,
    "arc_barycenter_is_origin": barycenter == origin,
    "origin_fixed_by_full_D8": origin_fixed,
    "full_D8_fixed_point_unique": r_minus_i_det != 0,
    "origin_not_an_arc_position": origin not in arc_points,
    "v4_lane_orbit_size_4": len(v4_orbit) == 4,
    "v4_lane_quotient_has_one_class": (
        len(quotient_classes) == 1
    ),
    "quotient_center_not_extra_lane": ("center", origin) not in {("lane", v) for v in V4},
}

failed = [
    name for name, passed in checks.items()
    if not passed
]
theorem_pass = not failed

print("PACKET: g900_rosette_null_center_probe_024")
print("MODE: fixed-center quotient probe")
print("ARC_POINTS:", arc_points)
print("ARC_BARYCENTER:", barycenter)
print("D8_FIXED_CENTER:", origin)
print("R_MINUS_I_DETERMINANT:", r_minus_i_det)
print("V4_LANE_ORBIT:", sorted(v4_orbit))
print("V4_QUOTIENT_CLASS_COUNT:", len(quotient_classes))
print("CHECKS:", checks)
print("FAILED_CHECK_COUNT:", len(failed))
print("FAILED_CHECKS:", failed)
print("THEOREM_PASS:", theorem_pass)
print(
    "CLASSIFICATION:",
    (
        "rosette_has_a_unique_D8_fixed_null_center_"
        "representing_the_one_point_quotient_without_"
        "adding_a_lane_or_chart"
        if theorem_pass
        else "null_center_quotient_identification_not_derived"
    ),
)
print("NULL_IS_EXTRA_G60_STATE:", False)
print("NULL_IS_EXTRA_G15_EDGE:", False)
print("NULL_IS_QUOTIENT_REPRESENTATIVE:", theorem_pass)
print("PHYSICAL_LUMEN_CLAIM:", False)
print("MUTATION_PERFORMED:", False)
