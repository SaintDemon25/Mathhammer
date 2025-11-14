#!/usr/bin/env python3
"""
Comprehensive Edge Case and Error Handling Test Suite
Tests boundary conditions, invalid inputs, and error scenarios
"""

import sys
import logging

logging.basicConfig(level=logging.WARNING)

tests_passed = 0
tests_total = 0


def test_result(name, passed):
    """Record test result"""
    global tests_passed, tests_total
    tests_total += 1
    if passed:
        tests_passed += 1
        print(f"  ✅ {name}")
    else:
        print(f"  ❌ {name}")
    return passed


def test_1_zero_attacks_handling():
    """Test 1: Combat engine handles zero attacks gracefully"""
    print("\n" + "="*80)
    print("TEST 1: Zero Attacks Edge Case")
    print("="*80)

    try:
        from combat_engine import CombatSimulator, AttackType, WeaponAbilities, UnitAbilities

        sim = CombatSimulator()
        result = sim.simulate_attack_sequence(
            num_attacks=0,
            skill=3,
            strength=4,
            ap=0,
            damage='1',
            attack_type=AttackType.RANGED,
            toughness=4,
            save=3,
            invuln=None,
            wounds_per_model=1,
            unit_size=10,
            weapon_abilities=WeaponAbilities(),
            target_abilities=UnitAbilities(),
            attacker_abilities=UnitAbilities()
        )

        # Should return zero results without crashing
        passes = result.num_attacks == 0 and result.num_hits == 0
        print(f"  Zero attacks handled: {passes}")
        print(f"  Result: {result.num_attacks} attacks, {result.num_hits} hits")

        return test_result("Zero attacks handled gracefully", passes)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("Zero attacks handled gracefully", False)


def test_2_impossible_skill_values():
    """Test 2: Skill values outside valid range (2-6)"""
    print("\n" + "="*80)
    print("TEST 2: Invalid Skill Values")
    print("="*80)

    try:
        from combat_engine import CombatSimulator, AttackType, WeaponAbilities, UnitAbilities

        sim = CombatSimulator()

        # Test skill 7+ (impossible - should never hit)
        result_impossible = sim.simulate_attack_sequence(
            num_attacks=10,
            skill=7,
            strength=4,
            ap=0,
            damage='1',
            attack_type=AttackType.RANGED,
            toughness=4,
            save=3,
            invuln=None,
            wounds_per_model=1,
            unit_size=10,
            weapon_abilities=WeaponAbilities(),
            target_abilities=UnitAbilities(),
            attacker_abilities=UnitAbilities()
        )

        # Test skill 1 (always hits on 2+, skill 1 not valid in 10th)
        result_easy = sim.simulate_attack_sequence(
            num_attacks=10,
            skill=1,
            strength=4,
            ap=0,
            damage='1',
            attack_type=AttackType.RANGED,
            toughness=4,
            save=3,
            invuln=None,
            wounds_per_model=1,
            unit_size=10,
            weapon_abilities=WeaponAbilities(),
            target_abilities=UnitAbilities(),
            attacker_abilities=UnitAbilities()
        )

        # Skill 7+ should result in no hits (impossible to roll 7+ on d6)
        impossible_handled = result_impossible.num_hits == 0

        print(f"  Skill 7 handled: {impossible_handled} (hits: {result_impossible.num_hits})")
        print(f"  Skill 1 result: {result_easy.num_hits} hits")

        return test_result("Invalid skill values handled", impossible_handled)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("Invalid skill values handled", False)


def test_3_zero_unit_size():
    """Test 3: Zero or negative unit size"""
    print("\n" + "="*80)
    print("TEST 3: Zero/Negative Unit Size")
    print("="*80)

    try:
        from combat_engine import CombatSimulator, AttackType, WeaponAbilities, UnitAbilities

        sim = CombatSimulator()

        # Zero unit size
        result_zero = sim.simulate_attack_sequence(
            num_attacks=10,
            skill=3,
            strength=8,
            ap=-2,
            damage='3',
            attack_type=AttackType.RANGED,
            toughness=4,
            save=3,
            invuln=None,
            wounds_per_model=1,
            unit_size=0,
            weapon_abilities=WeaponAbilities(),
            target_abilities=UnitAbilities(),
            attacker_abilities=UnitAbilities()
        )

        # Should not crash, models_destroyed should be 0
        passes = result_zero.models_destroyed == 0
        print(f"  Zero unit size handled: {passes}")
        print(f"  Models destroyed: {result_zero.models_destroyed}")

        return test_result("Zero unit size handled", passes)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("Zero unit size handled", False)


def test_4_extreme_damage_values():
    """Test 4: Very high damage vs low wounds models"""
    print("\n" + "="*80)
    print("TEST 4: Extreme Damage Values")
    print("="*80)

    try:
        from combat_engine import CombatSimulator, AttackType, WeaponAbilities, UnitAbilities

        sim = CombatSimulator()

        # 100 damage vs 1 wound models - should overkill
        result = sim.simulate_attack_sequence(
            num_attacks=1,
            skill=2,  # Auto-hit essentially
            strength=10,
            ap=-4,
            damage='100',
            attack_type=AttackType.RANGED,
            toughness=3,
            save=3,
            invuln=None,
            wounds_per_model=1,
            unit_size=5,
            weapon_abilities=WeaponAbilities(),
            target_abilities=UnitAbilities(),
            attacker_abilities=UnitAbilities()
        )

        # Even with overkill, max 5 models can be destroyed
        passes = result.models_destroyed <= 5
        print(f"  Overkill handled correctly: {passes}")
        print(f"  Models destroyed: {result.models_destroyed} (max 5)")
        print(f"  Total damage: {result.total_damage}")

        return test_result("Extreme damage handled", passes)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("Extreme damage handled", False)


def test_5_invuln_better_than_save():
    """Test 5: Invulnerable save better than armor save"""
    print("\n" + "="*80)
    print("TEST 5: Invuln Better Than Save")
    print("="*80)

    try:
        from combat_engine import CombatSimulator, AttackType, WeaponAbilities, UnitAbilities

        sim = CombatSimulator()

        # 3+ armor, 2++ invuln - should use invuln
        result = sim.simulate_attack_sequence(
            num_attacks=100,
            skill=3,
            strength=8,
            ap=-3,  # Would make armor 6+
            damage='1',
            attack_type=AttackType.RANGED,
            toughness=4,
            save=3,
            invuln=2,  # 2++ better than 6+
            wounds_per_model=1,
            unit_size=50,
            weapon_abilities=WeaponAbilities(),
            target_abilities=UnitAbilities(),
            attacker_abilities=UnitAbilities()
        )

        # With 2++ saves, should save most wounds
        # Expected: ~83% save rate on 2++
        save_rate = result.num_saves_made / (result.num_saves_made + result.num_saves_failed) if result.num_wounds > 0 else 0

        # 2++ should save on 5/6 rolls = ~83%
        passes = save_rate > 0.7  # Allow some variance
        print(f"  Invuln used correctly: {passes}")
        print(f"  Save rate: {save_rate:.1%} (expected ~83% for 2++)")
        print(f"  Saves made: {result.num_saves_made}, failed: {result.num_saves_failed}")

        return test_result("Invuln better than save works", passes)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("Invuln better than save works", False)


def test_6_dice_notation_edge_cases():
    """Test 6: Various dice notation formats"""
    print("\n" + "="*80)
    print("TEST 6: Dice Notation Edge Cases")
    print("="*80)

    try:
        from combat_engine import DiceRoll

        # Test various formats
        test_cases = [
            ('1', 1),
            ('D3', (1, 3)),
            ('D6', (1, 6)),
            ('2D6', (2, 12)),
            ('D6+2', (3, 8)),
            ('2D6+4', (6, 16)),
        ]

        all_pass = True
        for notation, expected_range in test_cases:
            result = DiceRoll.parse_dice_notation(notation)
            if isinstance(expected_range, tuple):
                min_val, max_val = expected_range
                passes = min_val <= result <= max_val
            else:
                passes = result == expected_range

            print(f"  {notation}: {result} - {'✓' if passes else '✗'}")
            all_pass = all_pass and passes

        return test_result("Dice notation parsed correctly", all_pass)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("Dice notation parsed correctly", False)


def test_7_cp_tracking_bounds():
    """Test 7: CP cannot go negative"""
    print("\n" + "="*80)
    print("TEST 7: CP Tracking Bounds")
    print("="*80)

    try:
        with open('static/js/battle_mode.js', 'r') as f:
            content = f.read()

        # Check for CP validation
        has_cp_check = "cpRemaining >= stratData.cp_cost" in content or "cpRemaining >=" in content
        prevents_negative = "cpRemaining >= " in content

        print(f"  Has CP check before spending: {has_cp_check}")
        print(f"  Prevents negative CP: {prevents_negative}")

        return test_result("CP bounds enforced", has_cp_check and prevents_negative)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("CP bounds enforced", False)


def test_8_empty_weapon_list_handling():
    """Test 8: Unit with no weapons"""
    print("\n" + "="*80)
    print("TEST 8: Empty Weapon List")
    print("="*80)

    try:
        with open('static/js/battle_mode.js', 'r') as f:
            content = f.read()

        # Check for empty weapons handling
        has_empty_check = "availableWeapons.length === 0" in content
        shows_message = "No weapons available" in content

        print(f"  Checks for empty weapon list: {has_empty_check}")
        print(f"  Shows appropriate message: {shows_message}")

        return test_result("Empty weapon list handled", has_empty_check and shows_message)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("Empty weapon list handled", False)


def test_9_stratagem_cost_validation():
    """Test 9: Stratagem CP costs are valid"""
    print("\n" + "="*80)
    print("TEST 9: Stratagem Cost Validation")
    print("="*80)

    try:
        from stratagems import get_core_stratagems

        stratagems = get_core_stratagems()
        all_valid = True

        for strat in stratagems:
            # CP costs should be 1 or 2 for core stratagems
            valid_cost = strat.cp_cost in [1, 2]
            if not valid_cost:
                print(f"  Invalid cost for {strat.name}: {strat.cp_cost}")
                all_valid = False

        print(f"  All stratagems have valid costs (1-2 CP): {all_valid}")
        print(f"  Total stratagems checked: {len(stratagems)}")

        return test_result("Stratagem costs valid", all_valid)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("Stratagem costs valid", False)


def test_10_comparison_mode_max_weapons():
    """Test 10: Comparison mode enforces 5 weapon limit"""
    print("\n" + "="*80)
    print("TEST 10: Comparison Mode Weapon Limit")
    print("="*80)

    try:
        with open('static/js/battle_mode.js', 'r') as f:
            content = f.read()

        # Check for weapon limit
        has_limit_check = "selectedWeapons.length < 5" in content
        shows_limit_message = "Maximum 5 weapons" in content

        print(f"  Enforces 5 weapon limit: {has_limit_check}")
        print(f"  Shows limit message: {shows_limit_message}")

        return test_result("Weapon limit enforced", has_limit_check and shows_limit_message)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("Weapon limit enforced", False)


def main():
    """Run all edge case tests"""
    print("\n" + "="*80)
    print("🧪 COMPREHENSIVE EDGE CASE & ERROR HANDLING TEST SUITE")
    print("="*80)

    test_1_zero_attacks_handling()
    test_2_impossible_skill_values()
    test_3_zero_unit_size()
    test_4_extreme_damage_values()
    test_5_invuln_better_than_save()
    test_6_dice_notation_edge_cases()
    test_7_cp_tracking_bounds()
    test_8_empty_weapon_list_handling()
    test_9_stratagem_cost_validation()
    test_10_comparison_mode_max_weapons()

    print("\n" + "="*80)
    print("📊 FINAL RESULTS")
    print("="*80)
    print(f"Passed: {tests_passed}/{tests_total}")
    print("="*80)

    if tests_passed == tests_total:
        print("\n✅ ALL TESTS PASSED!\n")
        return 0
    else:
        print(f"\n⚠️  {tests_total - tests_passed} test(s) failed\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())
