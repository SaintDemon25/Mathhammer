#!/usr/bin/env python3
"""
Test Suite for Abilities and Stratagems
Tests ability descriptions display and stratagems system
"""

import sys
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.WARNING)

# Test counters
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


def test_1_unit_abilities_have_descriptions():
    """Test 1: Unit abilities are parsed with descriptions"""
    print("\n" + "="*80)
    print("TEST 1: Unit Abilities Have Descriptions")
    print("="*80)

    from enhanced_parser import EnhancedBSDataParser
    from pathlib import Path

    dataset_path = Path('datasets')
    if not dataset_path.exists():
        return test_result("Dataset exists", False)

    parser = EnhancedBSDataParser()
    catalog = parser.load_dataset_enhanced(str(dataset_path))

    # Find unit with abilities that have descriptions
    unit_with_described_ability = None
    for u in catalog.units.values():
        for ability in u.abilities:
            if ability.description and len(ability.description) > 10:
                unit_with_described_ability = u
                print(f"  Found: {u.name}")
                print(f"  Ability: {ability.name}")
                print(f"  Description: {ability.description[:100]}...")
                break
        if unit_with_described_ability:
            break

    return test_result("Unit abilities have descriptions", unit_with_described_ability is not None)


def test_2_ability_model_structure():
    """Test 2: Ability model has correct structure"""
    print("\n" + "="*80)
    print("TEST 2: Ability Model Structure")
    print("="*80)

    from mathhammer.models import Ability

    ability = Ability(
        name="Oath of Moment",
        description="Each time this unit's ranged weapons target their Oath of Moment target, you can re-roll the Hit roll.",
        keywords=["Strategic"]
    )

    print(f"  Name: {ability.name}")
    print(f"  Description: {ability.description}")
    print(f"  Keywords: {ability.keywords}")

    has_required_fields = (
        hasattr(ability, 'name') and
        hasattr(ability, 'description') and
        hasattr(ability, 'keywords')
    )

    return test_result("Ability model structure correct", has_required_fields)


def test_3_stratagems_loaded():
    """Test 3: Core stratagems are loaded"""
    print("\n" + "="*80)
    print("TEST 3: Core Stratagems Loaded")
    print("="*80)

    from stratagems import get_core_stratagems

    stratagems = get_core_stratagems()
    print(f"  Total core stratagems: {len(stratagems)}")

    # Should have 11 core stratagems in 10th edition
    expected_count = 11
    return test_result(f"Has {expected_count} core stratagems", len(stratagems) == expected_count)


def test_4_command_reroll_stratagem():
    """Test 4: Command Re-roll stratagem exists"""
    print("\n" + "="*80)
    print("TEST 4: Command Re-roll Stratagem")
    print("="*80)

    from stratagems import get_stratagem_by_id

    strat = get_stratagem_by_id("command_reroll")
    if not strat:
        return test_result("Command Re-roll exists", False)

    print(f"  Name: {strat.name}")
    print(f"  CP Cost: {strat.cp_cost}")
    print(f"  Phase: {strat.phase.value}")
    print(f"  Description: {strat.description[:80]}...")

    is_valid = (
        strat.cp_cost == 1 and
        strat.name == "Command Re-roll" and
        len(strat.description) > 0
    )

    return test_result("Command Re-roll has correct data", is_valid)


def test_5_fire_overwatch_stratagem():
    """Test 5: Fire Overwatch stratagem exists"""
    print("\n" + "="*80)
    print("TEST 5: Fire Overwatch Stratagem")
    print("="*80)

    from stratagems import get_stratagem_by_id

    strat = get_stratagem_by_id("fire_overwatch")
    if not strat:
        return test_result("Fire Overwatch exists", False)

    print(f"  Name: {strat.name}")
    print(f"  CP Cost: {strat.cp_cost}")
    print(f"  Effect: {strat.effect}")

    is_valid = (
        strat.cp_cost == 1 and
        strat.effect == "overwatch_shooting"
    )

    return test_result("Fire Overwatch has correct data", is_valid)


def test_6_go_to_ground_stratagem():
    """Test 6: Go to Ground stratagem provides cover"""
    print("\n" + "="*80)
    print("TEST 6: Go to Ground Stratagem")
    print("="*80)

    from stratagems import get_stratagem_by_id, apply_stratagem_to_combat

    strat = get_stratagem_by_id("go_to_ground")
    if not strat:
        return test_result("Go to Ground exists", False)

    # Test application
    combat_params = {
        'save': 3,
        'invuln': None
    }

    modified_params = apply_stratagem_to_combat("go_to_ground", combat_params)

    print(f"  Original: save=3+, invuln=None")
    print(f"  After stratagem: save=3+, invuln={modified_params.get('invuln')}, cover={modified_params.get('has_cover')}")

    provides_effects = (
        modified_params.get('has_cover') == True and
        modified_params.get('invuln') == 6
    )

    return test_result("Go to Ground provides cover + 6++ save", provides_effects)


def test_7_stratagems_by_phase():
    """Test 7: Get stratagems by phase"""
    print("\n" + "="*80)
    print("TEST 7: Stratagems by Phase")
    print("="*80)

    from stratagems import get_stratagems_by_phase, StratagemPhase

    shooting_strats = get_stratagems_by_phase(StratagemPhase.SHOOTING)
    fight_strats = get_stratagems_by_phase(StratagemPhase.FIGHT)

    print(f"  Shooting phase stratagems: {len(shooting_strats)}")
    for s in shooting_strats:
        print(f"    - {s.name}")

    print(f"  Fight phase stratagems: {len(fight_strats)}")
    for s in fight_strats:
        print(f"    - {s.name}")

    has_stratagems = len(shooting_strats) > 0 and len(fight_strats) > 0

    return test_result("Stratagems filtered by phase", has_stratagems)


def test_8_heroic_intervention_cost():
    """Test 8: Heroic Intervention costs 2 CP"""
    print("\n" + "="*80)
    print("TEST 8: Heroic Intervention Cost")
    print("="*80)

    from stratagems import get_stratagem_by_id

    strat = get_stratagem_by_id("heroic_intervention")
    if not strat:
        return test_result("Heroic Intervention exists", False)

    print(f"  Name: {strat.name}")
    print(f"  CP Cost: {strat.cp_cost}")

    return test_result("Heroic Intervention costs 2 CP", strat.cp_cost == 2)


def test_9_counter_offensive_cost():
    """Test 9: Counter-Offensive costs 2 CP"""
    print("\n" + "="*80)
    print("TEST 9: Counter-Offensive Cost")
    print("="*80)

    from stratagems import get_stratagem_by_id

    strat = get_stratagem_by_id("counter_offensive")
    if not strat:
        return test_result("Counter-Offensive exists", False)

    print(f"  Name: {strat.name}")
    print(f"  CP Cost: {strat.cp_cost}")

    return test_result("Counter-Offensive costs 2 CP", strat.cp_cost == 2)


def test_10_stratagem_phases():
    """Test 10: Stratagems have correct phases"""
    print("\n" + "="*80)
    print("TEST 10: Stratagem Phases")
    print("="*80)

    from stratagems import get_core_stratagems, StratagemPhase

    stratagems = get_core_stratagems()

    # Check specific stratagems have correct phases
    phase_checks = {
        'fire_overwatch': StratagemPhase.OPPONENT_MOVEMENT,
        'go_to_ground': StratagemPhase.OPPONENT_SHOOTING,
        'tank_shock': StratagemPhase.CHARGE,
        'grenades': StratagemPhase.SHOOTING,
        'heroic_intervention': StratagemPhase.OPPONENT_CHARGE,
        'counter_offensive': StratagemPhase.FIGHT,
        'epic_challenge': StratagemPhase.FIGHT,
        'insane_bravery': StratagemPhase.COMMAND
    }

    all_correct = True
    for strat in stratagems:
        if strat.id in phase_checks:
            expected_phase = phase_checks[strat.id]
            if strat.phase != expected_phase:
                print(f"  ❌ {strat.name}: expected {expected_phase.value}, got {strat.phase.value}")
                all_correct = False
            else:
                print(f"  ✓ {strat.name}: {strat.phase.value}")

    return test_result("All stratagem phases correct", all_correct)


def test_11_smokescreen_effect():
    """Test 11: Smokescreen applies -1 to hit"""
    print("\n" + "="*80)
    print("TEST 11: Smokescreen Effect")
    print("="*80)

    from stratagems import apply_stratagem_to_combat

    combat_params = {
        'hit_modifier': 0
    }

    modified_params = apply_stratagem_to_combat("smokescreen", combat_params)

    print(f"  Original hit modifier: {combat_params.get('hit_modifier')}")
    print(f"  After Smokescreen: {modified_params.get('hit_modifier')}")

    return test_result("Smokescreen applies -1 to hit", modified_params.get('hit_modifier') == -1)


def test_12_epic_challenge_precision():
    """Test 12: Epic Challenge grants Precision"""
    print("\n" + "="*80)
    print("TEST 12: Epic Challenge Precision")
    print("="*80)

    from stratagems import apply_stratagem_to_combat

    combat_params = {}
    modified_params = apply_stratagem_to_combat("epic_challenge", combat_params)

    print(f"  Precision granted: {modified_params.get('has_precision')}")

    return test_result("Epic Challenge grants Precision", modified_params.get('has_precision') == True)


def test_13_all_stratagems_have_descriptions():
    """Test 13: All stratagems have complete data"""
    print("\n" + "="*80)
    print("TEST 13: All Stratagems Complete")
    print("="*80)

    from stratagems import get_core_stratagems

    stratagems = get_core_stratagems()

    all_complete = True
    for strat in stratagems:
        if not strat.name or not strat.description or not strat.effect:
            print(f"  ❌ {strat.id} missing data")
            all_complete = False
        else:
            print(f"  ✓ {strat.name}")

    return test_result("All stratagems have complete data", all_complete)


def test_14_unit_abilities_api_format():
    """Test 14: Unit abilities API returns correct format"""
    print("\n" + "="*80)
    print("TEST 14: Unit Abilities API Format")
    print("="*80)

    from enhanced_parser import EnhancedBSDataParser
    from pathlib import Path

    dataset_path = Path('datasets')
    if not dataset_path.exists():
        return test_result("Dataset exists", False)

    parser = EnhancedBSDataParser()
    catalog = parser.load_dataset_enhanced(str(dataset_path))

    # Find unit with abilities
    for u in catalog.units.values():
        if len(u.abilities) > 0:
            # Simulate API response format
            unit_abilities = []
            for ability in u.abilities:
                unit_abilities.append({
                    'name': ability.name,
                    'description': ability.description
                })

            print(f"  Unit: {u.name}")
            print(f"  Abilities: {len(unit_abilities)}")
            if len(unit_abilities) > 0:
                print(f"  First ability: {unit_abilities[0]['name']}")
                print(f"  Has description: {len(unit_abilities[0].get('description', '')) > 0}")

            # Check format
            has_correct_format = all(
                'name' in ab and 'description' in ab
                for ab in unit_abilities
            )

            return test_result("API format correct", has_correct_format)

    return test_result("Found unit with abilities", False)


def test_15_stratagem_restrictions():
    """Test 15: Stratagems have restriction text"""
    print("\n" + "="*80)
    print("TEST 15: Stratagem Restrictions")
    print("="*80)

    from stratagems import get_core_stratagems

    stratagems = get_core_stratagems()

    count_with_restrictions = sum(1 for s in stratagems if s.restrictions)
    print(f"  Stratagems with restrictions: {count_with_restrictions}/{len(stratagems)}")

    # Most stratagems should have restrictions
    return test_result("Most stratagems have restrictions", count_with_restrictions >= 8)


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("🧪 ABILITIES AND STRATAGEMS TEST SUITE")
    print("="*80)

    # Run all tests
    test_1_unit_abilities_have_descriptions()
    test_2_ability_model_structure()
    test_3_stratagems_loaded()
    test_4_command_reroll_stratagem()
    test_5_fire_overwatch_stratagem()
    test_6_go_to_ground_stratagem()
    test_7_stratagems_by_phase()
    test_8_heroic_intervention_cost()
    test_9_counter_offensive_cost()
    test_10_stratagem_phases()
    test_11_smokescreen_effect()
    test_12_epic_challenge_precision()
    test_13_all_stratagems_have_descriptions()
    test_14_unit_abilities_api_format()
    test_15_stratagem_restrictions()

    # Summary
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
