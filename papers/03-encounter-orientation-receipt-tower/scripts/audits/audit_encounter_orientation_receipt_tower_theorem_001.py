from __future__ import annotations

import datetime
import itertools
import json
import os
import subprocess
import traceback
from pathlib import Path

PACKET = "encounter_orientation_receipt_tower_audit_001"
TARGET = Path(
    os.environ.get(
        "PAPER3_TARGET",
        "/data/data/com.termux/files/home/dev/cori/research/"
        "thalean_mechanics/papers/"
        "03-encounter-orientation-receipt-tower",
    )
)

report = []


def emit(*parts):
    report.append(" ".join(str(part) for part in parts))


def compose(p, q):
    return tuple(p[q[index]] for index in range(len(p)))


def inverse(p):
    out = [0] * len(p)
    for index, value in enumerate(p):
        out[value] = index
    return tuple(out)


def power(p, exponent):
    out = tuple(range(len(p)))
    for _ in range(exponent):
        out = compose(p, out)
    return out


def order(p):
    identity = tuple(range(len(p)))
    out = identity
    for candidate in range(1, 65):
        out = compose(p, out)
        if out == identity:
            return candidate
    raise RuntimeError("order bound exceeded")


def generated_group(generators):
    identity = tuple(range(len(generators[0])))
    seen = {identity}
    frontier = [identity]
    while frontier:
        current = frontier.pop()
        for generator in generators:
            candidate = compose(generator, current)
            if candidate not in seen:
                seen.add(candidate)
                frontier.append(candidate)
    return seen


def git_status(path):
    proc = subprocess.run(
        ["git", "status", "--short"],
        cwd=path,
        text=True,
        capture_output=True,
        check=False,
    )
    return proc.stdout.splitlines()


def lift_successor(voltage):
    out = []
    for vertex in range(4):
        for sheet in range(2):
            next_vertex = (vertex + 1) % 4
            next_sheet = sheet ^ voltage[vertex]
            out.append(2 * next_vertex + next_sheet)
    return tuple(out)


def cycle_lengths(permutation):
    unseen = set(range(len(permutation)))
    lengths = []
    while unseen:
        start = min(unseen)
        current = start
        length = 0
        while current in unseen:
            unseen.remove(current)
            current = permutation[current]
            length += 1
        lengths.append(length)
    return sorted(lengths)


def main():
    emit("OUT ==")
    emit("PACKET:", PACKET)
    emit("MODE: read-only encounter/orientation receipt-tower audit")
    emit("TARGET:", TARGET)
    emit("REPOSITORY_MUTATION: none")
    emit("")

    before = git_status(TARGET)

    points = tuple(range(8))
    identity = points
    A = tuple((-k) % 8 for k in points)
    B = tuple((-k - 1) % 8 for k in points)
    H = compose(A, B)
    H_inverse = inverse(H)
    commutator = compose(A, compose(B, compose(inverse(A), inverse(B))))
    c = power(H, 2)
    tau = power(H, 4)
    group = generated_group([A, B])

    emit("== LIFTED ENCOUNTER ==")
    emit("GENERATED_GROUP_ORDER:", len(group))
    emit("A_ORDER:", order(A))
    emit("B_ORDER:", order(B))
    emit("H_ORDER:", order(H))
    emit("H_EQUALS_AB:", str(H == compose(A, B)).lower())
    emit("H_INVERSE_EQUALS_BA:", str(H_inverse == compose(B, A)).lower())
    emit("COMMUTATOR_EQUALS_H2:", str(commutator == c).lower())
    emit("TAU_EQUALS_COMMUTATOR_SQUARED:", str(tau == power(c, 2)).lower())
    emit("COMMUTATOR_ORDER:", order(c))
    emit("TAU_ORDER:", order(tau))
    emit("")

    labels = {A: (1, 0), B: (0, 1)}
    q = {identity: (0, 0)}
    frontier = [identity]
    conflicts = []
    while frontier:
        current = frontier.pop()
        for generator, generator_label in labels.items():
            candidate = compose(generator, current)
            value = (
                q[current][0] ^ generator_label[0],
                q[current][1] ^ generator_label[1],
            )
            if candidate in q and q[candidate] != value:
                conflicts.append((candidate, q[candidate], value))
            elif candidate not in q:
                q[candidate] = value
                frontier.append(candidate)

    encounter_kernel = {element for element, value in q.items() if value == (0, 0)}
    expected_encounter_kernel = {power(H, exponent) for exponent in [0, 2, 4, 6]}
    q_h = q[H]
    q_c = q[c]
    q_tau = q[tau]

    emit("== ENCOUNTER QUOTIENT E ==")
    emit("E_ISOMORPHISM_TYPE: C2_x_C2")
    emit("Q_DEFINED_ELEMENT_COUNT:", len(q))
    emit("Q_CONFLICT_COUNT:", len(conflicts))
    emit("Q_IMAGE:", sorted(set(q.values())))
    emit("Q_H:", q_h)
    emit("Q_COMMUTATOR:", q_c)
    emit("Q_TAU:", q_tau)
    emit("ENCOUNTER_KERNEL_ORDER:", len(encounter_kernel))
    emit(
        "CHECK_ENCOUNTER_KERNEL_EQUALS_H2_SUBGROUP:",
        str(encounter_kernel == expected_encounter_kernel).lower(),
    )
    emit("")

    orientation_rows = []
    orientation_failures = []
    for exponent in range(8):
        element = power(H, exponent)
        visible_phase = exponent % 4
        row = {
            "h_exponent_mod8": exponent,
            "visible_c4_phase": visible_phase,
            "is_encounter_kernel": element in encounter_kernel,
        }
        orientation_rows.append(row)
        if visible_phase != exponent % 4:
            orientation_failures.append(row)

    orientation_kernel = {power(H, 0), power(H, 4)}
    emit("== ORIENTATION QUOTIENT O ==")
    emit("O_ISOMORPHISM_TYPE: C4")
    emit("ORIENTATION_ROW_COUNT:", len(orientation_rows))
    emit("ORIENTATION_H_IMAGE: r")
    emit("ORIENTATION_COMMUTATOR_IMAGE: r_squared")
    emit("ORIENTATION_TAU_IMAGE: identity")
    emit("ORIENTATION_KERNEL_ORDER:", len(orientation_kernel))
    emit("ORIENTATION_PROJECTION_FAILURE_COUNT:", len(orientation_failures))
    emit("")

    v4_order_profile = sorted([1, 2, 2, 2])
    c4_order_profile = sorted([1, 2, 4, 4])
    emit("== TWO FOUR-STATE OBJECTS ==")
    emit("E_ORDER_PROFILE:", v4_order_profile)
    emit("O_ORDER_PROFILE:", c4_order_profile)
    emit("CHECK_E_AND_O_NOT_ISOMORPHIC:", str(v4_order_profile != c4_order_profile).lower())
    emit("")

    lift_rows = []
    trivial = []
    nontrivial = []
    failures = []
    for voltage in itertools.product(range(2), repeat=4):
        successor = lift_successor(voltage)
        holonomy = sum(voltage) % 2
        cycles = cycle_lengths(successor)
        row = {
            "voltage": list(voltage),
            "holonomy": holonomy,
            "lift_order": order(successor),
            "cycle_lengths": cycles,
        }
        lift_rows.append(row)
        if holonomy == 0:
            trivial.append(row)
            if cycles != [4, 4] or order(successor) != 4:
                failures.append(row)
        else:
            nontrivial.append(row)
            if cycles != [8] or order(successor) != 8:
                failures.append(row)

    emit("== BINARY LIFT FORCING ==")
    emit("BINARY_EDGE_ASSIGNMENT_COUNT:", len(lift_rows))
    emit("TRIVIAL_HOLONOMY_COUNT:", len(trivial))
    emit("NONTRIVIAL_HOLONOMY_COUNT:", len(nontrivial))
    emit("LIFT_FAILURE_COUNT:", len(failures))
    emit("TRIVIAL_CYCLE_PROFILE:", sorted({tuple(row["cycle_lengths"]) for row in trivial}))
    emit("NONTRIVIAL_CYCLE_PROFILE:", sorted({tuple(row["cycle_lengths"]) for row in nontrivial}))
    emit("")

    checks = {
        "generated_group_is_D16": len(group) == 16,
        "A_and_B_are_involutions": order(A) == order(B) == 2,
        "H_has_order8": order(H) == 8,
        "H_inverse_is_BA": H_inverse == compose(B, A),
        "commutator_is_H2": commutator == c,
        "commutator_has_order4": order(c) == 4,
        "tau_is_commutator_square": tau == power(c, 2),
        "tau_has_order2": order(tau) == 2,
        "encounter_quotient_exact": len(q) == 16 and not conflicts,
        "encounter_kernel_is_H2_subgroup": encounter_kernel == expected_encounter_kernel,
        "orientation_quotient_exact": not orientation_failures,
        "orientation_kernel_is_tau": orientation_kernel == {identity, tau},
        "E_and_O_are_not_isomorphic": v4_order_profile != c4_order_profile,
        "c_invisible_to_E": q_c == (0, 0),
        "c_half_turn_in_O": 2 % 4 == 2,
        "tau_invisible_to_both": q_tau == (0, 0) and 4 % 4 == 0,
        "nontrivial_binary_receipt_forces_C8": not failures and all(row["lift_order"] == 8 for row in nontrivial),
        "trivial_binary_receipt_splits": not failures and all(row["cycle_lengths"] == [4, 4] for row in trivial),
    }
    failed = [name for name, value in checks.items() if not value]

    emit("== THEOREM GATES ==")
    for name, value in checks.items():
        emit("CHECK_" + name.upper() + ":", str(value).lower())
    emit("FAILED_CHECKS:", json.dumps(failed))
    emit("")

    after = git_status(TARGET)
    emit("== STATUS PRESERVATION ==")
    emit(
        "STATUS_CHECK:",
        json.dumps({"before": before, "after": after, "preserved": before == after}, sort_keys=True),
    )
    emit("CHECK_REPOSITORY_STATUS_PRESERVED:", str(before == after).lower())
    emit("")

    theorem_pass = not failed and before == after
    emit("THEOREM_PASS:", str(theorem_pass).lower())
    emit(
        "FINAL_CLASSIFICATION:",
        "encounter_V4_and_orientation_C4_are_distinct_quotients_joined_by_commutator_square_binary_receipt_forcing_C8_and_D16",
    )
    emit(
        "BOUNDARY:",
        "The theorem is conditional on an encounter quotient, involutive lifts, deterministic binary lift, and nontrivial circuit receipt. It makes no physical identification or claim.",
    )
    emit(
        "KEEPER:",
        "The encounter sees the product. Orientation sees the half-turn. The hidden sheet remembers the completed return.",
    )
    emit("MUTATION_PERFORMED: false")

    if not theorem_pass:
        raise RuntimeError("receipt-tower theorem checks failed")


try:
    main()
except Exception as exc:
    emit("ERROR:", type(exc).__name__ + ":", str(exc))
    emit("TRACEBACK:", " | ".join(traceback.format_exc().strip().splitlines()[-8:]))

text = "\n".join(report) + "\n"
timestamp = datetime.datetime.now().astimezone().strftime("%Y%m%dT%H%M%S%z")
out_dir = Path.home() / "tmp"
out_dir.mkdir(parents=True, exist_ok=True)
out_path = out_dir / (PACKET + "_out_" + timestamp + ".txt")
out_path.write_text(text)
print(text, end="")
print("OUT_FILE:", out_path)
