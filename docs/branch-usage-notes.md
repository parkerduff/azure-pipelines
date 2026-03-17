# Branch Usage Notes

## Overview

This repository uses long-lived branches to manage template variants.
This was never the intended architecture but evolved as teams needed
custom template behavior that the central team couldn't accommodate
quickly enough.

## Branch Inventory

### main
- **Purpose**: Canonical shared templates
- **Consumers**: pricing-engine, risk-batch (indirectly)
- **Status**: Actively maintained
- **Owner**: shared-ci-platform team

### master
- **Purpose**: Legacy default branch
- **Consumers**: portfolio-api, some deprecated pipelines
- **Status**: Should be merged into main; contains small divergences
- **Owner**: shared-ci-platform team
- **Notes**: Some pipelines still reference `master` because they were
  created before the default branch was changed to `main`

### staging/preprod
- **Purpose**: Template modifications for staging environments
- **Consumers**: risk-batch
- **Status**: Active but unmaintained
- **Owner**: team-quant (assumed)
- **Notes**: Added retry logic to python build template. Changes were
  never merged back to main.

### staging/release-hardening
- **Purpose**: Extra validation gates in release templates
- **Consumers**: Unknown — may be unused
- **Status**: Unclear
- **Owner**: Unknown

### team/frontend-custom
- **Purpose**: Frontend-specific template customizations
- **Consumers**: frontend-workbench
- **Status**: Active
- **Owner**: team-frontend
- **Notes**: Includes SSR build support and custom webpack configuration
  that the central node template doesn't provide

### team/quant-experiments
- **Purpose**: Experimental template changes for quant workloads
- **Consumers**: Possibly scenario-runner, notebook-executor
- **Status**: Unknown
- **Owner**: team-quant

### team/reporting-hotfix
- **Purpose**: Compliance workflow patches
- **Consumers**: regulatory-reporting
- **Status**: Active
- **Owner**: team-reporting
- **Notes**: Added extra compliance metadata generation steps

### legacy/master-support
- **Purpose**: Compatibility for pipelines that cannot upgrade
- **Consumers**: risk-batch (legacy pipeline), old-pricing-pipeline (deprecated)
- **Status**: Frozen
- **Owner**: None

## Known Issues

1. **No branch protection**: Any team can push to any branch
2. **No merge cadence**: Team branches are never merged back to main
3. **No consumer tracking**: Unknown which pipelines consume which branches
4. **Stale branches**: Some branches may have no active consumers
