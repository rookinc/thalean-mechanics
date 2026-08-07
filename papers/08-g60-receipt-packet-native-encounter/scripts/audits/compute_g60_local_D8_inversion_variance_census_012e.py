#!/usr/bin/env python3
import gc
import hashlib
import json
import pathlib
import subprocess
import sys

root = pathlib.Path(sys.argv[1]).resolve()
json_output = pathlib.Path(sys.argv[2]).resolve()

update_path = root / "artifacts/json/g60_gauge_covariant_update_census_012a.v1.json"
orientation_path = root / "artifacts/json/g60_full_A_orientation_character_extension_census_011o.v1.json"
prereg_path = root / "artifacts/json/g60_local_D8_inversion_variance_preregistration_012d.v1.json"

def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def load(path):
    with path.open() as handle:
        return json.load(handle)

head = subprocess.check_output(
    ["git", "--no-pager", "show", "-s", "--format=%h %s", "HEAD"],
    cwd=root,
    text=True,
).strip()

prereg = load(prereg_path)
update_full = load(update_path)
local_rows = update_full["local_reconstruction"]["presentation_rows"]
del update_full
gc.collect()

presentation_rows = []

for presentation_index, source_row in enumerate(local_rows):
    table = [
        [int(value) for value in row]
        for row in source_row["multiplication_table"]
    ]
    size = len(table)

    identities = [
        e for e in range(size)
        if all(
            table[e][x] == x and table[x][e] == x
            for x in range(size)
        )
    ]
    identity = identities[0] if len(identities) == 1 else None

    inverse = []
    inverse_uniqueness_failures = []
    for x in range(size):
        candidates = [
            y for y in range(size)
            if table[x][y] == identity
            and table[y][x] == identity
        ]
        if len(candidates) == 1:
            inverse.append(candidates[0])
        else:
            inverse.append(None)
            inverse_uniqueness_failures.append([x, candidates])

    noncommuting_pairs = [
        [x, y]
        for x in range(size)
        for y in range(size)
        if table[x][y] != table[y][x]
    ]

    ordinary_failures = [
        [x, y]
        for x in range(size)
        for y in range(size)
        if inverse[table[x][y]]
        != table[inverse[x]][inverse[y]]
    ]

    anti_failures = [
        [x, y]
        for x in range(size)
        for y in range(size)
        if inverse[table[x][y]]
        != table[inverse[y]][inverse[x]]
    ]

    right_to_left_failures = [
        [state, instruction]
        for state in range(size)
        for instruction in range(size)
        if inverse[table[state][instruction]]
        != table[inverse[instruction]][inverse[state]]
    ]

    right_to_right_failures = [
        [state, instruction]
        for state in range(size)
        for instruction in range(size)
        if inverse[table[state][instruction]]
        != table[inverse[state]][inverse[instruction]]
    ]

    automorphisms = [
        [int(value) for value in row["mapping"]]
        for row in source_row["automorphism_rows"]
    ]
    order_four = [
        int(value) for value in source_row["order_four_elements"]
    ]

    presentation_rows.append({
        "presentation_index": presentation_index,
        "local_group_order": size,
        "identity_indices": identities,
        "inverse_permutation": inverse,
        "inverse_uniqueness_failures": inverse_uniqueness_failures,
        "noncommuting_pair_count": len(noncommuting_pairs),
        "inversion_involutive": all(
            inverse[inverse[x]] == x for x in range(size)
        ),
        "inversion_fixed_points": [
            x for x in range(size) if inverse[x] == x
        ],
        "order_four_elements": order_four,
        "order_four_inverse_images": [
            inverse[x] for x in order_four
        ],
        "ordinary_homomorphism_failure_count":
            len(ordinary_failures),
        "anti_homomorphism_failure_count":
            len(anti_failures),
        "inversion_matches_automorphism_indices": [
            index for index, mapping in enumerate(automorphisms)
            if mapping == inverse
        ],
        "right_update_to_left_inverse_failure_count":
            len(right_to_left_failures),
        "right_update_to_right_inverse_failure_count":
            len(right_to_right_failures),
        "double_inversion_failure_count": sum(
            inverse[inverse[x]] != x for x in range(size)
        )
    })

del local_rows
gc.collect()

orientation_full = load(orientation_path)
reversal_rows = orientation_full["bridge_census"]["reversal_rows"]
orientation_bridge_count = orientation_full[
    "bridge_census"
]["alpha_1_bridge_count"]
orientation_reversal_verified = orientation_full[
    "bridge_census"
]["reversal_verified"]
del orientation_full
gc.collect()

checks = []

def check(name, passed):
    checks.append((name, bool(passed)))

check(
    "head",
    head == "cb7c2db Preregister G60 local D8 inversion variance",
)
check(
    "prereg_hash",
    digest(prereg_path)
    == "16ece0c496bfa2021e60e3c36df523825efbd8db13bcc6b0871fd903da6c50aa",
)
check(
    "update_hash",
    digest(update_path)
    == prereg["authorities"]["update_012a_sha256"],
)
check(
    "orientation_hash",
    digest(orientation_path)
    == prereg["authorities"]["orientation_011o_sha256"],
)

for row in presentation_rows:
    p = row["presentation_index"]
    prefix = "p" + str(p) + "_"
    check(prefix + "order_8", row["local_group_order"] == 8)
    check(prefix + "identity_unique",
          len(row["identity_indices"]) == 1)
    check(prefix + "nonabelian",
          row["noncommuting_pair_count"] > 0)
    check(prefix + "inverse_unique",
          not row["inverse_uniqueness_failures"])
    check(prefix + "involutive",
          row["inversion_involutive"] is True)
    check(prefix + "fixed_points_6",
          len(row["inversion_fixed_points"]) == 6)
    check(prefix + "order_four_2_3",
          row["order_four_elements"] == [2, 3])
    check(prefix + "order_four_exchanged",
          row["order_four_inverse_images"] == [3, 2])
    check(prefix + "ordinary_failures_positive",
          row["ordinary_homomorphism_failure_count"] > 0)
    check(prefix + "anti_failures_zero",
          row["anti_homomorphism_failure_count"] == 0)
    check(prefix + "not_in_Aut_D8",
          not row["inversion_matches_automorphism_indices"])
    check(prefix + "right_to_left_zero",
          row["right_update_to_left_inverse_failure_count"] == 0)
    check(prefix + "right_to_right_positive",
          row["right_update_to_right_inverse_failure_count"] > 0)
    check(prefix + "double_inversion_zero",
          row["double_inversion_failure_count"] == 0)

check("orientation_bridge_count_2",
      orientation_bridge_count == 2)
check("orientation_reversal_verified",
      orientation_reversal_verified is True)
check("orientation_reversal_row_count",
      len(reversal_rows) == 2)
check(
    "sheet_reversal_swaps",
    [
        row["sheet_reversal_map_indices"]
        for row in reversal_rows
    ] == [[1], [0]],
)
check(
    "root_inversion_swaps",
    [
        row["root_inversion_map_indices"]
        for row in reversal_rows
    ] == [[1], [0]],
)
check(
    "sheet_equals_root_inversion",
    all(
        row["sheet_reversal_equals_root_inversion"]
        for row in reversal_rows
    ),
)

failed = [name for name, passed in checks if not passed]
audit_pass = not failed

classification = (
    "local_D8_inversion_is_opposite_law_isomorphism_"
    "not_Aut_D8_character"
    if audit_pass
    else "preregistered_inversion_variance_prediction_failed"
)

candidate = {
    "packet":
        "g60_local_D8_inversion_variance_census_012e",
    "mode":
        "temporary_read_only_complete_local_inversion_variance_census",
    "locked_head": head,
    "authorities": {
        str(prereg_path): {
            "sha256": digest(prereg_path),
        },
        str(update_path): {
            "sha256": digest(update_path),
        },
        str(orientation_path): {
            "sha256": digest(orientation_path),
        },
    },
    "presentation_rows": presentation_rows,
    "orientation_reversal": {
        "bridge_count": orientation_bridge_count,
        "reversal_verified": orientation_reversal_verified,
        "reversal_rows": reversal_rows,
    },
    "preregistration_comparison": {
        "check_count": len(checks),
        "failed_check_count": len(failed),
        "failed_checks": failed,
        "prediction_matches": audit_pass,
    },
    "classification": classification,
    "earned_statement_candidate": (
        "In both selected local D8 presentations, inversion is "
        "involutive, fixes six elements, exchanges the two order-four "
        "elements, has nonzero ordinary homomorphism failures, has zero "
        "anti-homomorphism failures, and is absent from Aut(D8). "
        "It carries right multiplication to left multiplication by the "
        "inverse instruction. Together with the locked 011o reversal, "
        "this identifies orientation reversal as an opposite-law "
        "variance candidate rather than a local Aut(D8) character."
    ),
    "boundary": {
        "instruction_selected": False,
        "chart_orbit_selected": False,
        "orientation_selected": False,
        "three_torsors_identified": False,
        "autonomous_native_update_law_constructed": False,
        "mechanics_state_cell_established": False,
        "manuscript_mutated": False,
        "physical_claim": False,
    },
    "audit_pass_candidate": audit_pass,
    "repository_mutation_performed": False,
}

json_output.write_text(
    json.dumps(candidate, indent=2, sort_keys=True) + "\n"
)

print("== G60 LOCAL D8 INVERSION VARIANCE CENSUS 012e ==")
print("PACKET:", candidate["packet"])
print("MODE:", candidate["mode"])
print("LOCKED_HEAD:", head)
for row in presentation_rows:
    print(
        "PRESENTATION_ROW:",
        json.dumps(row, sort_keys=True),
    )
print("ORIENTATION_BRIDGE_COUNT:", orientation_bridge_count)
print("ORIENTATION_REVERSAL_VERIFIED:",
      str(orientation_reversal_verified).lower())
print("CHECK_COUNT:", len(checks))
print("FAILED_CHECK_COUNT:", len(failed))
print("PREDICTION_MATCHES:", str(audit_pass).lower())
print("CLASSIFICATION:", classification)
print("FAILED_CHECKS:", failed)
print("EARNED_STATEMENT_CANDIDATE:",
      candidate["earned_statement_candidate"])
print("INSTRUCTION_SELECTED: false")
print("CHART_ORBIT_SELECTED: false")
print("ORIENTATION_SELECTED: false")
print("MECHANICS_STATE_CELL_ESTABLISHED: false")
print("MANUSCRIPT_MUTATED: false")
print("PHYSICAL_CLAIM: false")
print("PROJECT_MUTATION_PERFORMED: false")

if failed:
    raise SystemExit(1)
