#!/usr/bin/env python3

import csv
import hashlib
import json
import subprocess
from collections import Counter, deque
from pathlib import Path

ROOT = Path(
    "/data/data/com.termux/files/home/dev/cori/research/"
    "thalean_mechanics/papers/"
    "08-g60-receipt-packet-native-encounter"
)
GIT_ROOT = ROOT.parents[1]

PROJECT42 = Path(
    "/data/data/com.termux/files/home/dev/cori/research/"
    "mathematics/42-graph-automorphism-groups"
)
ELECTRON = Path(
    "/data/data/com.termux/files/home/dev/cori/research/"
    "physics/quantum_mechanics/01-the-electron-spins-twice"
)

BLIND = (
    ROOT
    / "artifacts/receipts/"
    "g60_native_semiregular_receipt_action_census_002_mac.txt"
)
PACKET007 = (
    ROOT
    / "artifacts/receipts/"
    "g60_normal_v4_g15_quotient_unblinding_007.txt"
)
PACKET007_SUM = Path(str(PACKET007) + ".sha256")

ACTION = (
    PROJECT42
    / "artifacts/json/"
    "native_g60_fiber_product_isomorphism_044.json"
)
CERT033 = (
    PROJECT42
    / "sources/project41-paper42/"
    "project42_native_voltage_derivation_certificate_033.json"
)
G60_CSV = (
    ELECTRON
    / "paper/data/g60_local_edges.csv"
)

EXPECTED = {
    BLIND:
        "9d0f1ef5975cd8cd2575192012c8bfeefe15c2856d6646e827ffc4ada851f383",
    ACTION:
        "b37313b135495752b11e525bb61979163fdf54aec4be4f5d027dcee64c9efc21",
    CERT033:
        "9d5046dec7ea5d32f88782aa158a79082d4facf6f0b4fd4a7d3a3e4c552a0f70",
    G60_CSV:
        "c700a185fab6a5f434da09b7acb716b96c76170774bee946af8ea907e4fe7f9f",
}

SOURCE_COMMIT = "bbae505"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_status(root):
    result = subprocess.run(
        ["git", "-C", str(root), "status", "--short"],
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout.splitlines()


def compose(p, q):
    return tuple(p[q[i]] for i in range(len(p)))


def perm_order(p):
    seen = set()
    answer = 1

    def lcm(a, b):
        import math
        return a * b // math.gcd(a, b)

    for start in range(len(p)):
        if start in seen:
            continue
        cur = start
        length = 0
        while cur not in seen:
            seen.add(cur)
            cur = p[cur]
            length += 1
        if length:
            answer = lcm(answer, length)
    return answer


def xor2(a, b):
    return (a[0] ^ b[0], a[1] ^ b[1])


def edge_key(u, v):
    return (u, v) if u < v else (v, u)


def load_edges(path):
    answer = set()
    with path.open(newline="") as handle:
        for row in csv.DictReader(handle):
            answer.add(edge_key(
                int(row["local_u"]),
                int(row["local_v"]),
            ))
    return answer


def parse_normal_classes(path):
    rows = []
    for line in path.read_text().splitlines():
        if line.startswith("NORMAL_CLASS: "):
            rows.append(json.loads(line.split(": ", 1)[1]))
    return rows


def graph_adjacency(edges, n):
    adjacency = [set() for _ in range(n)]
    for u, v in edges:
        adjacency[u].add(v)
        adjacency[v].add(u)
    return adjacency


def enumerate_isomorphisms(source_edges, target_edges, n):
    source_adj = graph_adjacency(source_edges, n)
    target_adj = graph_adjacency(target_edges, n)

    mapping = {}
    used = set()
    results = []

    def compatible(source_vertex, target_vertex):
        if len(source_adj[source_vertex]) != len(target_adj[target_vertex]):
            return False

        for old_source, old_target in mapping.items():
            if ((old_source in source_adj[source_vertex])
                    != (old_target in target_adj[target_vertex])):
                return False
        return True

    def forward_possible():
        for source_vertex in range(n):
            if source_vertex in mapping:
                continue
            if not any(
                target_vertex not in used
                and compatible(source_vertex, target_vertex)
                for target_vertex in range(n)
            ):
                return False
        return True

    def recurse():
        if len(mapping) == n:
            results.append(tuple(mapping[i] for i in range(n)))
            return

        remaining = [v for v in range(n) if v not in mapping]
        source_vertex = max(
            remaining,
            key=lambda v: (
                sum(x in mapping for x in source_adj[v]),
                -v,
            ),
        )

        candidates = [
            target_vertex
            for target_vertex in range(n)
            if target_vertex not in used
            and compatible(source_vertex, target_vertex)
        ]

        for target_vertex in candidates:
            mapping[source_vertex] = target_vertex
            used.add(target_vertex)

            if forward_possible():
                recurse()

            used.remove(target_vertex)
            del mapping[source_vertex]

    recurse()
    return results


GL2 = (
    (0, 1, 1, 0),
    (0, 1, 1, 1),
    (1, 0, 0, 1),
    (1, 0, 1, 1),
    (1, 1, 0, 1),
    (1, 1, 1, 0),
)


def apply_matrix(matrix, vector):
    a, b, c, d = matrix
    x, y = vector
    return (
        (a * x + b * y) % 2,
        (c * x + d * y) % 2,
    )


def solve_gauge_equivalence(
    native_edges,
    native_delta,
    certificate_delta,
    mapping,
    matrix,
):
    adjacency = graph_adjacency(native_edges, 15)
    gauge_source = {0: (0, 0)}
    queue = deque([0])

    while queue:
        u = queue.popleft()
        for v in sorted(adjacency[u]):
            native_value = apply_matrix(
                matrix,
                native_delta[edge_key(u, v)],
            )
            certificate_value = certificate_delta[
                edge_key(mapping[u], mapping[v])
            ]
            required = xor2(native_value, certificate_value)
            candidate = xor2(gauge_source[u], required)

            if v not in gauge_source:
                gauge_source[v] = candidate
                queue.append(v)
            elif gauge_source[v] != candidate:
                return None

    for u, v in native_edges:
        lhs = certificate_delta[edge_key(mapping[u], mapping[v])]
        rhs = apply_matrix(matrix, native_delta[edge_key(u, v)])
        rhs = xor2(rhs, gauge_source[u])
        rhs = xor2(rhs, gauge_source[v])
        if lhs != rhs:
            return None

    historical_gauge = [None] * 15
    for source_vertex, historical_vertex in enumerate(mapping):
        historical_gauge[historical_vertex] = gauge_source[source_vertex]

    return tuple(historical_gauge)


def spanning_tree(edges, n, root=0):
    adjacency = graph_adjacency(edges, n)
    parent = {root: None}
    tree = set()
    queue = deque([root])

    while queue:
        u = queue.popleft()
        for v in sorted(adjacency[u]):
            if v in parent:
                continue
            parent[v] = u
            tree.add(edge_key(u, v))
            queue.append(v)

    return tree


def normalized_voltage(edges, delta, n=15):
    tree = spanning_tree(edges, n)
    adjacency = graph_adjacency(tree, n)
    gauge = {0: (0, 0)}
    queue = deque([0])

    while queue:
        u = queue.popleft()
        for v in sorted(adjacency[u]):
            if v in gauge:
                continue
            gauge[v] = xor2(
                gauge[u],
                delta[edge_key(u, v)],
            )
            queue.append(v)

    normalized = {}
    for edge in edges:
        u, v = edge
        normalized[edge] = xor2(
            xor2(delta[edge], gauge[u]),
            gauge[v],
        )

    return tree, normalized


STATUS_ROOTS = (ROOT, PROJECT42, ELECTRON)
status_before = {
    str(root): git_status(root)
    for root in STATUS_ROOTS
}

print("OUT ==")
print("PACKET: g60_native_v4_voltage_certificate_comparison_008")
print("MODE: read-only native V4 voltage comparison")
print("TARGET:", ROOT)
print("REPOSITORY_MUTATION: none")
print()

print("PROGRESS: [1/5] locking sources")

checks = {}

print("== SOURCE LOCK ==")
for path, expected_hash in EXPECTED.items():
    actual_hash = sha256(path)
    key = "CHECK_" + path.name.upper().replace(".", "_") + "_HASH"
    checks[key] = actual_hash == expected_hash
    print(path.name.upper() + "_SHA256:", actual_hash)
    print(key + ":", str(checks[key]).lower())

packet007_hash = sha256(PACKET007)
sidecar_hash = PACKET007_SUM.read_text().split()[0]
checks["CHECK_PACKET007_SIDECAR_HASH"] = (
    packet007_hash == sidecar_hash
)

relative_packet007 = PACKET007.relative_to(GIT_ROOT).as_posix()
committed = subprocess.run(
    [
        "git",
        "-C",
        str(GIT_ROOT),
        "show",
        SOURCE_COMMIT + ":" + relative_packet007,
    ],
    check=True,
    capture_output=True,
).stdout
checks["CHECK_PACKET007_COMMITTED_AT_BBAE505"] = (
    committed == PACKET007.read_bytes()
)

print("PACKET007_SHA256:", packet007_hash)
print(
    "CHECK_PACKET007_SIDECAR_HASH:",
    str(checks["CHECK_PACKET007_SIDECAR_HASH"]).lower(),
)
print(
    "CHECK_PACKET007_COMMITTED_AT_BBAE505:",
    str(checks["CHECK_PACKET007_COMMITTED_AT_BBAE505"]).lower(),
)
print()

print("PROGRESS: [2/5] deriving native V4 coordinates")

packet007_lines = PACKET007.read_text().splitlines()

def packet007_value(name):
    prefix = name + ":"
    for line in packet007_lines:
        if line.startswith(prefix):
            return line.split(":", 1)[1].strip()
    raise RuntimeError("missing Packet007 field: " + name)

selected_v4_index = int(
    packet007_value("SELECTED_V4_CLASS_INDEX")
)
selected_v4_generators = json.loads(
    packet007_value("SELECTED_V4_GENERATOR_INDICES")
)
selected_c2_index = int(
    packet007_value("SELECTED_C2_CLASS_INDEX")
)
selected_c2_generators = json.loads(
    packet007_value("SELECTED_C2_GENERATOR_INDICES")
)

action = json.loads(ACTION.read_text())
permutations = {
    int(row["actual_index"]): tuple(row["actual_permutation"])
    for row in action["mapping_rows"]
}

identity = tuple(range(60))
p65 = permutations[65]
p124 = permutations[124]
p326 = permutations[326]
product = compose(p65, p124)

v4_permutations = {
    (0, 0): identity,
    (1, 0): p65,
    (0, 1): p124,
    (1, 1): product,
}

checks["CHECK_UNIQUE_NORMAL_V4_CLASS20"] = (
    selected_v4_index == 20
    and selected_v4_generators == [65, 124]
)
checks["CHECK_UNIQUE_NORMAL_C2_CLASS22"] = (
    selected_c2_index == 22
    and selected_c2_generators == [326]
)
checks["CHECK_V4_PRODUCT_IS_NORMAL_C2"] = product == p326
checks["CHECK_V4_MEMBER_ORDERS"] = (
    perm_order(identity) == 1
    and perm_order(p65) == 2
    and perm_order(p124) == 2
    and perm_order(p326) == 2
)

unseen = set(range(60))
orbits = []
while unseen:
    seed = min(unseen)
    orbit = tuple(sorted(
        permutation[seed]
        for permutation in v4_permutations.values()
    ))
    orbits.append(orbit)
    unseen -= set(orbit)

orbits = sorted(orbits)
vertex_to_base = {}
vertex_to_coordinate = {}
coordinate_to_vertex = {}

for base_vertex, orbit in enumerate(orbits):
    section = min(orbit)
    for coordinate, permutation in v4_permutations.items():
        vertex = permutation[section]
        vertex_to_base[vertex] = base_vertex
        vertex_to_coordinate[vertex] = coordinate
        coordinate_to_vertex[(base_vertex, coordinate)] = vertex

checks["CHECK_FIFTEEN_V4_FIBERS"] = (
    len(orbits) == 15
    and all(len(orbit) == 4 for orbit in orbits)
    and len(vertex_to_coordinate) == 60
)

print("== NATIVE V4 COORDINATES ==")
print("NORMAL_V4_CLASS_INDEX:", selected_v4_index)
print("V4_MEMBER_INDICES: [0, 65, 124, 326]")
print("V4_COORDINATE_BASIS: 65=(1,0), 124=(0,1)")
print("V4_PRODUCT_INDEX:", 326 if product == p326 else None)
print("V4_FIBER_COUNT:", len(orbits))
print("V4_FIBER_SIZE_PROFILE:", dict(Counter(map(len, orbits))))
print()

raw_edges = load_edges(G60_CSV)
native_delta_sets = {}

for x, y in raw_edges:
    u = vertex_to_base[x]
    v = vertex_to_base[y]
    edge = edge_key(u, v)
    delta = xor2(
        vertex_to_coordinate[x],
        vertex_to_coordinate[y],
    )
    native_delta_sets.setdefault(edge, set()).add(delta)

native_edges = set(native_delta_sets)
native_delta = {
    edge: next(iter(values))
    for edge, values in native_delta_sets.items()
    if len(values) == 1
}

lift_profile = Counter()
for edge in native_edges:
    lift_profile[sum(
        1
        for x, y in raw_edges
        if edge_key(
            vertex_to_base[x],
            vertex_to_base[y],
        ) == edge
    )] += 1

checks["CHECK_NATIVE_V4_DELTA_CONSISTENT"] = (
    len(native_delta) == 30
    and all(len(values) == 1 for values in native_delta_sets.values())
)
checks["CHECK_NATIVE_G15_PROFILE"] = (
    len(native_edges) == 30
    and lift_profile == Counter({4: 30})
)

print("== DERIVED NATIVE V4 VOLTAGE ==")
print("BASE_VERTEX_COUNT:", len(orbits))
print("BASE_EDGE_COUNT:", len(native_edges))
print(
    "G60_LIFTS_PER_BASE_EDGE_PROFILE:",
    json.dumps(dict(sorted(lift_profile.items()))),
)
print(
    "NATIVE_DELTA_VALUE_COUNTS:",
    json.dumps({
        str(list(value)): count
        for value, count in sorted(Counter(native_delta.values()).items())
    }),
)
for edge in sorted(native_delta):
    print(
        "NATIVE_V4_ROW:",
        json.dumps(
            {
                "g15_edge": list(edge),
                "v4_translation_delta": list(native_delta[edge]),
            },
            sort_keys=True,
            separators=(",", ":"),
        ),
    )
print()

print("PROGRESS: [3/5] reconstructing G60 and holonomy")

reconstructed = set()
for u, v in native_edges:
    delta = native_delta[(u, v)]
    for coordinate in v4_permutations:
        target_coordinate = xor2(coordinate, delta)
        reconstructed.add(edge_key(
            coordinate_to_vertex[(u, coordinate)],
            coordinate_to_vertex[(v, target_coordinate)],
        ))

missing = raw_edges - reconstructed
extra = reconstructed - raw_edges

checks["CHECK_EXACT_G60_RECONSTRUCTION"] = (
    len(reconstructed) == 120
    and not missing
    and not extra
)

tree, normalized = normalized_voltage(
    native_edges,
    native_delta,
)
chords = sorted(native_edges - tree)
holonomies = [normalized[edge] for edge in chords]

holonomy_span = {(0, 0)}
for value in holonomies:
    holonomy_span |= {
        xor2(old, value)
        for old in tuple(holonomy_span)
    }

checks["CHECK_G15_CYCLE_RANK_16"] = (
    len(tree) == 14
    and len(chords) == 16
)
checks["CHECK_V4_HOLONOMY_SURJECTIVE"] = (
    holonomy_span
    == {(0, 0), (1, 0), (0, 1), (1, 1)}
)

gauge_failure_count = 0
canonical_chord_profile = tuple(
    normalized[edge]
    for edge in chords
)

for switched_vertex in range(15):
    for switch_value in ((1, 0), (0, 1), (1, 1)):
        switched = {}
        for edge, value in native_delta.items():
            u, v = edge
            changed = value
            if u == switched_vertex:
                changed = xor2(changed, switch_value)
            if v == switched_vertex:
                changed = xor2(changed, switch_value)
            switched[edge] = changed

        _, switched_normal = normalized_voltage(
            native_edges,
            switched,
        )
        switched_profile = tuple(
            switched_normal[edge]
            for edge in chords
        )
        if switched_profile != canonical_chord_profile:
            gauge_failure_count += 1

checks["CHECK_TREE_NORMAL_FORM_GAUGE_INVARIANT"] = (
    gauge_failure_count == 0
)

print("== EXACT G60 RECONSTRUCTION ==")
print("RECONSTRUCTED_VERTEX_COUNT:", 60)
print("RECONSTRUCTED_EDGE_COUNT:", len(reconstructed))
print("MISSING_EDGE_COUNT:", len(missing))
print("EXTRA_EDGE_COUNT:", len(extra))
print(
    "CHECK_RECONSTRUCTED_G60_EQUALS_RAW_G60:",
    str(checks["CHECK_EXACT_G60_RECONSTRUCTION"]).lower(),
)
print()
print("== V4 HOLONOMY ==")
print("TREE_EDGE_COUNT:", len(tree))
print("CHORD_EDGE_COUNT:", len(chords))
print("BASE_CYCLE_RANK:", len(chords))
print(
    "FUNDAMENTAL_HOLONOMY_VALUE_COUNTS:",
    json.dumps({
        str(list(value)): count
        for value, count in sorted(Counter(holonomies).items())
    }),
)
print(
    "HOLONOMY_IMAGE:",
    json.dumps([list(value) for value in sorted(holonomy_span)]),
)
print("SINGLE_VERTEX_GAUGE_TEST_COUNT:", 45)
print("GAUGE_NORMAL_FORM_FAILURE_COUNT:", gauge_failure_count)
print()

print("PROGRESS: [4/5] comparing certificate033")

certificate = json.loads(CERT033.read_text())
certificate_delta = {
    edge_key(*row["g15_edge"]):
        tuple(row["v4_translation_delta"])
    for row in certificate["edge_rows"]
}
historical_edges = set(certificate_delta)

checks["CHECK_CERTIFICATE033_PASSES"] = (
    certificate["audit_pass"] is True
    and certificate["g15_vertex_count"] == 15
    and certificate["g15_edge_count"] == 30
    and len(certificate_delta) == 30
)
checks["CHECK_EXACT_LABELED_G15_EDGE_SET"] = (
    native_edges == historical_edges
)

isomorphisms = enumerate_isomorphisms(
    native_edges,
    historical_edges,
    15,
)

matches = []
identity_mapping = tuple(range(15))
identity_mapping_match_count = 0

for mapping in isomorphisms:
    for matrix in GL2:
        gauge = solve_gauge_equivalence(
            native_edges,
            native_delta,
            certificate_delta,
            mapping,
            matrix,
        )
        if gauge is None:
            continue

        row = {
            "mapping": mapping,
            "matrix": matrix,
            "gauge": gauge,
        }
        matches.append(row)
        if mapping == identity_mapping:
            identity_mapping_match_count += 1

matches.sort(
    key=lambda row: (
        row["mapping"],
        row["matrix"],
        row["gauge"],
    )
)

canonical = matches[0] if matches else None

checks["CHECK_G15_ISOMORPHISM_COUNT_120"] = (
    len(isomorphisms) == 120
)
checks["CHECK_CERTIFICATE033_GAUGE_EQUIVALENT"] = (
    len(matches) > 0
)
checks["CHECK_IDENTITY_LABELED_COMPARISON_MATCHES"] = (
    identity_mapping_match_count > 0
)

print("== CERTIFICATE033 COMPARISON ==")
print("QUOTIENT_GRAPH_ISOMORPHISM_COUNT:", len(isomorphisms))
print("GL2_BASIS_COUNT:", len(GL2))
print("COMPARISON_TEST_COUNT:", len(isomorphisms) * len(GL2))
print("GAUGE_EQUIVALENCE_MATCH_COUNT:", len(matches))
print(
    "IDENTITY_MAPPING_MATCH_COUNT:",
    identity_mapping_match_count,
)

if canonical is not None:
    print(
        "CANONICAL_QUOTIENT_TO_G15_MAP:",
        json.dumps({
            str(i): canonical["mapping"][i]
            for i in range(15)
        }, separators=(",", ":")),
    )
    print(
        "CANONICAL_GL2_MATRIX:",
        json.dumps([
            list(canonical["matrix"][:2]),
            list(canonical["matrix"][2:]),
        ], separators=(",", ":")),
    )
    print(
        "CANONICAL_VERTEX_GAUGE:",
        json.dumps([
            list(value)
            for value in canonical["gauge"]
        ], separators=(",", ":")),
    )
print()

print("PROGRESS: [5/5] theorem checks")

checks["CHECK_SOURCE_HASHES_LOCKED"] = all(
    checks[key]
    for key in checks
    if "HASH" in key or "COMMITTED_AT" in key
)

ordered_checks = (
    "CHECK_SOURCE_HASHES_LOCKED",
    "CHECK_PACKET007_SIDECAR_HASH",
    "CHECK_PACKET007_COMMITTED_AT_BBAE505",
    "CHECK_UNIQUE_NORMAL_V4_CLASS20",
    "CHECK_UNIQUE_NORMAL_C2_CLASS22",
    "CHECK_V4_PRODUCT_IS_NORMAL_C2",
    "CHECK_V4_MEMBER_ORDERS",
    "CHECK_FIFTEEN_V4_FIBERS",
    "CHECK_NATIVE_V4_DELTA_CONSISTENT",
    "CHECK_NATIVE_G15_PROFILE",
    "CHECK_EXACT_G60_RECONSTRUCTION",
    "CHECK_G15_CYCLE_RANK_16",
    "CHECK_V4_HOLONOMY_SURJECTIVE",
    "CHECK_TREE_NORMAL_FORM_GAUGE_INVARIANT",
    "CHECK_CERTIFICATE033_PASSES",
    "CHECK_EXACT_LABELED_G15_EDGE_SET",
    "CHECK_G15_ISOMORPHISM_COUNT_120",
    "CHECK_CERTIFICATE033_GAUGE_EQUIVALENT",
    "CHECK_IDENTITY_LABELED_COMPARISON_MATCHES",
)

failed_checks = [
    key
    for key in ordered_checks
    if not checks.get(key, False)
]

print("== THEOREM CHECKS ==")
for key in ordered_checks:
    print(key + ":", str(checks.get(key, False)).lower())
print("FAILED_CHECKS:", failed_checks)
print()

status_after = {
    str(root): git_status(root)
    for root in STATUS_ROOTS
}
status_preserved = status_before == status_after

print("== STATUS PRESERVATION ==")
for root in STATUS_ROOTS:
    key = str(root)
    print(
        "STATUS_CHECK:",
        json.dumps(
            {
                "root": key,
                "before": status_before[key],
                "after": status_after[key],
                "preserved":
                    status_before[key] == status_after[key],
            },
            sort_keys=True,
            separators=(",", ":"),
        ),
    )
print(
    "CHECK_ALL_REPOSITORY_STATUS_PRESERVED:",
    str(status_preserved).lower(),
)

if failed_checks or not status_preserved:
    raise RuntimeError("native V4 voltage comparison failed")

print()
print("THEOREM_PASS: true")
print(
    "FINAL_CLASSIFICATION:",
    "recovered_normal_V4_action_constructs_the_exact_native_"
    "G60_over_G15_voltage_lift_and_matches_certificate033_"
    "up_to_graph_symmetry_basis_and_gauge",
)
print(
    "THEOREM:",
    "The preregistered unique normal V4 action supplies fifteen "
    "four-state fibers and a native V4 voltage on every G15 edge. "
    "The regular lift reconstructs all 60 G60 vertices and all 120 "
    "edges exactly. Its circuit holonomy generates V4. After allowing "
    "G15 graph symmetry, V4 basis change, and vertex gauge, the derived "
    "voltage equals the independently preserved certificate033 voltage."
)
print(
    "BOUNDARY:",
    "The displayed edge coordinates depend on the chosen V4 generators "
    "and minimum-labeled section. Their gauge-equivalence class, full "
    "holonomy image, and reconstructed cover do not. V4 receipt and "
    "full-automorphism covariance remain declared selection premises. "
    "No orientation or physics interpretation is claimed."
)
print(
    "NEXT_GATE:",
    "Package the normal C2 and normal V4 recoveries as one exact native "
    "G60 to G30 to G15 receipt-tower theorem."
)
print(
    "KEEPER:",
    "The binary receipt found the first floor. The V4 receipt recovered "
    "the whole tower and rebuilt the graph."
)
print("MUTATION_PERFORMED: false")
