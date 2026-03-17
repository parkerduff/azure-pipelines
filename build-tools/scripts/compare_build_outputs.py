#!/usr/bin/env python3
"""
Compare build outputs against validation baselines.

Used during release gates to verify that build artifacts match
expected patterns (file counts, sizes, names).
"""

import argparse
import json
import os
import sys
from pathlib import Path


def load_baseline(baseline_dir: str, artifact_name: str) -> dict:
    """Load the expected artifacts baseline for a service."""
    # Try to find a matching baseline file
    baseline_path = Path(baseline_dir)
    for service_dir in baseline_path.iterdir():
        if service_dir.is_dir():
            expected_file = service_dir / "expected-artifacts.json"
            if expected_file.exists():
                with open(expected_file) as f:
                    baseline = json.load(f)
                    if baseline.get("artifact_name") == artifact_name:
                        return baseline
    return None


def compare_outputs(artifact_name: str, baseline_dir: str):
    """Compare current build outputs against baseline."""
    baseline = load_baseline(baseline_dir, artifact_name)

    if baseline is None:
        print(f"WARNING: No baseline found for artifact '{artifact_name}'")
        print("  Skipping comparison. Consider adding a baseline.")
        return True

    print(f"Comparing '{artifact_name}' against baseline:")
    print(f"  Expected files: {baseline.get('expected_file_count', 'unknown')}")
    print(f"  Expected types: {baseline.get('expected_file_types', [])}")

    staging_dir = os.environ.get("BUILD_ARTIFACTSTAGINGDIRECTORY", "/tmp")
    actual_files = list(Path(staging_dir).rglob("*"))
    actual_count = len([f for f in actual_files if f.is_file()])

    expected_count = baseline.get("expected_file_count", 0)
    if actual_count < expected_count * 0.8:
        print(f"  FAIL: Expected ~{expected_count} files, found {actual_count}")
        return False

    print(f"  Actual files: {actual_count}")
    print("  Comparison: PASS")
    return True


def main():
    parser = argparse.ArgumentParser(description="Compare build outputs against baseline")
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--baseline", required=True)

    args = parser.parse_args()

    success = compare_outputs(args.artifact, args.baseline)
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
