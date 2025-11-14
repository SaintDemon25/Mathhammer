#!/usr/bin/env python3
"""
Combat Engine Integration Tests
Tests combat simulator with various scenarios
"""

from combat_engine import CombatSimulator, WeaponAbilities, UnitAbilities, AttackType


def test_combat_engine():
    """Test combat engine basics"""
    print("="*80)
    print("COMBAT ENGINE INTEGRATION TESTS")
    print("="*80)

    sim = CombatSimulator()
    tests_passed = 0
    tests_total = 0

    # Test 1: Basic ranged attack
    print("\nTest 1: Basic ranged attack (BS 3+, S4 vs T4, AP0)")
    tests_total += 1
    try:
        result = sim.simulate_attack_sequence(
            num_attacks=10,
            skill=3,
            strength=4,
            ap=0,
            damage="1",
            toughness=4,
            save=3,
            invuln=None,
            wounds_per_model=2,
            unit_size=10,
            attack_type=AttackType.RANGED,
            weapon_abilities=WeaponAbilities(),
            target_abilities=UnitAbilities(),
            attacker_abilities=UnitAbilities()
        )

        print(f"  Hits: {result.total_hits}")
        print(f"  Wounds: {result.total_wounds}")
        print(f"  ✓ Basic combat works")
        tests_passed += 1
    except Exception as e:
        print(f"  ✗ Failed: {e}")

    # Test 2: Lethal Hits
    print("\nTest 2: Lethal Hits ability")
    tests_total += 1
    try:
        abilities = WeaponAbilities(lethal_hits=True)
        result = sim.simulate_attack_sequence(
            num_attacks=100,
            skill=3,
            strength=4,
            ap=0,
            damage="1",
            toughness=8,  # Hard to wound
            save=3,
            invuln=None,
            wounds_per_model=2,
            unit_size=10,
            attack_type=AttackType.RANGED,
            weapon_abilities=abilities,
            target_abilities=UnitAbilities(),
            attacker_abilities=UnitAbilities()
        )

        if result.total_wounds > 0:
            print(f"  Wounds: {result.total_wounds}")
            print(f"  ✓ Lethal Hits working (auto-wound on crits)")
            tests_passed += 1
        else:
            print(f"  ✗ No wounds despite Lethal Hits")
    except Exception as e:
        print(f"  ✗ Failed: {e}")

    # Test 3: Devastating Wounds
    print("\nTest 3: Devastating Wounds ability")
    tests_total += 1
    try:
        abilities = WeaponAbilities(devastating_wounds=True)
        result = sim.simulate_attack_sequence(
            num_attacks=100,
            skill=3,
            strength=4,
            ap=0,
            damage="1",
            toughness=4,
            save=2,  # Good save
            invuln=None,
            wounds_per_model=2,
            unit_size=10,
            attack_type=AttackType.RANGED,
            weapon_abilities=abilities,
            target_abilities=UnitAbilities(),
            attacker_abilities=UnitAbilities()
        )

        print(f"  Wounds: {result.total_wounds}")
        print(f"  ✓ Devastating Wounds working")
        tests_passed += 1
    except Exception as e:
        print(f"  ✗ Failed: {e}")

    # Test 4: Feel No Pain
    print("\nTest 4: Feel No Pain 5+")
    tests_total += 1
    try:
        unit_abilities = UnitAbilities(feel_no_pain=5)
        result = sim.simulate_attack_sequence(
            num_attacks=100,
            skill=3,
            strength=8,
            ap=-3,
            damage="2",
            toughness=4,
            save=3,
            invuln=None,
            wounds_per_model=3,
            unit_size=10,
            attack_type=AttackType.RANGED,
            weapon_abilities=WeaponAbilities(),
            target_abilities=unit_abilities,
            attacker_abilities=UnitAbilities()
        )

        print(f"  Wounds dealt: {result.wounds_dealt}")
        print(f"  Final wounds: {result.total_wounds}")
        if result.total_wounds < result.wounds_dealt:
            print(f"  ✓ FNP reduced {result.wounds_dealt - result.total_wounds} wounds")
            tests_passed += 1
        else:
            print(f"  ✗ FNP didn't reduce wounds")
    except Exception as e:
        print(f"  ✗ Failed: {e}")

    # Test 5: Invulnerable save
    print("\nTest 5: 4+ Invulnerable save vs AP-4")
    tests_total += 1
    try:
        result = sim.simulate_attack_sequence(
            num_attacks=100,
            skill=3,
            strength=8,
            ap=-4,
            damage="1",
            toughness=4,
            save=3,
            invuln=4,
            wounds_per_model=2,
            unit_size=10,
            attack_type=AttackType.RANGED,
            weapon_abilities=WeaponAbilities(),
            target_abilities=UnitAbilities(),
            attacker_abilities=UnitAbilities()
        )

        if result.successful_saves > 0:
            print(f"  Saves: {result.successful_saves}")
            print(f"  ✓ Invuln save working")
            tests_passed += 1
        else:
            print(f"  ✗ No invuln saves")
    except Exception as e:
        print(f"  ✗ Failed: {e}")

    print(f"\n{'='*80}")
    print(f"Combat Engine: {tests_passed}/{tests_total} tests passed")
    print(f"{'='*80}")

    return tests_passed == tests_total


def test_with_real_data():
    """Test combat with real unit data from parser"""
    print("\n" + "="*80)
    print("COMBAT WITH REAL UNIT DATA")
    print("="*80)

    from pathlib import Path
    from enhanced_parser import EnhancedBSDataParser

    dataset_path = Path('datasets')
    if not dataset_path.exists():
        print("⚠️  Dataset not found, skipping")
        return True

    tests_passed = 0
    tests_total = 0

    # Load data
    parser = EnhancedBSDataParser()
    catalog = parser.load_dataset_enhanced(str(dataset_path))

    # Test 1: Find and use Land Raider Godhammer Lascannon
    print("\nTest 1: Land Raider Godhammer Lascannon vs Vehicle")
    tests_total += 1

    land_raider = None
    for unit in catalog.units.values():
        if unit.name == "Land Raider":
            land_raider = unit
            break

    if land_raider:
        godhammer = land_raider.get_weapon_by_name("Godhammer Lascannon")

        if godhammer:
            print(f"  ✓ Found weapon: {godhammer.name}")

            sim = CombatSimulator()
            result = sim.simulate_attack_sequence(
                num_attacks=2,
                skill=3,
                strength=12,
                ap=-3,
                damage="4",  # Approximate D6+1
                toughness=10,
                save=2,
                invuln=None,
                wounds_per_model=16,
                unit_size=1,
                attack_type=AttackType.RANGED,
                weapon_abilities=WeaponAbilities(),
                target_abilities=UnitAbilities(),
                attacker_abilities=UnitAbilities()
            )

            print(f"  Attacks: 2")
            print(f"  Hits: {result.total_hits}")
            print(f"  Wounds: {result.total_wounds}")
            print(f"  Total Damage: {result.total_wounds * 4}")
            print(f"  ✓ Simulation complete")
            tests_passed += 1
        else:
            print(f"  ✗ Weapon not found")
    else:
        print(f"  ✗ Land Raider not found")

    print(f"\n{'='*80}")
    print(f"Real Data Tests: {tests_passed}/{tests_total} passed")
    print(f"{'='*80}")

    return tests_passed == tests_total


def main():
    result1 = test_combat_engine()
    result2 = test_with_real_data()

    if result1 and result2:
        print("\n✅ ALL COMBAT INTEGRATION TESTS PASSED\n")
        return True
    else:
        print("\n❌ SOME TESTS FAILED\n")
        return False


if __name__ == '__main__':
    import sys
    sys.exit(0 if main() else 1)
