#!/usr/bin/env python3
"""
Test Suite for Weapon Comparison and Unit Composition
Tests the new comparison mode and variable unit size features
"""

import sys
import logging

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


def test_1_unit_size_input_exists():
    """Test 1: Unit size input field exists in HTML"""
    print("\n" + "="*80)
    print("TEST 1: Unit Size Input Field")
    print("="*80)

    try:
        with open('templates/battle_mode.html', 'r') as f:
            content = f.read()

        has_input = 'id="defender-unit-size"' in content
        has_label = 'Defender Unit Size' in content
        has_min_max = 'min="1"' in content and 'max="20"' in content

        print(f"  Has defender-unit-size input: {has_input}")
        print(f"  Has descriptive label: {has_label}")
        print(f"  Has min/max validation: {has_min_max}")

        return test_result("Unit size input exists", has_input and has_label and has_min_max)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("Unit size input exists", False)


def test_2_js_reads_unit_size():
    """Test 2: JavaScript reads unit size from input"""
    print("\n" + "="*80)
    print("TEST 2: JavaScript Reads Unit Size")
    print("="*80)

    try:
        with open('static/js/battle_mode.js', 'r') as f:
            content = f.read()

        reads_value = "document.getElementById('defender-unit-size').value" in content
        uses_in_api = "unit_size: defenderUnitSize" in content

        print(f"  Reads value from input: {reads_value}")
        print(f"  Sends to API: {uses_in_api}")

        return test_result("JavaScript reads unit size", reads_value and uses_in_api)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("JavaScript reads unit size", False)


def test_3_comparison_mode_button_exists():
    """Test 3: Comparison mode toggle button exists"""
    print("\n" + "="*80)
    print("TEST 3: Comparison Mode Button")
    print("="*80)

    try:
        with open('templates/battle_mode.html', 'r') as f:
            content = f.read()

        has_button = 'id="comparison-mode-btn"' in content
        has_toggle_function = 'toggleComparisonMode()' in content
        has_icon = 'fa-balance-scale' in content

        print(f"  Has comparison-mode-btn: {has_button}")
        print(f"  Has toggleComparisonMode function call: {has_toggle_function}")
        print(f"  Has balance scale icon: {has_icon}")

        return test_result("Comparison mode button exists",
                          has_button and has_toggle_function and has_icon)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("Comparison mode button exists", False)


def test_4_js_has_comparison_variables():
    """Test 4: JavaScript has comparison mode variables"""
    print("\n" + "="*80)
    print("TEST 4: Comparison Mode Variables")
    print("="*80)

    try:
        with open('static/js/battle_mode.js', 'r') as f:
            content = f.read()

        has_mode_var = "comparisonMode = false" in content or "let comparisonMode" in content
        has_weapons_array = "selectedWeapons = []" in content or "let selectedWeapons" in content

        print(f"  Has comparisonMode variable: {has_mode_var}")
        print(f"  Has selectedWeapons array: {has_weapons_array}")

        return test_result("Comparison mode variables exist", has_mode_var and has_weapons_array)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("Comparison mode variables exist", False)


def test_5_toggle_comparison_function_exists():
    """Test 5: toggleComparisonMode function exists"""
    print("\n" + "="*80)
    print("TEST 5: Toggle Comparison Function")
    print("="*80)

    try:
        with open('static/js/battle_mode.js', 'r') as f:
            content = f.read()

        has_function = "function toggleComparisonMode()" in content
        toggles_mode = "comparisonMode = !comparisonMode" in content
        updates_button = "btn.innerHTML" in content

        print(f"  Function defined: {has_function}")
        print(f"  Toggles mode variable: {toggles_mode}")
        print(f"  Updates button text: {updates_button}")

        return test_result("toggleComparisonMode function exists",
                          has_function and toggles_mode and updates_button)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("toggleComparisonMode function exists", False)


def test_6_weapon_card_multi_select():
    """Test 6: Weapon cards support multi-select in comparison mode"""
    print("\n" + "="*80)
    print("TEST 6: Weapon Card Multi-Select")
    print("="*80)

    try:
        with open('static/js/battle_mode.js', 'r') as f:
            content = f.read()

        checks_comparison_mode = "if (comparisonMode)" in content
        adds_to_array = "selectedWeapons.push(weapon)" in content
        removes_from_array = "selectedWeapons.splice(index, 1)" in content

        print(f"  Checks comparison mode: {checks_comparison_mode}")
        print(f"  Adds weapons to array: {adds_to_array}")
        print(f"  Removes weapons from array: {removes_from_array}")

        return test_result("Weapon cards support multi-select",
                          checks_comparison_mode and adds_to_array and removes_from_array)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("Weapon cards support multi-select", False)


def test_7_run_weapon_comparison_function():
    """Test 7: runWeaponComparison function exists"""
    print("\n" + "="*80)
    print("TEST 7: Run Weapon Comparison Function")
    print("="*80)

    try:
        with open('static/js/battle_mode.js', 'r') as f:
            content = f.read()

        has_function = "async function runWeaponComparison()" in content
        uses_promise_all = "Promise.all" in content
        calls_display_comparison = "displayComparisonResults" in content

        print(f"  Function defined: {has_function}")
        print(f"  Uses Promise.all for parallel requests: {uses_promise_all}")
        print(f"  Calls displayComparisonResults: {calls_display_comparison}")

        return test_result("runWeaponComparison function exists",
                          has_function and uses_promise_all and calls_display_comparison)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("runWeaponComparison function exists", False)


def test_8_display_comparison_results_function():
    """Test 8: displayComparisonResults function exists"""
    print("\n" + "="*80)
    print("TEST 8: Display Comparison Results Function")
    print("="*80)

    try:
        with open('static/js/battle_mode.js', 'r') as f:
            content = f.read()

        has_function = "function displayComparisonResults" in content
        creates_table = "results-table" in content or "<table" in content
        sorts_results = "sort((a, b)" in content

        print(f"  Function defined: {has_function}")
        print(f"  Creates comparison table: {creates_table}")
        print(f"  Sorts results by effectiveness: {sorts_results}")

        return test_result("displayComparisonResults function exists",
                          has_function and creates_table and sorts_results)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("displayComparisonResults function exists", False)


def test_9_comparison_table_css():
    """Test 9: CSS styles for comparison table exist"""
    print("\n" + "="*80)
    print("TEST 9: Comparison Table CSS")
    print("="*80)

    try:
        with open('static/css/battle_mode.css', 'r') as f:
            content = f.read()

        has_table_class = ".results-table" in content
        has_comparison_class = ".comparison-table" in content
        has_best_result_class = ".best-result" in content

        print(f"  Has .results-table styles: {has_table_class}")
        print(f"  Has .comparison-table styles: {has_comparison_class}")
        print(f"  Has .best-result highlight: {has_best_result_class}")

        return test_result("Comparison table CSS exists",
                          has_table_class and has_comparison_class and has_best_result_class)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("Comparison table CSS exists", False)


def test_10_calculate_combat_handles_comparison():
    """Test 10: calculateCombat function handles comparison mode"""
    print("\n" + "="*80)
    print("TEST 10: Calculate Combat Handles Comparison")
    print("="*80)

    try:
        with open('static/js/battle_mode.js', 'r') as f:
            content = f.read()

        checks_comparison = "if (comparisonMode && selectedWeapons.length > 1)" in content
        calls_comparison = "await runWeaponComparison()" in content
        updates_button_text = "Compare ${selectedWeapons.length} Weapons" in content

        print(f"  Checks for comparison mode: {checks_comparison}")
        print(f"  Calls runWeaponComparison: {calls_comparison}")
        print(f"  Updates button text dynamically: {updates_button_text}")

        return test_result("calculateCombat handles comparison",
                          checks_comparison and calls_comparison and updates_button_text)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("calculateCombat handles comparison", False)


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("🧪 WEAPON COMPARISON & UNIT COMPOSITION TEST SUITE")
    print("="*80)

    # Run all tests
    test_1_unit_size_input_exists()
    test_2_js_reads_unit_size()
    test_3_comparison_mode_button_exists()
    test_4_js_has_comparison_variables()
    test_5_toggle_comparison_function_exists()
    test_6_weapon_card_multi_select()
    test_7_run_weapon_comparison_function()
    test_8_display_comparison_results_function()
    test_9_comparison_table_css()
    test_10_calculate_combat_handles_comparison()

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
