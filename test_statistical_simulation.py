#!/usr/bin/env python3
"""
Test Suite for Statistical Simulation and Mortal Wounds
Tests that multiple simulations work and mortal wounds are calculated
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


def test_1_tank_shock_effect():
    """Test 1: Tank Shock adds mortal wounds"""
    print("\n" + "="*80)
    print("TEST 1: Tank Shock Stratagem Effects")
    print("="*80)

    from stratagems import apply_stratagem_to_combat

    combat_params = {
        'mortal_wounds_bonus': 0
    }

    modified = apply_stratagem_to_combat('tank_shock', combat_params)

    print(f"  Original mortal wounds: {combat_params['mortal_wounds_bonus']}")
    print(f"  Modified mortal wounds: {modified.get('mortal_wounds_bonus')}")
    print(f"  Tank shock active: {modified.get('tank_shock_active')}")

    has_mortal_wounds = modified.get('mortal_wounds_bonus', 0) > 0
    has_flag = modified.get('tank_shock_active') == True

    return test_result("Tank Shock adds mortal wounds", has_mortal_wounds and has_flag)


def test_2_grenades_effect():
    """Test 2: Grenades adds mortal wounds"""
    print("\n" + "="*80)
    print("TEST 2: Grenades Stratagem Effects")
    print("="*80)

    from stratagems import apply_stratagem_to_combat

    combat_params = {
        'mortal_wounds_bonus': 0
    }

    modified = apply_stratagem_to_combat('grenades', combat_params)

    print(f"  Original mortal wounds: {combat_params['mortal_wounds_bonus']}")
    print(f"  Modified mortal wounds: {modified.get('mortal_wounds_bonus')}")
    print(f"  Grenades active: {modified.get('grenades_active')}")

    has_mortal_wounds = modified.get('mortal_wounds_bonus', 0) > 0
    has_flag = modified.get('grenades_active') == True

    return test_result("Grenades adds mortal wounds", has_mortal_wounds and has_flag)


def test_3_api_accepts_num_simulations():
    """Test 3: API accepts num_simulations parameter"""
    print("\n" + "="*80)
    print("TEST 3: API Accepts num_simulations Parameter")
    print("="*80)

    try:
        with open('battle_mode_api.py', 'r') as f:
            content = f.read()

        accepts_param = "num_simulations = data.get('num_simulations'" in content
        loops_simulations = "for _ in range(num_simulations)" in content
        returns_stats = "'stats': stats" in content

        print(f"  Accepts num_simulations parameter: {accepts_param}")
        print(f"  Loops through simulations: {loops_simulations}")
        print(f"  Returns statistics: {returns_stats}")

        return test_result("API implements statistical simulation",
                          accepts_param and loops_simulations and returns_stats)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("API implements statistical simulation", False)


def test_4_api_calculates_statistics():
    """Test 4: API calculates min/max/avg statistics"""
    print("\n" + "="*80)
    print("TEST 4: API Calculates Statistics")
    print("="*80)

    try:
        with open('battle_mode_api.py', 'r') as f:
            content = f.read()

        has_min_damage = "'min_damage'" in content
        has_max_damage = "'max_damage'" in content
        has_avg_damage = "'avg_damage'" in content
        has_models_killed_stats = "'min_models_killed'" in content and "'max_models_killed'" in content

        print(f"  Calculates min_damage: {has_min_damage}")
        print(f"  Calculates max_damage: {has_max_damage}")
        print(f"  Calculates avg_damage: {has_avg_damage}")
        print(f"  Calculates models_killed stats: {has_models_killed_stats}")

        return test_result("API calculates statistics",
                          has_min_damage and has_max_damage and has_avg_damage and has_models_killed_stats)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("API calculates statistics", False)


def test_5_api_tracks_mortal_wounds():
    """Test 5: API tracks and applies mortal wounds"""
    print("\n" + "="*80)
    print("TEST 5: API Tracks Mortal Wounds")
    print("="*80)

    try:
        with open('battle_mode_api.py', 'r') as f:
            content = f.read()

        has_mortal_wounds_var = "mortal_wounds_bonus = combat_params.get('mortal_wounds_bonus'" in content
        adds_to_damage = "mortal_wounds_bonus for r in results" in content or "final_damage = avg_result['damage_after_fnp'] + mortal_wounds_bonus" in content
        returns_mortal_wounds = "'mortal_wounds':" in content

        print(f"  Extracts mortal_wounds from combat_params: {has_mortal_wounds_var}")
        print(f"  Adds mortal wounds to damage: {adds_to_damage}")
        print(f"  Returns mortal_wounds in result: {returns_mortal_wounds}")

        return test_result("API tracks mortal wounds",
                          has_mortal_wounds_var and adds_to_damage and returns_mortal_wounds)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("API tracks mortal wounds", False)


def test_6_ui_has_simulation_selector():
    """Test 6: UI has simulation iterations selector"""
    print("\n" + "="*80)
    print("TEST 6: UI Has Simulation Selector")
    print("="*80)

    try:
        with open('templates/battle_mode.html', 'r') as f:
            content = f.read()

        has_select = 'id="num-simulations"' in content
        has_options = 'value="100"' in content and 'value="1000"' in content
        has_label = 'Simulation Iterations' in content or 'simulation' in content.lower()

        print(f"  Has num-simulations select element: {has_select}")
        print(f"  Has multiple options (100, 1000): {has_options}")
        print(f"  Has descriptive label: {has_label}")

        return test_result("UI has simulation selector", has_select and has_options and has_label)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("UI has simulation selector", False)


def test_7_js_sends_num_simulations():
    """Test 7: JavaScript sends num_simulations to API"""
    print("\n" + "="*80)
    print("TEST 7: JavaScript Sends num_simulations")
    print("="*80)

    try:
        with open('static/js/battle_mode.js', 'r') as f:
            content = f.read()

        gets_value = "document.getElementById('num-simulations').value" in content
        sends_to_api = "num_simulations:" in content or "num_simulations :" in content

        print(f"  Gets value from selector: {gets_value}")
        print(f"  Sends to API: {sends_to_api}")

        return test_result("JavaScript sends num_simulations", gets_value and sends_to_api)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("JavaScript sends num_simulations", False)


def test_8_js_displays_statistics():
    """Test 8: JavaScript displays statistics in results"""
    print("\n" + "="*80)
    print("TEST 8: JavaScript Displays Statistics")
    print("="*80)

    try:
        with open('static/js/battle_mode.js', 'r') as f:
            content = f.read()

        checks_stats = "data.stats" in content or "stats ?" in content
        displays_range = "min_damage" in content or "max_damage" in content
        has_statistics_section = "Statistics" in content or "📊" in content

        print(f"  Checks for stats in response: {checks_stats}")
        print(f"  Displays damage range: {displays_range}")
        print(f"  Has statistics section: {has_statistics_section}")

        return test_result("JavaScript displays statistics",
                          checks_stats and displays_range and has_statistics_section)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("JavaScript displays statistics", False)


def test_9_js_displays_mortal_wounds():
    """Test 9: JavaScript displays mortal wounds"""
    print("\n" + "="*80)
    print("TEST 9: JavaScript Displays Mortal Wounds")
    print("="*80)

    try:
        with open('static/js/battle_mode.js', 'r') as f:
            content = f.read()

        checks_mortal_wounds = "mortal_wounds" in content
        has_mortal_wounds_display = "Mortal Wounds" in content or "💀" in content

        print(f"  Checks for mortal_wounds in result: {checks_mortal_wounds}")
        print(f"  Has mortal wounds display element: {has_mortal_wounds_display}")

        return test_result("JavaScript displays mortal wounds",
                          checks_mortal_wounds and has_mortal_wounds_display)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("JavaScript displays mortal wounds", False)


def test_10_css_styles_simulation_selector():
    """Test 10: CSS styles simulation selector"""
    print("\n" + "="*80)
    print("TEST 10: CSS Styles Simulation Selector")
    print("="*80)

    try:
        with open('static/css/battle_mode.css', 'r') as f:
            content = f.read()

        has_sim_options = ".simulation-options" in content
        has_sim_select = ".sim-select" in content

        print(f"  Has .simulation-options styles: {has_sim_options}")
        print(f"  Has .sim-select styles: {has_sim_select}")

        return test_result("CSS styles simulation selector",
                          has_sim_options and has_sim_select)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("CSS styles simulation selector", False)


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("🧪 STATISTICAL SIMULATION & MORTAL WOUNDS TEST SUITE")
    print("="*80)

    # Run all tests
    test_1_tank_shock_effect()
    test_2_grenades_effect()
    test_3_api_accepts_num_simulations()
    test_4_api_calculates_statistics()
    test_5_api_tracks_mortal_wounds()
    test_6_ui_has_simulation_selector()
    test_7_js_sends_num_simulations()
    test_8_js_displays_statistics()
    test_9_js_displays_mortal_wounds()
    test_10_css_styles_simulation_selector()

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
