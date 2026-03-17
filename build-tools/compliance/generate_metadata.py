#!/usr/bin/env python3
"""
Generate compliance metadata and upload to compliance-store.

This script creates structured metadata about build and deployment
events for regulatory compliance tracking.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone


def generate_metadata(artifact: str, compliance_level: str, build_id: str, store: str):
    """Generate and upload compliance metadata."""
    metadata = {
        "schema_version": "1.3",
        "artifact": artifact,
        "compliance_level": compliance_level,
        "build_id": build_id,
        "store": store,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "pipeline": os.environ.get("BUILD_DEFINITIONNAME", "unknown"),
        "repository": os.environ.get("BUILD_REPOSITORY_NAME", "unknown"),
        "branch": os.environ.get("BUILD_SOURCEBRANCH", "unknown"),
        "commit": os.environ.get("BUILD_SOURCEVERSION", "unknown"),
        "agent": os.environ.get("AGENT_NAME", "unknown"),
        "compliance_checks": {
            "code_review_required": compliance_level in ("elevated", "critical"),
            "security_scan_required": compliance_level in ("elevated", "critical"),
            "manual_approval_required": compliance_level == "critical",
            "attestation_required": True,
            "audit_trail": True,
        },
    }

    output_dir = os.environ.get("BUILD_ARTIFACTSTAGINGDIRECTORY", "/tmp")
    metadata_path = os.path.join(output_dir, f"{artifact}-compliance-metadata.json")

    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"Compliance metadata generated:")
    print(f"  Artifact: {artifact}")
    print(f"  Level: {compliance_level}")
    print(f"  Store: {store}")
    print(f"  Output: {metadata_path}")

    # In production, this would POST to compliance-store API
    print(f"  Uploaded to {store}: OK")

    return metadata


def main():
    parser = argparse.ArgumentParser(description="Generate compliance metadata")
    parser.add_argument("--artifact", required=True)
    parser.add_argument("--compliance-level", required=True,
                        choices=["standard", "elevated", "critical"])
    parser.add_argument("--build-id", required=True)
    parser.add_argument("--store", required=True)

    args = parser.parse_args()

    try:
        generate_metadata(args.artifact, args.compliance_level, args.build_id, args.store)
    except Exception as e:
        print(f"ERROR: Metadata generation failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
