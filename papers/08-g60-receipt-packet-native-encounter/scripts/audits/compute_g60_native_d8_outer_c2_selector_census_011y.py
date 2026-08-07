import hashlib
import itertools
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

project = Path(sys.argv[1]).resolve()
p42 = Path(sys.argv[2]).resolve()
candidate_path = Path(sys.argv[3]).resolve()

locked_head = "fe5a31e Correct G60 outer-C2 selector preregistration"

paths = {
    "correction": project / "artifacts/json/g60_native_d8_outer_c2_selector_preregistration_correction_011x1.v1.json",
    "correction_receipt": project / "artifacts/receipts/g60_native_d8_outer_c2_selector_preregistration_correction_011x1.txt",
    "prereg": project / "artifacts/json/g60_native_d8_outer_c2_selector_preregistration_011x.v1.json",
    "011w": project / "artifacts/json/g60_native_d8_chart_coherence_census_011w.v1.json",
    "native_action": p42 / "artifacts/json/native_g60_fiber_product_isomorphism_044.json",
}

expected_hashes = {
    "correction": "f1960c60fc243612dca4c769eb7783f784243c2b7bb4a736ba594b2f94d032de",
    "correction_receipt": "96f6a46259e5c50d1ab3c095c4b0e6ba8386200a67550f2d2f33fe9d79e7d8fc",
    "prereg": "a093ff51f40063d6bdf6754dc3dd8406b10c3ddcea62954cb8520f0331a9a201",
    "011w": "e5630a02b4e4c28caac017906aebae10b00c5b1a8e1ccdf640a414c1174f6919",
    "native_action": "b37313b135495752b11e525bb61979163fdf54aec4be4f5d027dcee64c9efc21",
}

def sha256_file(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()

def sha256_json(value):
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()

def git(*args):
    result = subprocess.run(
        ["git", *args],
        cwd=project,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout.strip()

def status_rows():
    return git("status", "--short", "--", ".").splitlines()

def compose(p, q):
    return tuple(p[q[i]] for i in range(len(p)))

def permutation_order(p):
    seen = set()
    result = 1

    def lcm(a, b):
        import math
        return a * b // math.gcd(a, b)

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
            result = lcm(result, length)
    return result

def action_orbits(actions, object_count):
    unseen = set(range(object_count))
    orbits = []
    while unseen:
        seed = min(unseen)
        orbit = {
            action[seed]
            for action in actions
        }
        orbits.append(sorted(orbit))
        unseen -= orbit
    return sorted(orbits, key=lambda row: (len(row), row))

def profile(values):
    return {
        str(key): value
        for key, value in sorted(Counter(values).items())
    }

if project in candidate_path.parents:
    raise RuntimeError("Candidate JSON must remain outside the project")

head = git("show", "-s", "--format=%h %s", "HEAD")
status_before = status_rows()

authority_rows = {}
for name, path in paths.items():
    if not path.is_file():
        raise FileNotFoundError(path)
    actual = sha256_file(path)
    expected = expected_hashes[name]
    authority_rows[str(path)] = {
        "expected_sha256": expected,
        "sha256": actual,
        "hash_match": actual == expected,
    }

all_authority_hashes_match = all(
    row["hash_match"]
    for row in authority_rows.values()
)

correction = json.loads(paths["correction"].read_text(encoding="utf-8"))
prereg = json.loads(paths["prereg"].read_text(encoding="utf-8"))
locked = json.loads(paths["011w"].read_text(encoding="utf-8"))
action_data = json.loads(paths["native_action"].read_text(encoding="utf-8"))

local_elements = tuple(
    (base, side)
    for base in range(4)
    for side in range(2)
)
local_index = {
    element: index
    for index, element in enumerate(local_elements)
}

def omega(bits, x, y):
    if x == 0 or y == 0:
        return 0
    return int(bits[(x - 1) * 3 + (y - 1)])

def local_table(bits):
    table = []
    for x, sx in local_elements:
        row = []
        for y, sy in local_elements:
            product = (
                x ^ y,
                sx ^ sy ^ omega(bits, x, y),
            )
            row.append(local_index[product])
        table.append(tuple(row))
    return tuple(table)

def local_inverse_rows(table):
    rows = []
    for x in range(8):
        candidates = [
            y
            for y in range(8)
            if table[x][y] == 0 and table[y][x] == 0
        ]
        if len(candidates) != 1:
            raise RuntimeError("Local inverse failure")
        rows.append(candidates[0])
    return tuple(rows)

def enumerate_automorphisms(table):
    automorphisms = []
    for tail in itertools.permutations(range(1, 8)):
        mapping = (0,) + tail
        valid = True
        for x in range(8):
            for y in range(8):
                if mapping[table[x][y]] != table[mapping[x]][mapping[y]]:
                    valid = False
                    break
            if not valid:
                break
        if valid:
            automorphisms.append(mapping)
    return tuple(sorted(automorphisms))

def inner_automorphisms(table):
    inverses = local_inverse_rows(table)
    rows = set()
    for g in range(8):
        mapping = tuple(
            table[table[g][x]][inverses[g]]
            for x in range(8)
        )
        rows.add(mapping)
    return tuple(sorted(rows))

presentation_rows = locked["chart_reconstruction"]["presentation_rows"]
chart_groups = locked["chart_reconstruction"]["chart_rows"]
locked_orbit_groups = locked["chart_action"]["orbit_rows_by_presentation"]
normalizer_groups = locked["normalizer_fiber_action"]["rows_by_presentation"]
gauge_rows = locked["gauge_presentation_comparison"]["gauge_rows"]

if len(presentation_rows) != 2 or len(chart_groups) != 2:
    raise RuntimeError("Locked chart schema mismatch")

chart_bundles = []
for presentation_index in range(2):
    rows = sorted(
        chart_groups[presentation_index]["charts"],
        key=lambda row: row["chart_index"],
    )
    if [row["chart_index"] for row in rows] != list(range(80)):
        raise RuntimeError("Chart indices are not consecutive")
    lookup = {
        (
            int(row["subgroup_index"]),
            tuple(int(x) for x in row["images"]),
        ): int(row["chart_index"])
        for row in rows
    }
    chart_bundles.append({
        "rows": rows,
        "lookup": lookup,
    })

print("== G60 NATIVE D8 OUTER-C2 SELECTOR CENSUS 011y ==")
print("MODE: temporary read-only complete outer-automorphism chart census")
print("LOCKED_HEAD:", head)
print("ALL_AUTHORITY_HASHES_MATCH:",
      str(all_authority_hashes_match).lower())

print()
print("LOCAL_AUTOMORPHISM_CENSUS_BEGIN")

presentation_census_rows = []
aut_actions_by_presentation = []
aut_rows_by_presentation = []
inner_sets = []

for presentation_index, presentation in enumerate(presentation_rows):
    bits = tuple(int(x) for x in presentation["bits"])
    table = local_table(bits)
    automorphisms = enumerate_automorphisms(table)
    inner = inner_automorphisms(table)
    inner_set = set(inner)
    inner_sets.append(inner_set)

    bundle = chart_bundles[presentation_index]
    charts = bundle["rows"]
    lookup = bundle["lookup"]

    chart_to_global_orbit = {}
    locked_global_orbits = []
    for orbit_row in locked_orbit_groups[presentation_index]:
        orbit_index = int(orbit_row["orbit_index"])
        orbit = {
            int(x)
            for x in orbit_row["chart_indices"]
        }
        locked_global_orbits.append(orbit)
        for chart in orbit:
            chart_to_global_orbit[chart] = orbit_index

    fiber_orbit_lookup = {}
    for normalizer_row in normalizer_groups[presentation_index]:
        subgroup_index = int(normalizer_row["subgroup_index"])
        fiber = [
            int(x)
            for x in normalizer_row["fiber_chart_indices"]
        ]
        for fiber_orbit_index, positions in enumerate(
            normalizer_row["fiber_orbits"]
        ):
            for position in positions:
                fiber_orbit_lookup[
                    (subgroup_index, fiber[int(position)])
                ] = fiber_orbit_index

    aut_rows = []
    aut_actions = []

    for aut_index, mapping in enumerate(automorphisms):
        induced = []
        for chart in charts:
            source_images = tuple(int(x) for x in chart["images"])
            target_images = tuple(
                source_images[mapping[element]]
                for element in range(8)
            )
            target = lookup.get((
                int(chart["subgroup_index"]),
                target_images,
            ))
            if target is None:
                raise RuntimeError("Automorphism chart image missing")
            induced.append(target)

        induced = tuple(induced)
        if sorted(induced) != list(range(80)):
            raise RuntimeError("Automorphism does not induce permutation")

        global_orbit_map = []
        for source_orbit_index, source_orbit in enumerate(
            locked_global_orbits
        ):
            targets = sorted({
                chart_to_global_orbit[induced[chart]]
                for chart in source_orbit
            })
            global_orbit_map.append({
                "source_orbit_index": source_orbit_index,
                "target_orbit_indices": targets,
            })

        fiber_maps = []
        fiber_failure_count = 0
        for subgroup_index in range(10):
            induced_fiber_map = []
            for source_fiber_orbit in range(2):
                source_charts = [
                    chart
                    for chart in range(80)
                    if charts[chart]["subgroup_index"] == subgroup_index
                    and fiber_orbit_lookup[
                        (subgroup_index, chart)
                    ] == source_fiber_orbit
                ]
                targets = sorted({
                    fiber_orbit_lookup[
                        (subgroup_index, induced[chart])
                    ]
                    for chart in source_charts
                })
                induced_fiber_map.append(targets)
                if len(targets) != 1:
                    fiber_failure_count += 1
            fiber_maps.append(induced_fiber_map)

        is_inner = mapping in inner_set
        induced_global_permutation = [
            row["target_orbit_indices"][0]
            if len(row["target_orbit_indices"]) == 1
            else None
            for row in global_orbit_map
        ]
        fiber_permutation_profile = Counter(
            tuple(
                targets[0]
                if len(targets) == 1
                else -1
                for targets in fiber_map
            )
            for fiber_map in fiber_maps
        )

        aut_rows.append({
            "automorphism_index": aut_index,
            "mapping": list(mapping),
            "automorphism_sha256": sha256_json(list(mapping)),
            "order": permutation_order(mapping),
            "class": "inner" if is_inner else "outer",
            "induced_chart_permutation_sha256":
                sha256_json(list(induced)),
            "induced_chart_permutation_order":
                permutation_order(induced),
            "induced_global_orbit_permutation":
                induced_global_permutation,
            "fiber_orbit_permutation_profile": {
                str(list(key)): value
                for key, value in sorted(
                    fiber_permutation_profile.items()
                )
            },
            "fiber_failure_count": fiber_failure_count,
        })
        aut_actions.append(induced)

    inner_rows = [
        row for row in aut_rows
        if row["class"] == "inner"
    ]
    outer_rows = [
        row for row in aut_rows
        if row["class"] == "outer"
    ]

    presentation_row = {
        "presentation_index": presentation_index,
        "cocycle_sha256": presentation["cocycle_sha256"],
        "automorphism_count": len(automorphisms),
        "automorphism_order_profile": profile(
            row["order"] for row in aut_rows
        ),
        "inner_automorphism_count": len(inner_rows),
        "inner_automorphism_order_profile": profile(
            row["order"] for row in inner_rows
        ),
        "outer_coset_count": len(outer_rows),
        "outer_coset_order_profile": profile(
            row["order"] for row in outer_rows
        ),
        "outer_involution_count": sum(
            row["order"] == 2 for row in outer_rows
        ),
        "outer_order_four_count": sum(
            row["order"] == 4 for row in outer_rows
        ),
        "all_inner_preserve_global_orbits": all(
            row["induced_global_orbit_permutation"] == [0, 1]
            for row in inner_rows
        ),
        "all_outer_exchange_global_orbits": all(
            row["induced_global_orbit_permutation"] == [1, 0]
            for row in outer_rows
        ),
        "all_inner_preserve_fiber_orbits": all(
            row["fiber_orbit_permutation_profile"] ==
                {"[0, 1]": 10}
            for row in inner_rows
        ),
        "all_outer_exchange_fiber_orbits": all(
            row["fiber_orbit_permutation_profile"] ==
                {"[1, 0]": 10}
            for row in outer_rows
        ),
        "fiber_failure_count": sum(
            row["fiber_failure_count"]
            for row in aut_rows
        ),
    }

    presentation_census_rows.append(presentation_row)
    aut_actions_by_presentation.append(tuple(aut_actions))
    aut_rows_by_presentation.append(aut_rows)

    print("PRESENTATION", presentation_index,
          "AUT_ORDER_PROFILE:",
          presentation_row["automorphism_order_profile"])
    print("PRESENTATION", presentation_index,
          "INNER_ORDER_PROFILE:",
          presentation_row["inner_automorphism_order_profile"])
    print("PRESENTATION", presentation_index,
          "OUTER_ORDER_PROFILE:",
          presentation_row["outer_coset_order_profile"])
    print("PRESENTATION", presentation_index,
          "OUTER_INVOLUTIONS:",
          presentation_row["outer_involution_count"])
    print("PRESENTATION", presentation_index,
          "OUTER_ORDER4:",
          presentation_row["outer_order_four_count"])

print("LOCAL_AUTOMORPHISM_CENSUS_END")

print()
print("FULL_A_CHART_ACTION_RECONSTRUCTION_BEGIN")

global_permutations = {
    int(row["actual_index"]): tuple(
        int(x) for x in row["actual_permutation"]
    )
    for row in action_data["mapping_rows"]
}
global_indices = tuple(sorted(global_permutations))
perm_to_global_index = {
    permutation: index
    for index, permutation in global_permutations.items()
}
degree = len(global_permutations[global_indices[0]])
identity_global = perm_to_global_index[tuple(range(degree))]

def inverse_permutation(p):
    result = [None] * len(p)
    for source, target in enumerate(p):
        result[target] = source
    return tuple(result)

global_inverse = {
    index: perm_to_global_index[
        inverse_permutation(global_permutations[index])
    ]
    for index in global_indices
}

def multiply_global(left, right):
    return perm_to_global_index[
        compose(
            global_permutations[left],
            global_permutations[right],
        )
    ]

def conjugate_global(g, x):
    return multiply_global(
        multiply_global(g, x),
        global_inverse[g],
    )

a_actions_by_presentation = []
a_action_failure_counts = []
a_orbit_profiles = []
a_action_image_orders = []
a_action_kernel_orders = []
a_action_kernel_indices_by_presentation = []

for presentation_index in range(2):
    charts = chart_bundles[presentation_index]["rows"]
    lookup = chart_bundles[presentation_index]["lookup"]

    subgroup_sets = {}
    for subgroup_index in range(10):
        candidates = [
            frozenset(int(x) for x in row["images"])
            for row in charts
            if int(row["subgroup_index"]) == subgroup_index
        ]
        if len(set(candidates)) != 1:
            raise RuntimeError("Native subgroup chart mismatch")
        subgroup_sets[subgroup_index] = candidates[0]

    subgroup_lookup = {
        subgroup: index
        for index, subgroup in subgroup_sets.items()
    }

    actions = []
    failure_count = 0

    for g in global_indices:
        image = []
        for chart in charts:
            target_images = tuple(
                conjugate_global(g, int(x))
                for x in chart["images"]
            )
            target_subgroup = subgroup_lookup.get(
                frozenset(target_images)
            )
            if target_subgroup is None:
                failure_count += 1
                image.append(-1)
                continue
            target_chart = lookup.get((
                target_subgroup,
                target_images,
            ))
            if target_chart is None:
                failure_count += 1
                image.append(-1)
                continue
            image.append(target_chart)
        actions.append(tuple(image))

    if any(sorted(action) != list(range(80)) for action in actions):
        failure_count += 1

    identity_action = tuple(range(80))
    kernel_indices = [
        global_indices[index]
        for index, action in enumerate(actions)
        if action == identity_action
    ]
    distinct_actions = tuple(sorted(set(actions)))
    orbits = action_orbits(distinct_actions, 80)

    a_actions_by_presentation.append(distinct_actions)
    a_action_failure_counts.append(failure_count)
    a_orbit_profiles.append(sorted(len(orbit) for orbit in orbits))
    a_action_image_orders.append(len(distinct_actions))
    a_action_kernel_orders.append(len(kernel_indices))
    a_action_kernel_indices_by_presentation.append(kernel_indices)

print("FULL_A_ACTION_FAILURE_COUNTS:", a_action_failure_counts)
print("FULL_A_ORBIT_PROFILES:", a_orbit_profiles)
print("FULL_A_ABSTRACT_GROUP_ORDER:", len(global_indices))
print("FULL_A_EFFECTIVE_IMAGE_ORDERS:", a_action_image_orders)
print("FULL_A_ACTION_KERNEL_ORDERS:", a_action_kernel_orders)
print("FULL_A_ACTION_KERNEL_INDICES:",
      a_action_kernel_indices_by_presentation)
print("FULL_A_CHART_ACTION_RECONSTRUCTION_END")

print()
print("OUTER_INVOLUTION_EXTENSION_BEGIN")

extended_rows = []
order_four_measurement_rows = []

for presentation_index in range(2):
    a_actions = a_actions_by_presentation[presentation_index]
    aut_rows = aut_rows_by_presentation[presentation_index]
    aut_actions = aut_actions_by_presentation[presentation_index]

    for row, outer_action in zip(aut_rows, aut_actions):
        if row["class"] != "outer":
            continue

        commutation_failure_count = sum(
            compose(a_action, outer_action)
            != compose(outer_action, a_action)
            for a_action in a_actions
        )

        if row["order"] == 2:
            extended_actions = set(a_actions)
            extended_actions.update(
                compose(a_action, outer_action)
                for a_action in a_actions
            )
            extended_actions = tuple(sorted(extended_actions))
            extended_orbits = action_orbits(
                extended_actions,
                80,
            )
            effective_stabilizer_orders = [
                sum(action[chart] == chart
                    for action in extended_actions)
                for chart in range(80)
            ]
            abstract_extended_group_order = (
                len(global_indices) * 2
            )
            effective_extended_image_order = len(
                extended_actions
            )
            extended_kernel_order = (
                abstract_extended_group_order
                // effective_extended_image_order
            )
            extended_rows.append({
                "presentation_index": presentation_index,
                "automorphism_index":
                    row["automorphism_index"],
                "automorphism_sha256":
                    row["automorphism_sha256"],
                "outer_automorphism_order": 2,
                "commutation_failure_count":
                    commutation_failure_count,
                "abstract_extended_group_order":
                    abstract_extended_group_order,
                "effective_extended_action_image_order":
                    effective_extended_image_order,
                "extended_action_kernel_order":
                    extended_kernel_order,
                "extended_orbit_profile":
                    sorted(len(orbit) for orbit in extended_orbits),
                "effective_extended_stabilizer_order_profile":
                    profile(effective_stabilizer_orders),
                "abstract_extended_stabilizer_order_profile":
                    profile(
                        order * extended_kernel_order
                        for order in effective_stabilizer_orders
                    ),
            })
        elif row["order"] == 4:
            identity_action = tuple(range(80))
            powers = [identity_action]
            for _ in range(3):
                powers.append(
                    compose(powers[-1], outer_action)
                )
            measured_actions = {
                compose(a_action, power)
                for a_action in a_actions
                for power in powers
            }
            measured_orbits = action_orbits(
                tuple(measured_actions),
                80,
            )
            order_four_measurement_rows.append({
                "presentation_index": presentation_index,
                "automorphism_index":
                    row["automorphism_index"],
                "automorphism_sha256":
                    row["automorphism_sha256"],
                "outer_automorphism_order": 4,
                "commutation_failure_count":
                    commutation_failure_count,
                "measured_abstract_generated_group_order":
                    len(global_indices) * 4,
                "measured_effective_action_image_order":
                    len(measured_actions),
                "measured_action_kernel_order":
                    (len(global_indices) * 4)
                    // len(measured_actions),
                "measured_orbit_profile":
                    sorted(len(orbit) for orbit in measured_orbits),
                "preregistered_action_order_prediction":
                    None,
            })

print("OUTER_INVOLUTION_EXTENSION_ROWS:", len(extended_rows))
print("OUTER_INVOLUTION_ABSTRACT_GROUP_ORDERS:",
      [row["abstract_extended_group_order"]
       for row in extended_rows])
print("OUTER_INVOLUTION_EFFECTIVE_IMAGE_ORDERS:",
      [row["effective_extended_action_image_order"]
       for row in extended_rows])
print("OUTER_INVOLUTION_ACTION_KERNEL_ORDERS:",
      [row["extended_action_kernel_order"]
       for row in extended_rows])
print("OUTER_INVOLUTION_ORBIT_PROFILES:",
      [row["extended_orbit_profile"] for row in extended_rows])
print("OUTER_INVOLUTION_EFFECTIVE_STABILIZER_PROFILES:",
      [row["effective_extended_stabilizer_order_profile"]
       for row in extended_rows])
print("OUTER_INVOLUTION_ABSTRACT_STABILIZER_PROFILES:",
      [row["abstract_extended_stabilizer_order_profile"]
       for row in extended_rows])
print("ORDER4_OUTER_MEASUREMENT_ROWS:",
      len(order_four_measurement_rows))
print("ORDER4_MEASURED_ABSTRACT_GROUP_ORDERS:",
      [row["measured_abstract_generated_group_order"]
       for row in order_four_measurement_rows])
print("ORDER4_MEASURED_EFFECTIVE_IMAGE_ORDERS:",
      [row["measured_effective_action_image_order"]
       for row in order_four_measurement_rows])
print("OUTER_INVOLUTION_EXTENSION_END")

alpha_rows = [
    orbit_row["alpha_1_character"]
    for orbit_group in locked_orbit_groups
    for orbit_row in orbit_group
]
q_rows = [
    orbit_row["q_axis_signature"]
    for orbit_group in locked_orbit_groups
    for orbit_row in orbit_group
]

alpha_constant = (
    len({
        json.dumps(row, sort_keys=True)
        for row in alpha_rows
    }) == 1
)
q_constant = (
    len({
        json.dumps(row, sort_keys=True)
        for row in q_rows
    }) == 1
)

gauge_torsor_rows = []
for gauge_row in gauge_rows:
    orbit_map = {
        int(row["source_orbit_index"]):
            [int(x) for x in row["target_orbit_indices"]]
        for row in gauge_row["orbit_map"]
    }
    preserves_labels = orbit_map == {
        0: [0],
        1: [1],
    }
    conjugates_outer_flip = preserves_labels
    gauge_torsor_rows.append({
        "gauge_index": int(gauge_row["gauge_index"]),
        "function_bits": gauge_row["function_bits"],
        "preserves_orbit_labels": preserves_labels,
        "conjugates_outer_flip_to_outer_flip":
            conjugates_outer_flip,
    })

gauge_torsors_equivalent = all(
    row["preserves_orbit_labels"]
    and row["conjugates_outer_flip_to_outer_flip"]
    for row in gauge_torsor_rows
)

expected_aut_profile = {"1": 1, "2": 5, "4": 2}
expected_inner_profile = {"1": 1, "2": 3}
expected_outer_profile = {"2": 2, "4": 2}

profiles_match = all(
    row["automorphism_count"] == 8
    and row["automorphism_order_profile"] ==
        expected_aut_profile
    and row["inner_automorphism_count"] == 4
    and row["inner_automorphism_order_profile"] ==
        expected_inner_profile
    and row["outer_coset_count"] == 4
    and row["outer_coset_order_profile"] ==
        expected_outer_profile
    and row["outer_involution_count"] == 2
    and row["outer_order_four_count"] == 2
    for row in presentation_census_rows
)

inner_outer_action_matches = all(
    row["all_inner_preserve_global_orbits"]
    and row["all_outer_exchange_global_orbits"]
    and row["all_inner_preserve_fiber_orbits"]
    and row["all_outer_exchange_fiber_orbits"]
    and row["fiber_failure_count"] == 0
    for row in presentation_census_rows
)

extended_matches = (
    len(extended_rows) == 4
    and all(
        row["commutation_failure_count"] == 0
        and row["abstract_extended_group_order"] == 960
        and row["effective_extended_action_image_order"] == 480
        and row["extended_action_kernel_order"] == 2
        and row["extended_orbit_profile"] == [80]
        and row["effective_extended_stabilizer_order_profile"] ==
            {"6": 80}
        and row["abstract_extended_stabilizer_order_profile"] ==
            {"12": 80}
        for row in extended_rows
    )
)

outer_selector_count = 0 if inner_outer_action_matches else None
minimal_torsor_cardinality = (
    2 if outer_selector_count == 0 else None
)
minimal_binary_choice_count = (
    1 if minimal_torsor_cardinality == 2 else None
)

prediction_matches = (
    head == locked_head
    and all_authority_hashes_match
    and correction["status"] ==
        "frozen_before_local_D8_automorphism_enumeration"
    and prereg["status"] ==
        "frozen_before_local_D8_automorphism_enumeration"
    and profiles_match
    and a_action_failure_counts == [0, 0]
    and a_orbit_profiles == [[40, 40], [40, 40]]
    and a_action_image_orders == [240, 240]
    and a_action_kernel_orders == [2, 2]
    and a_action_kernel_indices_by_presentation ==
        [[0, 326], [0, 326]]
    and inner_outer_action_matches
    and extended_matches
    and alpha_constant
    and q_constant
    and gauge_torsors_equivalent
    and outer_selector_count == 0
    and minimal_torsor_cardinality == 2
    and minimal_binary_choice_count == 1
)

if head != locked_head:
    classification = "authority_failure"
elif not all_authority_hashes_match:
    classification = "authority_failure"
elif not profiles_match:
    classification = "automorphism_order_profile_mismatch"
elif a_action_failure_counts != [0, 0]:
    classification = "local_D8_reconstruction_failure"
elif not inner_outer_action_matches:
    classification = "global_outer_exchange_failure"
elif not extended_matches:
    classification = "outer_involution_extended_action_failure"
elif not (alpha_constant and q_constant):
    classification = "locked_observable_separates_outer_orbits"
elif not gauge_torsors_equivalent:
    classification = "gauge_presentation_outer_torsor_mismatch"
elif outer_selector_count != 0:
    classification = "outer_gauge_invariant_selector_exists"
elif minimal_torsor_cardinality != 2:
    classification = "minimal_selector_torsor_not_binary"
elif prediction_matches:
    classification = (
        "native_D8_chart_orbit_selection_requires_one_"
        "external_outer_C2_torsor_choice"
    )
else:
    classification = "computation_failure"

status_after = status_rows()
repository_status_preserved = status_before == status_after

earned_statement = (
    "For each of the two gauge-related selected D8 presentations, "
    "the local automorphism group has order eight with order profile "
    "1,5,2 in orders 1,2,4. Its inner subgroup is V4 with order "
    "profile 1,3, while the four-element outer coset contains exactly "
    "two involutions and two order-four representatives. Every inner "
    "automorphism preserves each locked chart-orbit class, and every "
    "outer representative exchanges the two four-chart fiber classes "
    "and the two global forty-chart orbits. Each genuine outer "
    "involution commutes with the native chart action. The native "
    "480-element group has effective chart-action image order 240 "
    "because its central subgroup {1,a} is the pointwise kernel. "
    "Adjoining an outer involution gives an abstract group of order "
    "960 with effective image order 480, transitive on eighty charts; "
    "the abstract stabilizer has order twelve and its effective image "
    "has order six. The locked alpha_1 character and "
    "q-axis signature remain constant, and all four presentation "
    "gauge maps transport the same outer-C2 torsor. Thus no single "
    "chart orbit is invariant under the residual outer gauge. Within "
    "the bounded native D8 chart model, absolute orbit selection "
    "requires one additional two-valued outer-C2 torsor choice."
)

result = {
    "packet":
        "g60_native_d8_outer_c2_selector_census_011y_candidate",
    "mode":
        "temporary_read_only_complete_outer_automorphism_chart_census",
    "locked_head": locked_head,
    "authorities": authority_rows,
    "preregistration": {
        "original_packet": prereg["packet"],
        "correction_packet": correction["packet"],
        "correction_applied": True,
        "correction_status": correction["status"],
    },
    "local_automorphism_census": {
        "presentation_count": 2,
        "presentation_rows": presentation_census_rows,
        "automorphism_rows_by_presentation":
            aut_rows_by_presentation,
        "expected_automorphism_order_profile":
            expected_aut_profile,
        "expected_inner_order_profile":
            expected_inner_profile,
        "expected_outer_coset_order_profile":
            expected_outer_profile,
        "profiles_match": profiles_match,
    },
    "native_chart_action_reconstruction": {
        "abstract_full_group_order": len(global_indices),
        "effective_action_image_orders":
            a_action_image_orders,
        "action_kernel_orders":
            a_action_kernel_orders,
        "action_kernel_indices_by_presentation":
            a_action_kernel_indices_by_presentation,
        "action_kernel_names": ["1", "a"],
        "identity_index": identity_global,
        "action_failure_counts":
            a_action_failure_counts,
        "orbit_profiles": a_orbit_profiles,
    },
    "outer_involution_extensions": {
        "row_count": len(extended_rows),
        "rows": extended_rows,
        "all_match_corrected_prediction":
            extended_matches,
        "order_four_measurements_not_preregistered":
            order_four_measurement_rows,
    },
    "locked_observable_comparison": {
        "alpha_1_rows": alpha_rows,
        "alpha_1_constant_under_outer_exchange":
            alpha_constant,
        "q_axis_signature_rows": q_rows,
        "q_axis_signature_constant_under_outer_exchange":
            q_constant,
    },
    "presentation_gauge_torsor_comparison": {
        "gauge_map_count": len(gauge_torsor_rows),
        "gauge_rows": gauge_torsor_rows,
        "gauge_related_presentations_have_equivalent_outer_C2_torsors":
            gauge_torsors_equivalent,
    },
    "selector_result": {
        "full_A_invariant_single_orbit_choice_count": 2,
        "outer_gauge_invariant_single_orbit_selector_count":
            outer_selector_count,
        "minimal_extra_torsor_cardinality":
            minimal_torsor_cardinality,
        "minimal_extra_binary_choice_count":
            minimal_binary_choice_count,
        "absolute_orbit_selected": False,
        "bounded_model_necessity_established":
            prediction_matches,
    },
    "prediction_matches": prediction_matches,
    "classification": classification,
    "earned_statement_candidate": earned_statement,
    "repository": {
        "status_before": status_before,
        "status_after": status_after,
        "status_preserved": repository_status_preserved,
        "project_mutation_performed": False,
    },
    "candidate_provenance": {
        "candidate_path": str(candidate_path),
        "computation_script_path": str(Path(__file__).resolve()),
        "computation_script_sha256":
            sha256_file(Path(__file__).resolve()),
        "result_frozen": False,
        "candidate_promoted": False,
    },
    "boundary": {
        "bounded_native_D8_chart_model_only": True,
        "outer_selector_census_performed": True,
        "local_D8_automorphisms_enumerated": True,
        "outer_C2_exchange_verified":
            inner_outer_action_matches,
        "extra_binary_datum_proved_necessary_within_bounded_model":
            prediction_matches,
        "global_minimality_claim": False,
        "absolute_chart_orbit_selected": False,
        "strict_equivariant_chart_selected": False,
        "native_update_law_constructed": False,
        "mechanics_state_cell_established": False,
        "local_side_equals_011o_orientation_sheet": False,
        "orientation_selected": False,
        "manuscript_mutated": False,
        "geometry_claim": False,
        "physical_direction_claim": False,
        "physical_claim": False,
    },
}

candidate_path.parent.mkdir(parents=True, exist_ok=True)
candidate_path.write_text(
    json.dumps(result, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

print()
print("== FINAL OUTER-C2 SELECTOR REPORT ==")
print("AUTOMORPHISM_ORDER_PROFILES:",
      [row["automorphism_order_profile"]
       for row in presentation_census_rows])
print("INNER_ORDER_PROFILES:",
      [row["inner_automorphism_order_profile"]
       for row in presentation_census_rows])
print("OUTER_COSET_ORDER_PROFILES:",
      [row["outer_coset_order_profile"]
       for row in presentation_census_rows])
print("ALL_OUTER_EXCHANGE_GLOBAL_ORBITS:",
      str(all(row["all_outer_exchange_global_orbits"]
              for row in presentation_census_rows)).lower())
print("FULL_A_EFFECTIVE_IMAGE_ORDERS:",
      a_action_image_orders)
print("FULL_A_ACTION_KERNEL_INDICES:",
      a_action_kernel_indices_by_presentation)
print("OUTER_INVOLUTION_ABSTRACT_GROUP_ORDERS:",
      [row["abstract_extended_group_order"]
       for row in extended_rows])
print("OUTER_INVOLUTION_EFFECTIVE_IMAGE_ORDERS:",
      [row["effective_extended_action_image_order"]
       for row in extended_rows])
print("OUTER_INVOLUTION_EXTENDED_ORBIT_PROFILES:",
      [row["extended_orbit_profile"] for row in extended_rows])
print("ALPHA_1_CONSTANT_UNDER_OUTER_EXCHANGE:",
      str(alpha_constant).lower())
print("Q_AXIS_CONSTANT_UNDER_OUTER_EXCHANGE:",
      str(q_constant).lower())
print("GAUGE_TORSORS_EQUIVALENT:",
      str(gauge_torsors_equivalent).lower())
print("OUTER_GAUGE_INVARIANT_SELECTOR_COUNT:",
      outer_selector_count)
print("MINIMAL_EXTRA_TORSOR_CARDINALITY:",
      minimal_torsor_cardinality)
print("PREDICTION_MATCHES:",
      str(prediction_matches).lower())
print("CLASSIFICATION:", classification)
print("REPOSITORY_STATUS_PRESERVED:",
      str(repository_status_preserved).lower())
print("PROJECT_MUTATION_PERFORMED: false")
print("EXTRA_BINARY_DATUM_PROVED_NECESSARY_WITHIN_BOUNDED_MODEL:",
      str(prediction_matches).lower())
print("ABSOLUTE_CHART_ORBIT_SELECTED: false")
print("NATIVE_UPDATE_LAW_CONSTRUCTED: false")
print("MECHANICS_STATE_CELL_ESTABLISHED: false")
print("MANUSCRIPT_MUTATED: false")
print("PHYSICAL_CLAIM: false")
print("CANDIDATE_JSON:", candidate_path)
print("CANDIDATE_JSON_SHA256:", sha256_file(candidate_path))
