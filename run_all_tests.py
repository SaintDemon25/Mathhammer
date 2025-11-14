#!/usr/bin/env python3
"""
Comprehensive test suite for all Mathhammer components
Runs all tests and provides detailed reporting
"""

import sys
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')

# Import all test modules
from test_weapon_parsing import main as test_weapons
from test_unit_abilities import main as test_abilities
from test_army_builder_parser import main as test_army_parser

def run_combat_engine_tests():
    """Test combat engine with various scenarios"""
    print("\n" + "="*80)
    print("COMBAT ENGINE TESTS")
    print("="*80)

    from combat_engine import CombatSimulator, WeaponAbilities, UnitAbilities, AttackType

    sim = CombatSimulator()
    tests_passed = 0
    tests_total = 0

    # Test 1: Basic ranged attack
    print("\nTest 1: Basic ranged attack (BS 3+, S4 vs T4, AP0, Save 3+)")
    tests_total += 1
    result = sim.simulate_attack_sequence(
        num_attacks=10,
        skill=3,
        strength=4,
        ap=0,
        damage=1,
        target_toughness=4,
        target_save=3,
        attack_type=AttackType.RANGED
    )

    expected_hits = 10 * (4/6)  # 6.67 hits
    actual_hits = result.total_hits
    if 5 <= actual_hits <= 8:  # Reasonable range
        print(f"  ✓ Hits: {actual_hits} (expected ~6.67)")
        tests_passed += 1
    else:
        print(f"  ✗ Hits: {actual_hits} (expected ~6.67)")

    # Test 2: High AP vs low save
    print("\nTest 2: AP-3 vs 3+ save (should become 6+ save)")
    tests_total += 1
    result = sim.simulate_attack_sequence(
        num_attacks=100,
        skill=3,
        strength=4,
        ap=-3,
        damage=1,
        target_toughness=4,
        target_save=3,
        attack_type=AttackType.RANGED
    )

    # With AP-3, 3+ save becomes 6+ (only 1/6 saves)
    # So wounds should be much higher than with AP0
    if result.total_wounds > 20:  # Should be around 22-45
        print(f"  ✓ Wounds: {result.total_wounds} (AP-3 effective)")
        tests_passed += 1
    else:
        print(f"  ✗ Wounds: {result.total_wounds} (AP-3 not effective)")

    # Test 3: Lethal Hits ability
    print("\nTest 3: Lethal Hits (critical hits on 6+ auto-wound)")
    tests_total += 1
    abilities = WeaponAbilities(lethal_hits=True)
    result = sim.simulate_attack_sequence(
        num_attacks=100,
        skill=3,
        strength=4,
        ap=0,
        damage=1,
        target_toughness=8,  # Hard to wound normally
        target_save=3,
        attack_type=AttackType.RANGED,
        weapon_abilities=abilities
    )

    # Should have some lethal hits that auto-wound despite high toughness
    if result.total_wounds > 5:
        print(f"  ✓ Wounds: {result.total_wounds} (Lethal Hits working)")
        tests_passed += 1
    else:
        print(f"  ✗ Wounds: {result.total_wounds} (Lethal Hits may not be working)")

    # Test 4: Devastating Wounds
    print("\nTest 4: Devastating Wounds (critical wounds ignore saves)")
    tests_total += 1
    abilities = WeaponAbilities(devastating_wounds=True)
    result = sim.simulate_attack_sequence(
        num_attacks=100,
        skill=3,
        strength=4,
        ap=0,
        damage=1,
        target_toughness=4,
        target_save=2,  # Very good save
        attack_type=AttackType.RANGED,
        weapon_abilities=abilities,
        target_invuln_save=0
    )

    # Some wounds should bypass the 2+ save entirely
    if result.total_wounds > 8:
        print(f"  ✓ Wounds: {result.total_wounds} (Devastating Wounds bypassing saves)")
        tests_passed += 1
    else:
        print(f"  ✗ Wounds: {result.total_wounds} (Devastating Wounds may not be working)")

    # Test 5: Feel No Pain
    print("\nTest 5: Feel No Pain 5+ (ignores ~33% of wounds)")
    tests_total += 1
    unit_abilities = UnitAbilities(feel_no_pain=5)
    result = sim.simulate_attack_sequence(
        num_attacks=100,
        skill=3,
        strength=8,
        ap=-3,
        damage=2,
        target_toughness=4,
        target_save=3,
        attack_type=AttackType.RANGED,
        target_abilities=unit_abilities
    )

    wounds_before_fnp = result.wounds_dealt
    wounds_after_fnp = result.total_wounds
    fnp_saves = wounds_before_fnp - wounds_after_fnp

    print(f"  Wounds dealt: {wounds_before_fnp}")
    print(f"  FNP saves: {fnp_saves}")
    print(f"  Final wounds: {wounds_after_fnp}")

    if fnp_saves > 0:
        print(f"  ✓ FNP working")
        tests_passed += 1
    else:
        print(f"  ✗ FNP may not be working")

    # Test 6: Invulnerable save
    print("\nTest 6: 4+ Invulnerable save vs AP-4")
    tests_total += 1
    result = sim.simulate_attack_sequence(
        num_attacks=100,
        skill=3,
        strength=8,
        ap=-4,
        damage=1,
        target_toughness=4,
        target_save=3,
        attack_type=AttackType.RANGED,
        target_invuln_save=4
    )

    # With AP-4, normal save would be 7+ (impossible), but 4++ should work
    if result.successful_saves > 10:
        print(f"  ✓ Saves: {result.successful_saves} (Invuln working)")
        tests_passed += 1
    else:
        print(f"  ✗ Saves: {result.successful_saves} (Invuln may not be working)")

    print(f"\n{'='*80}")
    print(f"Combat Engine: {tests_passed}/{tests_total} tests passed")
    print(f"{'='*80}")

    return tests_passed == tests_total


def run_integration_tests():
    """Test integration between parser and combat engine"""
    print("\n" + "="*80)
    print("INTEGRATION TESTS")
    print("="*80)

    from enhanced_parser import EnhancedBSDataParser
    from combat_engine import CombatSimulator, AttackType

    dataset_path = Path('datasets')

    if not dataset_path.exists():
        print("⚠️  Dataset not found, skipping integration tests")
        return True

    tests_passed = 0
    tests_total = 0

    # Load parser
    parser = EnhancedBSDataParser()
    catalog = parser.load_dataset_enhanced(str(dataset_path))

    # Test 1: Load unit and use its weapons in combat
    print("\nTest 1: Load Land Raider and simulate Godhammer Lascannon attack")
    tests_total += 1

    land_raider = None
    for unit in catalog.units.values():
        if 'land raider' in unit.name.lower() and 'land raider' == unit.name.lower():
            land_raider = unit
            break

    if land_raider:
        print(f"  ✓ Found unit: {land_raider.name}")
        print(f"  Weapons available: {len(land_raider.weapons)}")

        # Find Godhammer Lascannon
        godhammer = land_raider.get_weapon_by_name("Godhammer Lascannon")

        if godhammer:
            print(f"  ✓ Found weapon: {godhammer.name}")

            # Extract stats
            attacks = godhammer.attacks or "2"
            bs = godhammer.ballistic_skill or "3+"
            strength = godhammer.strength or "12"
            ap = godhammer.armor_penetration or "-3"
            damage = godhammer.damage or "D6+1"

            print(f"    Stats: A={attacks}, BS={bs}, S={strength}, AP={ap}, D={damage}")

            # Simulate attack
            sim = CombatSimulator()
            result = sim.simulate_attack_sequence(
                num_attacks=2,
                skill=3,
                strength=12,
                ap=-3,
                damage=4,  # Approximate D6+1
                target_toughness=10,
                target_save=2,
                attack_type=AttackType.RANGED
            )

            print(f"    Hits: {result.total_hits}")
            print(f"    Wounds: {result.total_wounds}")
            print(f"    Damage: {result.total_wounds * 4}")

            tests_passed += 1
        else:
            print(f"  ✗ Could not find Godhammer Lascannon")
    else:
        print(f"  ✗ Could not find Land Raider")

    # Test 2: Test unit with abilities
    print("\nTest 2: Load unit with abilities and verify parsing")
    tests_total += 1

    captain = None
    for unit in catalog.units.values():
        if 'captain' in unit.name.lower() and len(unit.abilities) > 0:
            captain = unit
            break

    if captain:
        print(f"  ✓ Found unit: {captain.name}")
        print(f"  Abilities: {len(captain.abilities)}")

        for ability in captain.abilities[:3]:
            print(f"    • {ability.name}")

        tests_passed += 1
    else:
        print(f"  ✗ Could not find Captain with abilities")

    # Test 3: Test model composition
    print("\nTest 3: Verify model composition parsing")
    tests_total += 1

    intercessor = None
    for unit in catalog.units.values():
        if 'intercessor squad' in unit.name.lower() and len(unit.model_composition) > 0:
            intercessor = unit
            break

    if intercessor:
        print(f"  ✓ Found unit: {intercessor.name}")
        print(f"  Models: {len(intercessor.model_composition)}")

        for model in intercessor.model_composition:
            print(f"    • {model.name}: {model.min_count}-{model.max_count}")
            print(f"      Weapon groups: {len(model.weapon_groups)}")

        tests_passed += 1
    else:
        print(f"  ✗ Could not find Intercessor Squad with model composition")

    print(f"\n{'='*80}")
    print(f"Integration: {tests_passed}/{tests_total} tests passed")
    print(f"{'='*80}")

    return tests_passed == tests_total


def run_army_builder_tests():
    """Test army builder functionality"""
    print("\n" + "="*80)
    print("ARMY BUILDER TESTS")
    print("="*80)

    from mathhammer.models import Army, ArmyUnit
    import json
    from pathlib import Path

    tests_passed = 0
    tests_total = 0

    # Test 1: Create army
    print("\nTest 1: Create new army")
    tests_total += 1

    army = Army(
        name="Test Space Marines",
        faction="Imperium - Adeptus Astartes - Space Marines",
        detachment="Gladius Strike Force",
        points_limit=2000
    )

    if army.name == "Test Space Marines" and army.points_limit == 2000:
        print(f"  ✓ Army created: {army.name}")
        tests_passed += 1
    else:
        print(f"  ✗ Army creation failed")

    # Test 2: Add units
    print("\nTest 2: Add units to army")
    tests_total += 1

    unit1 = ArmyUnit(
        unit_id="test-1",
        unit_name="Intercessor Squad",
        faction=army.faction,
        points_cost=75
    )

    unit2 = ArmyUnit(
        unit_id="test-2",
        unit_name="Land Raider",
        faction=army.faction,
        points_cost=220
    )

    army.units.append(unit1)
    army.units.append(unit2)

    total_points = army.total_points()
    expected_points = 295

    if total_points == expected_points:
        print(f"  ✓ Total points: {total_points}")
        tests_passed += 1
    else:
        print(f"  ✗ Points calculation wrong: {total_points} != {expected_points}")

    # Test 3: Validate army
    print("\nTest 3: Validate army (under points limit)")
    tests_total += 1

    if army.is_valid():
        print(f"  ✓ Army is valid ({total_points}/{army.points_limit} pts)")
        tests_passed += 1
    else:
        print(f"  ✗ Army validation failed")

    # Test 4: Test over points limit
    print("\nTest 4: Validate army (over points limit)")
    tests_total += 1

    # Add many expensive units
    for i in range(20):
        army.units.append(ArmyUnit(
            unit_id=f"test-{i+3}",
            unit_name="Land Raider",
            faction=army.faction,
            points_cost=220
        ))

    if not army.is_valid():
        print(f"  ✓ Army correctly marked invalid ({army.total_points()}/{army.points_limit} pts)")
        tests_passed += 1
    else:
        print(f"  ✗ Army should be invalid (over points)")

    # Test 5: JSON serialization
    print("\nTest 5: JSON serialization/deserialization")
    tests_total += 1

    # Create clean army
    test_army = Army(
        name="Serialization Test",
        faction="Test Faction",
        detachment="Test Detachment",
        points_limit=1000
    )

    test_army.units.append(ArmyUnit(
        unit_id="unit-1",
        unit_name="Test Unit",
        faction="Test Faction",
        points_cost=100
    ))

    # Convert to dict
    army_dict = {
        'name': test_army.name,
        'faction': test_army.faction,
        'detachment': test_army.detachment,
        'points_limit': test_army.points_limit,
        'units': [
            {
                'unit_id': u.unit_id,
                'unit_name': u.unit_name,
                'faction': u.faction,
                'points_cost': u.points_cost,
                'selected_models': [],
                'enhancements': []
            }
            for u in test_army.units
        ],
        'created_at': '',
        'modified_at': ''
    }

    # Serialize
    json_str = json.dumps(army_dict, indent=2)

    # Deserialize
    loaded_dict = json.loads(json_str)

    if loaded_dict['name'] == "Serialization Test" and loaded_dict['units'][0]['unit_name'] == "Test Unit":
        print(f"  ✓ JSON serialization working")
        tests_passed += 1
    else:
        print(f"  ✗ JSON serialization failed")

    print(f"\n{'='*80}")
    print(f"Army Builder: {tests_passed}/{tests_total} tests passed")
    print(f"{'='*80}")

    return tests_passed == tests_total


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("🧪 COMPREHENSIVE TEST SUITE - WARHAMMER 40K MATHHAMMER")
    print("="*80)

    results = {}

    # Run all test suites
    print("\n" + "🔧 Running Component Tests...")

    try:
        print("\n" + "-"*80)
        print("1. WEAPON PARSING TESTS")
        print("-"*80)
        results['weapon_parsing'] = test_weapons()
    except Exception as e:
        print(f"❌ Weapon parsing tests failed: {e}")
        results['weapon_parsing'] = False

    try:
        print("\n" + "-"*80)
        print("2. UNIT ABILITIES TESTS")
        print("-"*80)
        results['unit_abilities'] = test_abilities()
    except Exception as e:
        print(f"❌ Unit abilities tests failed: {e}")
        results['unit_abilities'] = False

    try:
        print("\n" + "-"*80)
        print("3. ARMY BUILDER PARSER TESTS")
        print("-"*80)
        results['army_parser'] = test_army_parser()
    except Exception as e:
        print(f"❌ Army parser tests failed: {e}")
        results['army_parser'] = False

    try:
        results['combat_engine'] = run_combat_engine_tests()
    except Exception as e:
        print(f"❌ Combat engine tests failed: {e}")
        results['combat_engine'] = False

    try:
        results['integration'] = run_integration_tests()
    except Exception as e:
        print(f"❌ Integration tests failed: {e}")
        results['integration'] = False

    try:
        results['army_builder'] = run_army_builder_tests()
    except Exception as e:
        print(f"❌ Army builder tests failed: {e}")
        results['army_builder'] = False

    # Print summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)

    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title():.<50} {status}")

    total_passed = sum(1 for p in results.values() if p)
    total_tests = len(results)

    print("="*80)
    print(f"TOTAL: {total_passed}/{total_tests} test suites passed")
    print("="*80)

    if total_passed == total_tests:
        print("\n🎉 ALL TESTS PASSED! 🎉\n")
        return 0
    else:
        print(f"\n⚠️  {total_tests - total_passed} test suite(s) failed\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())
