#!/usr/bin/env python3
"""
Comprehensive Test Runner
Runs all test suites and provides summary
"""

import subprocess
import sys

test_suites = [
    ('test_edge_cases.py', 'Edge Cases & Error Handling'),
    ('test_combat_calculations.py', 'Combat Engine Calculations'),
    ('test_integration.py', 'Component Integration'),
    ('test_api_validation.py', 'API Validation & Error Handling'),
    ('test_comparison_features.py', 'Weapon Comparison & Unit Composition'),
    ('test_visualization.py', 'Visualization & Efficiency Metrics'),
]

print("="*80)
print("🧪 COMPREHENSIVE TEST SUITE RUNNER")
print("="*80)
print()

total_tests = 0
total_passed = 0
results = []

for test_file, description in test_suites:
    print(f"Running {description}...")
    try:
        result = subprocess.run(
            ['python', test_file],
            capture_output=True,
            text=True,
            timeout=60
        )

        # Parse results from output
        output = result.stdout + result.stderr

        # Look for "Passed: X/Y" pattern
        import re
        match = re.search(r'Passed: (\d+)/(\d+)', output)

        if match:
            passed = int(match.group(1))
            total = int(match.group(2))
            total_tests += total
            total_passed += passed

            status = "✅" if passed == total else "⚠️ "
            results.append((description, passed, total, status))
            print(f"  {status} {passed}/{total} tests passed")
        else:
            print(f"  ❌ Could not parse results")
            results.append((description, 0, 0, "❌"))

    except subprocess.TimeoutExpired:
        print(f"  ⏱️  Timeout")
        results.append((description, 0, 0, "⏱️"))
    except Exception as e:
        print(f"  ❌ Error: {e}")
        results.append((description, 0, 0, "❌"))

    print()

print("="*80)
print("📊 FINAL SUMMARY")
print("="*80)
print()
print(f"{'Test Suite':<45} {'Result':<15} {'Status':<5}")
print("-"*80)

for description, passed, total, status in results:
    if total > 0:
        result_str = f"{passed}/{total}"
    else:
        result_str = "N/A"
    print(f"{description:<45} {result_str:<15} {status:<5}")

print("-"*80)
print(f"{'TOTAL':<45} {total_passed}/{total_tests:<15}")
print("="*80)

if total_passed == total_tests:
    print(f"\n✅ ALL {total_tests} TESTS PASSED!\n")
    sys.exit(0)
else:
    print(f"\n⚠️  {total_tests - total_passed} test(s) failed\n")
    sys.exit(1)
