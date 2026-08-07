import hashlib
import itertools
import json
import math
import subprocess
import sys
from collections import Counter
from pathlib import Path

project = Path(sys.argv[1]).resolve()
candidate_path = Path(sys.argv[2]).resolve()

math_root = Path("/data/data/com.termux/files/home/dev/cori/research/mathematics/42-graph-automorphism-groups")
action_path = math_root / "artifacts/json/native_g60_fiber_product_isomorphism_044.json"
equivariance_path = math_root / "artifacts/json/native_g60_five_petersen_matching_equivariance_audit_078.json"
bridge_path = project / "artifacts/json/g60_duad_orientation_bridge_census_011g.v1.json"
minimal_path = project / "artifacts/json/g60_minimal_directional_datum_census_011i.v1.json"
prereg_path = project / "artifacts/json/g60_full_A_orientation_character_extension_preregistration_011n.v1.json"
twisted_path = project / "artifacts/json/g60_parity_twisted_duad_cover_census_011m.v1.json"
stabilizer_path = project / "artifacts/json/g60_root_stabilizer_action_type_census_011k.v1.json"

expected_hashes = {
    str(action_path): "b37313b135495752b11e525bb61979163fdf54aec4be4f5d027dcee64c9efc21",
    str(equivariance_path): "db01304b44015a25e8f207d3fe869ad96ebcd82d3d2bd7017908a9ed7c843ec7",
    str(bridge_path): "abc9e038b323fdd5af852a91b87aca4c5a1e35a6e484608af27a04a399c52e9c",
    str(minimal_path): "6d7164f98d686dc9d54b8146f19ab56c22c8aa70009f65bbcad7c7c88e9b962d",
    str(prereg_path): "ce0671b9d0ad33880c8b3d043878366abe885438976481f6fef3fbde16c21097",
    str(twisted_path): "8c556050e4ea028cc41eca4514366c3a0d6baa83620831259151dbed0b046a7e",
    str(stabilizer_path): "6685932b584a9784410ed57eabe7cfab27de43365ac74bc844c166f375b31574",
}

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def git(*args):
    return subprocess.run(
        ["git", *args],
        cwd=project,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    ).stdout.strip()

actual_hashes = {path: sha256(Path(path)) for path in expected_hashes}
hash_matches = {
    path: actual_hashes[path] == expected_hashes[path]
    for path in expected_hashes
}
all_hashes_match = all(hash_matches.values())

head = git("--no-pager", "show", "-s", "--format=%h %s", "HEAD")
status_before = git("status", "--short", "--", ".")

action_data = json.loads(action_path.read_text(encoding="utf-8"))
equivariance = json.loads(equivariance_path.read_text(encoding="utf-8"))
bridge = json.loads(bridge_path.read_text(encoding="utf-8"))
minimal = json.loads(minimal_path.read_text(encoding="utf-8"))
prereg = json.loads(prereg_path.read_text(encoding="utf-8"))
twisted_packet = json.loads(twisted_path.read_text(encoding="utf-8"))
stabilizer_packet = json.loads(stabilizer_path.read_text(encoding="utf-8"))

permutations = {
    int(row["actual_index"]): tuple(int(x) for x in row["actual_permutation"])
    for row in action_data["mapping_rows"]
}
indices = sorted(permutations)
degree = len(permutations[0])
perm_to_index = {perm: index for index, perm in permutations.items()}
identity_perm = tuple(range(degree))
identity = next(
    index for index in indices if permutations[index] == identity_perm
)

def compose(p, q):
    return tuple(p[q[v]] for v in range(degree))

print("== G60 FULL-A ORIENTATION CHARACTER-EXTENSION CENSUS 011o ==")
print("MODE: temporary read-only complete character-extension census")
print("LOCKED_HEAD:", head)
print("ALL_AUTHORITY_HASHES_MATCH:", str(all_hashes_match).lower())
print()
print("MULTIPLICATION_BEGIN")

multiplication = [[None] * 480 for _ in range(480)]
closure_failures = []
for row_number, g in enumerate(indices):
    if row_number % 40 == 0:
        print("MULTIPLICATION_PROGRESS:", row_number, "/", len(indices))
    for h in indices:
        product = perm_to_index.get(compose(permutations[g], permutations[h]))
        if product is None:
            closure_failures.append([g, h])
        else:
            multiplication[g][h] = product
print("MULTIPLICATION_PROGRESS:", len(indices), "/", len(indices))
print("MULTIPLICATION_END")

inverse = {}
inverse_failures = []
for g in indices:
    candidates = [
        h for h in indices
        if multiplication[g][h] == identity
        and multiplication[h][g] == identity
    ]
    if len(candidates) == 1:
        inverse[g] = candidates[0]
    else:
        inverse_failures.append([g, candidates])

operation_ok = not closure_failures and not inverse_failures

def conjugate(g, h):
    return multiplication[multiplication[g][h]][inverse[g]]

block_rows = {
    int(row["actual_index"]): tuple(int(x) for x in row["block_image"])
    for row in equivariance["action_rows"]
}
S5_image = tuple(sorted(set(block_rows.values())))

N = frozenset(minimal["canonical_propagation_subgroup"]["member_indices"])
complements = [
    frozenset(row["member_indices"])
    for row in minimal["complement_reconstruction"]["complement_rows"]
]

inverse_pairs = tuple(
    tuple(pair)
    for pair in bridge["A_sets"]["inverse_root_pairs"]["pairs"]
)
roots = tuple(sorted({root for pair in inverse_pairs for root in pair}))
ordered_duads = tuple(
    (i, j) for i in range(5) for j in range(5) if i != j
)
unordered_duads = tuple(
    (i, j) for i in range(5) for j in range(i + 1, 5)
)

pair_for_duad = {
    tuple(row["unordered_duad"]): tuple(row["inverse_pair"])
    for row in bridge["equivariant_bridges"][
        "unordered_to_inverse_pairs"
    ]["rows"]
}
duad_for_root = {}
for duad, pair in pair_for_duad.items():
    for root in pair:
        duad_for_root[root] = duad

def perm_parity(perm):
    inversions = sum(
        1 for i in range(len(perm))
        for j in range(i + 1, len(perm))
        if perm[i] > perm[j]
    )
    return "even" if inversions % 2 == 0 else "odd"

def cycle_type(perm):
    seen = set()
    lengths = []
    for start in range(len(perm)):
        if start in seen:
            continue
        current = start
        length = 0
        while current not in seen:
            seen.add(current)
            current = perm[current]
            length += 1
        lengths.append(length)
    return tuple(sorted(lengths, reverse=True))

def permutation_order(perm):
    result = 1
    for length in cycle_type(perm):
        result = math.lcm(result, length)
    return result

def subgroup_orbits(perms):
    unseen = set(range(5))
    sizes = []
    while unseen:
        start = min(unseen)
        orbit = {perm[start] for perm in perms}
        changed = True
        while changed:
            changed = False
            expanded = {perm[x] for perm in perms for x in orbit}
            if not expanded <= orbit:
                orbit |= expanded
                changed = True
        unseen -= orbit
        sizes.append(len(orbit))
    return tuple(sorted(sizes))

def image_profile(perms):
    perms = frozenset(perms)
    return {
        "order": len(perms),
        "element_order_profile": dict(sorted(Counter(
            permutation_order(perm) for perm in perms
        ).items())),
        "cycle_type_profile": {
            ",".join(str(x) for x in key): value
            for key, value in sorted(Counter(
                cycle_type(perm) for perm in perms
            ).items())
        },
        "parity_profile": dict(sorted(Counter(
            perm_parity(perm) for perm in perms
        ).items())),
        "orbit_size_profile": list(subgroup_orbits(perms)),
    }

def root_stabilizer(group, root):
    return frozenset(g for g in group if conjugate(g, root) == root)

def ordered_stabilizer(group, duad):
    return frozenset(
        g for g in group
        if block_rows[g][duad[0]] == duad[0]
        and block_rows[g][duad[1]] == duad[1]
    )

def projected(group):
    return frozenset(block_rows[g] for g in group)

def even_duad_setwise_stabilizer(duad):
    target = set(duad)
    return frozenset(
        perm for perm in S5_image
        if {perm[duad[0]], perm[duad[1]]} == target
        and perm_parity(perm) == "even"
    )

def conjugate_perm(g, h):
    inverse_g = [None] * 5
    for i, value in enumerate(g):
        inverse_g[value] = i
    return tuple(g[h[inverse_g[i]]] for i in range(5))

def subgroup_conjugate_in_S5(left, right):
    right = frozenset(right)
    return any(
        frozenset(conjugate_perm(g, h) for h in left) == right
        for g in S5_image
    )
# The locked prefix reconstructs the exact 480-element group, N,
# both complements, the five-point action, roots, and duad-root pairing.

A = tuple(indices)
N_set = frozenset(N)

source_objects = tuple(
    (duad, epsilon)
    for duad in unordered_duads
    for epsilon in (0, 1)
)
source_index = {
    source_object: index
    for index, source_object in enumerate(source_objects)
}

def p_value(g):
    return 0 if perm_parity(block_rows[g]) == "even" else 1

def n_value(g):
    return 0 if g in N_set else 1

def alpha_0_value(g):
    return p_value(g)

def alpha_1_value(g):
    return p_value(g) ^ n_value(g)

def character_sha256(values):
    payload = json.dumps(list(values), separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

def character_homomorphism_failures(value_function):
    failures = []
    for g in A:
        for h in A:
            product = multiplication[g][h]
            if value_function(product) != (
                value_function(g) ^ value_function(h)
            ):
                failures.append([g, h, product])
                return failures
    return failures

def generated_subgroup(generators):
    steps = set(generators)
    steps.update(inverse[g] for g in generators)
    reached = {identity}
    queue = [identity]

    while queue:
        current = queue.pop()
        for step in steps:
            product = multiplication[current][step]
            if product not in reached:
                reached.add(product)
                queue.append(product)

    return frozenset(reached)

def greedy_generators():
    generators = []
    generated = frozenset([identity])

    while len(generated) < len(A):
        candidate = min(g for g in A if g not in generated)
        generators.append(candidate)
        generated = generated_subgroup(generators)

    return tuple(generators)

def extend_generator_assignment(generators, assignment):
    generator_values = {
        generator: bit
        for generator, bit in zip(generators, assignment)
    }

    steps = []
    for generator in generators:
        bit = generator_values[generator]
        steps.append((generator, bit))
        steps.append((inverse[generator], bit))

    values = {identity: 0}
    queue = [identity]
    conflict = None

    while queue and conflict is None:
        current = queue.pop()
        current_value = values[current]

        for step, step_value in steps:
            product = multiplication[current][step]
            predicted = current_value ^ step_value

            if product in values:
                if values[product] != predicted:
                    conflict = {
                        "current": current,
                        "step": step,
                        "product": product,
                        "existing": values[product],
                        "predicted": predicted,
                    }
                    break
            else:
                values[product] = predicted
                queue.append(product)

    if conflict is not None or len(values) != len(A):
        return None, conflict

    value_tuple = tuple(values[g] for g in A)

    for g in A:
        for h in A:
            if value_tuple[multiplication[g][h]] != (
                value_tuple[g] ^ value_tuple[h]
            ):
                return None, {
                    "full_homomorphism_failure": [g, h]
                }

    return value_tuple, None

def enumerate_binary_characters():
    generators = greedy_generators()
    rows = []

    for mask in range(1 << len(generators)):
        assignment = tuple(
            (mask >> position) & 1
            for position in range(len(generators))
        )
        values, conflict = extend_generator_assignment(
            generators,
            assignment,
        )
        rows.append({
            "assignment": list(assignment),
            "valid": values is not None,
            "values": values,
            "conflict": conflict,
        })

    return generators, rows

def full_source_action(g, source_object, value_function):
    duad, epsilon = source_object
    image_duad = tuple(sorted(block_rows[g][x] for x in duad))
    image_epsilon = epsilon ^ value_function(g)
    return (image_duad, image_epsilon)

def validate_action(value_function):
    identity_failures = [
        source_object
        for source_object in source_objects
        if full_source_action(
            identity,
            source_object,
            value_function,
        ) != source_object
    ]

    closure_failures_action = []
    for g in A:
        for h in A:
            product = multiplication[g][h]
            for source_object in source_objects:
                left = full_source_action(
                    product,
                    source_object,
                    value_function,
                )
                right = full_source_action(
                    g,
                    full_source_action(
                        h,
                        source_object,
                        value_function,
                    ),
                    value_function,
                )
                if left != right:
                    closure_failures_action.append({
                        "g": g,
                        "h": h,
                        "source_object": [
                            list(source_object[0]),
                            source_object[1],
                        ],
                    })
                    return identity_failures, closure_failures_action

    return identity_failures, closure_failures_action

def action_orbits(value_function):
    unseen = set(source_objects)
    orbits = []

    while unseen:
        seed = min(unseen)
        orbit = {
            full_source_action(g, seed, value_function)
            for g in A
        }
        orbits.append(tuple(sorted(orbit)))
        unseen -= orbit

    return tuple(sorted(orbits, key=lambda row: (len(row), row)))

def action_pointwise_kernel(value_function):
    return tuple(
        g for g in A
        if all(
            full_source_action(g, source_object, value_function)
            == source_object
            for source_object in source_objects
        )
    )

def source_stabilizer_full(source_object, value_function):
    return frozenset(
        g for g in A
        if full_source_action(g, source_object, value_function)
        == source_object
    )

def map_signature(mapping):
    payload = [
        {
            "unordered_duad": list(source_object[0]),
            "epsilon": source_object[1],
            "root": mapping[index],
        }
        for index, source_object in enumerate(source_objects)
    ]
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))

def map_sha256(mapping):
    return hashlib.sha256(
        map_signature(mapping).encode("utf-8")
    ).hexdigest()

def enumerate_full_A_maps(value_function):
    base_source = source_objects[0]
    maps = []
    rejected_conflicts = []
    rejected_incomplete = []
    rejected_nonbijective = []
    rejected_equivariance = []

    for target_root in roots:
        mapping_by_source = {}
        conflict = False

        for g in A:
            source_image = full_source_action(
                g,
                base_source,
                value_function,
            )
            target_image = conjugate(g, target_root)

            if (
                source_image in mapping_by_source
                and mapping_by_source[source_image] != target_image
            ):
                conflict = True
                break

            mapping_by_source[source_image] = target_image

        if conflict:
            rejected_conflicts.append(target_root)
            continue

        if set(mapping_by_source) != set(source_objects):
            rejected_incomplete.append(target_root)
            continue

        mapping = tuple(
            mapping_by_source[source_object]
            for source_object in source_objects
        )

        if len(set(mapping)) != 20 or set(mapping) != set(roots):
            rejected_nonbijective.append(target_root)
            continue

        failure = None
        for g in A:
            for source_object in source_objects:
                left = mapping[source_index[full_source_action(
                    g,
                    source_object,
                    value_function,
                )]]
                right = conjugate(
                    g,
                    mapping[source_index[source_object]],
                )
                if left != right:
                    failure = {
                        "g": g,
                        "source_object": [
                            list(source_object[0]),
                            source_object[1],
                        ],
                        "left": left,
                        "right": right,
                    }
                    break
            if failure is not None:
                break

        if failure is not None:
            rejected_equivariance.append({
                "target_root": target_root,
                "failure": failure,
            })
            continue

        maps.append(mapping)

    unique_maps = {
        map_signature(mapping): mapping
        for mapping in maps
    }

    return {
        "maps": tuple(
            unique_maps[key]
            for key in sorted(unique_maps)
        ),
        "rejected_conflict_roots": rejected_conflicts,
        "rejected_incomplete_roots": rejected_incomplete,
        "rejected_nonbijective_roots": rejected_nonbijective,
        "rejected_equivariance_rows": rejected_equivariance,
    }

print()
print("CHARACTER_ENUMERATION_BEGIN")

p_failures = character_homomorphism_failures(p_value)
n_failures = character_homomorphism_failures(n_value)
alpha_0_failures = character_homomorphism_failures(alpha_0_value)
alpha_1_failures = character_homomorphism_failures(alpha_1_value)

generators, character_rows_raw = enumerate_binary_characters()
valid_character_values = tuple(
    row["values"]
    for row in character_rows_raw
    if row["valid"]
)

p_values = tuple(p_value(g) for g in A)
n_values = tuple(n_value(g) for g in A)
alpha_0_values = tuple(alpha_0_value(g) for g in A)
alpha_1_values = tuple(alpha_1_value(g) for g in A)

restriction_target = tuple(p_value(g) for g in sorted(N))
extension_values = tuple(
    values
    for values in valid_character_values
    if tuple(values[g] for g in sorted(N)) == restriction_target
)

extension_hashes = sorted(
    character_sha256(values)
    for values in extension_values
)

declared_extension_hashes = sorted([
    character_sha256(alpha_0_values),
    character_sha256(alpha_1_values),
])

extensions_exact = (
    len(extension_values) == 2
    and extension_hashes == declared_extension_hashes
)

print("CHARACTER_ENUMERATION_END")

print()
print("FULL_ACTION_VALIDATION_BEGIN")

alpha_0_identity_failures, alpha_0_closure_failures = (
    validate_action(alpha_0_value)
)
alpha_1_identity_failures, alpha_1_closure_failures = (
    validate_action(alpha_1_value)
)

alpha_0_valid = (
    not alpha_0_identity_failures
    and not alpha_0_closure_failures
)
alpha_1_valid = (
    not alpha_1_identity_failures
    and not alpha_1_closure_failures
)

alpha_0_orbits = action_orbits(alpha_0_value)
alpha_1_orbits = action_orbits(alpha_1_value)

alpha_0_transitive = (
    len(alpha_0_orbits) == 1
    and len(alpha_0_orbits[0]) == 20
)
alpha_1_transitive = (
    len(alpha_1_orbits) == 1
    and len(alpha_1_orbits[0]) == 20
)

alpha_0_kernel = action_pointwise_kernel(alpha_0_value)
alpha_1_kernel = action_pointwise_kernel(alpha_1_value)

print("FULL_ACTION_VALIDATION_END")

residual_character_rows = [
    {
        "element_index": g,
        "p": p_value(g),
        "n": n_value(g),
        "alpha_0": alpha_0_value(g),
        "alpha_1": alpha_1_value(g),
    }
    for g in (0, 65, 124, 326)
]

alpha_0_stabilizer_failures = []
alpha_1_stabilizer_failures = []

for source_object in source_objects:
    duad, epsilon = source_object
    assigned_pair = tuple(pair_for_duad[duad])

    alpha_0_stabilizer = source_stabilizer_full(
        source_object,
        alpha_0_value,
    )
    alpha_1_stabilizer = source_stabilizer_full(
        source_object,
        alpha_1_value,
    )

    for root in assigned_pair:
        target_stabilizer = root_stabilizer(A, root)

        if alpha_0_stabilizer != target_stabilizer:
            alpha_0_stabilizer_failures.append({
                "unordered_duad": list(duad),
                "epsilon": epsilon,
                "root": root,
            })

        if alpha_1_stabilizer != target_stabilizer:
            alpha_1_stabilizer_failures.append({
                "unordered_duad": list(duad),
                "epsilon": epsilon,
                "root": root,
            })

print()
print("FULL_A_BRIDGE_ENUMERATION_BEGIN")

alpha_0_enumeration = enumerate_full_A_maps(alpha_0_value)
alpha_1_enumeration = enumerate_full_A_maps(alpha_1_value)

alpha_0_maps = alpha_0_enumeration["maps"]
alpha_1_maps = alpha_1_enumeration["maps"]

print("FULL_A_BRIDGE_ENUMERATION_END")

alpha_0_map_hashes = [
    map_sha256(mapping)
    for mapping in alpha_0_maps
]
alpha_1_map_hashes = [
    map_sha256(mapping)
    for mapping in alpha_1_maps
]

locked_011m_hashes = sorted(
    twisted_packet["equivariant_bridges"]["N_map_sha256s"]
)
alpha_1_maps_equal_011m = (
    sorted(alpha_1_map_hashes) == locked_011m_hashes
)

reversal_rows = []
reversal_failures = []

for map_index, mapping in enumerate(alpha_1_maps):
    sheet_reversed = tuple(
        mapping[source_index[(source_object[0], source_object[1] ^ 1)]]
        for source_object in source_objects
    )
    root_inverted = tuple(
        inverse[root]
        for root in mapping
    )

    sheet_matches = [
        candidate_index
        for candidate_index, candidate in enumerate(alpha_1_maps)
        if candidate == sheet_reversed
    ]
    inversion_matches = [
        candidate_index
        for candidate_index, candidate in enumerate(alpha_1_maps)
        if candidate == root_inverted
    ]

    row = {
        "map_index": map_index,
        "sheet_reversal_map_indices": sheet_matches,
        "root_inversion_map_indices": inversion_matches,
        "sheet_reversal_equals_root_inversion": (
            sheet_reversed == root_inverted
        ),
        "reversal_changes_map": sheet_reversed != mapping,
    }
    reversal_rows.append(row)

    if not (
        len(sheet_matches) == 1
        and len(inversion_matches) == 1
        and row["sheet_reversal_equals_root_inversion"]
        and row["reversal_changes_map"]
    ):
        reversal_failures.append(map_index)

reversal_verified = (
    len(alpha_1_maps) == 2
    and not reversal_failures
)

anchor_rows = []
for source_object in source_objects:
    duad, epsilon = source_object
    for root in pair_for_duad[duad]:
        matching_maps = [
            map_index
            for map_index, mapping in enumerate(alpha_1_maps)
            if mapping[source_index[source_object]] == root
        ]
        anchor_rows.append({
            "unordered_duad": list(duad),
            "epsilon": epsilon,
            "root": root,
            "bridge_count": len(matching_maps),
            "matching_map_indices": matching_maps,
        })

anchor_profile = dict(sorted(Counter(
    row["bridge_count"]
    for row in anchor_rows
).items()))

anchors_unique = (
    len(anchor_rows) == 40
    and anchor_profile == {1: 40}
)

characters_valid = (
    not p_failures
    and not n_failures
    and not alpha_0_failures
    and not alpha_1_failures
)

kernel_predictions_match = (
    list(alpha_0_kernel) == [0, 65, 124, 326]
    and list(alpha_1_kernel) == [0, 326]
)

prediction_matches = (
    characters_valid
    and extensions_exact
    and alpha_0_valid
    and alpha_1_valid
    and alpha_0_transitive
    and alpha_1_transitive
    and kernel_predictions_match
    and len(alpha_0_maps) == 0
    and len(alpha_1_maps) == 2
    and alpha_1_maps_equal_011m
    and reversal_verified
    and anchors_unique
    and len(alpha_1_stabilizer_failures) == 0
    and len(alpha_0_stabilizer_failures) == 40
)

authority_failure = (
    not all_hashes_match
    or head != "dfd715e Preregister G60 full-A orientation character test"
    or not operation_ok
    or prereg["status"] != "frozen_before_computation"
    or twisted_packet["classification"]
        != "exactly_two_inversion_related_bridges_anchor_selects_one"
    or len(N) != 240
)

if not operation_ok:
    classification = "computation_failure"
elif authority_failure:
    classification = "authority_failure"
elif not characters_valid:
    classification = "p_or_n_not_homomorphism"
elif not extensions_exact:
    classification = "extension_count_not_two"
elif not (alpha_0_valid and alpha_1_valid):
    classification = "declared_full_action_invalid"
elif not kernel_predictions_match:
    classification = "character_kernel_prediction_failure"
elif len(alpha_0_maps) != 0:
    classification = "alpha_0_unexpectedly_supports_bridge"
elif len(alpha_1_maps) == 0:
    classification = "alpha_1_supports_no_bridge"
elif len(alpha_1_maps) == 1:
    classification = "alpha_1_supports_unexpected_unique_bridge"
elif len(alpha_1_maps) > 2:
    classification = "alpha_1_supports_more_than_two_bridges"
elif not alpha_1_maps_equal_011m:
    classification = "alpha_1_bridge_pair_differs_from_011m"
elif not reversal_verified:
    classification = "alpha_1_bridges_not_inversion_related"
elif not anchors_unique:
    classification = "anchor_does_not_select_unique_alpha_1_bridge"
else:
    classification = (
        "p_plus_n_unique_full_A_extension_supports_two_bridges"
    )

status_after = git("status", "--short", "--", ".")
repository_preserved = status_after == status_before

character_rows = []
for row in character_rows_raw:
    character_rows.append({
        "assignment": row["assignment"],
        "valid": row["valid"],
        "character_sha256": (
            character_sha256(row["values"])
            if row["values"] is not None
            else None
        ),
        "conflict": row["conflict"],
    })

result = {
    "packet": "g60_full_A_orientation_character_extension_census_011o_candidate",
    "mode": "temporary_read_only_complete_character_extension_census",
    "locked_head": head,
    "authorities": {
        path: {
            "expected_sha256": expected_hashes[path],
            "sha256": actual_hashes[path],
            "hash_match": hash_matches[path],
        }
        for path in expected_hashes
    },
    "group_reconstruction": {
        "group_order": len(A),
        "identity_index": identity,
        "closure_failure_count": len(closure_failures),
        "inverse_failure_count": len(inverse_failures),
        "operation_ok": operation_ok,
        "canonical_N_order": len(N),
    },
    "character_census": {
        "greedy_generators": list(generators),
        "generator_count": len(generators),
        "assignment_count": len(character_rows_raw),
        "valid_binary_character_count": len(valid_character_values),
        "character_rows": character_rows,
        "p_homomorphism_failure_count": len(p_failures),
        "n_homomorphism_failure_count": len(n_failures),
        "alpha_0_homomorphism_failure_count": len(alpha_0_failures),
        "alpha_1_homomorphism_failure_count": len(alpha_1_failures),
        "p_sha256": character_sha256(p_values),
        "n_sha256": character_sha256(n_values),
        "alpha_0_sha256": character_sha256(alpha_0_values),
        "alpha_1_sha256": character_sha256(alpha_1_values),
        "extension_count": len(extension_values),
        "extension_sha256s": extension_hashes,
        "declared_extension_sha256s": declared_extension_hashes,
        "extensions_exactly_alpha_0_alpha_1": extensions_exact,
        "residual_character_rows": residual_character_rows,
    },
    "full_actions": {
        "alpha_0": {
            "formula": "p",
            "identity_failure_count": len(alpha_0_identity_failures),
            "closure_failure_count": len(alpha_0_closure_failures),
            "action_valid": alpha_0_valid,
            "orbit_count": len(alpha_0_orbits),
            "orbit_size_profile": sorted(
                len(orbit) for orbit in alpha_0_orbits
            ),
            "transitive": alpha_0_transitive,
            "pointwise_kernel": list(alpha_0_kernel),
            "stabilizer_match_failure_count": len(
                alpha_0_stabilizer_failures
            ),
        },
        "alpha_1": {
            "formula": "p+n",
            "identity_failure_count": len(alpha_1_identity_failures),
            "closure_failure_count": len(alpha_1_closure_failures),
            "action_valid": alpha_1_valid,
            "orbit_count": len(alpha_1_orbits),
            "orbit_size_profile": sorted(
                len(orbit) for orbit in alpha_1_orbits
            ),
            "transitive": alpha_1_transitive,
            "pointwise_kernel": list(alpha_1_kernel),
            "stabilizer_match_failure_count": len(
                alpha_1_stabilizer_failures
            ),
        },
    },
    "bridge_census": {
        "alpha_0_bridge_count": len(alpha_0_maps),
        "alpha_0_map_sha256s": alpha_0_map_hashes,
        "alpha_0_rejected_conflict_roots": (
            alpha_0_enumeration["rejected_conflict_roots"]
        ),
        "alpha_1_bridge_count": len(alpha_1_maps),
        "alpha_1_map_sha256s": alpha_1_map_hashes,
        "locked_011m_map_sha256s": locked_011m_hashes,
        "alpha_1_maps_equal_011m": alpha_1_maps_equal_011m,
        "reversal_rows": reversal_rows,
        "reversal_failure_count": len(reversal_failures),
        "reversal_verified": reversal_verified,
    },
    "anchor_ablation": {
        "compatible_anchor_count": len(anchor_rows),
        "anchor_rows": anchor_rows,
        "anchor_bridge_count_profile": anchor_profile,
        "all_compatible_anchors_select_unique_bridge": anchors_unique,
        "without_anchor_bridge_count": len(alpha_1_maps),
    },
    "classification": classification,
    "prediction_matches": prediction_matches,
    "earned_statement_candidate": (
        "The locked N-sheet character has exactly two extensions to "
        "Aut(G60): p and p+n. Both define valid transitive twenty-object "
        "full-group actions. The p-only action has pointwise kernel V4 "
        "and admits no equivariant bridge to the roots. The p+n action "
        "has pointwise kernel Z1 and admits exactly the two bridges "
        "already frozen over N. These bridges are exchanged by sheet "
        "reversal and root inversion, and every compatible anchor "
        "selects exactly one."
    ),
    "boundary": {
        "full_A_source_action_constructed": True,
        "unique_supporting_character_identified": prediction_matches,
        "orientation_selected_without_anchor": False,
        "bounded_anchor_sufficiency": prediction_matches,
        "global_minimality_claim": False,
        "physical_direction_claim": False,
        "manuscript_mutated": False,
        "geometry_claim": False,
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
print("== FINAL FULL-A CHARACTER-EXTENSION REPORT ==")
print("OPERATION_OK:", str(operation_ok).lower())
print("GENERATOR_COUNT:", len(generators))
print("VALID_BINARY_CHARACTER_COUNT:", len(valid_character_values))
print("P_HOMOMORPHISM_FAILURE_COUNT:", len(p_failures))
print("N_HOMOMORPHISM_FAILURE_COUNT:", len(n_failures))
print("EXTENSION_COUNT:", len(extension_values))
print("EXTENSIONS_EXACT:", str(extensions_exact).lower())
print("ALPHA_0_ACTION_VALID:", str(alpha_0_valid).lower())
print("ALPHA_1_ACTION_VALID:", str(alpha_1_valid).lower())
print("ALPHA_0_ORBIT_SIZE_PROFILE:", sorted(len(x) for x in alpha_0_orbits))
print("ALPHA_1_ORBIT_SIZE_PROFILE:", sorted(len(x) for x in alpha_1_orbits))
print("ALPHA_0_POINTWISE_KERNEL:", list(alpha_0_kernel))
print("ALPHA_1_POINTWISE_KERNEL:", list(alpha_1_kernel))
print("ALPHA_0_STABILIZER_FAILURE_COUNT:", len(alpha_0_stabilizer_failures))
print("ALPHA_1_STABILIZER_FAILURE_COUNT:", len(alpha_1_stabilizer_failures))
print("ALPHA_0_BRIDGE_COUNT:", len(alpha_0_maps))
print("ALPHA_1_BRIDGE_COUNT:", len(alpha_1_maps))
print("ALPHA_1_MAP_SHA256S:", alpha_1_map_hashes)
print("ALPHA_1_MAPS_EQUAL_011M:", str(alpha_1_maps_equal_011m).lower())
print("REVERSAL_VERIFIED:", str(reversal_verified).lower())
print("ANCHOR_BRIDGE_COUNT_PROFILE:", anchor_profile)
print("PREDICTION_MATCHES:", str(prediction_matches).lower())
print("CLASSIFICATION:", classification)
print("REPOSITORY_STATUS_PRESERVED:", str(repository_preserved).lower())
print("PROJECT_MUTATION_PERFORMED: false")
print("FULL_A_SOURCE_ACTION_CONSTRUCTED: true")
print("ORIENTATION_SELECTED_WITHOUT_ANCHOR: false")
print("MANUSCRIPT_MUTATED: false")
print("PHYSICAL_CLAIM: false")
print("CANDIDATE_JSON:", candidate_path)
print("CANDIDATE_JSON_SHA256:", sha256(candidate_path))
