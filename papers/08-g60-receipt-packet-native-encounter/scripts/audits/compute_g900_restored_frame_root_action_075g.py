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


def normalize_duad(duad):
    return tuple(sorted(
        int(point)
        for point in duad
    ))


def transport_duad(action, duad):
    return tuple(sorted(
        action[point]
        for point in duad
    ))


def reflection_tuple(row):
    reflection = row["reflection"]

    return tuple(
        reflection[index]
        for index in range(6)
    )


def restored_frame_key(
    reflection,
    closure_point,
    opposite_point,
    closure_duad,
):
    return (
        tuple(reflection),
        int(closure_point),
        int(opposite_point),
        normalize_duad(closure_duad),
    )


def orbit_partition(states, transports):
    remaining = set(states)
    orbits = []

    while remaining:
        representative = min(remaining)

        orbit = frozenset(
            permutation[representative]
            for permutation in transports
        )

        if representative not in orbit:
            raise RuntimeError(
                "IDENTITY_MISSING_FROM_RESTORED_ORBIT: "
                f"{representative}"
            )

        reduced = remaining - orbit

        if len(reduced) >= len(remaining):
            raise RuntimeError(
                "RESTORED_ORBIT_NO_PROGRESS: "
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


def main():
    source069 = pathlib.Path(sys.argv[1]).resolve()
    compact_path = pathlib.Path(sys.argv[2]).resolve()

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

    if len(full_frames) != len(compact_frames):
        raise RuntimeError(
            "FULL_COMPACT_FRAME_COUNT_MISMATCH"
        )

    frame_rows = []

    for frame_id, full_row in enumerate(full_frames):
        compact_row = compact_frames[frame_id]

        if (
            reflection_tuple(full_row)
            != tuple(compact_row["reflection"])
        ):
            raise RuntimeError(
                "FRAME_ORDER_REFLECTION_MISMATCH: "
                f"{frame_id}"
            )

        frame_rows.append({
            "frame_id": frame_id,
            "reflection":
                reflection_tuple(full_row),
            "fixed_closure_point":
                full_row["fixed_closure_point"],
            "fixed_opposite_point":
                full_row["fixed_opposite_point"],
            "closure_duad":
                normalize_duad(
                    full_row["closure_duad"]
                ),
            "closure_state":
                full_row["closure_state"],
            "closure_side_id":
                full_row["closure_side_id"],
            "split_id":
                full_row["split_id"],
            "centered_roots": tuple(
                tuple(root)
                for root
                in compact_row["centered_roots"]
            ),
        })

    frame_rows = tuple(frame_rows)

    restored_keys = tuple(
        restored_frame_key(
            row["reflection"],
            row["fixed_closure_point"],
            row["fixed_opposite_point"],
            row["closure_duad"],
        )
        for row in frame_rows
    )

    frame_by_key = {
        key: row["frame_id"]
        for key, row
        in zip(restored_keys, frame_rows)
    }

    root_index = {
        row["frame_id"]: {
            root: root_slot
            for root_slot, root
            in enumerate(row["centered_roots"])
        }
        for row in frame_rows
    }

    states = tuple(
        (frame_id, root_slot)
        for frame_id in range(len(frame_rows))
        for root_slot in range(2)
    )

    state_index = {
        state: index
        for index, state in enumerate(states)
    }

    identity_six = tuple(range(6))

    six_identity_indices = tuple(
        action_id
        for action_id, action in enumerate(actions)
        if action == identity_six
    )

    action_index = {
        action: action_id
        for action_id, action in enumerate(actions)
    }

    transports = []
    failures = []

    for action_id, action in enumerate(actions):
        permutation = []

        for frame_id, root_slot in states:
            frame = frame_rows[frame_id]

            target_reflection = conjugate(
                action,
                frame["reflection"],
            )

            target_closure_point = action[
                frame["fixed_closure_point"]
            ]

            target_opposite_point = action[
                frame["fixed_opposite_point"]
            ]

            target_closure_duad = transport_duad(
                action,
                frame["closure_duad"],
            )

            target_frame = frame_by_key.get(
                restored_frame_key(
                    target_reflection,
                    target_closure_point,
                    target_opposite_point,
                    target_closure_duad,
                )
            )

            if target_frame is None:
                failures.append(
                    (
                        "frame_missing",
                        action_id,
                        frame_id,
                        root_slot,
                        target_closure_duad,
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

    identity_state = tuple(range(len(states)))

    bijective_transport_count = sum(
        None not in permutation
        and len(set(permutation)) == len(states)
        for permutation in transports
    )

    transport_identity_indices = tuple(
        action_id
        for action_id, permutation
        in enumerate(transports)
        if permutation == identity_state
    )

    distinct_transport_count = len(set(transports))

    homomorphism_failure_count = 0
    homomorphism_failure_preview = []

    if not failures:
        for left_id, left in enumerate(actions):
            for right_id, right in enumerate(actions):
                product = compose(left, right)
                product_id = action_index.get(product)

                if product_id is None:
                    homomorphism_failure_count += 1

                    if (
                        len(homomorphism_failure_preview)
                        < 20
                    ):
                        homomorphism_failure_preview.append(
                            (
                                "six_product_missing",
                                left_id,
                                right_id,
                            )
                        )

                    continue

                transported_product = compose(
                    transports[left_id],
                    transports[right_id],
                )

                if (
                    transported_product
                    != transports[product_id]
                ):
                    homomorphism_failure_count += 1

                    if (
                        len(homomorphism_failure_preview)
                        < 20
                    ):
                        homomorphism_failure_preview.append(
                            (
                                "lift_product_mismatch",
                                left_id,
                                right_id,
                                product_id,
                            )
                        )

    orbits = ()

    if (
        not failures
        and bijective_transport_count
        == len(actions)
        and len(transport_identity_indices) == 1
        and homomorphism_failure_count == 0
    ):
        orbits = orbit_partition(
            tuple(range(len(states))),
            transports,
        )

    state_to_orbit = {
        state_id: orbit_id
        for orbit_id, orbit in enumerate(orbits)
        for state_id in orbit
    }

    root_pair_orbit_profile = Counter()

    if orbits:
        for frame_id in range(len(frame_rows)):
            root_pair_orbit_profile[
                (
                    state_to_orbit[
                        state_index[(frame_id, 0)]
                    ],
                    state_to_orbit[
                        state_index[(frame_id, 1)]
                    ],
                )
            ] += 1

    orbit_rows = []

    for orbit_id, orbit in enumerate(orbits):
        frame_ids = {
            states[state_id][0]
            for state_id in orbit
        }

        orbit_rows.append({
            "orbit_id": orbit_id,
            "orbit_size": len(orbit),
            "frame_count": len(frame_ids),
            "root_slot_profile": dict(sorted(
                Counter(
                    states[state_id][1]
                    for state_id in orbit
                ).items()
            )),
            "closure_side_profile": dict(sorted(
                Counter(
                    frame_rows[
                        states[state_id][0]
                    ]["closure_side_id"]
                    for state_id in orbit
                ).items()
            )),
            "split_profile": dict(sorted(
                Counter(
                    frame_rows[
                        states[state_id][0]
                    ]["split_id"]
                    for state_id in orbit
                ).items()
            )),
            "state_preview": tuple(
                states[state_id]
                for state_id in sorted(orbit)[:20]
            ),
        })

    native_exchanges_roots = (
        bool(orbits)
        and all(
            state_to_orbit[state_index[(frame_id, 0)]]
            == state_to_orbit[
                state_index[(frame_id, 1)]
            ]
            for frame_id in range(len(frame_rows))
        )
    )

    affine_orientation_class_survives = (
        len(orbits) == 2
        and not native_exchanges_roots
        and all(
            state_to_orbit[state_index[(frame_id, 0)]]
            != state_to_orbit[
                state_index[(frame_id, 1)]
            ]
            for frame_id in range(len(frame_rows))
        )
    )

    checks = {
        "source_069_exists":
            source069.is_file(),
        "source_069_theorem_pass":
            namespace.get("theorem_pass") is True,
        "compact_packet_match":
            compact.get("packet")
            == "g900_frame_root_compact_export_072",
        "compact_source_theorem_pass":
            compact.get("source_072_theorem_pass")
            is True,
        "full_frame_count_60":
            len(frame_rows) == 60,
        "restored_key_count_60":
            len(set(restored_keys)) == 60,
        "frame_root_state_count_120":
            len(states) == 120,
        "six_action_count_120":
            len(actions) == 120,
        "six_identity_exists_once":
            len(six_identity_indices) == 1,
        "transport_failure_count_zero":
            not failures,
        "all_transports_bijective":
            bijective_transport_count == 120,
        "transport_identity_exists_once":
            len(transport_identity_indices) == 1,
        "transport_action_count_distinct_120":
            distinct_transport_count == 120,
        "homomorphism_failure_count_zero":
            homomorphism_failure_count == 0,
        "orbits_partition_120":
            bool(orbits)
            and sum(map(len, orbits)) == 120
            and len(set().union(*orbits)) == 120,
    }

    failed = [
        name
        for name, passed in checks.items()
        if not passed
    ]

    theorem_pass = not failed

    if theorem_pass and native_exchanges_roots:
        classification = (
            "after_restoring_the_closure_duad_coordinate_"
            "the_full_native_order_120_action_is_bijective_"
            "and_exchanges_the_two_centered_roots_so_no_"
            "absolute_affine_orientation_survives"
        )
    elif (
        theorem_pass
        and affine_orientation_class_survives
    ):
        classification = (
            "after_restoring_the_closure_duad_coordinate_"
            "the_full_native_order_120_action_is_bijective_"
            "and_the_two_centered_roots_form_two_distinct_"
            "native_affine_orientation_orbits"
        )
    elif theorem_pass:
        classification = (
            "after_restoring_the_closure_duad_coordinate_"
            "the_full_native_action_is_bijective_with_a_"
            "nonbinary_frame_root_orbit_structure"
        )
    else:
        classification = (
            "restored_closure_duad_frame_root_action_failed"
        )

    print(
        "PACKET:",
        "g900_restored_frame_root_action_075g",
    )
    print(
        "MODE:",
        "closure-duad-restored full frame-root action census",
    )
    print("FULL_FRAME_COUNT:", len(frame_rows))
    print(
        "RESTORED_FRAME_KEY_COUNT:",
        len(set(restored_keys)),
    )
    print("FRAME_ROOT_STATE_COUNT:", len(states))
    print("SIX_ACTION_COUNT:", len(actions))
    print(
        "SIX_IDENTITY_INDICES:",
        six_identity_indices,
    )
    print(
        "TRANSPORT_FAILURE_COUNT:",
        len(failures),
    )
    print(
        "TRANSPORT_FAILURE_PREVIEW:",
        failures[:30],
    )
    print(
        "BIJECTIVE_TRANSPORT_COUNT:",
        bijective_transport_count,
    )
    print(
        "DISTINCT_TRANSPORT_COUNT:",
        distinct_transport_count,
    )
    print(
        "TRANSPORT_IDENTITY_INDICES:",
        transport_identity_indices,
    )
    print(
        "HOMOMORPHISM_FAILURE_COUNT:",
        homomorphism_failure_count,
    )
    print(
        "HOMOMORPHISM_FAILURE_PREVIEW:",
        homomorphism_failure_preview,
    )
    print("FRAME_ROOT_ORBIT_COUNT:", len(orbits))
    print(
        "FRAME_ROOT_ORBIT_SIZE_PROFILE:",
        dict(sorted(
            Counter(
                len(orbit)
                for orbit in orbits
            ).items()
        )),
    )
    print("FRAME_ROOT_ORBIT_ROWS:", orbit_rows)
    print(
        "ROOT_PAIR_ORBIT_PROFILE:",
        dict(sorted(
            root_pair_orbit_profile.items()
        )),
    )
    print(
        "NATIVE_EXCHANGES_INVERSE_ROOTS:",
        native_exchanges_roots,
    )
    print(
        "AFFINE_ORIENTATION_CLASS_SURVIVES:",
        affine_orientation_class_survives,
    )

    if theorem_pass:
        print(
            "COMBINED_SHEET_ROOT_ORBIT_COUNT:",
            2 * len(orbits),
        )
        print(
            "COMBINED_SHEET_ROOT_ORBIT_SIZES:",
            tuple(sorted(
                len(orbit)
                for orbit in orbits
                for sheet in range(2)
            )),
        )

    print("SHEET_PRESERVATION_IMPORTED_FROM_072:", True)
    print("CHECKS:", checks)
    print("FAILED_CHECK_COUNT:", len(failed))
    print("FAILED_CHECKS:", failed)
    print("THEOREM_PASS:", theorem_pass)
    print("CLASSIFICATION:", classification)
    print("CANONICAL_SHEET_SELECTED:", False)
    print("CANONICAL_AFFINE_ROOT_SELECTED:", False)
    print("NUMERIC_ANGLE_VALUES_DERIVED:", False)
    print("PHYSICAL_CLAIM:", False)
    print("MUTATION_PERFORMED:", False)


if __name__ == "__main__":
    main()
