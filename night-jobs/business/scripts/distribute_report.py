#!/usr/bin/env python3
"""
Distribute generated reports to downstream team recipients.
"""

import argparse


def distribute(file_path: str, recipients: str):
    """Distribute report to recipients."""
    recipient_list = [r.strip() for r in recipients.split(",")]
    print(f"Distributing report: {file_path}")
    for r in recipient_list:
        print(f"  Sending to: {r}")
    print("Distribution complete.")


def main():
    parser = argparse.ArgumentParser(description="Distribute reports")
    parser.add_argument("--file", required=True)
    parser.add_argument("--recipients", required=True)

    args = parser.parse_args()
    distribute(args.file, args.recipients)


if __name__ == "__main__":
    main()
