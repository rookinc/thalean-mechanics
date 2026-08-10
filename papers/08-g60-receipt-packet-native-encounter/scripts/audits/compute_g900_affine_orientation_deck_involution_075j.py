#!/usr/bin/env python3

import ast
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


def read_orbits(ledger_path):
    for line in ledger_path.read_text(
        encoding="utf-8"
    ).splitlines():
        prefix = "FRAME_ROOT_ORBIT_ROWS: "

        if line.startswith(prefix):
            return ast.literal_eval(
                line[len(prefix):]
            )

    raise RuntimeError(
        "FRAME_ROOT_ORBIT_ROWS_NOT_FOUND"
    )


def main():
    source069 = pathlib.Path(sys.argv[1]).resolve()
    compact_path = pathlib.Path(sys.argv[2]).resolve()
    ledger_path = pathlib.Path(sys.argv[3]).resolve()

    captured = io.StringIO()

    with contextlib.redirect_stdout(captured):
        namespace = runpy.run_path(str(source069))

    full_frames = tuple(namespace["valid_rows"])

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

    states = tuple(
        (frame_id, root_slot)
        for frame_id in range(len(frames))
        for root_slot in range(2)
    )

    state_index = {
        state: index
        for index, state in enumerate(states)
    }

    transports = []
    failures = []

    for action_id, action in enumerate(actions):
        permutation = []

        for frame_id, root_slot in states:
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
                failures.append(
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
                failures.append(
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
                state_index[
                    (
                        target_frame,
                        target_root_slot,
                    )
                ]
            )

        transports.append(tuple(permutation))

    transports = tuple(transports)

    deck = []

    for frame_id, root_slot in states:
        root = frames[frame_id][
            "centered_roots"
        ][root_slot]

        inverse_root = inverse(root)

        inverse_slot = root_index[
            frame_id
        ].get(inverse_root)

        if inverse_slot is None:
            raise RuntimeError(
                "INVERSE_ROOT_MISSING: "
                f"{frame_id} {root_slot}"
            )

        deck.append(
            state_index[
                (
                    frame_id,
                    inverse_slot,
                )
            ]
        )

    deck = tuple(deck)

    identity = tuple(range(len(states)))

    deck_is_involution = (
        compose(deck, deck) == identity
    )

    deck_fixed_points = tuple(
        state_id
        for state_id, image in enumerate(deck)
        if state_id == image
    )

    commutation_failures = []

    for action_id, transport in enumerate(transports):
        if None in transport:
            continue

        if (
            compose(deck, transport)
            != compose(transport, deck)
        ):
            commutation_failures.append(action_id)

    orbit_rows = read_orbits(ledger_path)

    state_to_orbit = {
        state_index[tuple(state)]:
            row["orbit_id"]
        for row in orbit_rows
        for state in row["states"]
    }

    deck_orbit_profile = Counter(
        (
            state_to_orbit[state_id],
            state_to_orbit[deck[state_id]],
        )
        for state_id in range(len(states))
    )

    deck_exchanges_orbits = (
        len(orbit_rows) == 2
        and all(
            state_to_orbit[deck[state_id]]
            != state_to_orbit[state_id]
            for state_id in range(len(states))
        )
    )

    orbit_projection_rows = []

    for row in orbit_rows:
        orbit_states = tuple(
            state_index[tuple(state)]
            for state in row["states"]
        )

        projected_frames = tuple(
            states[state_id][0]
            for state_id in orbit_states
        )

        orbit_projection_rows.append({
            "orbit_id": row["orbit_id"],
            "orbit_size": len(orbit_states),
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
        })

    each_orbit_projects_bijectively = all(
        row["orbit_size"] == 60
        and row["projected_frame_count"] == 60
        and row[
            "frame_multiplicity_profile"
        ] == {1: 60}
        for row in orbit_projection_rows
    )

    deck_preserves_base_frame = all(
        states[deck[state_id]][0]
        == states[state_id][0]
        for state_id in range(len(states))
    )

    checks = {
        "source_069_exists":
            source069.is_file(),
        "source_069_theorem_pass":
            namespace.get("theorem_pass") is True,
        "compact_source_pass":
            compact.get("source_072_theorem_pass")
            is True,
        "frame_count_60":
            len(frames) == 60,
        "state_count_120":
            len(states) == 120,
        "restored_key_count_60":
            len(frame_by_key) == 60,
        "transport_failure_count_zero":
            not failures,
        "deck_is_bijection":
            len(set(deck)) == 120,
        "deck_is_involution":
            deck_is_involution,
        "deck_has_no_fixed_state":
            not deck_fixed_points,
        "deck_preserves_base_frame":
            deck_preserves_base_frame,
        "deck_commutes_with_all_native_actions":
            not commutation_failures,
        "two_native_orbits":
            len(orbit_rows) == 2,
        "deck_exchanges_native_orbits":
            deck_exchanges_orbits,
        "each_orbit_projects_bijectively":
            each_orbit_projects_bijectively,
    }

    failed = [
        name
        for name, passed in checks.items()
        if not passed
    ]

    theorem_pass = not failed

    print(
        "PACKET:",
        "g900_affine_orientation_deck_involution_075j",
    )
    print(
        "MODE:",
        "exact root-inversion deck transformation audit",
    )
    print("BASE_FRAME_COUNT:", len(frames))
    print("FRAME_ROOT_STATE_COUNT:", len(states))
    print(
        "TRANSPORT_FAILURE_COUNT:",
        len(failures),
    )
    print("DECK_MAP_SIZE:", len(deck))
    print(
        "DECK_IS_INVOLUTION:",
        deck_is_involution,
    )
    print(
        "DECK_FIXED_POINT_COUNT:",
        len(deck_fixed_points),
    )
    print(
        "DECK_PRESERVES_BASE_FRAME:",
        deck_preserves_base_frame,
    )
    print(
        "DECK_COMMUTATION_FAILURE_COUNT:",
        len(commutation_failures),
    )
    print(
        "DECK_COMMUTATION_FAILURES:",
        commutation_failures[:30],
    )
    print(
        "DECK_ORBIT_PROFILE:",
        dict(sorted(deck_orbit_profile.items())),
    )
    print(
        "DECK_EXCHANGES_ORBITS:",
        deck_exchanges_orbits,
    )
    print(
        "ORBIT_PROJECTION_ROWS:",
        orbit_projection_rows,
    )
    print(
        "EACH_ORBIT_PROJECTS_BIJECTIVELY:",
        each_orbit_projects_bijectively,
    )
    print("CHECKS:", checks)
    print("FAILED_CHECK_COUNT:", len(failed))
    print("FAILED_CHECKS:", failed)
    print("THEOREM_PASS:", theorem_pass)

    if theorem_pass:
        classification = (
            "the_restored_frame_root_register_is_a_"
            "two_sheeted_native_cover_of_the_sixty_"
            "frame_register_and_root_inversion_is_a_"
            "fixed_point_free_central_deck_involution_"
            "exchanging_the_two_affine_orientation_sheets"
        )
    else:
        classification = (
            "root_inversion_does_not_yet_establish_the_"
            "affine_orientation_double_cover"
        )

    print("CLASSIFICATION:", classification)
    print("LOCAL_ROOT_SLOT_NAMES_SHEET:", False)
    print("LOCAL_CORNER_MATCHING_NAMES_SHEET:", False)
    print("ABSOLUTE_ORIENTATION_SELECTED:", False)
    print("PHYSICAL_CLAIM:", False)
    print("MUTATION_PERFORMED:", False)


if __name__ == "__main__":
    main()
