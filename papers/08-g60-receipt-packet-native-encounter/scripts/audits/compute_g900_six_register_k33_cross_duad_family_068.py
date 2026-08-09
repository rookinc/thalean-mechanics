#!/usr/bin/env python3

import contextlib
import io
import itertools
import pathlib
import runpy
from collections import Counter

SOURCE_067 = (
    pathlib.Path(__file__).resolve().parent
    / "compute_g900_six_register_synthematic_total_067.py"
)

capture = io.StringIO()

with contextlib.redirect_stdout(capture):
    namespace = runpy.run_path(str(SOURCE_067))

data = namespace["data"]
six_points = tuple(namespace["six_points"])
vertices = tuple(namespace["vertices"])
state_to_duad = namespace["state_to_duad"]
state_to_syntheme = namespace["state_to_syntheme"]
syntheme_rows = namespace["syntheme_rows"]
graph_distance = namespace["graph_distance"]

source_066_namespace = namespace["namespace"]
state_actions = tuple(
    source_066_namespace["state_actions"]
)
six_register_actions = tuple(
    source_066_namespace["namespace"]["distinct_six_actions"]
)

duad_to_state = {
    duad: state
    for state, duad in state_to_duad.items()
}

def canonical_split(left):
    left = frozenset(left)
    right = frozenset(six_points) - left

    ordered = tuple(sorted((
        tuple(sorted(left)),
        tuple(sorted(right)),
    )))

    return ordered

splits = tuple(sorted({
    canonical_split(left)
    for left in itertools.combinations(six_points, 3)
}))

split_id_by_key = {
    split: split_id
    for split_id, split in enumerate(splits)
}

split_rows = []

for split_id, split in enumerate(splits):
    left = frozenset(split[0])
    right = frozenset(split[1])

    cross_duads = tuple(sorted(
        tuple(sorted((left_point, right_point)))
        for left_point in left
        for right_point in right
    ))

    same_side_duads = tuple(sorted(
        tuple(pair)
        for side in (left, right)
        for pair in itertools.combinations(sorted(side), 2)
    ))

    cross_states = tuple(sorted(
        duad_to_state[duad]
        for duad in cross_duads
    ))

    same_side_states = tuple(sorted(
        duad_to_state[duad]
        for duad in same_side_duads
    ))

    syntheme_cross_counts = {
        syntheme_id: sum(
            state in cross_states
            for state in row["native_states"]
        )
        for syntheme_id, row in enumerate(syntheme_rows)
    }

    cross_pair_distance_profile = Counter(
        graph_distance(left_state, right_state)
        for left_state, right_state
        in itertools.combinations(cross_states, 2)
    )

    same_side_pair_distance_profile = Counter(
        graph_distance(left_state, right_state)
        for left_state, right_state
        in itertools.combinations(same_side_states, 2)
    )

    cross_same_pair_distance_profile = Counter(
        graph_distance(cross_state, same_state)
        for cross_state in cross_states
        for same_state in same_side_states
    )

    endpoint_incidence_pair_count = sum(
        bool(set(left_duad) & set(right_duad))
        for left_duad, right_duad
        in itertools.combinations(cross_duads, 2)
    )

    disjoint_cross_pair_count = sum(
        set(left_duad).isdisjoint(right_duad)
        for left_duad, right_duad
        in itertools.combinations(cross_duads, 2)
    )

    split_rows.append({
        "split_id": split_id,
        "left_points": tuple(sorted(left)),
        "right_points": tuple(sorted(right)),
        "cross_duads": cross_duads,
        "cross_states": cross_states,
        "same_side_duads": same_side_duads,
        "same_side_states": same_side_states,
        "syntheme_cross_counts":
            dict(sorted(syntheme_cross_counts.items())),
        "syntheme_cross_count_profile":
            dict(sorted(Counter(
                syntheme_cross_counts.values()
            ).items())),
        "cross_pair_distance_profile":
            dict(sorted(cross_pair_distance_profile.items())),
        "same_side_pair_distance_profile":
            dict(sorted(same_side_pair_distance_profile.items())),
        "cross_same_pair_distance_profile":
            dict(sorted(cross_same_pair_distance_profile.items())),
        "endpoint_incidence_pair_count":
            endpoint_incidence_pair_count,
        "disjoint_cross_pair_count":
            disjoint_cross_pair_count,
    })

def image_split(split, permutation):
    left_image = frozenset(
        permutation[point]
        for point in split[0]
    )

    return canonical_split(left_image)

split_action_rows = []

for permutation in six_register_actions:
    split_permutation = tuple(
        split_id_by_key[
            image_split(split, permutation)
        ]
        for split in splits
    )

    split_action_rows.append(split_permutation)

distinct_split_actions = set(split_action_rows)

split_orbit = {
    permutation[0]
    for permutation in distinct_split_actions
}

split_zero_stabilizer_order = sum(
    permutation[0] == 0
    for permutation in distinct_split_actions
)

cross_state_membership = Counter(
    state
    for row in split_rows
    for state in row["cross_states"]
)

same_side_state_membership = Counter(
    state
    for row in split_rows
    for state in row["same_side_states"]
)

checks = {
    "source_067_exists":
        SOURCE_067.is_file(),
    "source_audit_pass":
        data.get("audit_pass") is True,
    "six_register_point_count_6":
        len(six_points) == 6,
    "unordered_three_plus_three_split_count_10":
        len(splits) == 10,
    "every_split_has_nine_cross_duads":
        all(
            len(row["cross_duads"]) == 9
            for row in split_rows
        ),
    "every_split_has_six_same_side_duads":
        all(
            len(row["same_side_duads"]) == 6
            for row in split_rows
        ),
    "every_split_partitions_all_15_G15_states":
        all(
            set(row["cross_states"]).isdisjoint(
                row["same_side_states"]
            )
            and set(row["cross_states"])
            | set(row["same_side_states"])
            == set(vertices)
            for row in split_rows
        ),
    "every_cross_duad_set_is_K33_edge_set":
        all(
            row["endpoint_incidence_pair_count"] == 18
            and row["disjoint_cross_pair_count"] == 18
            for row in split_rows
        ),
    "every_split_meets_synthemes_in_3_3_1_1_1":
        all(
            Counter(row["syntheme_cross_counts"].values())
            == Counter({3: 2, 1: 3})
            for row in split_rows
        ),
    "every_cross_nine_has_distance_profile_12_18_6":
        all(
            row["cross_pair_distance_profile"]
            == {1: 12, 2: 18, 3: 6}
            for row in split_rows
        ),
    "exceptional_S5_action_is_transitive_on_ten_splits":
        split_orbit == set(range(10)),
    "three_plus_three_split_stabilizer_order_12":
        split_zero_stabilizer_order == 12,
    "each_G15_state_is_cross_duad_in_six_splits":
        Counter(cross_state_membership.values())
        == Counter({6: 15}),
    "each_G15_state_is_same_side_in_four_splits":
        Counter(same_side_state_membership.values())
        == Counter({4: 15}),
}

failed = [
    name
    for name, passed in checks.items()
    if not passed
]

theorem_pass = not failed

print("PACKET: g900_six_register_k33_cross_duad_family_068")
print("MODE: exhaustive intrinsic three-plus-three split census")
print("SIX_REGISTER_POINTS:", six_points)
print("THREE_PLUS_THREE_SPLIT_COUNT:", len(splits))
print("SPLITS:", splits)
print("SPLIT_ROWS:", split_rows)
print("DISTINCT_SPLIT_ACTION_COUNT:", len(
    distinct_split_actions
))
print("SPLIT_ZERO_ORBIT:", tuple(sorted(split_orbit)))
print("SPLIT_ZERO_STABILIZER_ORDER:",
      split_zero_stabilizer_order)
print(
    "CROSS_STATE_MEMBERSHIP_PROFILE:",
    dict(sorted(Counter(
        cross_state_membership.values()
    ).items())),
)
print(
    "SAME_SIDE_STATE_MEMBERSHIP_PROFILE:",
    dict(sorted(Counter(
        same_side_state_membership.values()
    ).items())),
)
print("CHECKS:", checks)
print("FAILED_CHECK_COUNT:", len(failed))
print("FAILED_CHECKS:", failed)
print("THEOREM_PASS:", theorem_pass)
print(
    "CLASSIFICATION:",
    (
        "each_of_the_ten_intrinsic_three_plus_three_splits_"
        "of_the_six_decomposition_register_partitions_native_"
        "G15_into_six_same_side_duads_and_nine_cross_duads_"
        "forming_an_abstract_K3_3_edge_set_with_exact_native_"
        "pair_distance_profile_12_18_6"
        if theorem_pass
        else
        "intrinsic_six_plus_nine_K3_3_family_not_derived"
    ),
)
print("INTRINSIC_SIX_PLUS_NINE_PARTITION_DERIVED:",
      theorem_pass)
print("INTRINSIC_K33_CROSS_DUAD_FAMILY_DERIVED:",
      theorem_pass)
print("K33_FAMILY_SIZE:", len(splits))
print("CANONICAL_K33_SPLIT_SELECTED:", False)
print("HAND_DRAWING_LABELS_USED:", False)
print("DRAWING_FIVE_FOUR_EDGE_SPLIT_DERIVED:", False)
print("PHYSICAL_CUBE_CLAIM:", False)
print("MUTATION_PERFORMED:", False)
