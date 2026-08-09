#!/usr/bin/env python3

import contextlib
import io
import itertools
import pathlib
import runpy
from collections import Counter

SOURCE_068 = (
    pathlib.Path(__file__).resolve().parent
    / "compute_g900_six_register_k33_cross_duad_family_068.py"
)

capture = io.StringIO()

with contextlib.redirect_stdout(capture):
    namespace = runpy.run_path(str(SOURCE_068))

data = namespace["data"]
six_points = tuple(namespace["six_points"])
splits = tuple(namespace["splits"])
state_to_duad = namespace["state_to_duad"]
duad_to_state = namespace["duad_to_state"]
syntheme_rows = namespace["syntheme_rows"]
graph_distance = namespace["graph_distance"]

duad_to_syntheme = {
    duad: row["syntheme_id"]
    for row in syntheme_rows
    for duad in row["duads"]
}

syntheme_duads = {
    row["syntheme_id"]: tuple(row["duads"])
    for row in syntheme_rows
}

def duad(left, right):
    return tuple(sorted((int(left), int(right))))

def state_of(pair):
    return duad_to_state[duad(*pair)]

def pair_distance(pair_of_duads):
    left_state = state_of(pair_of_duads[0])
    right_state = state_of(pair_of_duads[1])

    return graph_distance(left_state, right_state)

frame_rows = []

for split_id, split in enumerate(splits):
    side_0 = frozenset(split[0])
    side_1 = frozenset(split[1])

    for closure_side_id, closure_side in enumerate(
        (side_0, side_1)
    ):
        opposite_side = (
            side_1
            if closure_side_id == 0
            else side_0
        )

        for closure_pair in itertools.combinations(
            sorted(closure_side),
            2,
        ):
            closure_pair = duad(*closure_pair)
            closure_state = state_of(closure_pair)
            closure_syntheme_id = duad_to_syntheme[
                closure_pair
            ]

            closure_syntheme_duads = syntheme_duads[
                closure_syntheme_id
            ]

            same_side_mates = tuple(
                pair
                for pair in closure_syntheme_duads
                if pair != closure_pair
                and set(pair).issubset(opposite_side)
            )

            cross_mates = tuple(
                pair
                for pair in closure_syntheme_duads
                if len(set(pair) & closure_side) == 1
                and len(set(pair) & opposite_side) == 1
            )

            valid_syntheme_shape = (
                len(same_side_mates) == 1
                and len(cross_mates) == 1
            )

            if not valid_syntheme_shape:
                frame_rows.append({
                    "split_id": split_id,
                    "closure_side_id": closure_side_id,
                    "closure_duad": closure_pair,
                    "valid_syntheme_shape": False,
                })
                continue

            opposite_pair = same_side_mates[0]
            fixed_cross_duad = cross_mates[0]

            closure_residual = tuple(sorted(
                closure_side - set(closure_pair)
            ))
            opposite_residual = tuple(sorted(
                opposite_side - set(opposite_pair)
            ))

            if (
                len(closure_residual) != 1
                or len(opposite_residual) != 1
            ):
                frame_rows.append({
                    "split_id": split_id,
                    "closure_side_id": closure_side_id,
                    "closure_duad": closure_pair,
                    "valid_syntheme_shape": False,
                })
                continue

            fixed_closure_point = closure_residual[0]
            fixed_opposite_point = opposite_residual[0]

            residual_cross_duad = duad(
                fixed_closure_point,
                fixed_opposite_point,
            )

            a, b = closure_pair
            c, e = opposite_pair
            f = fixed_closure_point
            d = fixed_opposite_point

            reflection = {
                a: b,
                b: a,
                c: e,
                e: c,
                d: d,
                f: f,
            }

            root_pair = tuple(sorted((
                duad(a, d),
                duad(b, d),
            )))

            boundary_star_pair = tuple(sorted((
                duad(c, f),
                duad(e, f),
            )))

            corner_pair_0 = tuple(sorted((
                duad(a, c),
                duad(b, e),
            )))

            corner_pair_1 = tuple(sorted((
                duad(a, e),
                duad(b, c),
            )))

            corner_distance_0 = pair_distance(corner_pair_0)
            corner_distance_1 = pair_distance(corner_pair_1)

            root_pair_distance = pair_distance(root_pair)
            boundary_star_distance = pair_distance(
                boundary_star_pair
            )

            fixed_cross_matches_residual = (
                fixed_cross_duad == residual_cross_duad
            )

            reflected_cross_orbits = (
                (fixed_cross_duad,),
                root_pair,
                boundary_star_pair,
                corner_pair_0,
                corner_pair_1,
            )

            cross_duads = {
                duad(left, right)
                for left in closure_side
                for right in opposite_side
            }

            orbit_union = {
                pair
                for orbit in reflected_cross_orbits
                for pair in orbit
            }

            frame_rows.append({
                "split_id": split_id,
                "closure_side_id": closure_side_id,
                "closure_duad": closure_pair,
                "closure_state": closure_state,
                "closure_syntheme_id":
                    closure_syntheme_id,
                "opposite_same_side_duad":
                    opposite_pair,
                "fixed_cross_duad":
                    fixed_cross_duad,
                "fixed_closure_point": f,
                "fixed_opposite_point": d,
                "reflection": reflection,
                "root_pair": root_pair,
                "root_pair_distance":
                    root_pair_distance,
                "boundary_star_pair":
                    boundary_star_pair,
                "boundary_star_distance":
                    boundary_star_distance,
                "corner_pair_0": corner_pair_0,
                "corner_pair_0_distance":
                    corner_distance_0,
                "corner_pair_1": corner_pair_1,
                "corner_pair_1_distance":
                    corner_distance_1,
                "corner_distance_multiset":
                    tuple(sorted((
                        corner_distance_0,
                        corner_distance_1,
                    ))),
                "reflected_cross_orbits":
                    reflected_cross_orbits,
                "fixed_cross_matches_residual":
                    fixed_cross_matches_residual,
                "reflection_is_involution":
                    all(
                        reflection[reflection[point]]
                        == point
                        for point in six_points
                    ),
                "reflection_cycle_profile":
                    tuple(sorted(Counter(
                        1 if reflection[point] == point
                        else 2
                        for point in six_points
                    ).elements())),
                "cross_orbits_partition_K33_edges":
                    orbit_union == cross_duads
                    and sum(
                        len(orbit)
                        for orbit in reflected_cross_orbits
                    ) == 9,
                "valid_syntheme_shape": True,
            })

valid_rows = tuple(
    row
    for row in frame_rows
    if row["valid_syntheme_shape"]
)

corner_distance_profile = Counter(
    row["corner_distance_multiset"]
    for row in valid_rows
)

root_distance_profile = Counter(
    row["root_pair_distance"]
    for row in valid_rows
)

boundary_star_distance_profile = Counter(
    row["boundary_star_distance"]
    for row in valid_rows
)

reflection_profile = Counter(
    row["reflection_cycle_profile"]
    for row in valid_rows
)

checks = {
    "source_068_exists":
        SOURCE_068.is_file(),
    "source_audit_pass":
        data.get("audit_pass") is True,
    "split_count_10":
        len(splits) == 10,
    "decorated_frame_count_60":
        len(frame_rows) == 60,
    "every_closure_has_valid_AB_CE_DF_syntheme_shape":
        len(valid_rows) == 60,
    "every_fixed_cross_duad_is_residual_DF":
        all(
            row["fixed_cross_matches_residual"]
            for row in valid_rows
        ),
    "every_reflection_is_involution":
        all(
            row["reflection_is_involution"]
            for row in valid_rows
        ),
    "every_reflection_has_two_fixed_two_swapped_pairs":
        reflection_profile
        == Counter({(1, 1, 2, 2, 2, 2): 60}),
    "every_reflection_partitions_nine_cross_duads_1_2_2_2_2":
        all(
            row["cross_orbits_partition_K33_edges"]
            and tuple(sorted(
                len(orbit)
                for orbit in row["reflected_cross_orbits"]
            )) == (1, 2, 2, 2, 2)
            for row in valid_rows
        ),
    "root_pair_always_native_distance_2":
        root_distance_profile == Counter({2: 60}),
    "boundary_star_pair_always_native_distance_2":
        boundary_star_distance_profile
        == Counter({2: 60}),
    "corner_pairs_have_uniform_distance_multiset":
        len(corner_distance_profile) == 1,
}

failed = [
    name
    for name, passed in checks.items()
    if not passed
]

theorem_pass = not failed

print("PACKET: g900_k33_closure_syntheme_reflection_069")
print("MODE: exhaustive split-plus-closure syntheme frame census")
print("SPLIT_COUNT:", len(splits))
print("DECORATED_FRAME_COUNT:", len(frame_rows))
print("VALID_FRAME_COUNT:", len(valid_rows))
print(
    "CORNER_DISTANCE_MULTISET_PROFILE:",
    dict(sorted(corner_distance_profile.items())),
)
print(
    "ROOT_PAIR_DISTANCE_PROFILE:",
    dict(sorted(root_distance_profile.items())),
)
print(
    "BOUNDARY_STAR_DISTANCE_PROFILE:",
    dict(sorted(boundary_star_distance_profile.items())),
)
print(
    "REFLECTION_CYCLE_PROFILE:",
    dict(sorted(reflection_profile.items())),
)
print("FRAME_PREVIEW:", valid_rows[:12])
print("CHECKS:", checks)
print("FAILED_CHECK_COUNT:", len(failed))
print("FAILED_CHECKS:", failed)
print("THEOREM_PASS:", theorem_pass)
print(
    "CLASSIFICATION:",
    (
        "for_every_intrinsic_three_plus_three_K3_3_carrier_"
        "and_every_same_side_closure_duad_the_native_"
        "synthematic_total_uniquely_completes_AB_to_AB_CE_DF_"
        "and_derives_a_reflection_with_cross_edge_orbit_"
        "profile_one_plus_two_plus_two_plus_two_plus_two"
        if theorem_pass
        else
        "K3_3_closure_syntheme_reflection_not_derived"
    ),
)
print("AB_CE_DF_SYNTHEME_COMPLETION_DERIVED:",
      theorem_pass)
print("DRAWING_REFLECTION_DERIVED:", theorem_pass)
print("FIXED_CROSS_AXIS_DF_DERIVED:", theorem_pass)
print("CROSS_EDGE_ORBIT_PROFILE:", (1, 2, 2, 2, 2))
print("DRAWING_FIVE_FOUR_SPLIT_DERIVED:", False)
print("CORNER_PAIR_SELECTION_DERIVED:", False)
print("HAND_DRAWING_LABELS_USED:", False)
print("PHYSICAL_CLAIM:", False)
print("MUTATION_PERFORMED:", False)
