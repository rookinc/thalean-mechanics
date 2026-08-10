#!/usr/bin/env python3

import ast
import contextlib
import io
import json
import pathlib
import runpy
import sys
from collections import Counter


def edge(value):
    return tuple(sorted(
        int(point)
        for point in value
    ))


def edge_pair(value):
    return tuple(sorted(
        edge(item)
        for item in value
    ))


def main():
    source069 = pathlib.Path(sys.argv[1]).resolve()
    compact_path = pathlib.Path(sys.argv[2]).resolve()
    ledger_path = pathlib.Path(sys.argv[3]).resolve()

    captured = io.StringIO()

    with contextlib.redirect_stdout(captured):
        namespace = runpy.run_path(str(source069))

    frames = tuple(namespace["valid_rows"])

    compact = json.loads(
        compact_path.read_text(encoding="utf-8")
    )

    compact_frames = {
        row["frame_id"]: row
        for row in compact["frames"]
    }

    orbit_rows = None

    for line in ledger_path.read_text(
        encoding="utf-8"
    ).splitlines():
        prefix = "FRAME_ROOT_ORBIT_ROWS: "

        if line.startswith(prefix):
            orbit_rows = ast.literal_eval(
                line[len(prefix):]
            )
            break

    if orbit_rows is None:
        raise RuntimeError(
            "ORBIT_ROWS_NOT_FOUND_IN_LEDGER"
        )

    state_to_orbit = {
        tuple(state): row["orbit_id"]
        for row in orbit_rows
        for state in row["states"]
    }

    rows = []
    profile = Counter()
    unmatched = []

    for frame_id, frame in enumerate(frames):
        closure_duad = edge(frame["closure_duad"])
        opposite_duad = edge(
            frame["opposite_same_side_duad"]
        )

        corner_zero = edge_pair(
            frame["corner_pair_0"]
        )

        corner_one = edge_pair(
            frame["corner_pair_1"]
        )

        roots = tuple(
            tuple(root)
            for root in compact_frames[
                frame_id
            ]["centered_roots"]
        )

        for root_slot, root in enumerate(roots):
            induced_matching = edge_pair(
                tuple(
                    edge((
                        source_point,
                        root[source_point],
                    ))
                    for source_point in closure_duad
                )
            )

            root_maps_closure_to_opposite = (
                tuple(sorted(
                    root[source_point]
                    for source_point in closure_duad
                ))
                == opposite_duad
            )

            if induced_matching == corner_zero:
                corner_index = 0
            elif induced_matching == corner_one:
                corner_index = 1
            else:
                corner_index = None
                unmatched.append({
                    "frame_id": frame_id,
                    "root_slot": root_slot,
                    "closure_duad": closure_duad,
                    "opposite_duad": opposite_duad,
                    "induced_matching":
                        induced_matching,
                    "corner_pair_0": corner_zero,
                    "corner_pair_1": corner_one,
                })

            orbit_id = state_to_orbit[
                (frame_id, root_slot)
            ]

            profile[
                (
                    orbit_id,
                    corner_index,
                )
            ] += 1

            rows.append({
                "frame_id": frame_id,
                "root_slot": root_slot,
                "orbit_id": orbit_id,
                "corner_matching_index":
                    corner_index,
                "root_maps_closure_to_opposite":
                    root_maps_closure_to_opposite,
                "closure_duad": closure_duad,
                "opposite_duad": opposite_duad,
                "induced_matching":
                    induced_matching,
            })

    orbit_to_corner_sets = {
        orbit_id: tuple(sorted({
            row["corner_matching_index"]
            for row in rows
            if row["orbit_id"] == orbit_id
        }))
        for orbit_id in sorted({
            row["orbit_id"]
            for row in rows
        })
    }

    corner_to_orbit_sets = {
        corner_index: tuple(sorted({
            row["orbit_id"]
            for row in rows
            if (
                row["corner_matching_index"]
                == corner_index
            )
        }))
        for corner_index in (0, 1)
    }

    corner_matching_selects_orbit = (
        len(orbit_to_corner_sets) == 2
        and all(
            len(values) == 1
            for values
            in orbit_to_corner_sets.values()
        )
        and all(
            len(values) == 1
            for values
            in corner_to_orbit_sets.values()
        )
        and (
            set(
                values[0]
                for values
                in orbit_to_corner_sets.values()
            )
            == {0, 1}
        )
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
        "ledger_state_count_120":
            len(state_to_orbit) == 120,
        "state_row_count_120":
            len(rows) == 120,
        "every_root_maps_closure_to_opposite":
            all(
                row[
                    "root_maps_closure_to_opposite"
                ]
                for row in rows
            ),
        "every_root_matches_one_corner_pair":
            not unmatched,
        "corner_matching_selects_orbit":
            corner_matching_selects_orbit,
    }

    failed = [
        name
        for name, passed in checks.items()
        if not passed
    ]

    theorem_pass = not failed

    print(
        "PACKET:",
        "g900_affine_orientation_corner_matching_075i",
    )
    print(
        "MODE:",
        "exact centered-root corner-matching invariant test",
    )
    print("FRAME_COUNT:", len(frames))
    print("STATE_COUNT:", len(rows))
    print(
        "CORNER_MATCHING_ORBIT_PROFILE:",
        dict(sorted(profile.items())),
    )
    print(
        "ORBIT_TO_CORNER_SETS:",
        orbit_to_corner_sets,
    )
    print(
        "CORNER_TO_ORBIT_SETS:",
        corner_to_orbit_sets,
    )
    print(
        "UNMATCHED_COUNT:",
        len(unmatched),
    )
    print(
        "UNMATCHED_PREVIEW:",
        unmatched[:20],
    )
    print("ROW_PREVIEW:", rows[:20])
    print("CHECKS:", checks)
    print("FAILED_CHECK_COUNT:", len(failed))
    print("FAILED_CHECKS:", failed)
    print("THEOREM_PASS:", theorem_pass)

    if theorem_pass:
        classification = (
            "the_two_native_affine_orientation_orbits_"
            "are_exactly_the_two_centered_root_corner_"
            "matchings_between_the_closure_duad_and_"
            "its_opposite_same_side_duad"
        )
    else:
        classification = (
            "corner_matching_does_not_alone_name_the_"
            "native_affine_orientation_orbits"
        )

    print("CLASSIFICATION:", classification)
    print(
        "ABSOLUTE_ORIENTATION_SELECTED:",
        False,
    )
    print("PHYSICAL_CLAIM:", False)
    print("MUTATION_PERFORMED:", False)


if __name__ == "__main__":
    main()
