# CI Platform Migration Context

## Background

This repository contains the shared CI platform configuration used across
the organization. It has evolved organically over approximately five years,
starting as a clean set of shared build templates and growing into a complex
ecosystem of templates, scripts, and operational workflows.

The original template architecture was designed and implemented by an
external contractor. When the engagement ended, maintenance was picked up
ad-hoc by various internal teams. No single team owns the full template
surface today, and the original design decisions are poorly documented.

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

### On-Premises Build Worker Misuse

The organization maintains self-hosted agent pools (`linux-build-workers`,
`high-memory-pool`) intended for CI builds. However, teams have discovered
that these long-running on-prem agents provide free, always-available compute
with network access to internal systems. As a result:

- Scheduled data exports run on build workers instead of dedicated job infrastructure
- Monte Carlo simulations and scenario sweeps use `high-memory-pool` agents
- Jupyter notebook execution happens nightly on `linux-build-workers`
- Compliance backfill jobs run on build workers because they need access to `attestation-database`

Teams avoid the dedicated night-jobs infrastructure because it requires
separate provisioning and approval. Build workers "just work."

This creates a migration complication: these workloads cannot simply move
to GitHub Actions hosted runners. They require network access to internal
systems and often exceed hosted runner time limits.

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
