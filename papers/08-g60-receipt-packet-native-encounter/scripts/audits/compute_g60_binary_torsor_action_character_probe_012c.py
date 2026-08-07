#!/usr/bin/env python3

import gc
import hashlib
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1]).resolve()

p_orientation = root / "artifacts/json/g60_full_A_orientation_character_extension_census_011o.v1.json"
p_chart = root / "artifacts/json/g60_native_d8_outer_c2_selector_census_011y.v1.json"
p_instruction = root / "artifacts/json/g60_gauge_covariant_update_census_012a.v1.json"

def sha256_file(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def load(path):
    with path.open() as handle:
        return json.load(handle)

def pair_bit(mapping, pair):
    image = [int(mapping[pair[0]]), int(mapping[pair[1]])]
    if image == pair:
        return 0
    if image == [pair[1], pair[0]]:
        return 1
    raise AssertionError(("pair not preserved", pair, image))

instruction = load(p_instruction)
instruction_rows = instruction["local_reconstruction"]["presentation_rows"]
instruction_gauges = instruction["presentation_gauge_comparison"]["matched_gauge_rows"]
del instruction
gc.collect()

chart = load(p_chart)
chart_rows = chart["local_automorphism_census"]["automorphism_rows_by_presentation"]
chart_gauges = chart["presentation_gauge_torsor_comparison"]["gauge_rows"]
del chart
gc.collect()

orientation = load(p_orientation)
reversal_rows = orientation["bridge_census"]["reversal_rows"]
orientation_summary = {
    "bridge_count": orientation["bridge_census"]["alpha_1_bridge_count"],
    "reversal_verified": orientation["bridge_census"]["reversal_verified"],
    "without_anchor_bridge_count": orientation["anchor_ablation"]["without_anchor_bridge_count"],
    "compatible_anchor_count": len(orientation["anchor_ablation"]["anchor_rows"]),
    "all_anchors_select_unique_bridge": orientation["anchor_ablation"]["all_compatible_anchors_select_unique_bridge"],
}
del orientation
gc.collect()

print("PACKET: g60_binary_torsor_action_character_probe_012c")
print("MODE: read_only_exact_action_character_comparison")
print("REPOSITORY_MUTATION: none")
print("CANONICAL_IDENTIFICATION_ASSUMED: false")
print("ORIENTATION_AUT_D8_LINK_ASSUMED: false")
print("SOURCE_SHA256_ORIENTATION:", sha256_file(p_orientation))
print("SOURCE_SHA256_CHART:", sha256_file(p_chart))
print("SOURCE_SHA256_INSTRUCTION:", sha256_file(p_instruction))

presentation_results = []

for presentation_index in range(2):
    irow = instruction_rows[presentation_index]
    pair = [int(x) for x in irow["order_four_elements"]]
    iauts = {
        int(row["automorphism_index"]): row
        for row in irow["automorphism_rows"]
    }
    cauts = {
        int(row["automorphism_index"]): row
        for row in chart_rows[presentation_index]
    }

    indices = sorted(set(iauts) & set(cauts))
    joined = []
    for index in indices:
        ibit = pair_bit(iauts[index]["mapping"], pair)
        cperm = [
            int(x)
            for x in cauts[index]["induced_global_orbit_permutation"]
        ]
        if cperm == [0, 1]:
            cbit = 0
        elif cperm == [1, 0]:
            cbit = 1
        else:
            raise AssertionError(("bad chart permutation", cperm))

        joined.append({
            "automorphism_index": index,
            "automorphism_order": int(iauts[index]["order"]),
            "chart_class": cauts[index]["class"],
            "instruction_bit": ibit,
            "chart_bit": cbit,
        })

    ikernel = [
        row["automorphism_index"]
        for row in joined
        if row["instruction_bit"] == 0
    ]
    ckernel = [
        row["automorphism_index"]
        for row in joined
        if row["chart_bit"] == 0
    ]
    intersection = sorted(set(ikernel) & set(ckernel))
    combined_image = sorted({
        (row["instruction_bit"], row["chart_bit"])
        for row in joined
    })
    same_character = all(
        row["instruction_bit"] == row["chart_bit"]
        for row in joined
    )

    result = {
        "presentation_index": presentation_index,
        "instruction_pair": pair,
        "joined_automorphism_count": len(joined),
        "instruction_kernel_indices": ikernel,
        "chart_kernel_indices": ckernel,
        "kernel_intersection_indices": intersection,
        "combined_character_image": combined_image,
        "characters_equal": same_character,
        "equivariant_bijection_exists_under_common_Aut_D8": same_character,
        "rows": joined,
    }
    presentation_results.append(result)

    print()
    print("PRESENTATION:", presentation_index)
    print("INSTRUCTION_PAIR:", pair)
    print("JOINED_AUTOMORPHISM_COUNT:", len(joined))
    for row in joined:
        print("AUT_ROW:", json.dumps(row, sort_keys=True))
    print("INSTRUCTION_KERNEL_INDICES:", ikernel)
    print("CHART_KERNEL_INDICES:", ckernel)
    print("KERNEL_INTERSECTION_INDICES:", intersection)
    print("COMBINED_CHARACTER_IMAGE:", combined_image)
    print("CHARACTERS_EQUAL:", str(same_character).lower())
    print("AUT_D8_EQUIVARIANT_BIJECTION_EXISTS:", str(same_character).lower())

igauges = {
    int(row["gauge_index"]): row
    for row in instruction_gauges
}
cgauges = {
    int(row["gauge_index"]): row
    for row in chart_gauges
}

gauge_deltas = []
print()
print("== PRESENTATION GAUGE COMPARISON ==")

for gauge_index in sorted(set(igauges) & set(cgauges)):
    imap = [int(x) for x in igauges[gauge_index]["local_isomorphism"]]
    ibit = pair_bit(imap, [2, 3])
    preserves = bool(cgauges[gauge_index]["preserves_orbit_labels"])
    cbit = 0 if preserves else 1
    delta = ibit ^ cbit
    gauge_deltas.append(delta)
    print(
        "GAUGE_ROW:",
        json.dumps({
            "gauge_index": gauge_index,
            "instruction_bit": ibit,
            "chart_bit": cbit,
            "comparison_delta": delta,
        }, sort_keys=True),
    )

gauge_delta_set = sorted(set(gauge_deltas))
gauge_compatible_family = len(gauge_delta_set) == 1

print("GAUGE_COMPARISON_DELTAS:", gauge_delta_set)
print("GAUGE_COMPATIBLE_BIJECTION_FAMILY_EXISTS:",
      str(gauge_compatible_family).lower())

print()
print("== ORIENTATION REVERSAL TORSOR ==")
print("ORIENTATION_SUMMARY:", json.dumps(orientation_summary, sort_keys=True))

orientation_bits = []
for row in sorted(reversal_rows, key=lambda x: int(x["map_index"])):
    index = int(row["map_index"])
    sheet_target = int(row["sheet_reversal_map_indices"][0])
    root_target = int(row["root_inversion_map_indices"][0])
    sheet_bit = int(sheet_target != index)
    root_bit = int(root_target != index)
    orientation_bits.append(sheet_bit)
    print(
        "ORIENTATION_ROW:",
        json.dumps({
            "map_index": index,
            "sheet_reversal_target": sheet_target,
            "root_inversion_target": root_target,
            "sheet_reversal_bit": sheet_bit,
            "root_inversion_bit": root_bit,
        }, sort_keys=True),
    )

instruction_chart_equal = all(
    row["characters_equal"]
    for row in presentation_results
)
combined_image_full = all(
    len(row["combined_character_image"]) == 4
    for row in presentation_results
)

if not instruction_chart_equal and combined_image_full:
    classification = (
        "instruction_and_chart_are_independent_C2_characters_"
        "on_local_Aut_D8"
    )
elif instruction_chart_equal:
    classification = (
        "instruction_and_chart_share_the_same_local_Aut_D8_character"
    )
else:
    classification = (
        "instruction_and_chart_characters_differ_without_full_independence"
    )

print()
print("== RESULT ==")
print("CLASSIFICATION:", classification)
print("INSTRUCTION_CHART_CHARACTERS_EQUAL:",
      str(instruction_chart_equal).lower())
print("COMBINED_CHARACTER_IMAGE_IS_C2xC2:",
      str(combined_image_full).lower())
print("GAUGE_COMPATIBLE_BIJECTION_FAMILY_EXISTS:",
      str(gauge_compatible_family).lower())
print("ORIENTATION_REVERSAL_BITS:", orientation_bits)
print("ORIENTATION_COMMON_ACTING_GROUP_LINK_ESTABLISHED: false")
print("THREE_WAY_CANONICAL_IDENTIFICATION_ESTABLISHED: false")
print("ANCHOR_TRANSFER_ESTABLISHED: false")
print("PROJECT_MUTATION_PERFORMED: false")
