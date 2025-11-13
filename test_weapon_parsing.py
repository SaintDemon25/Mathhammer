#!/usr/bin/env python3
"""
Test script to verify recursive weapon parsing works correctly
Tests specific units mentioned by user: Land Raider and Intercessor Squad
"""

import logging
from pathlib import Path
from enhanced_parser import EnhancedBSDataParser

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_unit_weapons(parser, unit_name: str, expected_min_weapons: int = 1):
    """Test that a unit has weapons loaded"""
    print(f"\n{'='*60}")
    print(f"Testing: {unit_name}")
    print(f"{'='*60}")

    # Find unit by name
    unit = None
    for u in parser.catalog.units.values():
        if unit_name.lower() in u.name.lower():
            unit = u
            break

    if not unit:
        print(f"❌ FAILED: Unit '{unit_name}' not found in catalog")
        return False

    print(f"✓ Found unit: {unit.name}")
    print(f"  ID: {unit.id}")
    print(f"  Faction: {unit.faction}")

    # Check weapons
    weapon_count = len(unit.weapons)
    print(f"\n  Weapons ({weapon_count} total):")

    if weapon_count == 0:
        print(f"  ❌ NO WEAPONS FOUND")
        return False

    for i, weapon in enumerate(unit.weapons, 1):
        print(f"    {i}. {weapon.name} ({weapon.type_name})")

        # Show weapon stats
        chars = weapon.characteristics
        if isinstance(chars, dict):
            stats = []
            for key in ['Range', 'A', 'BS', 'S', 'AP', 'D', 'Keywords']:
                if key in chars:
                    value = chars[key].value if hasattr(chars[key], 'value') else str(chars[key])
                    stats.append(f"{key}={value}")
            print(f"       Stats: {', '.join(stats)}")

    # Check if we have enough weapons
    if weapon_count >= expected_min_weapons:
        print(f"\n✅ PASS: Found {weapon_count} weapons (expected at least {expected_min_weapons})")
        return True
    else:
        print(f"\n❌ FAIL: Only found {weapon_count} weapons (expected at least {expected_min_weapons})")
        return False

def main():
    print("="*60)
    print("WEAPON PARSING TEST")
    print("="*60)

    dataset_path = Path('datasets')

    if not dataset_path.exists():
        print(f"❌ ERROR: Dataset not found at {dataset_path}")
        return

    # Load dataset with enhanced parser
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

    # Test cases
    results = []

    # Test 1: Land Raider (should have multiple weapons)
    # Expected: Godhammer Lascannon, Hunter-killer missile, Armoured tracks, etc.
    results.append(test_unit_weapons(parser, "Land Raider", expected_min_weapons=3))

    # Test 2: Intercessor Squad (should have weapons from nested models)
    # Expected: Bolt Rifle, Astartes Chainsword, Power weapons, etc.
    results.append(test_unit_weapons(parser, "Intercessor Squad", expected_min_weapons=2))

    # Test 3: Check a few more units to ensure general parsing works
    results.append(test_unit_weapons(parser, "Tactical Squad", expected_min_weapons=1))

    # Summary
    print(f"\n\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")

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
