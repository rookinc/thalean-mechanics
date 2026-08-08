#!/usr/bin/env python3

import contextlib
import io
import json
import os
import pathlib
import runpy
import sys
from collections import Counter

import networkx as nx

derive = pathlib.Path(sys.argv[1]).resolve()
h60_path = pathlib.Path(sys.argv[2]).resolve()
duad_path = pathlib.Path(sys.argv[3]).resolve()
p41 = pathlib.Path(sys.argv[4]).resolve()

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

def invert(permutation):
    result = [None] * len(permutation)

    for source, target in enumerate(permutation):
        result[target] = source

    return tuple(result)

def conjugate(conjugator, element):
    return compose(
        conjugator,
        compose(element, invert(conjugator)),
    )

def transported_permutation(permutation, mapping):
    transported = [None] * len(permutation)

    for source, target in mapping.items():
        transported[target] = mapping[permutation[source]]

    return tuple(transported)

def pullback_permutation(permutation, mapping):
    inverse_mapping = {
        target: source
        for source, target in mapping.items()
    }

    return tuple(
        inverse_mapping[
            permutation[mapping[source]]
        ]
        for source in range(len(permutation))
    )

h60 = json.loads(
    h60_path.read_text(encoding="utf-8")
)
duad = json.loads(
    duad_path.read_text(encoding="utf-8")
)

h60_elements = {
    tuple(row)
    for row in h60["elements"]
}

old_v4_indices = duad[
    "kernel_action"
]["native_v4_indices_derived_as_duad_kernel"]

old_v4 = {
    tuple(h60["elements"][index])
    for index in old_v4_indices
}

layer = load_native_source_layer(p41)
half_flip = tuple(layer.half_flip)

v4_prime = {
    conjugate(half_flip, element)
    for element in old_v4
}

previous_directory = pathlib.Path.cwd()
os.chdir(derive.parents[2])

captured = io.StringIO()

with contextlib.redirect_stdout(captured):
    namespace = runpy.run_path(str(derive))

os.chdir(previous_directory)

derivation_output = captured.getvalue()

candidate_graphs = namespace["candidate_graphs"]
native_graph = namespace["native_graph"]

new_v4 = {
    tuple(permutation)
    for permutation in namespace["sheet_v4"]
}

sheet_s4 = {
    tuple(permutation)
    for permutation in namespace["sheet_s4"]
}

full_extension = {
    tuple(permutation)
    for permutation in namespace["full_extension"]
}

presentation_rows = []

for color, candidate_graph in enumerate(candidate_graphs):
    matcher = nx.algorithms.isomorphism.GraphMatcher(
        candidate_graph,
        native_graph,
    )

    isomorphism_count = 0
    exact_v4_alignment_count = 0

    half_flip_full_extension_count = 0
    half_flip_sheet_s4_count = 0

    v4_prime_full_subset_count = 0
    v4_prime_sheet_s4_subset_count = 0

    full_intersection_profile = Counter()
    sheet_s4_intersection_profile = Counter()

    nonidentity_full_membership_profile = Counter()
    nonidentity_sheet_s4_membership_profile = Counter()

    for mapping in matcher.isomorphisms_iter():
        isomorphism_count += 1

        transported_v4 = {
            transported_permutation(
                permutation,
                mapping,
            )
            for permutation in new_v4
        }

        if transported_v4 == old_v4:
            exact_v4_alignment_count += 1

        pulled_half_flip = pullback_permutation(
            half_flip,
            mapping,
        )

        pulled_v4_prime = {
            pullback_permutation(
                permutation,
                mapping,
            )
            for permutation in v4_prime
        }

        if pulled_half_flip in full_extension:
            half_flip_full_extension_count += 1

        if pulled_half_flip in sheet_s4:
            half_flip_sheet_s4_count += 1

        full_intersection_size = len(
            pulled_v4_prime.intersection(
                full_extension
            )
        )
        sheet_s4_intersection_size = len(
            pulled_v4_prime.intersection(
                sheet_s4
            )
        )

        full_intersection_profile[
            full_intersection_size
        ] += 1

        sheet_s4_intersection_profile[
            sheet_s4_intersection_size
        ] += 1

        nonidentity_full_count = sum(
            permutation != identity
            and permutation in full_extension
            for permutation in pulled_v4_prime
        )

        nonidentity_sheet_s4_count = sum(
            permutation != identity
            and permutation in sheet_s4
            for permutation in pulled_v4_prime
        )

        nonidentity_full_membership_profile[
            nonidentity_full_count
        ] += 1

        nonidentity_sheet_s4_membership_profile[
            nonidentity_sheet_s4_count
        ] += 1

        if pulled_v4_prime <= full_extension:
            v4_prime_full_subset_count += 1

        if pulled_v4_prime <= sheet_s4:
            v4_prime_sheet_s4_subset_count += 1

    presentation_rows.append({
        "presentation": color,
        "isomorphism_count":
            isomorphism_count,
        "exact_v4_alignment_count":
            exact_v4_alignment_count,
        "half_flip_full_extension_count":
            half_flip_full_extension_count,
        "half_flip_sheet_s4_count":
            half_flip_sheet_s4_count,
        "v4_prime_full_subset_count":
            v4_prime_full_subset_count,
        "v4_prime_sheet_s4_subset_count":
            v4_prime_sheet_s4_subset_count,
        "full_intersection_profile":
            dict(sorted(
                full_intersection_profile.items()
            )),
        "sheet_s4_intersection_profile":
            dict(sorted(
                sheet_s4_intersection_profile.items()
            )),
        "nonidentity_full_membership_profile":
            dict(sorted(
                nonidentity_full_membership_profile.items()
            )),
        "nonidentity_sheet_s4_membership_profile":
            dict(sorted(
                nonidentity_sheet_s4_membership_profile.items()
            )),
    })

total_identifications = sum(
    row["isomorphism_count"]
    for row in presentation_rows
)

total_v4_prime_full_subset = sum(
    row["v4_prime_full_subset_count"]
    for row in presentation_rows
)

total_v4_prime_sheet_s4_subset = sum(
    row["v4_prime_sheet_s4_subset_count"]
    for row in presentation_rows
)

total_half_flip_full = sum(
    row["half_flip_full_extension_count"]
    for row in presentation_rows
)

total_half_flip_sheet_s4 = sum(
    row["half_flip_sheet_s4_count"]
    for row in presentation_rows
)

checks = {
    "derivation_certificate_pass":
        "CERTIFICATE_PASS: True"
        in derivation_output,
    "h60_order_480":
        len(h60_elements) == 480,
    "sheet_s4_order_24":
        len(sheet_s4) == 24,
    "full_extension_order_1440":
        len(full_extension) == 1440,
    "native_v4_order_4":
        len(old_v4) == 4,
    "transverse_v4_order_4":
        len(v4_prime) == 4,
    "v4_intersection_identity_only":
        old_v4.intersection(v4_prime)
        == {identity},
    "half_flip_outside_h60":
        half_flip not in h60_elements,
    "three_presentations":
        len(presentation_rows) == 3,
    "every_presentation_has_480_identifications":
        all(
            row["isomorphism_count"] == 480
            for row in presentation_rows
        ),
    "every_identification_aligns_native_v4":
        all(
            row["exact_v4_alignment_count"]
            == row["isomorphism_count"]
            for row in presentation_rows
        ),
}

failed = [
    name
    for name, passed in checks.items()
    if not passed
]

if total_v4_prime_full_subset == total_identifications:
    classification = (
        "transverse_V4_universally_contained_"
        "in_tricycle_full_extension"
    )
elif total_v4_prime_full_subset == 0:
    classification = (
        "transverse_V4_universally_excluded_"
        "from_tricycle_full_extension"
    )
else:
    classification = (
        "transverse_V4_membership_depends_"
        "on_spherical_to_native_identification"
    )

print(
    "== G900 TRICYCLE EXTENSION MEMBERSHIP AUDIT 008 =="
)
print(
    "DERIVATION_OUTPUT_LINE_COUNT:",
    len(derivation_output.splitlines()),
)
print(
    "DERIVATION_CERTIFICATE_PASS_PRESENT:",
    "CERTIFICATE_PASS: True"
    in derivation_output,
)
print("H60_ORDER:", len(h60_elements))
print("SHEET_S4_ORDER:", len(sheet_s4))
print(
    "FULL_EXTENSION_ORDER:",
    len(full_extension),
)
print("NATIVE_V4_ORDER:", len(old_v4))
print("TRANSVERSE_V4_ORDER:", len(v4_prime))
print(
    "NATIVE_TRANSVERSE_INTERSECTION_ORDER:",
    len(old_v4.intersection(v4_prime)),
)
print(
    "HALF_FLIP_IN_H60:",
    half_flip in h60_elements,
)
print(
    "TOTAL_IDENTIFICATION_COUNT:",
    total_identifications,
)

for row in presentation_rows:
    print(
        "PRESENTATION",
        row["presentation"],
        "ISOMORPHISM_COUNT",
        row["isomorphism_count"],
        "EXACT_V4_ALIGNMENT_COUNT",
        row["exact_v4_alignment_count"],
    )
    print(
        "PRESENTATION",
        row["presentation"],
        "HALF_FLIP_FULL_EXTENSION_COUNT",
        row["half_flip_full_extension_count"],
        "HALF_FLIP_SHEET_S4_COUNT",
        row["half_flip_sheet_s4_count"],
    )
    print(
        "PRESENTATION",
        row["presentation"],
        "V4_PRIME_FULL_SUBSET_COUNT",
        row["v4_prime_full_subset_count"],
        "V4_PRIME_SHEET_S4_SUBSET_COUNT",
        row["v4_prime_sheet_s4_subset_count"],
    )
    print(
        "PRESENTATION",
        row["presentation"],
        "FULL_INTERSECTION_PROFILE",
        row["full_intersection_profile"],
    )
    print(
        "PRESENTATION",
        row["presentation"],
        "SHEET_S4_INTERSECTION_PROFILE",
        row["sheet_s4_intersection_profile"],
    )
    print(
        "PRESENTATION",
        row["presentation"],
        "NONIDENTITY_FULL_MEMBERSHIP_PROFILE",
        row[
            "nonidentity_full_membership_profile"
        ],
    )
    print(
        "PRESENTATION",
        row["presentation"],
        "NONIDENTITY_SHEET_S4_MEMBERSHIP_PROFILE",
        row[
            "nonidentity_sheet_s4_membership_profile"
        ],
    )

print(
    "TOTAL_HALF_FLIP_FULL_EXTENSION_COUNT:",
    total_half_flip_full,
)
print(
    "TOTAL_HALF_FLIP_SHEET_S4_COUNT:",
    total_half_flip_sheet_s4,
)
print(
    "TOTAL_V4_PRIME_FULL_SUBSET_COUNT:",
    total_v4_prime_full_subset,
)
print(
    "TOTAL_V4_PRIME_SHEET_S4_SUBSET_COUNT:",
    total_v4_prime_sheet_s4_subset,
)
print("CHECKS:", checks)
print("FAILED_CHECK_COUNT:", len(failed))
print("FAILED_CHECKS:", failed)
print("AUDIT_PASS:", not failed)
print("CLASSIFICATION:", classification)
print("G900_GLOBAL_FIELD_SEARCHED: false")
print("PHYSICAL_CLAIM: false")
print("PROJECT_MUTATION_PERFORMED: false")

if failed:
    raise SystemExit(1)
