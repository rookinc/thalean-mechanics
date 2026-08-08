#!/usr/bin/env python3

import json
import pathlib
import sys
from collections import Counter

p41 = pathlib.Path(sys.argv[1]).resolve()
h60_path = pathlib.Path(sys.argv[2]).resolve()
surface_path = pathlib.Path(sys.argv[3]).resolve()
duad_path = pathlib.Path(sys.argv[4]).resolve()

sys.path.insert(0, str(p41))

from scripts.lib.project41_native import (
    IDENTITY60,
    load_native_source_layer,
)

identity = tuple(IDENTITY60)

def compose(left, right):
    return tuple(
        left[right[index]]
        for index in range(len(left))
    )

def parity_character(permutation):
    parity = 0

    for left in range(len(permutation)):
        for right in range(left + 1, len(permutation)):
            if permutation[left] > permutation[right]:
                parity ^= 1

    return 1 if parity == 0 else -1

h60_data = json.loads(
    h60_path.read_text(encoding="utf-8")
)
surface = json.loads(
    surface_path.read_text(encoding="utf-8")
)
duad = json.loads(
    duad_path.read_text(encoding="utf-8")
)
layer = load_native_source_layer(p41)

elements = [
    tuple(row)
    for row in h60_data["elements"]
]
element_index = {
    element: index
    for index, element in enumerate(elements)
}

preserving = set(
    surface["face_action"][
        "orientation_preserving_indices"
    ]
)
reversing = set(
    surface["face_action"][
        "orientation_reversing_indices"
    ]
)

surface_character = {
    index: 1 if index in preserving else -1
    for index in range(len(elements))
}

parity_values = {
    index: parity_character(element)
    for index, element in enumerate(elements)
}

identity_index = element_index.get(identity)
half_flip = tuple(layer.half_flip)
half_flip_parity = parity_character(half_flip)

v4_indices = duad[
    "kernel_action"
]["native_v4_indices_derived_as_duad_kernel"]

v4_rows = []

for index in v4_indices:
    element = elements[index]

    v4_rows.append({
        "index": index,
        "identity": element == identity,
        "surface_character":
            surface_character[index],
        "parity_character":
            parity_values[index],
    })

preserving_parity_profile = Counter(
    "even" if parity_values[index] == 1 else "odd"
    for index in preserving
)

reversing_parity_profile = Counter(
    "even" if parity_values[index] == 1 else "odd"
    for index in reversing
)

agreement_indices = [
    index
    for index in range(len(elements))
    if surface_character[index]
       == parity_values[index]
]

disagreement_indices = [
    index
    for index in range(len(elements))
    if surface_character[index]
       != parity_values[index]
]

homomorphism_failure_count = 0
first_homomorphism_failures = []

for left_index, left in enumerate(elements):
    for right_index, right in enumerate(elements):
        product = compose(left, right)
        product_index = element_index.get(product)

        if product_index is None:
            homomorphism_failure_count += 1

            if len(first_homomorphism_failures) < 10:
                first_homomorphism_failures.append({
                    "left": left_index,
                    "right": right_index,
                    "reason": "product_outside_h60",
                })
            continue

        expected = (
            surface_character[left_index]
            * surface_character[right_index]
        )
        actual = surface_character[product_index]

        if actual != expected:
            homomorphism_failure_count += 1

            if len(first_homomorphism_failures) < 10:
                first_homomorphism_failures.append({
                    "left": left_index,
                    "right": right_index,
                    "product": product_index,
                    "expected": expected,
                    "actual": actual,
                })

odd_h60_count = sum(
    value == -1
    for value in parity_values.values()
)

surface_character_is_parity = (
    len(agreement_indices) == len(elements)
)

if odd_h60_count > 0:
    generated_closure = "S60"
else:
    generated_closure = "A60"

if (
    generated_closure == "S60"
    and surface_character_is_parity
):
    extension_status = (
        "surface_orientation_character_extends_"
        "uniquely_as_S60_sign"
    )
    relative_orientation_character_extends = True
else:
    extension_status = (
        "surface_orientation_character_does_not_"
        "extend_through_carrier_closure"
    )
    relative_orientation_character_extends = False

checks = {
    "h60_order_480":
        len(elements) == 480,
    "identity_located":
        identity_index is not None,
    "preserving_count_240":
        len(preserving) == 240,
    "reversing_count_240":
        len(reversing) == 240,
    "orientation_partition_complete":
        preserving.isdisjoint(reversing)
        and preserving | reversing
            == set(range(480)),
    "surface_character_is_homomorphism":
        homomorphism_failure_count == 0,
    "native_v4_indices_present":
        len(v4_indices) == 4,
    "half_flip_even":
        half_flip_parity == 1,
}

failed = [
    name
    for name, passed in checks.items()
    if not passed
]

print(
    "== G900 ABSOLUTE ORIENTATION CHARACTER AUDIT 011 =="
)
print("H60_ORDER:", len(elements))
print("IDENTITY_INDEX:", identity_index)
print(
    "ORIENTATION_PRESERVING_COUNT:",
    len(preserving),
)
print(
    "ORIENTATION_REVERSING_COUNT:",
    len(reversing),
)
print(
    "PRESERVING_PARITY_PROFILE:",
    dict(sorted(preserving_parity_profile.items())),
)
print(
    "REVERSING_PARITY_PROFILE:",
    dict(sorted(reversing_parity_profile.items())),
)
print(
    "SURFACE_PARITY_AGREEMENT_COUNT:",
    len(agreement_indices),
)
print(
    "SURFACE_PARITY_DISAGREEMENT_COUNT:",
    len(disagreement_indices),
)
print(
    "FIRST_DISAGREEMENT_INDICES:",
    disagreement_indices[:20],
)
print(
    "SURFACE_CHARACTER_IS_PARITY:",
    surface_character_is_parity,
)
print(
    "SURFACE_CHARACTER_HOMOMORPHISM_FAILURE_COUNT:",
    homomorphism_failure_count,
)
print(
    "FIRST_HOMOMORPHISM_FAILURES:",
    first_homomorphism_failures,
)
print("H60_ODD_PERMUTATION_COUNT:", odd_h60_count)
print("HALF_FLIP_PARITY:", half_flip_parity)

for row in v4_rows:
    print(
        "V4_INDEX",
        row["index"],
        "IDENTITY",
        row["identity"],
        "SURFACE_CHARACTER",
        row["surface_character"],
        "PARITY_CHARACTER",
        row["parity_character"],
    )

print(
    "GENERATED_CLOSURE_FROM_A60_AND_H60:",
    generated_closure,
)
print(
    "RELATIVE_ORIENTATION_CHARACTER_EXTENDS:",
    relative_orientation_character_extends,
)
print("EXTENSION_STATUS:", extension_status)
print("ABSOLUTE_POSITIVE_SHEET_SELECTED: false")
print("EXTERNAL_ANCHOR_REQUIRED: true")
print("CHECKS:", checks)
print("FAILED_CHECK_COUNT:", len(failed))
print("FAILED_CHECKS:", failed)
print("AUDIT_PASS:", not failed)
print("PHYSICAL_CLAIM: false")
print("PROJECT_MUTATION_PERFORMED: false")

if failed:
    raise SystemExit(1)
