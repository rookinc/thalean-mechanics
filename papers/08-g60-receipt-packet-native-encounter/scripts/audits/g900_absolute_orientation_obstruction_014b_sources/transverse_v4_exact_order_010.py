#!/usr/bin/env python3

import json
import math
import pathlib
import sys

from sympy import __version__ as sympy_version
from sympy.combinatorics import Permutation, PermutationGroup

p41 = pathlib.Path(sys.argv[1]).resolve()
h60_path = pathlib.Path(sys.argv[2]).resolve()
duad_path = pathlib.Path(sys.argv[3]).resolve()

sys.path.insert(0, str(p41))

from scripts.lib.project41_native import (
    IDENTITY60,
    load_native_source_layer,
)

identity = tuple(IDENTITY60)

def compose(left, right):
    return tuple(
        left[right[index]]
        for index in range(len(left))
    )

def invert(permutation):
    result = [None] * len(permutation)

    for source, target in enumerate(permutation):
        result[target] = source

    return tuple(result)

def conjugate(conjugator, element):
    return compose(
        conjugator,
        compose(element, invert(conjugator)),
    )

def fixed_point_count(permutation):
    return sum(
        source == target
        for source, target in enumerate(permutation)
    )

def inversion_parity(permutation):
    parity = 0

    for left in range(len(permutation)):
        for right in range(left + 1, len(permutation)):
            if permutation[left] > permutation[right]:
                parity ^= 1

    return parity

h60 = json.loads(
    h60_path.read_text(encoding="utf-8")
)
duad = json.loads(
    duad_path.read_text(encoding="utf-8")
)
layer = load_native_source_layer(p41)

h60_elements = {
    tuple(row)
    for row in h60["elements"]
}

old_v4_indices = duad[
    "kernel_action"
]["native_v4_indices_derived_as_duad_kernel"]

native_v4 = {
    tuple(h60["elements"][index])
    for index in old_v4_indices
}

half_flip = tuple(layer.half_flip)

transverse_v4 = {
    conjugate(half_flip, element)
    for element in native_v4
}

generators = sorted(
    (native_v4 | transverse_v4) - {identity}
)

generator_rows = []

for index, generator in enumerate(generators):
    generator_rows.append({
        "index": index,
        "fixed_points": fixed_point_count(generator),
        "parity": inversion_parity(generator),
        "sympy_signature":
            Permutation(list(generator)).signature(),
    })

sympy_generators = [
    Permutation(list(generator))
    for generator in generators
]

group = PermutationGroup(sympy_generators)

print("== G900 TRANSVERSE V4 EXACT ORDER AUDIT 010 ==")
print("SYMPY_VERSION:", sympy_version)
print("GENERATOR_COUNT:", len(generators))
print("SCHREIER_SIMS_STARTED: true", flush=True)

group_order = int(group.order())

print("SCHREIER_SIMS_COMPLETED: true", flush=True)

s60_order = math.factorial(60)
a60_order = s60_order // 2

all_generators_even = all(
    row["parity"] == 0
    and row["sympy_signature"] == 1
    for row in generator_rows
)

is_transitive = bool(group.is_transitive())
is_primitive = bool(group.is_primitive())

if all_generators_even and group_order == a60_order:
    classification = (
        "transverse_V4_pair_generates_exact_A60"
    )
elif group_order == s60_order:
    classification = (
        "transverse_V4_pair_generates_exact_S60"
    )
else:
    classification = (
        "transverse_V4_pair_generates_proper_"
        "large_subgroup_of_A60"
        if all_generators_even
        else
        "transverse_V4_pair_generates_"
        "nonalternating_subgroup"
    )

checks = {
    "h60_order_480":
        len(h60_elements) == 480,
    "native_v4_order_4":
        len(native_v4) == 4,
    "transverse_v4_order_4":
        len(transverse_v4) == 4,
    "intersection_identity_only":
        native_v4.intersection(transverse_v4)
        == {identity},
    "six_generators":
        len(generators) == 6,
    "all_generators_fixed_point_free":
        all(
            row["fixed_points"] == 0
            for row in generator_rows
        ),
    "parity_methods_agree":
        all(
            (1 if row["parity"] == 0 else -1)
            == row["sympy_signature"]
            for row in generator_rows
        ),
    "group_order_positive":
        group_order > 0,
}

failed = [
    name
    for name, passed in checks.items()
    if not passed
]

print("NATIVE_V4_ORDER:", len(native_v4))
print("TRANSVERSE_V4_ORDER:", len(transverse_v4))
print(
    "V4_INTERSECTION_ORDER:",
    len(native_v4.intersection(transverse_v4)),
)

for row in generator_rows:
    print(
        "GENERATOR",
        row["index"],
        "FIXED_POINTS",
        row["fixed_points"],
        "PARITY",
        row["parity"],
        "SIGNATURE",
        row["sympy_signature"],
    )

print("ALL_GENERATORS_EVEN:", all_generators_even)
print("GROUP_ORDER:", group_order)
print("GROUP_ORDER_DIGITS:", len(str(group_order)))
print("A60_ORDER:", a60_order)
print("S60_ORDER:", s60_order)
print("ORDER_EQUALS_A60:", group_order == a60_order)
print("ORDER_EQUALS_S60:", group_order == s60_order)
print("TRANSITIVE:", is_transitive)
print("PRIMITIVE:", is_primitive)
print("BASE_LENGTH:", len(group.base))
print(
    "STRONG_GENERATOR_COUNT:",
    len(group.strong_gens),
)
print("CHECKS:", checks)
print("FAILED_CHECK_COUNT:", len(failed))
print("FAILED_CHECKS:", failed)
print("AUDIT_PASS:", not failed)
print("CLASSIFICATION:", classification)
print("PHYSICAL_CLAIM: false")
print("PROJECT_MUTATION_PERFORMED: false")

if failed:
    raise SystemExit(1)
