#!/usr/bin/env python3

import hashlib
import json
import pathlib
import re
import sys


EXPECTED = (
    {
        "step": "075f",
        "filename":
            "g900_compact_frame_collision_anatomy_075f.txt",
        "packet":
            "g900_compact_frame_collision_anatomy_075f",
        "theorem_pass": "True",
        "failure_count": "0",
        "required": (
            "LOSSY_EXPORT_CONFIRMED: True",
            "NATIVE_QUOTIENT_DERIVED: False",
        ),
        "role":
            "lossy compact frame coordinate diagnosed",
    },
    {
        "step": "075g",
        "filename":
            "g900_restored_frame_root_action_075g.txt",
        "packet":
            "g900_restored_frame_root_action_075g",
        "theorem_pass": "True",
        "failure_count": "0",
        "required": (
            "RESTORED_FRAME_KEY_COUNT: 60",
            "BIJECTIVE_TRANSPORT_COUNT: 120",
            "HOMOMORPHISM_FAILURE_COUNT: 0",
            "FRAME_ROOT_ORBIT_COUNT: 2",
            "FRAME_ROOT_ORBIT_SIZE_PROFILE: {60: 2}",
            "NATIVE_EXCHANGES_INVERSE_ROOTS: False",
            "AFFINE_ORIENTATION_CLASS_SURVIVES: True",
        ),
        "role":
            "closure-duad coordinate restores native action",
    },
    {
        "step": "075h",
        "filename":
            "g900_affine_orientation_orbit_ledger_075h.txt",
        "packet":
            "g900_affine_orientation_orbit_ledger_075h",
        "theorem_pass": "True",
        "failure_count": "0",
        "required": (
            "FRAME_ROOT_STATE_COUNT: 120",
            "FRAME_ROOT_ORBIT_COUNT: 2",
            "FRAME_ROOT_ORBIT_SIZE_PROFILE: {60: 2}",
            "AFFINE_ORIENTATION_CLASS_SURVIVES: True",
        ),
        "role":
            "complete affine-orientation orbit ledger",
    },
    {
        "step": "075i",
        "filename":
            "g900_affine_orientation_corner_matching_075i.txt",
        "packet":
            "g900_affine_orientation_corner_matching_075i",
        "theorem_pass": "False",
        "failure_count": "1",
        "required": (
            "ORBIT_TO_CORNER_SETS: {0: (0, 1), 1: (0, 1)}",
            "CORNER_TO_ORBIT_SETS: {0: (0, 1), 1: (0, 1)}",
            "FAILED_CHECKS: ['corner_matching_selects_orbit']",
            "ABSOLUTE_ORIENTATION_SELECTED: False",
        ),
        "role":
            "expected local-corner selector falsifier",
    },
    {
        "step": "075j",
        "filename":
            "g900_affine_orientation_deck_involution_075j.txt",
        "packet":
            "g900_affine_orientation_deck_involution_075j",
        "theorem_pass": "True",
        "failure_count": "0",
        "required": (
            "DECK_IS_INVOLUTION: True",
            "DECK_FIXED_POINT_COUNT: 0",
            "DECK_COMMUTATION_FAILURE_COUNT: 0",
            "DECK_EXCHANGES_ORBITS: True",
            "EACH_ORBIT_PROJECTS_BIJECTIVELY: True",
        ),
        "role":
            "central root-inversion deck involution",
    },
    {
        "step": "075k",
        "filename":
            "g900_combined_sheet_root_deck_group_075k.txt",
        "packet":
            "g900_combined_sheet_root_deck_group_075k",
        "theorem_pass": "False",
        "failure_count": "3",
        "required": (
            "COMBINED_TRANSPORT_FAILURE_COUNT: 28128",
            "DECK_GROUP_IS_V4: True",
            "FAILED_CHECKS: ['combined_transport_failure_count_zero', 'all_native_combined_actions_bijective', 'four_native_orbits_of_size_60']",
        ),
        "role":
            "expected raw-action-index join falsifier",
    },
    {
        "step": "075l",
        "filename":
            "g900_sheet_root_action_order_bridge_075l.txt",
        "packet":
            "g900_sheet_root_action_order_bridge_075l",
        "theorem_pass": "True",
        "failure_count": "0",
        "required": (
            "RAW_INDEX_FRAME_ACTION_MATCH_COUNT: 2",
            "DIRECT_BRIDGE_COUNT: 120",
            "DIRECT_BRIDGE_COMPLETE: True",
            "SELECTED_BRIDGE_IS_BIJECTION: True",
            "COMBINED_COVER_TEST_PERFORMED: False",
        ),
        "role":
            "exact action-order bridge",
    },
    {
        "step": "075m",
        "filename":
            "g900_combined_sheet_root_bridged_cover_075m.txt",
        "packet":
            "g900_combined_sheet_root_bridged_cover_075m",
        "theorem_pass": "True",
        "failure_count": "0",
        "required": (
            "COMBINED_STATE_COUNT: 240",
            "DIRECT_BRIDGE_COUNT: 120",
            "BRIDGE_FAILURE_COUNT: 0",
            "ROOT_TRANSPORT_FAILURE_COUNT: 0",
            "COMBINED_TRANSPORT_FAILURE_COUNT: 0",
            "COMBINED_NATIVE_ACTION_BIJECTION_COUNT: 120",
            "COMBINED_NATIVE_ACTION_DISTINCT_COUNT: 120",
            "DECK_GROUP_ORDER: 4",
            "DECK_GROUP_IS_V4: True",
            "DECK_ACTION_REGULAR_ON_FRAME_FIBERS: True",
            "SHEET_DECK_COMMUTATION_FAILURE_COUNT: 0",
            "ROOT_DECK_COMMUTATION_FAILURE_COUNT: 0",
            "COMBINED_NATIVE_ORBIT_COUNT: 4",
            "COMBINED_NATIVE_ORBIT_SIZE_PROFILE: {60: 4}",
        ),
        "role":
            "corrected four-sheet native cover theorem",
    },
)


def extract_last(text, name):
    matches = re.findall(
        rf"^{re.escape(name)}:\s*(.*?)\s*$",
        text,
        flags=re.MULTILINE,
    )

    return matches[-1] if matches else None


def sha256(path):
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def main():
    if len(sys.argv) != 3:
        raise SystemExit(
            "USAGE: audit_075n.py WORK CANDIDATE"
        )

    work = pathlib.Path(sys.argv[1]).resolve()
    candidate = pathlib.Path(sys.argv[2]).resolve()

    rows = []
    failures = []

    for expected in EXPECTED:
        path = work / expected["filename"]
        exists = path.is_file()

        if exists:
            text = path.read_text(
                encoding="utf-8",
                errors="replace",
            )
            packet = extract_last(text, "PACKET")
            theorem_pass = extract_last(
                text,
                "THEOREM_PASS",
            )
            failure_count = extract_last(
                text,
                "FAILED_CHECK_COUNT",
            )
            missing_markers = [
                marker
                for marker in expected["required"]
                if marker not in text
            ]
            digest = sha256(path)
            size_bytes = path.stat().st_size
        else:
            packet = None
            theorem_pass = None
            failure_count = None
            missing_markers = list(expected["required"])
            digest = None
            size_bytes = None

        row_checks = {
            "exists": exists,
            "packet_matches":
                packet == expected["packet"],
            "theorem_status_matches":
                theorem_pass
                == expected["theorem_pass"],
            "failure_count_matches":
                failure_count
                == expected["failure_count"],
            "required_markers_present":
                not missing_markers,
        }

        row_pass = all(row_checks.values())

        if not row_pass:
            failures.append(expected["step"])

        row = {
            "step": expected["step"],
            "role": expected["role"],
            "path": str(path),
            "packet": packet,
            "expected_packet": expected["packet"],
            "theorem_pass": theorem_pass,
            "expected_theorem_pass":
                expected["theorem_pass"],
            "failed_check_count": failure_count,
            "expected_failed_check_count":
                expected["failure_count"],
            "missing_markers": missing_markers,
            "sha256": digest,
            "size_bytes": size_bytes,
            "checks": row_checks,
            "row_pass": row_pass,
        }

        rows.append(row)

        print(
            "SCOUT:",
            expected["step"],
            "EXISTS=" + str(exists),
            "PACKET=" + str(packet),
            "PASS=" + str(theorem_pass),
            "FAILURES=" + str(failure_count),
            "ROW_PASS=" + str(row_pass),
        )

    checks = {
        "receipt_count_8": len(rows) == 8,
        "all_receipts_exist":
            all(row["checks"]["exists"] for row in rows),
        "all_packet_names_match":
            all(
                row["checks"]["packet_matches"]
                for row in rows
            ),
        "all_expected_theorem_statuses_match":
            all(
                row["checks"][
                    "theorem_status_matches"
                ]
                for row in rows
            ),
        "all_expected_failure_counts_match":
            all(
                row["checks"]["failure_count_matches"]
                for row in rows
            ),
        "all_required_markers_present":
            all(
                row["checks"][
                    "required_markers_present"
                ]
                for row in rows
            ),
        "corner_selector_075i_falsified_exactly":
            rows[3]["row_pass"],
        "raw_index_join_075k_falsified_exactly":
            rows[5]["row_pass"],
        "action_bridge_075l_passed":
            rows[6]["row_pass"],
        "four_sheet_cover_075m_passed":
            rows[7]["row_pass"],
    }

    failed_checks = [
        name
        for name, passed in checks.items()
        if not passed
    ]

    audit_pass = not failed_checks

    payload = {
        "schema":
            "g900_four_sheet_native_cover_capstone_075n.v1",
        "packet":
            "g900_four_sheet_native_cover_capstone_075n",
        "mode":
            "post-scout four-sheet native-cover capstone",
        "audit_pass": audit_pass,
        "checks": checks,
        "failed_check_count": len(failed_checks),
        "failed_checks": failed_checks,
        "receipt_rows": rows,
        "classification": (
            "the_sixty_intrinsic_frames_support_a_"
            "four_sheeted_native_cover_with_independent_"
            "synthematic_completion_and_affine_"
            "orientation_coordinates_and_central_"
            "Klein_four_deck_group"
            if audit_pass
            else
            "four_sheet_native_cover_capstone_failed"
        ),
        "boundaries": {
            "canonical_completion_sheet_selected": False,
            "canonical_affine_orientation_selected": False,
            "local_root_slot_names_orientation": False,
            "local_corner_matching_names_orientation": False,
            "numeric_angle_values_derived": False,
            "physical_claim": False,
        },
        "repository_mutation": "none",
        "permanent_artifact_written": True,
        "staging_performed": False,
        "commit_performed": False,
        "push_performed": False,
    }

    candidate.write_text(
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
        ) + "\n",
        encoding="utf-8",
    )

    print(
        "PACKET:",
        "g900_four_sheet_native_cover_capstone_075n",
    )
    print(
        "MODE:",
        "post-scout four-sheet native-cover capstone",
    )
    print("CHECKS:", checks)
    print(
        "FAILED_CHECK_COUNT:",
        len(failed_checks),
    )
    print("FAILED_CHECKS:", failed_checks)
    print("AUDIT_PASS:", audit_pass)
    print(
        "CLASSIFICATION:",
        payload["classification"],
    )
    print("OUTPUT:", candidate)
    print("PERMANENT_ARTIFACT_WRITTEN:", True)
    print("STAGING_PERFORMED:", False)
    print("COMMIT_PERFORMED:", False)
    print("PUSH_PERFORMED:", False)


if __name__ == "__main__":
    main()
