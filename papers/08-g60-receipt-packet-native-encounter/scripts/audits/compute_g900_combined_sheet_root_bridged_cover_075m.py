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


def compose(left, right):
    return tuple(
        left[right[index]]
        for index in range(len(left))
    )


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


def conjugate(permutation, element):
    permutation_inverse = inverse(permutation)

    return compose(
        permutation,
        compose(element, permutation_inverse),
    )


def orbit_partition(actions, state_count):
    unclassified = set(range(state_count))
    orbits = []

    while unclassified:
        representative = min(unclassified)

        orbit = {
            action[representative]
            for action in actions
        }

        if representative not in orbit:
            raise RuntimeError(
                "IDENTITY_MISSING_FROM_ORBIT: "
                + repr(representative)
            )

        if not orbit <= unclassified:
            overlap = sorted(orbit - unclassified)[:20]
            raise RuntimeError(
                "ORBIT_OVERLAP: " + repr(overlap)
            )

        orbits.append(frozenset(orbit))
        unclassified -= orbit

    return tuple(sorted(
        orbits,
        key=lambda orbit: (
            len(orbit),
            min(orbit),
        ),
    ))


def main():
    if len(sys.argv) != 3:
        raise SystemExit(
            "USAGE: probe_075m.py SOURCE069 SOURCE072"
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
    candidate_to_sheet = dict(
        namespace072["candidate_to_orbit"]
    )
    six_actions = tuple(
        tuple(action)
        for action in namespace072["six_register_actions"]
    )
    root_frame_rows = tuple(namespace072["frame_rows"])

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

    roots_by_frame = {
        frame_id: tuple(
            tuple(root)
            for root in root_frame_rows[frame_id][
                "centered_roots"
            ]
        )
        for frame_id in range(frame_count)
    }

    candidate_frame_actions = []

    for action in candidate_actions:
        frame_images = []

        for frame_id in range(frame_count):
            target_frames = {
                candidate_rows[action[candidate_id]][
                    "frame_id"
                ]
                for candidate_id
                in candidates_by_frame[frame_id]
            }

            if len(target_frames) != 1:
                raise RuntimeError(
                    "CANDIDATE_FRAME_IMAGE_AMBIGUOUS: "
                    + repr((
                        frame_id,
                        tuple(sorted(target_frames)),
                    ))
                )

            frame_images.append(next(iter(target_frames)))

        candidate_frame_actions.append(tuple(frame_images))

    candidate_frame_actions = tuple(candidate_frame_actions)

    candidate_action_by_frame_action = {}

    for candidate_action_id, frame_action in enumerate(
        candidate_frame_actions
    ):
        if frame_action in candidate_action_by_frame_action:
            raise RuntimeError(
                "CANDIDATE_FRAME_ACTION_DUPLICATE"
            )

        candidate_action_by_frame_action[
            frame_action
        ] = candidate_action_id

    six_frame_actions = []
    direct_bridge = {}
    bridge_failures = []

    for six_action_id, permutation in enumerate(six_actions):
        frame_images = []

        for frame_id, key in enumerate(frame_keys):
            target_key = transform_frame_key(
                key,
                permutation,
            )

            target_frame = frame_id_by_key.get(target_key)

            if target_frame is None:
                bridge_failures.append((
                    "six_frame_image_missing",
                    six_action_id,
                    frame_id,
                ))

            frame_images.append(target_frame)

        frame_action = tuple(frame_images)
        six_frame_actions.append(frame_action)

        candidate_action_id = (
            candidate_action_by_frame_action.get(
                frame_action
            )
        )

        if candidate_action_id is None:
            bridge_failures.append((
                "candidate_action_bridge_missing",
                six_action_id,
            ))
        else:
            direct_bridge[
                six_action_id
            ] = candidate_action_id

    six_frame_actions = tuple(six_frame_actions)

    states = tuple(
        (
            frame_id,
            candidate_id,
            root_slot,
        )
        for frame_id in range(frame_count)
        for candidate_id in candidates_by_frame[frame_id]
        for root_slot in range(
            len(roots_by_frame[frame_id])
        )
    )

    state_id = {
        state: index
        for index, state in enumerate(states)
    }

    combined_actions = []
    root_transport_failures = []
    combined_transport_failures = []

    for six_action_id, permutation in enumerate(six_actions):
        candidate_action_id = direct_bridge.get(
            six_action_id
        )

        if candidate_action_id is None:
            continue

        candidate_action = candidate_actions[
            candidate_action_id
        ]

        state_images = []

        for source_state_id, state in enumerate(states):
            frame_id, candidate_id, root_slot = state

            target_frame = six_frame_actions[
                six_action_id
            ][frame_id]

            source_root = roots_by_frame[
                frame_id
            ][root_slot]

            transported_root = conjugate(
                permutation,
                source_root,
            )

            target_roots = roots_by_frame[target_frame]

            matching_root_slots = tuple(
                target_root_slot
                for target_root_slot, target_root
                in enumerate(target_roots)
                if target_root == transported_root
            )

            if len(matching_root_slots) != 1:
                root_transport_failures.append((
                    six_action_id,
                    frame_id,
                    root_slot,
                    target_frame,
                    transported_root,
                    matching_root_slots,
                ))
                state_images.append(None)
                continue

            target_root_slot = matching_root_slots[0]
            target_candidate_id = candidate_action[
                candidate_id
            ]

            candidate_target_frame = candidate_rows[
                target_candidate_id
            ]["frame_id"]

            if candidate_target_frame != target_frame:
                combined_transport_failures.append((
                    six_action_id,
                    candidate_action_id,
                    frame_id,
                    target_frame,
                    candidate_id,
                    target_candidate_id,
                    candidate_target_frame,
                ))
                state_images.append(None)
                continue

            target_state = (
                target_frame,
                target_candidate_id,
                target_root_slot,
            )

            target_state_id = state_id.get(target_state)

            if target_state_id is None:
                combined_transport_failures.append((
                    "combined_state_missing",
                    six_action_id,
                    source_state_id,
                    target_state,
                ))
                state_images.append(None)
                continue

            state_images.append(target_state_id)

        combined_actions.append(tuple(state_images))

    combined_actions = tuple(combined_actions)

    complete_combined_actions = tuple(
        action
        for action in combined_actions
        if None not in action
    )

    combined_bijection_count = sum(
        len(set(action)) == len(states)
        for action in complete_combined_actions
    )

    combined_identity_indices = tuple(
        action_id
        for action_id, action in enumerate(
            complete_combined_actions
        )
        if action == tuple(range(len(states)))
    )

    combined_action_distinct_count = len(set(
        complete_combined_actions
    ))

    if (
        not root_transport_failures
        and not combined_transport_failures
        and len(complete_combined_actions) == 120
        and combined_bijection_count == 120
        and len(combined_identity_indices) == 1
    ):
        native_orbits = orbit_partition(
            complete_combined_actions,
            len(states),
        )
    else:
        native_orbits = ()

    state_to_orbit = {
        member: orbit_id
        for orbit_id, orbit in enumerate(native_orbits)
        for member in orbit
    }

    sheet_deck = []
    root_deck = []

    for state in states:
        frame_id, candidate_id, root_slot = state

        frame_candidates = candidates_by_frame[frame_id]
        other_candidates = tuple(
            value
            for value in frame_candidates
            if value != candidate_id
        )

        if len(other_candidates) != 1:
            raise RuntimeError(
                "SHEET_DECK_TARGET_NOT_UNIQUE"
            )

        other_candidate = other_candidates[0]

        other_root_slots = tuple(
            value
            for value in range(
                len(roots_by_frame[frame_id])
            )
            if value != root_slot
        )

        if len(other_root_slots) != 1:
            raise RuntimeError(
                "ROOT_DECK_TARGET_NOT_UNIQUE"
            )

        other_root_slot = other_root_slots[0]

        sheet_deck.append(state_id[(
            frame_id,
            other_candidate,
            root_slot,
        )])

        root_deck.append(state_id[(
            frame_id,
            candidate_id,
            other_root_slot,
        )])

    sheet_deck = tuple(sheet_deck)
    root_deck = tuple(root_deck)
    combined_deck = compose(sheet_deck, root_deck)
    identity = tuple(range(len(states)))

    deck_group = {
        identity,
        sheet_deck,
        root_deck,
        combined_deck,
    }

    sheet_deck_commutation_failures = []
    root_deck_commutation_failures = []

    for action_id, action in enumerate(
        complete_combined_actions
    ):
        if compose(sheet_deck, action) != compose(
            action,
            sheet_deck,
        ):
            sheet_deck_commutation_failures.append(
                action_id
            )

        if compose(root_deck, action) != compose(
            action,
            root_deck,
        ):
            root_deck_commutation_failures.append(
                action_id
            )

    frame_fiber_regular = all(
        {
            deck_element[state_id[(
                frame_id,
                candidates_by_frame[frame_id][0],
                0,
            )]]
            for deck_element in deck_group
        }
        == {
            state_id[state]
            for state in states
            if state[0] == frame_id
        }
        for frame_id in range(frame_count)
    )

    orbit_projection_rows = []

    for orbit_id, orbit in enumerate(native_orbits):
        projected_frames = Counter(
            states[member][0]
            for member in orbit
        )

        completion_sheet_profile = Counter(
            candidate_to_sheet[
                states[member][1]
            ]
            for member in orbit
        )

        root_slot_profile = Counter(
            states[member][2]
            for member in orbit
        )

        orbit_projection_rows.append({
            "orbit_id": orbit_id,
            "orbit_size": len(orbit),
            "projected_frame_count":
                len(projected_frames),
            "frame_multiplicity_profile":
                dict(sorted(Counter(
                    projected_frames.values()
                ).items())),
            "completion_sheet_profile":
                dict(sorted(
                    completion_sheet_profile.items()
                )),
            "root_slot_profile":
                dict(sorted(root_slot_profile.items())),
        })

    def deck_orbit_profile(deck):
        profile = Counter()

        for source_orbit_id, orbit in enumerate(
            native_orbits
        ):
            target_orbits = {
                state_to_orbit[deck[member]]
                for member in orbit
            }

            if len(target_orbits) == 1:
                target_orbit_id = next(
                    iter(target_orbits)
                )
                profile[(
                    source_orbit_id,
                    target_orbit_id,
                )] += len(orbit)
            else:
                profile[(
                    source_orbit_id,
                    tuple(sorted(target_orbits)),
                )] += len(orbit)

        return dict(sorted(profile.items()))

    native_orbit_size_profile = Counter(
        len(orbit)
        for orbit in native_orbits
    )

    checks = {
        "source_069_exists": source069.is_file(),
        "source_072_exists": source072.is_file(),
        "frame_count_60": frame_count == 60,
        "candidate_count_120": candidate_count == 120,
        "two_candidates_per_frame": all(
            len(candidates_by_frame[frame_id]) == 2
            for frame_id in range(frame_count)
        ),
        "two_roots_per_frame": all(
            len(roots_by_frame[frame_id]) == 2
            for frame_id in range(frame_count)
        ),
        "combined_state_count_240":
            len(states) == 240,
        "direct_bridge_count_120":
            len(direct_bridge) == 120,
        "bridge_failure_count_zero":
            not bridge_failures,
        "root_transport_failure_count_zero":
            not root_transport_failures,
        "combined_transport_failure_count_zero":
            not combined_transport_failures,
        "combined_action_count_120":
            len(complete_combined_actions) == 120,
        "all_combined_actions_bijective":
            combined_bijection_count == 120,
        "combined_actions_distinct_120":
            combined_action_distinct_count == 120,
        "combined_identity_exists_once":
            len(combined_identity_indices) == 1,
        "sheet_deck_fixed_point_free":
            all(
                sheet_deck[index] != index
                for index in range(len(states))
            ),
        "root_deck_fixed_point_free":
            all(
                root_deck[index] != index
                for index in range(len(states))
            ),
        "deck_involutions_commute":
            compose(sheet_deck, root_deck)
            == compose(root_deck, sheet_deck),
        "deck_group_is_V4":
            len(deck_group) == 4
            and all(
                compose(element, element) == identity
                for element in deck_group
            ),
        "deck_regular_on_frame_fibers":
            frame_fiber_regular,
        "sheet_deck_central":
            not sheet_deck_commutation_failures,
        "root_deck_central":
            not root_deck_commutation_failures,
        "four_native_orbits_size_60":
            native_orbit_size_profile
            == Counter({60: 4}),
        "each_orbit_projects_bijectively":
            all(
                row["projected_frame_count"] == 60
                and row[
                    "frame_multiplicity_profile"
                ] == {1: 60}
                for row in orbit_projection_rows
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
        "g900_combined_sheet_root_bridged_cover_075m",
    )
    print(
        "MODE:",
        "action-order-bridged combined cover census",
    )
    print("BASE_FRAME_COUNT:", frame_count)
    print(
        "COMPLETION_CANDIDATE_COUNT:",
        candidate_count,
    )
    print("FRAME_ROOT_COUNT:", 2 * frame_count)
    print("COMBINED_STATE_COUNT:", len(states))
    print("DIRECT_BRIDGE_COUNT:", len(direct_bridge))
    print(
        "BRIDGE_FAILURE_COUNT:",
        len(bridge_failures),
    )
    print(
        "ROOT_TRANSPORT_FAILURE_COUNT:",
        len(root_transport_failures),
    )
    print(
        "COMBINED_TRANSPORT_FAILURE_COUNT:",
        len(combined_transport_failures),
    )
    print(
        "COMBINED_NATIVE_ACTION_COUNT:",
        len(complete_combined_actions),
    )
    print(
        "COMBINED_NATIVE_ACTION_BIJECTION_COUNT:",
        combined_bijection_count,
    )
    print(
        "COMBINED_NATIVE_ACTION_DISTINCT_COUNT:",
        combined_action_distinct_count,
    )
    print(
        "COMBINED_IDENTITY_INDICES:",
        combined_identity_indices,
    )
    print(
        "SHEET_DECK_FIXED_POINT_COUNT:",
        sum(
            sheet_deck[index] == index
            for index in range(len(states))
        ),
    )
    print(
        "ROOT_DECK_FIXED_POINT_COUNT:",
        sum(
            root_deck[index] == index
            for index in range(len(states))
        ),
    )
    print(
        "COMBINED_DECK_FIXED_POINT_COUNT:",
        sum(
            combined_deck[index] == index
            for index in range(len(states))
        ),
    )
    print(
        "DECK_INVOLUTIONS_COMMUTE:",
        compose(sheet_deck, root_deck)
        == compose(root_deck, sheet_deck),
    )
    print("DECK_GROUP_ORDER:", len(deck_group))
    print(
        "DECK_GROUP_IS_V4:",
        len(deck_group) == 4
        and all(
            compose(element, element) == identity
            for element in deck_group
        ),
    )
    print(
        "DECK_ACTION_REGULAR_ON_FRAME_FIBERS:",
        frame_fiber_regular,
    )
    print(
        "SHEET_DECK_COMMUTATION_FAILURE_COUNT:",
        len(sheet_deck_commutation_failures),
    )
    print(
        "ROOT_DECK_COMMUTATION_FAILURE_COUNT:",
        len(root_deck_commutation_failures),
    )
    print(
        "COMBINED_NATIVE_ORBIT_COUNT:",
        len(native_orbits),
    )
    print(
        "COMBINED_NATIVE_ORBIT_SIZE_PROFILE:",
        dict(sorted(native_orbit_size_profile.items())),
    )
    print(
        "COMBINED_ORBIT_ROWS:",
        orbit_projection_rows,
    )
    print(
        "SHEET_DECK_ORBIT_PROFILE:",
        deck_orbit_profile(sheet_deck),
    )
    print(
        "ROOT_DECK_ORBIT_PROFILE:",
        deck_orbit_profile(root_deck),
    )
    print(
        "COMBINED_DECK_ORBIT_PROFILE:",
        deck_orbit_profile(combined_deck),
    )
    print("CHECKS:", checks)
    print("FAILED_CHECK_COUNT:", len(failed))
    print("FAILED_CHECKS:", failed)
    print("THEOREM_PASS:", theorem_pass)
    print(
        "CLASSIFICATION:",
        (
            "the_combined_completion_sheet_and_affine_"
            "orientation_register_is_a_four_sheeted_"
            "native_cover_of_the_sixty_frame_register_"
            "with_central_Klein_four_deck_group_and_"
            "four_native_orbits_of_size_sixty"
            if theorem_pass
            else
            "bridged_combined_sheet_root_cover_not_derived"
        ),
    )
    print(
        "CANONICAL_COMPLETION_SHEET_SELECTED:",
        False,
    )
    print(
        "CANONICAL_AFFINE_ORIENTATION_SELECTED:",
        False,
    )
    print("NUMERIC_ANGLE_VALUES_DERIVED:", False)
    print("PHYSICAL_CLAIM:", False)
    print("MUTATION_PERFORMED:", False)


if __name__ == "__main__":
    main()
