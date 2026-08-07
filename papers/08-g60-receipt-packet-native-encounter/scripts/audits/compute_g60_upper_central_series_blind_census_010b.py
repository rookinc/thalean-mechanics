import csv
import hashlib
import json
import subprocess
import sys
from array import array
from collections import Counter
from datetime import datetime
from pathlib import Path

project = Path(sys.argv[1]).resolve()
action_path = Path(sys.argv[2]).resolve()
edge_path = Path(sys.argv[3]).resolve()
output_path = Path(sys.argv[4]).resolve()

expected_action_sha = (
    "b37313b135495752b11e525bb61979163fdf54aec4be4f5d027dcee64c9efc21"
)
expected_edge_sha = (
    "c700a185fab6a5f434da09b7acb716b96c76170774bee946af8ea907e4fe7f9f"
)
expected_prereg_sha = (
    "f43a9d1b3e97133d62d6f1b193409617226c63caba304e7613de4745182be2ea"
)

prereg_path = (
    project
    / "artifacts/json"
    / "g60_upper_central_receipt_selector_preregistration_010a.v1.json"
)

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
    inv = [None] * 60
    for v, image in enumerate(p):
        inv[image] = v
    return tuple(inv)

def counter_dict(values):
    return {
        str(key): count
        for key, count in sorted(Counter(values).items())
    }

status_before = git_output("status", "--short")
head_before = git_output("--no-pager", "show", "-s", "--oneline", "HEAD")

action_sha = sha256_file(action_path)
edge_sha = sha256_file(edge_path)
prereg_sha = sha256_file(prereg_path)

with prereg_path.open("r", encoding="utf-8") as handle:
    prereg = json.load(handle)

with action_path.open("r", encoding="utf-8") as handle:
    action_data = json.load(handle)

source_rows = action_data["mapping_rows"]
mapping_row_count = len(source_rows)
group_order = mapping_row_count

rows_by_index = {}
schema_failures = []

for row in source_rows:
    allowed = {
        "actual_index": row["actual_index"],
        "actual_permutation": row["actual_permutation"],
        "actual_order": row.get("actual_order"),
    }
    index = allowed["actual_index"]
    permutation = tuple(allowed["actual_permutation"])

    if index in rows_by_index:
        schema_failures.append("duplicate_actual_index:" + str(index))
    if len(permutation) != 60:
        schema_failures.append("bad_permutation_length:" + str(index))
    elif sorted(permutation) != list(range(60)):
        schema_failures.append("not_a_permutation:" + str(index))

    rows_by_index[index] = allowed

index_coverage_ok = sorted(rows_by_index) == list(range(group_order))
if not index_coverage_ok:
    schema_failures.append("actual_index_coverage_failure")

permutations = [
    tuple(rows_by_index[i]["actual_permutation"])
    for i in range(group_order)
]
declared_orders = [
    rows_by_index[i]["actual_order"]
    for i in range(group_order)
]

permutation_to_index = {
    permutation: index
    for index, permutation in enumerate(permutations)
}
duplicate_permutation_failures = group_order - len(permutation_to_index)

identity_permutation = tuple(range(60))
identity_candidates = [
    index
    for index, permutation in enumerate(permutations)
    if permutation == identity_permutation
]
identity_index = identity_candidates[0] if len(identity_candidates) == 1 else None

print("== G60 UPPER-CENTRAL BLIND CENSUS 010b ==")
print("MODE: read-only blind Phase A candidate")
print("PROJECT_MUTATION: none")
print("HISTORICAL_REFERENCE_FIELDS_ACCESSED: false")
print("PRIOR_CLASS_IDENTITIES_ACCESSED: false")
print("PRIOR_VOLTAGE_CERTIFICATES_ACCESSED: false")
print("ACTION_SHA256:", action_sha)
print("RAW_EDGE_SHA256:", edge_sha)
print("PREREGISTRATION_SHA256:", prereg_sha)
print("MAPPING_ROW_COUNT:", mapping_row_count)
print("PERMUTATION_DICTIONARY_SIZE:", len(permutation_to_index))
print("IDENTITY_CANDIDATE_COUNT:", len(identity_candidates))
print("IDENTITY_INDEX:", identity_index)
print()

sentinel = 65535
multiplication = []
closure_failures = []
product_lookup_mismatch_count = 0

print("MULTIPLICATION_TABLE_BEGIN")
for left in range(group_order):
    if left % 40 == 0:
        print("MULTIPLICATION_PROGRESS:", left, "/", group_order)
    p = permutations[left]
    products = array("H")
    for right in range(group_order):
        product_permutation = compose(p, permutations[right])
        product_index = permutation_to_index.get(product_permutation)
        if product_index is None:
            products.append(sentinel)
            if len(closure_failures) < 20:
                closure_failures.append([left, right])
        else:
            products.append(product_index)
            if permutations[product_index] != product_permutation:
                product_lookup_mismatch_count += 1
    multiplication.append(products)
print("MULTIPLICATION_PROGRESS:", group_order, "/", group_order)
print("MULTIPLICATION_TABLE_END")
print()

closure_failure_count = sum(
    1
    for row in multiplication
    for value in row
    if value == sentinel
)

identity_law_failures = []
if identity_index is not None and closure_failure_count == 0:
    for index in range(group_order):
        if multiplication[identity_index][index] != index:
            identity_law_failures.append(["left", index])
        if multiplication[index][identity_index] != index:
            identity_law_failures.append(["right", index])

inverse_indices = [None] * group_order
inverse_failures = []

if closure_failure_count == 0 and identity_index is not None:
    for index, permutation in enumerate(permutations):
        inverse_index = permutation_to_index.get(
            inverse_permutation(permutation)
        )
        if inverse_index is None:
            inverse_failures.append([index, "inverse_not_in_action"])
            continue
        inverse_indices[index] = inverse_index
        if multiplication[index][inverse_index] != identity_index:
            inverse_failures.append([index, "right_inverse_failure"])
        if multiplication[inverse_index][index] != identity_index:
            inverse_failures.append([index, "left_inverse_failure"])

def computed_element_order(index):
    current = identity_index
    for exponent in range(1, group_order + 1):
        current = multiplication[current][index]
        if current == identity_index:
            return exponent
    return None

computed_orders = [None] * group_order
order_consistency_failures = []

if not inverse_failures and closure_failure_count == 0:
    for index in range(group_order):
        order = computed_element_order(index)
        computed_orders[index] = order
        declared = declared_orders[index]
        if declared is not None and declared != order:
            order_consistency_failures.append(
                [index, declared, order]
            )

multiplication_consistency_failure_count = (
    len(schema_failures)
    + duplicate_permutation_failures
    + product_lookup_mismatch_count
    + len(identity_law_failures)
    + len(order_consistency_failures)
)

operation_ok = (
    action_sha == expected_action_sha
    and edge_sha == expected_edge_sha
    and prereg_sha == expected_prereg_sha
    and prereg["preregistration_status"]
        == "frozen_before_central_computation"
    and group_order == 480
    and not schema_failures
    and duplicate_permutation_failures == 0
    and len(identity_candidates) == 1
    and closure_failure_count == 0
    and not identity_law_failures
    and not inverse_failures
    and product_lookup_mismatch_count == 0
    and not order_consistency_failures
)

z1 = []
z2 = []
z3 = []

def commutator_index(g, h):
    value = multiplication[inverse_indices[g]][inverse_indices[h]]
    value = multiplication[value][g]
    value = multiplication[value][h]
    return value

if operation_ok:
    print("CENTER_SCAN_BEGIN")
    for candidate in range(group_order):
        if candidate % 40 == 0:
            print("CENTER_PROGRESS:", candidate, "/", group_order)
        if all(
            multiplication[candidate][other]
            == multiplication[other][candidate]
            for other in range(group_order)
        ):
            z1.append(candidate)
    print("CENTER_PROGRESS:", group_order, "/", group_order)
    print("CENTER_SCAN_END")
    print()

    z1_set = set(z1)

    print("SECOND_CENTER_SCAN_BEGIN")
    for candidate in range(group_order):
        if candidate % 40 == 0:
            print("SECOND_CENTER_PROGRESS:", candidate, "/", group_order)
        if all(
            commutator_index(candidate, other) in z1_set
            for other in range(group_order)
        ):
            z2.append(candidate)
    print("SECOND_CENTER_PROGRESS:", group_order, "/", group_order)
    print("SECOND_CENTER_SCAN_END")
    print()

    z2_set = set(z2)

    print("THIRD_CENTER_SCAN_BEGIN")
    for candidate in range(group_order):
        if candidate % 40 == 0:
            print("THIRD_CENTER_PROGRESS:", candidate, "/", group_order)
        if all(
            commutator_index(candidate, other) in z2_set
            for other in range(group_order)
        ):
            z3.append(candidate)
    print("THIRD_CENTER_PROGRESS:", group_order, "/", group_order)
    print("THIRD_CENTER_SCAN_END")
    print()

with edge_path.open("r", encoding="utf-8", newline="") as handle:
    reader = csv.DictReader(handle)
    edges = [
        tuple(sorted((int(row["local_u"]), int(row["local_v"]))))
        for row in reader
    ]

edge_set = set(edges)
adjacency = [set() for _ in range(60)]
for u, v in edges:
    adjacency[u].add(v)
    adjacency[v].add(u)

graph_action_failure_count = 0
graph_action_failure_examples = []

for index, permutation in enumerate(permutations):
    for u, v in edges:
        image = tuple(sorted((permutation[u], permutation[v])))
        if image not in edge_set:
            graph_action_failure_count += 1
            if len(graph_action_failure_examples) < 20:
                graph_action_failure_examples.append(
                    [index, [u, v], list(image)]
                )

def vertex_orbits(subgroup):
    unseen = set(range(60))
    orbits = []
    while unseen:
        seed = min(unseen)
        orbit = {
            permutations[element][seed]
            for element in subgroup
        }
        orbits.append(sorted(orbit))
        unseen.difference_update(orbit)
    return orbits

def edge_orbits(subgroup):
    unseen = set(edges)
    orbits = []
    while unseen:
        seed = min(unseen)
        orbit = {
            tuple(sorted((
                permutations[element][seed[0]],
                permutations[element][seed[1]],
            )))
            for element in subgroup
        }
        orbits.append(sorted([list(edge) for edge in orbit]))
        unseen.difference_update(orbit)
    return orbits

def action_profile(name, subgroup):
    subgroup_set = set(subgroup)
    vorbits = vertex_orbits(subgroup)
    eorbits = edge_orbits(subgroup)

    fixed_point_members = {}
    edge_inversion_members = {}

    for element in subgroup:
        if element == identity_index:
            continue

        fixed = [
            vertex
            for vertex in range(60)
            if permutations[element][vertex] == vertex
        ]
        if fixed:
            fixed_point_members[str(element)] = fixed

        inverted = []
        for edge_number, (u, v) in enumerate(edges):
            if (
                permutations[element][u] == v
                and permutations[element][v] == u
            ):
                inverted.append(edge_number)
        if inverted:
            edge_inversion_members[str(element)] = inverted

    orbit_id = {}
    for number, orbit in enumerate(vorbits):
        for vertex in orbit:
            orbit_id[vertex] = number

    quotient_edge_multiplicity = Counter()
    quotient_loops = []
    for u, v in edges:
        a = orbit_id[u]
        b = orbit_id[v]
        if a == b:
            quotient_loops.append([u, v])
        else:
            quotient_edge_multiplicity[tuple(sorted((a, b)))] += 1

    quotient_neighbors = [set() for _ in vorbits]
    for a, b in quotient_edge_multiplicity:
        quotient_neighbors[a].add(b)
        quotient_neighbors[b].add(a)

    local_covering_failures = []
    for vertex in range(60):
        source_orbit = orbit_id[vertex]
        neighbor_orbit_counts = Counter(
            orbit_id[neighbor]
            for neighbor in adjacency[vertex]
        )
        expected = quotient_neighbors[source_orbit]
        if (
            set(neighbor_orbit_counts) != expected
            or any(count != 1 for count in neighbor_orbit_counts.values())
        ):
            local_covering_failures.append({
                "vertex": vertex,
                "source_orbit": source_orbit,
                "neighbor_orbit_counts": {
                    str(k): v
                    for k, v in sorted(neighbor_orbit_counts.items())
                },
                "expected_neighbor_orbits": sorted(expected),
            })

    expected_multiplicity = len(subgroup)
    edge_multiplicity_failures = [
        {
            "quotient_edge": list(pair),
            "multiplicity": multiplicity,
            "expected": expected_multiplicity,
        }
        for pair, multiplicity
        in sorted(quotient_edge_multiplicity.items())
        if multiplicity != expected_multiplicity
    ]

    incremental_orders = [
        computed_orders[element]
        for element in subgroup
        if computed_orders[element] is not None
    ]

    return {
        "name": name,
        "member_indices": sorted(subgroup),
        "order": len(subgroup),
        "element_order_profile": counter_dict(incremental_orders),
        "vertex_orbit_count": len(vorbits),
        "vertex_orbit_size_profile": counter_dict(
            len(orbit) for orbit in vorbits
        ),
        "vertex_orbits": vorbits,
        "semiregular": not fixed_point_members,
        "fixed_point_failure_member_count": len(fixed_point_members),
        "fixed_point_failures": fixed_point_members,
        "edge_orbit_count": len(eorbits),
        "edge_orbit_size_profile": counter_dict(
            len(orbit) for orbit in eorbits
        ),
        "edge_inversion_failure_member_count": len(edge_inversion_members),
        "edge_inversion_failures": edge_inversion_members,
        "quotient_vertex_count": len(vorbits),
        "quotient_edge_count": len(quotient_edge_multiplicity),
        "quotient_loop_count": len(quotient_loops),
        "quotient_degree_profile": counter_dict(
            len(neighbors) for neighbors in quotient_neighbors
        ),
        "quotient_edge_multiplicity_profile": counter_dict(
            quotient_edge_multiplicity.values()
        ),
        "local_covering_failure_count": len(local_covering_failures),
        "local_covering_failures_first_20": local_covering_failures[:20],
        "edge_multiplicity_failure_count": len(edge_multiplicity_failures),
        "edge_multiplicity_failures_first_20": edge_multiplicity_failures[:20],
        "subgroup_contains_identity": identity_index in subgroup_set,
    }

central_profiles = {}
increment_profiles = {}

if operation_ok and graph_action_failure_count == 0:
    central_profiles = {
        "Z1": action_profile("Z1", z1),
        "Z2": action_profile("Z2", z2),
        "Z3": action_profile("Z3", z3),
    }
    increment_profiles = {
        "Z1": counter_dict(computed_orders[i] for i in z1),
        "Z2_minus_Z1": counter_dict(
            computed_orders[i] for i in sorted(set(z2) - set(z1))
        ),
        "Z3_minus_Z2": counter_dict(
            computed_orders[i] for i in sorted(set(z3) - set(z2))
        ),
    }

if not operation_ok:
    outcome = "computation_failure"
elif len(z1) != 2:
    outcome = "unexpected_center"
elif set(z2) == set(z1):
    outcome = "center_only"
elif len(z2) == 4:
    outcome = "exact_target"
elif len(z2) > 4:
    outcome = "larger_second_center"
else:
    outcome = "computation_failure"

central_action_checks_pass = bool(central_profiles) and all(
    profile["semiregular"]
    and profile["edge_inversion_failure_member_count"] == 0
    and profile["local_covering_failure_count"] == 0
    and profile["edge_multiplicity_failure_count"] == 0
    for profile in central_profiles.values()
)

status_after = git_output("status", "--short")
head_after = git_output("--no-pager", "show", "-s", "--oneline", "HEAD")

repository_status_preserved = (
    status_before == status_after
    and head_before == head_after
)

result = {
    "packet": "g60_upper_central_series_blind_census_010b",
    "version": 1,
    "created_at": datetime.now().astimezone().isoformat(),
    "mode": "read_only_blind_phase_a_candidate",
    "authorities": {
        "action_path": str(action_path),
        "action_sha256": action_sha,
        "action_hash_match": action_sha == expected_action_sha,
        "raw_edge_path": str(edge_path),
        "raw_edge_sha256": edge_sha,
        "raw_edge_hash_match": edge_sha == expected_edge_sha,
        "preregistration_path": str(prereg_path),
        "preregistration_sha256": prereg_sha,
        "preregistration_hash_match": prereg_sha == expected_prereg_sha,
    },
    "blindness": {
        "action_fields_accessed": [
            "actual_index",
            "actual_permutation",
            "actual_order",
        ],
        "historical_reference_fields_accessed": False,
        "prior_class_identities_accessed": False,
        "prior_quotient_labels_accessed": False,
        "prior_voltage_certificates_accessed": False,
        "phase_b_unblinding_performed": False,
    },
    "group_reconstruction": {
        "composition_convention": "compose(p,q)[v] = p[q[v]]",
        "commutator_convention": "inverse(g)*inverse(h)*g*h",
        "mapping_row_count": mapping_row_count,
        "group_order": group_order,
        "permutation_dictionary_size": len(permutation_to_index),
        "identity_candidate_count": len(identity_candidates),
        "identity_index": identity_index,
        "schema_failure_count": len(schema_failures),
        "schema_failures": schema_failures,
        "duplicate_permutation_failure_count": duplicate_permutation_failures,
        "closure_failure_count": closure_failure_count,
        "closure_failures_first_20": closure_failures,
        "inverse_failure_count": len(inverse_failures),
        "inverse_failures_first_20": inverse_failures[:20],
        "identity_law_failure_count": len(identity_law_failures),
        "identity_law_failures_first_20": identity_law_failures[:20],
        "product_lookup_mismatch_count": product_lookup_mismatch_count,
        "declared_order_consistency_failure_count": len(order_consistency_failures),
        "declared_order_consistency_failures_first_20": order_consistency_failures[:20],
        "multiplication_consistency_failure_count": multiplication_consistency_failure_count,
        "associativity_source": "Exact permutation composition.",
        "operation_reconstruction_ok": operation_ok,
    },
    "central_series": {
        "center_order": len(z1),
        "center_member_indices": z1,
        "second_center_order": len(z2),
        "second_center_member_indices": z2,
        "third_center_order": len(z3),
        "third_center_member_indices": z3,
        "Z1_subset_Z2": set(z1).issubset(z2),
        "Z2_subset_Z3": set(z2).issubset(z3),
        "increment_element_order_profiles": increment_profiles,
    },
    "native_graph_action": {
        "raw_vertex_count": 60,
        "raw_edge_count": len(edges),
        "full_action_graph_automorphism_failure_count": graph_action_failure_count,
        "full_action_graph_automorphism_failures_first_20": graph_action_failure_examples,
        "central_layer_profiles": central_profiles,
        "central_action_checks_pass": central_action_checks_pass,
    },
    "classification": {
        "preregistered_outcome": outcome,
        "outcome_predicate_changed_after_result": False,
        "replacement_selector_searched": False,
        "smallest_order_selector_used": False,
    },
    "repository_preservation": {
        "head_before": head_before,
        "head_after": head_after,
        "status_before_sha256": status_hash(status_before),
        "status_after_sha256": status_hash(status_after),
        "status_before_row_count": len(status_before.splitlines()),
        "status_after_row_count": len(status_after.splitlines()),
        "repository_status_preserved": repository_status_preserved,
        "project_mutation_performed": False,
    },
    "boundary": {
        "candidate_report_only": True,
        "phase_a_result_frozen": False,
        "phase_b_allowed_now": False,
        "unblinding_performed": False,
        "historical_tower_comparison_performed": False,
        "manuscript_mutated": False,
        "orientation_claim": False,
        "geometry_claim": False,
        "physical_claim": False,
        "theorem_claim": False,
    },
}

output_path.parent.mkdir(parents=True, exist_ok=True)
output_path.write_text(
    json.dumps(result, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

print("== FINAL BLIND CENSUS REPORT ==")
print("PACKET:", result["packet"])
print("ACTION_HASH_MATCH:", str(action_sha == expected_action_sha).lower())
print("RAW_EDGE_HASH_MATCH:", str(edge_sha == expected_edge_sha).lower())
print("PREREGISTRATION_HASH_MATCH:", str(prereg_sha == expected_prereg_sha).lower())
print("MAPPING_ROW_COUNT:", mapping_row_count)
print("GROUP_ORDER:", group_order)
print("IDENTITY_INDEX:", identity_index)
print("CLOSURE_FAILURE_COUNT:", closure_failure_count)
print("INVERSE_FAILURE_COUNT:", len(inverse_failures))
print("MULTIPLICATION_CONSISTENCY_FAILURE_COUNT:", multiplication_consistency_failure_count)
print("DECLARED_ORDER_CONSISTENCY_FAILURE_COUNT:", len(order_consistency_failures))
print("OPERATION_RECONSTRUCTION_OK:", str(operation_ok).lower())
print("CENTER_ORDER:", len(z1))
print("CENTER_MEMBER_INDICES:", z1)
print("SECOND_CENTER_ORDER:", len(z2))
print("SECOND_CENTER_MEMBER_INDICES:", z2)
print("THIRD_CENTER_ORDER:", len(z3))
print("THIRD_CENTER_MEMBER_INDICES:", z3)
print("Z1_SUBSET_Z2:", str(set(z1).issubset(z2)).lower())
print("Z2_SUBSET_Z3:", str(set(z2).issubset(z3)).lower())
print("INCREMENT_ELEMENT_ORDER_PROFILES:", json.dumps(increment_profiles, sort_keys=True))
print("FULL_ACTION_GRAPH_AUTOMORPHISM_FAILURE_COUNT:", graph_action_failure_count)

for layer in ("Z1", "Z2", "Z3"):
    profile = central_profiles.get(layer)
    if profile is None:
        continue
    print(layer + "_ELEMENT_ORDER_PROFILE:", profile["element_order_profile"])
    print(layer + "_VERTEX_ORBIT_COUNT:", profile["vertex_orbit_count"])
    print(layer + "_VERTEX_ORBIT_SIZE_PROFILE:", profile["vertex_orbit_size_profile"])
    print(layer + "_SEMIREGULAR:", str(profile["semiregular"]).lower())
    print(layer + "_EDGE_ORBIT_COUNT:", profile["edge_orbit_count"])
    print(layer + "_EDGE_ORBIT_SIZE_PROFILE:", profile["edge_orbit_size_profile"])
    print(layer + "_EDGE_INVERSION_FAILURE_MEMBER_COUNT:", profile["edge_inversion_failure_member_count"])
    print(layer + "_QUOTIENT_VERTEX_COUNT:", profile["quotient_vertex_count"])
    print(layer + "_QUOTIENT_EDGE_COUNT:", profile["quotient_edge_count"])
    print(layer + "_QUOTIENT_LOOP_COUNT:", profile["quotient_loop_count"])
    print(layer + "_QUOTIENT_DEGREE_PROFILE:", profile["quotient_degree_profile"])
    print(layer + "_LOCAL_COVERING_FAILURE_COUNT:", profile["local_covering_failure_count"])
    print(layer + "_EDGE_MULTIPLICITY_FAILURE_COUNT:", profile["edge_multiplicity_failure_count"])

print("CENTRAL_ACTION_CHECKS_PASS:", str(central_action_checks_pass).lower())
print("PREREGISTERED_OUTCOME_CLASSIFICATION:", outcome)
print("REPLACEMENT_SELECTOR_SEARCHED: false")
print("SMALLEST_ORDER_SELECTOR_USED: false")
print("REPOSITORY_STATUS_PRESERVED:", str(repository_status_preserved).lower())
print("PROJECT_MUTATION_PERFORMED: false")
print("PHASE_A_RESULT_FROZEN: false")
print("PHASE_B_ALLOWED_NOW: false")
print("UNBLINDING_PERFORMED: false")
print("MANUSCRIPT_MUTATED: false")
print("THEOREM_CLAIM: false")
print("CANDIDATE_JSON:", output_path)
print("CANDIDATE_JSON_SHA256:", sha256_file(output_path))
