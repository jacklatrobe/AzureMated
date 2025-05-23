#!/usr/bin/env python
"""
Run the test suite with coverage reports
"""

import os
import sys
import subprocess

def main():
    """Run the test suite with coverage reports"""
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Change to the project root directory
    os.chdir(script_dir)
    
    # Run pytest with coverage
    cmd = [
        "pytest",
        "--cov=utils",
        "--cov=main",
        "--cov-report=term-missing",
        "--cov-report=html:coverage_html"
    ]
    
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd)

if __name__ == "__main__":
    main()
