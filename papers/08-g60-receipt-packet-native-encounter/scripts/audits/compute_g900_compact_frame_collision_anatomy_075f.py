#!/usr/bin/env python3

import contextlib
import io
import pathlib
import runpy
import sys
from collections import Counter, defaultdict


def freeze(value):
    if isinstance(value, dict):
        return tuple(sorted(
            (
                freeze(key),
                freeze(item),
            )
            for key, item in value.items()
        ))

    if isinstance(value, (list, tuple, set, frozenset)):
        return tuple(
            freeze(item)
            for item in value
        )

    return value


def compact_key(row):
    reflection_map = row["reflection"]

    reflection = tuple(
        reflection_map[index]
        for index in range(6)
    )

    return (
        reflection,
        row["fixed_closure_point"],
        row["fixed_opposite_point"],
    )


def field_value(row, field):
    if field not in row:
        return ("MISSING",)

    return freeze(row[field])


def main():
    source_path = pathlib.Path(sys.argv[1]).resolve()

    captured = io.StringIO()

    with contextlib.redirect_stdout(captured):
        namespace = runpy.run_path(str(source_path))

    source_stdout = captured.getvalue()

    valid_rows = namespace.get("valid_rows")

    if not isinstance(valid_rows, (list, tuple)):
        print(
            "PACKET:",
            "g900_compact_frame_collision_anatomy_075f",
        )
        print("SOURCE069:", source_path)
        print(
            "CAPTURED_STDOUT_LINE_COUNT:",
            len(source_stdout.splitlines()),
        )
        print("VALID_ROWS_EXPOSED:", False)
        print(
            "NAMESPACE_KEYS:",
            tuple(sorted(namespace))[:100],
        )
        print("THEOREM_PASS:", False)
        print(
            "CLASSIFICATION:",
            "source_069_does_not_expose_valid_rows",
        )
        print("MUTATION_PERFORMED:", False)
        return

    rows = tuple(valid_rows)

    groups = defaultdict(list)

    for frame_id, row in enumerate(rows):
        groups[compact_key(row)].append(
            (frame_id, row)
        )

    group_size_profile = Counter(
        len(members)
        for members in groups.values()
    )

    all_fields = tuple(sorted(
        set().union(
            *(
                set(row)
                for row in rows
            )
        )
    ))

    ignored_fields = {
        "frame_id",
        "candidate_id",
    }

    candidate_fields = tuple(
        field
        for field in all_fields
        if field not in ignored_fields
    )

    field_pair_difference_count = Counter()
    field_augmented_key_count = {}
    exact_separator_fields = []

    for field in candidate_fields:
        difference_count = sum(
            field_value(members[0][1], field)
            != field_value(members[1][1], field)
            for members in groups.values()
            if len(members) == 2
        )

        field_pair_difference_count[field] = (
            difference_count
        )

        augmented_keys = {
            (
                compact_key(row),
                field_value(row, field),
            )
            for row in rows
        }

        field_augmented_key_count[field] = len(
            augmented_keys
        )

        if (
            difference_count == len(groups)
            and len(augmented_keys) == len(rows)
        ):
            exact_separator_fields.append(field)

    pair_rows = []
    difference_signature_profile = Counter()

    for pair_id, (key, members) in enumerate(
        sorted(
            groups.items(),
            key=lambda item: min(
                frame_id
                for frame_id, row in item[1]
            ),
        )
    ):
        frame_ids = tuple(
            frame_id
            for frame_id, row in members
        )

        if len(members) == 2:
            left = members[0][1]
            right = members[1][1]

            differing_fields = tuple(
                field
                for field in candidate_fields
                if field_value(left, field)
                != field_value(right, field)
            )
        else:
            differing_fields = ()

        difference_signature_profile[
            differing_fields
        ] += 1

        if pair_id < 30:
            field_differences = {
                field: (
                    field_value(members[0][1], field),
                    field_value(members[1][1], field),
                )
                for field in differing_fields
            } if len(members) == 2 else {}

            pair_rows.append({
                "pair_id": pair_id,
                "frame_ids": frame_ids,
                "compact_key": key,
                "differing_fields":
                    differing_fields,
                "field_differences":
                    field_differences,
            })

    always_equal_fields = tuple(
        field
        for field in candidate_fields
        if field_pair_difference_count[field] == 0
    )

    sometimes_different_fields = tuple(
        field
        for field in candidate_fields
        if (
            0
            < field_pair_difference_count[field]
            < len(groups)
        )
    )

    always_different_fields = tuple(
        field
        for field in candidate_fields
        if field_pair_difference_count[field]
        == len(groups)
    )

    separator_value_profiles = {}

    for field in exact_separator_fields:
        separator_value_profiles[field] = dict(
            sorted(
                Counter(
                    repr(field_value(row, field))
                    for row in rows
                ).items()
            )
        )

    checks = {
        "source_069_exists":
            source_path.is_file(),
        "source_069_audit_pass":
            namespace.get("theorem_pass") is True,
        "valid_row_count_60":
            len(rows) == 60,
        "compact_key_count_30":
            len(groups) == 30,
        "every_compact_key_has_two_frames":
            group_size_profile == Counter({2: 30}),
        "collision_pairs_cover_all_frames":
            sum(map(len, groups.values())) == 60,
        "exact_separator_field_exists":
            bool(exact_separator_fields),
    }

    failed = [
        name
        for name, passed in checks.items()
        if not passed
    ]

    theorem_pass = not failed

    print(
        "PACKET:",
        "g900_compact_frame_collision_anatomy_075f",
    )
    print(
        "MODE:",
        "full-frame versus compact-key collision anatomy",
    )
    print("SOURCE069:", source_path)
    print(
        "CAPTURED_STDOUT_LINE_COUNT:",
        len(source_stdout.splitlines()),
    )
    print("VALID_FRAME_COUNT:", len(rows))
    print("FULL_FIELD_COUNT:", len(all_fields))
    print("FULL_FIELDS:", all_fields)
    print("COMPACT_KEY_COUNT:", len(groups))
    print(
        "COMPACT_KEY_GROUP_SIZE_PROFILE:",
        dict(sorted(group_size_profile.items())),
    )
    print(
        "ALWAYS_EQUAL_FIELDS:",
        always_equal_fields,
    )
    print(
        "SOMETIMES_DIFFERENT_FIELDS:",
        sometimes_different_fields,
    )
    print(
        "ALWAYS_DIFFERENT_FIELDS:",
        always_different_fields,
    )
    print(
        "EXACT_SEPARATOR_FIELDS:",
        tuple(exact_separator_fields),
    )
    print(
        "FIELD_PAIR_DIFFERENCE_COUNT:",
        dict(sorted(
            field_pair_difference_count.items()
        )),
    )
    print(
        "FIELD_AUGMENTED_KEY_COUNT:",
        dict(sorted(
            field_augmented_key_count.items()
        )),
    )
    print(
        "SEPARATOR_VALUE_PROFILES:",
        separator_value_profiles,
    )
    print(
        "DIFFERENCE_SIGNATURE_PROFILE:",
        dict(sorted(
            (
                repr(signature),
                count,
            )
            for signature, count
            in difference_signature_profile.items()
        )),
    )
    print("PAIR_ROWS:", pair_rows)
    print("CHECKS:", checks)
    print("FAILED_CHECK_COUNT:", len(failed))
    print("FAILED_CHECKS:", failed)
    print("THEOREM_PASS:", theorem_pass)

    if theorem_pass:
        classification = (
            "the_thirty_two_to_one_compact_frame_"
            "collisions_are_completely_resolved_by_"
            "the_reported_full_frame_separator_fields"
        )
    else:
        classification = (
            "compact_frame_collision_coordinate_"
            "not_yet_isolated"
        )

    print("CLASSIFICATION:", classification)
    print("NATIVE_QUOTIENT_DERIVED:", False)
    print("LOSSY_EXPORT_CONFIRMED:", theorem_pass)
    print("REPOSITORY_MUTATION: none")


if __name__ == "__main__":
    main()
