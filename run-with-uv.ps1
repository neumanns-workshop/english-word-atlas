# Run commands with uv without relying on activated environments
param (
    [Parameter(Position=0, Mandatory=$true)]
    [ValidateSet("test", "lint", "coverage", "html-coverage")]
    [string]$Command
)

# Clean old environment if needed
if (Test-Path ".venv") {
    Write-Host "Removing existing .venv directory..."
    Remove-Item -Recurse -Force ".venv"
}

# Create new environment
Write-Host "Creating fresh virtual environment..."
uv venv

# Get the full path to the Python executable
$VenvPython = Join-Path -Path (Get-Location) -ChildPath ".venv\Scripts\python.exe"

if (-not (Test-Path $VenvPython)) {
    Write-Host "Error: Virtual environment Python not found at $VenvPython"
    exit 1
}

# Install dependencies
Write-Host "Installing dependencies..."
uv pip install -e ".[dev]" --python $VenvPython

# Run the command
function Run-Command {
    param (
        [Parameter(Mandatory=$true)]
        [string[]]$Args
    )
    
    Write-Host "Running: $Args"
    uv run --python $VenvPython -- $Args
}

# Process command argument
switch ($Command) {
    "test" {
        Run-Command "pytest"
    }
    "lint" {
        Run-Command "black", "word_atlas", "tests"
    }
    "coverage" {
        Run-Command "pytest", "--cov=word_atlas", "--cov-report=term"
    }
    "html-coverage" {
        Run-Command "pytest", "--cov=word_atlas", "--cov-report=html:coverage_html"
    }
    default {
        Write-Host "Unknown command: $Command"
        Write-Host "Available commands: test, lint, coverage, html-coverage"
    }
} 