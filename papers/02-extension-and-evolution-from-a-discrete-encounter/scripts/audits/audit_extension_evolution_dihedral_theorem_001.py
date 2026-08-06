from __future__ import annotations

import datetime
import itertools
import json
import os
import subprocess
import traceback
from pathlib import Path

PACKET = "extension_evolution_dihedral_realization_audit_001"
TARGET = Path(
    os.environ.get(
        "PAPER2_TARGET",
        "/data/data/com.termux/files/home/dev/cori/research/"
        "thalean_mechanics/papers/"
        "02-extension-and-evolution-from-a-discrete-encounter",
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


def add_v4(left, right):
    return (left[0] ^ right[0], left[1] ^ right[1])


def git_status(path):
    proc = subprocess.run(
        ["git", "status", "--short"],
        cwd=path,
        text=True,
        capture_output=True,
        check=False,
    )
    return proc.stdout.splitlines()


def main():
    emit("OUT ==")
    emit("PACKET:", PACKET)
    emit("MODE: read-only extension/evolution finite realization audit")
    emit("TARGET:", TARGET)
    emit("REPOSITORY_MUTATION: none")
    emit("")

    if not TARGET.exists():
        raise FileNotFoundError("missing target: " + str(TARGET))

    status_before = git_status(TARGET)

    points = tuple(range(8))
    identity = points

    # A and B are reflections. Composition is left after right.
    A = tuple((-point) % 8 for point in points)
    B = tuple((-point - 1) % 8 for point in points)
    H = compose(A, B)
    H_inverse = inverse(H)
    BA = compose(B, A)

    commutator = compose(
        compose(compose(A, B), inverse(A)),
        inverse(B),
    )

    group = generated_group([A, B])

    rotations = [power(H, exponent) for exponent in range(8)]
    reflected = [compose(A, power(H, exponent)) for exponent in range(8)]
    normal_forms = rotations + reflected

    emit("== FINITE DIHEDRAL REALIZATION ==")
    emit("POINT_COUNT:", len(points))
    emit("GENERATED_GROUP_ORDER:", len(group))
    emit("A_ORDER:", order(A))
    emit("B_ORDER:", order(B))
    emit("H_EQUALS_AB:", str(H == compose(A, B)).lower())
    emit("H_ORDER:", order(H))
    emit("H_INVERSE_EQUALS_BA:", str(H_inverse == BA).lower())
    emit(
        "COMMUTATOR_EQUALS_H_SQUARED:",
        str(commutator == power(H, 2)).lower(),
    )
    emit(
        "NORMAL_FORM_COUNT:",
        len(set(normal_forms)),
    )
    emit(
        "NORMAL_FORMS_EXHAUST_GROUP:",
        str(set(normal_forms) == group).lower(),
    )
    emit("")

    # q maps A to a=(1,0), B to b=(0,1), and H=AB to ab=(1,1).
    q = {}
    q_conflicts = []
    for exponent in range(8):
        rotation = power(H, exponent)
        rotation_value = (
            exponent % 2,
            exponent % 2,
        )
        if rotation in q and q[rotation] != rotation_value:
            q_conflicts.append(rotation)
        q[rotation] = rotation_value

        reflection = compose(A, rotation)
        reflection_value = add_v4((1, 0), rotation_value)
        if reflection in q and q[reflection] != reflection_value:
            q_conflicts.append(reflection)
        q[reflection] = reflection_value

    homomorphism_failures = []
    for left in group:
        for right in group:
            product = compose(left, right)
            if q[product] != add_v4(q[left], q[right]):
                homomorphism_failures.append((left, right))

    kernel = {element for element in group if q[element] == (0, 0)}
    expected_kernel = {
        identity,
        power(H, 2),
        power(H, 4),
        power(H, 6),
    }

    visible_values = sorted(set(q.values()))

    emit("== VISIBLE ENCOUNTER QUOTIENT ==")
    emit("VISIBLE_ALGEBRA:", "E={1,a,b,ab}=C2_x_C2")
    emit("Q_DEFINED_ELEMENT_COUNT:", len(q))
    emit("Q_CONFLICT_COUNT:", len(q_conflicts))
    emit("Q_IMAGE:", json.dumps(visible_values))
    emit("Q_SURJECTIVE:", str(len(visible_values) == 4).lower())
    emit("Q_HOMOMORPHISM_FAILURE_COUNT:", len(homomorphism_failures))
    emit("Q_A:", q[A])
    emit("Q_B:", q[B])
    emit("Q_AB:", q[compose(A, B)])
    emit("Q_BA:", q[compose(B, A)])
    emit(
        "CHECK_AB_BA_SAME_VISIBLE_IMAGE:",
        str(q[compose(A, B)] == q[compose(B, A)] == (1, 1)).lower(),
    )
    emit("KERNEL_ORDER:", len(kernel))
    emit(
        "KERNEL_EQUALS_H2_SUBGROUP:",
        str(kernel == expected_kernel).lower(),
    )
    emit("")

    extension_identity = compose(commutator, BA) == H

    emit("== EXTENSION AND EVOLUTION ==")
    emit("FORWARD_EVOLVER:", "H=AB")
    emit("REVERSE_EVOLVER:", "H_inverse=BA")
    emit("EXTENSION_RECEIPT:", "c=[A,B]=H^2")
    emit(
        "CHECK_AB_EQUALS_COMMUTATOR_TIMES_BA:",
        str(extension_identity).lower(),
    )
    emit(
        "CHECK_COMMUTATOR_IN_KERNEL:",
        str(commutator in kernel).lower(),
    )
    emit(
        "CHECK_COMMUTATOR_NONTRIVIAL:",
        str(commutator != identity).lower(),
    )
    emit(
        "CHECK_VISIBLE_QUOTIENT_FORGETS_ORDER:",
        str(q[H] == q[H_inverse]).lower(),
    )
    emit(
        "CHECK_LIFT_RETAINS_ORDER:",
        str(H != H_inverse).lower(),
    )
    emit("")

    orbit = [power(H, exponent)[0] for exponent in range(8)]
    orbit_unique = len(set(orbit)) == 8

    emit("== GENERATED GEOMETRY ==")
    emit("H_ORBIT_FROM_ZERO:", json.dumps(orbit))
    emit("H_ORBIT_SIZE:", len(set(orbit)))
    emit("CHECK_H_ORBIT_IS_C8:", str(orbit_unique).lower())
    emit(
        "CHECK_A_CONJUGATES_H_TO_INVERSE:",
        str(compose(compose(A, H), A) == H_inverse).lower(),
    )
    emit(
        "CHECK_B_CONJUGATES_H_TO_INVERSE:",
        str(compose(compose(B, H), B) == H_inverse).lower(),
    )
    emit("")

    # The evolver subgroup has its separate visible orientation quotient C8 -> C4.
    orientation_projection_failures = []
    for left_exp, right_exp in itertools.product(range(8), repeat=2):
        projected_sum = ((left_exp % 4) + (right_exp % 4)) % 4
        product_projection = (left_exp + right_exp) % 4
        if projected_sum != product_projection:
            orientation_projection_failures.append(
                (left_exp, right_exp)
            )

    orientation_kernel = [
        exponent for exponent in range(8) if exponent % 4 == 0
    ]

    emit("== CYCLIC RECEIPT SUBQUOTIENT ==")
    emit("EVOLVER_SUBGROUP_ORDER:", 8)
    emit("VISIBLE_ORIENTATION_ORDER:", 4)
    emit(
        "ORIENTATION_PROJECTION_FAILURE_COUNT:",
        len(orientation_projection_failures),
    )
    emit("ORIENTATION_KERNEL_EXPONENTS:", orientation_kernel)
    emit(
        "CHECK_VISIBLE_RETURN_AT_H4:",
        str(4 % 4 == 0 and power(H, 4) != identity).lower(),
    )
    emit("")

    checks = {
        "group_order_16": len(group) == 16,
        "A_involution": order(A) == 2,
        "B_involution": order(B) == 2,
        "H_order_8": order(H) == 8,
        "H_inverse_is_BA": H_inverse == BA,
        "commutator_is_H2": commutator == power(H, 2),
        "normal_forms_exact": set(normal_forms) == group,
        "q_conflict_free": not q_conflicts,
        "q_surjective": len(visible_values) == 4,
        "q_homomorphism": not homomorphism_failures,
        "AB_BA_same_visible": q[H] == q[H_inverse] == (1, 1),
        "kernel_is_H2_subgroup": kernel == expected_kernel,
        "extension_identity": extension_identity,
        "commutator_nontrivial_kernel": (
            commutator in kernel and commutator != identity
        ),
        "lift_retains_order": H != H_inverse,
        "orbit_is_C8": orbit_unique,
        "reversal_covariant": (
            compose(compose(A, H), A) == H_inverse
            and compose(compose(B, H), B) == H_inverse
        ),
        "C8_C4_projection_exact": not orientation_projection_failures,
        "C8_C4_kernel_is_C2": orientation_kernel == [0, 4],
    }

    failed = [name for name, value in checks.items() if not value]

    emit("== THEOREM GATES ==")
    for name, value in checks.items():
        emit("CHECK_" + name.upper() + ":", str(value).lower())
    emit("FAILED_CHECKS:", json.dumps(failed))
    emit("")

    status_after = git_status(TARGET)
    preserved = status_before == status_after

    emit("== STATUS PRESERVATION ==")
    emit(
        "STATUS_CHECK:",
        json.dumps(
            {
                "before": status_before,
                "after": status_after,
                "preserved": preserved,
            },
            sort_keys=True,
            separators=(",", ":"),
        ),
    )
    emit(
        "CHECK_REPOSITORY_STATUS_PRESERVED:",
        str(preserved).lower(),
    )
    emit("")

    theorem_pass = not failed and preserved
    emit("THEOREM_PASS:", str(theorem_pass).lower())
    emit(
        "FINAL_CLASSIFICATION:",
        "noncommuting_involutive_action_and_carrier_generate_"
        "a_dihedral_extension_whose_commutator_retains_"
        "encounter_order_erased_by_the_visible_V4_quotient",
    )
    emit(
        "BOUNDARY:",
        "The audit proves the abstract commutator theorem and one "
        "finite D16 realization. Extension means kernel-valued "
        "retained order information. No physical backaction, spatial "
        "extension, energy, electron, gravity, or radiation claim is "
        "made.",
    )
    emit(
        "KEEPER:",
        "The quotient records the encounter. The commutator records "
        "what the encounter could not forget.",
    )
    emit("MUTATION_PERFORMED: false")

    if not theorem_pass:
        raise RuntimeError("extension/evolution theorem gate failed")


try:
    main()
except Exception as exc:
    if not report:
        emit("OUT ==")
        emit("PACKET:", PACKET)
    emit("ERROR:", type(exc).__name__ + ":", str(exc))
    emit(
        "TRACEBACK:",
        " | ".join(traceback.format_exc().strip().splitlines()[-8:]),
    )
    emit("NEXT: Inspect the failed gate. The Termux session remains open.")

text = "\n".join(report) + "\n"
timestamp = datetime.datetime.now().astimezone().strftime(
    "%Y%m%dT%H%M%S%z"
)
out_path = (
    Path.home()
    / "tmp"
    / (PACKET + "_out_" + timestamp + ".txt")
)
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(text)

try:
    subprocess.run(
        ["termux-clipboard-set"],
        input=text,
        text=True,
        capture_output=True,
        check=False,
    )
except Exception:
    pass

print(text, end="")
print("OUT_FILE:", out_path)
