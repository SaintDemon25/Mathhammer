#!/usr/bin/env python3
"""
Test Battle Mode weapon filtering and combat calculations
"""

from battle_mode_api import filter_weapons_for_combat


def test_weapon_filtering():
    """Test weapon filtering for different combat types"""
    print("="*80)
    print("BATTLE MODE WEAPON FILTERING TEST")
    print("="*80)

    # Sample weapons
    weapons = [
        {'name': 'Bolt Rifle', 'type': 'Ranged Weapons', 'keywords': ''},
        {'name': 'Astartes Chainsword', 'type': 'Melee Weapons', 'keywords': ''},
        {'name': 'Heavy Bolt Pistol', 'type': 'Ranged Weapons', 'keywords': 'Pistol'},
        {'name': 'Plasma Pistol', 'type': 'Ranged Weapons', 'keywords': 'Pistol, Hazardous'},
        {'name': 'Power Fist', 'type': 'Melee Weapons', 'keywords': ''},
    ]

    tests_passed = 0
    tests_total = 0

    # Test 1: Ranged combat (normal shooting)
    print("\nTest 1: Ranged Combat (Normal Shooting)")
    print("-" * 40)
    tests_total += 1

    filtered = filter_weapons_for_combat(weapons, 'ranged', False)
    weapon_names = [w['name'] for w in filtered]

    print(f"Available weapons: {weapon_names}")

    # Should have all ranged weapons
    expected = ['Bolt Rifle', 'Heavy Bolt Pistol', 'Plasma Pistol']
    if set(weapon_names) == set(expected):
        print("✓ Correct: All ranged weapons available")
        tests_passed += 1
    else:
        print(f"✗ Expected: {expected}")

    # Test 2: Melee combat
    print("\nTest 2: Melee Combat")
    print("-" * 40)
    tests_total += 1

    filtered = filter_weapons_for_combat(weapons, 'melee', False)
    weapon_names = [w['name'] for w in filtered]

    print(f"Available weapons: {weapon_names}")

    # Should have melee weapons + pistols
    expected = ['Astartes Chainsword', 'Power Fist', 'Heavy Bolt Pistol', 'Plasma Pistol']
    if set(weapon_names) == set(expected):
        print("✓ Correct: Melee weapons + pistols available")
        tests_passed += 1
    else:
        print(f"✗ Expected: {expected}")

    # Test 3: Shooting while engaged (normal unit)
    print("\nTest 3: Shooting While Engaged (Normal Infantry)")
    print("-" * 40)
    tests_total += 1

    filtered = filter_weapons_for_combat(weapons, 'ranged_engaged', False)
    weapon_names = [w['name'] for w in filtered]

    print(f"Available weapons: {weapon_names}")

    # Should only have pistols
    expected = ['Heavy Bolt Pistol', 'Plasma Pistol']
    if set(weapon_names) == set(expected):
        print("✓ Correct: Only pistols available for normal units")
        tests_passed += 1
    else:
        print(f"✗ Expected: {expected}")

    # Test 4: Shooting while engaged (Monster/Vehicle)
    print("\nTest 4: Shooting While Engaged (Monster/Vehicle)")
    print("-" * 40)
    tests_total += 1

    filtered = filter_weapons_for_combat(weapons, 'ranged_engaged', True)
    weapon_names = [w['name'] for w in filtered]

    print(f"Available weapons: {weapon_names}")

    # Should have all ranged weapons (with -1 hit modifier)
    expected = ['Bolt Rifle', 'Heavy Bolt Pistol', 'Plasma Pistol']
    if set(weapon_names) == set(expected):
        print("✓ Correct: All ranged weapons available for Monsters/Vehicles")
        # Check if hit modifier is applied
        has_modifier = any(w.get('hit_modifier') == -1 for w in filtered)
        if has_modifier:
            print("✓ Correct: -1 hit modifier applied")
            tests_passed += 1
        else:
            print("✗ Missing -1 hit modifier")
    else:
        print(f"✗ Expected: {expected}")

    # Test 5: Melee only unit (no ranged weapons)
    print("\nTest 5: Melee-Only Unit")
    print("-" * 40)
    tests_total += 1

    melee_only = [
        {'name': 'Power Sword', 'type': 'Melee Weapons', 'keywords': ''},
        {'name': 'Thunder Hammer', 'type': 'Melee Weapons', 'keywords': 'Devastating Wounds'},
    ]

    filtered = filter_weapons_for_combat(melee_only, 'ranged', False)

    if len(filtered) == 0:
        print("✓ Correct: No weapons available for ranged combat")
        tests_passed += 1
    else:
        print(f"✗ Should have no weapons, got: {[w['name'] for w in filtered]}")

    # Summary
    print("\n" + "="*80)
    print(f"SUMMARY: {tests_passed}/{tests_total} tests passed")
    print("="*80)

    return tests_passed == tests_total


def main():
    success = test_weapon_filtering()

    if success:
        print("\n✅ ALL BATTLE MODE TESTS PASSED!\n")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED\n")
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
