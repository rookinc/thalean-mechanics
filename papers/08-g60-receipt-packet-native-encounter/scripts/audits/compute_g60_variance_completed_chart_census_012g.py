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
output_path = pathlib.Path(sys.argv[3]).resolve()

locked_head = "cd746bd Preregister G60 variance-completed chart test"

paths = {
    "prereg": project / "artifacts/json/g60_variance_completed_chart_preregistration_012f.v1.json",
    "012a": project / "artifacts/json/g60_gauge_covariant_update_census_012a.v1.json",
    "012c": project / "artifacts/json/g60_binary_torsor_action_character_probe_012c.v1.json",
    "012e": project / "artifacts/json/g60_local_D8_inversion_variance_census_012e.v1.json",
    "011w": project / "artifacts/json/g60_native_d8_chart_coherence_census_011w.v1.json",
    "011y": project / "artifacts/json/g60_native_d8_outer_c2_selector_census_011y.v1.json",
    "011o": project / "artifacts/json/g60_full_A_orientation_character_extension_census_011o.v1.json",
    "native": p42 / "artifacts/json/native_g60_fiber_product_isomorphism_044.json",
}

expected_hashes = {
    "prereg": "61af21d541a2f7e47ea152fdd71620ac79fb8d0bfd3576b7629adf45b8eae5c8",
    "012a": "4e6936b9b48c6f033b826df7c3ad4ac70ec3480129c5c73ec6a24630077096d2",
    "012c": "b08d3012ed20301897baa771ed99ecd6a859b8e7d1ef5b31c497652287962d76",
    "012e": "a42aed2a1b56144285fd0b2e575a7f932eb7de93b636e49b55cb9a7bd498328a",
    "011w": "e5630a02b4e4c28caac017906aebae10b00c5b1a8e1ccdf640a414c1174f6919",
    "011y": "d5a9036cf96aa97dd8848cd947bff4d07c711db0db2e3dca3ad13ec1c9cdfdab",
    "011o": "ad684db8bb65c5eb731c972d33e685ffc18a947f63c9ba4e9758f815821f0941",
    "native": "b37313b135495752b11e525bb61979163fdf54aec4be4f5d027dcee64c9efc21",
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

def compose_maps(left, right):
    return tuple(left[right[index]] for index in range(len(left)))

def pair_bit(mapping, pair):
    image = [int(mapping[pair[0]]), int(mapping[pair[1]])]
    if image == pair:
        return 0
    if image == [pair[1], pair[0]]:
        return 1
    raise AssertionError(("pair not preserved", pair, image))

head = git("show", "-s", "--format=%h %s", "HEAD")
if head != locked_head:
    raise SystemExit("locked HEAD mismatch: " + head)

expected_status = {
    "?? dist/a-blind-encounter-between-finite-receipt-algebra-and-the-native-g60-graph-overleaf.zip",
    "?? dist/a-blind-encounter-between-finite-receipt-algebra-and-the-native-g60-graph-overleaf.zip.sha256",
    "?? dist/g60-native-receipt-tower-overleaf.zip",
    "?? dist/g60-native-receipt-tower-overleaf.zip.sha256",
    "?? paper/",
    "?? scripts/zipit.sh",
}
status_before = set(
    line
    for line in git("status", "--short", "--", ".").splitlines()
    if line
)
if status_before != expected_status:
    raise SystemExit("unexpected scoped repository status")

authorities = {}
for name, path in paths.items():
    actual_hash = sha256_file(path)
    expected_hash = expected_hashes[name]
    if actual_hash != expected_hash:
        raise SystemExit("authority hash mismatch: " + str(path))
    authorities[str(path)] = {
        "role": name,
        "expected_sha256": expected_hash,
        "sha256": actual_hash,
        "hash_match": True,
    }

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
    product = compose_maps(
        native_permutations[left],
        native_permutations[right],
    )
    return native_lookup[product]

update_full = load_json(paths["012a"])
local_rows = update_full["local_reconstruction"]["presentation_rows"]
update_gauge_rows = update_full[
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

prereg = load_json(paths["prereg"])
predictions = prereg["predictions"]

presentation_results = []

for presentation_index in range(2):
    local_row = local_rows[presentation_index]
    table = [
        [int(value) for value in row]
        for row in local_row["multiplication_table"]
    ]
    automorphisms = [
        tuple(int(value) for value in row["mapping"])
        for row in local_row["automorphism_rows"]
    ]
    aut_lookup = {
        mapping: index
        for index, mapping in enumerate(automorphisms)
    }
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

    charts = [
        tuple(int(value) for value in row["images"])
        for row in sorted(
            chart_groups[presentation_index]["charts"],
            key=lambda row: int(row["chart_index"]),
        )
    ]
    ordinary_set = set(charts)
    opposite_charts = [
        tuple(chart[inverse[x]] for x in range(8))
        for chart in charts
    ]
    opposite_set = set(opposite_charts)

    ordinary_failures = []
    opposite_anti_failures = []
    opposite_ordinary_failures = []

    for chart_index, chart in enumerate(charts):
        opposite = opposite_charts[chart_index]
        ordinary_count = 0
        anti_count = 0
        wrong_side_count = 0

        for left in range(8):
            for right in range(8):
                product = table[left][right]

                if chart[product] != multiply_native(
                    chart[left], chart[right]
                ):
                    ordinary_count += 1

                if opposite[product] != multiply_native(
                    opposite[right], opposite[left]
                ):
                    anti_count += 1

                if opposite[product] != multiply_native(
                    opposite[left], opposite[right]
                ):
                    wrong_side_count += 1

        ordinary_failures.append(ordinary_count)
        opposite_anti_failures.append(anti_count)
        opposite_ordinary_failures.append(wrong_side_count)

    commute_failures = [
        aut_index
        for aut_index, automorphism in enumerate(automorphisms)
        if compose_maps(automorphism, inverse)
        != compose_maps(inverse, automorphism)
    ]

    extended_maps = {}
    for aut_index, automorphism in enumerate(automorphisms):
        for variance_bit in (0, 1):
            extended_maps[(aut_index, variance_bit)] = (
                automorphism
                if variance_bit == 0
                else compose_maps(automorphism, inverse)
            )

    direct_product_failures = []
    for left_aut in range(8):
        for left_variance in (0, 1):
            for right_aut in range(8):
                for right_variance in (0, 1):
                    aut_product = aut_lookup[
                        compose_maps(
                            automorphisms[left_aut],
                            automorphisms[right_aut],
                        )
                    ]
                    expected = extended_maps[
                        (
                            aut_product,
                            left_variance ^ right_variance,
                        )
                    ]
                    actual = compose_maps(
                        extended_maps[(left_aut, left_variance)],
                        extended_maps[(right_aut, right_variance)],
                    )
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
            mapping = extended_maps[(aut_index, variance_bit)]
            character_rows.append({
                "automorphism_index": aut_index,
                "variance_bit": variance_bit,
                "instruction_bit": pair_bit(mapping, pair),
                "chart_bit": chart_bits[aut_index],
            })

    instruction_character = [
        row["instruction_bit"] for row in character_rows
    ]
    chart_character = [
        row["chart_bit"] for row in character_rows
    ]
    variance_character = [
        row["variance_bit"] for row in character_rows
    ]

    if presentation_index == 0:
        runtime_rows = []

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

    character_vectors = {
        "instruction": instruction_character,
        "chart": chart_character,
        "variance": variance_character,
    }
    pairwise_rows = []
    character_names = ["instruction", "chart", "variance"]
    for left_index in range(3):
        for right_index in range(left_index + 1, 3):
            left_name = character_names[left_index]
            right_name = character_names[right_index]
            equal = (
                character_vectors[left_name]
                == character_vectors[right_name]
            )
            pairwise_rows.append({
                "left": left_name,
                "right": right_name,
                "characters_equal": equal,
                "equivariant_bijection_count": 2 if equal else 0,
            })

    instruction_formula_failures = [
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

    runtime_rows.append({
        "table": table,
        "inverse": inverse,
        "pair": pair,
        "automorphisms": automorphisms,
        "aut_lookup": aut_lookup,
        "chart_bits": chart_bits,
        "charts": charts,
        "opposite_charts": opposite_charts,
    })

    presentation_results.append({
        "presentation_index": presentation_index,
        "ordinary_chart_count": len(charts),
        "ordinary_chart_distinct_count": len(ordinary_set),
        "opposite_chart_count": len(opposite_charts),
        "opposite_chart_distinct_count": len(opposite_set),
        "variance_completed_chart_count": (
            len(ordinary_set | opposite_set)
        ),
        "ordinary_opposite_intersection_count": len(
            ordinary_set & opposite_set
        ),
        "ordinary_homomorphism_failure_profile": dict(
            sorted(Counter(ordinary_failures).items())
        ),
        "opposite_anti_homomorphism_failure_profile": dict(
            sorted(Counter(opposite_anti_failures).items())
        ),
        "opposite_ordinary_failure_profile": dict(
            sorted(Counter(opposite_ordinary_failures).items())
        ),
        "opposite_charts": [
            list(chart) for chart in opposite_charts
        ],
        "inversion_commutation_failure_indices": commute_failures,
        "extended_transformation_count": len(
            set(extended_maps.values())
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
        "pairwise_character_comparisons": pairwise_rows,
        "instruction_formula_failures":
            instruction_formula_failures,
    })

update_gauge_by_index = {
    int(row["gauge_index"]): row
    for row in update_gauge_rows
}
chart_gauge_by_index = {
    int(row["gauge_index"]): row
    for row in chart_gauge_rows
}
gauge_indices = sorted(
    set(update_gauge_by_index)
    & set(chart_gauge_by_index)
)

gauge_results = []

source_runtime = runtime_rows[0]
target_runtime = runtime_rows[1]
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

for gauge_index in gauge_indices:
    update_row = update_gauge_by_index[gauge_index]
    chart_row = chart_gauge_by_index[gauge_index]

    isomorphism = tuple(
        int(value)
        for value in update_row["local_isomorphism"]
    )
    inverse_isomorphism = [None] * 8
    for source, target in enumerate(isomorphism):
        inverse_isomorphism[target] = source
    inverse_isomorphism = tuple(inverse_isomorphism)

    inversion_commutation_failures = [
        source
        for source in range(8)
        if isomorphism[
            source_runtime["inverse"][source]
        ] != target_runtime["inverse"][
            isomorphism[source]
        ]
    ]

    ordinary_transport_failures = []
    ordinary_transport = []
    opposite_transport_failures = []
    opposite_transport = []

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
            ordinary_transport_failures.append(chart_index)

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
            opposite_transport_failures.append(chart_index)

    character_transport_failures = []
    conjugated_automorphism_indices = []

    for source_aut_index, source_aut in enumerate(
        source_runtime["automorphisms"]
    ):
        conjugated = compose_maps(
            isomorphism,
            compose_maps(source_aut, inverse_isomorphism),
        )
        target_aut_index = target_runtime[
            "aut_lookup"
        ].get(conjugated)
        conjugated_automorphism_indices.append(
            target_aut_index
        )

        if target_aut_index is None:
            character_transport_failures.append([
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
            character_transport_failures.append([
                source_aut_index,
                "instruction_character",
            ])
        if source_chart != target_chart:
            character_transport_failures.append([
                source_aut_index,
                "chart_character",
            ])

    gauge_results.append({
        "gauge_index": gauge_index,
        "function_bits": [
            int(value)
            for value in update_row["function_bits"]
        ],
        "local_isomorphism": list(isomorphism),
        "inversion_commutation_failure_count": len(
            inversion_commutation_failures
        ),
        "ordinary_chart_transport_failure_count": len(
            ordinary_transport_failures
        ),
        "opposite_chart_transport_failure_count": len(
            opposite_transport_failures
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
            conjugated_automorphism_indices,
        "character_transport_failure_count": len(
            character_transport_failures
        ),
        "chart_gauge_preserves_orbit_labels": (
            chart_row["preserves_orbit_labels"] is True
        ),
        "chart_gauge_conjugates_outer_flip": (
            chart_row[
                "conjugates_outer_flip_to_outer_flip"
            ] is True
        ),
    })

checks = []

def check(name, condition):
    checks.append((name, bool(condition)))

check("head", head == locked_head)
check("authority_count", len(authorities) == 8)
check(
    "authority_hashes",
    all(row["hash_match"] for row in authorities.values()),
)
check("presentation_count", len(presentation_results) == 2)

for row in presentation_results:
    prefix = "p" + str(row["presentation_index"]) + "_"
    check(prefix + "ordinary_80", row["ordinary_chart_count"] == 80)
    check(
        prefix + "ordinary_distinct_80",
        row["ordinary_chart_distinct_count"] == 80,
    )
    check(prefix + "opposite_80", row["opposite_chart_count"] == 80)
    check(
        prefix + "opposite_distinct_80",
        row["opposite_chart_distinct_count"] == 80,
    )
    check(
        prefix + "completed_160",
        row["variance_completed_chart_count"] == 160,
    )
    check(
        prefix + "sets_disjoint",
        row["ordinary_opposite_intersection_count"] == 0,
    )
    check(
        prefix + "ordinary_hom_zero",
        row["ordinary_homomorphism_failure_profile"]
        == {0: 80},
    )
    check(
        prefix + "opposite_anti_zero",
        row["opposite_anti_homomorphism_failure_profile"]
        == {0: 80},
    )
    check(
        prefix + "opposite_ordinary_24",
        row["opposite_ordinary_failure_profile"]
        == {24: 80},
    )
    check(
        prefix + "inversion_commutes",
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
        prefix + "four_chart_variance_classes",
        len(row["chart_variance_classes"]) == 4,
    )
    check(
        prefix + "chart_variance_image_C2xC2",
        row["chart_variance_character_image"]
        == [[0, 0], [0, 1], [1, 0], [1, 1]],
    )
    check(
        prefix + "joint_image_C2xC2xC2",
        row["three_character_joint_image"]
        == [
            [0, 0, 0],
            [0, 0, 1],
            [0, 1, 0],
            [0, 1, 1],
            [1, 0, 0],
            [1, 0, 1],
            [1, 1, 0],
            [1, 1, 1],
        ],
    )
    check(
        prefix + "joint_kernel_order_2",
        len(row["three_character_joint_kernel"]) == 2,
    )
    check(
        prefix + "characters_pairwise_distinct",
        all(
            comparison["characters_equal"] is False
            for comparison in row[
                "pairwise_character_comparisons"
            ]
        ),
    )
    check(
        prefix + "no_pairwise_equivariant_bijection",
        all(
            comparison["equivariant_bijection_count"] == 0
            for comparison in row[
                "pairwise_character_comparisons"
            ]
        ),
    )
    check(
        prefix + "instruction_formula",
        row["instruction_formula_failures"] == [],
    )

check("gauge_count_4", len(gauge_results) == 4)
check(
    "gauge_indices",
    [row["gauge_index"] for row in gauge_results]
    == [0, 1, 2, 3],
)
check(
    "gauge_inversion_commutes",
    all(
        row["inversion_commutation_failure_count"] == 0
        for row in gauge_results
    ),
)
check(
    "gauge_ordinary_transport",
    all(
        row["ordinary_chart_transport_failure_count"] == 0
        and row["ordinary_chart_transport_is_permutation"]
        for row in gauge_results
    ),
)
check(
    "gauge_opposite_transport",
    all(
        row["opposite_chart_transport_failure_count"] == 0
        and row["opposite_chart_transport_is_permutation"]
        for row in gauge_results
    ),
)
check(
    "gauge_character_decomposition",
    all(
        row["character_transport_failure_count"] == 0
        for row in gauge_results
    ),
)
check(
    "gauge_chart_labels",
    all(
        row["chart_gauge_preserves_orbit_labels"]
        and row["chart_gauge_conjugates_outer_flip"]
        for row in gauge_results
    ),
)
check(
    "orientation_locked_bridge_count",
    orientation_summary["bridge_count"] == 2,
)
check(
    "orientation_locked_reversal",
    orientation_summary["reversal_verified"] is True,
)
check(
    "orientation_targets",
    orientation_summary["sheet_reversal_targets"]
    == [[1], [0]]
    and orientation_summary["root_inversion_targets"]
    == [[1], [0]],
)

prediction_checks = {
    "presentation_count":
        predictions["presentation_count"] == 2,
    "ordinary_chart_count":
        predictions["ordinary_chart_count_each"] == 80,
    "opposite_chart_count":
        predictions["opposite_chart_count_each"] == 80,
    "completed_chart_count":
        predictions["variance_completed_chart_count_each"] == 160,
    "opposite_ordinary_failures":
        predictions[
            "opposite_chart_ordinary_failure_count_each_chart"
        ] == 24,
    "extended_group":
        predictions["extended_group_structure"]
        == "Aut(D8) x C2",
    "joint_image":
        predictions["three_character_joint_image"]
        == "C2xC2xC2",
    "joint_kernel":
        predictions["three_character_joint_kernel_order"] == 2,
    "pairwise_bijections":
        predictions["pairwise_equivariant_bijection_count"] == 0,
    "gauge_count":
        predictions["locked_presentation_gauge_map_count"] == 4,
    "orientation_unlinked":
        predictions[
            "orientation_to_variance_canonical_map_established"
        ] is False,
}
check(
    "preregistration_prediction_fields",
    all(prediction_checks.values()),
)

failed = [name for name, passed in checks if not passed]
prediction_matches = not failed

classification = (
    "variance_completed_local_chart_system_has_three_independent_"
    "binary_characters_without_canonical_torsor_collapse"
)

payload = {
    "packet": "g60_variance_completed_chart_census_012g",
    "mode": "temporary_read_only_complete_variance_completed_chart_census",
    "locked_head": locked_head,
    "authorities": authorities,
    "presentation_rows": presentation_results,
    "presentation_gauge_comparison": {
        "gauge_map_count": len(gauge_results),
        "gauge_rows": gauge_results,
        "all_gauge_maps_commute_with_inversion": all(
            row["inversion_commutation_failure_count"] == 0
            for row in gauge_results
        ),
        "all_gauge_maps_preserve_variance_sheet": all(
            row["opposite_chart_transport_failure_count"] == 0
            for row in gauge_results
        ),
        "all_gauge_maps_preserve_character_decomposition": all(
            row["character_transport_failure_count"] == 0
            for row in gauge_results
        ),
    },
    "orientation_comparison_boundary": {
        "locked_orientation_summary": orientation_summary,
        "orientation_bridge_common_action_established": False,
        "orientation_to_local_variance_canonical_map_established": False,
        "orientation_anchor_selects_instruction": False,
        "orientation_anchor_selects_chart_orbit": False,
    },
    "preregistration_comparison": {
        "prediction_checks": prediction_checks,
        "prediction_matches": prediction_matches,
    },
    "classification": classification,
    "audit_pass_candidate": not failed,
    "earned_statement_candidate": (
        "For each selected D8 presentation, the eighty ordinary charts "
        "extend canonically to eighty disjoint opposite-law charts. "
        "Local inversion commutes with all eight automorphisms, giving "
        "a sixteen-element Aut(D8) x C2 variance-completed action. "
        "The instruction, chart-orbit, and local variance characters "
        "are pairwise distinct and have joint image C2 x C2 x C2 with "
        "joint kernel of order two. All four locked presentation gauge "
        "maps preserve the opposite-law sheet and the character "
        "decomposition. The locked 011o orientation bridge remains an "
        "external comparison authority: no common action or canonical "
        "identification with local variance is established."
    ),
    "boundary": {
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
    },
    "repository_mutation_performed": False,
}

output_path.write_text(
    json.dumps(payload, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

status_after = set(
    line
    for line in git("status", "--short", "--", ".").splitlines()
    if line
)

print("== G60 VARIANCE-COMPLETED CHART CENSUS 012g ==")
print("PACKET:", payload["packet"])
print("MODE:", payload["mode"])
print("LOCKED_HEAD:", locked_head)
print("AUTHORITY_COUNT:", len(authorities))
for row in presentation_results:
    print(
        "PRESENTATION_ROW:",
        json.dumps({
            key: value
            for key, value in row.items()
            if key != "opposite_charts"
        }, sort_keys=True),
    )
print("GAUGE_ROW_COUNT:", len(gauge_results))
print("ORIENTATION_SUMMARY:",
      json.dumps(orientation_summary, sort_keys=True))
print("CHECK_COUNT:", len(checks))
print("FAILED_CHECK_COUNT:", len(failed))
print("PREDICTION_MATCHES:", str(prediction_matches).lower())
print("CLASSIFICATION:", classification)
print("FAILED_CHECKS:", failed)
print("EARNED_STATEMENT_CANDIDATE:",
      payload["earned_statement_candidate"])
print("ORIENTATION_TO_LOCAL_VARIANCE_IDENTIFIED: false")
print("INSTRUCTION_SELECTED: false")
print("CHART_ORBIT_SELECTED: false")
print("ORIENTATION_SELECTED: false")
print("MECHANICS_STATE_CELL_ESTABLISHED: false")
print("MANUSCRIPT_MUTATED: false")
print("PHYSICAL_CLAIM: false")
print("PROJECT_MUTATION_PERFORMED: false")
print(
    "SCOPED_STATUS_PRESERVED:",
    str(status_after == status_before).lower(),
)

if failed or status_after != status_before:
    raise SystemExit(1)
