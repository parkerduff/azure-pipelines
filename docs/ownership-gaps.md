# Service Ownership Gaps

## Overview

Many services in this repository have unclear or missing ownership.
This document tracks what is known.

## Service Ownership Matrix

| Service | Owner | Confidence | Notes |
|---------|-------|------------|-------|
| pricing-engine | unknown | low | Original team disbanded. Maintained by shared-ci-platform as best-effort. |
| portfolio-api | team-quant | medium | team-quant uses it but may not own the codebase |
| risk-batch | team-quant | high | Primary consumer of batch compute templates |
| market-sim | team-quant? | low | Built independently, no template usage, unclear maintenance |
| ops-control-plane | platform-team | medium | Infrastructure service, custom pipeline |
| frontend-workbench | team-frontend | high | Owns both the service and the alt-templates |
| regulatory-reporting | team-reporting | high | Owns compliance workflow and team-overrides templates |
| notebook-executor | ? | none | No owner identified. Runs nightly but nobody claims it. |
| scenario-runner | ? | none | No owner identified. Appears to be a team-quant project. |

## Night Jobs Ownership

| Job | Owner | Notes |
|-----|-------|-------|
| var-scenario-sweep | team-quant? | Uses high-memory compute pool |
| daily-positions-export | team-reporting? | Business data export |
| attestation-backfill | shared-ci-platform? | Compliance automation |

## Ad-Hoc Pipelines

| Pipeline | Owner | Notes |
|----------|-------|-------|
| onetime-data-migration | unknown | Should probably be deleted |
| bulk-reprocess-trades | unknown | Triggered manually, unclear frequency |

## Action Items

- [ ] Confirm pricing-engine ownership
- [ ] Determine if market-sim is still actively used
- [ ] Find owner for notebook-executor
- [ ] Find owner for scenario-runner
- [ ] Audit ad-hoc pipelines for deletion candidates
- [ ] Establish ownership requirement for all new pipelines
