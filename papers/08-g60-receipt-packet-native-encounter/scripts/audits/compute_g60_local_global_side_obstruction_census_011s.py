#!/usr/bin/env python3
import hashlib
import itertools
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

project = Path(sys.argv[1]).resolve()
candidate_path = Path(sys.argv[2]).resolve()

p41 = Path("/data/data/com.termux/files/home/dev/cori/research/mathematics/41-order-4-dodecahedral-residue")
p42 = Path("/data/data/com.termux/files/home/dev/cori/research/mathematics/42-graph-automorphism-groups")

prereg_path = project / "artifacts/json/g60_local_global_side_obstruction_preregistration_011r.v1.json"
q_path = project / "artifacts/json/g60_two_sided_slider_cocycle_census_011q.v1.json"
o_path = project / "artifacts/json/g60_full_A_orientation_character_extension_census_011o.v1.json"
d8_path = p41 / "artifacts/json/s3_sign_v4_d8_local_system_audit_021.json"
v4_path = p42 / "artifacts/json/native_g60_v4_recovery_052.json"
action_path = p42 / "artifacts/json/native_g60_fiber_product_isomorphism_044.json"
split_path = p42 / "artifacts/json/native_g60_s5_extension_splitting_audit_079.json"

expected_hashes = {
    str(prereg_path): "66156d68d525a45fa6e7800e3b6093f911306352080725e08249f25ffe69c59d",
    str(q_path): "63034d0c0fe4a35480bf879209a1da5dae0d5a581eeef063e489d8be1be2459e",
    str(o_path): "ad684db8bb65c5eb731c972d33e685ffc18a947f63c9ba4e9758f815821f0941",
    str(d8_path): "e0b14cb81a3a28838b180e7bb0aacb17686b7d040171d3f90c59a713437008fa",
    str(v4_path): "8ddf9791ff0814ced4b72ea14a4c7f330f1b0de577579ec3755b0d411f83f9ca",
    str(action_path): "b37313b135495752b11e525bb61979163fdf54aec4be4f5d027dcee64c9efc21",
    str(split_path): "728071622f7a6a98042a8dd4d1a6fa01cdcc8a456bd2bd5b5aadcf22965f5221",
}

locked_head = "1aaaadf Preregister G60 local-global side obstruction test"
expected_classification = (
    "native_center_kernel_obstructs_direct_side_identification"
)

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

def compose(p, q):
    return tuple(p[q[i]] for i in range(len(p)))

def multiplication_table(permutations):
    lookup = {
        permutation: index
        for index, permutation in enumerate(permutations)
    }
    table = []
    failures = []
    for left_index, left in enumerate(permutations):
        row = []
        for right_index, right in enumerate(permutations):
            product = compose(left, right)
            product_index = lookup.get(product)
            if product_index is None:
                failures.append([left_index, right_index])
            row.append(product_index)
        table.append(row)
    return table, failures

def identity_index(table):
    size = len(table)
    for candidate in range(size):
        if all(
            table[candidate][x] == x
            and table[x][candidate] == x
            for x in range(size)
        ):
            return candidate
    return None

def element_order(table, identity, element):
    current = identity
    for order in range(1, len(table) + 1):
        current = table[current][element]
        if current == identity:
            return order
    return None

def group_profile(table):
    identity = identity_index(table)
    orders = [
        element_order(table, identity, element)
        for element in range(len(table))
    ]
    center = [
        element
        for element in range(len(table))
        if all(
            table[element][other] == table[other][element]
            for other in range(len(table))
        )
    ]
    order_profile = dict(sorted(Counter(orders).items()))
    if len(table) == 8 and order_profile == {1: 1, 2: 5, 4: 2}:
        group_type = "D8"
    elif len(table) == 8 and order_profile == {1: 1, 2: 1, 4: 6}:
        group_type = "Q8"
    else:
        group_type = "other"
    return {
        "group_type": group_type,
        "order": len(table),
        "identity_index": identity,
        "center_indices": center,
        "center_order": len(center),
        "element_order_profile": {
            str(key): value
            for key, value in order_profile.items()
        },
    }

def omega(bits, pair_positions, left, right):
    if left == 0 or right == 0:
        return 0
    return bits[pair_positions[(left, right)]]

def local_extension(bits, pair_positions):
    elements = [
        (visible, side)
        for visible in range(4)
        for side in (0, 1)
    ]
    lookup = {
        element: index
        for index, element in enumerate(elements)
    }
    table = []
    for left_visible, left_side in elements:
        row = []
        for right_visible, right_side in elements:
            product = (
                left_visible ^ right_visible,
                left_side
                ^ right_side
                ^ omega(
                    bits,
                    pair_positions,
                    left_visible,
                    right_visible,
                ),
            )
            row.append(lookup[product])
        table.append(row)
    return elements, table

def enumerate_isomorphisms(source_table, target_table):
    source_identity = identity_index(source_table)
    target_identity = identity_index(target_table)
    source_nonidentity = [
        index for index in range(8)
        if index != source_identity
    ]
    target_nonidentity = [
        index for index in range(8)
        if index != target_identity
    ]

    rows = []
    for target_images in itertools.permutations(target_nonidentity):
        mapping = [None] * 8
        mapping[source_identity] = target_identity
        for source, target in zip(source_nonidentity, target_images):
            mapping[source] = target

        valid = True
        for left in range(8):
            for right in range(8):
                if (
                    mapping[source_table[left][right]]
                    != target_table[mapping[left]][mapping[right]]
                ):
                    valid = False
                    break
            if not valid:
                break

        if valid:
            rows.append(mapping)
    return rows

head = git("show", "-s", "--format=%h %s", "HEAD")
status_before = git("status", "--short", "--", ".")

actual_hashes = {
    path: sha256_file(Path(path))
    for path in expected_hashes
}
hash_matches = {
    path: actual_hashes[path] == expected_hashes[path]
    for path in expected_hashes
}
all_hashes_match = all(hash_matches.values())

prereg = json.loads(prereg_path.read_text(encoding="utf-8"))
q_data = json.loads(q_path.read_text(encoding="utf-8"))
o_data = json.loads(o_path.read_text(encoding="utf-8"))
d8_data = json.loads(d8_path.read_text(encoding="utf-8"))
v4_data = json.loads(v4_path.read_text(encoding="utf-8"))
action_data = json.loads(action_path.read_text(encoding="utf-8"))
split_data = json.loads(split_path.read_text(encoding="utf-8"))

print("== G60 LOCAL/GLOBAL SIDE OBSTRUCTION CENSUS 011s ==")
print("MODE: temporary read-only complete marked-action census")
print("LOCKED_HEAD:", head)
print("ALL_AUTHORITY_HASHES_MATCH:", str(all_hashes_match).lower())

names = {"1": 0, "a": 1, "b": 2, "ab": 3}
pair_order = q_data["cochain_enumeration"]["normalized_pair_order"]
pair_positions = {
    (names[left], names[right]): index
    for index, (left, right) in enumerate(pair_order)
}

selected_cocycles = q_data["native_filter"]["selected_cocycle_rows"]
coboundary_bits = {
    tuple(row["bits"])
    for row in q_data["cochain_enumeration"]["coboundary_rows"]
}

print()
print("NATIVE_INDEX_IDENTIFICATION_BEGIN")

action_rows = action_data["mapping_rows"]
permutation_to_index = {
    tuple(row["actual_permutation"]): int(row["actual_index"])
    for row in action_rows
}

native_index_names = {
    name: permutation_to_index.get(tuple(permutation))
    for name, permutation in {
        "a": v4_data["involutions"]["a"],
        "b": v4_data["involutions"]["b"],
        "ab": v4_data["involutions"]["ab"],
    }.items()
}
native_index_names["1"] = 0

residual_rows = o_data["character_census"]["residual_character_rows"]
alpha_1_by_index = {
    int(row["element_index"]): int(row["alpha_1"])
    for row in residual_rows
}
alpha_1_restriction = {
    name: alpha_1_by_index[native_index_names[name]]
    for name in ("1", "a", "b", "ab")
}

print("NATIVE_V4_INDICES:", native_index_names)
print("ALPHA_1_RESTRICTION:", alpha_1_restriction)
print("NATIVE_INDEX_IDENTIFICATION_END")

print()
print("NATIVE_D8_RECONSTRUCTION_BEGIN")

native_permutations = [
    tuple(int(x) for x in permutation)
    for permutation in d8_data["measurements"]["local_square_group"]
]
native_table, native_closure_failures = multiplication_table(
    native_permutations
)
native_profile = group_profile(native_table)

identity_permutation = (0, 1, 2, 3)
native_translation_permutations = {
    "1": identity_permutation,
    "a": (3, 2, 1, 0),
    "b": (1, 0, 3, 2),
    "ab": (2, 3, 0, 1),
}
native_permutation_to_group_index = {
    permutation: index
    for index, permutation in enumerate(native_permutations)
}
native_named_group_indices = {
    name: native_permutation_to_group_index[permutation]
    for name, permutation in native_translation_permutations.items()
}
native_a_group_index = native_named_group_indices["a"]
native_nonidentity_center = [
    index
    for index in native_profile["center_indices"]
    if index != native_profile["identity_index"]
]

print("NATIVE_GROUP_PROFILE:", native_profile)
print("NATIVE_NAMED_GROUP_INDICES:", native_named_group_indices)
print("NATIVE_NONIDENTITY_CENTER:", native_nonidentity_center)
print("NATIVE_D8_RECONSTRUCTION_END")

print()
print("ISOMORPHISM_ENUMERATION_BEGIN")

representative_rows = []
all_isomorphism_rows = []
local_profiles = []
local_side_delta_profiles = []

for representative_index, cocycle_row in enumerate(selected_cocycles):
    bits = tuple(int(x) for x in cocycle_row["bits"])
    elements, local_table = local_extension(bits, pair_positions)
    local_profile = group_profile(local_table)
    local_profiles.append(local_profile)

    local_lookup = {
        element: index
        for index, element in enumerate(elements)
    }
    local_central_flip_index = local_lookup[(0, 1)]

    local_side_deltas = []
    for state_index, state in enumerate(elements):
        image_index = local_table[local_central_flip_index][state_index]
        image_state = elements[image_index]
        local_side_deltas.append(state[1] ^ image_state[1])

    local_side_delta_profile = dict(
        sorted(Counter(local_side_deltas).items())
    )
    local_side_delta_profiles.append(local_side_delta_profile)

    isomorphisms = enumerate_isomorphisms(
        local_table,
        native_table,
    )

    isomorphism_rows = []
    for isomorphism_index, mapping in enumerate(isomorphisms):
        center_image = mapping[local_central_flip_index]
        center_image_name = next(
            (
                name
                for name, group_index
                in native_named_group_indices.items()
                if group_index == center_image
            ),
            None,
        )
        local_delta = 1
        global_delta = alpha_1_restriction["a"]
        compatible = (
            center_image == native_a_group_index
            and local_delta == global_delta
        )
        row = {
            "representative_index": representative_index,
            "isomorphism_index": isomorphism_index,
            "mapping": mapping,
            "mapping_sha256": sha256_json(mapping),
            "local_central_flip_index": local_central_flip_index,
            "native_center_image_index": center_image,
            "native_center_image_name": center_image_name,
            "local_side_delta": local_delta,
            "011o_sheet_delta": global_delta,
            "direct_marked_side_compatible": compatible,
        }
        isomorphism_rows.append(row)
        all_isomorphism_rows.append(row)

    representative_rows.append({
        "representative_index": representative_index,
        "cocycle_sha256": cocycle_row["cocycle_sha256"],
        "bits": list(bits),
        "local_group_profile": local_profile,
        "local_central_flip_index": local_central_flip_index,
        "local_side_delta_profile": {
            str(key): value
            for key, value in local_side_delta_profile.items()
        },
        "isomorphism_count": len(isomorphisms),
        "all_isomorphisms_map_center_to_native_a": all(
            row["native_center_image_index"]
            == native_a_group_index
            for row in isomorphism_rows
        ),
        "direct_marked_side_identification_count": sum(
            row["direct_marked_side_compatible"]
            for row in isomorphism_rows
        ),
        "isomorphism_rows": isomorphism_rows,
    })

print("ISOMORPHISM_ENUMERATION_END")

selected_bits = [
    tuple(row["bits"])
    for row in selected_cocycles
]
representative_difference = tuple(
    left ^ right
    for left, right in zip(selected_bits[0], selected_bits[1])
)
representatives_gauge_related = (
    representative_difference in coboundary_bits
)

native_center_mapping_failure_count = sum(
    not row["all_isomorphisms_map_center_to_native_a"]
    for row in representative_rows
)
direct_identification_count = sum(
    row["direct_marked_side_identification_count"]
    for row in representative_rows
)
total_isomorphism_count = sum(
    row["isomorphism_count"]
    for row in representative_rows
)

local_delta_profile = dict(sorted(Counter(
    row["local_side_delta"]
    for row in all_isomorphism_rows
).items()))
global_delta_profile = dict(sorted(Counter(
    row["011o_sheet_delta"]
    for row in all_isomorphism_rows
).items()))

index_identification_ok = native_index_names == {
    "1": 0,
    "a": 326,
    "b": 124,
    "ab": 65,
}
alpha_restriction_ok = alpha_1_restriction == {
    "1": 0,
    "a": 0,
    "b": 1,
    "ab": 1,
}
local_groups_are_D8 = all(
    profile["group_type"] == "D8"
    for profile in local_profiles
)
native_group_is_D8 = native_profile["group_type"] == "D8"
isomorphism_counts_ok = (
    [row["isomorphism_count"] for row in representative_rows]
    == [8, 8]
    and total_isomorphism_count == 16
)
local_center_flips_side = all(
    profile == {1: 8}
    for profile in local_side_delta_profiles
)
native_center_preserves_011o_sheet = (
    alpha_1_restriction["a"] == 0
)

authority_failure = (
    not all_hashes_match
    or head != locked_head
    or prereg.get("status")
    != "frozen_before_marked_action_census"
)

if native_closure_failures:
    classification = "computation_failure"
elif authority_failure:
    classification = "authority_failure"
elif not index_identification_ok or not alpha_restriction_ok:
    classification = "native_V4_index_name_mismatch"
elif not local_groups_are_D8:
    classification = "selected_extension_not_D8"
elif not native_group_is_D8:
    classification = "native_local_group_not_D8"
elif not isomorphism_counts_ok:
    classification = "isomorphism_count_mismatch"
elif native_center_mapping_failure_count:
    classification = "center_mapping_failure"
elif not local_center_flips_side:
    classification = "local_center_does_not_flip_local_side"
elif not native_center_preserves_011o_sheet:
    classification = "native_center_unexpectedly_flips_011o_sheet"
elif direct_identification_count:
    classification = "unexpected_direct_marked_side_identification"
else:
    classification = expected_classification

prediction_matches = (
    classification == expected_classification
    and total_isomorphism_count == 16
    and direct_identification_count == 0
    and representatives_gauge_related
)

status_after = git("status", "--short", "--", ".")
repository_preserved = status_after == status_before

result = {
    "packet": "g60_local_global_side_obstruction_census_011s_candidate",
    "mode": "temporary_read_only_complete_marked_action_census",
    "locked_head": head,
    "authorities": {
        path: {
            "expected_sha256": expected_hashes[path],
            "sha256": actual_hashes[path],
            "hash_match": hash_matches[path],
        }
        for path in expected_hashes
    },
    "native_index_identification": {
        "native_V4_indices": native_index_names,
        "expected_native_V4_indices": {
            "1": 0,
            "a": 326,
            "b": 124,
            "ab": 65,
        },
        "index_identification_ok": index_identification_ok,
        "011o_alpha_1_restriction": alpha_1_restriction,
        "expected_011o_alpha_1_restriction": {
            "1": 0,
            "a": 0,
            "b": 1,
            "ab": 1,
        },
        "alpha_restriction_ok": alpha_restriction_ok,
    },
    "native_D8": {
        "group_profile": native_profile,
        "closure_failure_count": len(native_closure_failures),
        "named_group_indices": native_named_group_indices,
        "native_a_group_index": native_a_group_index,
        "nonidentity_center_indices": native_nonidentity_center,
        "native_center_is_a": (
            native_nonidentity_center == [native_a_group_index]
        ),
    },
    "selected_extensions": {
        "representative_count": len(representative_rows),
        "representative_rows": representative_rows,
        "representatives_gauge_related": representatives_gauge_related,
        "representative_difference": list(
            representative_difference
        ),
    },
    "marked_action_comparison": {
        "isomorphism_count_per_representative": [
            row["isomorphism_count"]
            for row in representative_rows
        ],
        "total_isomorphism_count": total_isomorphism_count,
        "center_mapping_failure_count": (
            native_center_mapping_failure_count
        ),
        "all_isomorphisms_map_local_center_to_native_a": (
            native_center_mapping_failure_count == 0
        ),
        "local_side_delta_profile": {
            str(key): value
            for key, value in local_delta_profile.items()
        },
        "011o_sheet_delta_profile": {
            str(key): value
            for key, value in global_delta_profile.items()
        },
        "local_center_flips_side": local_center_flips_side,
        "native_center_preserves_011o_sheet": (
            native_center_preserves_011o_sheet
        ),
        "direct_marked_side_identification_count": (
            direct_identification_count
        ),
        "direct_side_identification_obstructed": (
            direct_identification_count == 0
            and local_center_flips_side
            and native_center_preserves_011o_sheet
        ),
    },
    "classification": classification,
    "prediction_matches": prediction_matches,
    "earned_statement_candidate": (
        "Both gauge-related presentations of the selected 011q "
        "central extension reconstruct D8. Each admits exactly eight "
        "group isomorphisms to the native local D8, and every one of "
        "the sixteen isomorphisms maps the local central flip to the "
        "unique nonidentity native center a. The local central flip "
        "changes the 011q side coordinate, whereas native a lies in "
        "the kernel of the 011o alpha_1 sheet character. Therefore "
        "no direct marked identification of the two binary witnesses "
        "exists. This center-action obstruction does not rule out a "
        "relation mediated by an intermediate bridge."
    ),
    "boundary": {
        "bounded_marked_D8_comparison_complete": True,
        "direct_side_identification_obstructed": (
            direct_identification_count == 0
        ),
        "local_side_equals_011o_orientation_sheet": False,
        "intermediate_bridge_constructed": False,
        "broader_local_global_relation_ruled_out": False,
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
        "status_before": status_before.splitlines(),
        "status_after": status_after.splitlines(),
        "status_preserved": repository_preserved,
        "project_mutation_performed": False,
    },
}

candidate_path.parent.mkdir(parents=True, exist_ok=True)
candidate_path.write_text(
    json.dumps(result, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

print()
print("== FINAL LOCAL/GLOBAL SIDE OBSTRUCTION REPORT ==")
print("NATIVE_V4_INDICES:", native_index_names)
print("ALPHA_1_RESTRICTION:", alpha_1_restriction)
print("NATIVE_GROUP_PROFILE:", native_profile)
print("LOCAL_GROUP_TYPES:", [
    profile["group_type"]
    for profile in local_profiles
])
print("ISOMORPHISM_COUNTS:", [
    row["isomorphism_count"]
    for row in representative_rows
])
print("TOTAL_ISOMORPHISM_COUNT:", total_isomorphism_count)
print(
    "ALL_ISOMORPHISMS_MAP_LOCAL_CENTER_TO_NATIVE_A:",
    str(native_center_mapping_failure_count == 0).lower(),
)
print("LOCAL_SIDE_DELTA_PROFILE:", local_delta_profile)
print("011O_SHEET_DELTA_PROFILE:", global_delta_profile)
print(
    "DIRECT_MARKED_SIDE_IDENTIFICATION_COUNT:",
    direct_identification_count,
)
print(
    "REPRESENTATIVES_GAUGE_RELATED:",
    str(representatives_gauge_related).lower(),
)
print("PREDICTION_MATCHES:", str(prediction_matches).lower())
print("CLASSIFICATION:", classification)
print(
    "REPOSITORY_STATUS_PRESERVED:",
    str(repository_preserved).lower(),
)
print("PROJECT_MUTATION_PERFORMED: false")
print(
    "DIRECT_SIDE_IDENTIFICATION_OBSTRUCTED:",
    str(direct_identification_count == 0).lower(),
)
print("LOCAL_SIDE_EQUALS_011O_ORIENTATION_SHEET: false")
print("INTERMEDIATE_BRIDGE_CONSTRUCTED: false")
print("NATIVE_UPDATE_LAW_CONSTRUCTED: false")
print("MECHANICS_STATE_CELL_ESTABLISHED: false")
print("MANUSCRIPT_MUTATED: false")
print("PHYSICAL_CLAIM: false")
print("CANDIDATE_JSON:", candidate_path)
print("CANDIDATE_JSON_SHA256:", sha256_file(candidate_path))
