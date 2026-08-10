#!/usr/bin/env python3

import contextlib
import io
import json
import pathlib
import runpy
import sys
from collections import Counter


def inverse(permutation):
    result = [None] * len(permutation)

    for point, image in enumerate(permutation):
        result[image] = point

    return tuple(result)


def compose(left, right):
    return tuple(
        left[right[index]]
        for index in range(len(left))
    )


def conjugate(g, h):
    return compose(
        compose(g, h),
        inverse(g),
    )


def duad(value):
    return tuple(sorted(
        int(point)
        for point in value
    ))


def transport_duad(action, value):
    return tuple(sorted(
        action[point]
        for point in value
    ))


def reflection_tuple(row):
    return tuple(
        row["reflection"][index]
        for index in range(6)
    )


def frame_key(
    reflection,
    closure_point,
    opposite_point,
    closure_duad,
):
    return (
        tuple(reflection),
        int(closure_point),
        int(opposite_point),
        duad(closure_duad),
    )


def orbit_partition(states, actions):
    remaining = set(states)
    orbits = []

    while remaining:
        representative = min(remaining)

        orbit = frozenset(
            action[representative]
            for action in actions
        )

        if representative not in orbit:
            raise RuntimeError(
                "COMBINED_IDENTITY_MISSING: "
                f"{representative}"
            )

        reduced = remaining - orbit

        if len(reduced) >= len(remaining):
            raise RuntimeError(
                "COMBINED_ORBIT_NO_PROGRESS: "
                f"{representative}"
            )

        orbits.append(orbit)
        remaining = reduced

    return tuple(sorted(
        orbits,
        key=lambda orbit: (
            len(orbit),
            min(orbit),
        ),
    ))


def load_namespace(path):
    captured = io.StringIO()

    with contextlib.redirect_stdout(captured):
        namespace = runpy.run_path(str(path))

    return namespace, captured.getvalue()


def main():
    source069 = pathlib.Path(sys.argv[1]).resolve()
    source072 = pathlib.Path(sys.argv[2]).resolve()
    compact_path = pathlib.Path(sys.argv[3]).resolve()

    ns069, stdout069 = load_namespace(source069)
    ns072, stdout072 = load_namespace(source072)

    full_frames = tuple(ns069["valid_rows"])

    compact = json.loads(
        compact_path.read_text(encoding="utf-8")
    )

    actions = tuple(
        tuple(action)
        for action in compact["six_register_actions"]
    )

    compact_frames = {
        row["frame_id"]: row
        for row in compact["frames"]
    }

    candidate_rows = tuple(ns072["candidate_rows"])
    candidate_actions = tuple(
        tuple(action)
        for action in ns072["candidate_actions"]
    )
    candidate_to_sheet = dict(
        ns072["candidate_to_orbit"]
    )

    frames = []

    for frame_id, full_row in enumerate(full_frames):
        compact_row = compact_frames[frame_id]

        frames.append({
            "frame_id": frame_id,
            "reflection":
                reflection_tuple(full_row),
            "fixed_closure_point":
                full_row["fixed_closure_point"],
            "fixed_opposite_point":
                full_row["fixed_opposite_point"],
            "closure_duad":
                duad(full_row["closure_duad"]),
            "centered_roots": tuple(
                tuple(root)
                for root
                in compact_row["centered_roots"]
            ),
        })

    frames = tuple(frames)

    frame_by_key = {
        frame_key(
            row["reflection"],
            row["fixed_closure_point"],
            row["fixed_opposite_point"],
            row["closure_duad"],
        ): row["frame_id"]
        for row in frames
    }

    root_index = {
        row["frame_id"]: {
            root: root_slot
            for root_slot, root
            in enumerate(row["centered_roots"])
        }
        for row in frames
    }

    frame_to_candidates = {
        frame_id: tuple(sorted(
            row["candidate_id"]
            for row in candidate_rows
            if row["frame_id"] == frame_id
        ))
        for frame_id in range(len(frames))
    }

    candidate_to_frame = {
        row["candidate_id"]: row["frame_id"]
        for row in candidate_rows
    }

    root_states = tuple(
        (frame_id, root_slot)
        for frame_id in range(len(frames))
        for root_slot in range(2)
    )

    root_state_index = {
        state: index
        for index, state in enumerate(root_states)
    }

    root_transports = []
    root_failures = []

    for action_id, action in enumerate(actions):
        permutation = []

        for frame_id, root_slot in root_states:
            frame = frames[frame_id]

            target_frame = frame_by_key.get(
                frame_key(
                    conjugate(
                        action,
                        frame["reflection"],
                    ),
                    action[
                        frame["fixed_closure_point"]
                    ],
                    action[
                        frame["fixed_opposite_point"]
                    ],
                    transport_duad(
                        action,
                        frame["closure_duad"],
                    ),
                )
            )

            if target_frame is None:
                root_failures.append(
                    (
                        "frame_missing",
                        action_id,
                        frame_id,
                        root_slot,
                    )
                )
                permutation.append(None)
                continue

            target_root = conjugate(
                action,
                frame["centered_roots"][root_slot],
            )

            target_root_slot = root_index[
                target_frame
            ].get(target_root)

            if target_root_slot is None:
                root_failures.append(
                    (
                        "root_missing",
                        action_id,
                        frame_id,
                        root_slot,
                        target_frame,
                    )
                )
                permutation.append(None)
                continue

            permutation.append(
                root_state_index[
                    (
                        target_frame,
                        target_root_slot,
                    )
                ]
            )

        root_transports.append(tuple(permutation))

    root_transports = tuple(root_transports)

    combined_states = tuple(
        (
            frame_id,
            candidate_id,
            root_slot,
        )
        for frame_id in range(len(frames))
        for candidate_id in frame_to_candidates[frame_id]
        for root_slot in range(2)
    )

    combined_index = {
        state: index
        for index, state in enumerate(combined_states)
    }

    native_combined_actions = []
    combined_failures = []

    for action_id in range(len(actions)):
        permutation = []

        for (
            frame_id,
            candidate_id,
            root_slot,
        ) in combined_states:
            target_candidate = candidate_actions[
                action_id
            ][candidate_id]

            target_root_state_id = root_transports[
                action_id
            ][
                root_state_index[
                    (
                        frame_id,
                        root_slot,
                    )
                ]
            ]

            if target_root_state_id is None:
                combined_failures.append(
                    (
                        "root_transport_missing",
                        action_id,
                        frame_id,
                        candidate_id,
                        root_slot,
                    )
                )
                permutation.append(None)
                continue

            (
                target_root_frame,
                target_root_slot,
            ) = root_states[target_root_state_id]

            target_candidate_frame = (
                candidate_to_frame[
                    target_candidate
                ]
            )

            if (
                target_candidate_frame
                != target_root_frame
            ):
                combined_failures.append(
                    (
                        "base_frame_mismatch",
                        action_id,
                        frame_id,
                        candidate_id,
                        root_slot,
                        target_candidate_frame,
                        target_root_frame,
                    )
                )
                permutation.append(None)
                continue

            permutation.append(
                combined_index[
                    (
                        target_root_frame,
                        target_candidate,
                        target_root_slot,
                    )
                ]
            )

        native_combined_actions.append(
            tuple(permutation)
        )

    native_combined_actions = tuple(
        native_combined_actions
    )

    sheet_deck = []
    root_deck = []

    for (
        frame_id,
        candidate_id,
        root_slot,
    ) in combined_states:
        frame_candidates = frame_to_candidates[
            frame_id
        ]

        other_candidate = next(
            candidate
            for candidate in frame_candidates
            if candidate != candidate_id
        )

        sheet_deck.append(
            combined_index[
                (
                    frame_id,
                    other_candidate,
                    root_slot,
                )
            ]
        )

        root = frames[frame_id][
            "centered_roots"
        ][root_slot]

        inverse_root_slot = root_index[
            frame_id
        ][inverse(root)]

        root_deck.append(
            combined_index[
                (
                    frame_id,
                    candidate_id,
                    inverse_root_slot,
                )
            ]
        )

    sheet_deck = tuple(sheet_deck)
    root_deck = tuple(root_deck)

    identity = tuple(
        range(len(combined_states))
    )

    combined_deck = compose(
        sheet_deck,
        root_deck,
    )

    deck_elements = (
        identity,
        sheet_deck,
        root_deck,
        combined_deck,
    )

    sheet_fixed_count = sum(
        index == image
        for index, image
        in enumerate(sheet_deck)
    )

    root_fixed_count = sum(
        index == image
        for index, image
        in enumerate(root_deck)
    )

    combined_fixed_count = sum(
        index == image
        for index, image
        in enumerate(combined_deck)
    )

    sheet_commutation_failures = []
    root_commutation_failures = []

    for action_id, native_action in enumerate(
        native_combined_actions
    ):
        if None in native_action:
            continue

        if (
            compose(sheet_deck, native_action)
            != compose(native_action, sheet_deck)
        ):
            sheet_commutation_failures.append(
                action_id
            )

        if (
            compose(root_deck, native_action)
            != compose(native_action, root_deck)
        ):
            root_commutation_failures.append(
                action_id
            )

    decks_commute = (
        compose(sheet_deck, root_deck)
        == compose(root_deck, sheet_deck)
    )

    deck_action_is_regular_on_each_fiber = all(
        len({
            deck[state_id]
            for deck in deck_elements
        }) == 4
        for state_id in range(len(combined_states))
    )

    orbits = ()

    if (
        not root_failures
        and not combined_failures
        and all(
            None not in action
            and len(set(action))
            == len(combined_states)
            for action in native_combined_actions
        )
    ):
        orbits = orbit_partition(
            tuple(range(len(combined_states))),
            native_combined_actions,
        )

    state_to_orbit = {
        state_id: orbit_id
        for orbit_id, orbit in enumerate(orbits)
        for state_id in orbit
    }

    orbit_rows = []

    for orbit_id, orbit in enumerate(orbits):
        projected_frames = tuple(
            combined_states[state_id][0]
            for state_id in orbit
        )

        sheet_profile = Counter(
            candidate_to_sheet[
                combined_states[state_id][1]
            ]
            for state_id in orbit
        )

        root_slot_profile = Counter(
            combined_states[state_id][2]
            for state_id in orbit
        )

        orbit_rows.append({
            "orbit_id": orbit_id,
            "orbit_size": len(orbit),
            "projected_frame_count":
                len(set(projected_frames)),
            "frame_multiplicity_profile":
                dict(sorted(
                    Counter(
                        Counter(
                            projected_frames
                        ).values()
                    ).items()
                )),
            "sheet_profile":
                dict(sorted(sheet_profile.items())),
            "root_slot_profile":
                dict(sorted(
                    root_slot_profile.items()
                )),
        })

    sheet_deck_orbit_profile = Counter()
    root_deck_orbit_profile = Counter()
    combined_deck_orbit_profile = Counter()

    if orbits:
        for state_id in range(len(combined_states)):
            source_orbit = state_to_orbit[state_id]

            sheet_deck_orbit_profile[
                (
                    source_orbit,
                    state_to_orbit[
                        sheet_deck[state_id]
                    ],
                )
            ] += 1

            root_deck_orbit_profile[
                (
                    source_orbit,
                    state_to_orbit[
                        root_deck[state_id]
                    ],
                )
            ] += 1

            combined_deck_orbit_profile[
                (
                    source_orbit,
                    state_to_orbit[
                        combined_deck[state_id]
                    ],
                )
            ] += 1

    checks = {
        "source_069_theorem_pass":
            ns069.get("theorem_pass") is True,
        "source_072_theorem_pass":
            ns072.get("theorem_pass") is True,
        "frame_count_60":
            len(frames) == 60,
        "two_completion_candidates_per_frame":
            all(
                len(candidates) == 2
                for candidates
                in frame_to_candidates.values()
            ),
        "two_roots_per_frame":
            all(
                len(row["centered_roots"]) == 2
                for row in frames
            ),
        "combined_state_count_240":
            len(combined_states) == 240,
        "root_transport_failure_count_zero":
            not root_failures,
        "combined_transport_failure_count_zero":
            not combined_failures,
        "all_native_combined_actions_bijective":
            all(
                None not in action
                and len(set(action)) == 240
                for action
                in native_combined_actions
            ),
        "sheet_deck_is_fixed_point_free_involution":
            compose(sheet_deck, sheet_deck)
            == identity
            and sheet_fixed_count == 0,
        "root_deck_is_fixed_point_free_involution":
            compose(root_deck, root_deck)
            == identity
            and root_fixed_count == 0,
        "combined_deck_is_fixed_point_free_involution":
            compose(combined_deck, combined_deck)
            == identity
            and combined_fixed_count == 0,
        "deck_involutions_commute":
            decks_commute,
        "deck_group_order_4":
            len(set(deck_elements)) == 4,
        "deck_group_regular_on_each_frame_fiber":
            deck_action_is_regular_on_each_fiber,
        "sheet_deck_central":
            not sheet_commutation_failures,
        "root_deck_central":
            not root_commutation_failures,
        "four_native_orbits_of_size_60":
            len(orbits) == 4
            and Counter(
                len(orbit)
                for orbit in orbits
            ) == Counter({60: 4}),
        "each_orbit_projects_bijectively_to_frames":
            all(
                row["projected_frame_count"] == 60
                and row[
                    "frame_multiplicity_profile"
                ] == {1: 60}
                for row in orbit_rows
            ),
    }

    failed = [
        name
        for name, passed in checks.items()
        if not passed
    ]

    theorem_pass = not failed

    print(
        "PACKET:",
        "g900_combined_sheet_root_deck_group_075k",
    )
    print(
        "MODE:",
        "exact combined completion-sheet and affine-root cover audit",
    )
    print("BASE_FRAME_COUNT:", len(frames))
    print(
        "COMPLETION_CANDIDATE_COUNT:",
        len(candidate_rows),
    )
    print("FRAME_ROOT_COUNT:", 120)
    print(
        "COMBINED_STATE_COUNT:",
        len(combined_states),
    )
    print(
        "ROOT_TRANSPORT_FAILURE_COUNT:",
        len(root_failures),
    )
    print(
        "COMBINED_TRANSPORT_FAILURE_COUNT:",
        len(combined_failures),
    )
    print(
        "SHEET_DECK_FIXED_POINT_COUNT:",
        sheet_fixed_count,
    )
    print(
        "ROOT_DECK_FIXED_POINT_COUNT:",
        root_fixed_count,
    )
    print(
        "COMBINED_DECK_FIXED_POINT_COUNT:",
        combined_fixed_count,
    )
    print(
        "DECK_INVOLUTIONS_COMMUTE:",
        decks_commute,
    )
    print(
        "DECK_GROUP_ORDER:",
        len(set(deck_elements)),
    )
    print(
        "DECK_GROUP_IS_V4:",
        (
            len(set(deck_elements)) == 4
            and all(
                compose(deck, deck) == identity
                for deck in deck_elements
            )
        ),
    )
    print(
        "DECK_ACTION_REGULAR_ON_FRAME_FIBERS:",
        deck_action_is_regular_on_each_fiber,
    )
    print(
        "SHEET_DECK_COMMUTATION_FAILURE_COUNT:",
        len(sheet_commutation_failures),
    )
    print(
        "ROOT_DECK_COMMUTATION_FAILURE_COUNT:",
        len(root_commutation_failures),
    )
    print(
        "COMBINED_NATIVE_ORBIT_COUNT:",
        len(orbits),
    )
    print(
        "COMBINED_NATIVE_ORBIT_SIZE_PROFILE:",
        dict(sorted(
            Counter(
                len(orbit)
                for orbit in orbits
            ).items()
        )),
    )
    print(
        "COMBINED_ORBIT_ROWS:",
        orbit_rows,
    )
    print(
        "SHEET_DECK_ORBIT_PROFILE:",
        dict(sorted(
            sheet_deck_orbit_profile.items()
        )),
    )
    print(
        "ROOT_DECK_ORBIT_PROFILE:",
        dict(sorted(
            root_deck_orbit_profile.items()
        )),
    )
    print(
        "COMBINED_DECK_ORBIT_PROFILE:",
        dict(sorted(
            combined_deck_orbit_profile.items()
        )),
    )
    print("CHECKS:", checks)
    print("FAILED_CHECK_COUNT:", len(failed))
    print("FAILED_CHECKS:", failed)
    print("THEOREM_PASS:", theorem_pass)

    if theorem_pass:
        classification = (
            "the_combined_completion_sheet_and_affine_"
            "orientation_register_is_a_four_sheeted_"
            "native_cover_of_the_sixty_frame_register_"
            "with_central_Klein_four_deck_group_and_four_"
            "native_orbits_of_size_sixty"
        )
    else:
        classification = (
            "combined_sheet_root_Klein_four_cover_not_derived"
        )

    print("CLASSIFICATION:", classification)
    print("CANONICAL_COMPLETION_SHEET_SELECTED:", False)
    print("CANONICAL_AFFINE_ORIENTATION_SELECTED:", False)
    print("NUMERIC_ANGLE_VALUES_DERIVED:", False)
    print("PHYSICAL_CLAIM:", False)
    print("MUTATION_PERFORMED:", False)


if __name__ == "__main__":
    main()
