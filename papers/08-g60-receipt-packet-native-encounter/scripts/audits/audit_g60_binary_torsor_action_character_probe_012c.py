#!/usr/bin/env python3
import gc
import hashlib
import json
import pathlib
import subprocess
import sys

root = pathlib.Path(sys.argv[1]).resolve()
candidate_script = pathlib.Path(sys.argv[2]).resolve()
candidate_report = pathlib.Path(sys.argv[3]).resolve()

orientation_path = root / "artifacts/json/g60_full_A_orientation_character_extension_census_011o.v1.json"
chart_path = root / "artifacts/json/g60_native_d8_outer_c2_selector_census_011y.v1.json"
instruction_path = root / "artifacts/json/g60_gauge_covariant_update_census_012a.v1.json"

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def read_json(path):
    with path.open() as handle:
        return json.load(handle)

checks = []

def check(name, passed):
    checks.append((name, bool(passed)))

check("head", subprocess.check_output(
    ["git", "--no-pager", "show", "-s", "--format=%h %s", "HEAD"],
    cwd=root, text=True
).strip() == "4646919 Lock G60 gauge-covariant update descent")

check("candidate_script_hash",
      digest(candidate_script) == "fb7e5caa8d09110a81ff016302c976cd146eb1baf178dc0ba0e45f1b852bef2a")
check("candidate_report_hash",
      digest(candidate_report) == "868d89956ca8a2af5911334197ab5c5be92989c5d3689367a16b0e9c074d3e96")
check("orientation_hash",
      digest(orientation_path) == "ad684db8bb65c5eb731c972d33e685ffc18a947f63c9ba4e9758f815821f0941")
check("chart_hash",
      digest(chart_path) == "d5a9036cf96aa97dd8848cd947bff4d07c711db0db2e3dca3ad13ec1c9cdfdab")
check("instruction_hash",
      digest(instruction_path) == "4e6936b9b48c6f033b826df7c3ad4ac70ec3480129c5c73ec6a24630077096d2")

instruction_full = read_json(instruction_path)
instruction = {
    "local_reconstruction": {
        "presentation_rows": instruction_full[
            "local_reconstruction"
        ]["presentation_rows"],
    },
    "presentation_gauge_comparison": {
        "matched_gauge_rows": instruction_full[
            "presentation_gauge_comparison"
        ]["matched_gauge_rows"],
    },
}
del instruction_full
gc.collect()

chart_full = read_json(chart_path)
chart = {
    "local_automorphism_census": {
        "automorphism_rows_by_presentation": chart_full[
            "local_automorphism_census"
        ]["automorphism_rows_by_presentation"],
    },
    "presentation_gauge_torsor_comparison": {
        "gauge_rows": chart_full[
            "presentation_gauge_torsor_comparison"
        ]["gauge_rows"],
    },
}
del chart_full
gc.collect()

orientation_full = read_json(orientation_path)
orientation = {
    "bridge_census": orientation_full["bridge_census"],
    "anchor_ablation": orientation_full["anchor_ablation"],
}
del orientation_full
gc.collect()

for p in range(2):
    ir = sorted(
        instruction["local_reconstruction"]["presentation_rows"][p]["automorphism_rows"],
        key=lambda row: int(row["automorphism_index"]),
    )
    cr = sorted(
        chart["local_automorphism_census"]["automorphism_rows_by_presentation"][p],
        key=lambda row: int(row["automorphism_index"]),
    )

    ibits = []
    cbits = []
    for irow, crow in zip(ir, cr):
        mapping = [int(x) for x in irow["mapping"]]
        image = [mapping[2], mapping[3]]
        check("p%d_pair_preserved_%d" % (p, len(ibits)),
              image in ([2, 3], [3, 2]))
        ibits.append(int(image == [3, 2]))

        permutation = [
            int(x)
            for x in crow["induced_global_orbit_permutation"]
        ]
        check("p%d_chart_perm_%d" % (p, len(cbits)),
              permutation in ([0, 1], [1, 0]))
        cbits.append(int(permutation == [1, 0]))

    check("p%d_instruction_bits" % p,
          ibits == [0, 0, 0, 0, 1, 1, 1, 1])
    check("p%d_chart_bits" % p,
          cbits == [0, 0, 1, 1, 0, 0, 1, 1])
    check("p%d_instruction_kernel" % p,
          [i for i, bit in enumerate(ibits) if bit == 0] == [0, 1, 2, 3])
    check("p%d_chart_kernel" % p,
          [i for i, bit in enumerate(cbits) if bit == 0] == [0, 1, 4, 5])
    check("p%d_joint_image" % p,
          sorted(set(zip(ibits, cbits))) == [(0, 0), (0, 1), (1, 0), (1, 1)])

ig = sorted(
    instruction["presentation_gauge_comparison"]["matched_gauge_rows"],
    key=lambda row: int(row["gauge_index"]),
)
cg = sorted(
    chart["presentation_gauge_torsor_comparison"]["gauge_rows"],
    key=lambda row: int(row["gauge_index"]),
)

instruction_gauge_bits = []
chart_gauge_bits = []

for irow, crow in zip(ig, cg):
    mapping = [int(x) for x in irow["local_isomorphism"]]
    image = [mapping[2], mapping[3]]
    instruction_gauge_bits.append(int(image == [3, 2]))
    chart_gauge_bits.append(
        int(not bool(crow["preserves_orbit_labels"]))
    )

check("instruction_gauge_bits",
      instruction_gauge_bits == [0, 0, 1, 1])
check("chart_gauge_bits",
      chart_gauge_bits == [0, 0, 0, 0])
check("gauge_deltas",
      sorted(set(
          a ^ b
          for a, b in zip(instruction_gauge_bits, chart_gauge_bits)
      )) == [0, 1])

reversal = sorted(
    orientation["bridge_census"]["reversal_rows"],
    key=lambda row: int(row["map_index"]),
)
check("orientation_bridge_count",
      orientation["bridge_census"]["alpha_1_bridge_count"] == 2)
check("sheet_reversal_targets",
      [row["sheet_reversal_map_indices"] for row in reversal] == [[1], [0]])
check("root_inversion_targets",
      [row["root_inversion_map_indices"] for row in reversal] == [[1], [0]])
check("anchors_unique",
      orientation["anchor_ablation"]["all_compatible_anchors_select_unique_bridge"] is True)

text = candidate_report.read_text()
for marker in [
    "CLASSIFICATION: instruction_and_chart_are_independent_C2_characters_on_local_Aut_D8",
    "INSTRUCTION_CHART_CHARACTERS_EQUAL: false",
    "COMBINED_CHARACTER_IMAGE_IS_C2xC2: true",
    "GAUGE_COMPATIBLE_BIJECTION_FAMILY_EXISTS: false",
    "ORIENTATION_COMMON_ACTING_GROUP_LINK_ESTABLISHED: false",
    "THREE_WAY_CANONICAL_IDENTIFICATION_ESTABLISHED: false",
    "ANCHOR_TRANSFER_ESTABLISHED: false",
    "PROJECT_MUTATION_PERFORMED: false",
]:
    check("report_marker_" + marker.split(":")[0], marker in text)

failed = [name for name, passed in checks if not passed]

print("== G60 BINARY TORSOR ACTION CHARACTER GUARD 012c ==")
print("CHECK_COUNT:", len(checks))
print("FAILED_CHECK_COUNT:", len(failed))
for name, passed in checks:
    print("CHECK", name + ":", str(passed).lower())
print("GUARD_PASS:", str(not failed).lower())
print("FAILED_CHECKS:", failed)
print("CANDIDATE_PROMOTED: false")
print("PROJECT_MUTATION_PERFORMED: false")

if failed:
    raise SystemExit(1)
