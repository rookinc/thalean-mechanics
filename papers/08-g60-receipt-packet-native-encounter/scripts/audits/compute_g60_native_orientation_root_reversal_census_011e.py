import hashlib
import json
import subprocess
import sys
from array import array
from collections import Counter, deque
from pathlib import Path

project = Path(sys.argv[1]).resolve()
output_path = Path(sys.argv[2]).resolve()

action_path = Path(
    "/data/data/com.termux/files/home/dev/cori/research/mathematics/"
    "42-graph-automorphism-groups/artifacts/json/"
    "native_g60_fiber_product_isomorphism_044.json"
)
absence_path = (
    project
    / "artifacts/json"
    / "g60_fourth_root_structured_absence_anatomy_011d.v1.json"
)

expected_action = "b37313b135495752b11e525bb61979163fdf54aec4be4f5d027dcee64c9efc21"
expected_absence = "0ad32f6908e1cf8f7ad1093aafa9ff51ce8b3ff03481aa2a4a9d18b841f26691"

def sha256_file(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def git_output(*args):
    return subprocess.run(
        ["git", "-C", str(project), *args],
        text=True,
        capture_output=True,
        check=True,
    ).stdout.rstrip("\n")

def profile(values):
    return {
        str(key): count
        for key, count in sorted(Counter(values).items())
    }

status_before = git_output("status", "--short")
head_before = git_output("--no-pager", "show", "-s", "--oneline", "HEAD")

action_sha = sha256_file(action_path)
absence_sha = sha256_file(absence_path)

action = json.loads(action_path.read_text(encoding="utf-8"))
absence = json.loads(absence_path.read_text(encoding="utf-8"))

rows = sorted(action["mapping_rows"], key=lambda row: row["actual_index"])
permutations = [tuple(row["actual_permutation"]) for row in rows]
orders = [row["actual_order"] for row in rows]
group_order = len(permutations)

perm_to_index = {
    permutation: index
    for index, permutation in enumerate(permutations)
}
identity = perm_to_index[tuple(range(60))]

multiplication = []
closure_failures = 0

print("== G60 NATIVE ORIENTATION-ROOT REVERSAL 011e ==")
print("MODE: temporary read-only reversal census")
print("LOCKED_HEAD:", head_before)

for left in range(group_order):
    if left % 40 == 0:
        print("MULTIPLICATION_PROGRESS:", left, "/", group_order)
    p = permutations[left]
    row = array("H")
    for right in range(group_order):
        product_permutation = tuple(
            p[permutations[right][vertex]]
            for vertex in range(60)
        )
        product = perm_to_index.get(product_permutation)
        if product is None:
            closure_failures += 1
            row.append(65535)
        else:
            row.append(product)
    multiplication.append(row)

print("MULTIPLICATION_PROGRESS:", group_order, "/", group_order)

inverse = [None] * group_order
inverse_failures = []

for element in range(group_order):
    candidates = [
        candidate for candidate in range(group_order)
        if (
            multiplication[element][candidate] == identity
            and multiplication[candidate][element] == identity
        )
    ]
    if len(candidates) != 1:
        inverse_failures.append(element)
    else:
        inverse[element] = candidates[0]

def conjugate(g, x):
    return multiplication[multiplication[g][x]][inverse[g]]

def generated_subgroup(generators):
    expanded = set(generators)
    expanded.update(inverse[g] for g in list(expanded))
    reached = {identity}
    queue = deque([identity])
    while queue:
        current = queue.popleft()
        for generator in expanded:
            candidate = multiplication[current][generator]
            if candidate not in reached:
                reached.add(candidate)
                queue.append(candidate)
    return reached

tau = absence["receipt_layers"]["tau"]
roots = sorted(
    absence["power_map_anatomy"]["tau_square_root_indices"]
)
root_set = set(roots)

square_failures = [
    c for c in roots
    if multiplication[c][c] != tau
]
order_failures = [
    c for c in roots
    if orders[c] != 4
]
inverse_closure_failures = [
    c for c in roots
    if inverse[c] not in root_set
]
self_inverse_roots = [
    c for c in roots
    if inverse[c] == c
]

inverse_pairs = sorted({
    tuple(sorted((c, inverse[c])))
    for c in roots
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
        } & set(elements)
        orbits.append(sorted(orbit))
        remaining.difference_update(orbit)
    return sorted(orbits, key=lambda row: (len(row), row))

def conjugate_pair(g, pair):
    return tuple(sorted((
        conjugate(g, pair[0]),
        conjugate(g, pair[1]),
    )))

def pair_orbits(pairs):
    remaining = set(pairs)
    orbits = []
    while remaining:
        seed = min(remaining)
        orbit = {
            conjugate_pair(g, seed)
            for g in range(group_order)
        } & set(pairs)
        orbits.append(sorted([list(pair) for pair in orbit]))
        remaining.difference_update(orbit)
    return sorted(orbits, key=lambda row: (len(row), row))

element_orbits = conjugacy_orbits(roots)
root_pair_orbits = pair_orbits(inverse_pairs)

involutions = [
    element for element in range(group_order)
    if orders[element] == 2
]

witnesses_by_root = {}
missing_witnesses = []
generated_orders = []

for position, c in enumerate(roots):
    if position % 5 == 0:
        print("REVERSAL_PROGRESS:", position, "/", len(roots))

    witnesses = []
    subgroup_orders = Counter()

    for s in involutions:
        if multiplication[multiplication[s][c]][s] != inverse[c]:
            continue
        subgroup_order = len(generated_subgroup([c, s]))
        witnesses.append(s)
        subgroup_orders[subgroup_order] += 1
        generated_orders.append(subgroup_order)

    witnesses_by_root[str(c)] = {
        "inverse": inverse[c],
        "witness_count": len(witnesses),
        "witness_indices": witnesses,
        "generated_subgroup_order_profile": {
            str(key): value
            for key, value in sorted(subgroup_orders.items())
        },
    }

    if not witnesses:
        missing_witnesses.append(c)

print("REVERSAL_PROGRESS:", len(roots), "/", len(roots))

operation_ok = (
    head_before.startswith("306410c ")
    and action_sha == expected_action
    and absence_sha == expected_absence
    and closure_failures == 0
    and not inverse_failures
)

reversal_obstruction = (
    operation_ok
    and len(roots) == 20
    and len(inverse_pairs) == 10
    and not self_inverse_roots
    and not missing_witnesses
)

classification = (
    "multiple_reversal_orbits"
    if reversal_obstruction and len(inverse_pairs) > 1
    else "orientation_root_reversal_census_failed_or_weakened"
)

status_after = git_output("status", "--short")
head_after = git_output("--no-pager", "show", "-s", "--oneline", "HEAD")
repository_preserved = (
    status_before == status_after
    and head_before == head_after
)

result = {
    "packet": "g60_native_orientation_root_reversal_census_011e",
    "version": 1,
    "mode": "temporary_read_only_reversal_census",
    "authorities": {
        "action_sha256": action_sha,
        "action_hash_match": action_sha == expected_action,
        "absence_011d_sha256": absence_sha,
        "absence_hash_match": absence_sha == expected_absence,
    },
    "group_reconstruction": {
        "group_order": group_order,
        "identity_index": identity,
        "closure_failure_count": closure_failures,
        "inverse_failure_count": len(inverse_failures),
        "operation_ok": operation_ok,
    },
    "orientation_root_set": {
        "tau_index": tau,
        "root_count": len(roots),
        "root_indices": roots,
        "square_failure_count": len(square_failures),
        "order_failure_count": len(order_failures),
        "inverse_closure_failure_count": len(inverse_closure_failures),
        "self_inverse_root_count": len(self_inverse_roots),
        "inverse_pair_count": len(inverse_pairs),
        "inverse_pairs": [list(pair) for pair in inverse_pairs],
        "element_conjugacy_orbit_count": len(element_orbits),
        "element_conjugacy_orbits": element_orbits,
        "pair_conjugacy_orbit_count": len(root_pair_orbits),
        "pair_conjugacy_orbits": root_pair_orbits,
    },
    "reversal_witnesses": {
        "involution_count": len(involutions),
        "all_roots_have_involutive_reverser": not missing_witnesses,
        "missing_witness_count": len(missing_witnesses),
        "missing_witness_roots": missing_witnesses,
        "witnesses_by_root": witnesses_by_root,
        "generated_subgroup_order_profile": profile(generated_orders),
        "D_preservation_basis": (
            "Conjugation inside A preserves the characteristic "
            "upper-central layers Z1 and Z2."
        ),
    },
    "classification": classification,
    "reversal_obstruction_verified_on_orientation_root_layer": (
        reversal_obstruction
    ),
    "repository_status_preserved": repository_preserved,
    "boundary": {
        "candidate_only": True,
        "result_frozen": False,
        "roots_relabelled_as_absent_H": False,
        "one_inverse_pair_selected": len(inverse_pairs) == 1,
        "multiple_inverse_pairs": len(inverse_pairs) > 1,
        "orientation_selected": False,
        "minimal_directional_datum_identified": False,
        "larger_carrier_constructed": False,
        "manuscript_mutated": False,
        "physical_claim": False,
    },
}

output_path.write_text(
    json.dumps(result, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

print("== FINAL ORIENTATION-ROOT REVERSAL REPORT ==")
print("ACTION_HASH_MATCH:", str(action_sha == expected_action).lower())
print("ABSENCE_011D_HASH_MATCH:", str(absence_sha == expected_absence).lower())
print("OPERATION_OK:", str(operation_ok).lower())
print("TAU_INDEX:", tau)
print("ROOT_COUNT:", len(roots))
print("ROOT_INDICES:", roots)
print("SELF_INVERSE_ROOT_COUNT:", len(self_inverse_roots))
print("INVERSE_PAIR_COUNT:", len(inverse_pairs))
print("INVERSE_PAIRS:", [list(pair) for pair in inverse_pairs])
print("ELEMENT_CONJUGACY_ORBIT_COUNT:", len(element_orbits))
print("ELEMENT_CONJUGACY_ORBIT_SIZE_PROFILE:", profile(len(row) for row in element_orbits))
print("PAIR_CONJUGACY_ORBIT_COUNT:", len(root_pair_orbits))
print("PAIR_CONJUGACY_ORBIT_SIZE_PROFILE:", profile(len(row) for row in root_pair_orbits))
print("INVOLUTION_COUNT:", len(involutions))
print("MISSING_REVERSAL_WITNESS_COUNT:", len(missing_witnesses))
print("ALL_ROOTS_HAVE_INVOLUTIVE_REVERSER:", str(not missing_witnesses).lower())
print("GENERATED_SUBGROUP_ORDER_PROFILE:", profile(generated_orders))
print("REVERSAL_OBSTRUCTION_VERIFIED:", str(reversal_obstruction).lower())
print("CLASSIFICATION:", classification)
print("ROOTS_RELABELLED_AS_ABSENT_H: false")
print("ORIENTATION_SELECTED: false")
print("MINIMAL_DIRECTIONAL_DATUM_IDENTIFIED: false")
print("REPOSITORY_STATUS_PRESERVED:", str(repository_preserved).lower())
print("PROJECT_MUTATION_PERFORMED: false")
print("CANDIDATE_JSON:", output_path)
print("CANDIDATE_JSON_SHA256:", sha256_file(output_path))
