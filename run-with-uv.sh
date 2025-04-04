#!/bin/bash
# Run commands with uv without relying on activated environments

set -e

# Clean old environment if needed
if [ -d ".venv" ]; then
  echo "Removing existing .venv directory..."
  rm -rf .venv
fi

# Create new environment
echo "Creating fresh virtual environment..."
uv venv

# Function to run commands in the new environment
run_cmd() {
  echo "Running: $@"
  # Use the full path to the python executable in .venv
  VENV_PYTHON="$(pwd)/.venv/bin/python"
  
  if [ ! -f "$VENV_PYTHON" ]; then
    echo "Error: Virtual environment Python not found at $VENV_PYTHON"
    exit 1
  fi
  
  # Run the command with the venv python
  uv run --python "$VENV_PYTHON" -- "$@"
}

# Install dependencies
echo "Installing dependencies..."
uv pip install -e ".[dev]" --python "$(pwd)/.venv/bin/python"

# Process command argument
if [ "$1" == "test" ]; then
  run_cmd pytest
elif [ "$1" == "lint" ]; then
  run_cmd black word_atlas tests
elif [ "$1" == "coverage" ]; then
  run_cmd pytest --cov=word_atlas --cov-report=term
elif [ "$1" == "html-coverage" ]; then
  run_cmd pytest --cov=word_atlas --cov-report=html:coverage_html
else
  echo "Usage: $0 [test|lint|coverage|html-coverage]"
  echo ""
  echo "Available commands:"
  echo "  test           Run tests with pytest"
  echo "  lint           Run black linter"
  echo "  coverage       Run tests with coverage"
  echo "  html-coverage  Run tests with HTML coverage report"
fi 