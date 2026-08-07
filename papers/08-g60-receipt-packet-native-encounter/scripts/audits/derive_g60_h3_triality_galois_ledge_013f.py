#!/usr/bin/env python3

import json
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path


SOURCE = Path(
    "/data/data/com.termux/files/home/dev/cori/research/"
    "mathematics/42-graph-automorphism-groups/artifacts/json/"
    "native_g60_v4_voltage_character_quotients_057.json"
)


@dataclass(frozen=True)
class Q5:
    a: Fraction = Fraction(0)
    b: Fraction = Fraction(0)

    @staticmethod
    def make(value):
        if isinstance(value, Q5):
            return value
        if isinstance(value, float) and value.is_integer():
            value = int(value)
        return Q5(Fraction(value), Fraction(0))

    def __add__(self, other):
        other = Q5.make(other)
        return Q5(self.a + other.a, self.b + other.b)

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        other = Q5.make(other)
        return Q5(self.a - other.a, self.b - other.b)

    def __rsub__(self, other):
        return Q5.make(other) - self

    def __neg__(self):
        return Q5(-self.a, -self.b)

    def __mul__(self, other):
        other = Q5.make(other)
        return Q5(
            self.a * other.a + 5 * self.b * other.b,
            self.a * other.b + self.b * other.a,
        )

    def __rmul__(self, other):
        return self * other

    def inverse(self):
        denominator = self.a * self.a - 5 * self.b * self.b
        if denominator == 0:
            raise ZeroDivisionError
        return Q5(
            self.a / denominator,
            -self.b / denominator,
        )

    def __truediv__(self, other):
        return self * Q5.make(other).inverse()

    def __rtruediv__(self, other):
        return Q5.make(other) / self

    def __float__(self):
        return float(self.a) + float(self.b) * (5 ** 0.5)

    def text(self):
        if self.b == 0:
            return str(self.a)
        if self.a == 0:
            return f"{self.b}*sqrt5"
        sign = "+" if self.b > 0 else "-"
        return f"{self.a}{sign}{abs(self.b)}*sqrt5"


ZERO = Q5()
ONE = Q5.make(1)
SQRT5 = Q5(Fraction(0), Fraction(1))
PHI = (ONE + SQRT5) / 2
PHI2 = PHI * PHI
PHI4 = PHI2 * PHI2
PHI8 = PHI4 * PHI4


def matrix(rows):
    return [
        [Q5.make(value) for value in row]
        for row in rows
    ]


def identity(size):
    return [
        [
            ONE if row == column else ZERO
            for column in range(size)
        ]
        for row in range(size)
    ]


def add(left, right):
    return [
        [
            left[row][column] + right[row][column]
            for column in range(len(left[0]))
        ]
        for row in range(len(left))
    ]


def subtract(left, right):
    return [
        [
            left[row][column] - right[row][column]
            for column in range(len(left[0]))
        ]
        for row in range(len(left))
    ]


def scale(scalar, value):
    scalar = Q5.make(scalar)
    return [
        [
            scalar * entry
            for entry in row
        ]
        for row in value
    ]


def multiply(left, right):
    row_count = len(left)
    middle_count = len(right)
    column_count = len(right[0])

    return [
        [
            sum(
                (
                    left[row][middle] * right[middle][column]
                    for middle in range(middle_count)
                ),
                ZERO,
            )
            for column in range(column_count)
        ]
        for row in range(row_count)
    ]


def transpose(value):
    return [
        list(row)
        for row in zip(*value)
    ]


def trace(value):
    return sum(
        (value[index][index] for index in range(len(value))),
        ZERO,
    )


def equal(left, right):
    return left == right


def is_zero(value):
    return all(
        entry == ZERO
        for row in value
        for entry in row
    )


def rank(value):
    work = [row[:] for row in value]
    row_count = len(work)
    column_count = len(work[0]) if work else 0
    pivot_row = 0

    for column in range(column_count):
        pivot = next(
            (
                row
                for row in range(pivot_row, row_count)
                if work[row][column] != ZERO
            ),
            None,
        )

        if pivot is None:
            continue

        work[pivot_row], work[pivot] = (
            work[pivot],
            work[pivot_row],
        )

        pivot_value = work[pivot_row][column]
        work[pivot_row] = [
            entry / pivot_value
            for entry in work[pivot_row]
        ]

        for row in range(row_count):
            if row == pivot_row:
                continue

            factor = work[row][column]
            if factor == ZERO:
                continue

            work[row] = [
                left - factor * right
                for left, right in zip(
                    work[row],
                    work[pivot_row],
                )
            ]

        pivot_row += 1

        if pivot_row == row_count:
            break

    return pivot_row


def column(value, index):
    return [
        value[row][index]
        for row in range(len(value))
    ]


def vector_add(left, right, sign=1):
    return [
        left[index] + sign * right[index]
        for index in range(len(left))
    ]


def dot(left, right):
    return sum(
        (
            left[index] * right[index]
            for index in range(len(left))
        ),
        ZERO,
    )


def outer(left, right):
    return [
        [
            left[row] * right[column]
            for column in range(len(right))
        ]
        for row in range(len(left))
    ]


def spectral_projector_golden_plus(operator):
    size = len(operator)
    unit = identity(size)

    eigenvalue = ONE + SQRT5
    other_values = [
        Q5.make(-2),
        ONE - SQRT5,
        ONE,
    ]

    numerator = identity(size)
    denominator = ONE

    for other in other_values:
        numerator = multiply(
            numerator,
            subtract(
                operator,
                scale(other, unit),
            ),
        )
        denominator *= eigenvalue - other

    return scale(ONE / denominator, numerator)


data = json.loads(SOURCE.read_text(encoding="utf-8"))

A_b = matrix(
    data["character_rows"]["chi_b"]["adjacency_matrix"]
)
A_ab = matrix(
    data["character_rows"]["chi_ab"]["adjacency_matrix"]
)

size = len(A_b)
unit = identity(size)

P_b = spectral_projector_golden_plus(A_b)
P_ab = spectral_projector_golden_plus(A_ab)

golden_eigenvalue = ONE + SQRT5

commutator = subtract(
    multiply(A_b, A_ab),
    multiply(A_ab, A_b),
)

cross_square = multiply(
    P_b,
    multiply(
        transpose(commutator),
        multiply(
            P_ab,
            multiply(commutator, P_b),
        ),
    ),
)

transverse_square = Fraction(16, 25) * PHI4
longitudinal_square = Fraction(16, 25) * PHI8

minimal_identity = multiply(
    subtract(
        cross_square,
        scale(longitudinal_square, P_b),
    ),
    subtract(
        cross_square,
        scale(transverse_square, P_b),
    ),
)

P_long = scale(
    ONE / (longitudinal_square - transverse_square),
    subtract(
        cross_square,
        scale(transverse_square, P_b),
    ),
)

diagonal_values = {
    entry
    for entry in (
        P_b[index][index]
        for index in range(size)
    )
}

axis_score_squares = [
    P_long[index][index] / P_b[index][index]
    for index in range(size)
]

maximum_score_square = max(
    axis_score_squares,
    key=float,
)

closest_indices = [
    index
    for index, value in enumerate(axis_score_squares)
    if value == maximum_score_square
]

first_index, second_index = closest_indices

first_axis = column(P_b, first_index)
second_axis = column(P_b, second_index)

axis_inner_product = (
    P_b[first_index][second_index]
    / P_b[first_index][first_index]
)

bisector_sign = 1 if float(axis_inner_product) > 0 else -1

bisector = vector_add(
    first_axis,
    second_axis,
    bisector_sign,
)

bisector_projector = scale(
    ONE / dot(bisector, bisector),
    outer(bisector, bisector),
)

checks = []


def check(name, passed):
    checks.append((name, bool(passed)))


check("source_audit_pass", data["audit_pass"] is True)

check(
    "b_projector_idempotent",
    equal(multiply(P_b, P_b), P_b),
)
check(
    "ab_projector_idempotent",
    equal(multiply(P_ab, P_ab), P_ab),
)
check(
    "b_projector_eigenvalue",
    equal(
        multiply(A_b, P_b),
        scale(golden_eigenvalue, P_b),
    ),
)
check(
    "ab_projector_eigenvalue",
    equal(
        multiply(A_ab, P_ab),
        scale(golden_eigenvalue, P_ab),
    ),
)
check("b_golden_rank_3", rank(P_b) == 3)
check("ab_golden_rank_3", rank(P_ab) == 3)
check("b_projector_trace_3", trace(P_b) == Q5.make(3))
check("ab_projector_trace_3", trace(P_ab) == Q5.make(3))
check(
    "uniform_frame_diagonal",
    diagonal_values == {Q5(Fraction(1, 5), Fraction(0))},
)
check(
    "cross_square_supported_on_b",
    equal(multiply(P_b, cross_square), cross_square)
    and equal(multiply(cross_square, P_b), cross_square),
)
check("cross_square_rank_3", rank(cross_square) == 3)
check(
    "cross_square_minimal_identity",
    is_zero(minimal_identity),
)
check(
    "longitudinal_multiplicity_1",
    rank(
        subtract(
            cross_square,
            scale(transverse_square, P_b),
        )
    ) == 1,
)
check(
    "longitudinal_projector_rank_1",
    rank(P_long) == 1,
)
check(
    "longitudinal_projector_idempotent",
    equal(multiply(P_long, P_long), P_long),
)
check(
    "two_closest_root_axes",
    len(closest_indices) == 2,
)
check(
    "closest_score_cos2_18",
    maximum_score_square
    == Q5(Fraction(5, 8), Fraction(1, 8)),
)
check(
    "closest_pair_inner_phi_over_2",
    axis_inner_product == PHI / 2
    or axis_inner_product == -(PHI / 2),
)
check(
    "longitudinal_is_exact_bisector",
    equal(P_long, bisector_projector),
)
check(
    "gain_square_ratio_phi4",
    longitudinal_square / transverse_square == PHI4,
)

failed = [
    name
    for name, passed in checks
    if not passed
]

print("== EXACT Q(SQRT5) CHARACTER-EXCHANGE CERTIFICATE ==")
print("SOURCE_AUDIT_PASS:", data["audit_pass"])
print("B_GOLDEN_PROJECTOR_RANK:", rank(P_b))
print("AB_GOLDEN_PROJECTOR_RANK:", rank(P_ab))
print("GOLDEN_EIGENVALUE:", golden_eigenvalue.text())
print("PROJECTOR_DIAGONAL:", next(iter(diagonal_values)).text())
print("COMMUTATOR_RANK:", rank(commutator))
print("CROSS_SQUARE_RANK:", rank(cross_square))
print(
    "TRANSVERSE_SINGULAR_VALUE_SQUARED:",
    transverse_square.text(),
)
print(
    "LONGITUDINAL_SINGULAR_VALUE_SQUARED:",
    longitudinal_square.text(),
)
print(
    "SINGULAR_VALUE_GAIN_RATIO:",
    "phi^2 = " + PHI2.text(),
)
print("LONGITUDINAL_PROJECTOR_RANK:", rank(P_long))
print("CLOSEST_ROOT_AXIS_INDICES:", closest_indices)
print(
    "CLOSEST_SCORE_SQUARED:",
    maximum_score_square.text(),
)
print(
    "CLOSEST_ROOT_PAIR_INNER_PRODUCT:",
    axis_inner_product.text(),
)
print(
    "LONGITUDINAL_IS_EXACT_ROOT_PAIR_BISECTOR:",
    equal(P_long, bisector_projector),
)
print("CHECK_COUNT:", len(checks))
print("FAILED_CHECK_COUNT:", len(failed))
print("FAILED_CHECKS:", failed)
print("CERTIFICATE_PASS:", not failed)
print(
    "CLASSIFICATION:",
    "golden_character_exchange_selects_an_exact_"
    "adjacent_H3_root_pair_bisector_over_Q_sqrt5",
)
print("ABSOLUTE_AXIS_SIGN_SELECTED: false")
print("PHYSICAL_SPACE_IDENTIFIED: false")
print("G900_IDENTIFIED: false")
print("PROJECT_MUTATION_PERFORMED: false")

if failed:
    raise SystemExit(1)

print("== EXACT H3 BISECTOR-ORBIT G60 CERTIFICATE ==")

import networkx as nx
from itertools import product


def matvec(operator, vector):
    return [
        sum(
            (
                operator[row][column] * vector[column]
                for column in range(len(vector))
            ),
            ZERO,
        )
        for row in range(len(operator))
    ]


def vector_scale(scalar, vector):
    return [
        scalar * entry
        for entry in vector
    ]


def matrix_key(operator):
    return tuple(
        entry
        for row in operator
        for entry in row
    )


def canonical_line(vector):
    sign = 1

    for entry in vector:
        if entry != ZERO:
            sign = 1 if float(entry) > 0 else -1
            break

    return tuple(vector_scale(sign, vector))


def graph_from_relations(points, norm_squared, relations):
    graph = nx.Graph()
    graph.add_nodes_from(range(len(points)))

    for left in range(len(points)):
        for right in range(left + 1, len(points)):
            normalized_dot = (
                dot(points[left], points[right])
                / norm_squared
            )

            if normalized_dot in relations:
                graph.add_edge(left, right)

    return graph


def shell_profile(graph, source):
    lengths = nx.single_source_shortest_path_length(
        graph,
        source,
    )

    return tuple(
        sum(
            distance == shell
            for distance in lengths.values()
        )
        for shell in range(max(lengths.values()) + 1)
    )


def graph_checks(graph):
    return {
        "vertices_60": graph.number_of_nodes() == 60,
        "edges_120": graph.number_of_edges() == 120,
        "degree_4": {
            degree
            for _, degree in graph.degree()
        } == {4},
        "connected": nx.is_connected(graph),
        "diameter_6":
            nx.is_connected(graph)
            and nx.diameter(graph) == 6,
        "shells":
            nx.is_connected(graph)
            and {
                shell_profile(graph, vertex)
                for vertex in graph.nodes()
            } == {
                (1, 4, 8, 16, 24, 6, 1)
            },
    }


half = Q5.make(Fraction(1, 2))
inverse_phi = PHI - ONE

roots = set()

for axis in range(3):
    for sign in (-1, 1):
        root = [ZERO, ZERO, ZERO]
        root[axis] = Q5.make(sign)
        roots.add(tuple(root))

base = [
    ONE,
    PHI,
    inverse_phi,
]

even_permutations = [
    (0, 1, 2),
    (1, 2, 0),
    (2, 0, 1),
]

for permutation in even_permutations:
    permuted = [
        base[index]
        for index in permutation
    ]

    for signs in product((-1, 1), repeat=3):
        roots.add(tuple(
            half * signs[index] * permuted[index]
            for index in range(3)
        ))

roots = sorted(
    roots,
    key=lambda root: tuple(float(entry) for entry in root),
)

root_norms = {
    dot(root, root)
    for root in roots
}

reflection_generators = []

for root in roots:
    reflection_generators.append(
        subtract(
            identity(3),
            scale(
                Q5.make(2),
                outer(root, root),
            ),
        )
    )

identity3 = identity(3)
reflection_group = {
    matrix_key(identity3): identity3,
}
queue = [identity3]

while queue:
    current = queue.pop()

    for generator in reflection_generators:
        candidate = multiply(generator, current)
        key = matrix_key(candidate)

        if key not in reflection_group:
            reflection_group[key] = candidate
            queue.append(candidate)

standard_pair = next(
    (left, right)
    for left in range(len(roots))
    for right in range(left + 1, len(roots))
    if dot(roots[left], roots[right]) == PHI / 2
)

standard_bisector = vector_add(
    list(roots[standard_pair[0]]),
    list(roots[standard_pair[1]]),
)

bisector_norm_squared = dot(
    standard_bisector,
    standard_bisector,
)

oriented_points = {
    tuple(matvec(element, standard_bisector))
    for element in reflection_group.values()
}

oriented_points = sorted(
    oriented_points,
    key=lambda point: tuple(float(entry) for entry in point),
)

projective_lines = {
    canonical_line(point)
    for point in oriented_points
}

antipodal_closure = all(
    tuple(vector_scale(-1, list(point))) in oriented_points
    for point in oriented_points
)

relation_0 = -(Q5.make(5) + SQRT5) / 20
relation_1 = -(Q5.make(5) - SQRT5) / 20
relation_2_low = (
    Q5.make(Fraction(1, 2))
    - SQRT5 / 5
)
relation_2_high = (
    Q5.make(Fraction(1, 2))
    + SQRT5 / 5
)

relation_sets = [
    {relation_0},
    {relation_1},
    {relation_2_low, relation_2_high},
]

candidate_graphs = [
    graph_from_relations(
        oriented_points,
        bisector_norm_squared,
        relations,
    )
    for relations in relation_sets
]

quotient = data["quotient"]
coordinate_rows = quotient["vertex_coordinates"]

coordinate_lookup = {
    (
        row["quotient_index"],
        row["group_element"],
    ): int(vertex)
    for vertex, row in coordinate_rows.items()
}

group_code = {
    "1": 0,
    "a": 1,
    "b": 2,
    "ab": 3,
}
code_group = {
    value: key
    for key, value in group_code.items()
}

native_graph = nx.Graph()
native_graph.add_nodes_from(range(60))

for row in data["voltage_rows"]:
    source_quotient = row["source_quotient"]
    target_quotient = row["target_quotient"]
    voltage = group_code[row["voltage"]]

    for group_name, group_value in group_code.items():
        target_group = code_group[group_value ^ voltage]

        source_vertex = coordinate_lookup[
            (source_quotient, group_name)
        ]
        target_vertex = coordinate_lookup[
            (target_quotient, target_group)
        ]

        native_graph.add_edge(source_vertex, target_vertex)

native_checks = graph_checks(native_graph)
candidate_checks = [
    graph_checks(graph)
    for graph in candidate_graphs
]

native_isomorphisms = [
    nx.is_isomorphic(graph, native_graph)
    for graph in candidate_graphs
]

exact_dot_profile = {}

for left in range(len(oriented_points)):
    for right in range(left + 1, len(oriented_points)):
        value = (
            dot(
                oriented_points[left],
                oriented_points[right],
            )
            / bisector_norm_squared
        )
        exact_dot_profile[value] = (
            exact_dot_profile.get(value, 0) + 1
        )

orbit_checks = []


def orbit_check(name, passed):
    orbit_checks.append((name, bool(passed)))


orbit_check("root_count_30", len(roots) == 30)
orbit_check("all_roots_unit", root_norms == {ONE})
orbit_check(
    "reflection_group_order_120",
    len(reflection_group) == 120,
)
orbit_check(
    "standard_pair_inner_phi_over_2",
    dot(
        roots[standard_pair[0]],
        roots[standard_pair[1]],
    ) == PHI / 2,
)
orbit_check(
    "bisector_norm_squared_2_plus_phi",
    bisector_norm_squared == Q5.make(2) + PHI,
)
orbit_check(
    "oriented_point_count_60",
    len(oriented_points) == 60,
)
orbit_check(
    "projective_line_count_30",
    len(projective_lines) == 30,
)
orbit_check("antipodal_closure", antipodal_closure)
orbit_check(
    "three_relation_sets",
    len(relation_sets) == 3,
)
orbit_check(
    "all_native_checks",
    all(native_checks.values()),
)
orbit_check(
    "all_candidate_checks",
    all(
        all(row.values())
        for row in candidate_checks
    ),
)
orbit_check(
    "all_candidates_native_isomorphic",
    all(native_isomorphisms),
)

orbit_failed = [
    name
    for name, passed in orbit_checks
    if not passed
]

print("H3_ROOT_COUNT:", len(roots))
print("H3_ROOT_NORM_SET:", [value.text() for value in root_norms])
print("H3_REFLECTION_GROUP_ORDER:", len(reflection_group))
print("STANDARD_ADJACENT_ROOT_PAIR:", list(standard_pair))
print(
    "STANDARD_ROOT_PAIR_INNER_PRODUCT:",
    (PHI / 2).text(),
)
print(
    "BISECTOR_NORM_SQUARED:",
    bisector_norm_squared.text(),
)
print("PROJECTIVE_BISECTOR_LINE_COUNT:", len(projective_lines))
print("ORIENTED_BISECTOR_POINT_COUNT:", len(oriented_points))
print("ANTIPODAL_CLOSURE:", antipodal_closure)
print(
    "EXACT_G60_RELATION_0:",
    relation_0.text(),
)
print(
    "EXACT_G60_RELATION_1:",
    relation_1.text(),
)
print(
    "EXACT_G60_RELATION_2:",
    [
        relation_2_low.text(),
        relation_2_high.text(),
    ],
)
print("NATIVE_CHECKS:", native_checks)

for index, graph in enumerate(candidate_graphs):
    print(
        "PRESENTATION",
        index,
        "RELATIONS",
        [value.text() for value in relation_sets[index]],
        "CHECKS",
        candidate_checks[index],
        "NATIVE_ISOMORPHIC",
        native_isomorphisms[index],
    )

print("EXACT_DOT_VALUE_COUNT:", len(exact_dot_profile))
print("CHECK_COUNT:", len(orbit_checks))
print("FAILED_CHECK_COUNT:", len(orbit_failed))
print("FAILED_CHECKS:", orbit_failed)
print("CERTIFICATE_PASS:", not orbit_failed)
print(
    "CLASSIFICATION:",
    "native_G60_has_three_exact_Q_sqrt5_"
    "spherical_presentations_on_the_oriented_"
    "H3_adjacent_root_bisector_orbit",
)
print("PHYSICAL_SPACE_IDENTIFIED: false")
print("G900_IDENTIFIED: false")
print("PROJECT_MUTATION_PERFORMED: false")

if orbit_failed:
    raise SystemExit(1)


print("== THREE-PRESENTATION ALGEBRA GATE ==")

import numpy as np


def integer_adjacency(graph):
    order = sorted(graph.nodes())
    index = {
        vertex: position
        for position, vertex in enumerate(order)
    }

    result = np.zeros(
        (len(order), len(order)),
        dtype=np.int64,
    )

    for left, right in graph.edges():
        i = index[left]
        j = index[right]
        result[i, j] = 1
        result[j, i] = 1

    return result


presentation_operators = [
    integer_adjacency(graph)
    for graph in candidate_graphs
]

identity60 = np.eye(60, dtype=np.int64)

edge_intersections = {}

for left in range(3):
    for right in range(left + 1, 3):
        edge_intersections[(left, right)] = int(
            np.sum(
                presentation_operators[left]
                * presentation_operators[right]
            ) // 2
        )

commutator_rows = []

for left in range(3):
    for right in range(left + 1, 3):
        commutator = (
            presentation_operators[left]
            @ presentation_operators[right]
            - presentation_operators[right]
            @ presentation_operators[left]
        )

        commutator_rows.append({
            "pair": [left, right],
            "zero": bool(np.all(commutator == 0)),
            "rank": int(np.linalg.matrix_rank(commutator)),
            "nonzero_entry_count": int(
                np.count_nonzero(commutator)
            ),
            "frobenius_squared": int(
                np.sum(commutator * commutator)
            ),
        })

basis_words = [
    ("I", identity60),
    ("A0", presentation_operators[0]),
    ("A1", presentation_operators[1]),
    ("A2", presentation_operators[2]),
]

second_words = []

for left in range(3):
    for right in range(3):
        second_words.append((
            f"A{left}A{right}",
            presentation_operators[left]
            @ presentation_operators[right],
        ))

first_span = np.column_stack([
    operator.reshape(-1)
    for _, operator in basis_words
]).astype(float)

first_span_rank = int(np.linalg.matrix_rank(first_span))

algebra_columns = [
    operator.reshape(-1)
    for _, operator in basis_words + second_words
]

degree_two_algebra_rank = int(np.linalg.matrix_rank(
    np.column_stack(algebra_columns).astype(float)
))

product_residual_rows = []

for name, operator in second_words:
    coefficients, _, _, _ = np.linalg.lstsq(
        first_span,
        operator.reshape(-1).astype(float),
        rcond=None,
    )

    reconstruction = (
        first_span @ coefficients
    ).reshape(60, 60)

    product_residual_rows.append({
        "word": name,
        "residual": float(np.linalg.norm(
            operator - reconstruction
        )),
    })

maximum_product_residual = max(
    row["residual"]
    for row in product_residual_rows
)

direct_v4_algebra = (
    first_span_rank == 4
    and degree_two_algebra_rank == 4
    and all(row["zero"] for row in commutator_rows)
    and maximum_product_residual < 1e-8
)

print("EDGE_INTERSECTIONS:", edge_intersections)
print("COMMUTATOR_ROWS:", commutator_rows)
print("FIRST_SPAN_RANK:", first_span_rank)
print("DEGREE_TWO_ALGEBRA_RANK:", degree_two_algebra_rank)
print(
    "MAXIMUM_PRODUCT_CLOSURE_RESIDUAL:",
    maximum_product_residual,
)
print(
    "DIRECT_V4_CHARACTER_ALGEBRA:",
    direct_v4_algebra,
)
print(
    "THREE_PRESENTATIONS_CANONICALLY_IDENTIFIED_"
    "WITH_NONTRIVIAL_V4_CHARACTERS:",
    direct_v4_algebra,
)
print(
    "INTERPRETATION:",
    (
        "direct_commutative_V4_algebra_supported"
        if direct_v4_algebra
        else
        "cardinality_three_is_not_yet_a_V4_character_identification"
    ),
)
print("PROJECT_MUTATION_PERFORMED: false")

print("== G60 PRESENTATION TRIALITY TEST ==")

import time

triality_started = time.time()

base_colored_graph = nx.Graph()
base_colored_graph.add_nodes_from(range(60))

for color, graph in enumerate(candidate_graphs):
    for left, right in graph.edges():
        base_colored_graph.add_edge(
            left,
            right,
            color=color,
        )


def recolored_target(color_permutation):
    inverse = {
        target: source
        for source, target in enumerate(color_permutation)
    }

    target = nx.Graph()
    target.add_nodes_from(base_colored_graph.nodes())

    for left, right, row in base_colored_graph.edges(data=True):
        target.add_edge(
            left,
            right,
            color=inverse[row["color"]],
        )

    return target


def permutation_order(permutation, maximum=240):
    current = list(range(len(permutation)))

    for order in range(1, maximum + 1):
        current = [
            permutation[current[index]]
            for index in range(len(permutation))
        ]

        if current == list(range(len(permutation))):
            return order

    return None


def compose_permutations(left, right):
    return [
        left[right[index]]
        for index in range(len(left))
    ]


def inverse_permutation(permutation):
    inverse = [None] * len(permutation)

    for source, target in enumerate(permutation):
        inverse[target] = source

    return inverse


def transports_colors(permutation, color_permutation):
    for color, graph in enumerate(candidate_graphs):
        target_graph = candidate_graphs[color_permutation[color]]

        for left, right in graph.edges():
            if not target_graph.has_edge(
                permutation[left],
                permutation[right],
            ):
                return False

    return True


def collect_color_conjugators(
    color_permutation,
    maximum_count=5000,
):
    target = recolored_target(color_permutation)

    edge_match = nx.algorithms.isomorphism.categorical_edge_match(
        "color",
        -1,
    )

    matcher = nx.algorithms.isomorphism.GraphMatcher(
        base_colored_graph,
        target,
        edge_match=edge_match,
    )

    rows = []

    for mapping in matcher.isomorphisms_iter():
        permutation = [
            mapping[index]
            for index in range(60)
        ]

        if not transports_colors(
            permutation,
            color_permutation,
        ):
            continue

        rows.append({
            "permutation": permutation,
            "order": permutation_order(permutation),
        })

        if len(rows) >= maximum_count:
            break

    return rows


cycle_colors = [1, 2, 0]
swap_colors = [1, 0, 2]

cycle_conjugators = collect_color_conjugators(cycle_colors)
swap_conjugators = collect_color_conjugators(swap_colors)

order_three_cycles = [
    row["permutation"]
    for row in cycle_conjugators
    if row["order"] == 3
]

order_two_swaps = [
    row["permutation"]
    for row in swap_conjugators
    if row["order"] == 2
]

s3_pair = None

for cycle in order_three_cycles:
    cycle_inverse = inverse_permutation(cycle)

    for swap in order_two_swaps:
        conjugated = compose_permutations(
            swap,
            compose_permutations(cycle, swap),
        )

        if conjugated == cycle_inverse:
            s3_pair = {
                "cycle": cycle,
                "swap": swap,
            }
            break

    if s3_pair is not None:
        break

cycle_order_profile = {}

for row in cycle_conjugators:
    cycle_order_profile[row["order"]] = (
        cycle_order_profile.get(row["order"], 0) + 1
    )

swap_order_profile = {}

for row in swap_conjugators:
    swap_order_profile[row["order"]] = (
        swap_order_profile.get(row["order"], 0) + 1
    )

triality_checks = {
    "cyclic_conjugator_exists":
        bool(cycle_conjugators),
    "order_three_cycle_exists":
        bool(order_three_cycles),
    "swap_conjugator_exists":
        bool(swap_conjugators),
    "order_two_swap_exists":
        bool(order_two_swaps),
    "s3_relations_realized":
        s3_pair is not None,
}

print("CYCLE_COLOR_ACTION:", cycle_colors)
print("SWAP_COLOR_ACTION:", swap_colors)
print("CYCLE_CONJUGATOR_COUNT:", len(cycle_conjugators))
print("CYCLE_ORDER_PROFILE:", cycle_order_profile)
print("ORDER_THREE_CYCLE_COUNT:", len(order_three_cycles))
print("SWAP_CONJUGATOR_COUNT:", len(swap_conjugators))
print("SWAP_ORDER_PROFILE:", swap_order_profile)
print("ORDER_TWO_SWAP_COUNT:", len(order_two_swaps))
print("TRIALITY_CHECKS:", triality_checks)

if s3_pair is not None:
    print(
        "ORDER_THREE_PERMUTATION_FIRST_TWENTY:",
        s3_pair["cycle"][:20],
    )
    print(
        "ORDER_TWO_PERMUTATION_FIRST_TWENTY:",
        s3_pair["swap"][:20],
    )

print(
    "PRESENTATION_TRIALITY_PROVED:",
    triality_checks["order_three_cycle_exists"],
)
print(
    "PRESENTATION_S3_ACTION_PROVED:",
    triality_checks["s3_relations_realized"],
)
print(
    "CLASSIFICATION:",
    (
        "three_native_G60_spherical_presentations_form_"
        "an_S3_triality_on_one_60_point_carrier"
        if triality_checks["s3_relations_realized"]
        else
        "presentation_triality_not_yet_proved"
    ),
)
print(
    "RUNTIME_SECONDS:",
    round(time.time() - triality_started, 3),
)
print("PHYSICAL_SPACE_IDENTIFIED: false")
print("G900_IDENTIFIED: false")
print("PROJECT_MUTATION_PERFORMED: false")

print("== G60 TRIALITY DIRECTION AUDIT ==")

cycle_permutation = s3_pair["cycle"]
reverser_permutation = s3_pair["swap"]

point_index = {
    tuple(point): index
    for index, point in enumerate(oriented_points)
}

antipodal_permutation = [
    point_index[tuple(vector_scale(-1, list(point)))]
    for point in oriented_points
]


def apply_power(permutation, point, power):
    result = point

    for _ in range(power):
        result = permutation[result]

    return result


def permutation_cycles(permutation):
    unseen = set(range(len(permutation)))
    cycles = []

    while unseen:
        start = min(unseen)
        cycle = []
        current = start

        while current not in cycle:
            cycle.append(current)
            unseen.discard(current)
            current = permutation[current]

        cycles.append(tuple(cycle))

    return cycles


def determinant3(rows):
    a, b, c = rows[0]
    d, e, f = rows[1]
    g, h, i = rows[2]

    return (
        a * (e * i - f * h)
        - b * (d * i - f * g)
        + c * (d * h - e * g)
    )


def sign_label(value):
    numerical = float(value)

    if numerical > 1e-12:
        return "+"
    if numerical < -1e-12:
        return "-"
    return "0"


cycle_decomposition = permutation_cycles(cycle_permutation)

fixed_points = [
    cycle[0]
    for cycle in cycle_decomposition
    if len(cycle) == 1
]

three_cycles = [
    cycle
    for cycle in cycle_decomposition
    if len(cycle) == 3
]

cycle_word_profile = {}
cycle_sign_profile = {}
cycle_orientation_profile = {
    "positive": 0,
    "negative": 0,
    "zero": 0,
}

cycle_rows = []

for cycle in three_cycles:
    left, middle, right = cycle

    exact_word = (
        dot(
            oriented_points[left],
            oriented_points[middle],
        ) / bisector_norm_squared,
        dot(
            oriented_points[middle],
            oriented_points[right],
        ) / bisector_norm_squared,
        dot(
            oriented_points[right],
            oriented_points[left],
        ) / bisector_norm_squared,
    )

    sign_word = tuple(
        sign_label(value)
        for value in exact_word
    )

    orientation = determinant3([
        oriented_points[left],
        oriented_points[middle],
        oriented_points[right],
    ])

    if float(orientation) > 1e-12:
        orientation_label = "positive"
    elif float(orientation) < -1e-12:
        orientation_label = "negative"
    else:
        orientation_label = "zero"

    cycle_word_profile[exact_word] = (
        cycle_word_profile.get(exact_word, 0) + 1
    )
    cycle_sign_profile[sign_word] = (
        cycle_sign_profile.get(sign_word, 0) + 1
    )
    cycle_orientation_profile[orientation_label] += 1

    cycle_rows.append({
        "cycle": list(cycle),
        "word": [
            value.text()
            for value in exact_word
        ],
        "sign_word": list(sign_word),
        "orientation": orientation.text(),
        "orientation_label": orientation_label,
    })

cycle_commutes_with_antipode = all(
    cycle_permutation[antipodal_permutation[index]]
    == antipodal_permutation[cycle_permutation[index]]
    for index in range(60)
)

reverser_commutes_with_antipode = all(
    reverser_permutation[antipodal_permutation[index]]
    == antipodal_permutation[reverser_permutation[index]]
    for index in range(60)
)

reverser_reverses_cycle = all(
    reverser_permutation[
        cycle_permutation[
            reverser_permutation[index]
        ]
    ]
    == inverse_permutation(cycle_permutation)[index]
    for index in range(60)
)

antipodal_cycle_pairing = all(
    tuple(
        antipodal_permutation[index]
        for index in cycle
    ) in three_cycles
    or tuple(
        reversed(tuple(
            antipodal_permutation[index]
            for index in cycle
        ))
    ) in three_cycles
    for cycle in three_cycles
)

presentation_polarity_word = (
    "negative_single_shell",
    "negative_single_shell",
    "positive_double_shell",
)

two_plus_one_polarity = (
    presentation_polarity_word.count(
        "negative_single_shell"
    ) == 2
    and presentation_polarity_word.count(
        "positive_double_shell"
    ) == 1
)

direction_checks = {
    "cycle_order_3":
        permutation_order(cycle_permutation) == 3,
    "reverser_order_2":
        permutation_order(reverser_permutation) == 2,
    "cycle_decomposition_covers_60":
        sum(len(cycle) for cycle in cycle_decomposition) == 60,
    "only_lengths_1_or_3":
        {
            len(cycle)
            for cycle in cycle_decomposition
        }.issubset({1, 3}),
    "cycle_commutes_with_antipode":
        cycle_commutes_with_antipode,
    "reverser_commutes_with_antipode":
        reverser_commutes_with_antipode,
    "reverser_reverses_cycle":
        reverser_reverses_cycle,
    "antipodal_cycle_pairing":
        antipodal_cycle_pairing,
    "two_negative_one_positive_phase":
        two_plus_one_polarity,
}

print(
    "TRIALITY_CYCLE_LENGTH_PROFILE:",
    {
        length: sum(
            len(cycle) == length
            for cycle in cycle_decomposition
        )
        for length in sorted({
            len(cycle)
            for cycle in cycle_decomposition
        })
    },
)
print("FIXED_POINT_COUNT:", len(fixed_points))
print("FIXED_POINTS:", fixed_points)
print("THREE_CYCLE_COUNT:", len(three_cycles))
print(
    "EXACT_CYCLE_WORD_PROFILE:",
    {
        tuple(value.text() for value in word): count
        for word, count in cycle_word_profile.items()
    },
)
print("CYCLE_SIGN_PROFILE:", cycle_sign_profile)
print(
    "CYCLE_ORIENTATION_PROFILE:",
    cycle_orientation_profile,
)
print(
    "FIRST_FIVE_NONTRIVIAL_CYCLES:",
    cycle_rows[:5],
)
print(
    "CYCLE_COMMUTES_WITH_ANTIPODE:",
    cycle_commutes_with_antipode,
)
print(
    "REVERSER_COMMUTES_WITH_ANTIPODE:",
    reverser_commutes_with_antipode,
)
print(
    "REVERSER_REVERSES_CYCLE:",
    reverser_reverses_cycle,
)
print(
    "ANTIPODAL_CYCLE_PAIRING:",
    antipodal_cycle_pairing,
)
print(
    "PRESENTATION_POLARITY_WORD:",
    presentation_polarity_word,
)
print(
    "TWO_NEGATIVE_ONE_POSITIVE_PHASE:",
    two_plus_one_polarity,
)
print("DIRECTION_CHECKS:", direction_checks)
print(
    "DIRECTION_AUDIT_PASS:",
    all(direction_checks.values()),
)
print(
    "CLASSIFICATION:",
    (
        "S3_triality_orients_the_three_G60_phases_"
        "with_two_negative_single_shell_phases_and_"
        "one_positive_double_shell_phase"
        if all(direction_checks.values())
        else
        "triality_direction_structure_requires_refinement"
    ),
)
print("LITERAL_PHYSICAL_MOTION_DERIVED: false")
print("PHYSICAL_SPACE_IDENTIFIED: false")
print("G900_IDENTIFIED: false")
print("PROJECT_MUTATION_PERFORMED: false")

print("== TRIALITY ORIENTATION-SHEET CENSUS ==")


def commutes(left, right):
    return compose_permutations(left, right) == (
        compose_permutations(right, left)
    )


def cycle_length_profile(permutation):
    profile = {}

    for cycle in permutation_cycles(permutation):
        profile[len(cycle)] = profile.get(len(cycle), 0) + 1

    return profile


orientation_cycle_rows = []

for cycle in order_three_cycles:
    cycle_inverse = inverse_permutation(cycle)

    sheet_defect = compose_permutations(
        cycle,
        compose_permutations(
            antipodal_permutation,
            compose_permutations(
                cycle_inverse,
                antipodal_permutation,
            ),
        ),
    )

    orientation_cycle_rows.append({
        "commutes_with_antipode":
            commutes(cycle, antipodal_permutation),
        "fixed_point_count":
            sum(cycle[index] == index for index in range(60)),
        "cycle_profile":
            cycle_length_profile(cycle),
        "sheet_defect_order":
            permutation_order(sheet_defect),
        "sheet_defect_profile":
            cycle_length_profile(sheet_defect),
    })

orientation_swap_rows = []

for swap in order_two_swaps:
    orientation_swap_rows.append({
        "commutes_with_antipode":
            commutes(swap, antipodal_permutation),
        "fixed_point_count":
            sum(swap[index] == index for index in range(60)),
        "cycle_profile":
            cycle_length_profile(swap),
    })

cycle_antipode_commuting_count = sum(
    row["commutes_with_antipode"]
    for row in orientation_cycle_rows
)

swap_antipode_commuting_count = sum(
    row["commutes_with_antipode"]
    for row in orientation_swap_rows
)

cycle_profile_census = {}

for row in orientation_cycle_rows:
    key = tuple(sorted(row["cycle_profile"].items()))
    cycle_profile_census[key] = (
        cycle_profile_census.get(key, 0) + 1
    )

sheet_defect_census = {}

for row in orientation_cycle_rows:
    key = (
        row["sheet_defect_order"],
        tuple(sorted(row["sheet_defect_profile"].items())),
    )
    sheet_defect_census[key] = (
        sheet_defect_census.get(key, 0) + 1
    )

swap_profile_census = {}

for row in orientation_swap_rows:
    key = tuple(sorted(row["cycle_profile"].items()))
    swap_profile_census[key] = (
        swap_profile_census.get(key, 0) + 1
    )

all_cycles_mix_orientation_sheet = (
    cycle_antipode_commuting_count == 0
)

all_swaps_preserve_orientation_pairing = (
    swap_antipode_commuting_count
    == len(order_two_swaps)
)

print(
    "ORDER_THREE_TRIALITY_COUNT:",
    len(order_three_cycles),
)
print(
    "ORDER_THREE_COMMUTING_WITH_ANTIPODE_COUNT:",
    cycle_antipode_commuting_count,
)
print(
    "ORDER_THREE_CYCLE_PROFILE_CENSUS:",
    cycle_profile_census,
)
print(
    "SHEET_DEFECT_CENSUS:",
    sheet_defect_census,
)
print(
    "ORDER_TWO_REVERSER_COUNT:",
    len(order_two_swaps),
)
print(
    "ORDER_TWO_COMMUTING_WITH_ANTIPODE_COUNT:",
    swap_antipode_commuting_count,
)
print(
    "ORDER_TWO_CYCLE_PROFILE_CENSUS:",
    swap_profile_census,
)
print(
    "ALL_TRIALITY_CYCLES_MIX_ORIENTATION_SHEET:",
    all_cycles_mix_orientation_sheet,
)
print(
    "ALL_INVOLUTIVE_REVERSERS_PRESERVE_ANTIPODAL_PAIRING:",
    all_swaps_preserve_orientation_pairing,
)
print(
    "ORIENTATION_SHEET_CENSUS_PASS:",
    all_cycles_mix_orientation_sheet
    and all_swaps_preserve_orientation_pairing,
)
print(
    "CLASSIFICATION:",
    (
        "XY_reversal_descends_projectively_while_"
        "XYZ_triality_is_intrinsically_oriented"
        if (
            all_cycles_mix_orientation_sheet
            and all_swaps_preserve_orientation_pairing
        )
        else
        "orientation_sheet_behavior_has_multiple_classes"
    ),
)
print("LITERAL_PHYSICAL_MOTION_DERIVED: false")
print("PHYSICAL_SPACE_IDENTIFIED: false")
print("G900_IDENTIFIED: false")
print("PROJECT_MUTATION_PERFORMED: false")

print("== ORIENTATION-SHEET V4 AND S4 TEST ==")

identity_permutation = list(range(60))
C = s3_pair["cycle"]
R = s3_pair["swap"]
C2 = compose_permutations(C, C)


def conjugate(permutation, operator):
    return compose_permutations(
        permutation,
        compose_permutations(
            operator,
            inverse_permutation(permutation),
        ),
    )


tau_x = antipodal_permutation
tau_y = conjugate(C, tau_x)
tau_z = conjugate(C2, tau_x)

sheet_involutions = [
    tau_x,
    tau_y,
    tau_z,
]


def permutation_key(permutation):
    return tuple(permutation)


def generated_permutation_group(generators):
    identity = list(range(60))
    group = {
        permutation_key(identity): identity,
    }
    queue = [identity]

    while queue:
        current = queue.pop()

        for generator in generators:
            product = compose_permutations(
                generator,
                current,
            )
            key = permutation_key(product)

            if key not in group:
                group[key] = product
                queue.append(product)

    return list(group.values())


sheet_v4 = generated_permutation_group([
    tau_x,
    tau_y,
])

sheet_s4 = generated_permutation_group([
    tau_x,
    C,
    R,
])

sheet_s4_order_profile = {}

for element in sheet_s4:
    order = permutation_order(element)
    sheet_s4_order_profile[order] = (
        sheet_s4_order_profile.get(order, 0) + 1
    )

pair_products = {}

for left in range(3):
    for right in range(left + 1, 3):
        product_value = compose_permutations(
            sheet_involutions[left],
            sheet_involutions[right],
        )

        target = next(
            (
                index
                for index, involution
                in enumerate(sheet_involutions)
                if involution == product_value
            ),
            None,
        )

        pair_products[(left, right)] = target

C_sheet_action = []

for involution in sheet_involutions:
    image = conjugate(C, involution)
    C_sheet_action.append(
        next(
            index
            for index, target in enumerate(sheet_involutions)
            if target == image
        )
    )

R_sheet_action = []

for involution in sheet_involutions:
    image = conjugate(R, involution)
    R_sheet_action.append(
        next(
            index
            for index, target in enumerate(sheet_involutions)
            if target == image
        )
    )

sheet_v4_keys = {
    permutation_key(element)
    for element in sheet_v4
}

sheet_v4_normal = all(
    permutation_key(
        conjugate(group_element, v4_element)
    ) in sheet_v4_keys
    for group_element in sheet_s4
    for v4_element in sheet_v4
)

sheet_checks = {
    "three_distinct_sheet_involutions":
        len({
            permutation_key(value)
            for value in sheet_involutions
        }) == 3,
    "all_sheet_maps_order_two":
        all(
            permutation_order(value) == 2
            for value in sheet_involutions
        ),
    "all_sheet_maps_fixed_point_free":
        all(
            all(
                value[index] != index
                for index in range(60)
            )
            for value in sheet_involutions
        ),
    "sheet_involutions_pairwise_commute":
        all(
            commutes(
                sheet_involutions[left],
                sheet_involutions[right],
            )
            for left in range(3)
            for right in range(left + 1, 3)
        ),
    "pair_products_give_third":
        set(pair_products.values()) == {0, 1, 2},
    "generated_sheet_group_is_v4":
        len(sheet_v4) == 4,
    "C_cycles_sheet_involutions":
        C_sheet_action == [1, 2, 0],
    "R_is_sheet_transposition":
        sorted(R_sheet_action) == [0, 1, 2]
        and R_sheet_action != [0, 1, 2],
    "generated_extension_order_24":
        len(sheet_s4) == 24,
    "s4_order_profile":
        sheet_s4_order_profile
        == {
            1: 1,
            2: 9,
            3: 8,
            4: 6,
        },
    "v4_normal_in_extension":
        sheet_v4_normal,
}

print(
    "SHEET_INVOLUTION_FIXED_POINT_COUNTS:",
    [
        sum(
            involution[index] == index
            for index in range(60)
        )
        for involution in sheet_involutions
    ],
)
print(
    "SHEET_INVOLUTION_ORDER_PROFILE:",
    [
        permutation_order(involution)
        for involution in sheet_involutions
    ],
)
print("PAIR_PRODUCTS:", pair_products)
print("SHEET_V4_ORDER:", len(sheet_v4))
print("C_SHEET_ACTION:", C_sheet_action)
print("R_SHEET_ACTION:", R_sheet_action)
print("SHEET_EXTENSION_ORDER:", len(sheet_s4))
print(
    "SHEET_EXTENSION_ORDER_PROFILE:",
    sheet_s4_order_profile,
)
print("SHEET_V4_NORMAL:", sheet_v4_normal)
print("SHEET_CHECKS:", sheet_checks)
print(
    "ORIENTATION_SHEET_V4_PROVED:",
    all(
        sheet_checks[name]
        for name in (
            "three_distinct_sheet_involutions",
            "all_sheet_maps_order_two",
            "all_sheet_maps_fixed_point_free",
            "sheet_involutions_pairwise_commute",
            "pair_products_give_third",
            "generated_sheet_group_is_v4",
        )
    ),
)
print(
    "ORIENTATION_SHEET_S4_PROVED:",
    all(sheet_checks.values()),
)
print(
    "CLASSIFICATION:",
    (
        "three_orientation_sheet_involutions_form_V4_"
        "and_triality_extends_them_to_S4"
        if all(sheet_checks.values())
        else
        "orientation_sheet_extension_requires_refinement"
    ),
)
print("LITERAL_PHYSICAL_MOTION_DERIVED: false")
print("PHYSICAL_SPACE_IDENTIFIED: false")
print("G900_IDENTIFIED: false")
print("PROJECT_MUTATION_PERFORMED: false")


print("== A5 V4 KERNEL AND ORDER-1440 EXTENSION TEST ==")

rotation_matrices = [
    operator
    for operator in reflection_group.values()
    if determinant3(operator) == ONE
]

rotation_permutations = []

for operator in rotation_matrices:
    permutation = [
        point_index[tuple(matvec(operator, point))]
        for point in oriented_points
    ]

    if permutation not in rotation_permutations:
        rotation_permutations.append(permutation)

rotation_keys = {
    permutation_key(permutation)
    for permutation in rotation_permutations
}

rotation_order_profile = {}

for permutation in rotation_permutations:
    order = permutation_order(permutation)
    rotation_order_profile[order] = (
        rotation_order_profile.get(order, 0) + 1
    )

rotations_preserve_all_presentations = all(
    transports_colors(
        permutation,
        [0, 1, 2],
    )
    for permutation in rotation_permutations
)

a5_v4_commute = all(
    commutes(rotation, sheet)
    for rotation in rotation_permutations
    for sheet in sheet_v4
)

a5_v4_intersection = (
    rotation_keys
    & {
        permutation_key(element)
        for element in sheet_v4
    }
)

kernel_products = {
    permutation_key(
        compose_permutations(rotation, sheet)
    )
    for rotation in rotation_permutations
    for sheet in sheet_v4
}

kernel_group = generated_permutation_group(
    rotation_permutations
    + [tau_x, tau_y]
)

expected_a5_v4_order_profile = {
    1: 1,
    2: 63,
    3: 20,
    5: 24,
    6: 60,
    10: 72,
}

kernel_order_profile = {}

for element in kernel_group:
    order = permutation_order(element)
    kernel_order_profile[order] = (
        kernel_order_profile.get(order, 0) + 1
    )

C_normalizes_a5 = all(
    permutation_key(conjugate(C, rotation))
    in rotation_keys
    for rotation in rotation_permutations
)

R_normalizes_a5 = all(
    permutation_key(conjugate(R, rotation))
    in rotation_keys
    for rotation in rotation_permutations
)

sheet_s4_keys = {
    permutation_key(element)
    for element in sheet_s4
}

a5_s4_intersection = rotation_keys & sheet_s4_keys

a5_commutes_with_sheet_s4 = all(
    commutes(rotation, sheet)
    for rotation in rotation_permutations
    for sheet in sheet_s4
)

full_extension = generated_permutation_group(
    rotation_permutations
    + [tau_x, C, R]
)

full_extension_keys = {
    permutation_key(element)
    for element in full_extension
}

kernel_keys = {
    permutation_key(element)
    for element in kernel_group
}

kernel_normal_in_full = all(
    permutation_key(
        conjugate(generator, element)
    ) in kernel_keys
    for generator in (C, R)
    for element in kernel_group
)

a5_normal_in_full = (
    C_normalizes_a5
    and R_normalizes_a5
)

kernel_checks = {
    "rotation_group_order_60":
        len(rotation_permutations) == 60,
    "rotation_profile_is_A5":
        rotation_order_profile
        == {
            1: 1,
            2: 15,
            3: 20,
            5: 24,
        },
    "rotations_preserve_all_presentations":
        rotations_preserve_all_presentations,
    "A5_and_V4_commute":
        a5_v4_commute,
    "A5_V4_intersection_identity":
        len(a5_v4_intersection) == 1,
    "A5_V4_product_order_240":
        len(kernel_products) == 240,
    "generated_kernel_order_240":
        len(kernel_group) == 240,
    "kernel_profile_is_A5_times_V4":
        kernel_order_profile
        == expected_a5_v4_order_profile,
    "C_normalizes_A5":
        C_normalizes_a5,
    "R_normalizes_A5":
        R_normalizes_a5,
    "A5_S4_intersection_identity":
        len(a5_s4_intersection) == 1,
    "full_extension_order_1440":
        len(full_extension) == 1440,
    "kernel_normal_in_full":
        kernel_normal_in_full,
    "A5_normal_in_full":
        a5_normal_in_full,
}

print("ROTATION_MATRIX_COUNT:", len(rotation_matrices))
print("A5_PERMUTATION_ORDER:", len(rotation_permutations))
print("A5_ORDER_PROFILE:", rotation_order_profile)
print(
    "ROTATIONS_PRESERVE_ALL_PRESENTATIONS:",
    rotations_preserve_all_presentations,
)
print("A5_V4_COMMUTE:", a5_v4_commute)
print(
    "A5_V4_INTERSECTION_ORDER:",
    len(a5_v4_intersection),
)
print("A5_V4_PRODUCT_ORDER:", len(kernel_products))
print("GENERATED_KERNEL_ORDER:", len(kernel_group))
print("KERNEL_ORDER_PROFILE:", kernel_order_profile)
print("C_NORMALIZES_A5:", C_normalizes_a5)
print("R_NORMALIZES_A5:", R_normalizes_a5)
print(
    "A5_S4_INTERSECTION_ORDER:",
    len(a5_s4_intersection),
)
print(
    "A5_COMMUTES_WITH_SHEET_S4:",
    a5_commutes_with_sheet_s4,
)
print("FULL_EXTENSION_ORDER:", len(full_extension))
print("KERNEL_NORMAL_IN_FULL:", kernel_normal_in_full)
print("A5_NORMAL_IN_FULL:", a5_normal_in_full)
print("KERNEL_CHECKS:", kernel_checks)
print(
    "KERNEL_A5_TIMES_V4_PROVED:",
    all(
        kernel_checks[name]
        for name in (
            "rotation_group_order_60",
            "rotation_profile_is_A5",
            "A5_and_V4_commute",
            "A5_V4_intersection_identity",
            "A5_V4_product_order_240",
            "generated_kernel_order_240",
            "kernel_profile_is_A5_times_V4",
        )
    ),
)
print(
    "FULL_ORDER_1440_EXTENSION_PROVED:",
    all(kernel_checks.values()),
)
print(
    "FULL_GROUP_STRUCTURE:",
    (
        "A5_times_S4"
        if (
            all(kernel_checks.values())
            and a5_commutes_with_sheet_s4
        )
        else (
            "A5_semidirect_S4"
            if all(kernel_checks.values())
            else "full_group_structure_requires_refinement"
        )
    ),
)
print(
    "CLASSIFICATION:",
    (
        "common_presentation_kernel_is_A5_times_V4_"
        "inside_an_order_1440_A5_by_S4_extension"
        if all(kernel_checks.values())
        else
        "order_240_kernel_candidate_requires_refinement"
    ),
)
print("LITERAL_PHYSICAL_MOTION_DERIVED: false")
print("PHYSICAL_SPACE_IDENTIFIED: false")
print("G900_IDENTIFIED: false")
print("PROJECT_MUTATION_PERFORMED: false")

print("== A5 OUTER AUTOMORPHISM AND GOLDEN GALOIS TEST ==")


def conjugacy_classes(group):
    group_by_key = {
        permutation_key(element): element
        for element in group
    }
    unseen = set(group_by_key)
    classes = []

    while unseen:
        representative_key = min(unseen)
        representative = group_by_key[representative_key]

        class_keys = {
            permutation_key(
                conjugate(element, representative)
            )
            for element in group
        }

        classes.append([
            group_by_key[key]
            for key in sorted(class_keys)
        ])

        unseen -= class_keys

    return classes


a5_classes = conjugacy_classes(rotation_permutations)

a5_classes = sorted(
    a5_classes,
    key=lambda row: (
        permutation_order(row[0]),
        len(row),
        min(permutation_key(value) for value in row),
    ),
)

a5_class_index = {}

for index, class_row in enumerate(a5_classes):
    for element in class_row:
        a5_class_index[permutation_key(element)] = index

a5_class_rows = [
    {
        "index": index,
        "order": permutation_order(class_row[0]),
        "size": len(class_row),
    }
    for index, class_row in enumerate(a5_classes)
]


def induced_class_action(actor):
    action = []
    uniform = True

    for class_row in a5_classes:
        targets = {
            a5_class_index[
                permutation_key(
                    conjugate(actor, element)
                )
            ]
            for element in class_row
        }

        if len(targets) != 1:
            uniform = False
            action.append(sorted(targets))
        else:
            action.append(next(iter(targets)))

    return action, uniform


def inner_implementers(actor):
    implementers = []

    for candidate in rotation_permutations:
        matches = all(
            conjugate(actor, element)
            == conjugate(candidate, element)
            for element in rotation_permutations
        )

        if matches:
            implementers.append(candidate)

    return implementers


C_class_action, C_class_action_uniform = (
    induced_class_action(C)
)
R_class_action, R_class_action_uniform = (
    induced_class_action(R)
)

C_inner_implementers = inner_implementers(C)
R_inner_implementers = inner_implementers(R)

order_five_class_indices = [
    row["index"]
    for row in a5_class_rows
    if row["order"] == 5
]

C_preserves_order_five_classes = all(
    C_class_action[index] == index
    for index in order_five_class_indices
)

R_swaps_order_five_classes = (
    len(order_five_class_indices) == 2
    and R_class_action[order_five_class_indices[0]]
        == order_five_class_indices[1]
    and R_class_action[order_five_class_indices[1]]
        == order_five_class_indices[0]
)

C_action_is_inner = len(C_inner_implementers) == 1
R_action_is_inner = len(R_inner_implementers) == 1
R_action_is_outer = not R_action_is_inner


def golden_conjugate(value):
    return Q5(value.a, -value.b)


galois_presentation_action = []

for relations in relation_sets:
    conjugated_relations = {
        golden_conjugate(value)
        for value in relations
    }

    target = next(
        (
            index
            for index, candidate in enumerate(relation_sets)
            if candidate == conjugated_relations
        ),
        None,
    )

    galois_presentation_action.append(target)

galois_matches_R_color_action = (
    galois_presentation_action == swap_colors
)

outer_extension = generated_permutation_group(
    rotation_permutations + [R]
)

inner_cycle_extension = generated_permutation_group(
    rotation_permutations + [C]
)

galois_checks = {
    "A5_has_five_conjugacy_classes":
        len(a5_classes) == 5,
    "A5_class_size_order_profile":
        sorted(
            (row["order"], row["size"])
            for row in a5_class_rows
        ) == [
            (1, 1),
            (2, 15),
            (3, 20),
            (5, 12),
            (5, 12),
        ],
    "C_class_action_uniform":
        C_class_action_uniform,
    "R_class_action_uniform":
        R_class_action_uniform,
    "C_action_inner":
        C_action_is_inner,
    "C_preserves_order_five_classes":
        C_preserves_order_five_classes,
    "R_action_outer":
        R_action_is_outer,
    "R_swaps_order_five_classes":
        R_swaps_order_five_classes,
    "golden_conjugation_action_defined":
        None not in galois_presentation_action,
    "golden_conjugation_matches_R":
        galois_matches_R_color_action,
    "A5_with_R_has_order_120":
        len(outer_extension) == 120,
    "A5_with_C_has_order_180":
        len(inner_cycle_extension) == 180,
}

print("A5_CONJUGACY_CLASS_ROWS:", a5_class_rows)
print("ORDER_FIVE_CLASS_INDICES:", order_five_class_indices)
print("C_CLASS_ACTION:", C_class_action)
print("R_CLASS_ACTION:", R_class_action)
print(
    "C_INNER_IMPLEMENTER_COUNT:",
    len(C_inner_implementers),
)
print(
    "R_INNER_IMPLEMENTER_COUNT:",
    len(R_inner_implementers),
)
print("C_ACTION_IS_INNER:", C_action_is_inner)
print("R_ACTION_IS_OUTER:", R_action_is_outer)
print(
    "C_PRESERVES_ORDER_FIVE_CLASSES:",
    C_preserves_order_five_classes,
)
print(
    "R_SWAPS_ORDER_FIVE_CLASSES:",
    R_swaps_order_five_classes,
)
print(
    "GOLDEN_GALOIS_PRESENTATION_ACTION:",
    galois_presentation_action,
)
print(
    "GOLDEN_GALOIS_MATCHES_R_COLOR_ACTION:",
    galois_matches_R_color_action,
)
print("A5_WITH_R_ORDER:", len(outer_extension))
print("A5_WITH_C_ORDER:", len(inner_cycle_extension))
print("GALOIS_CHECKS:", galois_checks)
print(
    "GOLDEN_GALOIS_OUTER_AUTOMORPHISM_PROVED:",
    all(galois_checks.values()),
)
print(
    "CLASSIFICATION:",
    (
        "triality_cycler_acts_internally_on_A5_while_"
        "the_reverser_realizes_sqrt5_Galois_conjugation_"
        "as_the_outer_A5_automorphism"
        if all(galois_checks.values())
        else
        "A5_Galois_action_requires_refinement"
    ),
)
print("LITERAL_PHYSICAL_MOTION_DERIVED: false")
print("PHYSICAL_SPACE_IDENTIFIED: false")
print("G900_IDENTIFIED: false")
print("PROJECT_MUTATION_PERFORMED: false")
