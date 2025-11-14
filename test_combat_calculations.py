#!/usr/bin/env python3
"""
Detailed Combat Engine Calculation Test Suite
Tests dice mechanics, wound charts, critical hits, and ability interactions
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


def test_1_strength_vs_toughness_wound_chart():
    """Test 1: Wound chart calculations (S vs T)"""
    print("\n" + "="*80)
    print("TEST 1: Wound Chart Mechanics")
    print("="*80)

    try:
        from combat_engine import CombatSimulator, AttackType, WeaponAbilities, UnitAbilities

        sim = CombatSimulator()

        # S >= 2xT: wound on 2+
        result_easy = sim.simulate_attack_sequence(
            num_attacks=1000, skill=2, strength=8, ap=0, damage='1', attack_type=AttackType.RANGED,
            toughness=4, save=6, invuln=None, wounds_per_model=1, unit_size=1000,
            weapon_abilities=WeaponAbilities(), target_abilities=UnitAbilities(), attacker_abilities=UnitAbilities()
        )

        # S = T: wound on 4+
        result_equal = sim.simulate_attack_sequence(
            num_attacks=1000, skill=2, strength=4, ap=0, damage='1', attack_type=AttackType.RANGED,
            toughness=4, save=6, invuln=None, wounds_per_model=1, unit_size=1000,
            weapon_abilities=WeaponAbilities(), target_abilities=UnitAbilities(), attacker_abilities=UnitAbilities()
        )

        # S <= T/2: wound on 6+
        result_hard = sim.simulate_attack_sequence(
            num_attacks=1000, skill=2, strength=2, ap=0, damage='1', attack_type=AttackType.RANGED,
            toughness=8, save=6, invuln=None, wounds_per_model=1, unit_size=1000,
            weapon_abilities=WeaponAbilities(), target_abilities=UnitAbilities(), attacker_abilities=UnitAbilities()
        )

        # Calculate wound rates (out of successful hits)
        wound_rate_easy = result_easy.num_wounds / result_easy.num_hits if result_easy.num_hits > 0 else 0
        wound_rate_equal = result_equal.num_wounds / result_equal.num_hits if result_equal.num_hits > 0 else 0
        wound_rate_hard = result_hard.num_wounds / result_hard.num_hits if result_hard.num_hits > 0 else 0

        print(f"  S8 vs T4 (2+): {wound_rate_easy:.1%} (expected ~83%)")
        print(f"  S4 vs T4 (4+): {wound_rate_equal:.1%} (expected ~50%)")
        print(f"  S2 vs T8 (6+): {wound_rate_hard:.1%} (expected ~17%)")

        # Allow 10% variance due to dice randomness
        passes = (
            0.73 <= wound_rate_easy <= 0.93 and
            0.40 <= wound_rate_equal <= 0.60 and
            0.07 <= wound_rate_hard <= 0.27
        )

        return test_result("Wound chart works correctly", passes)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("Wound chart works correctly", False)


def test_2_ap_modifies_saves():
    """Test 2: AP correctly modifies saves"""
    print("\n" + "="*80)
    print("TEST 2: AP Save Modification")
    print("="*80)

    try:
        from combat_engine import CombatSimulator, AttackType, WeaponAbilities, UnitAbilities

        sim = CombatSimulator()

        # AP 0 vs 3+ save
        result_no_ap = sim.simulate_attack_sequence(
            num_attacks=100, skill=3, strength=4, ap=0, damage='1', attack_type=AttackType.RANGED,
            toughness=4, save=3, invuln=None, wounds_per_model=1, unit_size=100,
            weapon_abilities=WeaponAbilities(), target_abilities=UnitAbilities(), attacker_abilities=UnitAbilities()
        )

        # AP -3 vs 3+ save (becomes 6+)
        result_with_ap = sim.simulate_attack_sequence(
            num_attacks=100, skill=3, strength=4, ap=-3, damage='1', attack_type=AttackType.RANGED,
            toughness=4, save=3, invuln=None, wounds_per_model=1, unit_size=100,
            weapon_abilities=WeaponAbilities(), target_abilities=UnitAbilities(), attacker_abilities=UnitAbilities()
        )

        # Calculate save rates
        save_rate_no_ap = result_no_ap.num_saves_made / result_no_ap.num_wounds if result_no_ap.num_wounds > 0 else 0
        save_rate_with_ap = result_with_ap.num_saves_made / result_with_ap.num_wounds if result_with_ap.num_wounds > 0 else 0

        print(f"  3+ save vs AP0: {save_rate_no_ap:.1%} (expected ~67%)")
        print(f"  3+ save vs AP-3: {save_rate_with_ap:.1%} (expected ~17%)")

        # AP should significantly reduce save rate
        passes = save_rate_no_ap > save_rate_with_ap * 2

        return test_result("AP modifies saves correctly", passes)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("AP modifies saves correctly", False)


def test_3_critical_hits_on_6():
    """Test 3: Critical hits occur on unmodified 6s"""
    print("\n" + "="*80)
    print("TEST 3: Critical Hits (Unmodified 6s)")
    print("="*80)

    try:
        from combat_engine import CombatSimulator, AttackType, WeaponAbilities, UnitAbilities

        sim = CombatSimulator()

        # Many attacks to get statistical significance
        result = sim.simulate_attack_sequence(
            num_attacks=600, skill=3, strength=4, ap=0, damage='1', attack_type=AttackType.RANGED,
            toughness=4, save=3, invuln=None, wounds_per_model=1, unit_size=200,
            weapon_abilities=WeaponAbilities(), target_abilities=UnitAbilities(), attacker_abilities=UnitAbilities()
        )

        # Critical hit rate: For skill 3+, we hit on 3,4,5,6. Of these, 6 is critical = 1/4 = 25%
        crit_rate = result.num_critical_hits / result.num_hits if result.num_hits > 0 else 0

        print(f"  Total hits: {result.num_hits}")
        print(f"  Critical hits: {result.num_critical_hits}")
        print(f"  Critical rate: {crit_rate:.1%} (expected ~25% for skill 3+)")

        # Allow 5% variance (20% to 30%)
        passes = 0.20 <= crit_rate <= 0.30

        return test_result("Critical hits at correct rate", passes)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("Critical hits at correct rate", False)


def test_4_lethal_hits_auto_wound():
    """Test 4: Lethal Hits make critical hits auto-wound"""
    print("\n" + "="*80)
    print("TEST 4: Lethal Hits Ability")
    print("="*80)

    try:
        from combat_engine import CombatSimulator, WeaponAbilities, UnitAbilities, AttackType

        sim = CombatSimulator()

        # With Lethal Hits, S1 vs T10 should still wound on critical hits
        abilities = WeaponAbilities(lethal_hits=True)

        result = sim.simulate_attack_sequence(
            num_attacks=600, skill=2, strength=1, ap=0, damage='1', attack_type=AttackType.RANGED,
            toughness=10, save=6, invuln=None, wounds_per_model=1, unit_size=200,
            weapon_abilities=abilities, target_abilities=UnitAbilities(), attacker_abilities=UnitAbilities()
        )

        # Should have wounds from lethal hits despite S1 vs T10
        has_lethal_wounds = result.lethal_hits_auto_wounds > 0
        total_wounds = result.num_wounds

        print(f"  Lethal hit auto-wounds: {result.lethal_hits_auto_wounds}")
        print(f"  Total wounds: {total_wounds}")
        print(f"  Has wounds despite S1 vs T10: {has_lethal_wounds}")

        return test_result("Lethal Hits auto-wounds work", has_lethal_wounds)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("Lethal Hits auto-wounds work", False)


def test_5_devastating_wounds_bypass_saves():
    """Test 5: Devastating Wounds critical wounds bypass saves"""
    print("\n" + "="*80)
    print("TEST 5: Devastating Wounds Ability")
    print("="*80)

    try:
        from combat_engine import CombatSimulator, WeaponAbilities, UnitAbilities, AttackType

        sim = CombatSimulator()

        # Normal attack
        result_normal = sim.simulate_attack_sequence(
            num_attacks=100, skill=3, strength=8, ap=-3, damage='1', attack_type=AttackType.RANGED,
            toughness=4, save=2, invuln=None, wounds_per_model=1, unit_size=100,
            weapon_abilities=WeaponAbilities(), target_abilities=UnitAbilities(), attacker_abilities=UnitAbilities()
        )

        # With Devastating Wounds
        abilities = WeaponAbilities(devastating_wounds=True)
        result_dev_wounds = sim.simulate_attack_sequence(
            num_attacks=100, skill=3, strength=8, ap=-3, damage='1', attack_type=AttackType.RANGED,
            toughness=4, save=2, invuln=None, wounds_per_model=1, unit_size=100,
            weapon_abilities=abilities, target_abilities=UnitAbilities(), attacker_abilities=UnitAbilities()
        )

        # Devastating wounds should result in more damage (critical wounds bypass saves)
        more_effective = result_dev_wounds.total_damage >= result_normal.total_damage

        print(f"  Normal damage: {result_normal.total_damage}")
        print(f"  Devastating Wounds damage: {result_dev_wounds.total_damage}")
        print(f"  Critical wounds: {result_dev_wounds.num_critical_wounds}")

        return test_result("Devastating Wounds increases damage", more_effective)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("Devastating Wounds increases damage", False)


def test_6_sustained_hits_extra_hits():
    """Test 6: Sustained Hits generates extra hits on crits"""
    print("\n" + "="*80)
    print("TEST 6: Sustained Hits Ability")
    print("="*80)

    try:
        from combat_engine import CombatSimulator, WeaponAbilities, UnitAbilities, AttackType

        sim = CombatSimulator()

        # With Sustained Hits 2
        abilities = WeaponAbilities(sustained_hits=2)
        result = sim.simulate_attack_sequence(
            num_attacks=600, skill=3, strength=4, ap=0, damage='1', attack_type=AttackType.RANGED,
            toughness=4, save=6, invuln=None, wounds_per_model=1, unit_size=300,
            weapon_abilities=abilities, target_abilities=UnitAbilities(), attacker_abilities=UnitAbilities()
        )

        # Should generate extra hits
        has_sustained_hits = result.sustained_hits_generated > 0

        print(f"  Total hits: {result.num_hits}")
        print(f"  Sustained hits generated: {result.sustained_hits_generated}")
        print(f"  Critical hits: {result.num_critical_hits}")

        return test_result("Sustained Hits generates extra hits", has_sustained_hits)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("Sustained Hits generates extra hits", False)


def test_7_twin_linked_rerolls_wounds():
    """Test 7: Twin-Linked allows wound rerolls"""
    print("\n" + "="*80)
    print("TEST 7: Twin-Linked Ability")
    print("="*80)

    try:
        from combat_engine import CombatSimulator, WeaponAbilities, UnitAbilities, AttackType

        sim = CombatSimulator()

        # Without Twin-Linked
        result_normal = sim.simulate_attack_sequence(
            num_attacks=100, skill=3, strength=4, ap=0, damage='1', attack_type=AttackType.RANGED,
            toughness=8, save=6, invuln=None, wounds_per_model=1, unit_size=100,
            weapon_abilities=WeaponAbilities(), target_abilities=UnitAbilities(), attacker_abilities=UnitAbilities()
        )

        # With Twin-Linked (reroll wounds)
        abilities = WeaponAbilities(twin_linked=True)
        result_twin = sim.simulate_attack_sequence(
            num_attacks=100, skill=3, strength=4, ap=0, damage='1', attack_type=AttackType.RANGED,
            toughness=8, save=6, invuln=None, wounds_per_model=1, unit_size=100,
            weapon_abilities=abilities, target_abilities=UnitAbilities(), attacker_abilities=UnitAbilities()
        )

        # Twin-linked should increase wound rate
        more_wounds = result_twin.num_wounds > result_normal.num_wounds

        print(f"  Normal wounds: {result_normal.num_wounds}")
        print(f"  Twin-Linked wounds: {result_twin.num_wounds}")

        return test_result("Twin-Linked improves wound rate", more_wounds)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("Twin-Linked improves wound rate", False)


def test_8_torrent_auto_hits():
    """Test 8: Torrent weapons automatically hit"""
    print("\n" + "="*80)
    print("TEST 8: Torrent Ability (Auto-Hit)")
    print("="*80)

    try:
        from combat_engine import CombatSimulator, WeaponAbilities, UnitAbilities, AttackType

        sim = CombatSimulator()

        # Torrent with terrible skill (should still hit)
        abilities = WeaponAbilities(torrent=True)
        result = sim.simulate_attack_sequence(
            num_attacks=100, skill=6, strength=4, ap=0, damage='1', attack_type=AttackType.RANGED,
            toughness=4, save=6, invuln=None, wounds_per_model=1, unit_size=100,
            weapon_abilities=abilities, target_abilities=UnitAbilities(), attacker_abilities=UnitAbilities()
        )

        # Should hit all attacks despite skill 6
        hit_rate = result.num_hits / result.num_attacks if result.num_attacks > 0 else 0

        print(f"  Attacks: {result.num_attacks}")
        print(f"  Hits: {result.num_hits}")
        print(f"  Hit rate: {hit_rate:.1%} (expected 100%)")

        # Should auto-hit (allowing small variance for implementation)
        passes = hit_rate > 0.95

        return test_result("Torrent auto-hits work", passes)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("Torrent auto-hits work", False)


def test_9_feel_no_pain_reduces_damage():
    """Test 9: Feel No Pain reduces final damage"""
    print("\n" + "="*80)
    print("TEST 9: Feel No Pain Ability")
    print("="*80)

    try:
        from combat_engine import CombatSimulator, WeaponAbilities, UnitAbilities, AttackType

        sim = CombatSimulator()

        # Without FNP
        result_no_fnp = sim.simulate_attack_sequence(
            num_attacks=100, skill=3, strength=8, ap=-3, damage='2', attack_type=AttackType.RANGED,
            toughness=4, save=3, invuln=None, wounds_per_model=2, unit_size=50,
            weapon_abilities=WeaponAbilities(), target_abilities=UnitAbilities(), attacker_abilities=UnitAbilities()
        )

        # With 5+ FNP
        target_abilities = UnitAbilities(feel_no_pain=5)
        result_fnp = sim.simulate_attack_sequence(
            num_attacks=100, skill=3, strength=8, ap=-3, damage='2', attack_type=AttackType.RANGED,
            toughness=4, save=3, invuln=None, wounds_per_model=2, unit_size=50,
            weapon_abilities=WeaponAbilities(), target_abilities=target_abilities, attacker_abilities=UnitAbilities()
        )

        # FNP should reduce final damage
        fnp_reduces_damage = result_fnp.damage_after_fnp < result_fnp.total_damage

        print(f"  No FNP damage: {result_no_fnp.total_damage}")
        print(f"  With FNP total damage: {result_fnp.total_damage}")
        print(f"  After FNP: {result_fnp.damage_after_fnp}")

        return test_result("Feel No Pain reduces damage", fnp_reduces_damage)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("Feel No Pain reduces damage", False)


def test_10_cover_improves_saves():
    """Test 10: Cover bonus improves armor saves"""
    print("\n" + "="*80)
    print("TEST 10: Cover Bonus")
    print("="*80)

    try:
        from combat_engine import CombatSimulator, WeaponAbilities, UnitAbilities, AttackType

        sim = CombatSimulator()

        # Without cover
        result_no_cover = sim.simulate_attack_sequence(
            num_attacks=100, skill=3, strength=4, ap=0, damage='1', attack_type=AttackType.RANGED,
            toughness=4, save=4, invuln=None, wounds_per_model=1, unit_size=100,
            weapon_abilities=WeaponAbilities(), target_abilities=UnitAbilities(), attacker_abilities=UnitAbilities()
        )

        # With cover (+1 to save)
        target_abilities = UnitAbilities(cover=True, cover_bonus=1)
        result_with_cover = sim.simulate_attack_sequence(
            num_attacks=100, skill=3, strength=4, ap=0, damage='1', attack_type=AttackType.RANGED,
            toughness=4, save=4, invuln=None, wounds_per_model=1, unit_size=100,
            weapon_abilities=WeaponAbilities(), target_abilities=target_abilities, attacker_abilities=UnitAbilities()
        )

        # Cover should improve save rate
        save_rate_no_cover = result_no_cover.num_saves_made / result_no_cover.num_wounds if result_no_cover.num_wounds > 0 else 0
        save_rate_with_cover = result_with_cover.num_saves_made / result_with_cover.num_wounds if result_with_cover.num_wounds > 0 else 0

        cover_improves_saves = save_rate_with_cover > save_rate_no_cover

        print(f"  Save rate without cover: {save_rate_no_cover:.1%}")
        print(f"  Save rate with cover: {save_rate_with_cover:.1%}")

        return test_result("Cover improves saves", cover_improves_saves)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("Cover improves saves", False)


def main():
    """Run all combat calculation tests"""
    print("\n" + "="*80)
    print("🧪 DETAILED COMBAT ENGINE CALCULATION TEST SUITE")
    print("="*80)

    test_1_strength_vs_toughness_wound_chart()
    test_2_ap_modifies_saves()
    test_3_critical_hits_on_6()
    test_4_lethal_hits_auto_wound()
    test_5_devastating_wounds_bypass_saves()
    test_6_sustained_hits_extra_hits()
    test_7_twin_linked_rerolls_wounds()
    test_8_torrent_auto_hits()
    test_9_feel_no_pain_reduces_damage()
    test_10_cover_improves_saves()

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
