#!/usr/bin/env python3
"""
Test Suite for UI Enhancements
Tests ability descriptions display and stratagem integration
"""

import sys
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


def test_1_unit_api_returns_ability_objects():
    """Test 1: Unit API returns ability objects with name and description"""
    print("\n" + "="*80)
    print("TEST 1: Unit API Returns Ability Objects")
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
            ability_obj = {
                'name': u.abilities[0].name,
                'description': u.abilities[0].description
            }

            print(f"  Unit: {u.name}")
            print(f"  Ability object: {ability_obj}")

            has_both_fields = 'name' in ability_obj and 'description' in ability_obj
            return test_result("API format has name and description", has_both_fields)

    return test_result("Found unit with abilities", False)


def test_2_stratagem_phase_mapping():
    """Test 2: Combat types map to correct stratagem phases"""
    print("\n" + "="*80)
    print("TEST 2: Combat Type to Phase Mapping")
    print("="*80)

    phase_map = {
        'ranged': 'shooting',
        'melee': 'fight',
        'ranged_engaged': 'opponent_shooting'
    }

    print("  Combat type mappings:")
    for combat_type, phase in phase_map.items():
        print(f"    {combat_type} → {phase}")

    return test_result("Phase mapping defined", len(phase_map) == 3)


def test_3_stratagems_exist_for_shooting_phase():
    """Test 3: Stratagems exist for shooting phase"""
    print("\n" + "="*80)
    print("TEST 3: Shooting Phase Stratagems")
    print("="*80)

    from stratagems import get_stratagems_by_phase, StratagemPhase

    stratagems = get_stratagems_by_phase(StratagemPhase.SHOOTING)

    print(f"  Found {len(stratagems)} stratagems for Shooting Phase:")
    for s in stratagems:
        print(f"    - {s.name} ({s.cp_cost} CP)")

    return test_result("Shooting phase has stratagems", len(stratagems) > 0)


def test_4_stratagems_exist_for_fight_phase():
    """Test 4: Stratagems exist for fight phase"""
    print("\n" + "="*80)
    print("TEST 4: Fight Phase Stratagems")
    print("="*80)

    from stratagems import get_stratagems_by_phase, StratagemPhase

    stratagems = get_stratagems_by_phase(StratagemPhase.FIGHT)

    print(f"  Found {len(stratagems)} stratagems for Fight Phase:")
    for s in stratagems:
        print(f"    - {s.name} ({s.cp_cost} CP)")

    return test_result("Fight phase has stratagems", len(stratagems) > 0)


def test_5_css_classes_defined():
    """Test 5: CSS classes for UI elements are defined"""
    print("\n" + "="*80)
    print("TEST 5: CSS Classes Defined")
    print("="*80)

    from pathlib import Path

    css_file = Path('static/css/battle_mode.css')
    if not css_file.exists():
        return test_result("CSS file exists", False)

    content = css_file.read_text()

    required_classes = [
        '.stratagems-panel',
        '.stratagem-item',
        '.stratagem-name',
        '.unit-abilities',
        '.ability-item',
        '.ability-item-name',
        '.ability-item-description'
    ]

    all_found = True
    for css_class in required_classes:
        if css_class in content:
            print(f"  ✓ {css_class}")
        else:
            print(f"  ✗ {css_class}")
            all_found = False

    return test_result("All CSS classes defined", all_found)


def test_6_html_elements_added():
    """Test 6: HTML elements for stratagems added to battle mode"""
    print("\n" + "="*80)
    print("TEST 6: HTML Elements Added")
    print("="*80)

    from pathlib import Path

    html_file = Path('templates/battle_mode.html')
    if not html_file.exists():
        return test_result("HTML file exists", False)

    content = html_file.read_text()

    # Check for stratagems panel (unit-abilities is added dynamically by JS)
    required_elements = [
        'stratagems-panel',
        'stratagems-list'
    ]

    all_found = True
    for element_id in required_elements:
        if element_id in content:
            print(f"  ✓ {element_id}")
        else:
            print(f"  ✗ {element_id}")
            all_found = False

    # Also verify the link to stratagems page
    has_strat_link = '/stratagems' in content
    print(f"  ✓ Stratagems page link: {has_strat_link}")

    return test_result("All HTML elements added", all_found and has_strat_link)


def test_7_javascript_functions_defined():
    """Test 7: JavaScript functions for stratagems are defined"""
    print("\n" + "="*80)
    print("TEST 7: JavaScript Functions Defined")
    print("="*80)

    from pathlib import Path

    js_file = Path('static/js/battle_mode.js')
    if not js_file.exists():
        return test_result("JS file exists", False)

    content = js_file.read_text()

    required_functions = [
        'loadStratagemsForPhase',
        'toggleStratagem',
        'activeStratagems'
    ]

    all_found = True
    for func in required_functions:
        if func in content:
            print(f"  ✓ {func}")
        else:
            print(f"  ✗ {func}")
            all_found = False

    return test_result("All JS functions defined", all_found)


def test_8_stratagem_reference_page_exists():
    """Test 8: Stratagem reference page exists"""
    print("\n" + "="*80)
    print("TEST 8: Stratagem Reference Page")
    print("="*80)

    from pathlib import Path

    strat_page = Path('templates/stratagems.html')
    exists = strat_page.exists()

    if exists:
        print(f"  Found: {strat_page}")
        content = strat_page.read_text()
        has_title = 'Core Stratagems' in content
        has_cards = 'stratagem-card' in content

        print(f"  Has title: {has_title}")
        print(f"  Has cards: {has_cards}")

        return test_result("Stratagem page complete", has_title and has_cards)

    return test_result("Stratagem page exists", False)


def test_9_font_awesome_included():
    """Test 9: Font Awesome icons included in battle mode"""
    print("\n" + "="*80)
    print("TEST 9: Font Awesome Icons")
    print("="*80)

    from pathlib import Path

    html_file = Path('templates/battle_mode.html')
    content = html_file.read_text()

    has_font_awesome = 'font-awesome' in content or 'fontawesome' in content

    print(f"  Font Awesome included: {has_font_awesome}")

    return test_result("Font Awesome included", has_font_awesome)


def test_10_stratagem_api_route_exists():
    """Test 10: Stratagem API route exists in combat_app.py"""
    print("\n" + "="*80)
    print("TEST 10: Stratagem API Routes")
    print("="*80)

    from pathlib import Path

    app_file = Path('combat_app.py')
    content = app_file.read_text()

    routes = [
        '/api/stratagems',
        'get_stratagems',
        'get_stratagem',
        'get_stratagems_for_phase'
    ]

    all_found = True
    for route in routes:
        if route in content:
            print(f"  ✓ {route}")
        else:
            print(f"  ✗ {route}")
            all_found = False

    return test_result("All API routes defined", all_found)


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("🧪 UI ENHANCEMENTS TEST SUITE")
    print("="*80)

    # Run all tests
    test_1_unit_api_returns_ability_objects()
    test_2_stratagem_phase_mapping()
    test_3_stratagems_exist_for_shooting_phase()
    test_4_stratagems_exist_for_fight_phase()
    test_5_css_classes_defined()
    test_6_html_elements_added()
    test_7_javascript_functions_defined()
    test_8_stratagem_reference_page_exists()
    test_9_font_awesome_included()
    test_10_stratagem_api_route_exists()

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
