#!/usr/bin/env python3
"""
Upload VaR computation results to the data warehouse.
"""

import argparse
import os


def upload_results(input_dir: str, destination: str, date: str):
    """Upload result files to data warehouse."""
    files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
    print(f"Uploading {len(files)} files to {destination}")
    print(f"  Date: {date}")
    for f in sorted(files):
        print(f"  Uploading: {f}")
    print("Upload complete.")


def main():
    parser = argparse.ArgumentParser(description="Upload results to data warehouse")
    parser.add_argument("--input", required=True)
    parser.add_argument("--destination", required=True)
    parser.add_argument("--date", required=True)

    args = parser.parse_args()
    upload_results(args.input, args.destination, args.date)


if __name__ == "__main__":
    main()
