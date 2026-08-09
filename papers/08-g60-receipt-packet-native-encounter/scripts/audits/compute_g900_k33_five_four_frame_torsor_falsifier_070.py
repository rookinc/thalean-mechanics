#!/usr/bin/env python3

import contextlib
import io
import pathlib
import runpy
from collections import Counter

SOURCE_069 = (
    pathlib.Path(__file__).resolve().parent
    / "compute_g900_k33_closure_syntheme_reflection_069.py"
)

capture = io.StringIO()

with contextlib.redirect_stdout(capture):
    namespace = runpy.run_path(str(SOURCE_069))

data = namespace["data"]
splits = tuple(namespace["splits"])
valid_rows = tuple(namespace["valid_rows"])
duad_to_state = namespace["duad_to_state"]

source_068 = namespace["namespace"]
six_register_actions = tuple(
    source_068["six_register_actions"]
)

def duad(left, right):
    return tuple(sorted((int(left), int(right))))

def canonical_split(left):
    left = frozenset(left)
    all_points = frozenset(
        point
        for split in splits
        for side in split
        for point in side
    )
    right = all_points - left

    return tuple(sorted((
        tuple(sorted(left)),
        tuple(sorted(right)),
    )))

def image_duad(pair, permutation):
    return duad(
        permutation[pair[0]],
        permutation[pair[1]],
    )

candidate_rows = []

for frame_id, row in enumerate(valid_rows):
    split = splits[row["split_id"]]
    closure_side = tuple(sorted(
        split[row["closure_side_id"]]
    ))

    fixed_axis = row["fixed_cross_duad"]
    root_pair = tuple(row["root_pair"])
    boundary_star_pair = tuple(
        row["boundary_star_pair"]
    )
    corner_pairs = (
        tuple(row["corner_pair_0"]),
        tuple(row["corner_pair_1"]),
    )

    for corner_choice in (0, 1):
        selected_corner = corner_pairs[corner_choice]
        rejected_corner = corner_pairs[corner_choice ^ 1]

        interior_five = tuple(sorted(
            (fixed_axis,)
            + root_pair
            + selected_corner
        ))

        boundary_four = tuple(sorted(
            boundary_star_pair
            + rejected_corner
        ))

        candidate_rows.append({
            "candidate_id": len(candidate_rows),
            "frame_id": frame_id,
            "split_id": row["split_id"],
            "split": split,
            "closure_side": closure_side,
            "closure_duad": row["closure_duad"],
            "opposite_duad":
                row["opposite_same_side_duad"],
            "fixed_axis": fixed_axis,
            "corner_choice": corner_choice,
            "selected_corner_pair":
                selected_corner,
            "rejected_corner_pair":
                rejected_corner,
            "interior_five": interior_five,
            "boundary_four": boundary_four,
            "interior_states": tuple(sorted(
                duad_to_state[pair]
                for pair in interior_five
            )),
            "boundary_states": tuple(sorted(
                duad_to_state[pair]
                for pair in boundary_four
            )),
        })

def candidate_key(row):
    return (
        row["split"],
        row["closure_side"],
        row["closure_duad"],
        row["interior_five"],
        row["boundary_four"],
    )

candidate_id_by_key = {
    candidate_key(row): row["candidate_id"]
    for row in candidate_rows
}

def image_candidate(row, permutation):
    image_closure_side = tuple(sorted(
        permutation[point]
        for point in row["closure_side"]
    ))

    image_split = canonical_split(
        image_closure_side
    )

    image_closure_duad = image_duad(
        row["closure_duad"],
        permutation,
    )

    image_interior = tuple(sorted(
        image_duad(pair, permutation)
        for pair in row["interior_five"]
    ))

    image_boundary = tuple(sorted(
        image_duad(pair, permutation)
        for pair in row["boundary_four"]
    ))

    return (
        image_split,
        image_closure_side,
        image_closure_duad,
        image_interior,
        image_boundary,
    )

candidate_actions = []

for permutation in six_register_actions:
    candidate_permutation = tuple(
        candidate_id_by_key[
            image_candidate(row, permutation)
        ]
        for row in candidate_rows
    )

    candidate_actions.append(candidate_permutation)

distinct_candidate_actions = set(
    candidate_actions
)

base_orbit = {
    permutation[0]
    for permutation in distinct_candidate_actions
}

base_stabilizer = {
    permutation
    for permutation in distinct_candidate_actions
    if permutation[0] == 0
}

frame_candidate_count = Counter(
    row["frame_id"]
    for row in candidate_rows
)

interior_size_profile = Counter(
    len(row["interior_five"])
    for row in candidate_rows
)

boundary_size_profile = Counter(
    len(row["boundary_four"])
    for row in candidate_rows
)

interior_boundary_intersection_profile = Counter(
    len(
        set(row["interior_five"])
        & set(row["boundary_four"])
    )
    for row in candidate_rows
)

interior_boundary_union_profile = Counter(
    len(
        set(row["interior_five"])
        | set(row["boundary_four"])
    )
    for row in candidate_rows
)

checks = {
    "source_069_exists":
        SOURCE_069.is_file(),
    "source_audit_pass":
        data.get("audit_pass") is True,
    "base_frame_count_60":
        len(valid_rows) == 60,
    "two_candidates_per_base_frame":
        frame_candidate_count
        == Counter({
            frame_id: 2
            for frame_id in range(60)
        }),
    "complete_candidate_count_120":
        len(candidate_rows) == 120,
    "candidate_keys_are_distinct":
        len(candidate_id_by_key) == 120,
    "every_interior_has_five_edges":
        interior_size_profile == Counter({5: 120}),
    "every_boundary_has_four_edges":
        boundary_size_profile == Counter({4: 120}),
    "interior_and_boundary_are_disjoint":
        interior_boundary_intersection_profile
        == Counter({0: 120}),
    "interior_and_boundary_partition_K33_nine":
        interior_boundary_union_profile
        == Counter({9: 120}),
    "native_action_count_120":
        len(six_register_actions) == 120,
    "all_candidate_actions_are_distinct":
        len(distinct_candidate_actions) == 120,
    "candidate_action_is_transitive":
        base_orbit == set(range(120)),
    "candidate_action_is_free":
        len(base_stabilizer) == 1,
    "candidate_action_is_regular":
        len(distinct_candidate_actions)
        == len(candidate_rows)
        == len(base_orbit)
        == 120,
}

failed = [
    name
    for name, passed in checks.items()
    if not passed
]

theorem_pass = not failed

print("PACKET: g900_k33_five_four_frame_torsor_070")
print("MODE: exact complete decorated-frame orbit census")
print("BASE_FRAME_COUNT:", len(valid_rows))
print("CANDIDATES_PER_FRAME_PROFILE:", dict(sorted(
    Counter(frame_candidate_count.values()).items()
)))
print("COMPLETE_CANDIDATE_COUNT:", len(candidate_rows))
print("NATIVE_ACTION_COUNT:", len(
    distinct_candidate_actions
))
print("BASE_ORBIT_SIZE:", len(base_orbit))
print("BASE_STABILIZER_ORDER:", len(base_stabilizer))
print("INTERIOR_SIZE_PROFILE:", dict(sorted(
    interior_size_profile.items()
)))
print("BOUNDARY_SIZE_PROFILE:", dict(sorted(
    boundary_size_profile.items()
)))
print(
    "INTERIOR_BOUNDARY_INTERSECTION_PROFILE:",
    dict(sorted(
        interior_boundary_intersection_profile.items()
    )),
)
print(
    "INTERIOR_BOUNDARY_UNION_PROFILE:",
    dict(sorted(
        interior_boundary_union_profile.items()
    )),
)
print("CANDIDATE_PREVIEW:", candidate_rows[:12])
print("CHECKS:", checks)
print("FAILED_CHECK_COUNT:", len(failed))
print("FAILED_CHECKS:", failed)
print("THEOREM_PASS:", theorem_pass)
print(
    "CLASSIFICATION:",
    (
        "the_sixty_intrinsic_split_closure_reflection_frames_"
        "each_have_exactly_two_complementary_five_four_corner_"
        "placements_and_the_resulting_one_hundred_twenty_"
        "complete_K3_3_frames_form_a_free_transitive_torsor_"
        "for_the_full_native_order_120_symmetry_group"
        if theorem_pass
        else
        "complete_K3_3_five_four_frame_torsor_not_derived"
    ),
)
print("FIVE_FOUR_FRAME_FAMILY_DERIVED:", theorem_pass)
print("FIVE_FOUR_FRAME_COUNT:", len(candidate_rows))
print("NATIVE_SYMMETRY_ACTION_IS_FREE:", theorem_pass)
print("NATIVE_SYMMETRY_ACTION_IS_TRANSITIVE:", theorem_pass)
print("COMPLETE_FRAME_IS_NATIVE_SYMMETRY_TORSOR:", theorem_pass)
print("CANONICAL_COMPLETE_FRAME_SELECTED:", False)
print("HAND_DRAWING_SELECTS_ONE_TORSOR_POINT:", theorem_pass)
print("NUMERIC_ANGLE_VALUES_DERIVED:", False)
print("PHYSICAL_CLAIM:", False)
print("MUTATION_PERFORMED:", False)
