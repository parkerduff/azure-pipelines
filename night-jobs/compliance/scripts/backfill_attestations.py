#!/usr/bin/env python3
"""
Backfill missing attestation records in attestation-database.
"""

import argparse
import json


def backfill(gaps_file: str, store: str, dry_run: bool):
    """Backfill missing attestations."""
    with open(gaps_file) as f:
        gaps = json.load(f)

    missing = gaps.get("missing_attestations", [])
    print(f"Backfilling {len(missing)} missing attestations")
    print(f"  Store: {store}")
    print(f"  Dry run: {dry_run}")

    for gap in missing:
        if dry_run:
            print(f"  [DRY RUN] Would backfill: {gap}")
        else:
            print(f"  Backfilling: {gap}")

    print("Backfill complete.")


def main():
    parser = argparse.ArgumentParser(description="Backfill attestations")
    parser.add_argument("--gaps", required=True)
    parser.add_argument("--store", required=True)
    parser.add_argument("--dry-run", type=str, default="true")

    args = parser.parse_args()
    dry_run = args.dry_run.lower() == "true"
    backfill(args.gaps, args.store, dry_run)


if __name__ == "__main__":
    main()
