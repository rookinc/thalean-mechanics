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
prereg_path = project / "artifacts/json/g60_root_stabilizer_action_type_preregistration_011j.v1.json"

expected_hashes = {
    str(action_path): "b37313b135495752b11e525bb61979163fdf54aec4be4f5d027dcee64c9efc21",
    str(equivariance_path): "db01304b44015a25e8f207d3fe869ad96ebcd82d3d2bd7017908a9ed7c843ec7",
    str(bridge_path): "abc9e038b323fdd5af852a91b87aca4c5a1e35a6e484608af27a04a399c52e9c",
    str(minimal_path): "6d7164f98d686dc9d54b8146f19ab56c22c8aa70009f65bbcad7c7c88e9b962d",
    str(prereg_path): "3e87e98d4d1095a1aa3188d442fe77b18ec5611f3786c3257f4ce80ec13459c8",
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

print("== G60 ROOT STABILIZER ACTION-TYPE CENSUS 011k ==")
print("MODE: temporary read-only complete stabilizer census")
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

print()
print("STABILIZER_CENSUS_BEGIN")

N_root_rows = []
N_ordered_rows = []
complement_root_rows = []
complement_ordered_rows = []

for row_number, root in enumerate(roots):
    if row_number % 5 == 0:
        print("ROOT_STABILIZER_PROGRESS:", row_number, "/", len(roots))
    stabilizer = root_stabilizer(N, root)
    image = projected(stabilizer)
    N_root_rows.append({
        "root": root,
        "assigned_unordered_duad": list(duad_for_root[root]),
        "stabilizer_order": len(stabilizer),
        "image_profile": image_profile(image),
        "image": [list(perm) for perm in sorted(image)],
    })
    for complement_index, complement in enumerate(complements):
        stabilizer_H = root_stabilizer(complement, root)
        image_H = projected(stabilizer_H)
        complement_root_rows.append({
            "complement_index": complement_index,
            "root": root,
            "assigned_unordered_duad": list(duad_for_root[root]),
            "stabilizer_order": len(stabilizer_H),
            "image_profile": image_profile(image_H),
            "image": [list(perm) for perm in sorted(image_H)],
        })

print("ROOT_STABILIZER_PROGRESS:", len(roots), "/", len(roots))

for duad in ordered_duads:
    stabilizer = ordered_stabilizer(N, duad)
    image = projected(stabilizer)
    N_ordered_rows.append({
        "ordered_duad": list(duad),
        "stabilizer_order": len(stabilizer),
        "image_profile": image_profile(image),
        "image": [list(perm) for perm in sorted(image)],
    })
    for complement_index, complement in enumerate(complements):
        stabilizer_H = ordered_stabilizer(complement, duad)
        image_H = projected(stabilizer_H)
        complement_ordered_rows.append({
            "complement_index": complement_index,
            "ordered_duad": list(duad),
            "stabilizer_order": len(stabilizer_H),
            "image_profile": image_profile(image_H),
            "image": [list(perm) for perm in sorted(image_H)],
        })

print("STABILIZER_CENSUS_END")

even_duad_rows = []
for duad in unordered_duads:
    subgroup = even_duad_setwise_stabilizer(duad)
    even_duad_rows.append({
        "unordered_duad": list(duad),
        "profile": image_profile(subgroup),
        "image": [list(perm) for perm in sorted(subgroup)],
    })

def image_key(row):
    return frozenset(tuple(perm) for perm in row["image"])

N_root_images = {image_key(row) for row in N_root_rows}
N_ordered_images = {image_key(row) for row in N_ordered_rows}
complement_root_images = {
    image_key(row) for row in complement_root_rows
}
complement_ordered_images = {
    image_key(row) for row in complement_ordered_rows
}
even_duad_images = {image_key(row) for row in even_duad_rows}

N_exact_match_failures = []
for row in N_root_rows:
    expected = even_duad_setwise_stabilizer(
        tuple(row["assigned_unordered_duad"])
    )
    if image_key(row) != expected:
        N_exact_match_failures.append(row["root"])

complement_exact_match_failures = []
for row in complement_root_rows:
    expected = even_duad_setwise_stabilizer(
        tuple(row["assigned_unordered_duad"])
    )
    if image_key(row) != expected:
        complement_exact_match_failures.append([
            row["complement_index"], row["root"]
        ])

root_profiles = {
    json.dumps(row["image_profile"], sort_keys=True)
    for row in N_root_rows + complement_root_rows
}
ordered_profiles = {
    json.dumps(row["image_profile"], sort_keys=True)
    for row in N_ordered_rows + complement_ordered_rows
}
even_profiles = {
    json.dumps(row["profile"], sort_keys=True)
    for row in even_duad_rows
}

root_profile_uniform = len(root_profiles) == 1
ordered_profile_uniform = len(ordered_profiles) == 1
even_profile_uniform = len(even_profiles) == 1

root_profile = N_root_rows[0]["image_profile"]
ordered_profile = N_ordered_rows[0]["image_profile"]
even_profile = even_duad_rows[0]["profile"]

same_abstract_profile = (
    root_profile["element_order_profile"]
    == ordered_profile["element_order_profile"]
)
representative_conjugate = subgroup_conjugate_in_S5(
    image_key(N_root_rows[0]),
    image_key(N_ordered_rows[0]),
)

exact_even_match = (
    not N_exact_match_failures
    and not complement_exact_match_failures
    and N_root_images == even_duad_images
    and complement_root_images == even_duad_images
)

mixed_profiles = not (
    root_profile_uniform
    and ordered_profile_uniform
    and even_profile_uniform
)

authority_failure = (
    not all_hashes_match
    or head != "ea06a19 Preregister G60 root stabilizer action type"
    or not operation_ok
    or prereg["status"] != "frozen_before_root_stabilizer_action_type_census"
    or len(S5_image) != 120
    or len(N) != 240
    or len(complements) != 2
)

if not operation_ok:
    classification = "computation_failure"
elif authority_failure:
    classification = "authority_failure"
elif mixed_profiles:
    classification = "mixed_or_nonuniform_stabilizer_profiles"
elif representative_conjugate:
    classification = "same_stabilizer_conjugacy_class"
elif not same_abstract_profile:
    classification = "different_abstract_stabilizer_types"
elif exact_even_match:
    classification = "root_stabilizer_exactly_matches_even_duad_setwise_stabilizer"
else:
    classification = "same_abstract_type_nonconjugate_embedding"

status_after = git("status", "--short", "--", ".")
repository_preserved = status_after == status_before

result = {
    "packet": "g60_root_stabilizer_action_type_census_011k_candidate",
    "mode": "temporary_read_only_complete_stabilizer_census",
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
        "five_point_image_order": len(S5_image),
    },
    "uniform_profiles": {
        "root_profile_uniform": root_profile_uniform,
        "ordered_duad_profile_uniform": ordered_profile_uniform,
        "even_duad_profile_uniform": even_profile_uniform,
        "root_profile": root_profile,
        "ordered_duad_profile": ordered_profile,
        "even_duad_profile": even_profile,
        "same_abstract_element_order_profile": same_abstract_profile,
        "root_and_ordered_stabilizers_conjugate_in_S5": representative_conjugate,
    },
    "stabilizer_census": {
        "N_root_row_count": len(N_root_rows),
        "N_ordered_duad_row_count": len(N_ordered_rows),
        "complement_root_row_count": len(complement_root_rows),
        "complement_ordered_duad_row_count": len(complement_ordered_rows),
        "distinct_N_root_image_count": len(N_root_images),
        "distinct_N_ordered_image_count": len(N_ordered_images),
        "distinct_complement_root_image_count": len(complement_root_images),
        "distinct_complement_ordered_image_count": len(complement_ordered_images),
        "distinct_even_duad_image_count": len(even_duad_images),
        "N_root_rows": N_root_rows,
        "N_ordered_rows": N_ordered_rows,
        "complement_root_rows": complement_root_rows,
        "complement_ordered_rows": complement_ordered_rows,
        "even_duad_rows": even_duad_rows,
    },
    "exact_even_duad_comparison": {
        "N_exact_match_failure_count": len(N_exact_match_failures),
        "N_exact_match_failures": N_exact_match_failures,
        "complement_exact_match_failure_count": len(complement_exact_match_failures),
        "complement_exact_match_failures": complement_exact_match_failures,
        "N_root_image_family_equals_even_duad_family": N_root_images == even_duad_images,
        "complement_root_image_family_equals_even_duad_family": complement_root_images == even_duad_images,
        "exact_even_match": exact_even_match,
    },
    "classification": classification,
    "prediction_matches": (
        classification
        == "root_stabilizer_exactly_matches_even_duad_setwise_stabilizer"
    ),
    "boundary": {
        "classification_only": True,
        "replacement_source_A_set_constructed": False,
        "new_selector_searched": False,
        "minimal_directional_datum_identified": False,
        "orientation_selected": False,
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
print("== FINAL ROOT STABILIZER ACTION-TYPE REPORT ==")
print("OPERATION_OK:", str(operation_ok).lower())
print("FIVE_POINT_IMAGE_ORDER:", len(S5_image))
print("ROOT_PROFILE_UNIFORM:", str(root_profile_uniform).lower())
print("ORDERED_DUAD_PROFILE_UNIFORM:", str(ordered_profile_uniform).lower())
print("ROOT_STABILIZER_PROFILE:", root_profile)
print("ORDERED_DUAD_STABILIZER_PROFILE:", ordered_profile)
print("EVEN_DUAD_STABILIZER_PROFILE:", even_profile)
print("SAME_ABSTRACT_ELEMENT_ORDER_PROFILE:", str(same_abstract_profile).lower())
print("ROOT_AND_ORDERED_CONJUGATE_IN_S5:", str(representative_conjugate).lower())
print("DISTINCT_ROOT_STABILIZER_IMAGE_COUNT:", len(N_root_images))
print("DISTINCT_ORDERED_STABILIZER_IMAGE_COUNT:", len(N_ordered_images))
print("DISTINCT_EVEN_DUAD_STABILIZER_IMAGE_COUNT:", len(even_duad_images))
print("N_EXACT_EVEN_DUAD_MATCH_FAILURE_COUNT:", len(N_exact_match_failures))
print("COMPLEMENT_EXACT_EVEN_DUAD_MATCH_FAILURE_COUNT:", len(complement_exact_match_failures))
print("ROOT_IMAGE_FAMILY_EQUALS_EVEN_DUAD_FAMILY:", str(N_root_images == even_duad_images).lower())
print("EXACT_EVEN_DUAD_MATCH:", str(exact_even_match).lower())
print("PREDICTION_MATCHES:", str(result["prediction_matches"]).lower())
print("CLASSIFICATION:", classification)
print("REPOSITORY_STATUS_PRESERVED:", str(repository_preserved).lower())
print("PROJECT_MUTATION_PERFORMED: false")
print("REPLACEMENT_SOURCE_A_SET_CONSTRUCTED: false")
print("ORIENTATION_SELECTED: false")
print("MANUSCRIPT_MUTATED: false")
print("PHYSICAL_CLAIM: false")
print("CANDIDATE_JSON:", candidate_path)
print("CANDIDATE_JSON_SHA256:", sha256(candidate_path))
