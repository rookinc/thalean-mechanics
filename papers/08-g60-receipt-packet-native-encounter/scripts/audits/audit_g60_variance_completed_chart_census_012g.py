#!/usr/bin/env python3

import gc
import hashlib
import json
import pathlib
import subprocess
import sys
from collections import Counter

project = pathlib.Path(sys.argv[1]).resolve()
p42 = pathlib.Path(sys.argv[2]).resolve()
compute_path = pathlib.Path(sys.argv[3]).resolve()
candidate_path = pathlib.Path(sys.argv[4]).resolve()
report_path = pathlib.Path(sys.argv[5]).resolve()

expected_head = "cd746bd Preregister G60 variance-completed chart test"
expected_compute_hash = (
    "40c7628428923e8b13555dd5cb3d49db3047f5e43b9651d9b99ac3f0d43bdb1f"
)
expected_candidate_hash = (
    "3782d825dc93b3caa7c207feb1ed9c5708e11ef773732ecf5e9e4f155a921111"
)
expected_report_hash = (
    "c95275d148989a8a790570a996aaa5d078750fd33cfaf5e446c5b17f9ee7a0b6"
)

expected_authority_hashes = {
    "prereg":
        "61af21d541a2f7e47ea152fdd71620ac79fb8d0bfd3576b7629adf45b8eae5c8",
    "012a":
        "4e6936b9b48c6f033b826df7c3ad4ac70ec3480129c5c73ec6a24630077096d2",
    "012c":
        "b08d3012ed20301897baa771ed99ecd6a859b8e7d1ef5b31c497652287962d76",
    "012e":
        "a42aed2a1b56144285fd0b2e575a7f932eb7de93b636e49b55cb9a7bd498328a",
    "011w":
        "e5630a02b4e4c28caac017906aebae10b00c5b1a8e1ccdf640a414c1174f6919",
    "011y":
        "d5a9036cf96aa97dd8848cd947bff4d07c711db0db2e3dca3ad13ec1c9cdfdab",
    "011o":
        "ad684db8bb65c5eb731c972d33e685ffc18a947f63c9ba4e9758f815821f0941",
    "native":
        "b37313b135495752b11e525bb61979163fdf54aec4be4f5d027dcee64c9efc21",
}

paths = {
    "012a": project / "artifacts/json/g60_gauge_covariant_update_census_012a.v1.json",
    "012e": project / "artifacts/json/g60_local_D8_inversion_variance_census_012e.v1.json",
    "011w": project / "artifacts/json/g60_native_d8_chart_coherence_census_011w.v1.json",
    "011y": project / "artifacts/json/g60_native_d8_outer_c2_selector_census_011y.v1.json",
    "011o": project / "artifacts/json/g60_full_A_orientation_character_extension_census_011o.v1.json",
    "native": p42 / "artifacts/json/native_g60_fiber_product_isomorphism_044.json",
}

def sha256_file(path):
    digest = hashlib.sha256()
    with pathlib.Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

def load_json(path):
    with pathlib.Path(path).open(encoding="utf-8") as handle:
        return json.load(handle)

def git(*args):
    return subprocess.check_output(
        ["git", "--no-pager", *args],
        cwd=project,
        text=True,
    ).strip()

def compose(left, right):
    return tuple(left[right[index]] for index in range(len(left)))

def pair_bit(mapping, pair):
    image = [int(mapping[pair[0]]), int(mapping[pair[1]])]
    if image == pair:
        return 0
    if image == [pair[1], pair[0]]:
        return 1
    raise AssertionError(("pair not preserved", pair, image))

checks = []

def check(name, condition):
    checks.append((name, bool(condition)))

check(
    "head",
    git("show", "-s", "--format=%h %s", "HEAD")
    == expected_head,
)
check(
    "compute_hash",
    sha256_file(compute_path) == expected_compute_hash,
)
check(
    "candidate_hash",
    sha256_file(candidate_path) == expected_candidate_hash,
)
check(
    "report_hash",
    sha256_file(report_path) == expected_report_hash,
)

with candidate_path.open(encoding="utf-8") as handle:
    candidate = json.load(handle)

check(
    "packet",
    candidate["packet"]
    == "g60_variance_completed_chart_census_012g",
)
check(
    "mode",
    candidate["mode"]
    == "frozen_complete_variance_completed_chart_census",
)
check("locked_head", candidate["locked_head"] == expected_head)
check("candidate_audit_pass", candidate["audit_pass_candidate"] is True)
check(
    "candidate_prediction_matches",
    candidate["preregistration_comparison"][
        "prediction_matches"
    ] is True,
)
check("candidate_authority_count", len(candidate["authorities"]) == 8)

authority_rows_ok = True
for path_string, row in candidate["authorities"].items():
    path = pathlib.Path(path_string)
    role = row["role"]
    expected_hash = expected_authority_hashes.get(role)
    if (
        expected_hash is None
        or not path.is_file()
        or sha256_file(path) != expected_hash
        or row["expected_sha256"] != expected_hash
        or row["sha256"] != expected_hash
        or row["hash_match"] is not True
    ):
        authority_rows_ok = False
check("candidate_authority_hashes", authority_rows_ok)

expected_status = {
    "?? artifacts/json/g60_variance_completed_chart_census_012g.v1.json",
    "?? artifacts/receipts/g60_variance_completed_chart_census_012g.txt",
    "?? artifacts/receipts/g60_variance_completed_chart_census_012g_raw_run.txt",
    "?? notes/g60_variance_completed_chart_census_012g.md",
    "?? scripts/audits/audit_g60_variance_completed_chart_census_012g.py",
    "?? scripts/audits/compute_g60_variance_completed_chart_census_012g.py",
    "?? dist/a-blind-encounter-between-finite-receipt-algebra-and-the-native-g60-graph-overleaf.zip",
    "?? dist/a-blind-encounter-between-finite-receipt-algebra-and-the-native-g60-graph-overleaf.zip.sha256",
    "?? dist/g60-native-receipt-tower-overleaf.zip",
    "?? dist/g60-native-receipt-tower-overleaf.zip.sha256",
    "?? paper/",
    "?? scripts/zipit.sh",
}
status = set(
    line
    for line in git("status", "--short", "--", ".").splitlines()
    if line
)
check("scoped_status", status == expected_status)

native_full = load_json(paths["native"])
mapping_rows = sorted(
    native_full["mapping_rows"],
    key=lambda row: int(row["actual_index"]),
)
native_permutations = [
    tuple(int(value) for value in row["actual_permutation"])
    for row in mapping_rows
]
native_lookup = {
    permutation: index
    for index, permutation in enumerate(native_permutations)
}
del native_full
del mapping_rows
gc.collect()

def multiply_native(left, right):
    return native_lookup[
        compose(
            native_permutations[left],
            native_permutations[right],
        )
    ]

update_full = load_json(paths["012a"])
local_rows = update_full["local_reconstruction"]["presentation_rows"]
gauge_rows = update_full[
    "presentation_gauge_comparison"
]["matched_gauge_rows"]
del update_full
gc.collect()

chart_full = load_json(paths["011w"])
chart_groups = chart_full["chart_reconstruction"]["chart_rows"]
del chart_full
gc.collect()

selector_full = load_json(paths["011y"])
chart_aut_rows = selector_full[
    "local_automorphism_census"
]["automorphism_rows_by_presentation"]
chart_gauge_rows = selector_full[
    "presentation_gauge_torsor_comparison"
]["gauge_rows"]
del selector_full
gc.collect()

variance_full = load_json(paths["012e"])
variance_rows = variance_full["presentation_rows"]
del variance_full
gc.collect()

reconstructed = []
runtime = []

for presentation_index in range(2):
    local_row = local_rows[presentation_index]
    table = [
        [int(value) for value in row]
        for row in local_row["multiplication_table"]
    ]
    inverse = tuple(
        int(value)
        for value in variance_rows[
            presentation_index
        ]["inverse_permutation"]
    )
    pair = [
        int(value)
        for value in local_row["order_four_elements"]
    ]
    automorphisms = [
        tuple(int(value) for value in row["mapping"])
        for row in local_row["automorphism_rows"]
    ]
    aut_lookup = {
        mapping: index
        for index, mapping in enumerate(automorphisms)
    }

    charts = [
        tuple(int(value) for value in row["images"])
        for row in sorted(
            chart_groups[presentation_index]["charts"],
            key=lambda row: int(row["chart_index"]),
        )
    ]
    ordinary_set = set(charts)
    opposite_charts = [
        tuple(chart[inverse[index]] for index in range(8))
        for chart in charts
    ]
    opposite_set = set(opposite_charts)

    ordinary_profile = Counter()
    opposite_anti_profile = Counter()
    opposite_ordinary_profile = Counter()

    for chart, opposite in zip(charts, opposite_charts):
        ordinary_failures = 0
        opposite_anti_failures = 0
        opposite_ordinary_failures = 0

        for left in range(8):
            for right in range(8):
                product = table[left][right]

                if chart[product] != multiply_native(
                    chart[left], chart[right]
                ):
                    ordinary_failures += 1

                if opposite[product] != multiply_native(
                    opposite[right], opposite[left]
                ):
                    opposite_anti_failures += 1

                if opposite[product] != multiply_native(
                    opposite[left], opposite[right]
                ):
                    opposite_ordinary_failures += 1

        ordinary_profile[ordinary_failures] += 1
        opposite_anti_profile[opposite_anti_failures] += 1
        opposite_ordinary_profile[opposite_ordinary_failures] += 1

    commute_failures = [
        aut_index
        for aut_index, automorphism in enumerate(automorphisms)
        if compose(automorphism, inverse)
        != compose(inverse, automorphism)
    ]

    extended = {}
    for aut_index, automorphism in enumerate(automorphisms):
        extended[(aut_index, 0)] = automorphism
        extended[(aut_index, 1)] = compose(
            automorphism, inverse
        )

    direct_product_failures = []
    for left_aut in range(8):
        for left_variance in (0, 1):
            for right_aut in range(8):
                for right_variance in (0, 1):
                    aut_product = aut_lookup[
                        compose(
                            automorphisms[left_aut],
                            automorphisms[right_aut],
                        )
                    ]
                    actual = compose(
                        extended[(left_aut, left_variance)],
                        extended[(right_aut, right_variance)],
                    )
                    expected = extended[
                        (
                            aut_product,
                            left_variance ^ right_variance,
                        )
                    ]
                    if actual != expected:
                        direct_product_failures.append([
                            left_aut,
                            left_variance,
                            right_aut,
                            right_variance,
                        ])

    chart_bits = {}
    for row in chart_aut_rows[presentation_index]:
        aut_index = int(row["automorphism_index"])
        permutation = [
            int(value)
            for value in row[
                "induced_global_orbit_permutation"
            ]
        ]
        if permutation == [0, 1]:
            chart_bits[aut_index] = 0
        elif permutation == [1, 0]:
            chart_bits[aut_index] = 1
        else:
            raise AssertionError(("bad chart permutation", permutation))

    character_rows = []
    for aut_index in range(8):
        for variance_bit in (0, 1):
            character_rows.append({
                "automorphism_index": aut_index,
                "variance_bit": variance_bit,
                "instruction_bit": pair_bit(
                    extended[(aut_index, variance_bit)],
                    pair,
                ),
                "chart_bit": chart_bits[aut_index],
            })

    triple_image = sorted({
        (
            row["instruction_bit"],
            row["chart_bit"],
            row["variance_bit"],
        )
        for row in character_rows
    })
    chart_variance_image = sorted({
        (row["chart_bit"], row["variance_bit"])
        for row in character_rows
    })
    joint_kernel = [
        [
            row["automorphism_index"],
            row["variance_bit"],
        ]
        for row in character_rows
        if (
            row["instruction_bit"] == 0
            and row["chart_bit"] == 0
            and row["variance_bit"] == 0
        )
    ]

    vectors = {
        "instruction": [
            row["instruction_bit"] for row in character_rows
        ],
        "chart": [
            row["chart_bit"] for row in character_rows
        ],
        "variance": [
            row["variance_bit"] for row in character_rows
        ],
    }
    pairwise = []
    names = ["instruction", "chart", "variance"]
    for left_index in range(3):
        for right_index in range(left_index + 1, 3):
            left_name = names[left_index]
            right_name = names[right_index]
            equal = vectors[left_name] == vectors[right_name]
            pairwise.append({
                "left": left_name,
                "right": right_name,
                "characters_equal": equal,
                "equivariant_bijection_count": (
                    2 if equal else 0
                ),
            })

    formula_failures = [
        [
            row["automorphism_index"],
            row["variance_bit"],
        ]
        for row in character_rows
        if row["instruction_bit"] != (
            pair_bit(
                automorphisms[row["automorphism_index"]],
                pair,
            )
            ^ row["variance_bit"]
        )
    ]

    result = {
        "presentation_index": presentation_index,
        "ordinary_chart_count": len(charts),
        "ordinary_chart_distinct_count": len(ordinary_set),
        "opposite_chart_count": len(opposite_charts),
        "opposite_chart_distinct_count": len(opposite_set),
        "variance_completed_chart_count": len(
            ordinary_set | opposite_set
        ),
        "ordinary_opposite_intersection_count": len(
            ordinary_set & opposite_set
        ),
        "ordinary_homomorphism_failure_profile": {
            str(key): value
            for key, value in sorted(ordinary_profile.items())
        },
        "opposite_anti_homomorphism_failure_profile": {
            str(key): value
            for key, value in sorted(
                opposite_anti_profile.items()
            )
        },
        "opposite_ordinary_failure_profile": {
            str(key): value
            for key, value in sorted(
                opposite_ordinary_profile.items()
            )
        },
        "opposite_charts": [
            list(chart) for chart in opposite_charts
        ],
        "inversion_commutation_failure_indices":
            commute_failures,
        "extended_transformation_count": len(
            set(extended.values())
        ),
        "direct_product_failure_count": len(
            direct_product_failures
        ),
        "direct_product_failures": direct_product_failures,
        "chart_variance_classes": [
            [chart_bit, variance_bit]
            for chart_bit in (0, 1)
            for variance_bit in (0, 1)
        ],
        "chart_variance_character_image": [
            list(value) for value in chart_variance_image
        ],
        "character_rows": character_rows,
        "three_character_joint_image": [
            list(value) for value in triple_image
        ],
        "three_character_joint_kernel": joint_kernel,
        "pairwise_character_comparisons": pairwise,
        "instruction_formula_failures": formula_failures,
    }
    reconstructed.append(result)

    runtime.append({
        "inverse": inverse,
        "pair": pair,
        "automorphisms": automorphisms,
        "aut_lookup": aut_lookup,
        "chart_bits": chart_bits,
        "charts": charts,
        "opposite_charts": opposite_charts,
    })

candidate_rows = sorted(
    candidate["presentation_rows"],
    key=lambda row: int(row["presentation_index"]),
)

check("presentation_count", len(candidate_rows) == 2)
check("reconstructed_count", len(reconstructed) == 2)

for presentation_index in range(2):
    check(
        "p" + str(presentation_index) + "_exact_reconstruction",
        reconstructed[presentation_index]
        == candidate_rows[presentation_index],
    )

    row = reconstructed[presentation_index]
    prefix = "p" + str(presentation_index) + "_"
    check(prefix + "ordinary_80", row["ordinary_chart_count"] == 80)
    check(prefix + "opposite_80", row["opposite_chart_count"] == 80)
    check(
        prefix + "completed_160",
        row["variance_completed_chart_count"] == 160,
    )
    check(
        prefix + "disjoint",
        row["ordinary_opposite_intersection_count"] == 0,
    )
    check(
        prefix + "ordinary_hom_zero",
        row["ordinary_homomorphism_failure_profile"]
        == {"0": 80},
    )
    check(
        prefix + "opposite_anti_zero",
        row["opposite_anti_homomorphism_failure_profile"]
        == {"0": 80},
    )
    check(
        prefix + "opposite_ordinary_24",
        row["opposite_ordinary_failure_profile"]
        == {"24": 80},
    )
    check(
        prefix + "commutation",
        row["inversion_commutation_failure_indices"] == [],
    )
    check(
        prefix + "extended_16",
        row["extended_transformation_count"] == 16,
    )
    check(
        prefix + "direct_product",
        row["direct_product_failure_count"] == 0,
    )
    check(
        prefix + "joint_image_8",
        len(row["three_character_joint_image"]) == 8,
    )
    check(
        prefix + "joint_kernel_2",
        len(row["three_character_joint_kernel"]) == 2,
    )
    check(
        prefix + "pairwise_distinct",
        all(
            comparison["characters_equal"] is False
            and comparison["equivariant_bijection_count"] == 0
            for comparison in row[
                "pairwise_character_comparisons"
            ]
        ),
    )
    check(
        prefix + "instruction_formula",
        row["instruction_formula_failures"] == [],
    )

gauge_by_index = {
    int(row["gauge_index"]): row
    for row in gauge_rows
}
chart_gauge_by_index = {
    int(row["gauge_index"]): row
    for row in chart_gauge_rows
}
gauge_indices = sorted(
    set(gauge_by_index) & set(chart_gauge_by_index)
)

source_runtime = runtime[0]
target_runtime = runtime[1]
target_chart_lookup = {
    chart: index
    for index, chart in enumerate(target_runtime["charts"])
}
target_opposite_lookup = {
    chart: index
    for index, chart in enumerate(
        target_runtime["opposite_charts"]
    )
}

reconstructed_gauge_rows = []

for gauge_index in gauge_indices:
    gauge_row = gauge_by_index[gauge_index]
    chart_gauge_row = chart_gauge_by_index[gauge_index]

    isomorphism = tuple(
        int(value)
        for value in gauge_row["local_isomorphism"]
    )
    inverse_isomorphism = [None] * 8
    for source, target in enumerate(isomorphism):
        inverse_isomorphism[target] = source
    inverse_isomorphism = tuple(inverse_isomorphism)

    inversion_failures = [
        source
        for source in range(8)
        if isomorphism[
            source_runtime["inverse"][source]
        ] != target_runtime["inverse"][
            isomorphism[source]
        ]
    ]

    ordinary_transport = []
    ordinary_failures = []
    for chart_index, chart in enumerate(
        source_runtime["charts"]
    ):
        transported = tuple(
            chart[inverse_isomorphism[target]]
            for target in range(8)
        )
        target_index = target_chart_lookup.get(transported)
        ordinary_transport.append(target_index)
        if target_index is None:
            ordinary_failures.append(chart_index)

    opposite_transport = []
    opposite_failures = []
    for chart_index, chart in enumerate(
        source_runtime["opposite_charts"]
    ):
        transported = tuple(
            chart[inverse_isomorphism[target]]
            for target in range(8)
        )
        target_index = target_opposite_lookup.get(transported)
        opposite_transport.append(target_index)
        if target_index is None:
            opposite_failures.append(chart_index)

    character_failures = []
    conjugated_indices = []

    for source_aut_index, source_aut in enumerate(
        source_runtime["automorphisms"]
    ):
        conjugated = compose(
            isomorphism,
            compose(source_aut, inverse_isomorphism),
        )
        target_aut_index = target_runtime[
            "aut_lookup"
        ].get(conjugated)
        conjugated_indices.append(target_aut_index)

        if target_aut_index is None:
            character_failures.append([
                source_aut_index,
                "missing_conjugated_automorphism",
            ])
            continue

        source_instruction = pair_bit(
            source_aut,
            source_runtime["pair"],
        )
        target_instruction = pair_bit(
            target_runtime["automorphisms"][
                target_aut_index
            ],
            target_runtime["pair"],
        )
        source_chart = source_runtime[
            "chart_bits"
        ][source_aut_index]
        target_chart = target_runtime[
            "chart_bits"
        ][target_aut_index]

        if source_instruction != target_instruction:
            character_failures.append([
                source_aut_index,
                "instruction_character",
            ])
        if source_chart != target_chart:
            character_failures.append([
                source_aut_index,
                "chart_character",
            ])

    reconstructed_gauge_rows.append({
        "gauge_index": gauge_index,
        "function_bits": [
            int(value)
            for value in gauge_row["function_bits"]
        ],
        "local_isomorphism": list(isomorphism),
        "inversion_commutation_failure_count": len(
            inversion_failures
        ),
        "ordinary_chart_transport_failure_count": len(
            ordinary_failures
        ),
        "opposite_chart_transport_failure_count": len(
            opposite_failures
        ),
        "ordinary_chart_transport_is_permutation": (
            None not in ordinary_transport
            and len(set(ordinary_transport)) == 80
        ),
        "opposite_chart_transport_is_permutation": (
            None not in opposite_transport
            and len(set(opposite_transport)) == 80
        ),
        "conjugated_automorphism_indices":
            conjugated_indices,
        "character_transport_failure_count": len(
            character_failures
        ),
        "chart_gauge_preserves_orbit_labels": (
            chart_gauge_row[
                "preserves_orbit_labels"
            ] is True
        ),
        "chart_gauge_conjugates_outer_flip": (
            chart_gauge_row[
                "conjugates_outer_flip_to_outer_flip"
            ] is True
        ),
    })

reconstructed_gauge = {
    "gauge_map_count": len(reconstructed_gauge_rows),
    "gauge_rows": reconstructed_gauge_rows,
    "all_gauge_maps_commute_with_inversion": all(
        row["inversion_commutation_failure_count"] == 0
        for row in reconstructed_gauge_rows
    ),
    "all_gauge_maps_preserve_variance_sheet": all(
        row["opposite_chart_transport_failure_count"] == 0
        for row in reconstructed_gauge_rows
    ),
    "all_gauge_maps_preserve_character_decomposition": all(
        row["character_transport_failure_count"] == 0
        for row in reconstructed_gauge_rows
    ),
}

check(
    "gauge_exact_reconstruction",
    reconstructed_gauge
    == candidate["presentation_gauge_comparison"],
)
check("gauge_count_4", reconstructed_gauge["gauge_map_count"] == 4)
check(
    "gauge_indices",
    [
        row["gauge_index"]
        for row in reconstructed_gauge_rows
    ] == [0, 1, 2, 3],
)
check(
    "gauge_inversion",
    reconstructed_gauge[
        "all_gauge_maps_commute_with_inversion"
    ] is True,
)
check(
    "gauge_variance_sheet",
    reconstructed_gauge[
        "all_gauge_maps_preserve_variance_sheet"
    ] is True,
)
check(
    "gauge_character_decomposition",
    reconstructed_gauge[
        "all_gauge_maps_preserve_character_decomposition"
    ] is True,
)
check(
    "gauge_ordinary_permutations",
    all(
        row["ordinary_chart_transport_is_permutation"]
        for row in reconstructed_gauge_rows
    ),
)
check(
    "gauge_opposite_permutations",
    all(
        row["opposite_chart_transport_is_permutation"]
        for row in reconstructed_gauge_rows
    ),
)

del runtime
del reconstructed
del local_rows
del chart_groups
del chart_aut_rows
gc.collect()

orientation_full = load_json(paths["011o"])
orientation_summary = {
    "bridge_count": orientation_full[
        "bridge_census"
    ]["alpha_1_bridge_count"],
    "reversal_verified": orientation_full[
        "bridge_census"
    ]["reversal_verified"],
    "sheet_reversal_targets": [
        row["sheet_reversal_map_indices"]
        for row in orientation_full[
            "bridge_census"
        ]["reversal_rows"]
    ],
    "root_inversion_targets": [
        row["root_inversion_map_indices"]
        for row in orientation_full[
            "bridge_census"
        ]["reversal_rows"]
    ],
}
del orientation_full
gc.collect()

orientation_boundary = candidate[
    "orientation_comparison_boundary"
]
check(
    "orientation_summary_exact",
    orientation_boundary["locked_orientation_summary"]
    == orientation_summary,
)
check("orientation_bridge_count", orientation_summary["bridge_count"] == 2)
check(
    "orientation_reversal",
    orientation_summary["reversal_verified"] is True,
)
check(
    "orientation_targets",
    orientation_summary["sheet_reversal_targets"]
    == [[1], [0]]
    and orientation_summary["root_inversion_targets"]
    == [[1], [0]],
)
check(
    "orientation_common_action_false",
    orientation_boundary[
        "orientation_bridge_common_action_established"
    ] is False,
)
check(
    "orientation_identification_false",
    orientation_boundary[
        "orientation_to_local_variance_canonical_map_established"
    ] is False,
)
check(
    "orientation_anchor_instruction_false",
    orientation_boundary[
        "orientation_anchor_selects_instruction"
    ] is False,
)
check(
    "orientation_anchor_chart_false",
    orientation_boundary[
        "orientation_anchor_selects_chart_orbit"
    ] is False,
)

expected_classification = (
    "variance_completed_local_chart_system_has_three_independent_"
    "binary_characters_without_canonical_torsor_collapse"
)
check(
    "classification",
    candidate["classification"] == expected_classification,
)
check(
    "earned_statement",
    bool(candidate["earned_statement"]),
)
check(
    "repository_no_mutation",
    candidate["repository_mutation_performed"] is False,
)

expected_boundary = {
    "variance_completed_census_performed": True,
    "opposite_chart_bundle_constructed": True,
    "orientation_to_local_variance_identified": False,
    "instruction_selected": False,
    "chart_orbit_selected": False,
    "orientation_selected": False,
    "autonomous_native_update_law_constructed": False,
    "mechanics_state_cell_established": False,
    "manuscript_mutated": False,
    "geometry_claim": False,
    "physical_claim": False,
}
check("boundary_exact", candidate["boundary"] == expected_boundary)

report_text = report_path.read_text(encoding="utf-8")
report_markers = [
    "CHECK_COUNT: 53",
    "FAILED_CHECK_COUNT: 0",
    "PREDICTION_MATCHES: true",
    "CLASSIFICATION: " + expected_classification,
    "ORIENTATION_TO_LOCAL_VARIANCE_IDENTIFIED: false",
    "INSTRUCTION_SELECTED: false",
    "CHART_ORBIT_SELECTED: false",
    "ORIENTATION_SELECTED: false",
    "MECHANICS_STATE_CELL_ESTABLISHED: false",
    "MANUSCRIPT_MUTATED: false",
    "PHYSICAL_CLAIM: false",
    "PROJECT_MUTATION_PERFORMED: false",
    "SCOPED_STATUS_PRESERVED: true",
]
for marker in report_markers:
    check(
        "report_" + marker.split(":", 1)[0],
        marker in report_text,
    )

failed = [name for name, passed in checks if not passed]

print("== G60 VARIANCE-COMPLETED CHART CENSUS GUARD 012g ==")
print("CHECK_COUNT:", len(checks))
print("FAILED_CHECK_COUNT:", len(failed))
for name, passed in checks:
    print("CHECK", name + ":", str(passed).lower())
print("GUARD_PASS:", str(not failed).lower())
print("FAILED_CHECKS:", failed)
print("CANDIDATE_PROMOTED: false")
print("PROJECT_MUTATION_PERFORMED: false")

if failed:
    raise SystemExit(1)
