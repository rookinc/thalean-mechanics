#!/usr/bin/env python3

import contextlib
import io
import pathlib
import runpy
from collections import Counter, defaultdict

SOURCE_070B = (
    pathlib.Path(__file__).resolve().parent
    / "compute_g900_k33_five_four_frame_double_cover_070b.py"
)

capture = io.StringIO()

with contextlib.redirect_stdout(capture):
    namespace = runpy.run_path(str(SOURCE_070B))

data = namespace["data"]
candidate_rows = tuple(namespace["candidate_rows"])
candidate_to_orbit = namespace["candidate_to_orbit"]

source_070 = namespace["namespace"]
source_069 = source_070["namespace"]

splits = tuple(source_069["splits"])
syntheme_rows = tuple(source_069["syntheme_rows"])

ROLES = ("A", "B", "C", "D", "E", "F")

ROLE_REFLECTION = {
    "A": "B",
    "B": "A",
    "C": "E",
    "E": "C",
    "D": "D",
    "F": "F",
}

def role_duad(left, right):
    return tuple(sorted((left, right)))

def canonical_syntheme(duads):
    return tuple(sorted(
        role_duad(*pair)
        for pair in duads
    ))

def canonical_total(synthemes):
    return tuple(sorted(
        canonical_syntheme(syntheme)
        for syntheme in synthemes
    ))

def reflect_total(total):
    return canonical_total(
        tuple(
            tuple(
                role_duad(
                    ROLE_REFLECTION[pair[0]],
                    ROLE_REFLECTION[pair[1]],
                )
                for pair in syntheme
            )
            for syntheme in total
        )
    )

def total_mod_reflection(total):
    reflected = reflect_total(total)
    return min(total, reflected)

STANDARD_FIXED_SYNTHEME = canonical_syntheme((
    ("A", "B"),
    ("C", "E"),
    ("D", "F"),
))

completion_rows = []

for row in candidate_rows:
    split = splits[row["split_id"]]
    closure_side = set(row["closure_side"])

    closure_pair = tuple(row["closure_duad"])
    opposite_pair = tuple(row["opposite_duad"])
    fixed_axis = tuple(row["fixed_axis"])
    selected_corner = tuple(
        row["selected_corner_pair"]
    )

    a_point = min(closure_pair)
    b_point = max(closure_pair)

    f_candidates = closure_side - set(closure_pair)
    f_point = next(iter(f_candidates))

    d_point = next(
        point
        for point in fixed_axis
        if point != f_point
    )

    e_point = next(
        point
        for pair in selected_corner
        if a_point in pair
        for point in pair
        if point != a_point
    )

    c_point = next(
        point
        for point in opposite_pair
        if point != e_point
    )

    role_to_point = {
        "A": a_point,
        "B": b_point,
        "C": c_point,
        "D": d_point,
        "E": e_point,
        "F": f_point,
    }

    point_to_role = {
        point: role
        for role, point in role_to_point.items()
    }

    pulled_synthemes = tuple(
        canonical_syntheme(
            tuple(
                role_duad(
                    point_to_role[pair[0]],
                    point_to_role[pair[1]],
                )
                for pair in syntheme_row["duads"]
            )
        )
        for syntheme_row in syntheme_rows
    )

    pulled_total = canonical_total(
        pulled_synthemes
    )

    reflected_total = reflect_total(
        pulled_total
    )

    reflection_class = total_mod_reflection(
        pulled_total
    )

    completion_rows.append({
        "candidate_id": row["candidate_id"],
        "frame_id": row["frame_id"],
        "native_orbit_id":
            candidate_to_orbit[row["candidate_id"]],
        "role_to_point": role_to_point,
        "pulled_total": pulled_total,
        "reflected_total": reflected_total,
        "reflection_class": reflection_class,
        "contains_standard_fixed_syntheme":
            STANDARD_FIXED_SYNTHEME in pulled_total,
        "reflection_preserves_total":
            reflected_total == pulled_total,
    })

reflection_classes = tuple(sorted({
    row["reflection_class"]
    for row in completion_rows
}))

reflection_class_id = {
    total: class_id
    for class_id, total in enumerate(
        reflection_classes
    )
}

for row in completion_rows:
    row["reflection_class_id"] = (
        reflection_class_id[
            row["reflection_class"]
        ]
    )

orbit_to_class_profile = Counter(
    (
        row["native_orbit_id"],
        row["reflection_class_id"],
    )
    for row in completion_rows
)

frame_class_pair_profile = Counter()

for frame_id in range(60):
    frame_rows = [
        row
        for row in completion_rows
        if row["frame_id"] == frame_id
    ]

    frame_class_pair_profile[
        tuple(sorted(
            row["reflection_class_id"]
            for row in frame_rows
        ))
    ] += 1

class_size_profile = Counter(
    row["reflection_class_id"]
    for row in completion_rows
)

fixed_syntheme_total_classes = defaultdict(set)

for row in completion_rows:
    fixed_syntheme_total_classes[
        STANDARD_FIXED_SYNTHEME
    ].add(row["reflection_class"])

checks = {
    "source_070b_exists":
        SOURCE_070B.is_file(),
    "source_audit_pass":
        data.get("audit_pass") is True,
    "candidate_count_120":
        len(completion_rows) == 120,
    "every_pulled_total_contains_AB_CE_DF":
        all(
            row["contains_standard_fixed_syntheme"]
            for row in completion_rows
        ),
    "every_pulled_total_is_reflection_invariant":
        all(
            row["reflection_preserves_total"]
            for row in completion_rows
        ),
    "exactly_two_reflection_classes":
        len(reflection_classes) == 2,
    "reflection_class_sizes_60_60":
        Counter(class_size_profile.values())
        == Counter({60: 2}),
    "each_base_frame_has_one_of_each_completion_class":
        frame_class_pair_profile
        == Counter({(0, 1): 60}),
    "native_orbits_equal_completion_classes":
        len(orbit_to_class_profile) == 2
        and set(orbit_to_class_profile.values())
        == {60}
        and {
            orbit_id
            for orbit_id, class_id
            in orbit_to_class_profile
        } == {0, 1}
        and {
            class_id
            for orbit_id, class_id
            in orbit_to_class_profile
        } == {0, 1},
    "fixed_syntheme_has_two_total_completions":
        len(
            fixed_syntheme_total_classes[
                STANDARD_FIXED_SYNTHEME
            ]
        ) == 2,
}

failed = [
    name
    for name, passed in checks.items()
    if not passed
]

theorem_pass = not failed

print("PACKET: g900_k33_sheet_synthematic_completion_071")
print("MODE: exact frame-coordinate synthematic completion census")
print("STANDARD_FIXED_SYNTHEME:", STANDARD_FIXED_SYNTHEME)
print("REFLECTION_CLASS_COUNT:", len(reflection_classes))
print("REFLECTION_CLASSES:", reflection_classes)
print(
    "REFLECTION_CLASS_SIZE_PROFILE:",
    dict(sorted(class_size_profile.items())),
)
print(
    "ORBIT_TO_CLASS_PROFILE:",
    dict(sorted(orbit_to_class_profile.items())),
)
print(
    "FRAME_CLASS_PAIR_PROFILE:",
    dict(sorted(frame_class_pair_profile.items())),
)
print("COMPLETION_PREVIEW:", completion_rows[:20])
print("CHECKS:", checks)
print("FAILED_CHECK_COUNT:", len(failed))
print("FAILED_CHECKS:", failed)
print("THEOREM_PASS:", theorem_pass)
print(
    "CLASSIFICATION:",
    (
        "the_two_native_five_four_frame_sheets_are_exactly_"
        "the_two_reflection_invariant_synthematic_total_"
        "completions_of_the_fixed_frame_syntheme_AB_CE_DF"
        if theorem_pass
        else
        "frame_sheet_synthematic_completion_identity_failed"
    ),
)
print("FRAME_SHEET_BIT_DERIVED:", theorem_pass)
print(
    "FRAME_SHEET_BIT_MEANING:",
    "choice_of_synthematic_total_completion_of_AB_CE_DF",
)
print("LOCAL_DISTANCE_SELECTS_COMPLETION:", False)
print("NATIVE_ORBIT_SELECTS_COMPLETION_CLASS:", theorem_pass)
print("ABSOLUTE_COMPLETION_SELECTED:", False)
print("HAND_DRAWING_SELECTS_ONE_COMPLETION:", theorem_pass)
print("NUMERIC_ANGLE_VALUES_DERIVED:", False)
print("PHYSICAL_CLAIM:", False)
print("MUTATION_PERFORMED:", False)
