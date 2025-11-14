#!/usr/bin/env python3
"""
Test Suite for Stratagem Effects Integration
Tests that stratagems properly modify combat calculations
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


def test_1_apply_stratagem_function_exists():
    """Test 1: Apply stratagem function exists and is importable"""
    print("\n" + "="*80)
    print("TEST 1: Stratagem Application Function")
    print("="*80)

    try:
        from stratagems import apply_stratagem_to_combat
        print("  Function imported successfully")
        return test_result("apply_stratagem_to_combat function exists", True)
    except ImportError as e:
        print(f"  Import error: {e}")
        return test_result("apply_stratagem_to_combat function exists", False)


def test_2_go_to_ground_effect():
    """Test 2: Go to Ground adds cover and invuln save"""
    print("\n" + "="*80)
    print("TEST 2: Go to Ground Stratagem Effects")
    print("="*80)

    from stratagems import apply_stratagem_to_combat

    combat_params = {
        'invuln': None,
        'has_cover': False
    }

    modified = apply_stratagem_to_combat('go_to_ground', combat_params)

    print(f"  Original invuln: {combat_params['invuln']}")
    print(f"  Modified invuln: {modified.get('invuln')}")
    print(f"  Original has_cover: {combat_params['has_cover']}")
    print(f"  Modified has_cover: {modified.get('has_cover')}")

    has_cover = modified.get('has_cover') == True
    has_invuln = modified.get('invuln') == 6

    return test_result("Go to Ground adds cover and 6++ save", has_cover and has_invuln)


def test_3_smokescreen_effect():
    """Test 3: Smokescreen adds -1 to hit modifier"""
    print("\n" + "="*80)
    print("TEST 3: Smokescreen Stratagem Effects")
    print("="*80)

    from stratagems import apply_stratagem_to_combat

    combat_params = {
        'hit_modifier': 0
    }

    modified = apply_stratagem_to_combat('smokescreen', combat_params)

    print(f"  Original hit modifier: {combat_params['hit_modifier']}")
    print(f"  Modified hit modifier: {modified.get('hit_modifier')}")

    return test_result("Smokescreen adds -1 to hit", modified.get('hit_modifier') == -1)


def test_4_epic_challenge_effect():
    """Test 4: Epic Challenge grants Precision"""
    print("\n" + "="*80)
    print("TEST 4: Epic Challenge Stratagem Effects")
    print("="*80)

    from stratagems import apply_stratagem_to_combat

    combat_params = {
        'has_precision': False
    }

    modified = apply_stratagem_to_combat('epic_challenge', combat_params)

    print(f"  Original has_precision: {combat_params['has_precision']}")
    print(f"  Modified has_precision: {modified.get('has_precision')}")

    return test_result("Epic Challenge grants Precision", modified.get('has_precision') == True)


def test_5_battle_mode_api_imports_stratagems():
    """Test 5: Battle mode API imports stratagem functions"""
    print("\n" + "="*80)
    print("TEST 5: Battle Mode API Integration")
    print("="*80)

    try:
        # Check if battle_mode_api imports stratagems
        with open('battle_mode_api.py', 'r') as f:
            content = f.read()

        has_import = 'from stratagems import' in content
        has_apply_function = 'apply_stratagem_to_combat' in content
        has_get_function = 'get_stratagem_by_id' in content

        print(f"  Has stratagems import: {has_import}")
        print(f"  Uses apply_stratagem_to_combat: {has_apply_function}")
        print(f"  Uses get_stratagem_by_id: {has_get_function}")

        return test_result("Battle mode API integrates stratagems",
                          has_import and has_apply_function and has_get_function)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("Battle mode API integrates stratagems", False)


def test_6_battle_mode_api_accepts_stratagems():
    """Test 6: Battle mode API endpoint accepts active_stratagems parameter"""
    print("\n" + "="*80)
    print("TEST 6: API Accepts Stratagems Parameter")
    print("="*80)

    try:
        with open('battle_mode_api.py', 'r') as f:
            content = f.read()

        accepts_param = "active_stratagems = data.get('active_stratagems'" in content
        applies_stratagems = "for stratagem_id in active_stratagems" in content

        print(f"  Accepts active_stratagems parameter: {accepts_param}")
        print(f"  Loops through stratagems to apply: {applies_stratagems}")

        return test_result("API accepts and processes stratagems",
                          accepts_param and applies_stratagems)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("API accepts and processes stratagems", False)


def test_7_battle_mode_js_sends_stratagems():
    """Test 7: Battle mode JS sends active stratagems to API"""
    print("\n" + "="*80)
    print("TEST 7: JavaScript Sends Stratagems")
    print("="*80)

    try:
        with open('static/js/battle_mode.js', 'r') as f:
            content = f.read()

        sends_stratagems = "active_stratagems: activeStratagems" in content

        print(f"  Sends active_stratagems in request: {sends_stratagems}")

        return test_result("JavaScript sends stratagems to API", sends_stratagems)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("JavaScript sends stratagems to API", False)


def test_8_battle_mode_js_displays_applied_stratagems():
    """Test 8: Battle mode JS displays applied stratagems in results"""
    print("\n" + "="*80)
    print("TEST 8: JavaScript Displays Applied Stratagems")
    print("="*80)

    try:
        with open('static/js/battle_mode.js', 'r') as f:
            content = f.read()

        displays_stratagems = "stratagems_applied" in content
        has_active_stratagems_section = "Active Stratagems" in content

        print(f"  Checks for stratagems_applied in response: {displays_stratagems}")
        print(f"  Has 'Active Stratagems' results section: {has_active_stratagems_section}")

        return test_result("JavaScript displays applied stratagems",
                          displays_stratagems and has_active_stratagems_section)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("JavaScript displays applied stratagems", False)


def test_9_cp_tracking_variables_exist():
    """Test 9: CP tracking variables exist in JavaScript"""
    print("\n" + "="*80)
    print("TEST 9: CP Tracking Variables")
    print("="*80)

    try:
        with open('static/js/battle_mode.js', 'r') as f:
            content = f.read()

        has_cp_total = "let cpTotal" in content or "var cpTotal" in content
        has_cp_remaining = "let cpRemaining" in content or "var cpRemaining" in content
        has_spent_stratagems = "spentStratagems" in content

        print(f"  Has cpTotal variable: {has_cp_total}")
        print(f"  Has cpRemaining variable: {has_cp_remaining}")
        print(f"  Has spentStratagems object: {has_spent_stratagems}")

        return test_result("CP tracking variables defined",
                          has_cp_total and has_cp_remaining and has_spent_stratagems)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("CP tracking variables defined", False)


def test_10_cp_tracking_ui_exists():
    """Test 10: CP tracking UI elements exist in HTML"""
    print("\n" + "="*80)
    print("TEST 10: CP Tracking UI Elements")
    print("="*80)

    try:
        with open('templates/battle_mode.html', 'r') as f:
            content = f.read()

        has_cp_panel = "cp-tracker-panel" in content
        has_cp_remaining = "cp-remaining" in content
        has_cp_total = "cp-total" in content
        has_cp_reset = "cp-reset-btn" in content

        print(f"  Has CP tracker panel: {has_cp_panel}")
        print(f"  Has CP remaining display: {has_cp_remaining}")
        print(f"  Has CP total display: {has_cp_total}")
        print(f"  Has CP reset button: {has_cp_reset}")

        return test_result("CP tracking UI elements exist",
                          has_cp_panel and has_cp_remaining and has_cp_total and has_cp_reset)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("CP tracking UI elements exist", False)


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("🧪 STRATAGEM EFFECTS INTEGRATION TEST SUITE")
    print("="*80)

    # Run all tests
    test_1_apply_stratagem_function_exists()
    test_2_go_to_ground_effect()
    test_3_smokescreen_effect()
    test_4_epic_challenge_effect()
    test_5_battle_mode_api_imports_stratagems()
    test_6_battle_mode_api_accepts_stratagems()
    test_7_battle_mode_js_sends_stratagems()
    test_8_battle_mode_js_displays_applied_stratagems()
    test_9_cp_tracking_variables_exist()
    test_10_cp_tracking_ui_exists()

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
