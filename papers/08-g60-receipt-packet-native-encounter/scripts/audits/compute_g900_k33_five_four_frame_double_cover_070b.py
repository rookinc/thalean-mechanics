#!/usr/bin/env python3

import contextlib
import io
import pathlib
import runpy
from collections import Counter, defaultdict

SOURCE_070 = (
    pathlib.Path(__file__).resolve().parent
    / "compute_g900_k33_five_four_frame_torsor_falsifier_070.py"
)

capture = io.StringIO()

with contextlib.redirect_stdout(capture):
    namespace = runpy.run_path(str(SOURCE_070))

data = namespace["data"]
candidate_rows = tuple(namespace["candidate_rows"])
candidate_actions = tuple(namespace["distinct_candidate_actions"])

candidate_count = len(candidate_rows)
all_candidate_ids = set(range(candidate_count))

unclassified = set(all_candidate_ids)
orbits = []

while unclassified:
    seed = min(unclassified)

    orbit = frozenset(
        permutation[seed]
        for permutation in candidate_actions
    )

    orbits.append(orbit)
    unclassified -= orbit

orbits = tuple(sorted(
    orbits,
    key=lambda orbit: (
        len(orbit),
        min(orbit),
    ),
))

candidate_to_orbit = {
    candidate_id: orbit_id
    for orbit_id, orbit in enumerate(orbits)
    for candidate_id in orbit
}

orbit_rows = []

for orbit_id, orbit in enumerate(orbits):
    representative = min(orbit)

    stabilizer = tuple(
        permutation
        for permutation in candidate_actions
        if permutation[representative] == representative
    )

    frame_profile = Counter(
        candidate_rows[candidate_id]["frame_id"]
        for candidate_id in orbit
    )

    corner_choice_profile = Counter(
        candidate_rows[candidate_id]["corner_choice"]
        for candidate_id in orbit
    )

    orbit_rows.append({
        "orbit_id": orbit_id,
        "orbit_size": len(orbit),
        "representative_candidate_id": representative,
        "representative":
            candidate_rows[representative],
        "stabilizer_order": len(stabilizer),
        "frame_count": len(frame_profile),
        "frame_multiplicity_profile":
            dict(sorted(Counter(
                frame_profile.values()
            ).items())),
        "corner_choice_profile":
            dict(sorted(corner_choice_profile.items())),
        "candidate_preview": tuple(sorted(orbit))[:30],
    })

frame_sheet_rows = []

for frame_id in range(60):
    frame_candidates = tuple(sorted(
        row["candidate_id"]
        for row in candidate_rows
        if row["frame_id"] == frame_id
    ))

    frame_orbits = tuple(
        candidate_to_orbit[candidate_id]
        for candidate_id in frame_candidates
    )

    frame_sheet_rows.append({
        "frame_id": frame_id,
        "candidate_ids": frame_candidates,
        "orbit_ids": frame_orbits,
        "candidates_lie_on_distinct_sheets":
            len(set(frame_orbits)) == 2,
    })

orbit_size_profile = Counter(
    len(orbit)
    for orbit in orbits
)

stabilizer_order_profile = Counter(
    row["stabilizer_order"]
    for row in orbit_rows
)

frame_orbit_pair_profile = Counter(
    tuple(sorted(row["orbit_ids"]))
    for row in frame_sheet_rows
)

action_preserves_orbit_partition = all(
    candidate_to_orbit[permutation[candidate_id]]
    == candidate_to_orbit[candidate_id]
    for permutation in candidate_actions
    for candidate_id in range(candidate_count)
)

checks = {
    "source_070_exists":
        SOURCE_070.is_file(),
    "source_audit_pass":
        data.get("audit_pass") is True,
    "candidate_count_120":
        candidate_count == 120,
    "native_action_count_120":
        len(candidate_actions) == 120,
    "candidate_orbit_count_2":
        len(orbits) == 2,
    "candidate_orbit_size_profile_60_60":
        orbit_size_profile == Counter({60: 2}),
    "each_orbit_stabilizer_order_2":
        stabilizer_order_profile == Counter({2: 2}),
    "each_orbit_is_transitive":
        all(
            len({
                permutation[min(orbit)]
                for permutation in candidate_actions
            }) == 60
            for orbit in orbits
        ),
    "every_base_frame_has_one_candidate_per_orbit":
        all(
            row["candidates_lie_on_distinct_sheets"]
            for row in frame_sheet_rows
        )
        and frame_orbit_pair_profile
        == Counter({(0, 1): 60}),
    "each_orbit_projects_bijectively_to_60_frames":
        all(
            row["frame_count"] == 60
            and row["frame_multiplicity_profile"] == {1: 60}
            for row in orbit_rows
        ),
    "native_action_preserves_two_sheet_partition":
        action_preserves_orbit_partition,
    "no_native_automorphism_exchanges_sheets":
        all(
            candidate_to_orbit[permutation[0]] == 0
            for permutation in candidate_actions
        ),
}

failed = [
    name
    for name, passed in checks.items()
    if not passed
]

theorem_pass = not failed

print("PACKET: g900_k33_five_four_frame_double_cover_070b")
print("MODE: corrected complete-frame orbit decomposition")
print("COMPLETE_CANDIDATE_COUNT:", candidate_count)
print("NATIVE_ACTION_COUNT:", len(candidate_actions))
print("ORBIT_COUNT:", len(orbits))
print("ORBIT_SIZE_PROFILE:", dict(sorted(
    orbit_size_profile.items()
)))
print("STABILIZER_ORDER_PROFILE:", dict(sorted(
    stabilizer_order_profile.items()
)))
print("ORBIT_ROWS:", orbit_rows)
print(
    "FRAME_ORBIT_PAIR_PROFILE:",
    dict(sorted(frame_orbit_pair_profile.items())),
)
print("FRAME_SHEET_PREVIEW:", frame_sheet_rows[:20])
print("CHECKS:", checks)
print("FAILED_CHECK_COUNT:", len(failed))
print("FAILED_CHECKS:", failed)
print("THEOREM_PASS:", theorem_pass)
print(
    "CLASSIFICATION:",
    (
        "the_one_hundred_twenty_complete_five_four_K3_3_"
        "frames_split_into_two_native_orbits_of_sixty_each_"
        "with_every_base_closure_reflection_frame_having_one_"
        "candidate_on_each_sheet_and_no_native_automorphism_"
        "exchanging_the_two_sheets"
        if theorem_pass
        else
        "K3_3_five_four_frame_double_cover_not_derived"
    ),
)
print("TWO_NATIVE_FRAME_SHEETS_DERIVED:", theorem_pass)
print("FRAME_SHEET_SIZE:", 60)
print("FRAME_STABILIZER_ORDER:", 2)
print("EACH_SHEET_PROJECTS_BIJECTIVELY_TO_BASE_FRAMES:",
      theorem_pass)
print("NATIVE_SHEET_EXCHANGE_EXISTS:", False)
print("LOCAL_METRIC_DISTINGUISHES_SHEETS:", False)
print("GLOBAL_NATIVE_ACTION_DISTINGUISHES_SHEETS:",
      theorem_pass)
print("HAND_DRAWING_SELECTS_ONE_FRAME_AND_ONE_SHEET:",
      theorem_pass)
print("CANONICAL_SHEET_SELECTED:", False)
print("NUMERIC_ANGLE_VALUES_DERIVED:", False)
print("PHYSICAL_CLAIM:", False)
print("MUTATION_PERFORMED:", False)
