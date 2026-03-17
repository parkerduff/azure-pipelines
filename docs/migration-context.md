# CI Platform Migration Context

## Background

This repository contains the shared CI platform configuration used across
the organization. It has evolved organically over approximately five years,
starting as a clean set of shared build templates and growing into a complex
ecosystem of templates, scripts, and operational workflows.

## Current State

The platform currently includes:

- **Central templates** in `templates/` — the original shared build, test, and release templates
- **Alternative templates** in `alt-templates/` — team-maintained alternatives that diverged from central
- **Build tools** in `build-tools/` — shared scripts for artifact publishing, compliance, and notifications
- **Service pipelines** in `services/` — per-service CI pipeline definitions
- **Night jobs** in `night-jobs/` — scheduled operational workloads running on CI infrastructure
- **Ad-hoc pipelines** in `adhoc/` — one-off operational pipelines that were never cleaned up
- **Deprecated pipelines** in `deprecated/` — old pipelines kept "for reference"

## Key Problems

### Template Branch Drift

Teams created long-lived branches to customize templates for their needs.
Over time, these branches diverged from `main`, creating multiple versions
of the same templates with subtle differences.

Known template branches:
- `main` — canonical templates
- `master` — legacy default branch, still referenced by some pipelines
- `staging/preprod` — modified templates for staging environments
- `staging/release-hardening` — release workflow modifications
- `team/frontend-custom` — frontend team's template customizations
- `team/quant-experiments` — quant team's experimental changes
- `team/reporting-hotfix` — compliance workflow patches
- `legacy/master-support` — compatibility branch for old pipelines

### Duplicate Templates

The same build logic exists in multiple places:
- `templates/build/build-python.yml` (central)
- `templates/legacy/build-python-legacy.yml` (legacy)
- `alt-templates/data-science/build-python.yml` (data science fork)
- `services/risk-batch/pipeline-fragments/build-python-local.yml` (service-local fork)

### Non-Build Workloads

Several pipelines are not software builds at all. They use CI infrastructure
for compute-intensive jobs, data processing, and business reporting.
These need to be identified and handled separately during migration.

### Inconsistent Template References

Pipelines reference templates using different patterns:
- Direct branch reference (`ref: main`)
- Legacy branch reference (`ref: master`)
- Staging branch reference (`ref: staging/preprod`)
- Team branch reference (`ref: team/frontend-custom`)
- Variable-driven (`$(templates_branch)`)

## Migration Goal

Migrate all CI build pipelines to GitHub Actions while:
1. Preserving build behavior
2. Consolidating template drift
3. Identifying non-build workloads for separate handling
4. Validating artifact equivalence
5. Maintaining compliance and attestation workflows
