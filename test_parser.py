#!/usr/bin/env python3
"""
Test script for BSData parser
Run this to debug parsing issues
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from mathhammer.parser import BSDataParser

# Configure detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(levelname)s - %(name)s - %(message)s'
)

def test_parser():
    """Test the BSData parser"""
    parser = BSDataParser()
    dataset_path = Path('datasets')

    print("=" * 60)
    print("BSData Parser Test")
    print("=" * 60)

    # Check for files
    gst_files = list(dataset_path.glob('*.gst'))
    cat_files = list(dataset_path.glob('*.cat'))

    print(f"\nFound {len(gst_files)} .gst files:")
    for f in gst_files:
        print(f"  - {f.name} ({f.stat().st_size} bytes)")

    print(f"\nFound {len(cat_files)} .cat files:")
    for f in cat_files:
        print(f"  - {f.name} ({f.stat().st_size} bytes)")

    if not gst_files and not cat_files:
        print("\n❌ No .gst or .cat files found in datasets/ directory!")
        print("\nPlease add BSData files. You can:")
        print("1. Download from https://github.com/BSData/wh40k-10e")
        print("2. Run: cd datasets && git clone https://github.com/BSData/wh40k-10e.git temp && mv temp/*.cat temp/*.gst . && rm -rf temp")
        return

    print("\n" + "=" * 60)
    print("Starting parser...")
    print("=" * 60 + "\n")

    try:
        catalog = parser.load_dataset(str(dataset_path))

        print("\n" + "=" * 60)
        print("Parser Results")
        print("=" * 60)
        print(f"\n✓ Total units loaded: {len(catalog.units)}")
        print(f"✓ Total factions: {len(catalog.factions)}")

        if catalog.factions:
            print(f"\nFactions found:")
            for faction in sorted(catalog.factions):
                units_in_faction = len(catalog.get_units_by_faction(faction))
                print(f"  - {faction}: {units_in_faction} units")

        if catalog.units:
            print(f"\nSample units (first 10):")
            for i, unit in enumerate(list(catalog.units.values())[:10]):
                print(f"\n  {i+1}. {unit.name}")
                print(f"     Faction: {unit.faction}")
                print(f"     Profile: {'✓' if unit.unit_profile else '✗'}")
                print(f"     Weapons: {len(unit.weapons)}")

                if unit.unit_profile:
                    print(f"     Stats: M={unit.unit_profile.movement}, T={unit.unit_profile.toughness}, "
                          f"Sv={unit.unit_profile.save}, W={unit.unit_profile.wounds}")

                if unit.weapons:
                    for weapon in unit.weapons[:2]:  # Show first 2 weapons
                        print(f"       - {weapon.name}: Range={weapon.range_value}, "
                              f"A={weapon.attacks}, S={weapon.strength}, AP={weapon.armor_penetration}")
        else:
            print("\n⚠ No units were loaded!")
            print("This could mean:")
            print("  1. The .cat files don't contain recognizable unit data")
            print("  2. The parser needs adjustment for the specific file format")
            print("  3. The files might be corrupted or in an unexpected format")

        return catalog

    except Exception as e:
        print(f"\n❌ Error during parsing: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    test_parser()
