import hashlib
import itertools
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

project = Path(sys.argv[1]).resolve()
candidate_path = Path(sys.argv[2]).resolve()

p41 = Path(
    "/data/data/com.termux/files/home/dev/cori/research/mathematics/"
    "41-order-4-dodecahedral-residue"
)
p42 = Path(
    "/data/data/com.termux/files/home/dev/cori/research/mathematics/"
    "42-graph-automorphism-groups"
)

authority_paths = {
    str(
        p41 / "artifacts/json/"
        "synthematic_total_534_transport_tower_audit_020.json"
    ): "bd45e9224afaa22ae39855fb87ed391221340a6bb5b9375edcc012d2610449e4",
    str(
        p41 / "artifacts/json/"
        "s3_sign_v4_d8_local_system_audit_021.json"
    ): "e0b14cb81a3a28838b180e7bb0aacb17686b7d040171d3f90c59a713437008fa",
    str(
        p42 / "artifacts/json/native_g60_v4_recovery_052.json"
    ): "8ddf9791ff0814ced4b72ea14a4c7f330f1b0de577579ec3755b0d411f83f9ca",
    str(
        p42 / "artifacts/json/"
        "native_g60_s5_extension_splitting_audit_079.json"
    ): "728071622f7a6a98042a8dd4d1a6fa01cdcc8a456bd2bd5b5aadcf22965f5221",
    str(
        project / "artifacts/json/"
        "g60_full_A_orientation_character_extension_census_011o.v1.json"
    ): "ad684db8bb65c5eb731c972d33e685ffc18a947f63c9ba4e9758f815821f0941",
    str(
        project / "artifacts/json/"
        "g60_two_sided_slider_cocycle_preregistration_011p.v1.json"
    ): "5c09a3f307b05bf25c8ed11606ee3c58a93da16a973699b3905fa03c1b51b7bf",
}

locked_head = "449c222 Preregister G60 two-sided slider cocycle test"

names = {0: "1", 1: "a", 2: "b", 3: "ab"}
pairs = tuple((x, y) for x in range(1, 4) for y in range(1, 4))
identity = (0, 0)
central_flip = (0, 1)

expected_type_profile = {
    "C2_x_C2_x_C2": 1,
    "C4_x_C2": 3,
    "D8": 3,
    "Q8": 1,
}
expected_order_profiles = {
    "C2_x_C2_x_C2": {"1": 1, "2": 7},
    "C4_x_C2": {"1": 1, "2": 3, "4": 4},
    "D8": {"1": 1, "2": 5, "4": 2},
    "Q8": {"1": 1, "2": 1, "4": 6},
}
expected_native_signature = {"a": 1, "b": 0, "ab": 0}

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

def omega(bits, x, y):
    if x == 0 or y == 0:
        return 0
    return bits[pairs.index((x, y))]

def xor_bits(left, right):
    return tuple(a ^ b for a, b in zip(left, right))

def is_cocycle(bits):
    for x in range(4):
        for y in range(4):
            for z in range(4):
                left = omega(bits, x, y) ^ omega(bits, x ^ y, z)
                right = omega(bits, y, z) ^ omega(bits, x, y ^ z)
                if left != right:
                    return False
    return True

def coboundary(one_bits):
    def f(x):
        return 0 if x == 0 else one_bits[x - 1]

    return tuple(
        f(x) ^ f(y) ^ f(x ^ y)
        for x, y in pairs
    )

def multiply(bits, left, right):
    x, e = left
    y, f = right
    return (
        x ^ y,
        e ^ f ^ omega(bits, x, y),
    )

def element_order(bits, element):
    current = identity
    for order in range(1, 17):
        current = multiply(bits, current, element)
        if current == identity:
            return order
    return None

def extension_profile(bits):
    elements = tuple(
        (x, e)
        for x in range(4)
        for e in range(2)
    )

    associativity_failures = []
    for x in elements:
        for y in elements:
            for z in elements:
                left = multiply(bits, multiply(bits, x, y), z)
                right = multiply(bits, x, multiply(bits, y, z))
                if left != right:
                    associativity_failures.append([x, y, z])

    identity_failures = [
        element
        for element in elements
        if multiply(bits, identity, element) != element
        or multiply(bits, element, identity) != element
    ]

    inverse_failures = []
    for element in elements:
        candidates = [
            candidate
            for candidate in elements
            if multiply(bits, element, candidate) == identity
            and multiply(bits, candidate, element) == identity
        ]
        if len(candidates) != 1:
            inverse_failures.append([element, candidates])

    orders = [element_order(bits, element) for element in elements]
    order_profile = {
        str(order): count
        for order, count in sorted(Counter(orders).items())
    }

    center = [
        element
        for element in elements
        if all(
            multiply(bits, element, other)
            == multiply(bits, other, element)
            for other in elements
        )
    ]

    group_type = None
    for candidate_type, candidate_profile in expected_order_profiles.items():
        if order_profile == candidate_profile:
            group_type = candidate_type
            break

    square_signature = {
        names[x]: omega(bits, x, x)
        for x in (1, 2, 3)
    }

    A = (1, 0)
    B = (2, 0)
    AB = multiply(bits, A, B)
    BA = multiply(bits, B, A)

    return {
        "associativity_failure_count": len(associativity_failures),
        "identity_failure_count": len(identity_failures),
        "inverse_failure_count": len(inverse_failures),
        "order_profile": order_profile,
        "center": [list(element) for element in center],
        "center_order": len(center),
        "central_flip_in_center": central_flip in center,
        "group_type": group_type,
        "square_signature": square_signature,
        "A": list(A),
        "B": list(B),
        "AB": list(AB),
        "BA": list(BA),
        "same_visible_endpoint": AB[0] == BA[0] == 3,
        "side_discrepancy": AB[1] ^ BA[1],
        "opposite_central_sides": (
            AB[0] == BA[0]
            and (AB[1] ^ BA[1]) == 1
        ),
    }

print("== G60 TWO-SIDED SLIDER COCYCLE CENSUS 011q ==")
print("MODE: temporary read-only complete normalized cocycle census")

head = git("show", "-s", "--format=%h %s", "HEAD")
status_before = git("status", "--short", "--", ".")

actual_hashes = {
    path: sha256_file(Path(path))
    for path in authority_paths
}
hash_matches = {
    path: actual_hashes[path] == expected
    for path, expected in authority_paths.items()
}
all_authority_hashes_match = all(hash_matches.values())

print("LOCKED_HEAD:", head)
print("ALL_AUTHORITY_HASHES_MATCH:", str(all_authority_hashes_match).lower())

prereg_path = project / (
    "artifacts/json/"
    "g60_two_sided_slider_cocycle_preregistration_011p.v1.json"
)
prereg = json.loads(prereg_path.read_text(encoding="utf-8"))

native_021_path = p41 / (
    "artifacts/json/s3_sign_v4_d8_local_system_audit_021.json"
)
native_021 = json.loads(native_021_path.read_text(encoding="utf-8"))

native_052_path = p42 / "artifacts/json/native_g60_v4_recovery_052.json"
native_052 = json.loads(native_052_path.read_text(encoding="utf-8"))

print()
print("COCHAIN_ENUMERATION_BEGIN")

normalized_functions = []
cocycles = []

for mask in range(512):
    if mask % 64 == 0:
        print("COCHAIN_PROGRESS:", mask, "/ 512")

    bits = tuple((mask >> index) & 1 for index in range(9))
    normalized_functions.append(bits)

    if is_cocycle(bits):
        cocycles.append(bits)

print("COCHAIN_PROGRESS: 512 / 512")
print("COCHAIN_ENUMERATION_END")

print()
print("COBOUNDARY_ENUMERATION_BEGIN")

one_cochains = [
    tuple((mask >> index) & 1 for index in range(3))
    for mask in range(8)
]
coboundaries = sorted({
    coboundary(bits)
    for bits in one_cochains
})

print("NORMALIZED_ONE_COCHAIN_COUNT:", len(one_cochains))
print("DISTINCT_NORMALIZED_COBOUNDARY_COUNT:", len(coboundaries))
print("COBOUNDARY_ENUMERATION_END")

print()
print("COHOMOLOGY_CLASSIFICATION_BEGIN")

class_members = {}
for cocycle in cocycles:
    orbit = tuple(sorted(
        xor_bits(cocycle, boundary)
        for boundary in coboundaries
    ))
    class_key = orbit[0]
    class_members.setdefault(class_key, set()).add(cocycle)

sorted_class_keys = sorted(class_members)

cocycle_rows = []
class_rows = []
cocycle_to_class = {}

for class_index, class_key in enumerate(sorted_class_keys):
    members = sorted(class_members[class_key])
    profiles = [extension_profile(member) for member in members]

    for member, profile in zip(members, profiles):
        cocycle_to_class[member] = class_index
        cocycle_rows.append({
            "cocycle_sha256": sha256_json(list(member)),
            "bits": list(member),
            "class_index": class_index,
            "group_type": profile["group_type"],
            "order_profile": profile["order_profile"],
            "center_order": profile["center_order"],
            "square_signature": profile["square_signature"],
            "AB": profile["AB"],
            "BA": profile["BA"],
            "same_visible_endpoint": profile["same_visible_endpoint"],
            "side_discrepancy": profile["side_discrepancy"],
            "opposite_central_sides": profile["opposite_central_sides"],
        })

    profile_keys = {
        json.dumps({
            "group_type": profile["group_type"],
            "order_profile": profile["order_profile"],
            "center_order": profile["center_order"],
            "central_flip_in_center": profile["central_flip_in_center"],
            "square_signature": profile["square_signature"],
            "same_visible_endpoint": profile["same_visible_endpoint"],
            "side_discrepancy": profile["side_discrepancy"],
            "opposite_central_sides": profile["opposite_central_sides"],
            "associativity_failure_count": profile["associativity_failure_count"],
            "identity_failure_count": profile["identity_failure_count"],
            "inverse_failure_count": profile["inverse_failure_count"],
        }, sort_keys=True)
        for profile in profiles
    }

    representative = members[0]
    representative_profile = profiles[0]

    class_rows.append({
        "class_index": class_index,
        "class_sha256": sha256_json([list(member) for member in members]),
        "representative_count": len(members),
        "representative_sha256s": [
            sha256_json(list(member))
            for member in members
        ],
        "profile_uniform": len(profile_keys) == 1,
        "group_type": representative_profile["group_type"],
        "order_profile": representative_profile["order_profile"],
        "center_order": representative_profile["center_order"],
        "central_flip_in_center": representative_profile[
            "central_flip_in_center"
        ],
        "square_signature": representative_profile["square_signature"],
        "same_visible_endpoint": representative_profile[
            "same_visible_endpoint"
        ],
        "side_discrepancy": representative_profile["side_discrepancy"],
        "opposite_central_sides": representative_profile[
            "opposite_central_sides"
        ],
        "associativity_failure_count": sum(
            profile["associativity_failure_count"]
            for profile in profiles
        ),
        "identity_failure_count": sum(
            profile["identity_failure_count"]
            for profile in profiles
        ),
        "inverse_failure_count": sum(
            profile["inverse_failure_count"]
            for profile in profiles
        ),
    })

print("COHOMOLOGY_CLASSIFICATION_END")

type_profile = {
    group_type: count
    for group_type, count in sorted(Counter(
        row["group_type"]
        for row in class_rows
    ).items())
}

route_separating_cocycle_rows = [
    row for row in cocycle_rows
    if row["opposite_central_sides"]
]
route_separating_class_rows = [
    row for row in class_rows
    if row["opposite_central_sides"]
]

native_selected_class_rows = [
    row
    for row in class_rows
    if row["group_type"] == "D8"
    and row["order_profile"] == {"1": 1, "2": 5, "4": 2}
    and row["center_order"] == 2
    and row["square_signature"] == expected_native_signature
]

native_selected_indices = [
    row["class_index"]
    for row in native_selected_class_rows
]

native_selected_cocycle_rows = [
    row
    for row in cocycle_rows
    if row["class_index"] in native_selected_indices
]

all_extension_operations_valid = all(
    row["associativity_failure_count"] == 0
    and row["identity_failure_count"] == 0
    and row["inverse_failure_count"] == 0
    for row in class_rows
)

all_classes_have_two_representatives = all(
    row["representative_count"] == 2
    for row in class_rows
)

all_route_separating_classes_nonabelian = all(
    row["group_type"] in {"D8", "Q8"}
    for row in route_separating_class_rows
)

selected_separates_AB_BA = (
    len(native_selected_class_rows) == 1
    and native_selected_class_rows[0]["same_visible_endpoint"] is True
    and native_selected_class_rows[0]["opposite_central_sides"] is True
)

selected_representatives_gauge_related = (
    len(native_selected_cocycle_rows) == 2
    and xor_bits(
        tuple(native_selected_cocycle_rows[0]["bits"]),
        tuple(native_selected_cocycle_rows[1]["bits"]),
    ) in coboundaries
)

native_measurements = native_021["measurements"]
native_order_profile = {
    str(key): value
    for key, value in native_measurements[
        "local_square_group_element_order_profile"
    ].items()
}

native_abstract_D8_match = (
    native_021.get("audit_pass") is True
    and native_021["boundary"].get("local_structure_group_d8_derived") is True
    and native_measurements.get("local_square_group_order") == 8
    and native_measurements.get("local_square_group_center_order") == 2
    and native_order_profile == {"1": 1, "2": 5, "4": 2}
    and len(native_selected_class_rows) == 1
    and native_selected_class_rows[0]["group_type"] == "D8"
)

native_visible_V4_match = (
    native_052.get("audit_pass") is True
    and native_052["checks"].get("a_and_b_commute") is True
    and native_052["checks"].get("multiplication_closes") is True
    and native_052["boundary"].get(
        "four_state_character_register_verified"
    ) is True
)

counts_match_prediction = (
    len(normalized_functions) == 512
    and len(cocycles) == 16
    and len(coboundaries) == 2
    and len(class_rows) == 8
    and all_classes_have_two_representatives
)

type_profile_matches_prediction = type_profile == expected_type_profile

route_counts_match_prediction = (
    len(route_separating_cocycle_rows) == 8
    and len(route_separating_class_rows) == 4
    and all_route_separating_classes_nonabelian
)

native_selection_matches_prediction = (
    len(native_selected_class_rows) == 1
    and len(native_selected_cocycle_rows) == 2
    and native_selected_class_rows[0]["group_type"] == "D8"
    and selected_separates_AB_BA
    and selected_representatives_gauge_related
    and native_abstract_D8_match
)

operation_ok = (
    all_extension_operations_valid
    and all(
        row["profile_uniform"] is True
        for row in class_rows
    )
)

authority_failure = (
    not all_authority_hashes_match
    or head != locked_head
    or prereg.get("status") != "frozen_before_cocycle_enumeration"
    or prereg.get("locked_head")
    != "656c767 Lock G60 full-A orientation character bridge"
    or native_021.get("audit_pass") is not True
    or native_052.get("audit_pass") is not True
)

if not operation_ok:
    classification = "computation_failure"
elif authority_failure:
    classification = "authority_failure"
elif len(cocycles) != 16:
    classification = "normalized_cocycle_count_mismatch"
elif len(class_rows) != 8:
    classification = "cohomology_class_count_mismatch"
elif not type_profile_matches_prediction:
    classification = "extension_type_profile_mismatch"
elif len(route_separating_class_rows) == 0:
    classification = "no_route_separating_central_extension"
elif len(native_selected_class_rows) == 0:
    classification = "native_D8_profile_selects_no_class"
elif len(native_selected_class_rows) > 1:
    classification = "native_D8_profile_selects_multiple_classes"
elif not selected_separates_AB_BA:
    classification = "unique_native_axis_class_does_not_separate_AB_BA"
else:
    classification = (
        "unique_native_axis_D8_class_separates_AB_BA_"
        "without_orientation_sheet_identification"
    )

prediction_matches = (
    counts_match_prediction
    and type_profile_matches_prediction
    and route_counts_match_prediction
    and native_selection_matches_prediction
    and classification
    == (
        "unique_native_axis_D8_class_separates_AB_BA_"
        "without_orientation_sheet_identification"
    )
)

status_after = git("status", "--short", "--", ".")
repository_status_preserved = status_after == status_before

result = {
    "packet": "g60_two_sided_slider_cocycle_census_011q_candidate",
    "mode": "temporary_read_only_complete_normalized_cocycle_census",
    "locked_head": head,
    "authorities": {
        path: {
            "expected_sha256": authority_paths[path],
            "sha256": actual_hashes[path],
            "hash_match": hash_matches[path],
        }
        for path in authority_paths
    },
    "base_register": {
        "group": "V4",
        "labels": names,
        "operation": "bitwise_xor",
        "visible_state_count": 4,
        "native_visible_V4_match": native_visible_V4_match,
    },
    "cochain_enumeration": {
        "normalized_function_count": len(normalized_functions),
        "normalized_pair_order": [
            [names[x], names[y]]
            for x, y in pairs
        ],
        "normalized_cocycle_count": len(cocycles),
        "normalized_one_cochain_count": len(one_cochains),
        "distinct_normalized_coboundary_count": len(coboundaries),
        "coboundary_rows": [
            {
                "bits": list(boundary),
                "sha256": sha256_json(list(boundary)),
            }
            for boundary in coboundaries
        ],
        "cocycle_rows": sorted(
            cocycle_rows,
            key=lambda row: row["cocycle_sha256"],
        ),
    },
    "cohomology": {
        "class_count": len(class_rows),
        "all_classes_have_two_representatives": (
            all_classes_have_two_representatives
        ),
        "extension_type_class_profile": type_profile,
        "all_extension_operations_valid": (
            all_extension_operations_valid
        ),
        "class_rows": class_rows,
    },
    "route_test": {
        "route_pair": ["A_then_B", "B_then_A"],
        "visible_endpoint": "ab",
        "route_separating_cocycle_count": len(
            route_separating_cocycle_rows
        ),
        "route_separating_class_count": len(
            route_separating_class_rows
        ),
        "route_separating_class_indices": [
            row["class_index"]
            for row in route_separating_class_rows
        ],
        "route_separating_type_profile": dict(sorted(Counter(
            row["group_type"]
            for row in route_separating_class_rows
        ).items())),
        "all_route_separating_classes_nonabelian": (
            all_route_separating_classes_nonabelian
        ),
    },
    "native_filter": {
        "native_authority_group_type": "D8",
        "native_authority_order_profile": native_order_profile,
        "native_authority_center_order": native_measurements.get(
            "local_square_group_center_order"
        ),
        "declared_axis_square_signature": (
            expected_native_signature
        ),
        "selected_class_count": len(native_selected_class_rows),
        "selected_class_rows": native_selected_class_rows,
        "selected_cocycle_count": len(
            native_selected_cocycle_rows
        ),
        "selected_cocycle_rows": native_selected_cocycle_rows,
        "selected_representatives_gauge_related": (
            selected_representatives_gauge_related
        ),
        "native_abstract_D8_match": native_abstract_D8_match,
        "selected_class_separates_AB_BA": (
            selected_separates_AB_BA
        ),
    },
    "prediction_comparison": {
        "counts_match": counts_match_prediction,
        "extension_type_profile_matches": (
            type_profile_matches_prediction
        ),
        "route_counts_match": route_counts_match_prediction,
        "native_selection_matches": (
            native_selection_matches_prediction
        ),
        "prediction_matches": prediction_matches,
    },
    "classification": classification,
    "earned_statement_candidate": (
        "The complete normalized C2-valued cocycle census on the "
        "native visible V4 register has eight cohomology classes with "
        "extension-type profile C2^3, 3 C4xC2, 3 D8, and Q8. Four "
        "nonabelian classes distinguish A-then-B from B-then-A by a "
        "central side bit while preserving the visible endpoint ab. "
        "The native D8 order profile together with q(a)=1, q(b)=0, "
        "q(ab)=0 selects exactly one D8 class, represented by two "
        "gauge-related normalized cocycles. This proves a bounded "
        "two-sided local history lift but does not identify its central "
        "side with the 011o orientation sheet."
    ),
    "boundary": {
        "finite_central_extension_theorem_candidate": True,
        "two_sided_slider_cocycle_constructed": True,
        "native_axis_class_selected": (
            len(native_selected_class_rows) == 1
        ),
        "AB_BA_distinguished_in_selected_class": (
            selected_separates_AB_BA
        ),
        "unique_cocycle_representative_selected": False,
        "local_side_equals_011o_orientation_sheet": False,
        "local_to_global_side_map_constructed": False,
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
        "status_preserved": repository_status_preserved,
        "project_mutation_performed": False,
    },
}

candidate_path.parent.mkdir(parents=True, exist_ok=True)
candidate_path.write_text(
    json.dumps(result, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

print()
print("== FINAL TWO-SIDED SLIDER COCYCLE REPORT ==")
print("NORMALIZED_FUNCTION_COUNT:", len(normalized_functions))
print("NORMALIZED_COCYCLE_COUNT:", len(cocycles))
print("DISTINCT_NORMALIZED_COBOUNDARY_COUNT:", len(coboundaries))
print("COHOMOLOGY_CLASS_COUNT:", len(class_rows))
print("EXTENSION_TYPE_CLASS_PROFILE:", type_profile)
print("ROUTE_SEPARATING_COCYCLE_COUNT:", len(route_separating_cocycle_rows))
print("ROUTE_SEPARATING_CLASS_COUNT:", len(route_separating_class_rows))
print(
    "ROUTE_SEPARATING_TYPE_PROFILE:",
    result["route_test"]["route_separating_type_profile"],
)
print("NATIVE_SELECTED_CLASS_COUNT:", len(native_selected_class_rows))
print("NATIVE_SELECTED_COCYCLE_COUNT:", len(native_selected_cocycle_rows))
print(
    "NATIVE_SELECTED_CLASS_ROWS:",
    native_selected_class_rows,
)
print(
    "SELECTED_REPRESENTATIVES_GAUGE_RELATED:",
    str(selected_representatives_gauge_related).lower(),
)
print(
    "NATIVE_ABSTRACT_D8_MATCH:",
    str(native_abstract_D8_match).lower(),
)
print(
    "SELECTED_CLASS_SEPARATES_AB_BA:",
    str(selected_separates_AB_BA).lower(),
)
print("PREDICTION_MATCHES:", str(prediction_matches).lower())
print("CLASSIFICATION:", classification)
print(
    "REPOSITORY_STATUS_PRESERVED:",
    str(repository_status_preserved).lower(),
)
print("PROJECT_MUTATION_PERFORMED: false")
print("LOCAL_SIDE_EQUALS_011O_ORIENTATION_SHEET: false")
print("NATIVE_UPDATE_LAW_CONSTRUCTED: false")
print("MECHANICS_STATE_CELL_ESTABLISHED: false")
print("MANUSCRIPT_MUTATED: false")
print("PHYSICAL_CLAIM: false")
print("CANDIDATE_JSON:", candidate_path)
print("CANDIDATE_JSON_SHA256:", sha256_file(candidate_path))
