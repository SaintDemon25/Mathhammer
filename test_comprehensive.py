#!/usr/bin/env python3
"""
Comprehensive testing for Warhammer 40k Combat Simulator
Tests all abilities, combinations, and edge cases
"""

from combat_engine import (
    CombatSimulator, WeaponAbilities, UnitAbilities, AttackType
)

def test_basic_combat():
    """Test 1: Basic combat with no abilities"""
    print("\n" + "="*60)
    print("TEST 1: Basic Combat (No Abilities)")
    print("="*60)
    print("10 attacks, BS 3+, S4, AP-1, D1 vs T4, 3+, 2W")

    result = CombatSimulator.simulate_attack_sequence(
        num_attacks=10,
        skill=3,
        strength=4,
        ap=1,
        damage="1",
        attack_type=AttackType.RANGED,
        toughness=4,
        save=3,
        invuln=None,
        wounds_per_model=2,
        unit_size=5,
        weapon_abilities=WeaponAbilities(),
        target_abilities=UnitAbilities(),
        attacker_abilities=UnitAbilities()
    )

    print(f"✓ Attacks: {result.num_attacks}")
    print(f"✓ Hits: {result.num_hits} ({result.num_critical_hits} critical)")
    print(f"✓ Wounds: {result.num_wounds}")
    print(f"✓ Damage: {result.damage_after_fnp}")
    assert result.num_attacks == 10, "Should have 10 attacks"
    print("✓ PASSED")


def test_lethal_hits():
    """Test 2: Lethal Hits ability"""
    print("\n" + "="*60)
    print("TEST 2: Lethal Hits")
    print("="*60)
    print("Critical hits should auto-wound")

    result = CombatSimulator.simulate_attack_sequence(
        num_attacks=30,  # More attacks for statistical significance
        skill=3,
        strength=4,
        ap=0,
        damage="1",
        attack_type=AttackType.RANGED,
        toughness=8,  # High toughness to see auto-wound effect
        save=3,
        invuln=None,
        wounds_per_model=1,
        unit_size=10,
        weapon_abilities=WeaponAbilities(lethal_hits=True),
        target_abilities=UnitAbilities(),
        attacker_abilities=UnitAbilities()
    )

    print(f"✓ Lethal Hits Auto-wounds: {result.lethal_hits_auto_wounds}")
    print(f"✓ Critical Hits: {result.num_critical_hits}")
    assert result.lethal_hits_auto_wounds > 0, "Should have some lethal hits auto-wounds"
    print("✓ PASSED")


def test_devastating_wounds():
    """Test 3: Devastating Wounds ability"""
    print("\n" + "="*60)
    print("TEST 3: Devastating Wounds")
    print("="*60)
    print("Critical wounds should bypass all saves")

    result = CombatSimulator.simulate_attack_sequence(
        num_attacks=30,
        skill=3,
        strength=4,
        ap=0,
        damage="1",
        attack_type=AttackType.RANGED,
        toughness=4,
        save=2,  # Very good save
        invuln=4,  # With invuln
        wounds_per_model=1,
        unit_size=10,
        weapon_abilities=WeaponAbilities(devastating_wounds=True),
        target_abilities=UnitAbilities(),
        attacker_abilities=UnitAbilities()
    )

    print(f"✓ Critical Wounds: {result.num_critical_wounds}")
    print(f"✓ Saves Failed: {result.num_saves_failed}")
    # Critical wounds should bypass saves entirely
    assert result.num_critical_wounds <= result.num_saves_failed, "Critical wounds should bypass saves"
    print("✓ PASSED")


def test_sustained_hits():
    """Test 4: Sustained Hits ability"""
    print("\n" + "="*60)
    print("TEST 4: Sustained Hits")
    print("="*60)
    print("Critical hits should generate additional hits")

    result = CombatSimulator.simulate_attack_sequence(
        num_attacks=30,
        skill=3,
        strength=4,
        ap=0,
        damage="1",
        attack_type=AttackType.RANGED,
        toughness=4,
        save=3,
        invuln=None,
        wounds_per_model=1,
        unit_size=10,
        weapon_abilities=WeaponAbilities(sustained_hits=2),  # Sustained Hits 2
        target_abilities=UnitAbilities(),
        attacker_abilities=UnitAbilities()
    )

    print(f"✓ Critical Hits: {result.num_critical_hits}")
    print(f"✓ Sustained Hits Generated: {result.sustained_hits_generated}")
    print(f"✓ Total Hits: {result.num_hits}")
    assert result.sustained_hits_generated > 0, "Should generate sustained hits"
    print("✓ PASSED")


def test_anti_keyword():
    """Test 5: Anti-X ability"""
    print("\n" + "="*60)
    print("TEST 5: Anti-INFANTRY 4+")
    print("="*60)
    print("Wound rolls of 4+ vs INFANTRY should be critical")

    result = CombatSimulator.simulate_attack_sequence(
        num_attacks=30,
        skill=3,
        strength=4,
        ap=0,
        damage="1",
        attack_type=AttackType.RANGED,
        toughness=4,
        save=3,
        invuln=None,
        wounds_per_model=1,
        unit_size=10,
        weapon_abilities=WeaponAbilities(anti=("INFANTRY", 4)),
        target_abilities=UnitAbilities(keywords={"INFANTRY", "IMPERIUM"}),
        attacker_abilities=UnitAbilities()
    )

    print(f"✓ Wounds: {result.num_wounds}")
    print(f"✓ Critical Wounds: {result.num_critical_wounds}")
    # Should have more critical wounds due to Anti
    assert result.num_critical_wounds > 0, "Should have critical wounds from Anti"
    print("✓ PASSED")


def test_twin_linked():
    """Test 6: Twin-linked (re-roll wounds)"""
    print("\n" + "="*60)
    print("TEST 6: Twin-linked")
    print("="*60)
    print("Should re-roll wound rolls")

    # Run multiple times to see statistical improvement
    results_without = []
    results_with = []

    for _ in range(100):
        result = CombatSimulator.simulate_attack_sequence(
            num_attacks=10,
            skill=3,
            strength=3,  # Lower strength for more failed wounds
            ap=0,
            damage="1",
            attack_type=AttackType.RANGED,
            toughness=5,  # Higher toughness
            save=3,
            invuln=None,
            wounds_per_model=1,
            unit_size=10,
            weapon_abilities=WeaponAbilities(twin_linked=False),
            target_abilities=UnitAbilities(),
            attacker_abilities=UnitAbilities()
        )
        results_without.append(result.num_wounds)

        result = CombatSimulator.simulate_attack_sequence(
            num_attacks=10,
            skill=3,
            strength=3,
            ap=0,
            damage="1",
            attack_type=AttackType.RANGED,
            toughness=5,
            save=3,
            invuln=None,
            wounds_per_model=1,
            unit_size=10,
            weapon_abilities=WeaponAbilities(twin_linked=True),
            target_abilities=UnitAbilities(),
            attacker_abilities=UnitAbilities()
        )
        results_with.append(result.num_wounds)

    avg_without = sum(results_without) / len(results_without)
    avg_with = sum(results_with) / len(results_with)

    print(f"✓ Avg wounds without Twin-linked: {avg_without:.2f}")
    print(f"✓ Avg wounds with Twin-linked: {avg_with:.2f}")
    print(f"✓ Improvement: {((avg_with - avg_without) / avg_without * 100):.1f}%")
    assert avg_with > avg_without, "Twin-linked should improve wounds"
    print("✓ PASSED")


def test_feel_no_pain():
    """Test 7: Feel No Pain"""
    print("\n" + "="*60)
    print("TEST 7: Feel No Pain 5+")
    print("="*60)

    results_without = []
    results_with = []

    for _ in range(100):
        result = CombatSimulator.simulate_attack_sequence(
            num_attacks=20,
            skill=3,
            strength=4,
            ap=0,
            damage="1",
            attack_type=AttackType.RANGED,
            toughness=4,
            save=3,
            invuln=None,
            wounds_per_model=1,
            unit_size=10,
            weapon_abilities=WeaponAbilities(),
            target_abilities=UnitAbilities(feel_no_pain=None),
            attacker_abilities=UnitAbilities()
        )
        results_without.append(result.damage_after_fnp)

        result = CombatSimulator.simulate_attack_sequence(
            num_attacks=20,
            skill=3,
            strength=4,
            ap=0,
            damage="1",
            attack_type=AttackType.RANGED,
            toughness=4,
            save=3,
            invuln=None,
            wounds_per_model=1,
            unit_size=10,
            weapon_abilities=WeaponAbilities(),
            target_abilities=UnitAbilities(feel_no_pain=5),
            attacker_abilities=UnitAbilities()
        )
        results_with.append(result.damage_after_fnp)

    avg_without = sum(results_without) / len(results_without)
    avg_with = sum(results_with) / len(results_with)

    print(f"✓ Avg damage without FNP: {avg_without:.2f}")
    print(f"✓ Avg damage with FNP 5+: {avg_with:.2f}")
    print(f"✓ Damage reduction: {((avg_without - avg_with) / avg_without * 100):.1f}%")
    assert avg_with < avg_without, "FNP should reduce damage"
    print("✓ PASSED")


def test_stealth():
    """Test 8: Stealth (-1 to hit)"""
    print("\n" + "="*60)
    print("TEST 8: Stealth")
    print("="*60)

    results_without = []
    results_with = []

    for _ in range(100):
        result = CombatSimulator.simulate_attack_sequence(
            num_attacks=20,
            skill=3,
            strength=4,
            ap=0,
            damage="1",
            attack_type=AttackType.RANGED,
            toughness=4,
            save=3,
            invuln=None,
            wounds_per_model=1,
            unit_size=10,
            weapon_abilities=WeaponAbilities(),
            target_abilities=UnitAbilities(stealth=False),
            attacker_abilities=UnitAbilities()
        )
        results_without.append(result.num_hits)

        result = CombatSimulator.simulate_attack_sequence(
            num_attacks=20,
            skill=3,
            strength=4,
            ap=0,
            damage="1",
            attack_type=AttackType.RANGED,
            toughness=4,
            save=3,
            invuln=None,
            wounds_per_model=1,
            unit_size=10,
            weapon_abilities=WeaponAbilities(),
            target_abilities=UnitAbilities(stealth=True),
            attacker_abilities=UnitAbilities()
        )
        results_with.append(result.num_hits)

    avg_without = sum(results_without) / len(results_without)
    avg_with = sum(results_with) / len(results_with)

    print(f"✓ Avg hits without Stealth: {avg_without:.2f}")
    print(f"✓ Avg hits with Stealth: {avg_with:.2f}")
    print(f"✓ Hit reduction: {((avg_without - avg_with) / avg_without * 100):.1f}%")
    assert avg_with < avg_without, "Stealth should reduce hits"
    print("✓ PASSED")


def test_cover():
    """Test 9: Cover bonus"""
    print("\n" + "="*60)
    print("TEST 9: Cover (+1 to saves)")
    print("="*60)

    results_without = []
    results_with = []

    for _ in range(100):
        result = CombatSimulator.simulate_attack_sequence(
            num_attacks=20,
            skill=3,
            strength=4,
            ap=1,
            damage="1",
            attack_type=AttackType.RANGED,
            toughness=4,
            save=3,
            invuln=None,
            wounds_per_model=1,
            unit_size=10,
            weapon_abilities=WeaponAbilities(),
            target_abilities=UnitAbilities(cover=False),
            attacker_abilities=UnitAbilities()
        )
        results_without.append(result.num_saves_failed)

        result = CombatSimulator.simulate_attack_sequence(
            num_attacks=20,
            skill=3,
            strength=4,
            ap=1,
            damage="1",
            attack_type=AttackType.RANGED,
            toughness=4,
            save=3,
            invuln=None,
            wounds_per_model=1,
            unit_size=10,
            weapon_abilities=WeaponAbilities(),
            target_abilities=UnitAbilities(cover=True, cover_bonus=1),
            attacker_abilities=UnitAbilities()
        )
        results_with.append(result.num_saves_failed)

    avg_without = sum(results_without) / len(results_without)
    avg_with = sum(results_with) / len(results_with)

    print(f"✓ Avg failed saves without cover: {avg_without:.2f}")
    print(f"✓ Avg failed saves with cover: {avg_with:.2f}")
    print(f"✓ Improvement: {((avg_without - avg_with) / avg_without * 100):.1f}%")
    assert avg_with < avg_without, "Cover should reduce failed saves"
    print("✓ PASSED")


def test_blast():
    """Test 10: Blast ability"""
    print("\n" + "="*60)
    print("TEST 10: Blast")
    print("="*60)

    # Small unit (< 5 models)
    result_small = CombatSimulator.simulate_attack_sequence(
        num_attacks=5,
        skill=3,
        strength=4,
        ap=0,
        damage="1",
        attack_type=AttackType.RANGED,
        toughness=4,
        save=3,
        invuln=None,
        wounds_per_model=1,
        unit_size=3,
        weapon_abilities=WeaponAbilities(blast=True),
        target_abilities=UnitAbilities(),
        attacker_abilities=UnitAbilities()
    )

    # Medium unit (5-9 models)
    result_medium = CombatSimulator.simulate_attack_sequence(
        num_attacks=5,
        skill=3,
        strength=4,
        ap=0,
        damage="1",
        attack_type=AttackType.RANGED,
        toughness=4,
        save=3,
        invuln=None,
        wounds_per_model=1,
        unit_size=7,
        weapon_abilities=WeaponAbilities(blast=True),
        target_abilities=UnitAbilities(),
        attacker_abilities=UnitAbilities()
    )

    # Large unit (10+ models)
    result_large = CombatSimulator.simulate_attack_sequence(
        num_attacks=5,
        skill=3,
        strength=4,
        ap=0,
        damage="1",
        attack_type=AttackType.RANGED,
        toughness=4,
        save=3,
        invuln=None,
        wounds_per_model=1,
        unit_size=15,
        weapon_abilities=WeaponAbilities(blast=True),
        target_abilities=UnitAbilities(),
        attacker_abilities=UnitAbilities()
    )

    print(f"✓ Attacks vs 3 models: {result_small.num_attacks} (base 5)")
    print(f"✓ Attacks vs 7 models: {result_medium.num_attacks} (base 5, +1 for 5-9)")
    print(f"✓ Attacks vs 15 models: {result_large.num_attacks} (base 5, +2 for 10+)")

    assert result_small.num_attacks == 5, "Small unit should have base attacks"
    assert result_medium.num_attacks == 6, "Medium unit should have +1 attack"
    assert result_large.num_attacks == 7, "Large unit should have +2 attacks"
    print("✓ PASSED")


def test_torrent():
    """Test 11: Torrent (auto-hits)"""
    print("\n" + "="*60)
    print("TEST 11: Torrent (Auto-hits)")
    print("="*60)

    result = CombatSimulator.simulate_attack_sequence(
        num_attacks=10,
        skill=6,  # Very bad skill
        strength=4,
        ap=0,
        damage="1",
        attack_type=AttackType.RANGED,
        toughness=4,
        save=3,
        invuln=None,
        wounds_per_model=1,
        unit_size=10,
        weapon_abilities=WeaponAbilities(torrent=True),
        target_abilities=UnitAbilities(),
        attacker_abilities=UnitAbilities()
    )

    print(f"✓ Attacks: {result.num_attacks}")
    print(f"✓ Hits: {result.num_hits}")
    assert result.num_hits == result.num_attacks, "Torrent should auto-hit all attacks"
    print("✓ PASSED")


def test_combination_lethal_sustained():
    """Test 12: Lethal Hits + Sustained Hits combination"""
    print("\n" + "="*60)
    print("TEST 12: Lethal Hits + Sustained Hits 1")
    print("="*60)
    print("Critical hits should auto-wound AND generate extra hit")

    result = CombatSimulator.simulate_attack_sequence(
        num_attacks=30,
        skill=3,
        strength=4,
        ap=0,
        damage="1",
        attack_type=AttackType.RANGED,
        toughness=8,  # High toughness to see effect
        save=3,
        invuln=None,
        wounds_per_model=1,
        unit_size=10,
        weapon_abilities=WeaponAbilities(
            lethal_hits=True,
            sustained_hits=1
        ),
        target_abilities=UnitAbilities(),
        attacker_abilities=UnitAbilities()
    )

    print(f"✓ Critical Hits: {result.num_critical_hits}")
    print(f"✓ Lethal Hits Auto-wounds: {result.lethal_hits_auto_wounds}")
    print(f"✓ Sustained Hits Generated: {result.sustained_hits_generated}")
    print(f"✓ Total Hits: {result.num_hits}")

    assert result.sustained_hits_generated > 0, "Should generate sustained hits"
    assert result.lethal_hits_auto_wounds > 0, "Should have lethal auto-wounds"
    print("✓ PASSED")


def test_combination_devastating_anti():
    """Test 13: Devastating Wounds + Anti combination"""
    print("\n" + "="*60)
    print("TEST 13: Devastating Wounds + Anti-INFANTRY 4+")
    print("="*60)

    result = CombatSimulator.simulate_attack_sequence(
        num_attacks=30,
        skill=3,
        strength=4,
        ap=0,
        damage="1",
        attack_type=AttackType.RANGED,
        toughness=4,
        save=2,  # Very good save
        invuln=4,  # With invuln
        wounds_per_model=1,
        unit_size=10,
        weapon_abilities=WeaponAbilities(
            devastating_wounds=True,
            anti=("INFANTRY", 4)
        ),
        target_abilities=UnitAbilities(keywords={"INFANTRY"}),
        attacker_abilities=UnitAbilities()
    )

    print(f"✓ Wounds: {result.num_wounds}")
    print(f"✓ Critical Wounds: {result.num_critical_wounds}")
    print(f"✓ Saves Failed: {result.num_saves_failed}")
    assert result.num_critical_wounds > 0, "Should have critical wounds from Anti"
    print("✓ PASSED")


def run_all_tests():
    """Run all comprehensive tests"""
    print("\n" + "="*70)
    print("  WARHAMMER 40K COMBAT SIMULATOR - COMPREHENSIVE TEST SUITE")
    print("="*70)

    tests = [
        test_basic_combat,
        test_lethal_hits,
        test_devastating_wounds,
        test_sustained_hits,
        test_anti_keyword,
        test_twin_linked,
        test_feel_no_pain,
        test_stealth,
        test_cover,
        test_blast,
        test_torrent,
        test_combination_lethal_sustained,
        test_combination_devastating_anti
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ ERROR: {e}")
            failed += 1

    print("\n" + "="*70)
    print(f"SUMMARY: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("="*70)

    if failed == 0:
        print("✓ ALL TESTS PASSED!")
    else:
        print(f"✗ {failed} TEST(S) FAILED")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
