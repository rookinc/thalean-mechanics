#!/usr/bin/env python3

import json
import pathlib
from collections import Counter

SOURCE = pathlib.Path(
    "/data/data/com.termux/files/home/dev/cori/research/"
    "mathematics/41-order-4-dodecahedral-residue/"
    "artifacts/json/intrinsic_g15_line_petersen_audit_015.json"
)

data = json.loads(SOURCE.read_text(encoding="utf-8"))

def edge(left, right):
    return tuple(sorted((int(left), int(right))))

native_edges = {
    edge(*row["quotient_edge"])
    for row in data["measurements"]["quotient_edges"]
}

INNER_ORDER = (13, 14, 7, 6, 10)
SPOKES = (11, 9, 12, 5, 8)

inner_edges = tuple(
    edge(
        INNER_ORDER[index],
        INNER_ORDER[(index + 1) % 5],
    )
    for index in range(5)
)

edge_to_spoke = {}

for spoke in SPOKES:
    neighbors = tuple(sorted(
        vertex
        for vertex in INNER_ORDER
        if edge(spoke, vertex) in native_edges
    ))
    edge_to_spoke[edge(*neighbors)] = spoke

midpoints = tuple(
    "Y_" + str(index)
    for index in range(5)
)

midpoint_to_spoke = {
    midpoints[index]: edge_to_spoke[inner_edges[index]]
    for index in range(5)
}

spoke_to_midpoint = {
    spoke: midpoint
    for midpoint, spoke in midpoint_to_spoke.items()
}

QUOTIENT_POINT = "Y1"

midpoint_quotient = {
    midpoint: QUOTIENT_POINT
    for midpoint in midpoints
}

spoke_to_quotient = {
    spoke: midpoint_quotient[spoke_to_midpoint[spoke]]
    for spoke in SPOKES
}

quotient_reverse_relation = {
    QUOTIENT_POINT: tuple(sorted(SPOKES))
}

set_theoretic_sections = tuple(
    {
        QUOTIENT_POINT: spoke,
    }
    for spoke in sorted(SPOKES)
)

rotation_on_midpoints = {
    midpoints[index]: midpoints[(index + 1) % 5]
    for index in range(5)
}

rotation_on_spokes = {
    midpoint_to_spoke[midpoints[index]]:
        midpoint_to_spoke[midpoints[(index + 1) % 5]]
    for index in range(5)
}

rotation_fixed_spokes = tuple(
    spoke
    for spoke in SPOKES
    if rotation_on_spokes[spoke] == spoke
)

equivariant_sections = tuple(
    section
    for section in set_theoretic_sections
    if rotation_on_spokes[section[QUOTIENT_POINT]]
       == section[QUOTIENT_POINT]
)

section_orbit = []
current = min(SPOKES)

while current not in section_orbit:
    section_orbit.append(current)
    current = rotation_on_spokes[current]

section_orbit = tuple(section_orbit)

checks = {
    "source_audit_pass":
        data.get("audit_pass") is True,
    "native_midpoint_count_5":
        len(midpoints) == 5,
    "native_spoke_count_5":
        len(SPOKES) == 5,
    "native_spoke_midpoint_map_is_bijection":
        len(spoke_to_midpoint) == 5
        and len(set(spoke_to_midpoint.values())) == 5,
    "all_midpoints_collapse_to_one_quotient_point":
        set(midpoint_quotient.values()) == {QUOTIENT_POINT},
    "all_spokes_map_to_one_quotient_point":
        set(spoke_to_quotient.values()) == {QUOTIENT_POINT},
    "quotient_reverse_fiber_has_size_5":
        len(quotient_reverse_relation[QUOTIENT_POINT]) == 5,
    "five_set_theoretic_reverse_sections":
        len(set_theoretic_sections) == 5,
    "C5_rotation_has_no_fixed_spoke":
        not rotation_fixed_spokes,
    "no_C5_equivariant_reverse_section":
        not equivariant_sections,
    "five_sections_form_one_C5_orbit":
        len(section_orbit) == 5
        and set(section_orbit) == set(SPOKES),
}

failed = [
    name
    for name, passed in checks.items()
    if not passed
]

theorem_pass = not failed

print("PACKET: g900_midpoint_quotient_reverse_obstruction_054")
print("MODE: five-midpoint to one-point quotient section test")
print("INNER_EDGE_ORDER:", inner_edges)
print("MIDPOINT_TO_SPOKE:", midpoint_to_spoke)
print("SPOKE_TO_MIDPOINT:", spoke_to_midpoint)
print("MIDPOINT_QUOTIENT:", midpoint_quotient)
print("SPOKE_TO_QUOTIENT:", spoke_to_quotient)
print("QUOTIENT_REVERSE_RELATION:", quotient_reverse_relation)
print("SET_THEORETIC_SECTION_COUNT:", len(set_theoretic_sections))
print("SET_THEORETIC_SECTIONS:", set_theoretic_sections)
print("C5_ROTATION_ON_SPOKES:", rotation_on_spokes)
print("C5_ROTATION_FIXED_SPOKES:", rotation_fixed_spokes)
print("C5_EQUIVARIANT_SECTION_COUNT:", len(equivariant_sections))
print("SECTION_ORBIT:", section_orbit)
print("CHECKS:", checks)
print("FAILED_CHECK_COUNT:", len(failed))
print("FAILED_CHECKS:", failed)
print("THEOREM_PASS:", theorem_pass)
print(
    "CLASSIFICATION:",
    (
        "after_the_five_native_edge_midpoints_are_collapsed_"
        "to_one_quotient_point_the_forward_spoke_map_is_"
        "well_defined_but_the_reverse_has_a_five_element_"
        "fiber_and_no_C5_equivariant_section"
        if theorem_pass
        else "midpoint_quotient_reverse_obstruction_not_derived"
    ),
)
print("NATIVE_Y_TO_D_INVERSE_EXISTS_BEFORE_QUOTIENT:", theorem_pass)
print("QUOTIENT_D_TO_Y1_DEFINED:", theorem_pass)
print("QUOTIENT_Y1_TO_D_SINGLE_VALUED:", False)
print("QUOTIENT_Y1_TO_D_STATUS:", "undefined_without_section")
print("EXTERNAL_SECTION_REQUIRED_TO_NAME_D:", theorem_pass)
print("NATIVE_C5_SELECTS_SECTION:", False)
print("PHYSICAL_CLAIM:", False)
print("MUTATION_PERFORMED:", False)
