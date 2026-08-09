#!/usr/bin/env python3

import itertools
import json

P08 = (
    "/data/data/com.termux/files/home/dev/cori/research/"
    "thalean_mechanics/papers/"
    "08-g60-receipt-packet-native-encounter"
)

Y = P08 + (
    "/artifacts/json/"
    "g60_native_d8_outer_c2_selector_census_011y.v1.json"
)
W = P08 + (
    "/artifacts/json/"
    "g60_native_d8_chart_coherence_census_011w.v1.json"
)
C25 = P08 + (
    "/artifacts/json/"
    "g60_native_rosette_pipe_null_corollary_025.v1.json"
)

y = json.load(open(Y))
w = json.load(open(W))
c25 = json.load(open(C25))

def values(value, key):
    out = []
    if isinstance(value, dict):
        for k, v in value.items():
            if k == key:
                out.append(v)
            out.extend(values(v, key))
    elif isinstance(value, list):
        for item in value:
            out.extend(values(item, key))
    return out

def has_true(value, key):
    return any(v is True for v in values(value, key))

def has_false(value, key):
    return any(v is False for v in values(value, key))

SECTIONS = (0, 1)

def outer_swap(section):
    return section ^ 1

# Enumerate all binary properties on the two sections.
labelings = []
for outputs in itertools.product((0, 1), repeat=2):
    labeling = {
        0: outputs[0],
        1: outputs[1],
    }
    invariant = all(
        labeling[outer_swap(section)] == labeling[section]
        for section in SECTIONS
    )
    separates = labeling[0] != labeling[1]
    labelings.append({
        "outputs": outputs,
        "outer_invariant": invariant,
        "separates_sections": separates,
    })

invariant_labelings = [
    row for row in labelings
    if row["outer_invariant"]
]
separating_labelings = [
    row for row in labelings
    if row["separates_sections"]
]
invariant_separating = [
    row for row in labelings
    if row["outer_invariant"]
    and row["separates_sections"]
]

# The two separating labelings are exchanged by reversing
# the external orientation bit.
separating_pairs = {
    row["outputs"] for row in separating_labelings
}

presentation_rows = values(y, "presentation_rows")[0]

checks = {
    "source_011y_audit_pass": y["audit_pass"] is True,
    "source_011w_audit_pass": w["audit_pass"] is True,
    "source_025_audit_pass": c25["audit_pass"] is True,
    "both_presentations_loaded": len(presentation_rows) == 2,
    "all_outer_exchange_fiber_orbits": all(
        row["all_outer_exchange_fiber_orbits"] is True
        for row in presentation_rows
    ),
    "alpha1_constant_under_outer_exchange": has_true(
        y,
        "alpha_1_constant_under_outer_exchange",
    ),
    "q_axis_constant_under_outer_exchange": has_true(
        y,
        "q_axis_signature_constant_under_outer_exchange",
    ),
    "native_single_orbit_selector_count_zero": (
        0 in values(
            y,
            "outer_gauge_invariant_single_orbit_selector_count",
        )
    ),
    "locked_character_does_not_select_orbit": has_false(
        w,
        "locked_character_data_selects_one_outer_orbit",
    ),
    "residual_outer_gauge_is_C2": (
        "C2" in values(w, "residual_outer_gauge_group")
    ),
    "binary_property_count_4": len(labelings) == 4,
    "outer_invariant_property_count_2": (
        len(invariant_labelings) == 2
    ),
    "section_separating_property_count_2": (
        len(separating_labelings) == 2
    ),
    "no_invariant_property_separates_sections": (
        len(invariant_separating) == 0
    ),
    "separating_pair_is_orientation_pair": (
        separating_pairs == {(0, 1), (1, 0)}
    ),
}

failed = [
    name for name, passed in checks.items()
    if not passed
]
theorem_pass = not failed

print("PACKET: g900_registration_signature_dominance_probe_027")
print("MODE: native outer-C2 selector obstruction")
print("ALL_BINARY_LABELINGS:", labelings)
print("INVARIANT_LABELING_COUNT:", len(invariant_labelings))
print("SEPARATING_LABELING_COUNT:", len(separating_labelings))
print(
    "INVARIANT_SEPARATING_LABELING_COUNT:",
    len(invariant_separating),
)
print(
    "SEPARATING_ORIENTATION_PAIR:",
    sorted(separating_pairs),
)
print("CHECKS:", checks)
print("FAILED_CHECK_COUNT:", len(failed))
print("FAILED_CHECKS:", failed)
print("THEOREM_PASS:", theorem_pass)
print(
    "CLASSIFICATION:",
    (
        "native_outer_C2_forbids_absolute_registration_"
        "signature_dominance_but_allows_an_externally_"
        "oriented_covariant_pair"
        if theorem_pass
        else "registration_signature_dominance_boundary_unresolved"
    ),
)
print("NATIVE_REGISTRATION_DOMINANT_SECTION_SELECTED:", False)
print("NATIVE_SIGNATURE_DOMINANT_SECTION_SELECTED:", False)
print("COVARIANT_DOMINANCE_PAIR_AVAILABLE:", theorem_pass)
print("EXTERNAL_C2_BIT_REQUIRED_TO_NAME_PAIR:", theorem_pass)
print("PHYSICAL_DOMINANCE_CLAIM:", False)
print("MUTATION_PERFORMED:", False)
