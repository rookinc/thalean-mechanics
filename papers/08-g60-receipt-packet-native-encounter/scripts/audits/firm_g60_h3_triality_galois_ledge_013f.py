#!/usr/bin/env python3

import hashlib
import json
import pathlib
import sys

source_path = pathlib.Path(sys.argv[1]).resolve()
raw_path = pathlib.Path(sys.argv[2]).resolve()
packet_path = pathlib.Path(sys.argv[3]).resolve()

def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1048576), b""):
            digest.update(block)
    return digest.hexdigest()

text = raw_path.read_text(encoding="utf-8")

section_requirements = {
    "== EXACT Q(SQRT5) CHARACTER-EXCHANGE CERTIFICATE ==": [
        "SOURCE_AUDIT_PASS: True",
        "B_GOLDEN_PROJECTOR_RANK: 3",
        "AB_GOLDEN_PROJECTOR_RANK: 3",
        "SINGULAR_VALUE_GAIN_RATIO: phi^2 = 3/2+1/2*sqrt5",
        "LONGITUDINAL_PROJECTOR_RANK: 1",
        "LONGITUDINAL_IS_EXACT_ROOT_PAIR_BISECTOR: True",
        "FAILED_CHECK_COUNT: 0",
        "CERTIFICATE_PASS: True",
    ],
    "== EXACT H3 BISECTOR-ORBIT G60 CERTIFICATE ==": [
        "H3_ROOT_COUNT: 30",
        "H3_REFLECTION_GROUP_ORDER: 120",
        "PROJECTIVE_BISECTOR_LINE_COUNT: 30",
        "ORIENTED_BISECTOR_POINT_COUNT: 60",
        "ANTIPODAL_CLOSURE: True",
        "SPHERICAL_PRESENTATION_COUNT",
        "FAILED_CHECK_COUNT: 0",
        "CERTIFICATE_PASS: True",
    ],
    "== G60 PRESENTATION TRIALITY TEST ==": [
        "CYCLE_COLOR_ACTION: [1, 2, 0]",
        "SWAP_COLOR_ACTION: [1, 0, 2]",
        "PRESENTATION_TRIALITY_PROVED: True",
        "PRESENTATION_S3_ACTION_PROVED: True",
    ],
    "== G60 TRIALITY DIRECTION AUDIT ==": [
        "CYCLE_COMMUTES_WITH_ANTIPODE: False",
        "REVERSER_COMMUTES_WITH_ANTIPODE: True",
        "REVERSER_REVERSES_CYCLE: True",
        "DIRECTION_AUDIT_PASS: False",
    ],
    "== TRIALITY ORIENTATION-SHEET CENSUS ==": [
        "ORDER_THREE_TRIALITY_COUNT: 84",
        "ORDER_THREE_COMMUTING_WITH_ANTIPODE_COUNT: 0",
        "ORDER_TWO_REVERSER_COUNT: 20",
        "ORDER_TWO_COMMUTING_WITH_ANTIPODE_COUNT: 20",
        "ORIENTATION_SHEET_CENSUS_PASS: True",
    ],
    "== ORIENTATION-SHEET V4 AND S4 TEST ==": [
        "SHEET_V4_ORDER: 4",
        "SHEET_EXTENSION_ORDER: 24",
        "SHEET_V4_NORMAL: True",
        "ORIENTATION_SHEET_V4_PROVED: True",
        "ORIENTATION_SHEET_S4_PROVED: True",
    ],
    "== A5 V4 KERNEL AND ORDER-1440 EXTENSION TEST ==": [
        "A5_PERMUTATION_ORDER: 60",
        "A5_V4_PRODUCT_ORDER: 240",
        "GENERATED_KERNEL_ORDER: 240",
        "FULL_EXTENSION_ORDER: 1440",
        "KERNEL_A5_TIMES_V4_PROVED: True",
        "FULL_ORDER_1440_EXTENSION_PROVED: True",
        "FULL_GROUP_STRUCTURE: A5_semidirect_S4",
    ],
    "== A5 OUTER AUTOMORPHISM AND GOLDEN GALOIS TEST ==": [
        "C_CLASS_ACTION: [0, 1, 2, 3, 4]",
        "R_CLASS_ACTION: [0, 1, 2, 4, 3]",
        "C_ACTION_IS_INNER: True",
        "R_ACTION_IS_OUTER: True",
        "R_SWAPS_ORDER_FIVE_CLASSES: True",
        "GOLDEN_GALOIS_PRESENTATION_ACTION: [1, 0, 2]",
        "GOLDEN_GALOIS_MATCHES_R_COLOR_ACTION: True",
        "A5_WITH_R_ORDER: 120",
        "A5_WITH_C_ORDER: 180",
        "GOLDEN_GALOIS_OUTER_AUTOMORPHISM_PROVED: True",
    ],
}

headers = list(section_requirements)
checks = []

def check(name, passed):
    checks.append((name, bool(passed)))

for header in headers:
    check(
        "section_once_" + header.strip("= ").lower().replace(" ", "_"),
        text.count(header) == 1,
    )

for index, header in enumerate(headers):
    start = text.find(header)
    if start < 0:
        section = ""
    else:
        later_starts = [
            text.find(other, start + len(header))
            for other in headers
            if text.find(other, start + len(header)) >= 0
        ]
        end = min(later_starts) if later_starts else len(text)
        section = text[start:end]

    for required in section_requirements[header]:
        if required == "SPHERICAL_PRESENTATION_COUNT":
            passed = section.count("NATIVE_ISOMORPHIC True") == 3
        else:
            passed = required in section

        check(
            header.strip("= ").lower().replace(" ", "_")
            + "__"
            + required.lower().replace(" ", "_"),
            passed,
        )

check(
    "physical_space_not_identified",
    "PHYSICAL_SPACE_IDENTIFIED: false" in text,
)
check(
    "g900_not_identified",
    "G900_IDENTIFIED: false" in text,
)
check(
    "project_not_mutated",
    "PROJECT_MUTATION_PERFORMED: false" in text,
)

failed = [
    name
    for name, passed in checks
    if not passed
]

packet = {
    "packet": "g60_h3_triality_galois_ledge",
    "version": 1,
    "mode": "temporary_consolidated_theorem_candidate",
    "authorities": {
        "exact_derivation_script": {
            "path": str(source_path),
            "sha256": sha256(source_path),
        },
        "raw_run_receipt": {
            "path": str(raw_path),
            "sha256": sha256(raw_path),
        },
    },
    "theorem": {
        "carrier": (
            "oriented_H3_adjacent_root_bisector_orbit"
        ),
        "carrier_size": 60,
        "projective_line_count": 30,
        "spherical_presentation_count": 3,
        "presentation_symmetry": "S3_triality",
        "orientation_sheet_kernel": "V4",
        "orientation_sheet_extension": "S4",
        "common_presentation_kernel": "A5_times_V4",
        "common_presentation_kernel_order": 240,
        "full_extension_order": 1440,
        "full_group_structure": "A5_semidirect_S4",
        "triality_cycler_action_on_A5": "inner",
        "triality_reverser_action_on_A5": "outer",
        "golden_galois_action": {
            "field_map": "sqrt5_maps_to_minus_sqrt5",
            "presentation_permutation": [1, 0, 2],
            "matches_triality_reverser": True,
        },
    },
    "refined_negative_result": {
        "early_direction_audit_passed": False,
        "reason": (
            "cyclic_triality_does_not_descend_through_"
            "the_antipodal_projective_quotient"
        ),
        "refinement": (
            "reversal_preserves_antipodal_pairing_while_"
            "cyclic_triality_intrinsically_mixes_orientation_sheets"
        ),
        "refinement_passed": True,
    },
    "boundary": {
        "absolute_axis_sign_selected": False,
        "literal_physical_motion_derived": False,
        "physical_space_identified": False,
        "g900_identified": False,
        "project_mutated": False,
    },
    "check_count": len(checks),
    "failed_check_count": len(failed),
    "failed_checks": failed,
    "candidate_pass": not failed,
    "candidate_frozen": False,
    "candidate_promoted": False,
}

packet_path.write_text(
    json.dumps(packet, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

print("== G60 H3 TRIALITY-GALOIS LEDGE CONSOLIDATION ==")
print("CHECK_COUNT:", len(checks))
print("FAILED_CHECK_COUNT:", len(failed))
print("FAILED_CHECKS:", failed)
print("CANDIDATE_PASS:", not failed)
print("SOURCE_SHA256:", sha256(source_path))
print("RAW_RECEIPT_SHA256:", sha256(raw_path))
print("PACKET_SHA256:", sha256(packet_path))
print("PACKET:", packet_path)
print("CANDIDATE_FROZEN: false")
print("CANDIDATE_PROMOTED: false")
print("PROJECT_MUTATION_PERFORMED: false")

if failed:
    raise SystemExit(1)
