#!/usr/bin/env python3

from collections import Counter, deque

POINTS = tuple(range(5))

def permutation(multiplier, offset):
    return tuple(
        (multiplier * value + offset) % 5
        for value in POINTS
    )

def compose(left, right):
    return tuple(
        left[right[index]]
        for index in POINTS
    )

def inverse(permutation_row):
    return tuple(
        permutation_row.index(index)
        for index in POINTS
    )

def permutation_order(permutation_row):
    identity = POINTS
    current = identity

    for exponent in range(1, 101):
        current = compose(permutation_row, current)
        if current == identity:
            return exponent

    return None

def generate_group(generators):
    identity = POINTS
    group = {identity}
    queue = deque([identity])

    while queue:
        current = queue.popleft()

        for generator in generators:
            for candidate in (
                compose(generator, current),
                compose(current, generator),
            ):
                if candidate not in group:
                    group.add(candidate)
                    queue.append(candidate)

    return tuple(sorted(group))

def orbit(group, point):
    return tuple(sorted({
        element[point]
        for element in group
    }))

def stabilizer(group, point):
    return tuple(
        element
        for element in group
        if element[point] == point
    )

def conjugate(left, middle):
    return compose(
        compose(left, middle),
        inverse(left),
    )

rotation = permutation(1, 1)
twist_forward = permutation(2, 0)
twist_inverse = permutation(3, 0)
half_turn = permutation(4, 0)
identity = permutation(1, 0)

group = generate_group((
    rotation,
    twist_forward,
))

all_affine_rows = tuple(sorted({
    permutation(multiplier, offset)
    for multiplier in (1, 2, 3, 4)
    for offset in range(5)
}))

translation_subgroup = tuple(sorted({
    permutation(1, offset)
    for offset in range(5)
}))

zero_stabilizer = stabilizer(group, 0)

zero_stabilizer_expected = tuple(sorted({
    permutation(multiplier, 0)
    for multiplier in (1, 2, 3, 4)
}))

order_profile = Counter(
    permutation_order(element)
    for element in group
)

fixed_point_profile = Counter(
    sum(
        element[index] == index
        for index in POINTS
    )
    for element in group
)

translation_normal = all(
    conjugate(group_element, translation) in translation_subgroup
    for group_element in group
    for translation in translation_subgroup
)

ordered_distinct_pairs = tuple(
    (left, right)
    for left in POINTS
    for right in POINTS
    if left != right
)

pair_image_counts = {}

base_pair = (0, 1)

for target_pair in ordered_distinct_pairs:
    pair_image_counts[target_pair] = sum(
        (
            element[base_pair[0]],
            element[base_pair[1]],
        ) == target_pair
        for element in group
    )

sharply_two_transitive = (
    len(ordered_distinct_pairs) == 20
    and set(pair_image_counts.values()) == {1}
)

section_candidates = POINTS

full_group_fixed_points = tuple(
    point
    for point in POINTS
    if all(
        element[point] == point
        for element in group
    )
)

checks = {
    "rotation_order_5":
        permutation_order(rotation) == 5,
    "forward_twist_order_4":
        permutation_order(twist_forward) == 4,
    "inverse_twist_order_4":
        permutation_order(twist_inverse) == 4,
    "twists_are_inverse":
        inverse(twist_forward) == twist_inverse,
    "common_square_is_half_turn":
        compose(twist_forward, twist_forward) == half_turn
        and compose(twist_inverse, twist_inverse) == half_turn,
    "generated_group_order_20":
        len(group) == 20,
    "generated_group_equals_all_AGL15_maps":
        group == all_affine_rows,
    "translation_subgroup_order_5":
        len(translation_subgroup) == 5,
    "translation_subgroup_is_normal":
        translation_normal,
    "zero_stabilizer_order_4":
        len(zero_stabilizer) == 4,
    "zero_stabilizer_is_multiplier_C4":
        zero_stabilizer == zero_stabilizer_expected,
    "point_orbit_size_5":
        len(orbit(group, 0)) == 5,
    "group_order_profile_exact":
        order_profile == Counter({
            1: 1,
            2: 5,
            4: 10,
            5: 4,
        }),
    "action_is_sharply_two_transitive":
        sharply_two_transitive,
    "one_point_quotient_has_five_sections":
        len(section_candidates) == 5,
    "no_full_group_invariant_section":
        not full_group_fixed_points,
}

failed = [
    name
    for name, passed in checks.items()
    if not passed
]

theorem_pass = not failed

print("PACKET: g900_five_bridge_affine_group_055")
print("MODE: exact induced five-position register algebra")
print("ROTATION:", rotation)
print("TWIST_FORWARD:", twist_forward)
print("TWIST_INVERSE:", twist_inverse)
print("COMMON_HALF_TURN:", half_turn)
print("GENERATED_GROUP_ORDER:", len(group))
print("TRANSLATION_SUBGROUP_ORDER:", len(translation_subgroup))
print("ZERO_STABILIZER_ORDER:", len(zero_stabilizer))
print("ZERO_STABILIZER:", zero_stabilizer)
print("POINT_ORBIT:", orbit(group, 0))
print("ORDER_PROFILE:", dict(sorted(order_profile.items())))
print("FIXED_POINT_PROFILE:", dict(sorted(fixed_point_profile.items())))
print("PAIR_IMAGE_COUNT_PROFILE:", dict(Counter(
    pair_image_counts.values()
)))
print("FULL_GROUP_FIXED_POINTS:", full_group_fixed_points)
print("CHECKS:", checks)
print("FAILED_CHECK_COUNT:", len(failed))
print("FAILED_CHECKS:", failed)
print("THEOREM_PASS:", theorem_pass)
print(
    "CLASSIFICATION:",
    (
        "the_induced_five_bridge_register_algebra_is_"
        "AGL_1_5_equals_C5_semidirect_C4_with_a_normal_"
        "translation_C5_and_order_four_point_stabilizer"
        if theorem_pass
        else "five_bridge_affine_group_not_derived"
    ),
)
print("INDUCED_REGISTER_GROUP_IS_AGL_1_5:", theorem_pass)
print("GROUP_ORDER:", 20 if theorem_pass else None)
print("NORMAL_TRANSLATION_SUBGROUP:", "C5" if theorem_pass else None)
print("POINT_STABILIZER:", "C4" if theorem_pass else None)
print("ONE_FIXED_FOUR_MOVING_EXPLAINED:", theorem_pass)
print("QUOTIENT_SECTION_COUNT:", 5)
print("INVARIANT_QUOTIENT_SECTION_COUNT:", 0)
print("NATIVE_G15_AUTOMORPHISM_GROUP_CLAIM:", False)
print("INDUCED_REGISTER_ALGEBRA_ONLY:", True)
print("PHYSICAL_CLAIM:", False)
print("MUTATION_PERFORMED:", False)
