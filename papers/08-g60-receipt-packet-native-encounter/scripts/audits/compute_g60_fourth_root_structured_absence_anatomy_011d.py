import hashlib
import json
import subprocess
import sys
from array import array
from collections import Counter
from datetime import datetime
from pathlib import Path

project = Path(sys.argv[1]).resolve()
output_path = Path(sys.argv[2]).resolve()

action_path = Path(
    "/data/data/com.termux/files/home/dev/cori/research/mathematics/"
    "42-graph-automorphism-groups/artifacts/json/"
    "native_g60_fiber_product_isomorphism_044.json"
)
phase_a_path = (
    project
    / "artifacts/json"
    / "g60_upper_central_series_blind_census_010b.v1.json"
)
carrier_path = (
    project
    / "artifacts/json"
    / "g60_native_evolver_census_011c.v1.json"
)

expected_hashes = {
    "action": "b37313b135495752b11e525bb61979163fdf54aec4be4f5d027dcee64c9efc21",
    "phase_a": "6c69d4e6c6a5eca1c5b7d15840a8958cc93eff5a13c1fe62a8840fe2bf0e8f26",
    "carrier_011c": "806a62bc3d67c1dd97f4bdb06ecc82868beb599c278cf1ee8da9cdf28bca1c49",
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

def profile(values):
    return {
        str(key): count
        for key, count in sorted(Counter(values).items())
    }

status_before = git_output("status", "--short")
head_before = git_output("--no-pager", "show", "-s", "--oneline", "HEAD")

actual_hashes = {
    "action": sha256_file(action_path),
    "phase_a": sha256_file(phase_a_path),
    "carrier_011c": sha256_file(carrier_path),
}

action = json.loads(action_path.read_text(encoding="utf-8"))
phase_a = json.loads(phase_a_path.read_text(encoding="utf-8"))
carrier = json.loads(carrier_path.read_text(encoding="utf-8"))

rows = sorted(action["mapping_rows"], key=lambda row: row["actual_index"])
permutations = [tuple(row["actual_permutation"]) for row in rows]
declared_orders = [row["actual_order"] for row in rows]
group_order = len(permutations)
perm_to_index = {
    permutation: index
    for index, permutation in enumerate(permutations)
}
identity = perm_to_index.get(tuple(range(60)))
sentinel = 65535

print("== G60 FOURTH-ROOT STRUCTURED ABSENCE 011d ==")
print("MODE: temporary read-only obstruction anatomy")
print("LOCKED_HEAD:", head_before)
print("ACTION_SHA256:", actual_hashes["action"])
print("PHASE_A_SHA256:", actual_hashes["phase_a"])
print("CARRIER_011C_SHA256:", actual_hashes["carrier_011c"])
print()

multiplication = []
closure_failure_count = 0

print("MULTIPLICATION_BEGIN")
for left in range(group_order):
    if left % 40 == 0:
        print("MULTIPLICATION_PROGRESS:", left, "/", group_order)
    p = permutations[left]
    table_row = array("H")
    for right in range(group_order):
        product = perm_to_index.get(
            tuple(p[permutations[right][v]] for v in range(60))
        )
        if product is None:
            closure_failure_count += 1
            table_row.append(sentinel)
        else:
            table_row.append(product)
    multiplication.append(table_row)
print("MULTIPLICATION_PROGRESS:", group_order, "/", group_order)
print("MULTIPLICATION_END")
print()

def power(element, exponent):
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

if closure_failure_count == 0 and identity is not None:
    for element in range(group_order):
        order = element_order(element)
        computed_orders.append(order)
        if order != declared_orders[element]:
            order_failures.append(
                [element, declared_orders[element], order]
            )

z1 = sorted(phase_a["central_series"]["center_member_indices"])
z2 = sorted(phase_a["central_series"]["second_center_member_indices"])
z1_set = set(z1)
z2_set = set(z2)
tau = next(element for element in z1 if element != identity)
outer_pair = sorted(z2_set - z1_set)

operation_ok = (
    head_before.startswith("d322004 ")
    and actual_hashes == expected_hashes
    and group_order == 480
    and len(perm_to_index) == 480
    and identity is not None
    and closure_failure_count == 0
    and not order_failures
    and carrier["classification"]["frozen_outcome"]
        == "no_exact_evolver_candidate"
)

order_profile = profile(computed_orders)
order8_elements = [
    element for element in range(group_order)
    if computed_orders[element] == 8
]

square_images = [power(element, 2) for element in range(group_order)]
fourth_images = [power(element, 4) for element in range(group_order)]

square_root_fibers = {
    target: [
        element for element in range(group_order)
        if square_images[element] == target
    ]
    for target in z2
}
fourth_root_fibers = {
    target: [
        element for element in range(group_order)
        if fourth_images[element] == target
    ]
    for target in z2
}

tau_square_roots = square_root_fibers[tau]
tau_fourth_roots = fourth_root_fibers[tau]

second_stage_root_counts = {
    str(c): sum(
        square_images[element] == c
        for element in range(group_order)
    )
    for c in tau_square_roots
}

fourth_power_image = sorted(set(fourth_images))
fourth_power_image_order_profile = profile(
    computed_orders[element]
    for element in fourth_power_image
)
fourth_power_source_order_profiles = {}

for target in fourth_power_image:
    sources = [
        element for element in range(group_order)
        if fourth_images[element] == target
    ]
    fourth_power_source_order_profiles[str(target)] = profile(
        computed_orders[element] for element in sources
    )

def conjugate(g, x):
    inverse_g = next(
        candidate
        for candidate in range(group_order)
        if (
            multiplication[g][candidate] == identity
            and multiplication[candidate][g] == identity
        )
    )
    return multiplication[multiplication[g][x]][inverse_g]

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
    return sorted(orbits, key=lambda row: (len(row), row))

tau_square_root_orbits = (
    conjugacy_orbits(tau_square_roots)
    if tau_square_roots else []
)
order8_orbits = (
    conjugacy_orbits(order8_elements)
    if order8_elements else []
)

vertex_orbit = sorted({
    permutations[element][0]
    for element in range(group_order)
})
action_transitive = len(vertex_orbit) == 60

stabilizer_rows = []
stabilizer_order_profiles = []
stabilizer_intersection_z1_profiles = []
stabilizer_intersection_z2_profiles = []
stabilizer_product_z2_sizes = []
stabilizer_cyclic_flags = []

for vertex in range(60):
    stabilizer = [
        element for element in range(group_order)
        if permutations[element][vertex] == vertex
    ]
    stabilizer_set = set(stabilizer)
    stabilizer_profile = profile(
        computed_orders[element] for element in stabilizer
    )
    intersection_z1 = sorted(stabilizer_set & z1_set)
    intersection_z2 = sorted(stabilizer_set & z2_set)
    product_with_z2 = {
        multiplication[s][z]
        for s in stabilizer
        for z in z2
    }
    cyclic = (
        len(stabilizer) == 8
        and any(computed_orders[element] == 8 for element in stabilizer)
    )

    stabilizer_rows.append({
        "vertex": vertex,
        "order": len(stabilizer),
        "element_order_profile": stabilizer_profile,
        "intersection_Z1": intersection_z1,
        "intersection_Z2": intersection_z2,
        "product_with_Z2_size": len(product_with_z2),
        "cyclic_order8": cyclic,
    })
    stabilizer_order_profiles.append(
        json.dumps(stabilizer_profile, sort_keys=True)
    )
    stabilizer_intersection_z1_profiles.append(
        tuple(intersection_z1)
    )
    stabilizer_intersection_z2_profiles.append(
        tuple(intersection_z2)
    )
    stabilizer_product_z2_sizes.append(len(product_with_z2))
    stabilizer_cyclic_flags.append(cyclic)

if tau_fourth_roots:
    fourth_root_classification = "tau_has_native_fourth_roots"
elif order8_elements:
    fourth_root_classification = (
        "order8_elements_exist_but_tau_is_excluded_from_their_fourth_powers"
    )
else:
    fourth_root_classification = "A_contains_no_order8_elements"

if not tau_square_roots:
    root_stage_classification = "tau_has_no_native_square_root"
elif not tau_fourth_roots:
    root_stage_classification = (
        "tau_has_order4_square_roots_but_none_has_a_native_square_root"
    )
else:
    root_stage_classification = "tau_has_native_fourth_roots"

structured_absence_pass = (
    operation_ok
    and not tau_fourth_roots
    and carrier["candidate_census"]["U0_count"] == 0
    and action_transitive
    and all(len(row["intersection_Z2"]) == 1 for row in stabilizer_rows)
)

status_after = git_output("status", "--short")
head_after = git_output("--no-pager", "show", "-s", "--oneline", "HEAD")
repository_preserved = (
    status_before == status_after
    and head_before == head_after
)

result = {
    "packet": "g60_fourth_root_structured_absence_anatomy_011d",
    "version": 1,
    "created_at": datetime.now().astimezone().isoformat(),
    "mode": "temporary_read_only_obstruction_anatomy",
    "authorities": {
        name: {
            "actual_sha256": actual_hashes[name],
            "expected_sha256": expected_hashes[name],
            "hash_match": actual_hashes[name] == expected_hashes[name],
        }
        for name in expected_hashes
    },
    "group": {
        "order": group_order,
        "identity_index": identity,
        "element_order_profile": order_profile,
        "order8_element_count": len(order8_elements),
        "order8_member_indices": order8_elements,
        "order8_conjugacy_orbit_count": len(order8_orbits),
        "order8_conjugacy_orbits": order8_orbits,
        "closure_failure_count": closure_failure_count,
        "declared_order_failure_count": len(order_failures),
        "operation_ok": operation_ok,
    },
    "receipt_layers": {
        "Z1": z1,
        "Z2": z2,
        "tau": tau,
        "outer_pair": outer_pair,
    },
    "power_map_anatomy": {
        "fourth_power_image_size": len(fourth_power_image),
        "fourth_power_image_indices": fourth_power_image,
        "fourth_power_image_order_profile": fourth_power_image_order_profile,
        "fourth_power_source_order_profiles": fourth_power_source_order_profiles,
        "Z2_square_root_fibers": {
            str(target): roots
            for target, roots in square_root_fibers.items()
        },
        "Z2_fourth_root_fibers": {
            str(target): roots
            for target, roots in fourth_root_fibers.items()
        },
        "tau_square_root_count": len(tau_square_roots),
        "tau_square_root_indices": tau_square_roots,
        "tau_square_root_order_profile": profile(
            computed_orders[element] for element in tau_square_roots
        ),
        "tau_square_root_conjugacy_orbit_count": len(
            tau_square_root_orbits
        ),
        "tau_square_root_conjugacy_orbits": tau_square_root_orbits,
        "tau_square_roots_second_stage_root_counts": second_stage_root_counts,
        "tau_fourth_root_count": len(tau_fourth_roots),
        "tau_fourth_root_indices": tau_fourth_roots,
        "fourth_root_classification": fourth_root_classification,
        "root_stage_classification": root_stage_classification,
    },
    "observation_receipt_transversality": {
        "vertex0_orbit_size": len(vertex_orbit),
        "full_action_transitive": action_transitive,
        "vertex_stabilizer_order_profile": profile(
            row["order"] for row in stabilizer_rows
        ),
        "vertex_stabilizer_element_order_profile_counts": profile(
            stabilizer_order_profiles
        ),
        "vertex_stabilizer_intersection_Z1_profile": profile(
            stabilizer_intersection_z1_profiles
        ),
        "vertex_stabilizer_intersection_Z2_profile": profile(
            stabilizer_intersection_z2_profiles
        ),
        "vertex_stabilizer_product_Z2_size_profile": profile(
            stabilizer_product_z2_sizes
        ),
        "cyclic_order8_stabilizer_count": sum(stabilizer_cyclic_flags),
        "stabilizer_rows": stabilizer_rows,
        "quotient_order_by_Z1": group_order // len(z1),
        "quotient_order_by_Z2": group_order // len(z2),
        "interpretation": (
            "Vertex stabilizers encode observation-preserving isotropy. "
            "Z2 acts freely within quotient fibers. Their trivial "
            "intersection separates local isotropy from interior receipt."
        ),
    },
    "classification": {
        "fourth_root": fourth_root_classification,
        "root_stage": root_stage_classification,
        "structured_absence_pass": structured_absence_pass,
        "replacement_selector_searched": False,
        "larger_carrier_constructed": False,
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
        "candidate_only": True,
        "result_frozen": False,
        "native_H_found": False,
        "orientation_obstruction_instantiated": False,
        "larger_carrier_constructed": False,
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

print("== FINAL STRUCTURED ABSENCE REPORT ==")
print("ALL_AUTHORITY_HASHES_MATCH:", str(actual_hashes == expected_hashes).lower())
print("OPERATION_OK:", str(operation_ok).lower())
print("ELEMENT_ORDER_PROFILE:", order_profile)
print("ORDER8_ELEMENT_COUNT:", len(order8_elements))
print("ORDER8_CONJUGACY_ORBIT_COUNT:", len(order8_orbits))
print("FOURTH_POWER_IMAGE_SIZE:", len(fourth_power_image))
print("FOURTH_POWER_IMAGE_ORDER_PROFILE:", fourth_power_image_order_profile)
print("TAU_SQUARE_ROOT_COUNT:", len(tau_square_roots))
print("TAU_SQUARE_ROOT_INDICES:", tau_square_roots)
print("TAU_SQUARE_ROOT_ORDER_PROFILE:", profile(computed_orders[element] for element in tau_square_roots))
print("TAU_SQUARE_ROOT_CONJUGACY_ORBIT_COUNT:", len(tau_square_root_orbits))
print("TAU_SQUARE_ROOTS_SECOND_STAGE_ROOT_COUNTS:", second_stage_root_counts)
print("TAU_FOURTH_ROOT_COUNT:", len(tau_fourth_roots))
print("FOURTH_ROOT_CLASSIFICATION:", fourth_root_classification)
print("ROOT_STAGE_CLASSIFICATION:", root_stage_classification)
print("Z2_SQUARE_ROOT_COUNTS:", {str(k): len(v) for k, v in square_root_fibers.items()})
print("Z2_FOURTH_ROOT_COUNTS:", {str(k): len(v) for k, v in fourth_root_fibers.items()})
print("FULL_ACTION_TRANSITIVE:", str(action_transitive).lower())
print("VERTEX_STABILIZER_ORDER_PROFILE:", profile(row["order"] for row in stabilizer_rows))
print("VERTEX_STABILIZER_ELEMENT_ORDER_PROFILE_COUNTS:", profile(stabilizer_order_profiles))
print("VERTEX_STABILIZER_INTERSECTION_Z1_PROFILE:", profile(stabilizer_intersection_z1_profiles))
print("VERTEX_STABILIZER_INTERSECTION_Z2_PROFILE:", profile(stabilizer_intersection_z2_profiles))
print("VERTEX_STABILIZER_PRODUCT_Z2_SIZE_PROFILE:", profile(stabilizer_product_z2_sizes))
print("CYCLIC_ORDER8_STABILIZER_COUNT:", sum(stabilizer_cyclic_flags))
print("QUOTIENT_ORDER_BY_Z1:", group_order // len(z1))
print("QUOTIENT_ORDER_BY_Z2:", group_order // len(z2))
print("STRUCTURED_ABSENCE_PASS:", str(structured_absence_pass).lower())
print("REPLACEMENT_SELECTOR_SEARCHED: false")
print("LARGER_CARRIER_CONSTRUCTED: false")
print("ORIENTATION_OBSTRUCTION_INSTANTIATED: false")
print("REPOSITORY_STATUS_PRESERVED:", str(repository_preserved).lower())
print("PROJECT_MUTATION_PERFORMED: false")
print("CANDIDATE_JSON:", output_path)
print("CANDIDATE_JSON_SHA256:", sha256_file(output_path))
