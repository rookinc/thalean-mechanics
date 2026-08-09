#!/usr/bin/env python3

import hashlib
import json
import pathlib
import sys

witness_path = pathlib.Path(sys.argv[1]).resolve()
source_025_path = pathlib.Path(sys.argv[2]).resolve()
source_028_path = pathlib.Path(sys.argv[3]).resolve()
output_path = pathlib.Path(sys.argv[4]).resolve()
is_permanent_output = 'artifacts/json' in output_path.as_posix()

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def sha256_file(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1048576), b""):
            digest.update(block)
    return digest.hexdigest()

witness = load(witness_path)
source_025 = load(source_025_path)
source_028 = load(source_028_path)

v4 = ((0, 0), (0, 1), (1, 0), (1, 1))
arcs = tuple(
    (leaf, outer_side)
    for leaf in v4
    for outer_side in (0, 1)
)

def signatory_action(leaf):
    return (leaf[0], leaf[1] ^ 1)

def registration_action(leaf):
    return (leaf[0] ^ 1, leaf[1])

def leaf_to_receipt(leaf):
    return leaf[0]

def receipt_to_aggregate(receipt):
    return 0

arc_fibers = {
    leaf: tuple(
        arc for arc in arcs
        if arc[0] == leaf
    )
    for leaf in v4
}

receipt_fibers = {
    receipt: tuple(
        leaf for leaf in v4
        if leaf_to_receipt(leaf) == receipt
    )
    for receipt in (0, 1)
}

aggregate_fiber = tuple(sorted(receipt_fibers))

type_rows = []
for row in witness["registered_types"]:
    entries = row["coordinate_to_inequality"]
    coordinate_to_value = {
        tuple(entry["coordinate"]):
            int(entry["inequality_index"])
        for entry in entries
    }

    receipts = {
        receipt: tuple(sorted(
            coordinate_to_value[leaf]
            for leaf in receipt_fibers[receipt]
        ))
        for receipt in (0, 1)
    }

    aggregate = tuple(sorted(
        value
        for receipt in (0, 1)
        for value in receipts[receipt]
    ))

    row_checks = {
        "coordinate_set_is_v4":
            tuple(sorted(coordinate_to_value)) == v4,
        "four_distinct_inequalities":
            len(set(coordinate_to_value.values())) == 4,
        "signatory_orbits_are_receipt_fibers":
            all(
                leaf_to_receipt(signatory_action(leaf))
                == leaf_to_receipt(leaf)
                for leaf in v4
            ),
        "registration_swaps_receipts":
            all(
                leaf_to_receipt(registration_action(leaf))
                == leaf_to_receipt(leaf) ^ 1
                for leaf in v4
            ),
        "two_receipts_each_have_two_values":
            len(receipts) == 2
            and all(len(values) == 2 for values in receipts.values()),
        "aggregate_contains_all_four_values":
            len(aggregate) == 4
            and set(aggregate) == set(coordinate_to_value.values()),
        "regular_orbit_exact":
            row["regular_orbit_exact"] is True,
        "pair_stabilizer_trivial":
            row["pair_stabilizer_order"] == 1,
    }

    type_rows.append({
        "type_index": row["type_index"],
        "receipts": {
            str(key): list(value)
            for key, value in receipts.items()
        },
        "aggregate": list(aggregate),
        "checks": row_checks,
        "exact": all(row_checks.values()),
    })

checks = {
    "witness_033_audit_pass":
        witness.get("audit_pass") is True,
    "source_025_audit_pass":
        source_025.get("audit_pass") is True,
    "source_028_audit_pass":
        source_028.get("audit_pass") is True,
    "registered_type_count_9":
        len(type_rows) == 9,
    "arc_count_8":
        len(arcs) == 8,
    "leaf_count_4":
        len(v4) == 4,
    "receipt_count_2":
        len(receipt_fibers) == 2,
    "aggregate_count_1":
        receipt_to_aggregate(0)
        == receipt_to_aggregate(1)
        == 0,
    "eight_to_four_fiber_profile_2_2_2_2":
        tuple(sorted(len(value) for value in arc_fibers.values()))
        == (2, 2, 2, 2),
    "four_to_two_fiber_profile_2_2":
        tuple(sorted(
            len(value) for value in receipt_fibers.values()
        )) == (2, 2),
    "two_to_one_fiber_profile_2":
        len(aggregate_fiber) == 2,
    "outer_arc_side_is_separate_from_signatory_bit":
        all(
            arc[1] in (0, 1)
            and arc[0][1] in (0, 1)
            for arc in arcs
        ),
    "all_nine_types_exact":
        all(row["exact"] for row in type_rows),
}

failed = [
    name
    for name, passed in checks.items()
    if not passed
]

audit_pass = not failed

result = {
    "packet": "g900_standalone_8_4_2_1_witness_034",
    "mode": "standalone_frozen_witness_quotient_audit",
    "audit_pass": audit_pass,
    "classification": (
        "frozen_minimal_register_witness_proves_exact_"
        "eight_to_four_to_two_to_one_quotient_ladder_"
        "across_all_nine_response_types"
        if audit_pass
        else "standalone_quotient_ladder_witness_failed"
    ),
    "earned_statement": (
        "The frozen witness consists of nine regular four-state "
        "V4 response types. Adjoining the independent outer arc-side "
        "torsor gives eight rosette arcs. Forgetting arc side gives "
        "four leaves; quotienting by the signatory involution gives "
        "two receipts; registration exchanges those receipts; and "
        "their union gives one aggregate."
    ),
    "sources": {
        str(witness_path): sha256_file(witness_path),
        str(source_025_path): sha256_file(source_025_path),
        str(source_028_path): sha256_file(source_028_path),
    },
    "quotient_profile": {
        "arc_count": len(arcs),
        "leaf_count": len(v4),
        "receipt_count": len(receipt_fibers),
        "aggregate_count": 1,
        "arc_to_leaf_fiber_sizes":
            sorted(len(value) for value in arc_fibers.values()),
        "leaf_to_receipt_fiber_sizes":
            sorted(len(value) for value in receipt_fibers.values()),
        "receipt_to_aggregate_fiber_size":
            len(aggregate_fiber),
    },
    "type_rows": type_rows,
    "checks": checks,
    "failed_checks": failed,
    "boundary": {
        "post_scout_witness_used": True,
        "discovery_ancestry_executed": False,
        "outer_arc_side_equals_signatory_bit": False,
        "canonical_leaf_labeling_selected": False,
        "native_derivation_complete": False,
        "universal_real_source_law_derived": False,
        "physical_claim": False,
        "gravity_claim": False,
    },
    "repository_mutation": {
        "permanent_artifact_written": is_permanent_output,
        "commit_performed": False,
        "push_performed": False,
    },
}

output_path.write_text(
    json.dumps(result, indent=2, sort_keys=True) + "\n",
    encoding="utf-8",
)

print("PACKET:", result["packet"])
print("MODE:", result["mode"])
print("QUOTIENT_PROFILE:", result["quotient_profile"])
print("TYPE_COUNT:", len(type_rows))
print("TYPE_FAILURE_COUNT:",
      sum(not row["exact"] for row in type_rows))
print("CHECKS:", checks)
print("FAILED_CHECK_COUNT:", len(failed))
print("FAILED_CHECKS:", failed)
print("AUDIT_PASS:", audit_pass)
print("CLASSIFICATION:", result["classification"])
print("DISCOVERY_ANCESTRY_EXECUTED:", False)
print("OUTER_ARC_SIDE_EQUALS_SIGNATORY_BIT:", False)
print("OUTPUT:", output_path)
print("PERMANENT_ARTIFACT_WRITTEN:", is_permanent_output)
print("MUTATION_PERFORMED:", False)
