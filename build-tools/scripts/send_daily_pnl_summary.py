#!/usr/bin/env python3
"""
Send daily P&L summary email.

This is a business operations script that has no relationship to CI/CD.
It was placed in build-tools because it needed to run on a schedule
and the CI system was the easiest place to set up a cron job.

Generates a daily profit-and-loss summary and emails it to
the reporting distribution list.

TODO: This should not be in the CI platform repository.
"""

import argparse
import sys
from datetime import datetime, timezone


def send_pnl_summary(date: str, recipients: str, format: str = "html"):
    """Generate and send P&L summary."""
    recipient_list = [r.strip() for r in recipients.split(",")]

    print(f"Daily P&L Summary")
    print(f"  Date: {date}")
    print(f"  Format: {format}")
    print(f"  Recipients: {', '.join(recipient_list)}")
    print()

    # In production, this would:
    # 1. Query the P&L database for the given date
    # 2. Generate an HTML or PDF report
    # 3. Send via SMTP to the recipient list

    print("  Generating summary report...")
    print("  Sending to distribution list...")
    print("  Done.")


def main():
    parser = argparse.ArgumentParser(description="Send daily P&L summary")
    parser.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"))
    parser.add_argument("--recipients", default="team-reporting,team-quant")
    parser.add_argument("--format", default="html", choices=["html", "pdf", "csv"])

    args = parser.parse_args()

    try:
        send_pnl_summary(args.date, args.recipients, args.format)
    except Exception as e:
        print(f"ERROR: P&L summary failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
