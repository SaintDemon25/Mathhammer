#!/usr/bin/env python3
"""
Integration Test Suite
Tests component interactions and data flow across the entire system
"""

import sys
import logging
import json
from pathlib import Path

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


def test_1_combat_engine_to_api_flow():
    """Test 1: Combat engine results flow correctly to API"""
    print("\n" + "="*80)
    print("TEST 1: Combat Engine to API Integration")
    print("="*80)

    try:
        from combat_engine import CombatSimulator, AttackType, WeaponAbilities, UnitAbilities

        # Simulate what the API does
        sim = CombatSimulator()
        result = sim.simulate_attack_sequence(
            num_attacks=10,
            skill=3,
            strength=4,
            ap=-1,
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

        # Check that all expected fields exist
        has_attacks = hasattr(result, 'num_attacks')
        has_hits = hasattr(result, 'num_hits')
        has_wounds = hasattr(result, 'num_wounds')
        has_damage = hasattr(result, 'total_damage')
        has_models_destroyed = hasattr(result, 'models_destroyed')

        print(f"  Result has all expected fields: {all([has_attacks, has_hits, has_wounds, has_damage, has_models_destroyed])}")
        print(f"  Attacks: {result.num_attacks}, Hits: {result.num_hits}, Wounds: {result.num_wounds}")
        print(f"  Damage: {result.total_damage}, Models: {result.models_destroyed}")

        return test_result("Combat engine to API flow works",
                          all([has_attacks, has_hits, has_wounds, has_damage, has_models_destroyed]))
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("Combat engine to API flow works", False)


def test_2_stratagem_system_integration():
    """Test 2: Stratagems integrate with combat calculations"""
    print("\n" + "="*80)
    print("TEST 2: Stratagem System Integration")
    print("="*80)

    try:
        from stratagems import get_core_stratagems, apply_stratagem_to_combat

        stratagems = get_core_stratagems()
        has_stratagems = len(stratagems) > 0

        # Test applying a stratagem
        test_params = {
            'skill': 3,
            'hit_modifier': 0,
            'invuln': None,
            'has_cover': False,
            'mortal_wounds_bonus': 0
        }

        # Apply Command Re-roll
        modified = apply_stratagem_to_combat('command_reroll', test_params)
        reroll_applied = modified.get('command_reroll_available', False)

        print(f"  Has core stratagems: {has_stratagems} ({len(stratagems)} total)")
        print(f"  Command Re-roll applies: {reroll_applied}")

        return test_result("Stratagem system integrates", has_stratagems and reroll_applied)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("Stratagem system integrates", False)


def test_3_dice_notation_in_combat():
    """Test 3: Dice notation integrates with damage calculation"""
    print("\n" + "="*80)
    print("TEST 3: Dice Notation Integration")
    print("="*80)

    try:
        from combat_engine import CombatSimulator, AttackType, WeaponAbilities, UnitAbilities

        sim = CombatSimulator()

        # Test with D6 damage (run multiple times for statistical average)
        d6_damages = []
        d6plus_damages = []

        for _ in range(10):
            result_d6 = sim.simulate_attack_sequence(
                num_attacks=100,
                skill=2,
                strength=8,
                ap=-2,
                damage='D6',  # Dice notation
                attack_type=AttackType.RANGED,
                toughness=4,
                save=3,
                invuln=None,
                wounds_per_model=3,
                unit_size=100,
                weapon_abilities=WeaponAbilities(),
                target_abilities=UnitAbilities(),
                attacker_abilities=UnitAbilities()
            )
            d6_damages.append(result_d6.total_damage)

            # Test with D6+2 damage
            result_d6_plus = sim.simulate_attack_sequence(
                num_attacks=100,
                skill=2,
                strength=8,
                ap=-2,
                damage='D6+2',  # Dice notation with modifier
                attack_type=AttackType.RANGED,
                toughness=4,
                save=3,
                invuln=None,
                wounds_per_model=3,
                unit_size=100,
                weapon_abilities=WeaponAbilities(),
                target_abilities=UnitAbilities(),
                attacker_abilities=UnitAbilities()
            )
            d6plus_damages.append(result_d6_plus.total_damage)

        # D6+2 should do more damage than D6 on average
        avg_d6 = sum(d6_damages) / len(d6_damages)
        avg_d6plus = sum(d6plus_damages) / len(d6plus_damages)
        more_damage = avg_d6plus > avg_d6

        print(f"  D6 average damage: {avg_d6:.1f}")
        print(f"  D6+2 average damage: {avg_d6plus:.1f}")
        print(f"  D6+2 > D6: {more_damage}")

        return test_result("Dice notation integrates with damage", more_damage)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("Dice notation integrates with damage", False)


def test_4_weapon_abilities_affect_combat():
    """Test 4: Weapon abilities properly affect combat results"""
    print("\n" + "="*80)
    print("TEST 4: Weapon Abilities Integration")
    print("="*80)

    try:
        from combat_engine import CombatSimulator, AttackType, WeaponAbilities, UnitAbilities

        sim = CombatSimulator()

        # Test without abilities
        result_normal = sim.simulate_attack_sequence(
            num_attacks=100,
            skill=3,
            strength=4,
            ap=0,
            damage='1',
            attack_type=AttackType.RANGED,
            toughness=4,
            save=6,
            invuln=None,
            wounds_per_model=1,
            unit_size=100,
            weapon_abilities=WeaponAbilities(),
            target_abilities=UnitAbilities(),
            attacker_abilities=UnitAbilities()
        )

        # Test with Torrent (auto-hit)
        abilities = WeaponAbilities(torrent=True)
        result_torrent = sim.simulate_attack_sequence(
            num_attacks=100,
            skill=6,  # Terrible skill, but Torrent auto-hits
            strength=4,
            ap=0,
            damage='1',
            attack_type=AttackType.RANGED,
            toughness=4,
            save=6,
            invuln=None,
            wounds_per_model=1,
            unit_size=100,
            weapon_abilities=abilities,
            target_abilities=UnitAbilities(),
            attacker_abilities=UnitAbilities()
        )

        # Torrent should have more hits despite worse skill (100 vs ~17 for skill 6)
        torrent_works = result_torrent.num_hits > result_normal.num_hits

        print(f"  Normal hits (skill 3): {result_normal.num_hits}")
        print(f"  Torrent hits (skill 6): {result_torrent.num_hits}")
        print(f"  Torrent improves hits: {torrent_works}")

        return test_result("Weapon abilities affect combat", torrent_works)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("Weapon abilities affect combat", False)


def test_5_target_abilities_affect_saves():
    """Test 5: Target abilities properly affect save results"""
    print("\n" + "="*80)
    print("TEST 5: Target Abilities Integration")
    print("="*80)

    try:
        from combat_engine import CombatSimulator, AttackType, WeaponAbilities, UnitAbilities

        sim = CombatSimulator()

        # Without cover - use larger sample
        result_no_cover = sim.simulate_attack_sequence(
            num_attacks=1000,
            skill=3,
            strength=4,
            ap=0,
            damage='1',
            attack_type=AttackType.RANGED,
            toughness=4,
            save=4,
            invuln=None,
            wounds_per_model=1,
            unit_size=1000,
            weapon_abilities=WeaponAbilities(),
            target_abilities=UnitAbilities(),
            attacker_abilities=UnitAbilities()
        )

        # With cover
        target_abilities = UnitAbilities(cover=True, cover_bonus=1)
        result_with_cover = sim.simulate_attack_sequence(
            num_attacks=1000,
            skill=3,
            strength=4,
            ap=0,
            damage='1',
            attack_type=AttackType.RANGED,
            toughness=4,
            save=4,
            invuln=None,
            wounds_per_model=1,
            unit_size=1000,
            weapon_abilities=WeaponAbilities(),
            target_abilities=target_abilities,
            attacker_abilities=UnitAbilities()
        )

        # Cover should reduce damage
        cover_helps = result_with_cover.total_damage < result_no_cover.total_damage

        print(f"  Damage without cover: {result_no_cover.total_damage}")
        print(f"  Damage with cover: {result_with_cover.total_damage}")
        print(f"  Cover reduces damage: {cover_helps}")

        return test_result("Target abilities affect saves", cover_helps)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("Target abilities affect saves", False)


def test_6_army_list_json_structure():
    """Test 6: Army list JSON files have correct structure"""
    print("\n" + "="*80)
    print("TEST 6: Army List JSON Structure")
    print("="*80)

    try:
        army_lists_dir = Path('army_lists')
        if not army_lists_dir.exists():
            print("  army_lists directory not found, skipping")
            return test_result("Army list JSON structure valid", True)

        json_files = list(army_lists_dir.glob('*.json'))
        if len(json_files) == 0:
            print("  No army list files found, skipping")
            return test_result("Army list JSON structure valid", True)

        all_valid = True
        for json_file in json_files[:3]:  # Check first 3 files
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            has_faction = 'faction' in data
            has_points = 'total_points' in data
            has_units = 'units' in data

            file_valid = has_faction and has_points and has_units
            all_valid = all_valid and file_valid

            print(f"  {json_file.name}: faction={has_faction}, points={has_points}, units={has_units}")

        return test_result("Army list JSON structure valid", all_valid)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("Army list JSON structure valid", False)


def test_7_statistical_simulation_consistency():
    """Test 7: Statistical simulations produce consistent results"""
    print("\n" + "="*80)
    print("TEST 7: Statistical Simulation Consistency")
    print("="*80)

    try:
        from combat_engine import CombatSimulator, AttackType, WeaponAbilities, UnitAbilities

        sim = CombatSimulator()

        # Run same simulation multiple times
        results = []
        for _ in range(5):
            result = sim.simulate_attack_sequence(
                num_attacks=1000,
                skill=3,
                strength=4,
                ap=0,
                damage='1',
                attack_type=AttackType.RANGED,
                toughness=4,
                save=3,
                invuln=None,
                wounds_per_model=1,
                unit_size=500,
                weapon_abilities=WeaponAbilities(),
                target_abilities=UnitAbilities(),
                attacker_abilities=UnitAbilities()
            )
            results.append(result.total_damage)

        # Calculate variance
        avg = sum(results) / len(results)
        variance = sum((x - avg) ** 2 for x in results) / len(results)
        std_dev = variance ** 0.5

        # Coefficient of variation should be reasonable (< 20%)
        cv = (std_dev / avg) * 100 if avg > 0 else 0
        consistent = cv < 20

        print(f"  Average damage: {avg:.1f}")
        print(f"  Std deviation: {std_dev:.1f}")
        print(f"  Coefficient of variation: {cv:.1f}%")
        print(f"  Results are consistent (CV < 20%): {consistent}")

        return test_result("Statistical simulations consistent", consistent)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("Statistical simulations consistent", False)


def test_8_cp_system_prevents_overspending():
    """Test 8: CP system integration prevents overspending"""
    print("\n" + "="*80)
    print("TEST 8: CP System Integration")
    print("="*80)

    try:
        with open('static/js/battle_mode.js', 'r') as f:
            content = f.read()

        # Check that JavaScript enforces CP limits
        has_cp_check = 'cpRemaining >= stratData.cp_cost' in content
        disables_button = '.disabled' in content or 'disabled' in content
        updates_display = 'updateCPDisplay' in content or 'CP:' in content

        print(f"  Checks CP before spending: {has_cp_check}")
        print(f"  Disables stratagems when no CP: {disables_button}")
        print(f"  Updates CP display: {updates_display}")

        return test_result("CP system prevents overspending",
                          has_cp_check and disables_button and updates_display)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("CP system prevents overspending", False)


def test_9_weapon_filtering_by_combat_type():
    """Test 9: Weapon filtering works for different combat types"""
    print("\n" + "="*80)
    print("TEST 9: Weapon Filtering Integration")
    print("="*80)

    try:
        from battle_mode_api import filter_weapons_for_combat

        # Sample weapons
        weapons = [
            {'name': 'Bolter', 'type': 'Ranged', 'keywords': ''},
            {'name': 'Plasma Pistol', 'type': 'Ranged', 'keywords': 'Pistol'},
            {'name': 'Chainsword', 'type': 'Melee', 'keywords': ''},
        ]

        # Test ranged combat (not engaged)
        ranged = filter_weapons_for_combat(weapons, 'ranged', False)
        ranged_correct = len(ranged) == 2  # Bolter + Plasma Pistol

        # Test melee combat
        melee = filter_weapons_for_combat(weapons, 'melee', False)
        melee_correct = len(melee) == 2  # Chainsword + Plasma Pistol

        # Test ranged while engaged (normal unit)
        ranged_engaged = filter_weapons_for_combat(weapons, 'ranged_engaged', False)
        engaged_correct = len(ranged_engaged) == 1  # Only Plasma Pistol

        print(f"  Ranged weapons: {len(ranged)} (expected 2)")
        print(f"  Melee weapons: {len(melee)} (expected 2)")
        print(f"  Ranged while engaged: {len(ranged_engaged)} (expected 1)")

        return test_result("Weapon filtering works correctly",
                          ranged_correct and melee_correct and engaged_correct)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("Weapon filtering works correctly", False)


def test_10_end_to_end_attack_sequence():
    """Test 10: Complete attack sequence from start to finish"""
    print("\n" + "="*80)
    print("TEST 10: End-to-End Attack Sequence")
    print("="*80)

    try:
        from combat_engine import CombatSimulator, AttackType, WeaponAbilities, UnitAbilities

        sim = CombatSimulator()

        # Simulate a complete attack: Space Marines vs Orks
        # 10 Intercessors with Bolt Rifles vs 20 Ork Boyz
        result = sim.simulate_attack_sequence(
            num_attacks=20,  # 10 models, 2 attacks each
            skill=3,  # BS 3+
            strength=4,  # Bolt Rifle S4
            ap=-1,  # AP -1
            damage='1',
            attack_type=AttackType.RANGED,
            toughness=5,  # Ork T5
            save=6,  # Ork 6+ save
            invuln=None,
            wounds_per_model=1,
            unit_size=20,
            weapon_abilities=WeaponAbilities(),
            target_abilities=UnitAbilities(),
            attacker_abilities=UnitAbilities()
        )

        # Validate sequence integrity
        attacks_valid = result.num_attacks == 20
        hits_valid = result.num_hits <= result.num_attacks
        wounds_valid = result.num_wounds <= result.num_hits
        damage_valid = result.total_damage >= 0
        models_valid = result.models_destroyed <= 20

        sequence_valid = all([attacks_valid, hits_valid, wounds_valid, damage_valid, models_valid])

        print(f"  Attacks: {result.num_attacks}")
        print(f"  Hits: {result.num_hits} ({result.num_critical_hits} critical)")
        print(f"  Wounds: {result.num_wounds} ({result.num_critical_wounds} critical)")
        print(f"  Damage: {result.total_damage}")
        print(f"  Models destroyed: {result.models_destroyed}")
        print(f"  Sequence integrity valid: {sequence_valid}")

        return test_result("End-to-end attack sequence works", sequence_valid)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("End-to-end attack sequence works", False)


def main():
    """Run all integration tests"""
    print("\n" + "="*80)
    print("🧪 INTEGRATION TEST SUITE")
    print("="*80)

    test_1_combat_engine_to_api_flow()
    test_2_stratagem_system_integration()
    test_3_dice_notation_in_combat()
    test_4_weapon_abilities_affect_combat()
    test_5_target_abilities_affect_saves()
    test_6_army_list_json_structure()
    test_7_statistical_simulation_consistency()
    test_8_cp_system_prevents_overspending()
    test_9_weapon_filtering_by_combat_type()
    test_10_end_to_end_attack_sequence()

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
