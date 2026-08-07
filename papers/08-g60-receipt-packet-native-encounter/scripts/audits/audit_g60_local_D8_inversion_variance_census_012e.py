#!/usr/bin/env python3
import gc
import hashlib
import json
import pathlib
import subprocess
import sys

root = pathlib.Path(sys.argv[1]).resolve()
candidate_script = pathlib.Path(sys.argv[2]).resolve()
candidate_json = pathlib.Path(sys.argv[3]).resolve()
candidate_report = pathlib.Path(sys.argv[4]).resolve()

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

checks = []

def check(name, passed):
    checks.append((name, bool(passed)))

head = subprocess.check_output(
    ["git", "--no-pager", "show", "-s", "--format=%h %s", "HEAD"],
    cwd=root,
    text=True,
).strip()

check(
    "head",
    head == "cb7c2db Preregister G60 local D8 inversion variance",
)
check(
    "candidate_script_hash",
    digest(candidate_script)
    == "866c593453fa5a9c44867c45a238c9b4d5c967c6343e1c5cf8cb195fd1aac982",
)
check(
    "candidate_json_hash",
    digest(candidate_json)
    == "a42aed2a1b56144285fd0b2e575a7f932eb7de93b636e49b55cb9a7bd498328a",
)
check(
    "candidate_report_hash",
    digest(candidate_report)
    == "c70eebf5bc394c1122a0398dd517a316dea5143222e4288a719034b1ca0b56db",
)
check(
    "update_hash",
    digest(update_path)
    == "4e6936b9b48c6f033b826df7c3ad4ac70ec3480129c5c73ec6a24630077096d2",
)
check(
    "orientation_hash",
    digest(orientation_path)
    == "ad684db8bb65c5eb731c972d33e685ffc18a947f63c9ba4e9758f815821f0941",
)
check(
    "prereg_hash",
    digest(prereg_path)
    == "16ece0c496bfa2021e60e3c36df523825efbd8db13bcc6b0871fd903da6c50aa",
)

candidate = load(candidate_json)
update_full = load(update_path)
source_rows = update_full["local_reconstruction"]["presentation_rows"]
del update_full
gc.collect()

measured_rows = []

for p, source in enumerate(source_rows):
    table = [
        [int(value) for value in row]
        for row in source["multiplication_table"]
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
    unique = True
    for x in range(size):
        matches = [
            y for y in range(size)
            if table[x][y] == identity
            and table[y][x] == identity
        ]
        unique = unique and len(matches) == 1
        inverse.append(matches[0] if len(matches) == 1 else None)

    noncommuting = sum(
        table[x][y] != table[y][x]
        for x in range(size)
        for y in range(size)
    )
    ordinary = sum(
        inverse[table[x][y]]
        != table[inverse[x]][inverse[y]]
        for x in range(size)
        for y in range(size)
    )
    anti = sum(
        inverse[table[x][y]]
        != table[inverse[y]][inverse[x]]
        for x in range(size)
        for y in range(size)
    )

    automorphisms = [
        [int(value) for value in row["mapping"]]
        for row in source["automorphism_rows"]
    ]

    measured_rows.append({
        "presentation_index": p,
        "identity_indices": identities,
        "inverse_permutation": inverse,
        "inverse_unique": unique,
        "noncommuting_pair_count": noncommuting,
        "ordinary_failure_count": ordinary,
        "anti_failure_count": anti,
        "fixed_points": [
            x for x in range(size) if inverse[x] == x
        ],
        "order_four_elements": [
            int(x) for x in source["order_four_elements"]
        ],
        "inversion_in_Aut_D8": inverse in automorphisms,
        "double_inversion_failure_count": sum(
            inverse[inverse[x]] != x for x in range(size)
        ),
    })

del source_rows
gc.collect()

candidate_rows = {
    int(row["presentation_index"]): row
    for row in candidate["presentation_rows"]
}

for measured in measured_rows:
    p = measured["presentation_index"]
    row = candidate_rows[p]
    prefix = "p" + str(p) + "_"

    check(prefix + "identity",
          measured["identity_indices"] == [0])
    check(prefix + "inverse_unique",
          measured["inverse_unique"] is True)
    check(prefix + "inverse_permutation",
          measured["inverse_permutation"]
          == [0, 1, 3, 2, 4, 5, 6, 7])
    check(prefix + "fixed_points",
          measured["fixed_points"] == [0, 1, 4, 5, 6, 7])
    check(prefix + "order_four",
          measured["order_four_elements"] == [2, 3])
    check(prefix + "not_in_Aut_D8",
          measured["inversion_in_Aut_D8"] is False)
    check(prefix + "noncommuting_24",
          measured["noncommuting_pair_count"] == 24)
    check(prefix + "ordinary_24",
          measured["ordinary_failure_count"] == 24)
    check(prefix + "anti_0",
          measured["anti_failure_count"] == 0)
    check(prefix + "double_inversion_0",
          measured["double_inversion_failure_count"] == 0)

    check(prefix + "candidate_identity",
          row["identity_indices"] == measured["identity_indices"])
    check(prefix + "candidate_inverse",
          row["inverse_permutation"]
          == measured["inverse_permutation"])
    check(prefix + "candidate_fixed_points",
          row["inversion_fixed_points"]
          == measured["fixed_points"])
    check(prefix + "candidate_order_four",
          row["order_four_elements"] == [2, 3]
          and row["order_four_inverse_images"] == [3, 2])
    check(prefix + "candidate_noncommuting",
          row["noncommuting_pair_count"]
          == measured["noncommuting_pair_count"])
    check(prefix + "candidate_ordinary",
          row["ordinary_homomorphism_failure_count"]
          == measured["ordinary_failure_count"])
    check(prefix + "candidate_anti",
          row["anti_homomorphism_failure_count"]
          == measured["anti_failure_count"])
    check(prefix + "candidate_not_Aut",
          row["inversion_matches_automorphism_indices"] == [])
    check(prefix + "candidate_right_to_left",
          row["right_update_to_left_inverse_failure_count"]
          == measured["anti_failure_count"])
    check(prefix + "candidate_right_to_right",
          row["right_update_to_right_inverse_failure_count"]
          == measured["ordinary_failure_count"])
    check(prefix + "candidate_double",
          row["double_inversion_failure_count"]
          == measured["double_inversion_failure_count"])

orientation_full = load(orientation_path)
bridge = orientation_full["bridge_census"]
reversal_rows = sorted(
    bridge["reversal_rows"],
    key=lambda row: int(row["map_index"]),
)
del orientation_full
gc.collect()

check("orientation_bridge_count",
      bridge["alpha_1_bridge_count"] == 2)
check("orientation_reversal_verified",
      bridge["reversal_verified"] is True)
check(
    "sheet_reversal_swaps",
    [row["sheet_reversal_map_indices"] for row in reversal_rows]
    == [[1], [0]],
)
check(
    "root_inversion_swaps",
    [row["root_inversion_map_indices"] for row in reversal_rows]
    == [[1], [0]],
)
check(
    "sheet_equals_root",
    all(
        row["sheet_reversal_equals_root_inversion"]
        for row in reversal_rows
    ),
)

comparison = candidate["preregistration_comparison"]
check("candidate_check_count", comparison["check_count"] == 38)
check("candidate_failures_zero",
      comparison["failed_check_count"] == 0)
check("candidate_prediction_matches",
      comparison["prediction_matches"] is True)
check(
    "classification",
    candidate["classification"]
    == "local_D8_inversion_is_opposite_law_isomorphism_not_Aut_D8_character",
)
check("candidate_audit_pass",
      candidate["audit_pass_candidate"] is True)
check("candidate_no_mutation",
      candidate["repository_mutation_performed"] is False)
check(
    "all_boundaries_false",
    all(
        value is False
        for value in candidate["boundary"].values()
    ),
)

report_text = candidate_report.read_text()
markers = [
    "CHECK_COUNT: 38",
    "FAILED_CHECK_COUNT: 0",
    "PREDICTION_MATCHES: true",
    "CLASSIFICATION: local_D8_inversion_is_opposite_law_isomorphism_not_Aut_D8_character",
    "INSTRUCTION_SELECTED: false",
    "CHART_ORBIT_SELECTED: false",
    "ORIENTATION_SELECTED: false",
    "MECHANICS_STATE_CELL_ESTABLISHED: false",
    "MANUSCRIPT_MUTATED: false",
    "PHYSICAL_CLAIM: false",
    "PROJECT_MUTATION_PERFORMED: false",
]
for marker in markers:
    check("report_" + marker.split(":")[0],
          marker in report_text)

failed = [name for name, passed in checks if not passed]

print("== G60 LOCAL D8 INVERSION VARIANCE CENSUS GUARD 012e ==")
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
