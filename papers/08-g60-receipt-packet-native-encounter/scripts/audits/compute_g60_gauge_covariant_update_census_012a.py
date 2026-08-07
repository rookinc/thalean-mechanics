#!/usr/bin/env python3

import hashlib
import itertools
import json
import math
import pathlib
import subprocess
import sys
from collections import Counter

project = pathlib.Path(sys.argv[1]).resolve()
p42 = pathlib.Path(sys.argv[2]).resolve()
output_path = pathlib.Path(sys.argv[3]).resolve()

locked_head = "8fe832f Preregister G60 gauge-covariant update descent"

authority_paths = {
    "prereg": project / "artifacts/json/g60_gauge_covariant_update_preregistration_011z.v1.json",
    "011y": project / "artifacts/json/g60_native_d8_outer_c2_selector_census_011y.v1.json",
    "011w": project / "artifacts/json/g60_native_d8_chart_coherence_census_011w.v1.json",
    "native_action": p42 / "artifacts/json/native_g60_fiber_product_isomorphism_044.json",
}

expected_hashes = {
    "prereg": "63b669fcbd75d29bc6e81fa624e427da91d9eb9013d881e7e511889c648e17f4",
    "011y": "d5a9036cf96aa97dd8848cd947bff4d07c711db0db2e3dca3ad13ec1c9cdfdab",
    "011w": "e5630a02b4e4c28caac017906aebae10b00c5b1a8e1ccdf640a414c1174f6919",
    "native_action": "b37313b135495752b11e525bb61979163fdf54aec4be4f5d027dcee64c9efc21",
}

def sha256_file(path):
    h = hashlib.sha256()
    with pathlib.Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def sha256_json(value):
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    return hashlib.sha256(payload).hexdigest()

def git(*args):
    return subprocess.check_output(
        ["git", "--no-pager", *args],
        cwd=project,
        text=True,
    ).strip()

def compose(p, q):
    return tuple(p[q[i]] for i in range(len(p)))

def inverse_permutation(p):
    inverse = [None] * len(p)
    for index, image in enumerate(p):
        inverse[image] = index
    return tuple(inverse)

def permutation_order(p):
    seen = set()
    result = 1
    for start in range(len(p)):
        if start in seen:
            continue
        current = start
        length = 0
        while current not in seen:
            seen.add(current)
            current = p[current]
            length += 1
        if length:
            result = math.lcm(result, length)
    return result

def profile(values):
    return {
        str(key): count
        for key, count in sorted(Counter(values).items())
    }

def action_orbits(permutations, object_count):
    unseen = set(range(object_count))
    orbits = []
    while unseen:
        start = min(unseen)
        orbit = {permutation[start] for permutation in permutations}
        orbits.append(sorted(orbit))
        unseen -= orbit
    return sorted(orbits, key=lambda row: (len(row), row))

def walk(value, path="$"):
    yield path, value
    if isinstance(value, dict):
        for key in sorted(value):
            yield from walk(value[key], path + "." + str(key))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from walk(item, path + "[" + str(index) + "]")

def find_mapping_rows(data):
    candidates = []
    required = {
        "actual_index",
        "actual_permutation",
        "reference_element",
    }
    for path, value in walk(data):
        if (
            isinstance(value, list)
            and len(value) == 480
            and value
            and isinstance(value[0], dict)
            and required <= set(value[0])
        ):
            candidates.append((path, value))
    if len(candidates) != 1:
        raise RuntimeError(
            "expected one 480-row native mapping list, found "
            + str([path for path, _ in candidates])
        )
    return candidates[0]

def enumerate_automorphisms(table):
    automorphisms = []
    for tail in itertools.permutations(range(1, 8)):
        mapping = (0,) + tail
        if all(
            mapping[table[left][right]]
            == table[mapping[left]][mapping[right]]
            for left in range(8)
            for right in range(8)
        ):
            automorphisms.append(mapping)
    return sorted(automorphisms)

def enumerate_isomorphisms(source, target):
    rows = []
    for tail in itertools.permutations(range(1, 8)):
        mapping = (0,) + tail
        if all(
            mapping[source[left][right]]
            == target[mapping[left]][mapping[right]]
            for left in range(8)
            for right in range(8)
        ):
            rows.append(mapping)
    return sorted(rows)

def element_orders(table):
    orders = []
    for element in range(8):
        current = 0
        for order in range(1, 17):
            current = table[current][element]
            if current == 0:
                orders.append(order)
                break
        else:
            raise RuntimeError("element order not found")
    return orders

def element_orbits(automorphisms):
    unseen = set(range(8))
    orbits = []
    while unseen:
        start = min(unseen)
        orbit = {mapping[start] for mapping in automorphisms}
        orbits.append(sorted(orbit))
        unseen -= orbit
    return sorted(orbits, key=lambda row: (len(row), row))

head = git("show", "-s", "--format=%h %s", "HEAD")
if head != locked_head:
    raise SystemExit(
        "locked head mismatch: expected "
        + locked_head
        + " got "
        + head
    )

repository_status_before = git("status", "--short", "--", ".")

authorities = {}
loaded = {}
for name, path in authority_paths.items():
    actual = sha256_file(path)
    expected = expected_hashes[name]
    if actual != expected:
        raise SystemExit(
            name + " hash mismatch: expected "
            + expected + " got " + actual
        )
    authorities[str(path)] = {
        "expected_sha256": expected,
        "sha256": actual,
        "hash_match": True,
    }
    with path.open() as handle:
        loaded[name] = json.load(handle)

prereg = loaded["prereg"]
locked = loaded["011w"]
selector = loaded["011y"]
native = loaded["native_action"]

pred = prereg["predictions"]
chart_groups = locked["chart_reconstruction"]["chart_rows"]
presentation_rows = locked["chart_reconstruction"]["presentation_rows"]
locked_gauge_rows = locked["gauge_presentation_comparison"]["gauge_rows"]

mapping_path, mapping_rows = find_mapping_rows(native)
mapping_rows = sorted(
    mapping_rows,
    key=lambda row: int(row["actual_index"]),
)

if [int(row["actual_index"]) for row in mapping_rows] != list(range(480)):
    raise RuntimeError("native actual indices are not 0 through 479")

global_permutations = [
    tuple(int(x) for x in row["actual_permutation"])
    for row in mapping_rows
]
global_lookup = {
    permutation: index
    for index, permutation in enumerate(global_permutations)
}

identity_global = tuple(range(len(global_permutations[0])))
if global_lookup.get(identity_global) != 0:
    raise RuntimeError("native identity is not index 0")

def multiply_global(left, right):
    product = compose(
        global_permutations[left],
        global_permutations[right],
    )
    return global_lookup[product]

print("== G60 GAUGE-COVARIANT UPDATE CENSUS 012a ==")
print("MODE: temporary read-only complete update-descent census")
print("LOCKED_HEAD:", locked_head)
print("ALL_AUTHORITY_HASHES_MATCH: true")
print("NATIVE_MAPPING_PATH:", mapping_path)
print()

print("LOCAL_TABLE_AND_AUTOMORPHISM_RECONSTRUCTION_BEGIN")

tables = []
automorphisms_by_presentation = []
element_orders_by_presentation = []
element_orbits_by_presentation = []
chart_homomorphism_failures = []
chart_lookup_by_presentation = []
charts_by_presentation = []

for presentation_index, chart_group in enumerate(chart_groups):
    charts = sorted(
        chart_group["charts"],
        key=lambda row: int(row["chart_index"]),
    )
    if len(charts) != 80:
        raise RuntimeError("chart count is not 80")

    charts_by_presentation.append(charts)

    first_chart = tuple(int(x) for x in charts[0]["images"])
    inverse_first = {
        native_index: local_index
        for local_index, native_index in enumerate(first_chart)
    }

    table = []
    for left in range(8):
        row = []
        for right in range(8):
            native_product = multiply_global(
                first_chart[left],
                first_chart[right],
            )
            if native_product not in inverse_first:
                raise RuntimeError(
                    "first chart image is not closed"
                )
            row.append(inverse_first[native_product])
        table.append(tuple(row))
    table = tuple(table)
    tables.append(table)

    lookup = {}
    homomorphism_failures = 0
    for chart in charts:
        chart_index = int(chart["chart_index"])
        subgroup_index = int(chart["subgroup_index"])
        images = tuple(int(x) for x in chart["images"])
        lookup[(subgroup_index, images)] = chart_index

        for left in range(8):
            for right in range(8):
                if (
                    images[table[left][right]]
                    != multiply_global(images[left], images[right])
                ):
                    homomorphism_failures += 1

    chart_lookup_by_presentation.append(lookup)
    chart_homomorphism_failures.append(homomorphism_failures)

    automorphisms = enumerate_automorphisms(table)
    automorphisms_by_presentation.append(automorphisms)

    orders = element_orders(table)
    orbits = element_orbits(automorphisms)
    element_orders_by_presentation.append(orders)
    element_orbits_by_presentation.append(orbits)

    print(
        "PRESENTATION", presentation_index,
        "CHART_HOMOMORPHISM_FAILURES:",
        homomorphism_failures,
    )
    print(
        "PRESENTATION", presentation_index,
        "AUTOMORPHISM_COUNT:", len(automorphisms),
    )
    print(
        "PRESENTATION", presentation_index,
        "AUTOMORPHISM_ORDER_PROFILE:",
        profile(permutation_order(row) for row in automorphisms),
    )
    print(
        "PRESENTATION", presentation_index,
        "ELEMENT_ORDER_PROFILE:", profile(orders),
    )
    print(
        "PRESENTATION", presentation_index,
        "ELEMENT_ORBIT_SIZES:",
        sorted(len(row) for row in orbits),
    )
    print(
        "PRESENTATION", presentation_index,
        "ORDER4_ELEMENTS:",
        [index for index, order in enumerate(orders) if order == 4],
    )

print("LOCAL_TABLE_AND_AUTOMORPHISM_RECONSTRUCTION_END")
print()

print("CHART_DECORATED_UPDATE_DESCENT_BEGIN")

descent_rows_by_presentation = []
descent_summaries = []
native_relations = []

for presentation_index in range(2):
    table = tables[presentation_index]
    charts = charts_by_presentation[presentation_index]
    chart_lookup = chart_lookup_by_presentation[presentation_index]
    automorphisms = automorphisms_by_presentation[presentation_index]

    chart_by_index = {
        int(row["chart_index"]): row
        for row in charts
    }

    inverse_automorphisms = {
        mapping: inverse_permutation(mapping)
        for mapping in automorphisms
    }

    def act(mapping, decorated):
        chart_index, state, instruction = decorated
        chart = chart_by_index[chart_index]
        subgroup_index = int(chart["subgroup_index"])
        images = tuple(int(x) for x in chart["images"])
        inverse = inverse_automorphisms[mapping]
        target_images = tuple(
            images[inverse[local]]
            for local in range(8)
        )
        target_chart = chart_lookup[
            (subgroup_index, target_images)
        ]
        return (
            target_chart,
            mapping[state],
            mapping[instruction],
        )

    all_decorated = [
        (int(chart["chart_index"]), state, instruction)
        for chart in charts
        for state in range(8)
        for instruction in range(8)
    ]

    unseen = set(all_decorated)
    quotient_rows = []
    orbit_sizes = []
    evaluation_failure_count = 0
    covariance_failure_count = 0

    while unseen:
        representative = min(unseen)
        orbit = {
            act(mapping, representative)
            for mapping in automorphisms
        }
        unseen -= orbit
        orbit_sizes.append(len(orbit))

        evaluations = set()
        for chart_index, state, instruction in orbit:
            chart = chart_by_index[chart_index]
            images = tuple(int(x) for x in chart["images"])
            next_state = table[state][instruction]
            native_state = images[state]
            native_instruction = images[instruction]
            native_next = images[next_state]

            if (
                multiply_global(native_state, native_instruction)
                != native_next
            ):
                covariance_failure_count += 1

            evaluations.add((
                int(chart["subgroup_index"]),
                native_state,
                native_instruction,
                native_next,
            ))

        if len(evaluations) != 1:
            evaluation_failure_count += 1

        evaluation = min(evaluations)
        chart_index, state, instruction = representative
        quotient_rows.append({
            "subgroup_index": evaluation[0],
            "native_state_index": evaluation[1],
            "native_instruction_index": evaluation[2],
            "native_next_state_index": evaluation[3],
            "orbit_size": len(orbit),
            "representative": {
                "chart_index": chart_index,
                "local_state": state,
                "local_instruction": instruction,
                "local_next_state": table[state][instruction],
            },
        })

    quotient_rows = sorted(
        quotient_rows,
        key=lambda row: (
            row["subgroup_index"],
            row["native_state_index"],
            row["native_instruction_index"],
            row["native_next_state_index"],
        ),
    )

    expected_native_relation = set()
    for subgroup_index in range(10):
        fiber_charts = [
            row for row in charts
            if int(row["subgroup_index"]) == subgroup_index
        ]
        reference_images = tuple(
            int(x) for x in fiber_charts[0]["images"]
        )
        for state in reference_images:
            for instruction in reference_images:
                expected_native_relation.add((
                    subgroup_index,
                    state,
                    instruction,
                    multiply_global(state, instruction),
                ))

    quotient_relation = {
        (
            row["subgroup_index"],
            row["native_state_index"],
            row["native_instruction_index"],
            row["native_next_state_index"],
        )
        for row in quotient_rows
    }

    missing = sorted(expected_native_relation - quotient_relation)
    extra = sorted(quotient_relation - expected_native_relation)

    subgroup_counts = profile(
        row["subgroup_index"]
        for row in quotient_rows
    )

    summary = {
        "presentation_index": presentation_index,
        "chart_count": len(charts),
        "decorated_update_row_count": len(all_decorated),
        "gauge_orbit_count": len(quotient_rows),
        "gauge_orbit_size_profile": profile(orbit_sizes),
        "evaluation_failure_count": evaluation_failure_count,
        "native_multiplication_failure_count":
            covariance_failure_count,
        "native_relation_row_count": len(expected_native_relation),
        "quotient_relation_row_count": len(quotient_relation),
        "missing_native_relation_row_count": len(missing),
        "extra_native_relation_row_count": len(extra),
        "subgroup_quotient_row_count_profile":
            profile(subgroup_counts.values()),
        "quotient_evaluation_well_defined":
            evaluation_failure_count == 0,
        "quotient_evaluation_bijective":
            not missing and not extra,
        "quotient_relation_sha256":
            sha256_json(sorted(quotient_relation)),
    }

    descent_rows_by_presentation.append(quotient_rows)
    descent_summaries.append(summary)
    native_relations.append(quotient_relation)

    print(
        "PRESENTATION", presentation_index,
        "DECORATED_UPDATE_ROWS:", len(all_decorated),
    )
    print(
        "PRESENTATION", presentation_index,
        "GAUGE_ORBITS:", len(quotient_rows),
    )
    print(
        "PRESENTATION", presentation_index,
        "GAUGE_ORBIT_SIZE_PROFILE:",
        summary["gauge_orbit_size_profile"],
    )
    print(
        "PRESENTATION", presentation_index,
        "SUBGROUP_ROW_COUNT_PROFILE:",
        summary["subgroup_quotient_row_count_profile"],
    )
    print(
        "PRESENTATION", presentation_index,
        "EVALUATION_FAILURES:", evaluation_failure_count,
    )
    print(
        "PRESENTATION", presentation_index,
        "MISSING_NATIVE_ROWS:", len(missing),
        "EXTRA_NATIVE_ROWS:", len(extra),
    )

print("CHART_DECORATED_UPDATE_DESCENT_END")
print()

print("PRESENTATION_GAUGE_INTERTWINER_TEST_BEGIN")

presentation_isomorphisms = enumerate_isomorphisms(
    tables[0],
    tables[1],
)

locked_hash_rows = {
    row["induced_chart_bijection_sha256"]: row
    for row in locked_gauge_rows
}

matched_gauge_rows = []
unmatched_isomorphism_rows = []

charts0 = charts_by_presentation[0]
charts1 = charts_by_presentation[1]
lookup1 = chart_lookup_by_presentation[1]
chart1_by_index = {
    int(row["chart_index"]): row
    for row in charts1
}

for isomorphism in presentation_isomorphisms:
    inverse = inverse_permutation(isomorphism)
    induced = []

    for chart in charts0:
        subgroup_index = int(chart["subgroup_index"])
        images = tuple(int(x) for x in chart["images"])
        target_images = tuple(
            images[inverse[local]]
            for local in range(8)
        )
        induced.append(
            lookup1[(subgroup_index, target_images)]
        )

    induced_hash = sha256_json(induced)

    if induced_hash not in locked_hash_rows:
        unmatched_isomorphism_rows.append({
            "local_isomorphism": list(isomorphism),
            "induced_chart_bijection_sha256": induced_hash,
        })
        continue

    locked_row = locked_hash_rows[induced_hash]
    failure_count = 0

    for chart in charts0:
        source_chart_index = int(chart["chart_index"])
        target_chart_index = induced[source_chart_index]
        source_images = tuple(int(x) for x in chart["images"])
        target_images = tuple(
            int(x)
            for x in chart1_by_index[target_chart_index]["images"]
        )

        for state in range(8):
            for instruction in range(8):
                source_next = tables[0][state][instruction]
                target_state = isomorphism[state]
                target_instruction = isomorphism[instruction]
                target_next = tables[1][target_state][target_instruction]

                if target_next != isomorphism[source_next]:
                    failure_count += 1

                if (
                    source_images[state]
                    != target_images[target_state]
                    or source_images[instruction]
                    != target_images[target_instruction]
                    or source_images[source_next]
                    != target_images[target_next]
                ):
                    failure_count += 1

    matched_gauge_rows.append({
        "gauge_index": int(locked_row["gauge_index"]),
        "function_bits": locked_row["function_bits"],
        "local_isomorphism": list(isomorphism),
        "local_isomorphism_order":
            permutation_order(isomorphism),
        "induced_chart_bijection_sha256": induced_hash,
        "induced_chart_bijection_is_permutation":
            sorted(induced) == list(range(80)),
        "update_intertwining_failure_count": failure_count,
    })

matched_gauge_rows = sorted(
    matched_gauge_rows,
    key=lambda row: row["gauge_index"],
)

print("PRESENTATION_ISOMORPHISM_COUNT:",
      len(presentation_isomorphisms))
print("LOCKED_GAUGE_MAP_COUNT:", len(locked_gauge_rows))
print("MATCHED_GAUGE_INTERTWINER_COUNT:",
      len(matched_gauge_rows))
print("GAUGE_INTERTWINING_FAILURE_COUNTS:",
      [row["update_intertwining_failure_count"]
       for row in matched_gauge_rows])
print("PRESENTATION_GAUGE_INTERTWINER_TEST_END")
print()

element_orbit_profiles = [
    sorted(len(row) for row in rows)
    for rows in element_orbits_by_presentation
]

order4_elements = [
    [
        index
        for index, order in enumerate(orders)
        if order == 4
    ]
    for orders in element_orders_by_presentation
]

order4_invariant_singletons = []
for presentation_index in range(2):
    automorphisms = automorphisms_by_presentation[presentation_index]
    invariant = [
        element
        for element in order4_elements[presentation_index]
        if all(mapping[element] == element for mapping in automorphisms)
    ]
    order4_invariant_singletons.append(invariant)

presentation_relations_equal = (
    native_relations[0] == native_relations[1]
)

prediction_checks = {
    "presentation_count":
        len(charts_by_presentation) == pred["presentation_count"],
    "charts_80_each":
        all(len(rows) == 80 for rows in charts_by_presentation),
    "chart_homomorphisms":
        chart_homomorphism_failures == [0, 0],
    "automorphisms_8_each":
        all(len(rows) == 8 for rows in automorphisms_by_presentation),
    "element_orbits_1_1_2_4":
        element_orbit_profiles == [[1, 1, 2, 4], [1, 1, 2, 4]],
    "order4_candidates_2":
        [len(rows) for rows in order4_elements] == [2, 2],
    "order4_invariant_singletons_zero":
        order4_invariant_singletons == [[], []],
    "decorated_rows_5120_each":
        [
            row["decorated_update_row_count"]
            for row in descent_summaries
        ] == [5120, 5120],
    "gauge_orbits_640_each":
        [
            row["gauge_orbit_count"]
            for row in descent_summaries
        ] == [640, 640],
    "free_gauge_action":
        all(
            row["gauge_orbit_size_profile"] == {"8": 640}
            for row in descent_summaries
        ),
    "subgroup_rows_64":
        all(
            row["subgroup_quotient_row_count_profile"] == {"64": 10}
            for row in descent_summaries
        ),
    "well_defined":
        all(
            row["quotient_evaluation_well_defined"]
            for row in descent_summaries
        ),
    "bijective":
        all(
            row["quotient_evaluation_bijective"]
            for row in descent_summaries
        ),
    "presentations_equal": presentation_relations_equal,
    "presentation_isomorphisms_8":
        len(presentation_isomorphisms) == 8,
    "locked_gauge_maps_4":
        len(locked_gauge_rows) == 4,
    "matched_gauge_intertwiners_4":
        len(matched_gauge_rows) == 4,
    "all_gauge_maps_intertwine":
        all(
            row["update_intertwining_failure_count"] == 0
            and row["induced_chart_bijection_is_permutation"]
            for row in matched_gauge_rows
        ),
    "no_autonomous_noncentral_instruction":
        order4_invariant_singletons == [[], []],
}

prediction_matches = all(prediction_checks.values())

if not all(authority["hash_match"] for authority in authorities.values()):
    classification = "authority_failure"
elif chart_homomorphism_failures != [0, 0]:
    classification = "chart_reconstruction_or_isomorphism_failure"
elif element_orbit_profiles != [[1, 1, 2, 4], [1, 1, 2, 4]]:
    classification = "local_automorphism_orbit_profile_mismatch"
elif not all(
    row["quotient_evaluation_well_defined"]
    for row in descent_summaries
):
    classification = "chart_decorated_update_does_not_descend"
elif not all(
    row["quotient_evaluation_bijective"]
    for row in descent_summaries
):
    classification = "quotient_update_not_native_subgroup_multiplication"
elif not presentation_relations_equal:
    classification = "gauge_presentations_produce_inequivalent_update_relations"
elif len(matched_gauge_rows) != 4 or any(
    row["update_intertwining_failure_count"]
    for row in matched_gauge_rows
):
    classification = "presentation_gauge_update_intertwining_failure"
elif order4_invariant_singletons != [[], []]:
    classification = "autonomous_noncentral_instruction_selected"
elif prediction_matches:
    classification = (
        "gauge_covariant_instruction_parametrized_D8_update_"
        "descends_without_autonomous_instruction_selection"
    )
else:
    classification = "computation_failure"

earned_statement_candidate = (
    "For each of the two gauge-related selected D8 presentations, "
    "the eighty locked charts support 5,120 chart-decorated "
    "state-instruction update rows. The order-eight local automorphism "
    "group acts freely on these rows, producing 640 gauge orbits, "
    "exactly sixty-four over each of the ten native D8 subgroups. "
    "Every orbit has a single chart-independent native evaluation, "
    "and quotient evaluation is bijective onto the native subgroup "
    "multiplication graph. The two cocycle presentations yield the "
    "same native relation, and all four locked presentation gauge maps "
    "intertwine it. The local element orbit profile is 1,1,2,4; the "
    "q-axis contains two order-four instruction candidates and neither "
    "is fixed by the full chart gauge. Thus a gauge-covariant, "
    "instruction-parametrized local update operation exists, but no "
    "autonomous noncentral instruction or unary native evolution law "
    "is selected."
)

repository_status_after = git("status", "--short", "--", ".")
repository_status_preserved = (
    repository_status_after == repository_status_before
    and git("show", "-s", "--format=%h %s", "HEAD") == locked_head
)

candidate = {
    "packet": "g60_gauge_covariant_update_census_012a_candidate",
    "mode": "temporary_read_only_complete_update_descent_census",
    "locked_head": locked_head,
    "authorities": authorities,
    "preregistration_comparison": {
        "preregistered_packet": prereg["packet"],
        "predicted_classification":
            pred["predicted_classification"],
        "prediction_checks": prediction_checks,
        "prediction_matches": prediction_matches,
    },
    "native_group_reconstruction": {
        "mapping_row_path": mapping_path,
        "group_order": len(mapping_rows),
        "identity_index": 0,
        "permutation_degree": len(global_permutations[0]),
    },
    "local_reconstruction": {
        "presentation_count": 2,
        "presentation_rows": [
            {
                "presentation_index": index,
                "bits": presentation_rows[index]["bits"],
                "chart_count":
                    len(charts_by_presentation[index]),
                "chart_homomorphism_failure_count":
                    chart_homomorphism_failures[index],
                "multiplication_table": [
                    list(row) for row in tables[index]
                ],
                "multiplication_table_sha256":
                    sha256_json(tables[index]),
                "automorphism_count":
                    len(automorphisms_by_presentation[index]),
                "automorphism_rows": [
                    {
                        "automorphism_index": aut_index,
                        "mapping": list(mapping),
                        "order": permutation_order(mapping),
                    }
                    for aut_index, mapping in enumerate(
                        automorphisms_by_presentation[index]
                    )
                ],
                "automorphism_order_profile":
                    profile(
                        permutation_order(mapping)
                        for mapping in
                        automorphisms_by_presentation[index]
                    ),
                "element_orders":
                    element_orders_by_presentation[index],
                "element_order_profile":
                    profile(element_orders_by_presentation[index]),
                "element_orbits":
                    element_orbits_by_presentation[index],
                "element_orbit_size_profile":
                    element_orbit_profiles[index],
                "order_four_elements":
                    order4_elements[index],
                "Aut_D8_invariant_order_four_singletons":
                    order4_invariant_singletons[index],
            }
            for index in range(2)
        ],
    },
    "chart_decorated_update_descent": {
        "decorated_update_row_count_both_presentations":
            sum(
                row["decorated_update_row_count"]
                for row in descent_summaries
            ),
        "gauge_orbit_count_both_presentations":
            sum(
                row["gauge_orbit_count"]
                for row in descent_summaries
            ),
        "presentation_summaries": descent_summaries,
        "quotient_rows_by_presentation":
            descent_rows_by_presentation,
        "presentation_quotient_relations_equal":
            presentation_relations_equal,
    },
    "presentation_gauge_comparison": {
        "local_presentation_isomorphism_count":
            len(presentation_isomorphisms),
        "locked_gauge_map_count": len(locked_gauge_rows),
        "matched_gauge_intertwiner_count":
            len(matched_gauge_rows),
        "matched_gauge_rows": matched_gauge_rows,
        "unmatched_isomorphism_rows":
            unmatched_isomorphism_rows,
        "all_locked_gauge_maps_intertwine_update":
            len(matched_gauge_rows) == 4
            and all(
                row["update_intertwining_failure_count"] == 0
                for row in matched_gauge_rows
            ),
    },
    "selector_boundary": {
        "q_axis_order_four_instruction_candidate_counts":
            [len(rows) for rows in order4_elements],
        "Aut_D8_invariant_q_axis_order_four_singleton_counts":
            [len(rows) for rows in order4_invariant_singletons],
        "autonomous_noncentral_instruction_selected": False,
        "order_four_instruction_pair_identified_with_outer_C2_torsor":
            False,
    },
    "classification": classification,
    "earned_statement_candidate": earned_statement_candidate,
    "repository": {
        "status_before": repository_status_before.splitlines(),
        "status_after": repository_status_after.splitlines(),
        "status_preserved": repository_status_preserved,
        "head_preserved":
            git("show", "-s", "--format=%h %s", "HEAD")
            == locked_head,
    },
    "boundary": {
        "update_census_performed": True,
        "local_automorphism_action_recomputed": True,
        "chart_decorated_update_rows_enumerated": True,
        "gauge_quotient_computed": True,
        "gauge_covariant_instruction_parametrized_update_constructed":
            classification
            == (
                "gauge_covariant_instruction_parametrized_D8_update_"
                "descends_without_autonomous_instruction_selection"
            ),
        "autonomous_native_update_instruction_selected": False,
        "native_update_law_constructed": False,
        "absolute_chart_orbit_selected": False,
        "strict_equivariant_chart_selected": False,
        "mechanics_state_cell_established": False,
        "local_side_equals_011o_orientation_sheet": False,
        "orientation_selected": False,
        "global_minimality_claim": False,
        "manuscript_mutated": False,
        "geometry_claim": False,
        "physical_direction_claim": False,
        "physical_claim": False,
        "project_mutation_performed": False,
    },
}

output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(
    json.dumps(candidate, indent=2, sort_keys=True) + "\n"
)

print("== FINAL UPDATE-DESCENT REPORT ==")
print("ELEMENT_ORBIT_PROFILES:", element_orbit_profiles)
print("ORDER4_INSTRUCTION_CANDIDATE_COUNTS:",
      [len(rows) for rows in order4_elements])
print("ORDER4_INVARIANT_SINGLETON_COUNTS:",
      [len(rows) for rows in order4_invariant_singletons])
print("DECORATED_UPDATE_ROW_COUNTS:",
      [row["decorated_update_row_count"]
       for row in descent_summaries])
print("GAUGE_ORBIT_COUNTS:",
      [row["gauge_orbit_count"]
       for row in descent_summaries])
print("QUOTIENT_RELATIONS_EQUAL:",
      str(presentation_relations_equal).lower())
print("MATCHED_GAUGE_INTERTWINER_COUNT:",
      len(matched_gauge_rows))
print("PREDICTION_MATCHES:",
      str(prediction_matches).lower())
print("CLASSIFICATION:", classification)
print("REPOSITORY_STATUS_PRESERVED:",
      str(repository_status_preserved).lower())
print("PROJECT_MUTATION_PERFORMED: false")
print(
    "GAUGE_COVARIANT_INSTRUCTION_PARAMETRIZED_UPDATE_CONSTRUCTED:",
    str(candidate["boundary"][
        "gauge_covariant_instruction_parametrized_update_constructed"
    ]).lower(),
)
print("AUTONOMOUS_NATIVE_UPDATE_INSTRUCTION_SELECTED: false")
print("NATIVE_UPDATE_LAW_CONSTRUCTED: false")
print("MECHANICS_STATE_CELL_ESTABLISHED: false")
print("MANUSCRIPT_MUTATED: false")
print("PHYSICAL_CLAIM: false")
print("CANDIDATE_JSON:", output_path)
print("CANDIDATE_JSON_SHA256:", sha256_file(output_path))
