# Using uv with English Word Atlas

[uv](https://github.com/astral-sh/uv) is a fast Python package installer and environment manager. Here's how to use it with this project:

## Quick Start

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create environment and install dependencies
uv venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uv pip install -e ".[dev]"

# Or use our helper script (recreates env each time)
./run-with-uv.sh test      # Run tests
./run-with-uv.sh lint      # Run linter
./run-with-uv.sh coverage  # Run coverage
```

## Common Commands

```bash
# Run tests
uv run -- pytest

# Run linter
uv run -- black word_atlas tests

# Run with coverage
uv run -- pytest --cov=word_atlas

# Install dependencies
uv pip install -e ".[dev,visualization,web]"
```

The helper scripts `run-with-uv.sh` (Unix/macOS) and `run-with-uv.ps1` (Windows) manage environment creation and dependency installation automatically. 