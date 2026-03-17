#!/usr/bin/env python3
"""
Export daily positions data for downstream reporting.

Connects to the positions database, extracts current holdings,
and writes output in the requested format.
"""

import argparse
import os


def export_positions(date: str, output_format: str, output_dir: str):
    """Export positions data."""
    os.makedirs(output_dir, exist_ok=True)

    print(f"Exporting positions for {date}")
    print(f"  Format: {output_format}")
    print(f"  Output: {output_dir}")

    # In production, this queries the positions database
    output_file = os.path.join(output_dir, f"positions_{date}.{output_format}")
    with open(output_file, "w") as f:
        f.write(f"# Positions export placeholder: {date}\n")

    print(f"  Written: {output_file}")
    print("Export complete.")


def main():
    parser = argparse.ArgumentParser(description="Export daily positions")
    parser.add_argument("--date", required=True)
    parser.add_argument("--format", default="parquet", choices=["parquet", "csv", "xlsx"])
    parser.add_argument("--output", required=True)

    args = parser.parse_args()
    export_positions(args.date, args.format, args.output)


if __name__ == "__main__":
    main()
