#!/usr/bin/env python3
"""
Test Suite for Probability Distribution Visualization and Efficiency Metrics
Tests the new visualization and metrics features
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


def test_1_api_calculates_distributions():
    """Test 1: API calculates damage and models distributions"""
    print("\n" + "="*80)
    print("TEST 1: API Calculates Distributions")
    print("="*80)

    try:
        with open('battle_mode_api.py', 'r') as f:
            content = f.read()

        has_counter_import = "from collections import Counter" in content
        calculates_damage_dist = "damage_distribution = Counter(total_damages)" in content
        calculates_models_dist = "models_distribution = Counter(models_killed)" in content
        converts_to_percent = "damage_dist_percent" in content

        print(f"  Imports Counter: {has_counter_import}")
        print(f"  Calculates damage distribution: {calculates_damage_dist}")
        print(f"  Calculates models distribution: {calculates_models_dist}")
        print(f"  Converts to percentages: {converts_to_percent}")

        return test_result("API calculates distributions",
                          has_counter_import and calculates_damage_dist and
                          calculates_models_dist and converts_to_percent)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("API calculates distributions", False)


def test_2_api_returns_distribution_data():
    """Test 2: API returns distribution data in stats"""
    print("\n" + "="*80)
    print("TEST 2: API Returns Distribution Data")
    print("="*80)

    try:
        with open('battle_mode_api.py', 'r') as f:
            content = f.read()

        has_damage_dist_key = "'damage_distribution':" in content
        has_models_dist_key = "'models_distribution':" in content
        sorts_distribution = "sorted(damage_dist_percent.items())" in content

        print(f"  Returns damage_distribution in stats: {has_damage_dist_key}")
        print(f"  Returns models_distribution in stats: {has_models_dist_key}")
        print(f"  Sorts distribution for display: {sorts_distribution}")

        return test_result("API returns distribution data",
                          has_damage_dist_key and has_models_dist_key and sorts_distribution)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("API returns distribution data", False)


def test_3_js_displays_damage_distribution():
    """Test 3: JavaScript displays damage distribution chart"""
    print("\n" + "="*80)
    print("TEST 3: JavaScript Displays Damage Distribution")
    print("="*80)

    try:
        with open('static/js/battle_mode.js', 'r') as f:
            content = f.read()

        checks_distribution = "stats.damage_distribution" in content
        has_distribution_chart = "distribution-chart" in content
        displays_bars = "distribution-bar" in content
        shows_percentages = "distribution-percent" in content

        print(f"  Checks for damage_distribution: {checks_distribution}")
        print(f"  Creates distribution chart: {has_distribution_chart}")
        print(f"  Displays distribution bars: {displays_bars}")
        print(f"  Shows percentages: {shows_percentages}")

        return test_result("JavaScript displays damage distribution",
                          checks_distribution and has_distribution_chart and
                          displays_bars and shows_percentages)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("JavaScript displays damage distribution", False)


def test_4_js_displays_models_distribution():
    """Test 4: JavaScript displays models killed distribution"""
    print("\n" + "="*80)
    print("TEST 4: JavaScript Displays Models Distribution")
    print("="*80)

    try:
        with open('static/js/battle_mode.js', 'r') as f:
            content = f.read()

        has_models_dist = "stats.models_distribution" in content
        has_models_title = "Models Killed Probability" in content
        has_models_bar_class = "models-bar" in content

        print(f"  Checks for models_distribution: {has_models_dist}")
        print(f"  Has models killed title: {has_models_title}")
        print(f"  Has special models-bar class: {has_models_bar_class}")

        return test_result("JavaScript displays models distribution",
                          has_models_dist and has_models_title and has_models_bar_class)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("JavaScript displays models distribution", False)


def test_5_js_shows_efficiency_metrics():
    """Test 5: JavaScript displays efficiency metrics"""
    print("\n" + "="*80)
    print("TEST 5: JavaScript Displays Efficiency Metrics")
    print("="*80)

    try:
        with open('static/js/battle_mode.js', 'r') as f:
            content = f.read()

        has_efficiency_section = "Efficiency Metrics" in content
        calculates_hit_rate = "result.num_hits / result.num_attacks" in content
        calculates_wound_rate = "result.num_wounds / result.num_hits" in content
        calculates_damage_per_attack = "summary.wounds_dealt / result.num_attacks" in content

        print(f"  Has efficiency metrics section: {has_efficiency_section}")
        print(f"  Calculates hit rate: {calculates_hit_rate}")
        print(f"  Calculates wound rate: {calculates_wound_rate}")
        print(f"  Calculates damage per attack: {calculates_damage_per_attack}")

        return test_result("JavaScript displays efficiency metrics",
                          has_efficiency_section and calculates_hit_rate and
                          calculates_wound_rate and calculates_damage_per_attack)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("JavaScript displays efficiency metrics", False)


def test_6_comparison_table_has_efficiency():
    """Test 6: Comparison table includes efficiency column"""
    print("\n" + "="*80)
    print("TEST 6: Comparison Table Has Efficiency")
    print("="*80)

    try:
        with open('static/js/battle_mode.js', 'r') as f:
            content = f.read()

        # Check in displayComparisonResults function
        has_efficiency_header = content.count("<th>Efficiency</th>") > 0
        calculates_efficiency = "const efficiency = r.data.summary.wounds_dealt / r.data.result.num_attacks" in content
        displays_efficiency = "dmg/atk" in content

        print(f"  Has Efficiency column header: {has_efficiency_header}")
        print(f"  Calculates efficiency value: {calculates_efficiency}")
        print(f"  Displays efficiency in table: {displays_efficiency}")

        return test_result("Comparison table has efficiency",
                          has_efficiency_header and calculates_efficiency and displays_efficiency)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("Comparison table has efficiency", False)


def test_7_css_distribution_styles():
    """Test 7: CSS has distribution visualization styles"""
    print("\n" + "="*80)
    print("TEST 7: CSS Distribution Styles")
    print("="*80)

    try:
        with open('static/css/battle_mode.css', 'r') as f:
            content = f.read()

        has_chart_class = ".distribution-chart" in content
        has_bar_class = ".distribution-bar" in content
        has_row_class = ".distribution-row" in content
        has_models_bar = ".models-bar" in content

        print(f"  Has .distribution-chart styles: {has_chart_class}")
        print(f"  Has .distribution-bar styles: {has_bar_class}")
        print(f"  Has .distribution-row styles: {has_row_class}")
        print(f"  Has .models-bar special style: {has_models_bar}")

        return test_result("CSS distribution styles exist",
                          has_chart_class and has_bar_class and has_row_class and has_models_bar)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("CSS distribution styles exist", False)


def test_8_css_efficiency_styles():
    """Test 8: CSS has efficiency metrics styles"""
    print("\n" + "="*80)
    print("TEST 8: CSS Efficiency Metrics Styles")
    print("="*80)

    try:
        with open('static/css/battle_mode.css', 'r') as f:
            content = f.read()

        has_metrics_class = ".efficiency-metrics" in content
        has_metric_class = ".efficiency-metric" in content
        has_value_class = ".efficiency-metric-value" in content
        has_label_class = ".efficiency-metric-label" in content

        print(f"  Has .efficiency-metrics styles: {has_metrics_class}")
        print(f"  Has .efficiency-metric styles: {has_metric_class}")
        print(f"  Has .efficiency-metric-value styles: {has_value_class}")
        print(f"  Has .efficiency-metric-label styles: {has_label_class}")

        return test_result("CSS efficiency styles exist",
                          has_metrics_class and has_metric_class and
                          has_value_class and has_label_class)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("CSS efficiency styles exist", False)


def test_9_distribution_only_shows_for_many_sims():
    """Test 9: Distribution only shows for 100+ simulations"""
    print("\n" + "="*80)
    print("TEST 9: Distribution Conditional Display")
    print("="*80)

    try:
        with open('static/js/battle_mode.js', 'r') as f:
            content = f.read()

        has_condition = "numSims >= 100" in content
        checks_distribution_exists = "stats.damage_distribution && stats.damage_distribution.length > 0" in content

        print(f"  Checks for numSims >= 100: {has_condition}")
        print(f"  Checks distribution exists: {checks_distribution_exists}")

        return test_result("Distribution conditional on simulation count",
                          has_condition and checks_distribution_exists)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("Distribution conditional on simulation count", False)


def test_10_bars_have_gradient_colors():
    """Test 10: Distribution bars use gradient colors"""
    print("\n" + "="*80)
    print("TEST 10: Gradient Bar Colors")
    print("="*80)

    try:
        with open('static/css/battle_mode.css', 'r') as f:
            content = f.read()

        # Check for gradient styling
        has_gradient = "linear-gradient" in content and "distribution-bar" in content
        has_gold_gradient = "#d4af37" in content or "#f4d03f" in content
        has_red_gradient = "#e94560" in content or "#ff6b81" in content

        print(f"  Uses linear gradients: {has_gradient}")
        print(f"  Has gold gradient (damage): {has_gold_gradient}")
        print(f"  Has red gradient (models): {has_red_gradient}")

        return test_result("Bars use gradient colors",
                          has_gradient and has_gold_gradient and has_red_gradient)
    except Exception as e:
        print(f"  Error: {e}")
        return test_result("Bars use gradient colors", False)


def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("🧪 VISUALIZATION & EFFICIENCY METRICS TEST SUITE")
    print("="*80)

    # Run all tests
    test_1_api_calculates_distributions()
    test_2_api_returns_distribution_data()
    test_3_js_displays_damage_distribution()
    test_4_js_displays_models_distribution()
    test_5_js_shows_efficiency_metrics()
    test_6_comparison_table_has_efficiency()
    test_7_css_distribution_styles()
    test_8_css_efficiency_styles()
    test_9_distribution_only_shows_for_many_sims()
    test_10_bars_have_gradient_colors()

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
