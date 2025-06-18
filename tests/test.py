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
        # Look for test file
        test_file = tests_dir / f"test_{test_name}.py"
        if test_file.exists():
            subprocess.run(["pytest", str(test_file), "-v"], check=False)
        else:
            print(f"Test file 'test_{test_name}.py' not found!")
            print("Available tests:")
            list_available_tests()


def list_available_tests():
    """List all available test files"""
    tests_dir = Path("tests")
    if tests_dir.exists():
        test_files = list(tests_dir.glob("test_*.py"))
        if test_files:
            for test_file in test_files:
                test_name = test_file.stem.replace("test_", "")
                print(f"  - {test_name}")
        else:
            print("  No test files found")
    else:
        print("  Tests directory not found")


if __name__ == "__main__":
    run_test()
