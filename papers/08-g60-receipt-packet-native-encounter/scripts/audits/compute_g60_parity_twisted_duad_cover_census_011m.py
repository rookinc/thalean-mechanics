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
prereg_path = project / "artifacts/json/g60_parity_twisted_duad_cover_preregistration_011l.v1.json"
stabilizer_path = project / "artifacts/json/g60_root_stabilizer_action_type_census_011k.v1.json"

expected_hashes = {
    str(action_path): "b37313b135495752b11e525bb61979163fdf54aec4be4f5d027dcee64c9efc21",
    str(equivariance_path): "db01304b44015a25e8f207d3fe869ad96ebcd82d3d2bd7017908a9ed7c843ec7",
    str(bridge_path): "abc9e038b323fdd5af852a91b87aca4c5a1e35a6e484608af27a04a399c52e9c",
    str(minimal_path): "6d7164f98d686dc9d54b8146f19ab56c22c8aa70009f65bbcad7c7c88e9b962d",
    str(prereg_path): "b576049b323ba72ffcd069070f0941b134241595fad954a3c59d37fa2e57d7a2",
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

print("== G60 PARITY-TWISTED DUAD COVER CENSUS 011m ==")
print("MODE: temporary read-only complete twisted-cover census")
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
# The locked 011k prefix above reconstructs:
# multiplication, inverse, conjugation, block_rows, N, complements,
# roots, unordered_duads, pair_for_duad, and perm_parity.

source_objects = tuple(
    (duad, epsilon)
    for duad in unordered_duads
    for epsilon in (0, 1)
)
source_index = {
    source_object: index
    for index, source_object in enumerate(source_objects)
}

def parity_bit(g):
    return 0 if perm_parity(block_rows[g]) == "even" else 1

def source_action(g, source_object):
    duad, epsilon = source_object
    image_duad = tuple(sorted(block_rows[g][x] for x in duad))
    image_epsilon = epsilon ^ parity_bit(g)
    return (image_duad, image_epsilon)

def root_action(g, root):
    return conjugate(g, root)

def source_stabilizer(group, source_object):
    return frozenset(
        g for g in group
        if source_action(g, source_object) == source_object
    )

def source_orbits(group):
    unseen = set(source_objects)
    orbits = []
    while unseen:
        seed = min(unseen)
        orbit = {
            source_action(g, seed)
            for g in group
        }
        orbits.append(tuple(sorted(orbit)))
        unseen -= orbit
    return tuple(sorted(orbits, key=lambda row: (len(row), row)))

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

def enumerate_equivariant_maps(group):
    group = tuple(sorted(group))
    base_source = source_objects[0]
    maps = []
    rejected_conflicts = []
    rejected_incomplete = []
    rejected_nonbijective = []
    rejected_equivariance = []

    for target_root in roots:
        mapping_by_source = {}
        conflict = False

        for g in group:
            source_image = source_action(g, base_source)
            target_image = root_action(g, target_root)

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

        if len(set(mapping)) != len(roots) or set(mapping) != set(roots):
            rejected_nonbijective.append(target_root)
            continue

        failure = None
        for g in group:
            for source_object in source_objects:
                left = mapping[source_index[source_action(g, source_object)]]
                right = root_action(
                    g,
                    mapping[source_index[source_object]],
                )
                if left != right:
                    failure = {
                        "group_element": g,
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

    ordered_maps = tuple(
        unique_maps[key]
        for key in sorted(unique_maps)
    )

    return {
        "maps": ordered_maps,
        "rejected_conflict_roots": rejected_conflicts,
        "rejected_incomplete_roots": rejected_incomplete,
        "rejected_nonbijective_roots": rejected_nonbijective,
        "rejected_equivariance_rows": rejected_equivariance,
    }

def map_rows(mapping, map_index):
    return [
        {
            "map_index": map_index,
            "unordered_duad": list(source_object[0]),
            "epsilon": source_object[1],
            "root": mapping[index],
        }
        for index, source_object in enumerate(source_objects)
    ]

print()
print("SOURCE_ACTION_VALIDATION_BEGIN")

identity_failures = [
    source_object
    for source_object in source_objects
    if source_action(identity, source_object) != source_object
]

closure_failures_source = []
for row_number, g in enumerate(sorted(N)):
    if row_number % 40 == 0:
        print(
            "SOURCE_ACTION_PROGRESS:",
            row_number,
            "/",
            len(N),
        )
    for h in N:
        product = multiplication[g][h]
        for source_object in source_objects:
            left = source_action(product, source_object)
            right = source_action(g, source_action(h, source_object))
            if left != right:
                closure_failures_source.append({
                    "g": g,
                    "h": h,
                    "source_object": [
                        list(source_object[0]),
                        source_object[1],
                    ],
                    "left": [list(left[0]), left[1]],
                    "right": [list(right[0]), right[1]],
                })
                break
        if closure_failures_source:
            break
    if closure_failures_source:
        break

print("SOURCE_ACTION_PROGRESS:", len(N), "/", len(N))
print("SOURCE_ACTION_VALIDATION_END")

source_action_valid = (
    not identity_failures
    and not closure_failures_source
)

source_orbit_rows = source_orbits(N)
source_transitive = (
    len(source_orbit_rows) == 1
    and len(source_orbit_rows[0]) == 20
)

print()
print("STABILIZER_EQUALITY_BEGIN")

source_stabilizer_rows = []
stabilizer_match_failures = []

for source_object in source_objects:
    duad, epsilon = source_object
    source_stab = source_stabilizer(N, source_object)
    assigned_pair = tuple(pair_for_duad[duad])

    root_stabilizers = {
        root: root_stabilizer(N, root)
        for root in assigned_pair
    }

    matching_roots = sorted(
        root
        for root, root_stab in root_stabilizers.items()
        if root_stab == source_stab
    )

    image = projected(source_stab)

    row = {
        "unordered_duad": list(duad),
        "epsilon": epsilon,
        "source_stabilizer_order": len(source_stab),
        "source_stabilizer_member_indices": sorted(source_stab),
        "source_stabilizer_image_order": len(image),
        "source_stabilizer_image_profile": image_profile(image),
        "assigned_inverse_pair": list(assigned_pair),
        "matching_root_stabilizers": matching_roots,
    }
    source_stabilizer_rows.append(row)

    if matching_roots != sorted(assigned_pair):
        stabilizer_match_failures.append({
            "unordered_duad": list(duad),
            "epsilon": epsilon,
            "assigned_pair": list(assigned_pair),
            "matching_roots": matching_roots,
        })

print("STABILIZER_EQUALITY_END")

source_stabilizer_orders = sorted({
    row["source_stabilizer_order"]
    for row in source_stabilizer_rows
})
source_image_orders = sorted({
    row["source_stabilizer_image_order"]
    for row in source_stabilizer_rows
})
source_image_profiles = {
    json.dumps(
        row["source_stabilizer_image_profile"],
        sort_keys=True,
    )
    for row in source_stabilizer_rows
}

print()
print("BRIDGE_ENUMERATION_BEGIN")

N_enumeration = enumerate_equivariant_maps(N)
N_maps = N_enumeration["maps"]

complement_enumerations = [
    enumerate_equivariant_maps(complement)
    for complement in complements
]
complement_maps = [
    row["maps"]
    for row in complement_enumerations
]

print("BRIDGE_ENUMERATION_END")

N_map_signatures = {
    map_signature(mapping)
    for mapping in N_maps
}
complement_map_signature_sets = [
    {
        map_signature(mapping)
        for mapping in maps
    }
    for maps in complement_maps
]

complement_map_sets_equal_N = all(
    signatures == N_map_signatures
    for signatures in complement_map_signature_sets
)

bridge_rows = []
for map_index, mapping in enumerate(N_maps):
    bridge_rows.append({
        "map_index": map_index,
        "map_sha256": map_sha256(mapping),
        "rows": map_rows(mapping, map_index),
    })

sheet_reversal_failures = []
root_inversion_failures = []
reversal_pair_rows = []

for map_index, mapping in enumerate(N_maps):
    sheet_reversed = tuple(
        mapping[source_index[(source_object[0], source_object[1] ^ 1)]]
        for source_object in source_objects
    )
    root_inverted = tuple(
        inverse[root]
        for root in mapping
    )

    sheet_match_indices = [
        candidate_index
        for candidate_index, candidate in enumerate(N_maps)
        if candidate == sheet_reversed
    ]
    inverse_match_indices = [
        candidate_index
        for candidate_index, candidate in enumerate(N_maps)
        if candidate == root_inverted
    ]

    if len(sheet_match_indices) != 1:
        sheet_reversal_failures.append(map_index)
    if len(inverse_match_indices) != 1:
        root_inversion_failures.append(map_index)

    reversal_pair_rows.append({
        "map_index": map_index,
        "sheet_reversal_map_indices": sheet_match_indices,
        "root_inversion_map_indices": inverse_match_indices,
        "sheet_reversal_equals_root_inversion": (
            sheet_reversed == root_inverted
        ),
        "reversal_changes_map": sheet_reversed != mapping,
    })

reversal_relation_verified = (
    len(N_maps) == 2
    and not sheet_reversal_failures
    and not root_inversion_failures
    and all(
        row["sheet_reversal_equals_root_inversion"]
        and row["reversal_changes_map"]
        for row in reversal_pair_rows
    )
)

anchor_rows = []
for source_object in source_objects:
    duad, epsilon = source_object
    for root in pair_for_duad[duad]:
        matching_maps = [
            map_index
            for map_index, mapping in enumerate(N_maps)
            if mapping[source_index[source_object]] == root
        ]
        anchor_rows.append({
            "unordered_duad": list(duad),
            "epsilon": epsilon,
            "root": root,
            "bridge_count": len(matching_maps),
            "matching_map_indices": matching_maps,
        })

anchor_bridge_count_profile = dict(sorted(Counter(
    row["bridge_count"]
    for row in anchor_rows
).items()))

all_compatible_anchors_select_unique = (
    len(anchor_rows) == 40
    and anchor_bridge_count_profile == {1: 40}
)

prediction_matches = (
    source_action_valid
    and source_transitive
    and source_stabilizer_orders == [12]
    and source_image_orders == [6]
    and len(source_image_profiles) == 1
    and not stabilizer_match_failures
    and len(N_maps) == 2
    and reversal_relation_verified
    and all_compatible_anchors_select_unique
    and [len(maps) for maps in complement_maps] == [2, 2]
    and complement_map_sets_equal_N
)

authority_failure = (
    not all_hashes_match
    or head != "a392373 Preregister G60 parity-twisted duad cover"
    or not operation_ok
    or prereg["status"] != "frozen_before_computation"
    or stabilizer_packet["classification"]
        != "root_stabilizer_exactly_matches_even_duad_setwise_stabilizer"
    or len(S5_image) != 120
    or len(N) != 240
    or len(complements) != 2
)

if not operation_ok:
    classification = "computation_failure"
elif authority_failure:
    classification = "authority_failure"
elif not source_action_valid:
    classification = "declared_source_action_invalid"
elif not source_transitive:
    classification = "declared_source_action_not_transitive"
elif stabilizer_match_failures:
    classification = "source_and_root_stabilizers_mismatch"
elif len(N_maps) == 0:
    classification = "no_equivariant_bridge"
elif len(N_maps) == 1:
    classification = "unexpected_unique_unanchored_bridge"
elif len(N_maps) > 2:
    classification = "more_than_two_unanchored_bridges"
elif not reversal_relation_verified:
    classification = "two_bridges_not_reversal_related"
elif not all_compatible_anchors_select_unique:
    classification = "anchor_does_not_select_unique_bridge"
else:
    classification = (
        "exactly_two_inversion_related_bridges_anchor_selects_one"
    )

status_after = git("status", "--short", "--", ".")
repository_preserved = status_after == status_before

result = {
    "packet": "g60_parity_twisted_duad_cover_census_011m_candidate",
    "mode": "temporary_read_only_complete_twisted_cover_census",
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
        "group_order": len(indices),
        "identity_index": identity,
        "closure_failure_count": len(closure_failures),
        "inverse_failure_count": len(inverse_failures),
        "operation_ok": operation_ok,
        "canonical_N_order": len(N),
        "complement_count": len(complements),
        "five_point_image_order": len(S5_image),
    },
    "source_action": {
        "name": "parity_twisted_unordered_duad_double_cover",
        "object_count": len(source_objects),
        "objects": [
            {
                "source_index": index,
                "unordered_duad": list(source_object[0]),
                "epsilon": source_object[1],
            }
            for index, source_object in enumerate(source_objects)
        ],
        "identity_failure_count": len(identity_failures),
        "identity_failures": identity_failures,
        "closure_failure_count": len(closure_failures_source),
        "closure_failures": closure_failures_source,
        "action_valid": source_action_valid,
        "orbit_count": len(source_orbit_rows),
        "orbit_size_profile": sorted(
            len(orbit)
            for orbit in source_orbit_rows
        ),
        "transitive": source_transitive,
    },
    "stabilizer_comparison": {
        "source_stabilizer_order_profile": source_stabilizer_orders,
        "source_stabilizer_image_order_profile": source_image_orders,
        "source_stabilizer_image_profile_count": len(source_image_profiles),
        "rows": source_stabilizer_rows,
        "exact_match_failure_count": len(stabilizer_match_failures),
        "exact_match_failures": stabilizer_match_failures,
        "all_source_stabilizers_match_assigned_root_pair": (
            not stabilizer_match_failures
        ),
    },
    "equivariant_bridges": {
        "N_bridge_count": len(N_maps),
        "N_map_sha256s": [
            map_sha256(mapping)
            for mapping in N_maps
        ],
        "N_bridge_rows": bridge_rows,
        "N_rejected_conflict_roots": (
            N_enumeration["rejected_conflict_roots"]
        ),
        "N_rejected_incomplete_roots": (
            N_enumeration["rejected_incomplete_roots"]
        ),
        "N_rejected_nonbijective_roots": (
            N_enumeration["rejected_nonbijective_roots"]
        ),
        "N_rejected_equivariance_rows": (
            N_enumeration["rejected_equivariance_rows"]
        ),
        "complement_bridge_counts": [
            len(maps)
            for maps in complement_maps
        ],
        "complement_map_sets_equal_N": complement_map_sets_equal_N,
        "reversal_pair_rows": reversal_pair_rows,
        "sheet_reversal_failure_count": len(sheet_reversal_failures),
        "root_inversion_failure_count": len(root_inversion_failures),
        "reversal_relation_verified": reversal_relation_verified,
    },
    "anchor_ablation": {
        "compatible_anchor_count": len(anchor_rows),
        "anchor_rows": anchor_rows,
        "anchor_bridge_count_profile": anchor_bridge_count_profile,
        "all_compatible_anchors_select_unique_bridge": (
            all_compatible_anchors_select_unique
        ),
        "without_anchor_bridge_count": len(N_maps),
        "one_binary_sheet_choice_sufficient": (
            all_compatible_anchors_select_unique
            and len(N_maps) == 2
        ),
    },
    "classification": classification,
    "prediction_matches": prediction_matches,
    "earned_statement_candidate": (
        "The canonical parity-twisted double cover of the ten unordered "
        "five-point duads is a transitive twenty-object N-set whose point "
        "stabilizers agree exactly with the assigned orientation-root "
        "stabilizers. Exactly two N-equivariant bijections to the twenty "
        "roots exist. They are exchanged both by global source-sheet "
        "reversal and by root inversion. Every compatible anchored sheet "
        "choice selects exactly one bridge, and both native S5 complements "
        "recover the same two bridges."
    ),
    "boundary": {
        "replacement_source_N_set_constructed": True,
        "full_A_equivariant_source_set_constructed": False,
        "bounded_binary_datum_sufficient_within_preregistered_source_action": (
            prediction_matches
        ),
        "global_minimality_claim": False,
        "orientation_selected_without_anchor": False,
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
print("== FINAL PARITY-TWISTED DUAD COVER REPORT ==")
print("OPERATION_OK:", str(operation_ok).lower())
print("CANONICAL_N_ORDER:", len(N))
print("SOURCE_OBJECT_COUNT:", len(source_objects))
print("SOURCE_ACTION_VALID:", str(source_action_valid).lower())
print("SOURCE_ORBIT_COUNT:", len(source_orbit_rows))
print(
    "SOURCE_ORBIT_SIZE_PROFILE:",
    sorted(len(orbit) for orbit in source_orbit_rows),
)
print("SOURCE_TRANSITIVE:", str(source_transitive).lower())
print("SOURCE_STABILIZER_ORDER_PROFILE:", source_stabilizer_orders)
print("SOURCE_IMAGE_ORDER_PROFILE:", source_image_orders)
print(
    "STABILIZER_MATCH_FAILURE_COUNT:",
    len(stabilizer_match_failures),
)
print("N_BRIDGE_COUNT:", len(N_maps))
print(
    "N_MAP_SHA256S:",
    [map_sha256(mapping) for mapping in N_maps],
)
print(
    "COMPLEMENT_BRIDGE_COUNTS:",
    [len(maps) for maps in complement_maps],
)
print(
    "COMPLEMENT_MAP_SETS_EQUAL_N:",
    str(complement_map_sets_equal_N).lower(),
)
print(
    "SHEET_REVERSAL_FAILURE_COUNT:",
    len(sheet_reversal_failures),
)
print(
    "ROOT_INVERSION_FAILURE_COUNT:",
    len(root_inversion_failures),
)
print(
    "REVERSAL_RELATION_VERIFIED:",
    str(reversal_relation_verified).lower(),
)
print("COMPATIBLE_ANCHOR_COUNT:", len(anchor_rows))
print(
    "ANCHOR_BRIDGE_COUNT_PROFILE:",
    anchor_bridge_count_profile,
)
print(
    "ALL_COMPATIBLE_ANCHORS_SELECT_UNIQUE_BRIDGE:",
    str(all_compatible_anchors_select_unique).lower(),
)
print("WITHOUT_ANCHOR_BRIDGE_COUNT:", len(N_maps))
print("PREDICTION_MATCHES:", str(prediction_matches).lower())
print("CLASSIFICATION:", classification)
print(
    "REPOSITORY_STATUS_PRESERVED:",
    str(repository_preserved).lower(),
)
print("PROJECT_MUTATION_PERFORMED: false")
print("REPLACEMENT_SOURCE_N_SET_CONSTRUCTED: true")
print("ORIENTATION_SELECTED_WITHOUT_ANCHOR: false")
print("MANUSCRIPT_MUTATED: false")
print("PHYSICAL_CLAIM: false")
print("CANDIDATE_JSON:", candidate_path)
print("CANDIDATE_JSON_SHA256:", sha256(candidate_path))
