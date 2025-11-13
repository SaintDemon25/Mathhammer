#!/usr/bin/env python3
"""
Test script to verify army builder parser features
Tests model composition, constraints, weapon options, and abilities
"""

import logging
from pathlib import Path
from enhanced_parser import EnhancedBSDataParser

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_unit_details(parser, unit_name: str):
    """Test detailed unit parsing including model composition"""
    print(f"\n{'='*80}")
    print(f"Testing: {unit_name}")
    print(f"{'='*80}")

    # Find unit by name
    unit = None
    for u in parser.catalog.units.values():
        if unit_name.lower() in u.name.lower():
            unit = u
            break

    if not unit:
        print(f"❌ FAILED: Unit '{unit_name}' not found")
        return False

    print(f"✓ Found unit: {unit.name}")
    print(f"  ID: {unit.id}")
    print(f"  Faction: {unit.faction}")
    print(f"  Points: {unit.points_cost}")
    print(f"  Max in Roster: {unit.max_in_roster}")

    # Categories
    if unit.categories:
        print(f"\n  Categories: {', '.join(unit.categories[:5])}")

    # Abilities
    print(f"\n  Unit Abilities ({len(unit.abilities)}):")
    for ability in unit.abilities:
        print(f"    • {ability.name}")
        if ability.description:
            desc_preview = ability.description[:100] + "..." if len(ability.description) > 100 else ability.description
            print(f"      {desc_preview}")

    # Model Composition
    print(f"\n  Model Composition ({len(unit.model_composition)} models):")
    for model in unit.model_composition:
        print(f"\n    Model: {model.name}")
        print(f"      Count: {model.min_count}-{model.max_count}")

        # Fixed weapons
        if model.fixed_weapons:
            print(f"      Fixed Weapons:")
            for weapon in model.fixed_weapons:
                print(f"        • {weapon.name}")

        # Weapon option groups
        if model.weapon_groups:
            print(f"      Weapon Option Groups ({len(model.weapon_groups)}):")
            for group in model.weapon_groups:
                print(f"        Group: {group.name} (select {group.min_selections}-{group.max_selections})")
                for option in group.options[:5]:  # Show first 5
                    default_marker = " [DEFAULT]" if option.is_default else ""
                    print(f"          - {option.name}{default_marker}")

    # Regular weapons list
    print(f"\n  All Available Weapons ({len(unit.weapons)}):")
    for i, weapon in enumerate(unit.weapons[:10], 1):  # Show first 10
        print(f"    {i}. {weapon.name} ({weapon.type_name})")

    print(f"\n✅ Unit details extracted successfully")
    return True

def main():
    print("="*80)
    print("ARMY BUILDER PARSER TEST")
    print("="*80)

    dataset_path = Path('datasets')

    if not dataset_path.exists():
        print(f"❌ ERROR: Dataset not found at {dataset_path}")
        return

    # Load dataset
    print(f"\nLoading dataset from: {dataset_path}")
    parser = EnhancedBSDataParser()

    try:
        catalog = parser.load_dataset_enhanced(str(dataset_path))
        print(f"✓ Loaded {len(catalog.units)} units from {len(catalog.factions)} factions")
    except Exception as e:
        print(f"❌ ERROR loading dataset: {e}")
        import traceback
        traceback.print_exc()
        return

    # Test specific units
    results = []

    # Test 1: Intercessor Squad (has model composition)
    results.append(test_unit_details(parser, "Intercessor Squad"))

    # Test 2: Land Raider (vehicle with weapon options)
    results.append(test_unit_details(parser, "Land Raider"))

    # Test 3: Captain (character with options)
    results.append(test_unit_details(parser, "Captain"))

    # Summary
    print(f"\n\n{'='*80}")
    print("TEST SUMMARY")
    print(f"{'='*80}")

    passed = sum(results)
    total = len(results)

    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("✅ ALL TESTS PASSED")
    else:
        print(f"❌ {total - passed} TEST(S) FAILED")

    return passed == total

if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)
