#!/usr/bin/env python
"""CLI tool to run voice agent test scenarios from feature files."""
from __future__ import annotations

import sys
import subprocess
from pathlib import Path


def main() -> int:
    """Run behave tests for voice agent scenarios."""
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    features_dir = project_root / "features"
    
    if not features_dir.exists():
        print(f"Error: Features directory not found at {features_dir}")
        return 1
    
    # Check if behave is installed
    try:
        import behave
    except ImportError:
        print("Error: behave is not installed. Install it with: pip install behave")
        return 1
    
    # Build behave command
    behave_args = ["behave"]
    
    # Add any command line arguments passed to this script
    if len(sys.argv) > 1:
        behave_args.extend(sys.argv[1:])
    else:
        # Default: run all features with verbose output
        behave_args.extend([str(features_dir), "--no-capture", "--format", "pretty"])
    
    # Change to project root and run behave
    print(f"Running voice agent feature tests from: {features_dir}")
    print(f"Command: {' '.join(behave_args)}\n")
    
    result = subprocess.run(behave_args, cwd=project_root)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
