#!/usr/bin/env python3

import contextlib
import io
import pathlib
import runpy
from collections import Counter

SOURCE_071 = (
    pathlib.Path(__file__).resolve().parent
    / "compute_g900_k33_sheet_synthematic_completion_071.py"
)

capture = io.StringIO()

with contextlib.redirect_stdout(capture):
    namespace = runpy.run_path(str(SOURCE_071))

data = namespace["data"]
completion_rows = tuple(namespace["completion_rows"])
candidate_to_orbit = namespace["candidate_to_orbit"]

source_070b = namespace["namespace"]
candidate_rows = tuple(source_070b["candidate_rows"])
candidate_actions = tuple(source_070b["candidate_actions"])

source_070 = source_070b["namespace"]
source_069 = source_070["namespace"]
valid_rows = tuple(source_069["valid_rows"])

source_068 = source_069["namespace"]
six_register_actions = tuple(
    source_068["six_register_actions"]
)

def compose(left, right):
    return tuple(
        left[right[index]]
        for index in range(len(left))
    )

def inverse(permutation):
    result = [None] * len(permutation)

    for index, image in enumerate(permutation):
        result[image] = index

    return tuple(result)

def permutation_order(permutation):
    identity = tuple(range(len(permutation)))
    current = identity

    for exponent in range(1, 1001):
        current = compose(permutation, current)

        if current == identity:
            return exponent

    return None

def cycle_profile(permutation):
    seen = set()
    profile = []

    for start in range(len(permutation)):
        if start in seen:
            continue

        current = start
        size = 0

        while current not in seen:
            seen.add(current)
            size += 1
            current = permutation[current]

        profile.append(size)

    return tuple(sorted(profile))

action_index_by_six_permutation = {
    permutation: index
    for index, permutation
    in enumerate(six_register_actions)
}

frame_to_candidates = {
    frame_id: tuple(sorted(
        row["candidate_id"]
        for row in candidate_rows
        if row["frame_id"] == frame_id
    ))
    for frame_id in range(len(valid_rows))
}

frame_rows = []

for frame_id, frame in enumerate(valid_rows):
    reflection_map = frame["reflection"]

    reflection = tuple(
        reflection_map[index]
        for index in range(6)
    )

    fixed_points = tuple(
        index
        for index in range(6)
        if reflection[index] == index
    )

    fixed_closure_point = frame[
        "fixed_closure_point"
    ]
    fixed_opposite_point = frame[
        "fixed_opposite_point"
    ]

    centered_roots = tuple(
        permutation
        for permutation in six_register_actions
        if compose(permutation, permutation)
        == reflection
        and permutation[fixed_closure_point]
        == fixed_closure_point
        and permutation[fixed_opposite_point]
        == fixed_opposite_point
    )

    root_action_indices = tuple(
        action_index_by_six_permutation[root]
        for root in centered_roots
    )

    frame_candidates = frame_to_candidates[frame_id]

    root_candidate_images = tuple(
        tuple(
            candidate_actions[action_index][candidate_id]
            for candidate_id in frame_candidates
        )
        for action_index in root_action_indices
    )

    root_sheet_images = tuple(
        tuple(
            candidate_to_orbit[image]
            for image in image_pair
        )
        for image_pair in root_candidate_images
    )

    source_sheets = tuple(
        candidate_to_orbit[candidate_id]
        for candidate_id in frame_candidates
    )

    roots_are_inverse_pair = (
        len(centered_roots) == 2
        and inverse(centered_roots[0])
        == centered_roots[1]
    )

    frame_rows.append({
        "frame_id": frame_id,
        "reflection": reflection,
        "reflection_cycle_profile":
            cycle_profile(reflection),
        "fixed_points": fixed_points,
        "fixed_closure_point":
            fixed_closure_point,
        "fixed_opposite_point":
            fixed_opposite_point,
        "centered_root_count":
            len(centered_roots),
        "centered_roots": centered_roots,
        "centered_root_orders": tuple(
            permutation_order(root)
            for root in centered_roots
        ),
        "centered_root_cycle_profiles": tuple(
            cycle_profile(root)
            for root in centered_roots
        ),
        "roots_are_inverse_pair":
            roots_are_inverse_pair,
        "frame_candidates": frame_candidates,
        "source_sheets": source_sheets,
        "root_candidate_images":
            root_candidate_images,
        "root_sheet_images":
            root_sheet_images,
        "every_root_preserves_each_source_sheet":
            all(
                root_sheet_images[root_index][candidate_index]
                == source_sheets[candidate_index]
                for root_index in range(len(centered_roots))
                for candidate_index in range(
                    len(frame_candidates)
                )
            ),
    })

root_count_profile = Counter(
    row["centered_root_count"]
    for row in frame_rows
)

root_order_profile = Counter(
    order
    for row in frame_rows
    for order in row["centered_root_orders"]
)

root_cycle_profile = Counter(
    profile
    for row in frame_rows
    for profile in row["centered_root_cycle_profiles"]
)

sheet_preservation_profile = Counter(
    row["every_root_preserves_each_source_sheet"]
    for row in frame_rows
)

four_choice_rows = tuple({
    "frame_id": row["frame_id"],
    "completion_sheet_count": 2,
    "affine_root_count": row["centered_root_count"],
    "combined_sheet_root_choice_count":
        2 * row["centered_root_count"],
} for row in frame_rows)

combined_choice_profile = Counter(
    row["combined_sheet_root_choice_count"]
    for row in four_choice_rows
)

checks = {
    "source_071_exists":
        SOURCE_071.is_file(),
    "source_audit_pass":
        data.get("audit_pass") is True,
    "base_frame_count_60":
        len(frame_rows) == 60,
    "every_reflection_has_profile_1_1_2_2":
        all(
            row["reflection_cycle_profile"]
            == (1, 1, 2, 2)
            for row in frame_rows
        ),
    "exactly_two_centered_square_roots_per_frame":
        root_count_profile == Counter({2: 60}),
    "all_centered_roots_have_order_4":
        root_order_profile == Counter({4: 120}),
    "all_centered_roots_have_profile_1_1_4":
        root_cycle_profile
        == Counter({(1, 1, 4): 120}),
    "roots_form_inverse_pairs":
        all(
            row["roots_are_inverse_pair"]
            for row in frame_rows
        ),
    "both_roots_preserve_both_completion_sheets":
        sheet_preservation_profile
        == Counter({True: 60}),
    "each_frame_has_four_independent_sheet_root_choices":
        combined_choice_profile
        == Counter({4: 60}),
}

failed = [
    name
    for name, passed in checks.items()
    if not passed
]

theorem_pass = not failed

orientation_equals_sheet = (
    theorem_pass
    and any(
        not row["every_root_preserves_each_source_sheet"]
        for row in frame_rows
    )
)

print("PACKET: g900_sheet_affine_square_root_join_072")
print("MODE: exact completion-sheet versus affine-root test")
print("BASE_FRAME_COUNT:", len(frame_rows))
print("CENTERED_ROOT_COUNT_PROFILE:", dict(sorted(
    root_count_profile.items()
)))
print("CENTERED_ROOT_ORDER_PROFILE:", dict(sorted(
    root_order_profile.items()
)))
print("CENTERED_ROOT_CYCLE_PROFILE:", dict(sorted(
    root_cycle_profile.items()
)))
print("SHEET_PRESERVATION_PROFILE:", dict(sorted(
    sheet_preservation_profile.items()
)))
print("COMBINED_CHOICE_PROFILE:", dict(sorted(
    combined_choice_profile.items()
)))
print("FRAME_PREVIEW:", frame_rows[:12])
print("CHECKS:", checks)
print("FAILED_CHECK_COUNT:", len(failed))
print("FAILED_CHECKS:", failed)
print("THEOREM_PASS:", theorem_pass)
print(
    "CLASSIFICATION:",
    (
        "each_base_frame_has_two_inverse_centered_order_four_"
        "square_roots_of_its_reflection_and_both_affine_"
        "orientations_preserve_each_of_the_two_synthematic_"
        "completion_sheets_so_sheet_and_affine_orientation_"
        "are_independent_binary_choices"
        if theorem_pass
        else
        "sheet_affine_square_root_relation_not_derived"
    ),
)
print("CENTERED_AFFINE_ROOT_PAIR_DERIVED:", theorem_pass)
print("AFFINE_ROOTS_ARE_INVERSES:", theorem_pass)
print("AFFINE_ROOT_SQUARE_IS_FRAME_REFLECTION:", theorem_pass)
print("SHEET_EQUALS_AFFINE_ORIENTATION:", orientation_equals_sheet)
print("SHEET_AND_AFFINE_ORIENTATION_ARE_INDEPENDENT:",
      theorem_pass and not orientation_equals_sheet)
print("CHOICES_PER_BASE_FRAME:", 4 if theorem_pass else None)
print("MULTIPLIER_2_VERSUS_3_ABSOLUTELY_SELECTED:", False)
print("COMPLETION_SHEET_ABSOLUTELY_SELECTED:", False)
print("NUMERIC_ANGLE_VALUES_DERIVED:", False)
print("PHYSICAL_CLAIM:", False)
print("MUTATION_PERFORMED:", False)
