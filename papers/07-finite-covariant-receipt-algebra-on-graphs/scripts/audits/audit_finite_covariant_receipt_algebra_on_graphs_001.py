#!/usr/bin/env python3
from __future__ import annotations

import itertools
from collections import deque
from dataclasses import dataclass


@dataclass(frozen=True)
class FiniteGroup:
    name: str
    elements: tuple[object, ...]
    mul: tuple[tuple[int, ...], ...]
    inv: tuple[int, ...]

    @property
    def order(self) -> int:
        return len(self.elements)

    def product(self, values) -> int:
        out = 0
        for value in values:
            out = self.mul[out][value]
        return out

    def element_order(self, value: int) -> int:
        out = 0
        for exponent in range(1, self.order + 1):
            out = self.mul[out][value]
            if out == 0:
                return exponent
        raise AssertionError("element order exceeded group order")


@dataclass(frozen=True)
class BaseGraph:
    name: str
    vertex_count: int
    edges: tuple[tuple[int, int], ...]

    @property
    def cycle_rank(self) -> int:
        return len(self.edges) - self.vertex_count + 1

    def adjacency(self):
        rows = [[] for _ in range(self.vertex_count)]
        for edge_index, (u, v) in enumerate(self.edges):
            rows[u].append((v, edge_index, 1))
            rows[v].append((u, edge_index, -1))
        for row in rows:
            row.sort()
        return rows


def table_group(name: str, elements: list[object], operation) -> FiniteGroup:
    index = {value: i for i, value in enumerate(elements)}
    if elements[0] != operation(elements[0], elements[0]):
        raise AssertionError(f"{name}: identity must be first")
    mul = tuple(
        tuple(index[operation(a, b)] for b in elements)
        for a in elements
    )
    inv = []
    for i in range(len(elements)):
        matches = [j for j in range(len(elements)) if mul[i][j] == 0 and mul[j][i] == 0]
        if len(matches) != 1:
            raise AssertionError(f"{name}: inverse failure")
        inv.append(matches[0])
    return FiniteGroup(name, tuple(elements), mul, tuple(inv))


def cyclic(order: int) -> FiniteGroup:
    return table_group(f"C{order}", list(range(order)), lambda a, b: (a + b) % order)


def klein_four() -> FiniteGroup:
    elements = [(0, 0), (1, 0), (0, 1), (1, 1)]
    return table_group("V4", elements, lambda a, b: (a[0] ^ b[0], a[1] ^ b[1]))


def symmetric_three() -> FiniteGroup:
    identity = (0, 1, 2)
    elements = [identity] + [p for p in itertools.permutations(range(3)) if p != identity]
    return table_group("S3", elements, lambda p, q: tuple(p[q[i]] for i in range(3)))


def dihedral_eight() -> FiniteGroup:
    elements = [(0, 0)] + [(k, e) for e in range(2) for k in range(4) if (k, e) != (0, 0)]

    def operation(a, b):
        k, e = a
        ell, f = b
        return ((k + (ell if e == 0 else -ell)) % 4, e ^ f)

    return table_group("D8", elements, operation)


def oriented_voltage(group: FiniteGroup, graph: BaseGraph, voltage, edge_index: int, direction: int) -> int:
    value = voltage[edge_index]
    return value if direction == 1 else group.inv[value]


def spanning_tree(graph: BaseGraph, root: int):
    adjacency = graph.adjacency()
    parent = {root: None}
    parent_step = {}
    queue = deque([root])
    tree_edges = set()
    while queue:
        u = queue.popleft()
        for v, edge_index, direction in adjacency[u]:
            if v in parent:
                continue
            parent[v] = u
            parent_step[v] = (edge_index, direction)
            tree_edges.add(edge_index)
            queue.append(v)
    if len(parent) != graph.vertex_count:
        raise AssertionError(f"{graph.name}: disconnected")
    return parent, parent_step, tree_edges


def normalize(group: FiniteGroup, graph: BaseGraph, voltage, root: int):
    parent, parent_step, tree_edges = spanning_tree(graph, root)
    children = [[] for _ in range(graph.vertex_count)]
    for child, par in parent.items():
        if par is not None:
            children[par].append(child)
    gauge = [0] * graph.vertex_count
    queue = deque([root])
    while queue:
        u = queue.popleft()
        for child in sorted(children[u]):
            edge_index, direction = parent_step[child]
            receipt = oriented_voltage(group, graph, voltage, edge_index, direction)
            gauge[child] = group.mul[group.inv[receipt]][gauge[u]]
            queue.append(child)

    normalized = []
    for edge_index, (u, v) in enumerate(graph.edges):
        value = group.mul[group.mul[group.inv[gauge[u]]][voltage[edge_index]]][gauge[v]]
        normalized.append(value)
    cotree = tuple(i for i in range(len(graph.edges)) if i not in tree_edges)
    generators = tuple(normalized[i] for i in cotree)
    return tuple(normalized), tuple(gauge), tuple(sorted(tree_edges)), generators


def generated_subgroup(group: FiniteGroup, generators) -> frozenset[int]:
    values = {0}
    values.update(generators)
    values.update(group.inv[g] for g in generators)
    changed = True
    while changed:
        changed = False
        current = tuple(values)
        for a in current:
            for b in current:
                value = group.mul[a][b]
                if value not in values:
                    values.add(value)
                    changed = True
    return frozenset(values)


def conjugate_value(group: FiniteGroup, value: int, by: int) -> int:
    return group.mul[group.mul[group.inv[by]][value]][by]


def canonical_representation(group: FiniteGroup, generators) -> tuple[int, ...]:
    return min(
        tuple(conjugate_value(group, value, by) for value in generators)
        for by in range(group.order)
    )


def canonical_subgroup(group: FiniteGroup, subgroup) -> tuple[int, ...]:
    return min(
        tuple(sorted(conjugate_value(group, value, by) for value in subgroup))
        for by in range(group.order)
    )


def gauge_transform(group: FiniteGroup, graph: BaseGraph, voltage, gauge):
    transformed = []
    for edge_index, (u, v) in enumerate(graph.edges):
        transformed.append(
            group.mul[group.mul[group.inv[gauge[u]]][voltage[edge_index]]][gauge[v]]
        )
    return tuple(transformed)


def lifted_components(group: FiniteGroup, graph: BaseGraph, voltage):
    adjacency = graph.adjacency()
    seen = set()
    sizes = []
    for start_v in range(graph.vertex_count):
        for start_x in range(group.order):
            start = (start_v, start_x)
            if start in seen:
                continue
            queue = deque([start])
            seen.add(start)
            size = 0
            while queue:
                u, x = queue.popleft()
                size += 1
                for v, edge_index, direction in adjacency[u]:
                    receipt = oriented_voltage(group, graph, voltage, edge_index, direction)
                    state = (v, group.mul[x][receipt])
                    if state not in seen:
                        seen.add(state)
                        queue.append(state)
            sizes.append(size)
    return tuple(sorted(sizes))


def main() -> None:
    print("OUT ==")
    print("PACKET: finite_covariant_receipt_algebra_on_graphs_audit_001")
    print("MODE: read-only exhaustive regular graph-lift audit")
    print("REPOSITORY_MUTATION: none")
    print()

    graphs = {
        "P4": BaseGraph("P4_tree", 4, ((0, 1), (1, 2), (2, 3))),
        "C3": BaseGraph("C3", 3, ((0, 1), (1, 2), (0, 2))),
        "C4": BaseGraph("C4", 4, ((0, 1), (1, 2), (2, 3), (0, 3))),
        "THETA": BaseGraph("theta_rank2", 4, ((0, 1), (0, 2), (1, 2), (0, 3), (1, 3))),
        "BOWTIE": BaseGraph("two_triangle_bouquet", 5, ((0, 1), (1, 2), (0, 2), (0, 3), (3, 4), (0, 4))),
    }
    groups = {
        "C2": cyclic(2),
        "C3": cyclic(3),
        "V4": klein_four(),
        "S3": symmetric_three(),
        "D8": dihedral_eight(),
    }
    cases = []
    for graph_key in ("P4", "C3"):
        for group_key in groups:
            cases.append((graphs[graph_key], groups[group_key]))
    for graph_key in ("C4", "THETA", "BOWTIE"):
        for group_key in ("C2", "C3", "V4", "S3"):
            cases.append((graphs[graph_key], groups[group_key]))

    assignment_total = 0
    tree_failure_count = 0
    classification_failure_count = 0
    component_failure_count = 0
    component_size_failure_count = 0
    connectedness_failure_count = 0
    gauge_failure_count = 0
    root_failure_count = 0
    cycle_specialization_failure_count = 0
    generator_rank_failure_count = 0
    rows = []

    print("== EXHAUSTIVE CASE PROGRESS ==")
    for case_index, (graph, group) in enumerate(cases, start=1):
        expected_rep_classes = {
            canonical_representation(group, generators)
            for generators in itertools.product(range(group.order), repeat=graph.cycle_rank)
        }
        observed_rep_classes = set()
        observed_profiles = set()
        connected_assignment_count = 0
        assignment_count = group.order ** len(graph.edges)

        for voltage in itertools.product(range(group.order), repeat=len(graph.edges)):
            assignment_total += 1
            normalized, _, tree_edges, generators = normalize(group, graph, voltage, 0)
            if any(normalized[i] != 0 for i in tree_edges):
                tree_failure_count += 1

            rep_class = canonical_representation(group, generators)
            observed_rep_classes.add(rep_class)
            subgroup = generated_subgroup(group, generators)
            expected_component_count = group.order // len(subgroup)
            expected_component_size = graph.vertex_count * len(subgroup)
            actual_sizes = lifted_components(group, graph, voltage)
            observed_profiles.add(actual_sizes)
            if len(actual_sizes) != expected_component_count:
                component_failure_count += 1
            if actual_sizes != tuple([expected_component_size] * expected_component_count):
                component_size_failure_count += 1

            connected = len(actual_sizes) == 1
            if connected != (subgroup == frozenset(range(group.order))):
                connectedness_failure_count += 1
            if connected:
                connected_assignment_count += 1
                if len(generators) < 1 and group.order > 1:
                    generator_rank_failure_count += 1
                if generated_subgroup(group, generators) != frozenset(range(group.order)):
                    generator_rank_failure_count += 1

            gauge = tuple((sum(voltage) + 2 * vertex + 1) % group.order for vertex in range(graph.vertex_count))
            transformed = gauge_transform(group, graph, voltage, gauge)
            _, _, _, transformed_generators = normalize(group, graph, transformed, 0)
            if canonical_representation(group, transformed_generators) != rep_class:
                gauge_failure_count += 1

            _, _, _, root_generators = normalize(group, graph, voltage, graph.vertex_count - 1)
            root_subgroup = generated_subgroup(group, root_generators)
            if canonical_subgroup(group, root_subgroup) != canonical_subgroup(group, subgroup):
                root_failure_count += 1

            if graph.cycle_rank == 1:
                generator = generators[0]
                expected_size = graph.vertex_count * group.element_order(generator)
                if any(size != expected_size for size in actual_sizes):
                    cycle_specialization_failure_count += 1

        if observed_rep_classes != expected_rep_classes:
            classification_failure_count += 1

        row = {
            "graph": graph.name,
            "vertices": graph.vertex_count,
            "edges": len(graph.edges),
            "cycle_rank": graph.cycle_rank,
            "group": group.name,
            "group_order": group.order,
            "assignments": assignment_count,
            "representation_classes": len(observed_rep_classes),
            "component_profiles": len(observed_profiles),
            "connected_assignments": connected_assignment_count,
        }
        rows.append(row)
        failures = (
            tree_failure_count
            + classification_failure_count
            + component_failure_count
            + component_size_failure_count
            + connectedness_failure_count
            + gauge_failure_count
            + root_failure_count
            + cycle_specialization_failure_count
            + generator_rank_failure_count
        )
        print(
            f"PROGRESS: [{case_index}/{len(cases)}] graph={graph.name} group={group.name} "
            f"assignments={assignment_count} failures={failures}"
        )

    print()
    print("== CASE CENSUS ==")
    for row in rows:
        print("CASE:", row)

    failed_checks = {
        "tree_normalization": tree_failure_count,
        "representation_classification": classification_failure_count,
        "component_count": component_failure_count,
        "component_size": component_size_failure_count,
        "connectedness": connectedness_failure_count,
        "gauge_covariance": gauge_failure_count,
        "root_invariance": root_failure_count,
        "cycle_specialization": cycle_specialization_failure_count,
        "generator_rank": generator_rank_failure_count,
    }

    print()
    print("== THEOREM CHECKS ==")
    print("BASE_GRAPH_COUNT:", len(graphs))
    print("RECEIPT_GROUP_COUNT:", len(groups))
    print("GRAPH_GROUP_CASE_COUNT:", len(cases))
    print("VOLTAGE_ASSIGNMENT_COUNT:", assignment_total)
    print("TREE_NORMALIZATION_FAILURE_COUNT:", tree_failure_count)
    print("REPRESENTATION_CLASSIFICATION_FAILURE_COUNT:", classification_failure_count)
    print("COMPONENT_COUNT_FAILURE_COUNT:", component_failure_count)
    print("COMPONENT_SIZE_FAILURE_COUNT:", component_size_failure_count)
    print("CONNECTEDNESS_FAILURE_COUNT:", connectedness_failure_count)
    print("GAUGE_COVARIANCE_FAILURE_COUNT:", gauge_failure_count)
    print("ROOT_INVARIANCE_FAILURE_COUNT:", root_failure_count)
    print("CYCLE_SPECIALIZATION_FAILURE_COUNT:", cycle_specialization_failure_count)
    print("GENERATOR_RANK_FAILURE_COUNT:", generator_rank_failure_count)
    print("CHECK_SPANNING_TREE_NORMAL_FORM_EXACT:", str(tree_failure_count == 0).lower())
    print("CHECK_GAUGE_CLASSES_MATCH_REPRESENTATION_CONJUGACY_CLASSES:", str(classification_failure_count == 0).lower())
    print("CHECK_COMPONENT_COUNT_IS_SUBGROUP_INDEX:", str(component_failure_count == 0).lower())
    print("CHECK_COMPONENT_SIZE_IS_BASE_TIMES_HOLONOMY_SUBGROUP:", str(component_size_failure_count == 0).lower())
    print("CHECK_CONNECTED_IFF_HOLONOMY_IMAGE_IS_RECEIPT_GROUP:", str(connectedness_failure_count == 0).lower())
    print("CHECK_GAUGE_COVARIANCE_EXACT:", str(gauge_failure_count == 0).lower())
    print("CHECK_ROOT_CHANGE_PRESERVES_SUBGROUP_CONJUGACY_CLASS:", str(root_failure_count == 0).lower())
    print("CHECK_CYCLE_MULTIPLICATION_RECOVERED:", str(cycle_specialization_failure_count == 0).lower())
    print("FAILED_CHECKS:", [name for name, count in failed_checks.items() if count])

    theorem_pass = all(count == 0 for count in failed_checks.values())
    print()
    print("THEOREM_PASS:", str(theorem_pass).lower())
    print(
        "FINAL_CLASSIFICATION:",
        "finite_regular_graph_lifts_are_classified_by_holonomy_representations_and_decompose_by_the_index_of_the_holonomy_subgroup",
    )
    print(
        "THEOREM:",
        "Gauge classes of regular R-receipt lifts of connected X correspond to R-conjugacy classes of homomorphisms pi1(X)->R. If H is the image, the lift has [R:H] components, each with |V(X)|*|H| vertices, and is connected exactly when H=R.",
    )
    print(
        "BOUNDARY:",
        "The audit verifies declared finite examples. It does not derive a receipt group, fiber action, projection, or edge receipt from an unlabeled raw graph.",
    )
    print(
        "KEEPER:",
        "The graph supplies the possible circuits. The receipt representation records what every circuit carries home.",
    )
    print("MUTATION_PERFORMED: false")

    if not theorem_pass:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
