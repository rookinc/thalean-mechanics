import hashlib
import json
import subprocess
import sys
from collections import Counter, deque
from pathlib import Path

project = Path(sys.argv[1]).resolve()
candidate_path = Path(sys.argv[2]).resolve()

action_path = Path("/data/data/com.termux/files/home/dev/cori/research/mathematics/42-graph-automorphism-groups/artifacts/json/native_g60_fiber_product_isomorphism_044.json")
equivariance_path = Path("/data/data/com.termux/files/home/dev/cori/research/mathematics/42-graph-automorphism-groups/artifacts/json/native_g60_five_petersen_matching_equivariance_audit_078.json")
splitting_path = Path("/data/data/com.termux/files/home/dev/cori/research/mathematics/42-graph-automorphism-groups/artifacts/json/native_g60_s5_extension_splitting_audit_079.json")
bridge_path = project / "artifacts/json/g60_duad_orientation_bridge_census_011g.v1.json"
prereg_path = project / "artifacts/json/g60_minimal_directional_datum_preregistration_011h.v1.json"

expected_hashes = {
    str(action_path): "b37313b135495752b11e525bb61979163fdf54aec4be4f5d027dcee64c9efc21",
    str(equivariance_path): "db01304b44015a25e8f207d3fe869ad96ebcd82d3d2bd7017908a9ed7c843ec7",
    str(splitting_path): "728071622f7a6a98042a8dd4d1a6fa01cdcc8a456bd2bd5b5aadcf22965f5221",
    str(bridge_path): "abc9e038b323fdd5af852a91b87aca4c5a1e35a6e484608af27a04a399c52e9c",
    str(prereg_path): "4cd0130cb68c9df2425bdf98ae0fb109497ae98f0702b6af9274ce6ae671d003",
}

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def digest_indices(values):
    text = ",".join(str(x) for x in sorted(values))
    return hashlib.sha256(text.encode("ascii")).hexdigest()

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
splitting = json.loads(splitting_path.read_text(encoding="utf-8"))
bridge = json.loads(bridge_path.read_text(encoding="utf-8"))
prereg = json.loads(prereg_path.read_text(encoding="utf-8"))

rows = action_data["mapping_rows"]
permutations = {
    int(row["actual_index"]): tuple(int(x) for x in row["actual_permutation"])
    for row in rows
}
indices = sorted(permutations)
degree = len(permutations[0])
perm_to_index = {perm: index for index, perm in permutations.items()}
identity_perm = tuple(range(degree))
identity_candidates = [
    index for index in indices if permutations[index] == identity_perm
]
identity = identity_candidates[0] if len(identity_candidates) == 1 else None

def compose(p, q):
    return tuple(p[q[v]] for v in range(degree))

print("== G60 MINIMAL DIRECTIONAL DATUM CENSUS 011i ==")
print("MODE: temporary read-only complete ladder census")
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
if identity is not None:
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

operation_ok = (
    len(indices) == 480
    and len(perm_to_index) == 480
    and identity == 0
    and not closure_failures
    and not inverse_failures
)

def conjugate(g, h):
    return multiplication[multiplication[g][h]][inverse[g]]

def generated_subgroup(generators):
    generator_set = set(generators)
    generator_set.update(inverse[g] for g in list(generator_set))
    seen = {identity}
    queue = deque([identity])
    while queue:
        x = queue.popleft()
        for generator in generator_set:
            y = multiplication[x][generator]
            if y not in seen:
                seen.add(y)
                queue.append(y)
    return frozenset(seen)

def is_subgroup(values):
    values = set(values)
    if identity not in values:
        return False
    if any(inverse[x] not in values for x in values):
        return False
    return all(multiplication[x][y] in values for x in values for y in values)

block_rows = {
    int(row["actual_index"]): tuple(int(x) for x in row["block_image"])
    for row in equivariance["action_rows"]
}

block_consistency_failures = []
for g in indices:
    for h in indices:
        gh = multiplication[g][h]
        expected = tuple(block_rows[g][block_rows[h][i]] for i in range(5))
        if block_rows[gh] != expected:
            block_consistency_failures.append([g, h])
            break
    if block_consistency_failures:
        break

Z1 = frozenset([0, 326])
Z2 = frozenset([0, 65, 124, 326])

selected = splitting["selected_generators"]
transposition_image = tuple(int(x) for x in selected["transposition"])
five_cycle_image = tuple(int(x) for x in selected["five_cycle"])

transposition_lifts = [
    g for g in indices if block_rows[g] == transposition_image
]
five_cycle_lifts = [
    g for g in indices if block_rows[g] == five_cycle_image
]

generated_candidates = {}
pair_rows = []
for t in transposition_lifts:
    for f in five_cycle_lifts:
        subgroup = generated_subgroup([t, f])
        generated_candidates[subgroup] = True
        image_count = len({block_rows[g] for g in subgroup})
        intersection = sorted(set(subgroup) & set(Z2))
        pair_rows.append({
            "transposition_lift": t,
            "five_cycle_lift": f,
            "generated_order": len(subgroup),
            "five_point_image_order": image_count,
            "Z2_intersection": intersection,
            "is_complement": (
                len(subgroup) == 120
                and image_count == 120
                and intersection == [identity]
            ),
            "subgroup_sha256": digest_indices(subgroup),
        })

complements = sorted(
    [
        subgroup for subgroup in generated_candidates
        if len(subgroup) == 120
        and len({block_rows[g] for g in subgroup}) == 120
        and set(subgroup) & set(Z2) == {identity}
    ],
    key=lambda subgroup: tuple(sorted(subgroup)),
)

candidate_order_profile = Counter(len(group) for group in generated_candidates)

def normalizer(subgroup):
    subgroup_set = set(subgroup)
    result = []
    for g in indices:
        image = {conjugate(g, h) for h in subgroup}
        if image == subgroup_set:
            result.append(g)
    return frozenset(result)

print()
print("NORMALIZER_SCAN_BEGIN")
normalizers = []
for complement_index, complement in enumerate(complements):
    print("NORMALIZER_PROGRESS:", complement_index, "/", len(complements))
    normalizers.append(normalizer(complement))
print("NORMALIZER_PROGRESS:", len(complements), "/", len(complements))
print("NORMALIZER_SCAN_END")

normalizers_equal = (
    len(normalizers) > 0
    and all(normalizer_set == normalizers[0] for normalizer_set in normalizers)
)
common_normalizer = normalizers[0] if normalizers_equal else frozenset()
common_normalizer_is_subgroup = (
    bool(common_normalizer) and is_subgroup(common_normalizer)
)
common_normalizer_normal = (
    bool(common_normalizer)
    and all(
        {conjugate(g, h) for h in common_normalizer}
        == set(common_normalizer)
        for g in indices
    )
)

complement_lookup = {
    frozenset(complement): index
    for index, complement in enumerate(complements)
}
complement_action_failures = []
complement_action_rows = []
complement_action_kernel = []
for g in indices:
    image_indices = []
    for complement in complements:
        image = frozenset(conjugate(g, h) for h in complement)
        image_index = complement_lookup.get(image)
        if image_index is None:
            complement_action_failures.append(g)
            break
        image_indices.append(image_index)
    if len(image_indices) == len(complements):
        complement_action_rows.append({
            "element_index": g,
            "complement_image": image_indices,
        })
        if image_indices == list(range(len(complements))):
            complement_action_kernel.append(g)

complement_family_kernel = frozenset(complement_action_kernel)
family_kernel_equals_common_normalizer = (
    complement_family_kernel == common_normalizer
)

ordered_duads = tuple(
    (i, j) for i in range(5) for j in range(5) if i != j
)
inverse_pairs = tuple(
    tuple(pair)
    for pair in bridge["A_sets"]["inverse_root_pairs"]["pairs"]
)
root_indices = tuple(sorted({
    root for pair in inverse_pairs for root in pair
}))

def act_ordered(g, pair):
    return (block_rows[g][pair[0]], block_rows[g][pair[1]])

def act_root(g, root):
    return conjugate(g, root)

def enumerate_maps(group_elements):
    group_elements = tuple(sorted(group_elements))
    source = ordered_duads
    target = root_indices
    base = source[0]
    stabilizer = [
        g for g in group_elements if act_ordered(g, base) == base
    ]
    fixed_targets = [
        root for root in target
        if all(act_root(g, root) == root for g in stabilizer)
    ]
    maps = []

    for base_target in fixed_targets:
        mapping = {}
        valid = True
        for source_value in source:
            images = {
                act_root(g, base_target)
                for g in group_elements
                if act_ordered(g, base) == source_value
            }
            if len(images) != 1:
                valid = False
                break
            mapping[source_value] = next(iter(images))

        if not valid or len(set(mapping.values())) != len(target):
            continue

        if any(
            mapping[act_ordered(g, source_value)]
            != act_root(g, mapping[source_value])
            for g in group_elements
            for source_value in source
        ):
            continue

        signature = tuple(mapping[source_value] for source_value in source)
        maps.append({
            "base_source": base,
            "base_target": base_target,
            "signature": signature,
            "mapping": mapping,
        })

    maps.sort(key=lambda row: row["signature"])
    return {
        "group_order": len(group_elements),
        "source_stabilizer_order": len(stabilizer),
        "fixed_target_count": len(fixed_targets),
        "maps": maps,
    }

print()
print("BRIDGE_ENUMERATION_BEGIN")
full_A_result = enumerate_maps(indices)
print("FULL_A_ENUMERATION_COMPLETE")
N_result = enumerate_maps(common_normalizer) if common_normalizer else {
    "group_order": 0,
    "source_stabilizer_order": 0,
    "fixed_target_count": 0,
    "maps": [],
}
print("COMMON_NORMALIZER_ENUMERATION_COMPLETE")
complement_results = [
    enumerate_maps(complement) for complement in complements
]
print("COMPLEMENT_ENUMERATION_COMPLETE")
print("BRIDGE_ENUMERATION_END")

N_signatures = {
    row["signature"] for row in N_result["maps"]
}
complement_signature_sets = [
    {row["signature"] for row in result["maps"]}
    for result in complement_results
]
complement_map_sets_identical = (
    len(complement_signature_sets) == 2
    and complement_signature_sets[0] == complement_signature_sets[1]
)
complement_maps_equal_N = (
    all(signatures == N_signatures for signatures in complement_signature_sets)
    if complement_signature_sets else False
)

unordered_bridge_rows = bridge["equivariant_bridges"][
    "unordered_to_inverse_pairs"
]["rows"]
pair_for_duad = {
    tuple(row["unordered_duad"]): tuple(row["inverse_pair"])
    for row in unordered_bridge_rows
}

anchor_rows = []
for ordered_duad in ordered_duads:
    unordered_duad = tuple(sorted(ordered_duad))
    compatible_roots = pair_for_duad[unordered_duad]
    for root in compatible_roots:
        N_count = sum(
            1 for row in N_result["maps"]
            if row["mapping"][ordered_duad] == root
        )
        complement_counts = [
            sum(
                1 for row in result["maps"]
                if row["mapping"][ordered_duad] == root
            )
            for result in complement_results
        ]
        anchor_rows.append({
            "ordered_duad": list(ordered_duad),
            "root": root,
            "inverse_root": next(
                x for x in compatible_roots if x != root
            ),
            "N_bridge_count": N_count,
            "complement_bridge_counts": complement_counts,
        })

anchor_N_count_profile = dict(sorted(Counter(
    row["N_bridge_count"] for row in anchor_rows
).items()))
anchor_complement_count_profiles = []
for complement_index in range(len(complements)):
    anchor_complement_count_profiles.append(dict(sorted(Counter(
        row["complement_bridge_counts"][complement_index]
        for row in anchor_rows
    ).items())))

anchor_all_unique = (
    len(anchor_rows) == 40
    and all(row["N_bridge_count"] == 1 for row in anchor_rows)
    and all(
        all(count == 1 for count in row["complement_bridge_counts"])
        for row in anchor_rows
    )
)

reversal_inversion_failures = []
for map_index, map_row in enumerate(N_result["maps"]):
    mapping = map_row["mapping"]
    for pair in ordered_duads:
        reverse = (pair[1], pair[0])
        if mapping[reverse] != inverse[mapping[pair]]:
            reversal_inversion_failures.append([map_index, list(pair)])

two_N_maps_inverse_related = False
if len(N_result["maps"]) == 2:
    first = N_result["maps"][0]["mapping"]
    second = N_result["maps"][1]["mapping"]
    two_N_maps_inverse_related = all(
        second[pair] == inverse[first[pair]]
        for pair in ordered_duads
    )

canonical_N_exists = (
    len(complements) == 2
    and normalizers_equal
    and len(common_normalizer) == 240
    and common_normalizer_is_subgroup
    and common_normalizer_normal
    and family_kernel_equals_common_normalizer
)

authority_failure = (
    not all_hashes_match
    or head != "0f46105 Preregister G60 minimal directional datum test"
    or not operation_ok
    or block_consistency_failures
    or prereg["status"] != "frozen_before_complement_normalizer_and_anchor_census"
    or len(transposition_lifts) != 4
    or len(five_cycle_lifts) != 4
    or full_A_result["maps"]
)

computation_failure = (
    not operation_ok
    or complement_action_failures
)

if computation_failure:
    classification = "computation_failure"
elif authority_failure:
    classification = "authority_failure"
elif not canonical_N_exists:
    classification = "no_canonical_propagation_subgroup"
elif len(N_result["maps"]) == 0:
    classification = "canonical_subgroup_has_no_oriented_bridge"
elif len(N_result["maps"]) == 1:
    classification = "unexpected_unique_bridge_without_anchor"
elif len(N_result["maps"]) > 2:
    classification = "multiple_bridges_beyond_global_reversal"
elif not complement_map_sets_identical or not complement_maps_equal_N:
    classification = "complement_choice_is_load_bearing"
elif not anchor_all_unique:
    classification = "anchor_does_not_select_unique_bridge"
else:
    classification = "anchored_binary_choice_is_sufficient_without_complement_choice"

status_after = git("status", "--short", "--", ".")
repository_preserved = status_after == status_before

def serializable_map_rows(result):
    output = []
    for map_index, row in enumerate(result["maps"]):
        for pair in ordered_duads:
            output.append({
                "map_index": map_index,
                "ordered_duad": list(pair),
                "root_index": row["mapping"][pair],
            })
    return output

result = {
    "packet": "g60_minimal_directional_datum_census_011i_candidate",
    "mode": "temporary_read_only_complete_ladder_census",
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
        "block_action_consistency_failure_count": len(block_consistency_failures),
        "operation_ok": operation_ok,
    },
    "complement_reconstruction": {
        "transposition_image": list(transposition_image),
        "five_cycle_image": list(five_cycle_image),
        "transposition_lift_count": len(transposition_lifts),
        "five_cycle_lift_count": len(five_cycle_lifts),
        "lift_pair_count": len(pair_rows),
        "distinct_generated_subgroup_count": len(generated_candidates),
        "generated_subgroup_order_profile": dict(sorted(candidate_order_profile.items())),
        "complement_count": len(complements),
        "complement_rows": [
            {
                "complement_index": index,
                "order": len(complement),
                "member_indices": sorted(complement),
                "member_indices_sha256": digest_indices(complement),
                "normalizer_order": len(normalizers[index]),
                "normalizer_indices_sha256": digest_indices(normalizers[index]),
            }
            for index, complement in enumerate(complements)
        ],
        "complement_conjugacy_action_failure_count": len(complement_action_failures),
    },
    "canonical_propagation_subgroup": {
        "exists": canonical_N_exists,
        "definition": "kernel_of_A_action_on_complete_unordered_complement_family",
        "order": len(common_normalizer),
        "index_in_A": (
            len(indices) // len(common_normalizer)
            if common_normalizer else None
        ),
        "member_indices": sorted(common_normalizer),
        "member_indices_sha256": (
            digest_indices(common_normalizer)
            if common_normalizer else None
        ),
        "normalizers_equal": normalizers_equal,
        "is_subgroup": common_normalizer_is_subgroup,
        "is_normal": common_normalizer_normal,
        "family_kernel_equals_common_normalizer": family_kernel_equals_common_normalizer,
        "intersection_Z2": sorted(set(common_normalizer) & set(Z2)),
    },
    "bridge_counts": {
        "full_A": {
            "group_order": full_A_result["group_order"],
            "bridge_count": len(full_A_result["maps"]),
        },
        "canonical_N": {
            "group_order": N_result["group_order"],
            "source_stabilizer_order": N_result["source_stabilizer_order"],
            "fixed_target_count": N_result["fixed_target_count"],
            "bridge_count": len(N_result["maps"]),
            "map_rows": serializable_map_rows(N_result),
        },
        "complements": [
            {
                "complement_index": index,
                "group_order": item["group_order"],
                "source_stabilizer_order": item["source_stabilizer_order"],
                "fixed_target_count": item["fixed_target_count"],
                "bridge_count": len(item["maps"]),
                "map_signature_sha256": hashlib.sha256(
                    repr(sorted(row["signature"] for row in item["maps"])).encode("ascii")
                ).hexdigest(),
            }
            for index, item in enumerate(complement_results)
        ],
        "complement_map_sets_identical": complement_map_sets_identical,
        "complement_maps_equal_N": complement_maps_equal_N,
        "two_N_maps_inverse_related": two_N_maps_inverse_related,
        "reversal_inversion_failure_count": len(reversal_inversion_failures),
    },
    "anchor_ablation": {
        "compatible_anchor_count": len(anchor_rows),
        "anchor_rows": anchor_rows,
        "N_anchor_bridge_count_profile": anchor_N_count_profile,
        "complement_anchor_bridge_count_profiles": anchor_complement_count_profiles,
        "all_compatible_anchors_select_unique_bridge": anchor_all_unique,
        "without_anchor_N_bridge_count": len(N_result["maps"]),
        "anchor_root_choice_cardinality": 2,
        "one_bit_description_earned": (
            anchor_all_unique
            and len(N_result["maps"]) == 2
            and two_N_maps_inverse_related
        ),
    },
    "prediction": {
        "prediction_matches": (
            canonical_N_exists
            and len(N_result["maps"]) == 2
            and all(len(item["maps"]) == 2 for item in complement_results)
            and complement_map_sets_identical
            and complement_maps_equal_N
            and anchor_all_unique
        ),
    },
    "classification": classification,
    "boundary": {
        "minimality_scope": "frozen_D0_to_D4_candidate_ladder_only",
        "global_information_theoretic_minimality": False,
        "orientation_selected_without_added_anchor": False,
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
print("== FINAL MINIMAL DIRECTIONAL DATUM REPORT ==")
print("OPERATION_OK:", str(operation_ok).lower())
print("TRANSPOSTION_LIFT_COUNT:", len(transposition_lifts))
print("FIVE_CYCLE_LIFT_COUNT:", len(five_cycle_lifts))
print("LIFT_PAIR_COUNT:", len(pair_rows))
print("GENERATED_SUBGROUP_ORDER_PROFILE:", dict(sorted(candidate_order_profile.items())))
print("COMPLEMENT_COUNT:", len(complements))
print("COMPLEMENT_NORMALIZER_ORDERS:", [len(x) for x in normalizers])
print("NORMALIZERS_EQUAL:", str(normalizers_equal).lower())
print("COMPLEMENT_FAMILY_KERNEL_ORDER:", len(complement_family_kernel))
print("COMMON_NORMALIZER_ORDER:", len(common_normalizer))
print("COMMON_NORMALIZER_INDEX:", len(indices) // len(common_normalizer) if common_normalizer else None)
print("COMMON_NORMALIZER_NORMAL:", str(common_normalizer_normal).lower())
print("COMMON_NORMALIZER_INTERSECTION_Z2:", sorted(set(common_normalizer) & set(Z2)))
print("CANONICAL_PROPAGATION_SUBGROUP_EXISTS:", str(canonical_N_exists).lower())
print("FULL_A_BRIDGE_COUNT:", len(full_A_result["maps"]))
print("N_BRIDGE_COUNT:", len(N_result["maps"]))
print("COMPLEMENT_BRIDGE_COUNTS:", [len(x["maps"]) for x in complement_results])
print("COMPLEMENT_MAP_SETS_IDENTICAL:", str(complement_map_sets_identical).lower())
print("COMPLEMENT_MAPS_EQUAL_N:", str(complement_maps_equal_N).lower())
print("TWO_N_MAPS_INVERSE_RELATED:", str(two_N_maps_inverse_related).lower())
print("REVERSAL_INVERSION_FAILURE_COUNT:", len(reversal_inversion_failures))
print("COMPATIBLE_ANCHOR_COUNT:", len(anchor_rows))
print("N_ANCHOR_BRIDGE_COUNT_PROFILE:", anchor_N_count_profile)
print("COMPLEMENT_ANCHOR_BRIDGE_COUNT_PROFILES:", anchor_complement_count_profiles)
print("ALL_COMPATIBLE_ANCHORS_SELECT_UNIQUE_BRIDGE:", str(anchor_all_unique).lower())
print("WITHOUT_ANCHOR_N_BRIDGE_COUNT:", len(N_result["maps"]))
print("ONE_BIT_DESCRIPTION_EARNED:", str(result["anchor_ablation"]["one_bit_description_earned"]).lower())
print("PREDICTION_MATCHES:", str(result["prediction"]["prediction_matches"]).lower())
print("CLASSIFICATION:", classification)
print("REPOSITORY_STATUS_PRESERVED:", str(repository_preserved).lower())
print("PROJECT_MUTATION_PERFORMED: false")
print("ORIENTATION_SELECTED_WITHOUT_ADDED_ANCHOR: false")
print("MANUSCRIPT_MUTATED: false")
print("PHYSICAL_CLAIM: false")
print("CANDIDATE_JSON:", candidate_path)
print("CANDIDATE_JSON_SHA256:", sha256(candidate_path))
