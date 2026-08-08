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

def permutation_order(permutation):
    identity = tuple(range(len(permutation)))
    current = identity

    for order in range(1, 1000):
        current = tuple(
            permutation[current[index]]
            for index in range(len(permutation))
        )

        if current == identity:
            return order

    return None

def transported_permutation(permutation, mapping):
    transported = [None] * len(permutation)

    for source, target in mapping.items():
        transported[target] = mapping[permutation[source]]

    return tuple(transported)

def preserves_graph(permutation, graph):
    original = {
        tuple(sorted(edge))
        for edge in graph.edges()
    }
    image = {
        tuple(sorted((
            permutation[left],
            permutation[right],
        )))
        for left, right in graph.edges()
    }
    return image == original

h60 = json.loads(h60_path.read_text(encoding="utf-8"))
duad = json.loads(duad_path.read_text(encoding="utf-8"))

old_v4_indices = duad[
    "kernel_action"
]["native_v4_indices_derived_as_duad_kernel"]

old_v4 = {
    tuple(h60["elements"][index])
    for index in old_v4_indices
}

old_identity = tuple(range(60))

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
sheet_involutions = [
    tuple(permutation)
    for permutation in namespace["sheet_involutions"]
]

alignment_rows = []

for color, candidate_graph in enumerate(candidate_graphs):
    matcher = nx.algorithms.isomorphism.GraphMatcher(
        candidate_graph,
        native_graph,
    )

    isomorphism_count = 0
    exact_v4_match_count = 0
    first_matching_mapping = None
    transported_intersection_profile = Counter()

    for mapping in matcher.isomorphisms_iter():
        isomorphism_count += 1

        transported_v4 = {
            transported_permutation(permutation, mapping)
            for permutation in new_v4
        }

        intersection_size = len(
            transported_v4.intersection(old_v4)
        )
        transported_intersection_profile[intersection_size] += 1

        if transported_v4 == old_v4:
            exact_v4_match_count += 1

            if first_matching_mapping is None:
                first_matching_mapping = [
                    mapping[index]
                    for index in range(60)
                ]

    alignment_rows.append({
        "presentation": color,
        "isomorphism_count": isomorphism_count,
        "exact_v4_match_count": exact_v4_match_count,
        "intersection_profile":
            dict(sorted(transported_intersection_profile.items())),
        "first_matching_mapping":
            first_matching_mapping,
    })

old_v4_order_profile = Counter(
    permutation_order(permutation)
    for permutation in old_v4
)

new_v4_order_profile = Counter(
    permutation_order(permutation)
    for permutation in new_v4
)

new_v4_presentation_preservation = [
    all(
        preserves_graph(permutation, graph)
        for permutation in new_v4
    )
    for graph in candidate_graphs
]

sheet_involution_fixed_point_counts = [
    sum(
        source == target
        for source, target in enumerate(permutation)
    )
    for permutation in sheet_involutions
]

checks = {
    "old_v4_has_order_4":
        len(old_v4) == 4,
    "old_v4_contains_identity":
        old_identity in old_v4,
    "new_v4_has_order_4":
        len(new_v4) == 4,
    "new_v4_contains_identity":
        old_identity in new_v4,
    "new_v4_preserves_all_three_presentations":
        all(new_v4_presentation_preservation),
    "every_presentation_has_480_native_isomorphisms":
        all(
            row["isomorphism_count"] == 480
            for row in alignment_rows
        ),
    "every_presentation_admits_exact_native_v4_alignment":
        all(
            row["exact_v4_match_count"] > 0
            for row in alignment_rows
        ),
}

failed = [
    name
    for name, passed in checks.items()
    if not passed
]

print("== G900 TRICYCLE V4 ALIGNMENT AUDIT 004 ==")
print(
    "DERIVATION_OUTPUT_LINE_COUNT:",
    len(derivation_output.splitlines()),
)
print(
    "DERIVATION_CERTIFICATE_PASS_PRESENT:",
    "CERTIFICATE_PASS: True" in derivation_output,
)
print("OLD_V4_INDICES:", old_v4_indices)
print(
    "OLD_V4_ORDER_PROFILE:",
    dict(sorted(old_v4_order_profile.items())),
)
print(
    "NEW_V4_ORDER_PROFILE:",
    dict(sorted(new_v4_order_profile.items())),
)
print(
    "SHEET_INVOLUTION_FIXED_POINT_COUNTS:",
    sheet_involution_fixed_point_counts,
)
print(
    "NEW_V4_PRESENTATION_PRESERVATION:",
    new_v4_presentation_preservation,
)

for row in alignment_rows:
    print(
        "PRESENTATION",
        row["presentation"],
        "ISOMORPHISM_COUNT",
        row["isomorphism_count"],
        "EXACT_V4_MATCH_COUNT",
        row["exact_v4_match_count"],
        "INTERSECTION_PROFILE",
        row["intersection_profile"],
    )

    if row["first_matching_mapping"] is not None:
        print(
            "PRESENTATION",
            row["presentation"],
            "FIRST_MATCHING_MAPPING_FIRST_TWENTY",
            row["first_matching_mapping"][:20],
        )

print("CHECKS:", checks)
print("FAILED_CHECK_COUNT:", len(failed))
print("FAILED_CHECKS:", failed)
print("V4_ALIGNMENT_PROVED:", not failed)
print(
    "CLASSIFICATION:",
    (
        "tricycle_sheet_V4_is_native_V4_under_each_"
        "spherical_to_native_G60_identification"
        if not failed
        else
        "tricycle_and_native_V4_alignment_not_yet_proved"
    ),
)
print("G900_GLOBAL_LIFT_TESTED: false")
print("PHYSICAL_CLAIM: false")
print("PROJECT_MUTATION_PERFORMED: false")

if failed:
    raise SystemExit(1)
