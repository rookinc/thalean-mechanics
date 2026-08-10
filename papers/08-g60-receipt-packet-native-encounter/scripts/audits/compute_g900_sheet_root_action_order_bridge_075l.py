#!/usr/bin/env python3

import contextlib
import io
import pathlib
import runpy
import sys
from collections import Counter


def load_quiet(path):
    capture = io.StringIO()

    with contextlib.redirect_stdout(capture):
        namespace = runpy.run_path(str(path))

    return namespace


def inverse(permutation):
    result = [None] * len(permutation)

    for source, target in enumerate(permutation):
        result[target] = source

    return tuple(result)


def transform_reflection(reflection, permutation):
    transformed = [None] * len(reflection)

    for source in range(len(reflection)):
        transformed[permutation[source]] = permutation[
            reflection[source]
        ]

    return tuple(transformed)


def frame_key(frame):
    reflection_map = frame["reflection"]

    reflection = tuple(
        reflection_map[index]
        for index in range(6)
    )

    return (
        reflection,
        frame["fixed_closure_point"],
        frame["fixed_opposite_point"],
        tuple(sorted(frame["closure_duad"])),
    )


def transform_frame_key(key, permutation):
    (
        reflection,
        fixed_closure_point,
        fixed_opposite_point,
        closure_duad,
    ) = key

    return (
        transform_reflection(reflection, permutation),
        permutation[fixed_closure_point],
        permutation[fixed_opposite_point],
        tuple(sorted(
            permutation[point]
            for point in closure_duad
        )),
    )


def main():
    if len(sys.argv) != 3:
        raise SystemExit(
            "USAGE: probe_075l.py SOURCE069 SOURCE072"
        )

    source069 = pathlib.Path(sys.argv[1]).resolve()
    source072 = pathlib.Path(sys.argv[2]).resolve()

    namespace069 = load_quiet(source069)
    namespace072 = load_quiet(source072)

    valid_rows = tuple(namespace069["valid_rows"])
    candidate_rows = tuple(namespace072["candidate_rows"])
    candidate_actions = tuple(
        tuple(action)
        for action in namespace072["candidate_actions"]
    )
    six_actions = tuple(
        tuple(action)
        for action in namespace072["six_register_actions"]
    )

    frame_count = len(valid_rows)
    candidate_count = len(candidate_rows)

    frame_keys = tuple(
        frame_key(frame)
        for frame in valid_rows
    )

    frame_id_by_key = {
        key: frame_id
        for frame_id, key in enumerate(frame_keys)
    }

    candidates_by_frame = {
        frame_id: tuple(sorted(
            row["candidate_id"]
            for row in candidate_rows
            if row["frame_id"] == frame_id
        ))
        for frame_id in range(frame_count)
    }

    candidate_frame_actions = []
    candidate_frame_failures = []

    for action_id, action in enumerate(candidate_actions):
        frame_images = []

        for frame_id in range(frame_count):
            source_candidates = candidates_by_frame[frame_id]

            target_frames = {
                candidate_rows[action[candidate_id]][
                    "frame_id"
                ]
                for candidate_id in source_candidates
            }

            if len(target_frames) != 1:
                candidate_frame_failures.append((
                    action_id,
                    frame_id,
                    tuple(sorted(target_frames)),
                ))
                frame_images.append(None)
            else:
                frame_images.append(next(iter(target_frames)))

        candidate_frame_actions.append(tuple(frame_images))

    candidate_frame_actions = tuple(candidate_frame_actions)

    six_frame_actions = []
    six_frame_failures = []

    for action_id, permutation in enumerate(six_actions):
        frame_images = []

        for frame_id, key in enumerate(frame_keys):
            transformed_key = transform_frame_key(
                key,
                permutation,
            )

            target_frame = frame_id_by_key.get(
                transformed_key
            )

            if target_frame is None:
                six_frame_failures.append((
                    action_id,
                    frame_id,
                    transformed_key,
                ))

            frame_images.append(target_frame)

        six_frame_actions.append(tuple(frame_images))

    six_frame_actions = tuple(six_frame_actions)

    candidate_action_ids_by_frame_action = {}

    for action_id, frame_action in enumerate(
        candidate_frame_actions
    ):
        candidate_action_ids_by_frame_action.setdefault(
            frame_action,
            []
        ).append(action_id)

    direct_bridge = {}
    direct_missing = []
    direct_ambiguous = []

    inverse_bridge = {}
    inverse_missing = []
    inverse_ambiguous = []

    for six_action_id, frame_action in enumerate(
        six_frame_actions
    ):
        direct_matches = tuple(
            candidate_action_ids_by_frame_action.get(
                frame_action,
                (),
            )
        )

        if len(direct_matches) == 1:
            direct_bridge[six_action_id] = direct_matches[0]
        elif len(direct_matches) == 0:
            direct_missing.append(six_action_id)
        else:
            direct_ambiguous.append((
                six_action_id,
                direct_matches,
            ))

        inverse_frame_action = inverse(frame_action)

        inverse_matches = tuple(
            candidate_action_ids_by_frame_action.get(
                inverse_frame_action,
                (),
            )
        )

        if len(inverse_matches) == 1:
            inverse_bridge[six_action_id] = inverse_matches[0]
        elif len(inverse_matches) == 0:
            inverse_missing.append(six_action_id)
        else:
            inverse_ambiguous.append((
                six_action_id,
                inverse_matches,
            ))

    raw_index_match_count = sum(
        six_frame_actions[action_id]
        == candidate_frame_actions[action_id]
        for action_id in range(len(six_actions))
    )

    raw_inverse_index_match_count = sum(
        inverse(six_frame_actions[action_id])
        == candidate_frame_actions[action_id]
        for action_id in range(len(six_actions))
    )

    direct_bridge_values = tuple(direct_bridge.values())
    inverse_bridge_values = tuple(inverse_bridge.values())

    direct_complete = (
        len(direct_bridge) == 120
        and len(set(direct_bridge_values)) == 120
        and not direct_missing
        and not direct_ambiguous
    )

    inverse_complete = (
        len(inverse_bridge) == 120
        and len(set(inverse_bridge_values)) == 120
        and not inverse_missing
        and not inverse_ambiguous
    )

    if direct_complete and not inverse_complete:
        selected_convention = "direct"
        selected_bridge = direct_bridge
    elif inverse_complete and not direct_complete:
        selected_convention = "inverse"
        selected_bridge = inverse_bridge
    elif direct_complete and inverse_complete:
        selected_convention = "both"
        selected_bridge = direct_bridge
    else:
        selected_convention = "none"
        selected_bridge = {}

    bridge_displacement_profile = Counter(
        candidate_action_id - six_action_id
        for six_action_id, candidate_action_id
        in selected_bridge.items()
    )

    checks = {
        "source_069_exists": source069.is_file(),
        "source_072_exists": source072.is_file(),
        "frame_count_60": frame_count == 60,
        "candidate_count_120": candidate_count == 120,
        "candidate_action_count_120":
            len(candidate_actions) == 120,
        "six_action_count_120":
            len(six_actions) == 120,
        "restored_frame_keys_distinct":
            len(frame_id_by_key) == 60,
        "two_candidates_per_frame":
            all(
                len(candidates_by_frame[frame_id]) == 2
                for frame_id in range(frame_count)
            ),
        "candidate_frame_failures_zero":
            not candidate_frame_failures,
        "six_frame_failures_zero":
            not six_frame_failures,
        "exact_action_order_bridge_exists":
            direct_complete or inverse_complete,
    }

    failed = [
        name
        for name, passed in checks.items()
        if not passed
    ]

    theorem_pass = not failed

    print(
        "PACKET:",
        "g900_sheet_root_action_order_bridge_075l",
    )
    print(
        "MODE:",
        "exact restored-frame action-order reconciliation",
    )
    print("FRAME_COUNT:", frame_count)
    print("COMPLETION_CANDIDATE_COUNT:", candidate_count)
    print("CANDIDATE_ACTION_COUNT:", len(candidate_actions))
    print("SIX_ACTION_COUNT:", len(six_actions))
    print(
        "CANDIDATE_FRAME_ACTION_DISTINCT_COUNT:",
        len(set(candidate_frame_actions)),
    )
    print(
        "SIX_FRAME_ACTION_DISTINCT_COUNT:",
        len(set(six_frame_actions)),
    )
    print(
        "CANDIDATE_FRAME_FAILURE_COUNT:",
        len(candidate_frame_failures),
    )
    print(
        "SIX_FRAME_FAILURE_COUNT:",
        len(six_frame_failures),
    )
    print(
        "RAW_INDEX_FRAME_ACTION_MATCH_COUNT:",
        raw_index_match_count,
    )
    print(
        "RAW_INVERSE_INDEX_FRAME_ACTION_MATCH_COUNT:",
        raw_inverse_index_match_count,
    )
    print("DIRECT_BRIDGE_COUNT:", len(direct_bridge))
    print("DIRECT_BRIDGE_MISSING_COUNT:", len(direct_missing))
    print(
        "DIRECT_BRIDGE_AMBIGUOUS_COUNT:",
        len(direct_ambiguous),
    )
    print("DIRECT_BRIDGE_COMPLETE:", direct_complete)
    print("INVERSE_BRIDGE_COUNT:", len(inverse_bridge))
    print(
        "INVERSE_BRIDGE_MISSING_COUNT:",
        len(inverse_missing),
    )
    print(
        "INVERSE_BRIDGE_AMBIGUOUS_COUNT:",
        len(inverse_ambiguous),
    )
    print("INVERSE_BRIDGE_COMPLETE:", inverse_complete)
    print("SELECTED_CONVENTION:", selected_convention)
    print(
        "SELECTED_BRIDGE_IS_BIJECTION:",
        len(selected_bridge) == 120
        and len(set(selected_bridge.values())) == 120,
    )
    print(
        "BRIDGE_DISPLACEMENT_PROFILE:",
        dict(sorted(bridge_displacement_profile.items())),
    )
    print(
        "BRIDGE_PREVIEW:",
        tuple(sorted(selected_bridge.items()))[:30],
    )
    print("CHECKS:", checks)
    print("FAILED_CHECK_COUNT:", len(failed))
    print("FAILED_CHECKS:", failed)
    print("THEOREM_PASS:", theorem_pass)
    print(
        "CLASSIFICATION:",
        (
            "the_completion_candidate_action_and_the_"
            "restored_affine_root_action_have_the_same_"
            "native_frame_action_after_an_explicit_"
            "action_order_bridge"
            if theorem_pass
            else
            "completion_and_root_action_order_bridge_"
            "not_derived"
        ),
    )
    print("COMBINED_COVER_TEST_PERFORMED:", False)
    print("REPOSITORY_MUTATION: none")


if __name__ == "__main__":
    main()
