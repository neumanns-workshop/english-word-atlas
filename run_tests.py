#!/usr/bin/env python
"""
Run tests for the English Word Atlas package.

This script runs pytest with common options. It's a convenient shortcut for
running tests during development.

Note: With uv, you can also use the commands in uv.toml:
    uv run test                    # Run all tests
    uv run coverage                # Run tests with coverage report
    uv run html-coverage           # Generate HTML coverage report

Traditional usage:
    python run_tests.py               # Run all tests
    python run_tests.py -v            # Run tests with verbose output
    python run_tests.py -k atlas      # Run tests containing 'atlas' in their name
    python run_tests.py --no-mock     # Run tests against the actual dataset
    python run_tests.py --cov         # Run tests with coverage report
    python run_tests.py --html        # Generate HTML coverage report
"""

import sys
import pytest


if __name__ == "__main__":
    # Parse arguments
    args = sys.argv[1:]
    
    # Add default options
    pytest_args = [
        "--color=yes",  # Colored output
    ]
    
    # Check for special flags
    if "--no-mock" in args:
        args.remove("--no-mock")
        # When --no-mock is specified, don't use the mock fixtures
        pytest_args.append("--fixture-mark-no-auto")
    
    # Check for coverage flag
    if "--cov" in args:
        args.remove("--cov")
        pytest_args.extend(["--cov=word_atlas", "--cov-report=term"])
    
    # Check for HTML coverage report flag
    if "--html" in args:
        args.remove("--html")
        pytest_args.extend(["--cov=word_atlas", "--cov-report=html:coverage_html"])
    
    # Add the remaining args
    pytest_args.extend(args)
    
    # Run pytest
    print(f"Running pytest with arguments: {' '.join(pytest_args)}")
    sys.exit(pytest.main(pytest_args)) 