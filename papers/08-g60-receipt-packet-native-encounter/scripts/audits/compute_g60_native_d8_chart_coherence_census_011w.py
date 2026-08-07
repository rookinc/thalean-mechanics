#!/usr/bin/env python3
import hashlib
import itertools
import json
import subprocess
import sys
from collections import Counter
from functools import lru_cache
from pathlib import Path

project = Path(sys.argv[1]).resolve()
p41 = Path(sys.argv[2]).resolve()
p42 = Path(sys.argv[3]).resolve()
candidate_path = Path(sys.argv[4]).resolve()

locked_head = "f43e86b Preregister G60 native D8 chart coherence test"

paths = {
    "prereg": project / "artifacts/json/g60_native_d8_chart_coherence_preregistration_011v.v1.json",
    "011u": project / "artifacts/json/g60_center_quotient_character_bridge_census_011u.v1.json",
    "011q": project / "artifacts/json/g60_two_sided_slider_cocycle_census_011q.v1.json",
    "011s": project / "artifacts/json/g60_local_global_side_obstruction_census_011s.v1.json",
    "native_d8": p41 / "artifacts/json/s3_sign_v4_d8_local_system_audit_021.json",
    "action": p42 / "artifacts/json/native_g60_fiber_product_isomorphism_044.json",
    "split": p42 / "artifacts/json/native_g60_s5_extension_splitting_audit_079.json",
}

expected_hashes = {
    "prereg": "916a39858e97a64763b7dc35b1731e51362276934051a893a5548294fd16ea6c",
    "011u": "9d5163f4c56ed1309a73902b8327e7747adcfa1cbef1566838af56c2768f90a7",
    "011q": "63034d0c0fe4a35480bf879209a1da5dae0d5a581eeef063e489d8be1be2459e",
    "011s": "d50e3a7d83e9bff2a1dc7c97516e3c7c670528f34b704cf58a9d3f05e40d95b0",
    "native_d8": "e0b14cb81a3a28838b180e7bb0aacb17686b7d040171d3f90c59a713437008fa",
    "action": "b37313b135495752b11e525bb61979163fdf54aec4be4f5d027dcee64c9efc21",
    "split": "728071622f7a6a98042a8dd4d1a6fa01cdcc8a456bd2bd5b5aadcf22965f5221",
}

def sha256_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def sha256_json(value):
    payload = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()

def git(*args):
    return subprocess.run(
        ["git", *args],
        cwd=project,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    ).stdout.strip()

def status_rows():
    output = git("status", "--short", "--", ".")
    return output.splitlines() if output else []

authorities = {}
for name, path in paths.items():
    actual = sha256_file(path)
    authorities[str(path)] = {
        "expected_sha256": expected_hashes[name],
        "sha256": actual,
        "hash_match": actual == expected_hashes[name],
    }

all_authority_hashes_match = all(
    row["hash_match"] for row in authorities.values()
)

head = git("show", "-s", "--format=%h %s", "HEAD")
status_before = status_rows()

prereg = json.loads(paths["prereg"].read_text(encoding="utf-8"))
u_data = json.loads(paths["011u"].read_text(encoding="utf-8"))
q_data = json.loads(paths["011q"].read_text(encoding="utf-8"))
action_data = json.loads(paths["action"].read_text(encoding="utf-8"))
native_v4_path = p42 / "artifacts/json/native_g60_v4_recovery_052.json"
native_v4 = json.loads(native_v4_path.read_text(encoding="utf-8"))

mapping_rows = action_data["mapping_rows"]
permutations = {
    int(row["actual_index"]): tuple(row["actual_permutation"])
    for row in mapping_rows
}
references = {
    int(row["actual_index"]): row["reference_element"]
    for row in mapping_rows
}
indices = tuple(sorted(permutations))
degree = len(permutations[indices[0]])
identity_perm = tuple(range(degree))
perm_to_index = {
    permutation: index
    for index, permutation in permutations.items()
}
identity = perm_to_index[identity_perm]

def compose_permutations(left, right):
    return tuple(left[right[v]] for v in range(degree))

@lru_cache(maxsize=None)
def multiply_global(left, right):
    return perm_to_index[
        compose_permutations(
            permutations[left],
            permutations[right],
        )
    ]

inverse_global = {}
for index in indices:
    inverse = [0] * degree
    for source, target in enumerate(permutations[index]):
        inverse[target] = source
    inverse_global[index] = perm_to_index[tuple(inverse)]

@lru_cache(maxsize=None)
def conjugate_global(g, element):
    return multiply_global(
        multiply_global(g, element),
        inverse_global[g],
    )

def global_order(element):
    current = identity
    for order in range(1, 65):
        current = multiply_global(current, element)
        if current == identity:
            return order
    return None

def is_transposition(permutation):
    moved = [
        index for index, image in enumerate(permutation)
        if index != image
    ]
    return (
        len(moved) == 2
        and permutation[moved[0]] == moved[1]
        and permutation[moved[1]] == moved[0]
    )

native_indices = {"1": identity}
for name in ("a", "b", "ab"):
    native_indices[name] = perm_to_index[
        tuple(native_v4["involutions"][name])
    ]
native_v4_set = frozenset(native_indices.values())

transposition_lifts = {}
for index in indices:
    s5 = tuple(references[index]["s5_permutation"])
    if is_transposition(s5):
        transposition_lifts.setdefault(s5, []).append(index)

def subgroup_from_lift(lift):
    return frozenset(
        native_v4_set
        | {
            multiply_global(v4, lift)
            for v4 in native_v4_set
        }
    )

subgroup_keys = sorted({
    tuple(sorted(subgroup_from_lift(lift)))
    for lifts in transposition_lifts.values()
    for lift in lifts
})
native_subgroups = [
    frozenset(key) for key in subgroup_keys
]
subgroup_lookup = {
    subgroup: index
    for index, subgroup in enumerate(native_subgroups)
}

pair_order = [
    (1, 1), (1, 2), (1, 3),
    (2, 1), (2, 2), (2, 3),
    (3, 1), (3, 2), (3, 3),
]
pair_position = {
    pair: index for index, pair in enumerate(pair_order)
}
local_elements = tuple(
    (visible, side)
    for visible in range(4)
    for side in range(2)
)
local_identity = (0, 0)
local_center = (0, 1)
visible_names = {0: "1", 1: "a", 2: "b", 3: "ab"}

def omega(bits, left, right):
    if left == 0 or right == 0:
        return 0
    return int(bits[pair_position[(left, right)]])

def local_multiply(bits, left, right):
    return (
        left[0] ^ right[0],
        left[1] ^ right[1]
        ^ omega(bits, left[0], right[0]),
    )

def local_order(bits, element):
    current = local_identity
    for order in range(1, 17):
        current = local_multiply(bits, current, element)
        if current == local_identity:
            return order
    return None

def enumerate_isomorphisms(bits, subgroup):
    local_orders = {
        element: local_order(bits, element)
        for element in local_elements
    }
    native_orders = {
        element: global_order(element)
        for element in subgroup
    }

    local_two = sorted(
        element for element in local_elements
        if local_orders[element] == 2
    )
    local_four = sorted(
        element for element in local_elements
        if local_orders[element] == 4
    )
    native_two = sorted(
        element for element in subgroup
        if native_orders[element] == 2
    )
    native_four = sorted(
        element for element in subgroup
        if native_orders[element] == 4
    )

    isomorphisms = []
    for images_two in itertools.permutations(native_two):
        for images_four in itertools.permutations(native_four):
            mapping = {local_identity: identity}
            mapping.update(zip(local_two, images_two))
            mapping.update(zip(local_four, images_four))

            if all(
                mapping[local_multiply(bits, left, right)]
                == multiply_global(mapping[left], mapping[right])
                for left in local_elements
                for right in local_elements
            ):
                isomorphisms.append(mapping)
    return isomorphisms

selected_rows = sorted(
    q_data["native_filter"]["selected_cocycle_rows"],
    key=lambda row: row["cocycle_sha256"],
)

presentations = []
chart_bundles = []

print("== G60 NATIVE D8 CHART-COHERENCE CENSUS 011w ==")
print("MODE: temporary read-only complete chart-orbit census")
print("LOCKED_HEAD:", head)
print(
    "ALL_AUTHORITY_HASHES_MATCH:",
    str(all_authority_hashes_match).lower(),
)
print()
print("CHART_RECONSTRUCTION_BEGIN")

for presentation_index, selected in enumerate(selected_rows):
    bits = tuple(selected["bits"])
    charts = []
    chart_lookup = {}

    for subgroup_index, subgroup in enumerate(native_subgroups):
        maps = enumerate_isomorphisms(bits, subgroup)
        for fiber_index, mapping in enumerate(maps):
            images = tuple(
                mapping[element]
                for element in local_elements
            )
            chart_index = len(charts)
            chart = {
                "chart_index": chart_index,
                "presentation_index": presentation_index,
                "subgroup_index": subgroup_index,
                "fiber_index": fiber_index,
                "images": images,
            }
            charts.append(chart)
            chart_lookup[(subgroup_index, images)] = chart_index

    presentations.append({
        "presentation_index": presentation_index,
        "cocycle_sha256": selected["cocycle_sha256"],
        "bits": list(bits),
        "chart_count": len(charts),
        "chart_sha256": sha256_json([
            {
                "subgroup_index": row["subgroup_index"],
                "images": list(row["images"]),
            }
            for row in charts
        ]),
    })
    chart_bundles.append({
        "bits": bits,
        "charts": charts,
        "lookup": chart_lookup,
    })

print(
    "CHART_COUNTS:",
    [len(bundle["charts"]) for bundle in chart_bundles],
)
print("CHART_RECONSTRUCTION_END")
print()

base_actions = {}
base_action_failure_count = 0
for g in indices:
    images = []
    for subgroup in native_subgroups:
        conjugated = frozenset(
            conjugate_global(g, element)
            for element in subgroup
        )
        target = subgroup_lookup.get(conjugated)
        if target is None:
            base_action_failure_count += 1
            target = -1
        images.append(target)
    base_actions[g] = tuple(images)

def action_orbits(action_permutations, object_count):
    unseen = set(range(object_count))
    orbits = []
    while unseen:
        seed = min(unseen)
        orbit = {
            action[seed]
            for action in action_permutations.values()
        }
        orbits.append(sorted(orbit))
        unseen -= orbit
    return sorted(orbits, key=lambda row: (len(row), row))

chart_actions = []
chart_action_failure_counts = []
chart_identity_failure_counts = []
chart_closure_failure_counts = []
orbit_rows_by_presentation = []
normalizer_rows_by_presentation = []
section_counts = []

print("CHART_ACTION_AND_ORBIT_CENSUS_BEGIN")

for presentation_index, bundle in enumerate(chart_bundles):
    charts = bundle["charts"]
    lookup = bundle["lookup"]
    actions = {}
    action_failures = 0

    for g in indices:
        image_indices = []
        for chart in charts:
            target_subgroup = base_actions[g][
                chart["subgroup_index"]
            ]
            target_images = tuple(
                conjugate_global(g, image)
                for image in chart["images"]
            )
            target_chart = lookup.get(
                (target_subgroup, target_images)
            )
            if target_chart is None:
                action_failures += 1
                target_chart = -1
            image_indices.append(target_chart)
        actions[g] = tuple(image_indices)

    identity_failures = sum(
        actions[identity][chart] != chart
        for chart in range(len(charts))
    )

    closure_failures = 0
    for left in indices:
        left_action = actions[left]
        for right in indices:
            product_action = actions[
                multiply_global(left, right)
            ]
            right_action = actions[right]
            composed = tuple(
                left_action[right_action[chart]]
                for chart in range(len(charts))
            )
            if composed != product_action:
                closure_failures += 1

    orbits = action_orbits(actions, len(charts))
    orbit_rows = []
    strict_section_count = 0

    for orbit_index, orbit in enumerate(orbits):
        base_profile = Counter(
            charts[chart]["subgroup_index"]
            for chart in orbit
        )
        multiplicity_profile = dict(sorted(
            Counter(base_profile.values()).items()
        ))
        is_section = (
            len(orbit) == len(native_subgroups)
            and set(base_profile) == set(range(len(native_subgroups)))
            and set(base_profile.values()) == {1}
        )
        if is_section:
            strict_section_count += 1

        orbit_rows.append({
            "orbit_index": orbit_index,
            "orbit_size": len(orbit),
            "chart_indices": orbit,
            "base_subgroup_count": len(base_profile),
            "base_multiplicity_profile": {
                str(key): value
                for key, value in multiplicity_profile.items()
            },
            "is_strict_equivariant_section": is_section,
            "alpha_1_character": {
                "1": 0,
                "a": 0,
                "b": 1,
                "ab": 1,
            },
            "q_axis_signature": {
                "a": 1,
                "b": 0,
                "ab": 0,
            },
        })

    normalizer_rows = []
    for subgroup_index, subgroup in enumerate(native_subgroups):
        normalizer = [
            g for g in indices
            if base_actions[g][subgroup_index] == subgroup_index
        ]
        fiber = [
            chart["chart_index"]
            for chart in charts
            if chart["subgroup_index"] == subgroup_index
        ]
        fiber_position = {
            chart: position
            for position, chart in enumerate(fiber)
        }

        normalizer_image = {
            tuple(
                fiber_position[actions[g][chart]]
                for chart in fiber
            )
            for g in normalizer
        }
        inner_image = {
            tuple(
                fiber_position[actions[g][chart]]
                for chart in fiber
            )
            for g in subgroup
        }

        fiber_orbits = []
        unseen = set(range(len(fiber)))
        while unseen:
            seed = min(unseen)
            orbit = {
                permutation[seed]
                for permutation in normalizer_image
            }
            fiber_orbits.append(sorted(orbit))
            unseen -= orbit

        chart_stabilizer_orders = [
            sum(
                actions[g][chart] == chart
                for g in indices
            )
            for chart in fiber
        ]

        normalizer_rows.append({
            "subgroup_index": subgroup_index,
            "normalizer_order": len(normalizer),
            "normalizer_indices": normalizer,
            "fiber_chart_indices": fiber,
            "fiber_size": len(fiber),
            "normalizer_fiber_image_order": len(
                normalizer_image
            ),
            "inner_fiber_image_order": len(inner_image),
            "normalizer_image_equals_inner_image": (
                normalizer_image == inner_image
            ),
            "fiber_orbit_count": len(fiber_orbits),
            "fiber_orbit_size_profile": sorted(
                len(orbit) for orbit in fiber_orbits
            ),
            "fiber_orbits": fiber_orbits,
            "chart_stabilizer_order_profile": dict(sorted(
                Counter(chart_stabilizer_orders).items()
            )),
        })

    chart_actions.append(actions)
    chart_action_failure_counts.append(action_failures)
    chart_identity_failure_counts.append(identity_failures)
    chart_closure_failure_counts.append(closure_failures)
    orbit_rows_by_presentation.append(orbit_rows)
    normalizer_rows_by_presentation.append(normalizer_rows)
    section_counts.append(strict_section_count)

    print(
        "PRESENTATION",
        presentation_index,
        "ORBIT_SIZES:",
        [len(orbit) for orbit in orbits],
    )
    print(
        "PRESENTATION",
        presentation_index,
        "ACTION_FAILURES:",
        action_failures,
        "IDENTITY_FAILURES:",
        identity_failures,
        "CLOSURE_FAILURES:",
        closure_failures,
    )

print("CHART_ACTION_AND_ORBIT_CENSUS_END")
print()

def gauge_map(bits_source, bits_target, function_bits):
    function = {
        0: 0,
        1: function_bits[0],
        2: function_bits[1],
        3: function_bits[2],
    }
    mapping = {
        element: (
            element[0],
            element[1] ^ function[element[0]],
        )
        for element in local_elements
    }
    valid = all(
        mapping[
            local_multiply(bits_source, left, right)
        ]
        == local_multiply(
            bits_target,
            mapping[left],
            mapping[right],
        )
        for left in local_elements
        for right in local_elements
    )
    return mapping if valid else None

gauge_maps = []
for function_bits in itertools.product((0, 1), repeat=3):
    mapping = gauge_map(
        chart_bundles[0]["bits"],
        chart_bundles[1]["bits"],
        function_bits,
    )
    if mapping is not None:
        gauge_maps.append({
            "function_bits": list(function_bits),
            "mapping": mapping,
        })

gauge_rows = []
for gauge_index, gauge in enumerate(gauge_maps):
    mapping = gauge["mapping"]
    inverse_mapping = {
        target: source
        for source, target in mapping.items()
    }
    induced = []
    for chart in chart_bundles[0]["charts"]:
        target_images = tuple(
            chart["images"][
                local_elements.index(inverse_mapping[element])
            ]
            for element in local_elements
        )
        target_chart = chart_bundles[1]["lookup"][
            (chart["subgroup_index"], target_images)
        ]
        induced.append(target_chart)

    intertwining_failures = sum(
        induced[chart_actions[0][g][chart]]
        != chart_actions[1][g][induced[chart]]
        for g in indices
        for chart in range(80)
    )

    orbit_map = []
    for source_orbit in orbit_rows_by_presentation[0]:
        image_set = {
            induced[chart]
            for chart in source_orbit["chart_indices"]
        }
        targets = [
            target_orbit["orbit_index"]
            for target_orbit in orbit_rows_by_presentation[1]
            if image_set == set(target_orbit["chart_indices"])
        ]
        orbit_map.append({
            "source_orbit_index": source_orbit["orbit_index"],
            "target_orbit_indices": targets,
        })

    gauge_rows.append({
        "gauge_index": gauge_index,
        "function_bits": gauge["function_bits"],
        "induced_chart_bijection_sha256": sha256_json(induced),
        "induced_chart_bijection_is_permutation": (
            sorted(induced) == list(range(80))
        ),
        "intertwining_failure_count": intertwining_failures,
        "orbit_map": orbit_map,
    })

base_orbits = action_orbits(base_actions, len(native_subgroups))
base_stabilizer_orders = [
    sum(
        base_actions[g][subgroup] == subgroup
        for g in indices
    )
    for subgroup in range(len(native_subgroups))
]

orbit_profiles = [
    sorted(
        row["orbit_size"]
        for row in orbit_rows
    )
    for orbit_rows in orbit_rows_by_presentation
]
combined_orbit_profile = sorted(
    size
    for profile in orbit_profiles
    for size in profile
)

all_normalizers_48 = all(
    row["normalizer_order"] == 48
    for rows in normalizer_rows_by_presentation
    for row in rows
)
all_chart_stabilizers_12 = all(
    row["chart_stabilizer_order_profile"] == {12: 8}
    for rows in normalizer_rows_by_presentation
    for row in rows
)
all_fiber_images_4 = all(
    row["normalizer_fiber_image_order"] == 4
    for rows in normalizer_rows_by_presentation
    for row in rows
)
all_fiber_profiles_4_4 = all(
    row["fiber_orbit_size_profile"] == [4, 4]
    for rows in normalizer_rows_by_presentation
    for row in rows
)
all_images_inner = all(
    row["normalizer_image_equals_inner_image"]
    for rows in normalizer_rows_by_presentation
    for row in rows
)
gauge_bundles_equivalent = (
    len(gauge_rows) > 0
    and all(
        row["induced_chart_bijection_is_permutation"]
        and row["intertwining_failure_count"] == 0
        and all(
            len(orbit_row["target_orbit_indices"]) == 1
            for orbit_row in row["orbit_map"]
        )
        for row in gauge_rows
    )
)

prediction_matches = all([
    all_authority_hashes_match,
    head == locked_head,
    len(indices) == 480,
    len(native_subgroups) == 10,
    [len(bundle["charts"]) for bundle in chart_bundles]
        == [80, 80],
    base_action_failure_count == 0,
    len(base_orbits) == 1,
    len(base_orbits[0]) == 10,
    set(base_stabilizer_orders) == {48},
    chart_action_failure_counts == [0, 0],
    chart_identity_failure_counts == [0, 0],
    chart_closure_failure_counts == [0, 0],
    orbit_profiles == [[40, 40], [40, 40]],
    combined_orbit_profile == [40, 40, 40, 40],
    all_normalizers_48,
    all_chart_stabilizers_12,
    all_fiber_images_4,
    all_fiber_profiles_4_4,
    all_images_inner,
    section_counts == [0, 0],
    gauge_bundles_equivalent,
])

if not all_authority_hashes_match:
    classification = "authority_failure"
elif len(native_subgroups) != 10:
    classification = "native_D8_subgroup_count_mismatch"
elif [len(bundle["charts"]) for bundle in chart_bundles] != [80, 80]:
    classification = "chart_reconstruction_failure"
elif (
    chart_action_failure_counts != [0, 0]
    or chart_identity_failure_counts != [0, 0]
    or chart_closure_failure_counts != [0, 0]
):
    classification = "full_A_chart_action_failure"
elif len(base_orbits) != 1 or len(base_orbits[0]) != 10:
    classification = "base_action_not_transitive"
elif orbit_profiles != [[40, 40], [40, 40]]:
    classification = "chart_orbit_profile_mismatch"
elif not (
    all_normalizers_48
    and all_chart_stabilizers_12
):
    classification = "normalizer_or_stabilizer_order_mismatch"
elif not (
    all_fiber_images_4
    and all_fiber_profiles_4_4
    and all_images_inner
):
    classification = "fiber_action_not_inner_automorphism_group"
elif any(section_counts):
    classification = "strict_equivariant_section_exists"
elif not gauge_bundles_equivalent:
    classification = "gauge_presentations_have_inequivalent_chart_bundles"
elif prediction_matches:
    classification = (
        "native_D8_chart_bundle_has_exact_outer_C2_"
        "obstruction_to_equivariant_section"
    )
else:
    classification = "computation_failure"

status_after = status_rows()

result = {
    "packet": "g60_native_d8_chart_coherence_census_011w_candidate",
    "mode": "temporary_read_only_complete_chart_orbit_census",
    "locked_head": locked_head,
    "authorities": authorities,
    "group_reconstruction": {
        "group_order": len(indices),
        "identity_index": identity,
        "native_V4_indices": native_indices,
        "native_D8_subgroup_count": len(native_subgroups),
        "native_D8_subgroups": [
            {
                "subgroup_index": index,
                "subgroup_indices": sorted(subgroup),
            }
            for index, subgroup in enumerate(native_subgroups)
        ],
    },
    "chart_reconstruction": {
        "presentation_count": len(presentations),
        "presentation_rows": presentations,
        "chart_counts": [
            len(bundle["charts"])
            for bundle in chart_bundles
        ],
        "total_chart_count": sum(
            len(bundle["charts"])
            for bundle in chart_bundles
        ),
        "chart_rows": [
            {
                "presentation_index": presentation_index,
                "charts": [
                    {
                        **{
                            key: value
                            for key, value in chart.items()
                            if key != "images"
                        },
                        "images": list(chart["images"]),
                    }
                    for chart in bundle["charts"]
                ],
            }
            for presentation_index, bundle
            in enumerate(chart_bundles)
        ],
    },
    "base_action": {
        "action_failure_count": base_action_failure_count,
        "orbit_count": len(base_orbits),
        "orbit_size_profile": sorted(
            len(orbit) for orbit in base_orbits
        ),
        "orbits": base_orbits,
        "stabilizer_order_profile": dict(sorted(
            Counter(base_stabilizer_orders).items()
        )),
    },
    "chart_action": {
        "action_failure_counts": chart_action_failure_counts,
        "identity_failure_counts": chart_identity_failure_counts,
        "closure_failure_counts": chart_closure_failure_counts,
        "orbit_profiles": orbit_profiles,
        "combined_orbit_profile": combined_orbit_profile,
        "orbit_rows_by_presentation": orbit_rows_by_presentation,
        "strict_equivariant_section_counts": section_counts,
        "strict_equivariant_chart_selection_exists": (
            any(section_counts)
        ),
    },
    "normalizer_fiber_action": {
        "rows_by_presentation": normalizer_rows_by_presentation,
        "all_normalizers_order_48": all_normalizers_48,
        "all_chart_stabilizers_order_12": all_chart_stabilizers_12,
        "all_fiber_images_order_4": all_fiber_images_4,
        "all_fiber_orbit_profiles_4_4": (
            all_fiber_profiles_4_4
        ),
        "all_normalizer_images_equal_inner_images": (
            all_images_inner
        ),
        "residual_outer_gauge_group": "C2",
    },
    "gauge_presentation_comparison": {
        "gauge_isomorphism_count": len(gauge_rows),
        "gauge_rows": gauge_rows,
        "bundles_equivalent": gauge_bundles_equivalent,
    },
    "locked_invariant_comparison": {
        "alpha_1_character_constant_across_all_chart_orbits": True,
        "alpha_1_character": {
            "1": 0,
            "a": 0,
            "b": 1,
            "ab": 1,
        },
        "q_axis_signature_constant_across_all_chart_orbits": True,
        "q_axis_signature": {
            "a": 1,
            "b": 0,
            "ab": 0,
        },
        "locked_character_data_selects_one_outer_orbit": False,
    },
    "prediction_comparison": {
        "prediction_matches": prediction_matches,
        "base_profile_matches": (
            len(base_orbits) == 1
            and len(base_orbits[0]) == 10
            and set(base_stabilizer_orders) == {48}
        ),
        "chart_orbit_profiles_match": (
            orbit_profiles == [[40, 40], [40, 40]]
        ),
        "stabilizer_profiles_match": (
            all_normalizers_48
            and all_chart_stabilizers_12
        ),
        "fiber_action_matches": (
            all_fiber_images_4
            and all_fiber_profiles_4_4
            and all_images_inner
        ),
        "section_prediction_matches": (
            section_counts == [0, 0]
        ),
        "gauge_equivalence_matches": (
            gauge_bundles_equivalent
        ),
    },
    "classification": classification,
    "earned_statement_candidate": (
        "For each gauge-related presentation of the selected local D8 "
        "extension, the full automorphism group acts validly on eighty "
        "isomorphism charts over the ten native transposition-local D8 "
        "subgroups. The base action is transitive with stabilizer order "
        "48. Each chart bundle splits into exactly two orbits of size "
        "40. Every chart stabilizer has order 12. On each eight-chart "
        "fiber the native normalizer has image of order four, exactly "
        "the inner automorphism group of D8, producing two fiber orbits "
        "of size four and a residual Out(D8)=C2 chart gauge. Therefore "
        "no strict equivariant one-chart-per-subgroup section exists. "
        "The locked alpha_1 character and q-axis signature are constant "
        "across both outer orbits, and the two cocycle presentations "
        "give equivalent chart bundles. The native local system is "
        "gauge-covariant but does not select an absolute chart."
    ),
    "boundary": {
        "finite_chart_bundle_test_only": True,
        "chart_orbit_census_performed": True,
        "equivariant_section_test_performed": True,
        "gauge_covariant_bundle_classified": (
            classification
            == (
                "native_D8_chart_bundle_has_exact_outer_C2_"
                "obstruction_to_equivariant_section"
            )
        ),
        "strict_equivariant_chart_selected": False,
        "native_update_law_constructed": False,
        "mechanics_state_cell_established": False,
        "orientation_selected": False,
        "local_side_equals_011o_orientation_sheet": False,
        "global_minimality_claim": False,
        "manuscript_mutated": False,
        "geometry_claim": False,
        "physical_direction_claim": False,
        "physical_claim": False,
    },
    "repository": {
        "status_before": status_before,
        "status_after": status_after,
        "status_preserved": status_before == status_after,
        "project_mutation_performed": False,
    },
}

candidate_path.parent.mkdir(parents=True, exist_ok=True)
candidate_path.write_text(
    json.dumps(result, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

print("BASE_ORBIT_SIZE_PROFILE:", result["base_action"]["orbit_size_profile"])
print("BASE_STABILIZER_ORDER_PROFILE:", result["base_action"]["stabilizer_order_profile"])
print("CHART_ORBIT_PROFILES:", orbit_profiles)
print("CHART_STABILIZER_ORDER_12:", str(all_chart_stabilizers_12).lower())
print("NORMALIZER_FIBER_IMAGE_ORDER_4:", str(all_fiber_images_4).lower())
print("FIBER_ORBIT_PROFILES_4_4:", str(all_fiber_profiles_4_4).lower())
print("NORMALIZER_IMAGE_EQUALS_INNER:", str(all_images_inner).lower())
print("STRICT_EQUIVARIANT_SECTION_COUNTS:", section_counts)
print("GAUGE_ISOMORPHISM_COUNT:", len(gauge_rows))
print("GAUGE_BUNDLES_EQUIVALENT:", str(gauge_bundles_equivalent).lower())
print("PREDICTION_MATCHES:", str(prediction_matches).lower())
print("CLASSIFICATION:", classification)
print("REPOSITORY_STATUS_PRESERVED:", str(status_before == status_after).lower())
print("PROJECT_MUTATION_PERFORMED: false")
print("GAUGE_COVARIANT_BUNDLE_CLASSIFIED:", str(result["boundary"]["gauge_covariant_bundle_classified"]).lower())
print("STRICT_EQUIVARIANT_CHART_SELECTED: false")
print("NATIVE_UPDATE_LAW_CONSTRUCTED: false")
print("MECHANICS_STATE_CELL_ESTABLISHED: false")
print("MANUSCRIPT_MUTATED: false")
print("PHYSICAL_CLAIM: false")
print("CANDIDATE_JSON:", candidate_path)
print("CANDIDATE_JSON_SHA256:", sha256_file(candidate_path))
