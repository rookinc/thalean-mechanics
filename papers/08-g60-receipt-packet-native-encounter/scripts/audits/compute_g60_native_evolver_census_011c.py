import csv
import hashlib
import json
import subprocess
import sys
from array import array
from collections import Counter, deque
from datetime import datetime
from pathlib import Path

project = Path(sys.argv[1]).resolve()
output_path = Path(sys.argv[2]).resolve()

action_path = Path(
    "/data/data/com.termux/files/home/dev/cori/research/mathematics/"
    "42-graph-automorphism-groups/artifacts/json/"
    "native_g60_fiber_product_isomorphism_044.json"
)
edge_path = Path(
    "/data/data/com.termux/files/home/dev/cori/research/physics/"
    "quantum_mechanics/01-the-electron-spins-twice/paper/data/"
    "g60_local_edges.csv"
)
phase_a_path = (
    project
    / "artifacts/json"
    / "g60_upper_central_series_blind_census_010b.v1.json"
)
prereg_path = (
    project
    / "artifacts/json"
    / "g60_native_evolver_candidate_preregistration_011b.v1.json"
)

expected_hashes = {
    "action": "b37313b135495752b11e525bb61979163fdf54aec4be4f5d027dcee64c9efc21",
    "edges": "c700a185fab6a5f434da09b7acb716b96c76170774bee946af8ea907e4fe7f9f",
    "phase_a": "6c69d4e6c6a5eca1c5b7d15840a8958cc93eff5a13c1fe62a8840fe2bf0e8f26",
    "prereg": "ee8ed4313bdbb18081a85f9de1e648536106b16fbeee7e49a6a482889d18100a",
}

def sha256_file(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def git_output(*args):
    result = subprocess.run(
        ["git", "-C", str(project), *args],
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout.rstrip("\n")

def status_hash(text):
    return hashlib.sha256((text + "\n").encode("utf-8")).hexdigest()

def compose(p, q):
    return tuple(p[q[v]] for v in range(60))

def inverse_permutation(p):
    inverse = [None] * 60
    for vertex, image in enumerate(p):
        inverse[image] = vertex
    return tuple(inverse)

def profile(values):
    return {
        str(key): count
        for key, count in sorted(Counter(values).items())
    }

status_before = git_output("status", "--short")
head_before = git_output("--no-pager", "show", "-s", "--oneline", "HEAD")

actual_hashes = {
    "action": sha256_file(action_path),
    "edges": sha256_file(edge_path),
    "phase_a": sha256_file(phase_a_path),
    "prereg": sha256_file(prereg_path),
}

phase_a = json.loads(phase_a_path.read_text(encoding="utf-8"))
prereg = json.loads(prereg_path.read_text(encoding="utf-8"))
action = json.loads(action_path.read_text(encoding="utf-8"))

rows = sorted(action["mapping_rows"], key=lambda row: row["actual_index"])
permutations = [tuple(row["actual_permutation"]) for row in rows]
declared_orders = [row["actual_order"] for row in rows]
group_order = len(permutations)
perm_to_index = {
    permutation: index
    for index, permutation in enumerate(permutations)
}

identity_permutation = tuple(range(60))
identity = perm_to_index.get(identity_permutation)
sentinel = 65535

print("== G60 NATIVE EVOLVER CENSUS 011c ==")
print("MODE: temporary read-only native group census")
print("LOCKED_HEAD:", head_before)
print("ACTION_SHA256:", actual_hashes["action"])
print("RAW_EDGE_SHA256:", actual_hashes["edges"])
print("PHASE_A_SHA256:", actual_hashes["phase_a"])
print("PREREGISTRATION_SHA256:", actual_hashes["prereg"])
print("GROUP_ORDER:", group_order)
print("IDENTITY_INDEX:", identity)
print()

multiplication = []
closure_failure_count = 0

print("MULTIPLICATION_BEGIN")
for left in range(group_order):
    if left % 40 == 0:
        print("MULTIPLICATION_PROGRESS:", left, "/", group_order)
    p = permutations[left]
    result_row = array("H")
    for right in range(group_order):
        product = perm_to_index.get(compose(p, permutations[right]))
        if product is None:
            closure_failure_count += 1
            result_row.append(sentinel)
        else:
            result_row.append(product)
    multiplication.append(result_row)
print("MULTIPLICATION_PROGRESS:", group_order, "/", group_order)
print("MULTIPLICATION_END")
print()

inverse_indices = [None] * group_order
inverse_failures = []

if closure_failure_count == 0 and identity is not None:
    for index, permutation in enumerate(permutations):
        inverse_index = perm_to_index.get(inverse_permutation(permutation))
        inverse_indices[index] = inverse_index
        if (
            inverse_index is None
            or multiplication[index][inverse_index] != identity
            or multiplication[inverse_index][index] != identity
        ):
            inverse_failures.append(index)

def power_index(element, exponent):
    result = identity
    base = element
    n = exponent
    while n:
        if n & 1:
            result = multiplication[result][base]
        base = multiplication[base][base]
        n >>= 1
    return result

def element_order(element):
    current = identity
    for exponent in range(1, group_order + 1):
        current = multiplication[current][element]
        if current == identity:
            return exponent
    return None

computed_orders = []
order_failures = []

if not inverse_failures and closure_failure_count == 0:
    for index in range(group_order):
        order = element_order(index)
        computed_orders.append(order)
        if order != declared_orders[index]:
            order_failures.append(
                [index, declared_orders[index], order]
            )

z1 = sorted(phase_a["central_series"]["center_member_indices"])
z2 = sorted(phase_a["central_series"]["second_center_member_indices"])
z1_set = set(z1)
z2_set = set(z2)
tau_candidates = [element for element in z1 if element != identity]
tau = tau_candidates[0] if len(tau_candidates) == 1 else None
outer_pair = sorted(z2_set - z1_set)

def conjugate(h, x):
    return multiplication[multiplication[h][x]][inverse_indices[h]]

def cyclic_subgroup(h):
    members = set()
    current = identity
    while current not in members:
        members.add(current)
        current = multiplication[current][h]
    return members

operation_ok = (
    head_before.startswith("da2bb02 ")
    and actual_hashes == expected_hashes
    and group_order == 480
    and len(perm_to_index) == 480
    and identity is not None
    and closure_failure_count == 0
    and not inverse_failures
    and not order_failures
    and len(tau_candidates) == 1
    and len(outer_pair) == 2
    and prereg["preregistration_status"]
        == "frozen_before_native_element_census"
)

u0 = []
u1 = []
u2 = []
intersection_by_element = {}
outer_action_by_element = {}

if operation_ok:
    print("CANDIDATE_SCAN_BEGIN")
    for h in range(group_order):
        if h % 80 == 0:
            print("CANDIDATE_PROGRESS:", h, "/", group_order)

        if computed_orders[h] != 8:
            continue
        if power_index(h, 4) != tau:
            continue
        u0.append(h)

        images = [conjugate(h, x) for x in outer_pair]
        outer_action_by_element[str(h)] = images
        if images != list(reversed(outer_pair)):
            continue
        u1.append(h)

        intersection = sorted(cyclic_subgroup(h) & z2_set)
        intersection_by_element[str(h)] = intersection
        if intersection != z1:
            continue
        u2.append(h)

    print("CANDIDATE_PROGRESS:", group_order, "/", group_order)
    print("CANDIDATE_SCAN_END")
    print()

u2_set = set(u2)
inverse_closure_failures = [
    h for h in u2
    if inverse_indices[h] not in u2_set
]
self_inverse_members = [
    h for h in u2
    if inverse_indices[h] == h
]

inverse_pairs = sorted({
    tuple(sorted((h, inverse_indices[h])))
    for h in u2
})
pair_set = set(inverse_pairs)

def conjugacy_orbits(elements):
    remaining = set(elements)
    orbits = []
    while remaining:
        seed = min(remaining)
        orbit = {
            conjugate(g, seed)
            for g in range(group_order)
        }
        orbit &= set(elements)
        orbits.append(sorted(orbit))
        remaining.difference_update(orbit)
    return sorted(orbits, key=lambda orbit: (len(orbit), orbit))

def conjugate_pair(g, pair):
    return tuple(sorted((
        conjugate(g, pair[0]),
        conjugate(g, pair[1]),
    )))

def pair_conjugacy_orbits(pairs):
    remaining = set(pairs)
    orbits = []
    while remaining:
        seed = min(remaining)
        orbit = {
            conjugate_pair(g, seed)
            for g in range(group_order)
        }
        orbit &= set(pairs)
        orbits.append(sorted([list(pair) for pair in orbit]))
        remaining.difference_update(orbit)
    return sorted(orbits, key=lambda orbit: (len(orbit), orbit))

u2_conjugacy_orbits = conjugacy_orbits(u2) if u2 else []
pair_orbits = pair_conjugacy_orbits(inverse_pairs) if inverse_pairs else []

involutions = [
    element for element in range(group_order)
    if computed_orders and computed_orders[element] == 2
]

def generated_subgroup(generators):
    generators = set(generators)
    generators.update(inverse_indices[g] for g in list(generators))
    reached = {identity}
    queue = deque([identity])
    while queue:
        current = queue.popleft()
        for generator in generators:
            candidate = multiplication[current][generator]
            if candidate not in reached:
                reached.add(candidate)
                queue.append(candidate)
    return reached

reversal_witnesses = {}
generated_order_profile_values = []
missing_reversal_witnesses = []

print("REVERSAL_WITNESS_SCAN_BEGIN")
for position, h in enumerate(u2):
    if position % 20 == 0:
        print("REVERSAL_PROGRESS:", position, "/", len(u2))

    inverse_h = inverse_indices[h]
    witnesses = []
    witness_order_profile = Counter()

    for s in involutions:
        if multiplication[multiplication[s][h]][s] != inverse_h:
            continue
        generated_order = len(generated_subgroup([h, s]))
        witnesses.append(s)
        witness_order_profile[generated_order] += 1
        generated_order_profile_values.append(generated_order)

    reversal_witnesses[str(h)] = {
        "inverse_index": inverse_h,
        "witness_count": len(witnesses),
        "witness_indices": witnesses,
        "generated_subgroup_order_profile": {
            str(key): value
            for key, value in sorted(witness_order_profile.items())
        },
    }

    if not witnesses:
        missing_reversal_witnesses.append(h)

print("REVERSAL_PROGRESS:", len(u2), "/", len(u2))
print("REVERSAL_WITNESS_SCAN_END")
print()

with edge_path.open("r", encoding="utf-8", newline="") as handle:
    edges = [
        tuple(sorted((int(row["local_u"]), int(row["local_v"]))))
        for row in csv.DictReader(handle)
    ]

fixed_point_counts = {}
edge_inversion_counts = {}

for h in u2:
    fixed_point_counts[str(h)] = sum(
        permutations[h][vertex] == vertex
        for vertex in range(60)
    )
    edge_inversion_counts[str(h)] = sum(
        permutations[h][u] == v
        and permutations[h][v] == u
        for u, v in edges
    )

if not operation_ok:
    classification = "computation_failure"
elif not u2:
    classification = "no_exact_evolver_candidate"
elif len(self_inverse_members) == len(u2):
    classification = "self_inverse_collapse"
elif len(inverse_pairs) > 1:
    classification = "multiple_reversal_orbits"
elif len(inverse_pairs) == 1 and not missing_reversal_witnesses:
    classification = "exact_reversal_obstruction"
elif len(u2) == 1 and missing_reversal_witnesses:
    classification = "unique_orientation_selected"
else:
    classification = "unclassified_frozen_outcome_gap"

local_reversal_obstruction_verified = (
    bool(u2)
    and not self_inverse_members
    and not missing_reversal_witnesses
)

status_after = git_output("status", "--short")
head_after = git_output("--no-pager", "show", "-s", "--oneline", "HEAD")
repository_preserved = (
    status_before == status_after
    and head_before == head_after
)

result = {
    "packet": "g60_native_evolver_census_011c",
    "version": 1,
    "created_at": datetime.now().astimezone().isoformat(),
    "mode": "temporary_read_only_native_group_census",
    "authorities": {
        name: {
            "actual_sha256": actual_hashes[name],
            "expected_sha256": expected_hashes[name],
            "hash_match": actual_hashes[name] == expected_hashes[name],
        }
        for name in expected_hashes
    },
    "group_reconstruction": {
        "group_order": group_order,
        "identity_index": identity,
        "closure_failure_count": closure_failure_count,
        "inverse_failure_count": len(inverse_failures),
        "declared_order_failure_count": len(order_failures),
        "operation_ok": operation_ok,
    },
    "native_tower": {
        "Z1_member_indices": z1,
        "Z2_member_indices": z2,
        "tau_index": tau,
        "outer_pair_indices": outer_pair,
    },
    "candidate_census": {
        "U0_count": len(u0),
        "U0_member_indices": u0,
        "U1_count": len(u1),
        "U1_member_indices": u1,
        "U2_count": len(u2),
        "U2_member_indices": u2,
        "U2_inverse_closure_failure_count": len(inverse_closure_failures),
        "U2_inverse_closure_failures": inverse_closure_failures,
        "U2_self_inverse_count": len(self_inverse_members),
        "U2_self_inverse_members": self_inverse_members,
        "U2_inverse_pair_count": len(inverse_pairs),
        "U2_inverse_pairs": [list(pair) for pair in inverse_pairs],
        "U2_element_conjugacy_orbit_count": len(u2_conjugacy_orbits),
        "U2_element_conjugacy_orbits": u2_conjugacy_orbits,
        "U2_pair_conjugacy_orbit_count": len(pair_orbits),
        "U2_pair_conjugacy_orbits": pair_orbits,
        "cyclic_intersections_with_Z2": intersection_by_element,
        "outer_pair_actions": outer_action_by_element,
    },
    "reversal_witness_census": {
        "involution_count_in_A": len(involutions),
        "all_U2_elements_have_involutive_reverser": (
            bool(u2) and not missing_reversal_witnesses
        ),
        "missing_reversal_witness_count": len(missing_reversal_witnesses),
        "missing_reversal_witness_members": missing_reversal_witnesses,
        "witnesses_by_element": reversal_witnesses,
        "all_generated_subgroup_order_profile": profile(
            generated_order_profile_values
        ),
        "local_reversal_obstruction_verified": (
            local_reversal_obstruction_verified
        ),
    },
    "native_action_profile": {
        "fixed_point_count_profile": profile(fixed_point_counts.values()),
        "fixed_point_counts_by_element": fixed_point_counts,
        "edge_inversion_count_profile": profile(
            edge_inversion_counts.values()
        ),
        "edge_inversion_counts_by_element": edge_inversion_counts,
    },
    "classification": {
        "frozen_outcome": classification,
        "primary_family": "U2",
        "fallback_to_U0_or_U1_used": False,
        "replacement_selector_used": False,
    },
    "repository_preservation": {
        "head_before": head_before,
        "head_after": head_after,
        "status_before_sha256": status_hash(status_before),
        "status_after_sha256": status_hash(status_after),
        "repository_status_preserved": repository_preserved,
        "project_mutation_performed": False,
    },
    "boundary": {
        "candidate_report_only": True,
        "result_frozen": False,
        "native_evolver_uniquely_selected": classification == "unique_orientation_selected",
        "one_inverse_pair_selected": len(inverse_pairs) == 1,
        "multiple_inverse_pairs": len(inverse_pairs) > 1,
        "local_reversal_obstruction_verified": local_reversal_obstruction_verified,
        "minimal_directional_datum_identified": False,
        "manuscript_mutated": False,
        "geometry_claim": False,
        "physical_claim": False,
    },
}

output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(
    json.dumps(result, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

print("== FINAL NATIVE EVOLVER CENSUS ==")
print("ALL_AUTHORITY_HASHES_MATCH:", str(actual_hashes == expected_hashes).lower())
print("OPERATION_OK:", str(operation_ok).lower())
print("CLOSURE_FAILURE_COUNT:", closure_failure_count)
print("INVERSE_FAILURE_COUNT:", len(inverse_failures))
print("DECLARED_ORDER_FAILURE_COUNT:", len(order_failures))
print("Z1_MEMBER_INDICES:", z1)
print("Z2_MEMBER_INDICES:", z2)
print("TAU_INDEX:", tau)
print("OUTER_PAIR_INDICES:", outer_pair)
print("U0_COUNT:", len(u0))
print("U1_COUNT:", len(u1))
print("U2_COUNT:", len(u2))
print("U2_MEMBER_INDICES:", u2)
print("U2_INVERSE_CLOSURE_FAILURE_COUNT:", len(inverse_closure_failures))
print("U2_SELF_INVERSE_COUNT:", len(self_inverse_members))
print("U2_INVERSE_PAIR_COUNT:", len(inverse_pairs))
print("U2_INVERSE_PAIRS:", [list(pair) for pair in inverse_pairs])
print("U2_ELEMENT_CONJUGACY_ORBIT_COUNT:", len(u2_conjugacy_orbits))
print("U2_ELEMENT_CONJUGACY_ORBIT_SIZE_PROFILE:", profile(len(orbit) for orbit in u2_conjugacy_orbits))
print("U2_PAIR_CONJUGACY_ORBIT_COUNT:", len(pair_orbits))
print("U2_PAIR_CONJUGACY_ORBIT_SIZE_PROFILE:", profile(len(orbit) for orbit in pair_orbits))
print("INVOLUTION_COUNT_IN_A:", len(involutions))
print("MISSING_REVERSAL_WITNESS_COUNT:", len(missing_reversal_witnesses))
print("ALL_U2_HAVE_INVOLUTIVE_REVERSER:", str(bool(u2) and not missing_reversal_witnesses).lower())
print("REVERSER_GENERATED_SUBGROUP_ORDER_PROFILE:", profile(generated_order_profile_values))
print("U2_FIXED_POINT_COUNT_PROFILE:", profile(fixed_point_counts.values()))
print("U2_EDGE_INVERSION_COUNT_PROFILE:", profile(edge_inversion_counts.values()))
print("LOCAL_REVERSAL_OBSTRUCTION_VERIFIED:", str(local_reversal_obstruction_verified).lower())
print("FROZEN_OUTCOME_CLASSIFICATION:", classification)
print("FALLBACK_TO_U0_OR_U1_USED: false")
print("REPLACEMENT_SELECTOR_USED: false")
print("REPOSITORY_STATUS_PRESERVED:", str(repository_preserved).lower())
print("PROJECT_MUTATION_PERFORMED: false")
print("RESULT_FROZEN: false")
print("MINIMAL_DIRECTIONAL_DATUM_IDENTIFIED: false")
print("MANUSCRIPT_MUTATED: false")
print("PHYSICAL_CLAIM: false")
print("CANDIDATE_JSON:", output_path)
print("CANDIDATE_JSON_SHA256:", sha256_file(output_path))
