#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from collections import Counter
from pathlib import Path


TARGET = (
    Path.home()
    / "dev/cori/research/thalean_mechanics/papers"
    / "08-g60-receipt-packet-native-encounter"
)

RECEIPT = (
    TARGET
    / "artifacts/receipts"
    / "g60_native_semiregular_receipt_action_census_002_mac.txt"
)

EXPECTED_SHA256 = (
    "9d0f1ef5975cd8cd2575192012c8bfeefe15c2856d6646e827ffc4ada851f383"
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_status(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(root), "status", "--short"],
        check=True,
        capture_output=True,
        text=True,
    )
    return [line for line in result.stdout.splitlines() if line]


def scalar(text: str, name: str) -> int:
    match = re.search(rf"^{re.escape(name)}:\s*(\d+)\s*$", text, re.MULTILINE)
    if not match:
        raise RuntimeError(f"missing scalar: {name}")
    return int(match.group(1))


status_before = git_status(TARGET)

print("OUT ==")
print("PACKET: g60_blind_receipt_action_adjudication_003")
print("MODE: read-only blind outcome adjudication")
print(f"TARGET: {TARGET}")
print("REPOSITORY_MUTATION: none")
print()

print("== LOCKED BLIND RECEIPT ==")
receipt_exists = RECEIPT.is_file()
receipt_sha256 = sha256(RECEIPT) if receipt_exists else None
receipt_bytes = RECEIPT.stat().st_size if receipt_exists else 0

print(f"RECEIPT_EXISTS: {str(receipt_exists).lower()}")
print(f"RECEIPT_SHA256: {receipt_sha256}")
print(f"RECEIPT_BYTES: {receipt_bytes}")
print(
    "CHECK_BLIND_RECEIPT_HASH_LOCKED:",
    str(receipt_sha256 == EXPECTED_SHA256).lower(),
)

if receipt_sha256 != EXPECTED_SHA256:
    raise RuntimeError("blind receipt hash mismatch")

text = RECEIPT.read_text(encoding="utf-8")

classes = []
for line in text.splitlines():
    prefix = "RECEIPT_ACTION_CLASS: "
    if line.startswith(prefix):
        classes.append(json.loads(line[len(prefix):]))

semiregular_subgroup_count = scalar(text, "SEMIREGULAR_SUBGROUP_COUNT")
conjugacy_class_count = scalar(
    text,
    "SEMIREGULAR_SUBGROUP_CONJUGACY_CLASS_COUNT",
)
cover_admissible_class_count = scalar(
    text,
    "COVER_ADMISSIBLE_CLASS_COUNT",
)
edge_inverting_class_count = scalar(
    text,
    "EDGE_INVERTING_CLASS_COUNT",
)

print()
print("== PREDECLARED OUTCOME RULE ==")
print("OUTCOME_RULE_NONE: class_count == 0")
print("OUTCOME_RULE_UNIQUE: class_count == 1")
print("OUTCOME_RULE_MULTIPLE: class_count > 1")

if conjugacy_class_count == 0:
    blind_outcome = "none"
elif conjugacy_class_count == 1:
    blind_outcome = "unique"
else:
    blind_outcome = "multiple"

print(f"BLIND_OUTCOME: {blind_outcome}")

class_ids = [row["class_index"] for row in classes]
group_order_counts = Counter(row["group_order"] for row in classes)
group_label_counts = Counter(row["group_label"] for row in classes)
conjugate_subgroup_total = sum(
    row["conjugate_subgroup_count"] for row in classes
)

print()
print("== BLIND CENSUS ADJUDICATION ==")
print(f"SEMIREGULAR_SUBGROUP_COUNT: {semiregular_subgroup_count}")
print(f"PARSED_CLASS_COUNT: {len(classes)}")
print(f"DECLARED_CLASS_COUNT: {conjugacy_class_count}")
print(f"CONJUGATE_SUBGROUP_TOTAL: {conjugate_subgroup_total}")
print(
    "GROUP_ORDER_CLASS_COUNTS:",
    json.dumps(dict(sorted(group_order_counts.items())), sort_keys=True),
)
print(
    "GROUP_LABEL_CLASS_COUNTS:",
    json.dumps(dict(sorted(group_label_counts.items())), sort_keys=True),
)
print(f"COVER_ADMISSIBLE_CLASS_COUNT: {cover_admissible_class_count}")
print(f"EDGE_INVERTING_CLASS_COUNT: {edge_inverting_class_count}")

normal_classes = [
    row for row in classes
    if row["conjugate_subgroup_count"] == 1
]

print()
print("== FULL-AUTOMORPHISM NORMAL CLASSES ==")
print(f"NORMAL_CLASS_COUNT: {len(normal_classes)}")

for row in normal_classes:
    print(
        "NORMAL_CLASS:",
        json.dumps(
            {
                "class_index": row["class_index"],
                "group_label": row["group_label"],
                "group_order": row["group_order"],
                "generator_indices": row["generator_indices"],
                "element_order_profile": row["element_order_profile"],
                "vertex_orbit_count": row["vertex_orbit_count"],
                "edge_orbit_count": row["edge_orbit_count"],
                "cover_admissible": row["cover_admissible"],
            },
            sort_keys=True,
            separators=(",", ":"),
        ),
    )

binary_classes = [
    row for row in classes
    if row["group_order"] == 2 and row["group_label"] == "C2"
]

normal_binary_classes = [
    row for row in binary_classes
    if row["conjugate_subgroup_count"] == 1
]

print()
print("== BLIND BINARY SUBSPECTRUM ==")
print(f"BINARY_CLASS_COUNT: {len(binary_classes)}")

for row in binary_classes:
    print(
        "BINARY_CLASS:",
        json.dumps(
            {
                "class_index": row["class_index"],
                "conjugate_subgroup_count": row["conjugate_subgroup_count"],
                "generator_indices": row["generator_indices"],
                "fiber_preview": row["fiber_preview"],
                "cover_admissible": row["cover_admissible"],
            },
            sort_keys=True,
            separators=(",", ":"),
        ),
    )

print(f"NORMAL_BINARY_CLASS_COUNT: {len(normal_binary_classes)}")

if len(normal_binary_classes) == 1:
    normal_binary = normal_binary_classes[0]
    print(f"NORMAL_BINARY_CLASS_INDEX: {normal_binary['class_index']}")
    print(
        "NORMAL_BINARY_GENERATOR_INDICES:",
        normal_binary["generator_indices"],
    )

checks = {
    "blind_receipt_hash_locked": receipt_sha256 == EXPECTED_SHA256,
    "blind_outcome_is_multiple": blind_outcome == "multiple",
    "parsed_22_classes": len(classes) == 22,
    "declared_22_classes": conjugacy_class_count == 22,
    "class_indices_exact": class_ids == list(range(1, 23)),
    "subgroup_total_198": semiregular_subgroup_count == 198,
    "class_orbits_sum_to_198": conjugate_subgroup_total == 198,
    "all_classes_cover_admissible": (
        cover_admissible_class_count == 22
        and all(row["cover_admissible"] for row in classes)
    ),
    "no_edge_inverting_classes": (
        edge_inverting_class_count == 0
        and all(not row["edge_inversion"] for row in classes)
    ),
    "three_binary_classes": len(binary_classes) == 3,
    "binary_conjugacy_orbit_sizes_are_1_2_15": sorted(
        row["conjugate_subgroup_count"] for row in binary_classes
    ) == [1, 2, 15],
    "unique_normal_binary_class": len(normal_binary_classes) == 1,
    "normal_binary_is_class22": (
        len(normal_binary_classes) == 1
        and normal_binary_classes[0]["class_index"] == 22
    ),
}

print()
print("== ADJUDICATION CHECKS ==")
for key, value in checks.items():
    print(f"CHECK_{key.upper()}: {str(value).lower()}")

failed_checks = [key for key, value in checks.items() if not value]
print(f"FAILED_CHECKS: {json.dumps(failed_checks)}")

status_after = git_status(TARGET)
status_preserved = status_before == status_after

print()
print("== STATUS PRESERVATION ==")
print(
    "STATUS_CHECK:",
    json.dumps(
        {
            "before": status_before,
            "after": status_after,
            "preserved": status_preserved,
        },
        sort_keys=True,
        separators=(",", ":"),
    ),
)
print(
    "CHECK_REPOSITORY_STATUS_PRESERVED:",
    str(status_preserved).lower(),
)

if failed_checks or not status_preserved:
    raise RuntimeError("blind adjudication failed")

print()
print(
    "FINAL_CLASSIFICATION:",
    "blind_native_G60_receipt_action_outcome_is_multiple_"
    "with_one_full_automorphism_normal_binary_class",
)
print(
    "BOUNDARY:",
    "The locked blind census supplies 22 cover-admissible action classes. "
    "It does not uniquely select a receipt action. Within the binary "
    "subspectrum, exactly one C2 subgroup is normal under the full native "
    "automorphism group. Calling that class the historical G60 deck action "
    "requires a later unblinding comparison. Binary receipt and full-"
    "automorphism invariance have not been imported as retrospective "
    "selection premises."
)
print(
    "NEXT_GATE:",
    "Freeze this blind adjudication, then compare its unique normal C2 "
    "class with the independently preserved G60-to-G30 deck involution."
)
print(
    "KEEPER:",
    "The blind answer is many. Inside the binary answers, symmetry leaves "
    "one standing still."
)
print("MUTATION_PERFORMED: false")
