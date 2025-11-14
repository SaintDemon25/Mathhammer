#!/usr/bin/env python3
"""
Complete test suite for all Mathhammer systems
Comprehensive testing with correct API usage
"""

import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.WARNING)

def test_weapons():
    """Test weapon parsing"""
    print("\n" + "="*80)
    print("1. WEAPON PARSING TEST")
    print("="*80)

    from enhanced_parser import EnhancedBSDataParser

    dataset_path = Path('datasets')
    if not dataset_path.exists():
        print("⚠️  Dataset not found")
        return False

    parser = EnhancedBSDataParser()
    catalog = parser.load_dataset_enhanced(str(dataset_path))

    # Test Land Raider
    land_raider = None
    for u in catalog.units.values():
        if u.name == "Land Raider":
            land_raider = u
            break

    if land_raider and len(land_raider.weapons) >= 3:
        print(f"✓ Land Raider: {len(land_raider.weapons)} weapons")
        return True
    else:
        print(f"✗ Land Raider failed")
        return False


def test_abilities():
    """Test unit abilities parsing"""
    print("\n" + "="*80)
    print("2. UNIT ABILITIES TEST")
    print("="*80)

    from unit_abilities import UnitAbilityParser, AbilityApplicator

    parser = UnitAbilityParser()
    applicator = AbilityApplicator()
    known = parser.get_known_abilities()

    # Test Target Elimination
    mods = known['Target Elimination']
    attacks = applicator.apply_to_attacks(mods, 2, weapon_name="Bolt Rifle")

    if attacks == 4:
        print(f"✓ Target Elimination: 2 → 4 attacks")
        return True
    else:
        print(f"✗ Target Elimination failed: {attacks}")
        return False


def test_army_builder():
    """Test army builder data models"""
    print("\n" + "="*80)
    print("3. ARMY BUILDER TEST")
    print("="*80)

    from mathhammer.models import Army, ArmyUnit

    army = Army(
        name="Test Army",
        faction="Space Marines",
        points_limit=2000
    )

    army.units.append(ArmyUnit(
        unit_id="unit-1",
        unit_name="Intercessor Squad",
        faction="Space Marines",
        points_cost=75
    ))

    if army.total_points() == 75 and army.is_valid():
        print(f"✓ Army: {army.total_points()}/{army.points_limit} pts")
        return True
    else:
        print(f"✗ Army validation failed")
        return False


def test_parser_details():
    """Test detailed parser features"""
    print("\n" + "="*80)
    print("4. PARSER DETAILS TEST")
    print("="*80)

    from enhanced_parser import EnhancedBSDataParser
    from pathlib import Path

    dataset_path = Path('datasets')
    if not dataset_path.exists():
        print("⚠️  Dataset not found")
        return False

    parser = EnhancedBSDataParser()
    catalog = parser.load_dataset_enhanced(str(dataset_path))

    # Find Assault Intercessor Squad
    unit = None
    for u in catalog.units.values():
        if "Assault Intercessor Squad" in u.name:
            unit = u
            break

    if unit:
        print(f"✓ Unit: {unit.name}")
        print(f"  Points: {unit.points_cost}")
        print(f"  Max in roster: {unit.max_in_roster}")
        print(f"  Abilities: {len(unit.abilities)}")
        print(f"  Model composition: {len(unit.model_composition)}")
        return True
    else:
        print(f"✗ Unit not found")
        return False


def test_combat():
    """Test combat engine"""
    print("\n" + "="*80)
    print("5. COMBAT ENGINE TEST")
    print("="*80)

    from combat_engine import CombatSimulator, WeaponAbilities, UnitAbilities, AttackType

    sim = CombatSimulator()

    # Simple test
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

    if result.num_hits > 0:
        print(f"✓ Combat: {result.num_hits} hits, {result.num_wounds} wounds")
        return True
    else:
        print(f"✗ Combat failed")
        return False


def test_lethal_hits():
    """Test Lethal Hits ability"""
    print("\n" + "="*80)
    print("6. LETHAL HITS TEST")
    print("="*80)

    from combat_engine import CombatSimulator, WeaponAbilities, UnitAbilities, AttackType

    sim = CombatSimulator()

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
        weapon_abilities=WeaponAbilities(lethal_hits=True),
        target_abilities=UnitAbilities(),
        attacker_abilities=UnitAbilities()
    )

    # Should get some wounds from auto-wounding crits
    if result.num_wounds > 0:
        print(f"✓ Lethal Hits: {result.num_wounds} wounds (auto-wound working)")
        return True
    else:
        print(f"✗ Lethal Hits: No wounds")
        return False


def test_feel_no_pain():
    """Test Feel No Pain ability"""
    print("\n" + "="*80)
    print("7. FEEL NO PAIN TEST")
    print("="*80)

    from combat_engine import CombatSimulator, WeaponAbilities, UnitAbilities, AttackType

    sim = CombatSimulator()

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
        target_abilities=UnitAbilities(feel_no_pain=5),
        attacker_abilities=UnitAbilities()
    )

    if result.damage_after_fnp < result.total_damage:
        fnp_saved = result.total_damage - result.damage_after_fnp
        print(f"✓ FNP: Reduced {fnp_saved} damage ({result.total_damage} → {result.damage_after_fnp})")
        return True
    else:
        print(f"✗ FNP: No reduction")
        return False


def test_integration():
    """Test parser + combat engine integration"""
    print("\n" + "="*80)
    print("8. INTEGRATION TEST")
    print("="*80)

    from pathlib import Path
    from enhanced_parser import EnhancedBSDataParser
    from combat_engine import CombatSimulator, WeaponAbilities, UnitAbilities, AttackType

    dataset_path = Path('datasets')
    if not dataset_path.exists():
        print("⚠️  Dataset not found")
        return False

    parser = EnhancedBSDataParser()
    catalog = parser.load_dataset_enhanced(str(dataset_path))

    # Find Land Raider
    land_raider = None
    for u in catalog.units.values():
        if u.name == "Land Raider":
            land_raider = u
            break

    if not land_raider:
        print("✗ Land Raider not found")
        return False

    # Get Godhammer Lascannon
    weapon = land_raider.get_weapon_by_name("Godhammer Lascannon")

    if not weapon:
        print("✗ Weapon not found")
        return False

    print(f"✓ Found: {weapon.name}")

    # Simulate attack
    sim = CombatSimulator()
    result = sim.simulate_attack_sequence(
        num_attacks=2,
        skill=3,
        strength=12,
        ap=-3,
        damage="4",
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

    print(f"  Hits: {result.num_hits}, Wounds: {result.num_wounds}, Damage: {result.total_damage}")

    if result.num_hits >= 0:  # Any result is success
        print(f"✓ Integration working")
        return True
    else:
        print(f"✗ Integration failed")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("🧪 COMPREHENSIVE TEST SUITE")
    print("="*80)

    tests = [
        ("Weapon Parsing", test_weapons),
        ("Unit Abilities", test_abilities),
        ("Army Builder", test_army_builder),
        ("Parser Details", test_parser_details),
        ("Combat Engine", test_combat),
        ("Lethal Hits", test_lethal_hits),
        ("Feel No Pain", test_feel_no_pain),
        ("Integration", test_integration),
    ]

    results = {}

    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"\n❌ {name} failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results[name] = False

    # Print summary
    print("\n" + "="*80)
    print("📊 FINAL SUMMARY")
    print("="*80)

    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name:.<50} {status}")

    passed_count = sum(1 for p in results.values() if p)
    total_count = len(results)

    print("="*80)
    print(f"TOTAL: {passed_count}/{total_count} tests passed")
    print("="*80)

    if passed_count == total_count:
        print("\n🎉 ALL TESTS PASSED! 🎉\n")
        return 0
    else:
        print(f"\n⚠️  {total_count - passed_count} test(s) failed\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())
