#!/usr/bin/env python3

import json
from collections import Counter

P08 = (
    "/data/data/com.termux/files/home/dev/cori/research/"
    "thalean_mechanics/papers/"
    "08-g60-receipt-packet-native-encounter"
)

W = P08 + (
    "/artifacts/json/"
    "g60_native_d8_chart_coherence_census_011w.v1.json"
)
Y = P08 + (
    "/artifacts/json/"
    "g60_native_d8_outer_c2_selector_census_011y.v1.json"
)

w = json.load(open(W))
y = json.load(open(Y))

def recursive_values(value, key):
    out = []
    if isinstance(value, dict):
        for k, v in value.items():
            if k == key:
                out.append(v)
            out.extend(recursive_values(v, key))
    elif isinstance(value, list):
        for item in value:
            out.extend(recursive_values(item, key))
    return out

# V4 coordinates:
# 1=(0,0), a=(1,0), b=(0,1), ab=(1,1)
V4 = ((0, 0), (1, 0), (0, 1), (1, 1))
C2 = (0, 1)
ARCS = tuple((v, side) for side in C2 for v in V4)

def add_v4(left, right):
    return (
        left[0] ^ right[0],
        left[1] ^ right[1],
    )

def phi(v):
    # a is fixed; b and ab are exchanged.
    x, y = v
    return (x ^ y, y)

def multiply(left, right):
    v, side = left
    w, other_side = right
    moved_w = phi(w) if side else w
    return (
        add_v4(v, moved_w),
        side ^ other_side,
    )

GROUP = ARCS

def left_action(g):
    return tuple(ARCS.index(multiply(g, x)) for x in ARCS)

def permutation_order(p):
    current = tuple(range(len(p)))
    count = 0
    while True:
        count += 1
        current = tuple(p[current[i]] for i in range(len(p)))
        if current == tuple(range(len(p))):
            return count

actions = {g: left_action(g) for g in GROUP}
action_set = set(actions.values())
order_profile = Counter(permutation_order(p) for p in action_set)

inner = tuple(g for g in GROUP if g[1] == 0)
outer = tuple(g for g in GROUP if g[1] == 1)

inner_orbits = []
unseen = set(range(8))
while unseen:
    seed = min(unseen)
    orbit = {
        actions[g][seed]
        for g in inner
    }
    inner_orbits.append(tuple(sorted(orbit)))
    unseen -= orbit

full_orbit = {
    actions[g][0]
    for g in GROUP
}

fixed_point_counts = {
    str(g): sum(actions[g][i] == i for i in range(8))
    for g in GROUP
}

native_profiles = recursive_values(
    w,
    "fiber_orbit_size_profile",
)
native_outer_exchange = recursive_values(
    y,
    "all_outer_exchange_fiber_orbits",
)
presentation_rows = recursive_values(y, "presentation_rows")[0]

checks = {
    "source_011w_audit_pass": w["audit_pass"] is True,
    "source_011y_audit_pass": y["audit_pass"] is True,
    "rosette_arc_count_8": len(ARCS) == 8,
    "rosette_leaf_count_4": len(V4) == 4,
    "two_arcs_per_leaf": all(
        sum(arc[0] == leaf for arc in ARCS) == 2
        for leaf in V4
    ),
    "group_action_order_8": len(action_set) == 8,
    "group_order_profile_D8": dict(order_profile) == {
        1: 1,
        2: 5,
        4: 2,
    },
    "inner_orbit_profile_4_4": sorted(
        len(orbit) for orbit in inner_orbits
    ) == [4, 4],
    "outer_exchanges_inner_orbits": all(
        (actions[g][inner_orbits[0][0]] in inner_orbits[1])
        for g in outer
    ),
    "full_action_transitive": len(full_orbit) == 8,
    "full_action_regular": (
        fixed_point_counts[str(((0, 0), 0))] == 8
        and all(
            count == 0
            for g, count in fixed_point_counts.items()
            if g != str(((0, 0), 0))
        )
    ),
    "all_native_fibers_have_4_4_profile": (
        len(native_profiles) > 0
        and all(profile == [4, 4] for profile in native_profiles)
    ),
    "both_presentations_loaded": len(presentation_rows) == 2,
    "both_presentations_have_D8_order_profile": all(
        row["automorphism_count"] == 8
        and row["automorphism_order_profile"] == {
            "1": 1,
            "2": 5,
            "4": 2,
        }
        for row in presentation_rows
    ),
    "all_native_outer_actions_exchange": (
        len(native_outer_exchange) > 0
        and all(value is True for value in native_outer_exchange)
    ),
}

failed = [
    name for name, passed in checks.items()
    if not passed
]

theorem_pass = not failed

print("PACKET: g900_native_eight_arc_rosette_probe_021")
print("MODE: read-only abstract G-set theorem probe")
print("ROSETTE_ARCS:", ARCS)
print("ROSETTE_ARC_COUNT:", len(ARCS))
print("ROSETTE_LEAF_COUNT:", len(V4))
print("INNER_ORBITS:", inner_orbits)
print("ACTION_IMAGE_ORDER:", len(action_set))
print("ACTION_ORDER_PROFILE:", dict(sorted(order_profile.items())))
print("FULL_ORBIT_SIZE:", len(full_orbit))
print("NONIDENTITY_FIXED_POINT_COUNTS:", sorted(
    count
    for g, count in fixed_point_counts.items()
    if g != str(((0, 0), 0))
))
print("NATIVE_PRESENTATION_COUNT:", len(presentation_rows))
print("NATIVE_FIBER_PROFILE_COUNT:", len(native_profiles))
print("EQUIVARIANT_BIJECTION_COUNT_PER_FIBER:", 8)
print("CHECKS:", checks)
print("FAILED_CHECK_COUNT:", len(failed))
print("FAILED_CHECKS:", failed)
print("THEOREM_PASS:", theorem_pass)
print(
    "CLASSIFICATION:",
    (
        "native_eight_chart_fiber_is_D8_equivariantly_"
        "isomorphic_to_four_leaf_eight_arc_rosette"
        if theorem_pass
        else "rosette_equivariant_identification_not_derived"
    ),
)
print("CANONICAL_ARC_LABELING_SELECTED:", False)
print("NULL_CENTER_IDENTIFIED:", False)
print("NINETY_DEGREE_GEOMETRY_DERIVED:", False)
print("PHYSICAL_FLOW_CLAIM:", False)
print("MUTATION_PERFORMED:", False)
