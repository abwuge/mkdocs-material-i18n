"""Test runner script for dynamic test discovery"""

import sys
import subprocess
from pathlib import Path


def run_test():
    """Dynamic test runner that can run specific test files or all tests"""
    if len(sys.argv) < 2:
        print("Usage: pdm run test <test_name|all>")
        print("Available tests:")
        list_available_tests()
        return

    test_name = sys.argv[1]
    tests_dir = Path("tests")

    if test_name == "all":
        # Run all tests
        subprocess.run(["pytest", "-v"], check=False)
    else:
        # Try to find matching test files using pattern matching
        test_patterns = [
            f"test_{test_name}.py",  # Exact match: test_config.py
            f"test_{test_name}_*.py",  # Pattern match: test_config_*.py
        ]

        matching_files = []
        for pattern in test_patterns:
            matching_files.extend(tests_dir.glob(pattern))

        if matching_files:
            test_paths = [str(f) for f in matching_files]
            subprocess.run(["pytest"] + test_paths + ["-v"], check=False)
        else:
            print(f"No test files found matching '{test_name}'!")
            print("Available tests:")
            list_available_tests()


def list_available_tests():
    """List all available test files in a hierarchical structure"""
    tests_dir = Path("tests")
    if not tests_dir.exists():
        print("  Tests directory not found")
        return

    test_files = list(tests_dir.glob("test_*.py"))
    if not test_files:
        print("  No test files found")
        return

    # Group tests by category automatically
    test_groups = {}
    individual_tests = []

    for test_file in test_files:
        name = test_file.stem.replace("test_", "")

        # Check if it's a grouped test (contains underscore after first part)
        if "_" in name:
            category = name.split("_")[0]
            subcategory = "_".join(name.split("_")[1:])

            if category not in test_groups:
                test_groups[category] = []
            test_groups[category].append((subcategory, test_file))
        else:
            individual_tests.append((name, test_file))

    # Display grouped tests
    if test_groups:
        print("  Grouped tests:")
        for category in sorted(test_groups.keys()):
            subcategories = test_groups[category]
            print(f"    {category}/ (run with 'pdm run test {category}')")
            for subcat, _ in sorted(subcategories):
                print(f"      - {category}_{subcat}")

    # Display individual tests
    if individual_tests:
        print("  Individual tests:")
        for name, _ in sorted(individual_tests):
            print(f"    - {name}")

    print("  Special commands:")
    print("    - all (run all tests)")


if __name__ == "__main__":
    run_test()
