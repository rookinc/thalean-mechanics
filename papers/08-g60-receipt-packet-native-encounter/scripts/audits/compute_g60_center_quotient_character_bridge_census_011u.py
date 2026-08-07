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

prereg_path = project / "artifacts/json/g60_center_quotient_character_bridge_preregistration_011t.v1.json"
q_path = project / "artifacts/json/g60_two_sided_slider_cocycle_census_011q.v1.json"
o_path = project / "artifacts/json/g60_full_A_orientation_character_extension_census_011o.v1.json"
s_path = project / "artifacts/json/g60_local_global_side_obstruction_census_011s.v1.json"

native_d8_path = p41 / "artifacts/json/s3_sign_v4_d8_local_system_audit_021.json"
native_v4_path = p42 / "artifacts/json/native_g60_v4_recovery_052.json"
action_path = p42 / "artifacts/json/native_g60_fiber_product_isomorphism_044.json"
split_path = p42 / "artifacts/json/native_g60_s5_extension_splitting_audit_079.json"

locked_head = "9aafeab Preregister G60 center-quotient character bridge"

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

prereg = json.loads(prereg_path.read_text(encoding="utf-8"))
q_data = json.loads(q_path.read_text(encoding="utf-8"))
o_data = json.loads(o_path.read_text(encoding="utf-8"))
s_data = json.loads(s_path.read_text(encoding="utf-8"))
native_d8 = json.loads(native_d8_path.read_text(encoding="utf-8"))
native_v4 = json.loads(native_v4_path.read_text(encoding="utf-8"))
action = json.loads(action_path.read_text(encoding="utf-8"))
split = json.loads(split_path.read_text(encoding="utf-8"))

paths = [
    prereg_path,
    q_path,
    o_path,
    s_path,
    native_d8_path,
    native_v4_path,
    action_path,
    split_path,
]

expected_authorities = prereg["authorities"]
authorities = {}
for path in paths:
    key = str(path)
    actual = sha256_file(path)
    expected_row = expected_authorities.get(key, {})
    expected = expected_row.get("sha256", expected_row.get("expected_sha256"))
    if path == prereg_path:
        expected = sha256_file(prereg_path)
    authorities[key] = {
        "expected_sha256": expected,
        "sha256": actual,
        "hash_match": expected == actual,
    }

all_authority_hashes_match = all(
    row["hash_match"] for row in authorities.values()
)

status_before = status_rows()
head = git("show", "-s", "--format=%h %s", "HEAD")

mapping_rows = action["mapping_rows"]
permutations = {
    int(row["actual_index"]): tuple(int(x) for x in row["actual_permutation"])
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
identity_index = perm_to_index[identity_perm]

def compose_permutations(p, q):
    return tuple(p[q[v]] for v in range(degree))

@lru_cache(maxsize=None)
def multiply_global(left, right):
    product = compose_permutations(
        permutations[left],
        permutations[right],
    )
    return perm_to_index[product]

def global_element_order(element):
    current = identity_index
    for order in range(1, 65):
        current = multiply_global(current, element)
        if current == identity_index:
            return order
    return None

def permutation_parity(permutation):
    inversions = sum(
        permutation[i] > permutation[j]
        for i in range(len(permutation))
        for j in range(i + 1, len(permutation))
    )
    return inversions % 2

def is_transposition(permutation):
    moved = [
        i for i, image in enumerate(permutation)
        if image != i
    ]
    return (
        len(moved) == 2
        and permutation[moved[0]] == moved[1]
        and permutation[moved[1]] == moved[0]
    )

def alpha_1_value(index):
    return int(references[index]["d8_flip"]) & 1

native_index_by_name = {"1": identity_index}
for name in ("a", "b", "ab"):
    permutation = tuple(native_v4["involutions"][name])
    native_index_by_name[name] = perm_to_index[permutation]

expected_native_indices = {
    "1": 0,
    "a": 326,
    "b": 124,
    "ab": 65,
}
native_index_identification_ok = (
    native_index_by_name == expected_native_indices
)

native_v4_indices = frozenset(native_index_by_name.values())
native_name_by_index = {
    index: name
    for name, index in native_index_by_name.items()
}

alpha_1_restriction = {
    name: alpha_1_value(index)
    for name, index in native_index_by_name.items()
}
expected_character = {
    "1": 0,
    "a": 0,
    "b": 1,
    "ab": 1,
}

transposition_lifts = {}
for index in indices:
    s5_permutation = tuple(references[index]["s5_permutation"])
    if is_transposition(s5_permutation):
        transposition_lifts.setdefault(
            s5_permutation,
            [],
        ).append(index)

def subgroup_from_lift(lift):
    coset = {
        multiply_global(v4_element, lift)
        for v4_element in native_v4_indices
    }
    return frozenset(native_v4_indices | coset)

subgroup_by_key = {}
transposition_rows = []

for transposition in sorted(transposition_lifts):
    lifts = sorted(transposition_lifts[transposition])
    generated_subgroups = {
        subgroup_from_lift(lift)
        for lift in lifts
    }
    subgroup = next(iter(generated_subgroups))
    subgroup_key = tuple(sorted(subgroup))
    subgroup_by_key.setdefault(
        subgroup_key,
        {
            "transpositions": [],
            "lifts": set(),
        },
    )
    subgroup_by_key[subgroup_key]["transpositions"].append(
        list(transposition)
    )
    subgroup_by_key[subgroup_key]["lifts"].update(lifts)
    transposition_rows.append({
        "s5_transposition": list(transposition),
        "lift_count": len(lifts),
        "lift_indices": lifts,
        "generated_subgroup_count": len(generated_subgroups),
        "generated_subgroup_indices": list(subgroup_key),
    })

def subgroup_profile(elements):
    elements = tuple(sorted(elements))
    order_rows = {
        element: global_element_order(element)
        for element in elements
    }
    order_profile = dict(sorted(Counter(order_rows.values()).items()))
    center = [
        element for element in elements
        if all(
            multiply_global(element, other)
            == multiply_global(other, element)
            for other in elements
        )
    ]
    closure_failures = sum(
        multiply_global(left, right) not in elements
        for left in elements
        for right in elements
    )
    group_type = "unknown"
    if (
        len(elements) == 8
        and order_profile == {1: 1, 2: 5, 4: 2}
        and len(center) == 2
    ):
        group_type = "D8"
    return {
        "group_type": group_type,
        "order": len(elements),
        "identity_index": identity_index,
        "center_indices": center,
        "center_names": [
            native_name_by_index.get(index)
            for index in center
        ],
        "center_order": len(center),
        "element_order_profile": {
            str(key): value
            for key, value in order_profile.items()
        },
        "closure_failure_count": closure_failures,
        "element_orders": {
            str(index): order_rows[index]
            for index in elements
        },
    }

native_subgroup_rows = []
native_subgroups = []

for subgroup_index, subgroup_key in enumerate(sorted(subgroup_by_key)):
    source = subgroup_by_key[subgroup_key]
    profile = subgroup_profile(subgroup_key)
    row = {
        "subgroup_index": subgroup_index,
        "subgroup_indices": list(subgroup_key),
        "transposition_count": len(source["transpositions"]),
        "transpositions": sorted(source["transpositions"]),
        "lift_count": len(source["lifts"]),
        "lift_indices": sorted(source["lifts"]),
        "profile": profile,
        "native_center_is_a": (
            set(profile["center_indices"])
            == {
                identity_index,
                native_index_by_name["a"],
            }
        ),
    }
    native_subgroup_rows.append(row)
    native_subgroups.append(tuple(subgroup_key))

pair_order = [
    (1, 1),
    (1, 2),
    (1, 3),
    (2, 1),
    (2, 2),
    (2, 3),
    (3, 1),
    (3, 2),
    (3, 3),
]
pair_to_position = {
    pair: position
    for position, pair in enumerate(pair_order)
}

def omega(bits, left, right):
    if left == 0 or right == 0:
        return 0
    return int(bits[pair_to_position[(left, right)]])

def local_multiply(bits, left, right):
    left_visible, left_side = left
    right_visible, right_side = right
    return (
        left_visible ^ right_visible,
        left_side
        ^ right_side
        ^ omega(bits, left_visible, right_visible),
    )

local_elements = tuple(
    (visible, side)
    for visible in range(4)
    for side in range(2)
)
local_identity = (0, 0)
local_center = (0, 1)
visible_names = {
    0: "1",
    1: "a",
    2: "b",
    3: "ab",
}

def local_element_order(bits, element):
    current = local_identity
    for order in range(1, 17):
        current = local_multiply(bits, current, element)
        if current == local_identity:
            return order
    return None

def local_profile(bits):
    orders = {
        element: local_element_order(bits, element)
        for element in local_elements
    }
    order_profile = dict(sorted(Counter(orders.values()).items()))
    center = [
        element for element in local_elements
        if all(
            local_multiply(bits, element, other)
            == local_multiply(bits, other, element)
            for other in local_elements
        )
    ]
    associativity_failures = sum(
        local_multiply(
            bits,
            local_multiply(bits, x, y),
            z,
        )
        != local_multiply(
            bits,
            x,
            local_multiply(bits, y, z),
        )
        for x in local_elements
        for y in local_elements
        for z in local_elements
    )
    group_type = "unknown"
    if (
        order_profile == {1: 1, 2: 5, 4: 2}
        and len(center) == 2
    ):
        group_type = "D8"
    return {
        "group_type": group_type,
        "order": len(local_elements),
        "center": [list(element) for element in center],
        "center_order": len(center),
        "element_order_profile": {
            str(key): value
            for key, value in order_profile.items()
        },
        "associativity_failure_count": associativity_failures,
        "element_orders": orders,
    }

def enumerate_isomorphisms(bits, subgroup):
    local_orders = {
        element: local_element_order(bits, element)
        for element in local_elements
    }
    native_orders = {
        element: global_element_order(element)
        for element in subgroup
    }

    local_by_order = {}
    native_by_order = {}
    for element, order in local_orders.items():
        local_by_order.setdefault(order, []).append(element)
    for element, order in native_orders.items():
        native_by_order.setdefault(order, []).append(element)

    if {
        key: len(value)
        for key, value in local_by_order.items()
    } != {
        key: len(value)
        for key, value in native_by_order.items()
    }:
        return []

    local_order_two = sorted(
        local_by_order.get(2, []),
        key=lambda value: (value[0], value[1]),
    )
    local_order_four = sorted(
        local_by_order.get(4, []),
        key=lambda value: (value[0], value[1]),
    )
    native_order_two = sorted(native_by_order.get(2, []))
    native_order_four = sorted(native_by_order.get(4, []))

    isomorphisms = []
    for image_order_two in itertools.permutations(native_order_two):
        for image_order_four in itertools.permutations(native_order_four):
            mapping = {
                local_identity: identity_index,
            }
            mapping.update(zip(local_order_two, image_order_two))
            mapping.update(zip(local_order_four, image_order_four))

            valid = True
            for left in local_elements:
                for right in local_elements:
                    local_product = local_multiply(bits, left, right)
                    native_product = multiply_global(
                        mapping[left],
                        mapping[right],
                    )
                    if mapping[local_product] != native_product:
                        valid = False
                        break
                if not valid:
                    break

            if valid:
                isomorphisms.append(mapping)

    return isomorphisms

selected_cocycle_rows = sorted(
    q_data["native_filter"]["selected_cocycle_rows"],
    key=lambda row: row["cocycle_sha256"],
)

presentation_rows = []
comparison_rows = []
pair_rows = []

all_quotient_character_tuples = set()
all_center_images = set()
isomorphism_counts = []

for presentation_index, selected_row in enumerate(selected_cocycle_rows):
    bits = tuple(int(value) for value in selected_row["bits"])
    profile = local_profile(bits)
    square_signature = {
        visible_names[visible]: local_multiply(
            bits,
            (visible, 0),
            (visible, 0),
        )[1]
        for visible in (1, 2, 3)
    }

    presentation_rows.append({
        "presentation_index": presentation_index,
        "cocycle_sha256": selected_row["cocycle_sha256"],
        "bits": list(bits),
        "profile": {
            key: value
            for key, value in profile.items()
            if key != "element_orders"
        },
        "square_signature": square_signature,
        "local_center": list(local_center),
    })

    for subgroup_index, subgroup in enumerate(native_subgroups):
        isomorphisms = enumerate_isomorphisms(bits, subgroup)
        isomorphism_counts.append(len(isomorphisms))
        pair_comparison_start = len(comparison_rows)

        for isomorphism_index, mapping in enumerate(isomorphisms):
            pulled_values = {
                element: alpha_1_value(mapping[element])
                for element in local_elements
            }
            center_image = mapping[local_center]
            all_center_images.add(center_image)

            center_killed = pulled_values[local_center] == 0
            descent_failure_count = sum(
                pulled_values[(visible, 0)]
                != pulled_values[(visible, 1)]
                for visible in range(4)
            )
            descends = (
                center_killed
                and descent_failure_count == 0
            )

            quotient_tuple = tuple(
                pulled_values[(visible, 0)]
                for visible in range(4)
            )
            quotient_character = {
                visible_names[visible]: quotient_tuple[visible]
                for visible in range(4)
            }
            all_quotient_character_tuples.add(quotient_tuple)

            quotient_kernel = [
                visible_names[visible]
                for visible in range(4)
                if quotient_tuple[visible] == 0
            ]
            local_kernel = [
                element
                for element in local_elements
                if pulled_values[element] == 0
            ]
            kernel_order_profile = dict(sorted(Counter(
                local_element_order(bits, element)
                for element in local_kernel
            ).items()))
            kernel_group_type = "unknown"
            if kernel_order_profile == {1: 1, 2: 1, 4: 2}:
                kernel_group_type = "C4"

            homomorphism_failure_count = sum(
                pulled_values[
                    local_multiply(bits, left, right)
                ]
                != (
                    pulled_values[left]
                    ^ pulled_values[right]
                )
                for left in local_elements
                for right in local_elements
            )

            comparison_rows.append({
                "presentation_index": presentation_index,
                "cocycle_sha256": selected_row["cocycle_sha256"],
                "subgroup_index": subgroup_index,
                "isomorphism_index": isomorphism_index,
                "local_center_image_index": center_image,
                "local_center_image_name": native_name_by_index.get(
                    center_image
                ),
                "center_killed_by_alpha_1": center_killed,
                "descent_failure_count": descent_failure_count,
                "descends_to_visible_V4": descends,
                "quotient_character": quotient_character,
                "quotient_character_sha256": sha256_json(
                    quotient_character
                ),
                "quotient_kernel": quotient_kernel,
                "kernel_group_type": kernel_group_type,
                "kernel_element_order_profile": {
                    str(key): value
                    for key, value in kernel_order_profile.items()
                },
                "homomorphism_failure_count": (
                    homomorphism_failure_count
                ),
                "matches_expected_character": (
                    quotient_character == expected_character
                ),
                "kernel_is_q_distinguished_axis": (
                    quotient_kernel == ["1", "a"]
                ),
            })

        pair_rows.append({
            "presentation_index": presentation_index,
            "subgroup_index": subgroup_index,
            "isomorphism_count": len(isomorphisms),
            "comparison_count": (
                len(comparison_rows) - pair_comparison_start
            ),
        })

unique_quotient_characters = [
    {
        visible_names[visible]: values[visible]
        for visible in range(4)
    }
    for values in sorted(all_quotient_character_tuples)
]

all_native_subgroups_D8 = all(
    row["profile"]["group_type"] == "D8"
    and row["profile"]["closure_failure_count"] == 0
    and row["native_center_is_a"]
    for row in native_subgroup_rows
)
all_eight_isomorphisms = (
    len(isomorphism_counts) == 20
    and set(isomorphism_counts) == {8}
)
total_isomorphism_count = sum(isomorphism_counts)
all_centers_map_to_native_a = (
    all_center_images == {native_index_by_name["a"]}
)
all_centers_killed = all(
    row["center_killed_by_alpha_1"]
    for row in comparison_rows
)
all_descend = all(
    row["descends_to_visible_V4"]
    for row in comparison_rows
)
all_expected_character = all(
    row["matches_expected_character"]
    for row in comparison_rows
)
all_kernel_axis = all(
    row["kernel_is_q_distinguished_axis"]
    for row in comparison_rows
)
all_kernel_C4 = all(
    row["kernel_group_type"] == "C4"
    for row in comparison_rows
)
all_homomorphisms = all(
    row["homomorphism_failure_count"] == 0
    for row in comparison_rows
)
gauge_representatives_agree = (
    len(selected_cocycle_rows) == 2
    and len(unique_quotient_characters) == 1
)

prediction_matches = all([
    all_authority_hashes_match,
    head == locked_head,
    len(indices) == 480,
    len(transposition_lifts) == 10,
    sum(len(value) for value in transposition_lifts.values()) == 40,
    all(len(value) == 4 for value in transposition_lifts.values()),
    len(native_subgroups) == 10,
    all_native_subgroups_D8,
    len(selected_cocycle_rows) == 2,
    all_eight_isomorphisms,
    total_isomorphism_count == 160,
    len(comparison_rows) == 160,
    all_centers_map_to_native_a,
    all_centers_killed,
    all_descend,
    all_homomorphisms,
    unique_quotient_characters == [expected_character],
    all_expected_character,
    all_kernel_axis,
    all_kernel_C4,
    gauge_representatives_agree,
])

if not all_authority_hashes_match:
    classification = "authority_failure"
elif head != locked_head:
    classification = "locked_head_failure"
elif len(indices) != 480:
    classification = "full_group_reconstruction_failure"
elif len(transposition_lifts) != 10:
    classification = "transposition_count_mismatch"
elif len(native_subgroups) != 10 or not all_native_subgroups_D8:
    classification = "native_D8_subgroup_census_failure"
elif not all_eight_isomorphisms:
    classification = "marked_isomorphism_count_mismatch"
elif not all_centers_map_to_native_a:
    classification = "local_center_native_center_mismatch"
elif not all_centers_killed:
    classification = "native_center_not_in_alpha_1_kernel"
elif not all_descend:
    classification = "center_quotient_descent_failure"
elif unique_quotient_characters != [expected_character]:
    classification = "quotient_character_not_unique_or_mismatch"
elif not all_kernel_axis:
    classification = "quotient_kernel_axis_mismatch"
elif not all_kernel_C4:
    classification = "pulled_back_kernel_not_C4"
elif not gauge_representatives_agree:
    classification = "gauge_presentations_disagree"
elif prediction_matches:
    classification = "unique_center_quotient_character_bridge"
else:
    classification = "computation_failure"

status_after = status_rows()
repository_status_preserved = status_before == status_after

result = {
    "packet": "g60_center_quotient_character_bridge_census_011u_candidate",
    "mode": "temporary_read_only_complete_center_quotient_character_bridge_census",
    "locked_head": locked_head,
    "authorities": authorities,
    "group_reconstruction": {
        "group_order": len(indices),
        "identity_index": identity_index,
        "native_v4_indices": native_index_by_name,
        "native_index_identification_ok": (
            native_index_identification_ok
        ),
        "alpha_1_restriction": alpha_1_restriction,
        "expected_alpha_1_restriction": expected_character,
        "transposition_count": len(transposition_lifts),
        "transposition_lift_count": sum(
            len(value)
            for value in transposition_lifts.values()
        ),
    },
    "native_D8_subgroup_census": {
        "subgroup_count": len(native_subgroups),
        "transposition_rows": transposition_rows,
        "subgroup_rows": native_subgroup_rows,
        "all_subgroups_D8": all_native_subgroups_D8,
        "all_subgroups_centered_on_native_a": all(
            row["native_center_is_a"]
            for row in native_subgroup_rows
        ),
    },
    "local_presentations": {
        "presentation_count": len(presentation_rows),
        "presentation_rows": presentation_rows,
        "representatives_gauge_related": q_data[
            "native_filter"
        ]["selected_representatives_gauge_related"],
    },
    "marked_comparison_census": {
        "presentation_subgroup_pair_count": len(pair_rows),
        "pair_rows": pair_rows,
        "isomorphism_counts": isomorphism_counts,
        "total_isomorphism_count": total_isomorphism_count,
        "comparison_count": len(comparison_rows),
        "comparison_rows": comparison_rows,
        "all_eight_isomorphisms_per_pair": (
            all_eight_isomorphisms
        ),
        "all_centers_map_to_native_a": (
            all_centers_map_to_native_a
        ),
        "all_centers_killed_by_alpha_1": all_centers_killed,
        "all_pulled_characters_are_homomorphisms": (
            all_homomorphisms
        ),
    },
    "center_quotient_character_bridge": {
        "all_characters_descend": all_descend,
        "unique_quotient_character_count": len(
            unique_quotient_characters
        ),
        "unique_quotient_characters": (
            unique_quotient_characters
        ),
        "expected_unique_character": expected_character,
        "all_match_expected_character": all_expected_character,
        "quotient_kernel": ["1", "a"],
        "all_kernels_equal_q_distinguished_axis": (
            all_kernel_axis
        ),
        "pulled_back_kernel_group_type": "C4",
        "all_pulled_back_kernels_are_C4": all_kernel_C4,
        "gauge_representatives_agree": (
            gauge_representatives_agree
        ),
        "quotient_forgets_local_central_side": True,
        "direct_side_obstruction_reversed": False,
    },
    "prediction_comparison": {
        "prediction_matches": prediction_matches,
        "native_D8_subgroup_count_matches": (
            len(native_subgroups) == 10
        ),
        "total_comparison_count_matches": (
            len(comparison_rows) == 160
        ),
        "unique_character_matches": (
            unique_quotient_characters == [expected_character]
        ),
        "kernel_matches": all_kernel_axis,
        "gauge_agreement_matches": gauge_representatives_agree,
    },
    "classification": classification,
    "earned_statement_candidate": (
        "The ten native transposition-local subgroups are D8 groups "
        "sharing the native V4 translation subgroup and the unique "
        "nonidentity center a. Across both gauge-related presentations "
        "of the selected 011q extension, each presentation-subgroup pair "
        "admits exactly eight group isomorphisms, giving 160 marked "
        "comparisons. Every pulled-back 011o alpha_1 character kills "
        "the local central flip and therefore descends through the "
        "center quotient to the same visible V4 character: "
        "lambda(1)=lambda(a)=0 and lambda(b)=lambda(ab)=1. Its quotient "
        "kernel is exactly the q-distinguished axis {1,a}, while its "
        "full preimage is C4. Thus a unique center-quotient character "
        "bridge exists. It relates the local D8 history lift to the "
        "011o orientation character only after forgetting the local "
        "central side, and does not identify the two side coordinates."
    ),
    "boundary": {
        "bounded_center_quotient_comparison": True,
        "center_quotient_character_bridge_constructed": (
            classification
            == "unique_center_quotient_character_bridge"
        ),
        "direct_side_identification_obstruction_preserved": True,
        "local_side_equals_011o_orientation_sheet": False,
        "native_update_law_constructed": False,
        "mechanics_state_cell_established": False,
        "orientation_selected": False,
        "global_minimality_claim": False,
        "manuscript_mutated": False,
        "geometry_claim": False,
        "physical_direction_claim": False,
        "physical_claim": False,
    },
    "repository": {
        "status_before": status_before,
        "status_after": status_after,
        "status_preserved": repository_status_preserved,
        "project_mutation_performed": False,
    },
}

candidate_path.parent.mkdir(parents=True, exist_ok=True)
candidate_path.write_text(
    json.dumps(result, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

print("== G60 CENTER-QUOTIENT CHARACTER BRIDGE CENSUS 011u ==")
print("MODE: temporary read-only complete center-quotient character bridge census")
print("LOCKED_HEAD:", head)
print("ALL_AUTHORITY_HASHES_MATCH:", str(all_authority_hashes_match).lower())
print()
print("NATIVE_RECONSTRUCTION_BEGIN")
print("FULL_GROUP_ORDER:", len(indices))
print("NATIVE_V4_INDICES:", native_index_by_name)
print("ALPHA_1_RESTRICTION:", alpha_1_restriction)
print("FIVE_POINT_TRANSPOSITION_COUNT:", len(transposition_lifts))
print(
    "TRANSPOSITION_LIFT_COUNT:",
    sum(len(value) for value in transposition_lifts.values()),
)
print("NATIVE_D8_SUBGROUP_COUNT:", len(native_subgroups))
print("NATIVE_RECONSTRUCTION_END")
print()
print("MARKED_COMPARISON_CENSUS_BEGIN")
print("LOCAL_PRESENTATION_COUNT:", len(presentation_rows))
print("PRESENTATION_SUBGROUP_PAIR_COUNT:", len(pair_rows))
print("ISOMORPHISM_COUNTS:", isomorphism_counts)
print("TOTAL_ISOMORPHISM_COUNT:", total_isomorphism_count)
print("TOTAL_COMPARISON_COUNT:", len(comparison_rows))
print(
    "ALL_CENTERS_MAP_TO_NATIVE_A:",
    str(all_centers_map_to_native_a).lower(),
)
print(
    "ALL_CENTERS_KILLED_BY_ALPHA_1:",
    str(all_centers_killed).lower(),
)
print("ALL_CHARACTERS_DESCEND:", str(all_descend).lower())
print("UNIQUE_QUOTIENT_CHARACTERS:", unique_quotient_characters)
print(
    "ALL_KERNELS_EQUAL_Q_DISTINGUISHED_AXIS:",
    str(all_kernel_axis).lower(),
)
print(
    "ALL_PULLED_BACK_KERNELS_ARE_C4:",
    str(all_kernel_C4).lower(),
)
print(
    "GAUGE_REPRESENTATIVES_AGREE:",
    str(gauge_representatives_agree).lower(),
)
print("MARKED_COMPARISON_CENSUS_END")
print()
print("PREDICTION_MATCHES:", str(prediction_matches).lower())
print("CLASSIFICATION:", classification)
print(
    "REPOSITORY_STATUS_PRESERVED:",
    str(repository_status_preserved).lower(),
)
print("PROJECT_MUTATION_PERFORMED: false")
print(
    "CENTER_QUOTIENT_CHARACTER_BRIDGE_CONSTRUCTED:",
    str(
        classification
        == "unique_center_quotient_character_bridge"
    ).lower(),
)
print("LOCAL_SIDE_EQUALS_011O_ORIENTATION_SHEET: false")
print("NATIVE_UPDATE_LAW_CONSTRUCTED: false")
print("MECHANICS_STATE_CELL_ESTABLISHED: false")
print("MANUSCRIPT_MUTATED: false")
print("PHYSICAL_CLAIM: false")
print("CANDIDATE_JSON:", candidate_path)
print("CANDIDATE_JSON_SHA256:", sha256_file(candidate_path))
