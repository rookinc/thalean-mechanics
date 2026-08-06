#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import json
import subprocess
from collections import Counter, deque
from pathlib import Path

HOME = Path.home()

PROJECT = HOME / "dev/cori/research/thalean_mechanics/papers/08-g60-receipt-packet-native-encounter"
PAPER7 = HOME / "dev/cori/research/thalean_mechanics/papers/07-finite-covariant-receipt-algebra-on-graphs"
PROJECT42 = HOME / "dev/cori/research/mathematics/42-graph-automorphism-groups"
ELECTRON = HOME / "dev/cori/research/physics/quantum_mechanics/01-the-electron-spins-twice"

PAPER7_ARTIFACT = (
    PAPER7
    / "artifacts/json/finite_covariant_receipt_algebra_on_graphs_theorem_001.v1.json"
)
G60_EDGES = ELECTRON / "paper/data/g60_local_edges.csv"
AUT_GROUP = (
    PROJECT42
    / "artifacts/json/native_g60_fiber_product_isomorphism_044.json"
)

EXPECTED_PAPER7_SHA = "09fd36fa74dd5868549349a5edd82d16c80b9efafa72561f53e69001235d3bda"
EXPECTED_G60_SHA = "c700a185fab6a5f434da09b7acb716b96c76170774bee946af8ea907e4fe7f9f"
EXPECTED_AUT_SHA = "b37313b135495752b11e525bb61979163fdf54aec4be4f5d027dcee64c9efc21"

ROOTS = [PAPER7, PROJECT42, ELECTRON]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_status(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "status", "--short"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    return result.stdout.splitlines()


def compose(p: tuple[int, ...], q: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(p[q[x]] for x in range(60))


def permutation_order(p: tuple[int, ...]) -> int:
    identity = tuple(range(60))
    power = identity
    for order in range(1, 481):
        power = compose(p, power)
        if power == identity:
            return order
    raise RuntimeError("Permutation order exceeded 480")


def closure(
    generator_indices: tuple[int, ...],
    permutations: list[tuple[int, ...]],
    permutation_index: dict[tuple[int, ...], int],
    inverse_index: list[int],
) -> frozenset[int]:
    identity_index = permutation_index[tuple(range(60))]
    generators = set(generator_indices)
    generators.update(inverse_index[index] for index in generator_indices)

    found = {identity_index}
    queue = deque([identity_index])

    while queue:
        current = queue.popleft()
        for generator in generators:
            product = compose(
                permutations[current],
                permutations[generator],
            )
            product_index = permutation_index[product]
            if product_index not in found:
                found.add(product_index)
                queue.append(product_index)

    return frozenset(found)


def conjugate_subgroup(
    subgroup: frozenset[int],
    by_index: int,
    permutations: list[tuple[int, ...]],
    permutation_index: dict[tuple[int, ...], int],
    inverse_index: list[int],
) -> tuple[int, ...]:
    by = permutations[by_index]
    by_inverse = permutations[inverse_index[by_index]]
    values = []

    for member_index in subgroup:
        value = compose(
            compose(by, permutations[member_index]),
            by_inverse,
        )
        values.append(permutation_index[value])

    return tuple(sorted(values))


def canonical_subgroup(
    subgroup: frozenset[int],
    permutations: list[tuple[int, ...]],
    permutation_index: dict[tuple[int, ...], int],
    inverse_index: list[int],
) -> tuple[int, ...]:
    return min(
        conjugate_subgroup(
            subgroup,
            by_index,
            permutations,
            permutation_index,
            inverse_index,
        )
        for by_index in range(len(permutations))
    )


def element_order_profile(
    subgroup: frozenset[int],
    orders: list[int],
) -> dict[str, int]:
    counts = Counter(orders[index] for index in subgroup)
    return {
        str(order): count
        for order, count in sorted(counts.items())
    }


def is_abelian(
    subgroup: frozenset[int],
    multiplication: list[list[int]],
) -> bool:
    members = tuple(subgroup)
    return all(
        multiplication[a][b] == multiplication[b][a]
        for a in members
        for b in members
    )


def group_label(
    subgroup: frozenset[int],
    orders: list[int],
    multiplication: list[list[int]],
) -> str:
    order = len(subgroup)
    profile = Counter(orders[index] for index in subgroup)
    abelian = is_abelian(subgroup, multiplication)

    if order == 1:
        return "trivial"
    if any(orders[index] == order for index in subgroup):
        return "C" + str(order)
    if order == 4 and abelian and profile == Counter({2: 3, 1: 1}):
        return "V4"
    if order == 6 and not abelian and profile == Counter({2: 3, 3: 2, 1: 1}):
        return "S3"
    if order == 8 and not abelian and profile == Counter({2: 5, 4: 2, 1: 1}):
        return "D8"
    if abelian:
        return "abelian_order_" + str(order)
    return "nonabelian_order_" + str(order)


def vertex_orbits(
    subgroup: frozenset[int],
    permutations: list[tuple[int, ...]],
) -> list[tuple[int, ...]]:
    unassigned = set(range(60))
    orbits = []

    while unassigned:
        vertex = min(unassigned)
        orbit = tuple(
            sorted(
                {
                    permutations[index][vertex]
                    for index in subgroup
                }
            )
        )
        orbits.append(orbit)
        unassigned.difference_update(orbit)

    return sorted(orbits)


def edge_orbits(
    subgroup: frozenset[int],
    permutations: list[tuple[int, ...]],
    edges: set[tuple[int, int]],
) -> list[tuple[tuple[int, int], ...]]:
    unassigned = set(edges)
    orbits = []

    while unassigned:
        edge = min(unassigned)
        u, v = edge
        orbit = {
            tuple(
                sorted(
                    (
                        permutations[index][u],
                        permutations[index][v],
                    )
                )
            )
            for index in subgroup
        }
        orbit_tuple = tuple(sorted(orbit))
        orbits.append(orbit_tuple)
        unassigned.difference_update(orbit)

    return sorted(orbits)


def has_edge_inversion(
    subgroup: frozenset[int],
    identity_index: int,
    permutations: list[tuple[int, ...]],
    edges: set[tuple[int, int]],
) -> bool:
    for index in subgroup:
        if index == identity_index:
            continue
        permutation = permutations[index]
        for u, v in edges:
            if permutation[u] == v and permutation[v] == u:
                return True
    return False


print("OUT ==")
print("PACKET: g60_native_semiregular_receipt_action_census_002")
print("MODE: read-only native semiregular subgroup census")
print("TARGET:", PROJECT)
print("REPOSITORY_MUTATION: none")
print()

status_before = {
    str(root): git_status(root)
    for root in ROOTS
}

print("== SOURCE LOCK ==")

actual_paper7_sha = sha256_file(PAPER7_ARTIFACT)
actual_g60_sha = sha256_file(G60_EDGES)
actual_aut_sha = sha256_file(AUT_GROUP)

print("PAPER7_SHA256:", actual_paper7_sha)
print("G60_EDGE_SHA256:", actual_g60_sha)
print("AUTOMORPHISM_ACTION_SHA256:", actual_aut_sha)
print(
    "CHECK_SOURCE_HASHES:",
    str(
        actual_paper7_sha == EXPECTED_PAPER7_SHA
        and actual_g60_sha == EXPECTED_G60_SHA
        and actual_aut_sha == EXPECTED_AUT_SHA
    ).lower(),
)

print()
print("== RAW G60 GRAPH ==")

with G60_EDGES.open(newline="") as handle:
    rows = list(csv.DictReader(handle))

raw_labels = sorted(
    {
        int(value)
        for row in rows
        for value in (row["local_u"], row["local_v"])
    }
)

if raw_labels != list(range(60)):
    raise RuntimeError(
        "G60 local labels are not exactly 0 through 59"
    )

edges = {
    tuple(
        sorted(
            (
                int(row["local_u"]),
                int(row["local_v"]),
            )
        )
    )
    for row in rows
}

if len(edges) != 120:
    raise RuntimeError("Expected exactly 120 unique G60 edges")

degree = Counter()

for u, v in edges:
    degree[u] += 1
    degree[v] += 1

degree_profile = Counter(degree.values())

print("G60_VERTEX_COUNT:", len(raw_labels))
print("G60_EDGE_COUNT:", len(edges))
print("G60_DEGREE_PROFILE:", dict(sorted(degree_profile.items())))
print("CHECK_G60_IS_60_VERTEX_4_REGULAR:", str(degree_profile == Counter({4: 60})).lower())

print()
print("== FULL AUTOMORPHISM ACTION ==")

artifact = json.loads(AUT_GROUP.read_text())
mapping_rows = artifact["mapping_rows"]

permutations = [
    tuple(row["actual_permutation"])
    for row in mapping_rows
]

permutation_set = set(permutations)

print("MAPPING_ROW_COUNT:", len(mapping_rows))
print("DISTINCT_PERMUTATION_COUNT:", len(permutation_set))

if len(mapping_rows) != 480 or len(permutation_set) != 480:
    raise RuntimeError("Expected exactly 480 distinct group permutations")

if any(sorted(permutation) != list(range(60)) for permutation in permutations):
    raise RuntimeError("A mapping row is not a permutation of 0 through 59")

permutation_index = {
    permutation: index
    for index, permutation in enumerate(permutations)
}

identity = tuple(range(60))

if identity not in permutation_index:
    raise RuntimeError("Identity permutation missing")

identity_index = permutation_index[identity]

inverse_index = []

for permutation in permutations:
    inverse = [0] * 60
    for source, target in enumerate(permutation):
        inverse[target] = source
    inverse_tuple = tuple(inverse)
    if inverse_tuple not in permutation_index:
        raise RuntimeError("Inverse permutation missing")
    inverse_index.append(permutation_index[inverse_tuple])

automorphism_failure_count = 0

for permutation in permutations:
    mapped_edges = {
        tuple(sorted((permutation[u], permutation[v])))
        for u, v in edges
    }
    if mapped_edges != edges:
        automorphism_failure_count += 1

print("IDENTITY_INDEX:", identity_index)
print("INVERSE_FAILURE_COUNT:", 0)
print("GRAPH_AUTOMORPHISM_FAILURE_COUNT:", automorphism_failure_count)
print(
    "CHECK_ALL_480_ROWS_ARE_G60_AUTOMORPHISMS:",
    str(automorphism_failure_count == 0).lower(),
)

print()
print("== GROUP TABLE ==")

multiplication = []

for left in permutations:
    row = []
    for right in permutations:
        product = compose(left, right)
        if product not in permutation_index:
            raise RuntimeError("Permutation set is not closed")
        row.append(permutation_index[product])
    multiplication.append(row)

orders = [
    permutation_order(permutation)
    for permutation in permutations
]

full_order_profile = dict(
    sorted(Counter(orders).items())
)

print("FULL_GROUP_ORDER:", len(permutations))
print("FULL_GROUP_ELEMENT_ORDER_PROFILE:", full_order_profile)
print("CHECK_GROUP_TABLE_CLOSED: true")

print()
print("== SEMIREGULAR ELEMENT CENSUS ==")

fixed_point_counts = [
    sum(
        permutation[vertex] == vertex
        for vertex in range(60)
    )
    for permutation in permutations
]

semiregular_element_indices = {
    index
    for index, fixed_count in enumerate(fixed_point_counts)
    if index == identity_index or fixed_count == 0
}

fixed_point_profile = dict(
    sorted(Counter(fixed_point_counts).items())
)

print("FIXED_POINT_COUNT_PROFILE:", fixed_point_profile)
print(
    "FIXED_POINT_FREE_NONIDENTITY_ELEMENT_COUNT:",
    len(semiregular_element_indices) - 1,
)
print(
    "SEMIREGULAR_ELEMENT_ORDER_PROFILE:",
    dict(
        sorted(
            Counter(
                orders[index]
                for index in semiregular_element_indices
                if index != identity_index
            ).items()
        )
    ),
)

print()
print("== SEMIREGULAR SUBGROUP ENUMERATION ==")

trivial = frozenset({identity_index})
subgroup_generators = {trivial: tuple()}
queue = deque([trivial])
processed = 0

while queue:
    subgroup = queue.popleft()
    generators = subgroup_generators[subgroup]
    processed += 1

    for candidate in sorted(
        semiregular_element_indices.difference(subgroup)
    ):
        candidate_generators = generators + (candidate,)
        generated = closure(
            candidate_generators,
            permutations,
            permutation_index,
            inverse_index,
        )

        if not generated.issubset(semiregular_element_indices):
            continue

        if generated not in subgroup_generators:
            subgroup_generators[generated] = candidate_generators
            queue.append(generated)

            if len(subgroup_generators) % 25 == 0:
                print(
                    "PROGRESS:",
                    "semiregular_subgroups=" + str(len(subgroup_generators)),
                    "queue=" + str(len(queue)),
                )

semiregular_subgroups = [
    subgroup
    for subgroup in subgroup_generators
    if len(subgroup) > 1
]

print("SEMIREGULAR_SUBGROUP_COUNT:", len(semiregular_subgroups))
print("ENUMERATION_QUEUE_PROCESSED_COUNT:", processed)

print()
print("== CONJUGACY CLASS REDUCTION ==")

classes = {}

for subgroup in semiregular_subgroups:
    canonical = canonical_subgroup(
        subgroup,
        permutations,
        permutation_index,
        inverse_index,
    )
    classes.setdefault(canonical, []).append(subgroup)

print("SEMIREGULAR_SUBGROUP_CONJUGACY_CLASS_COUNT:", len(classes))

print()
print("== NATIVE RECEIPT ACTION SPECTRUM ==")

class_rows = []
cover_admissible_class_count = 0
edge_inverting_class_count = 0

for class_index, canonical in enumerate(sorted(classes), start=1):
    subgroup = frozenset(canonical)
    generators = subgroup_generators.get(subgroup)

    if generators is None:
        for candidate_subgroup in classes[canonical]:
            candidate_canonical = canonical_subgroup(
                candidate_subgroup,
                permutations,
                permutation_index,
                inverse_index,
            )
            if candidate_canonical == canonical:
                subgroup = candidate_subgroup
                generators = subgroup_generators[subgroup]
                break

    vertex_fibers = vertex_orbits(subgroup, permutations)
    quotient_edge_orbits = edge_orbits(subgroup, permutations, edges)
    edge_inversion = has_edge_inversion(
        subgroup,
        identity_index,
        permutations,
        edges,
    )

    all_vertex_orbits_regular = all(
        len(orbit) == len(subgroup)
        for orbit in vertex_fibers
    )
    all_edge_orbits_regular = all(
        len(orbit) == len(subgroup)
        for orbit in quotient_edge_orbits
    )

    cover_admissible = (
        all_vertex_orbits_regular
        and all_edge_orbits_regular
        and not edge_inversion
    )

    if cover_admissible:
        cover_admissible_class_count += 1

    if edge_inversion:
        edge_inverting_class_count += 1

    row = {
        "class_index": class_index,
        "conjugate_subgroup_count": len(classes[canonical]),
        "group_order": len(subgroup),
        "group_label": group_label(
            subgroup,
            orders,
            multiplication,
        ),
        "abelian": is_abelian(subgroup, multiplication),
        "element_order_profile": element_order_profile(
            subgroup,
            orders,
        ),
        "generator_count_used": len(generators or ()),
        "generator_indices": list(generators or ()),
        "vertex_orbit_count": len(vertex_fibers),
        "vertex_orbit_sizes": sorted(
            set(len(orbit) for orbit in vertex_fibers)
        ),
        "edge_orbit_count": len(quotient_edge_orbits),
        "edge_orbit_sizes": sorted(
            set(len(orbit) for orbit in quotient_edge_orbits)
        ),
        "edge_inversion": edge_inversion,
        "cover_admissible": cover_admissible,
        "fiber_preview": [
            list(orbit)
            for orbit in vertex_fibers[:5]
        ],
    }

    class_rows.append(row)
    print("RECEIPT_ACTION_CLASS:", json.dumps(row, sort_keys=True))

print()
print("== SPECTRUM COUNTS ==")

order_class_counts = Counter(
    row["group_order"]
    for row in class_rows
)

label_class_counts = Counter(
    row["group_label"]
    for row in class_rows
)

cover_label_counts = Counter(
    row["group_label"]
    for row in class_rows
    if row["cover_admissible"]
)

print("CLASS_COUNT_BY_GROUP_ORDER:", dict(sorted(order_class_counts.items())))
print("CLASS_COUNT_BY_GROUP_LABEL:", dict(sorted(label_class_counts.items())))
print("COVER_ADMISSIBLE_CLASS_COUNT:", cover_admissible_class_count)
print("EDGE_INVERTING_CLASS_COUNT:", edge_inverting_class_count)
print("COVER_ADMISSIBLE_LABEL_COUNTS:", dict(sorted(cover_label_counts.items())))

print()
print("== STATUS PRESERVATION ==")

all_status_preserved = True

for root in ROOTS:
    before = status_before[str(root)]
    after = git_status(root)
    preserved = before == after
    all_status_preserved = all_status_preserved and preserved

    print(
        "STATUS_CHECK:",
        json.dumps(
            {
                "root": str(root),
                "before": before,
                "after": after,
                "preserved": preserved,
            },
            sort_keys=True,
        ),
    )

print(
    "CHECK_ALL_REPOSITORY_STATUS_PRESERVED:",
    str(all_status_preserved).lower(),
)

source_hashes_pass = (
    actual_paper7_sha == EXPECTED_PAPER7_SHA
    and actual_g60_sha == EXPECTED_G60_SHA
    and actual_aut_sha == EXPECTED_AUT_SHA
)

enumeration_pass = (
    source_hashes_pass
    and degree_profile == Counter({4: 60})
    and automorphism_failure_count == 0
    and len(permutations) == 480
    and len(semiregular_subgroups) > 0
    and len(classes) > 0
    and all_status_preserved
)

print()
print("== FINAL GATES ==")
print("CHECK_SOURCE_HASHES:", str(source_hashes_pass).lower())
print("CHECK_FULL_G60_ACTION_PARSED:", str(len(permutations) == 480).lower())
print("CHECK_ALL_ACTION_ROWS_PRESERVE_G60:", str(automorphism_failure_count == 0).lower())
print("CHECK_SEMIREGULAR_SUBGROUPS_FOUND:", str(bool(semiregular_subgroups)).lower())
print("CHECK_CONJUGACY_CLASSES_REDUCED:", str(bool(classes)).lower())
print("CHECK_NATIVE_ACTION_CENSUS_PASS:", str(enumeration_pass).lower())

if enumeration_pass:
    classification = "native_G60_semiregular_receipt_action_spectrum_enumerated"
    next_gate = (
        "For each cover-admissible conjugacy class, construct the orbit "
        "quotient, derive edge receipts from a native section, reconstruct "
        "G60, and compute the holonomy image."
    )
else:
    classification = "native_G60_semiregular_receipt_action_census_incomplete"
    next_gate = (
        "Inspect the failed action, subgroup, graph, or status gate before "
        "attempting quotient reconstruction."
    )

print()
print("FINAL_CLASSIFICATION:", classification)
print(
    "BOUNDARY:",
    "This packet enumerates native semiregular automorphism subgroups and "
    "cover-admissible action classes. It does not yet derive quotient edge "
    "receipts, reconstruct G60, compute holonomy, or select one realization.",
)
print("NEXT_GATE:", next_gate)
print(
    "KEEPER:",
    "G60 may answer with one receipt action, several, or none. The census "
    "does not choose for it.",
)
print("MUTATION_PERFORMED: false")
