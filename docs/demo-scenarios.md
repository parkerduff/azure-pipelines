# Demo Scenarios

## Overview

This repository is designed to demonstrate CI migration analysis capabilities.
Below are the key demo scenarios and what they exercise.

---

## Scenario 1: Pipeline Inventory

**Goal**: Enumerate all pipeline entrypoints across the repository.

**Expected findings**:
- Service pipelines in `services/*/azure-pipelines.yml`
- Legacy pipelines in `services/*/azure-pipelines-legacy.yml`
- Night jobs in `night-jobs/**/*.yml`
- Ad-hoc pipelines in `adhoc/*.yml`
- Deprecated pipelines in `deprecated/*.yml`

**Demonstrates**: Discovery across non-standard locations.

---

## Scenario 2: Pipeline Classification

**Goal**: Classify each pipeline into categories.

**Categories**:
- **Central template consumers** — use `templates/`
- **Alt-template consumers** — use `alt-templates/`
- **Custom pipelines** — inline YAML, no shared templates
- **Non-build workloads** — business/compute jobs on CI infra

**Demonstrates**: Semantic understanding of pipeline purpose.

---

## Scenario 3: Template Dependency Resolution

**Goal**: For each pipeline, determine which templates it uses and from which branch.

**Key patterns to resolve**:
- `ref: main` → standard template reference
- `ref: master` → legacy branch reference
- `ref: staging/preprod` → staging branch with modifications
- `ref: team/frontend-custom` → team-specific branch
- `ref: team/reporting-hotfix` → compliance hotfix branch
- `ref: legacy/master-support` → frozen compatibility branch

**Demonstrates**: Branch-aware dependency analysis.

---

## Scenario 4: Template Ecosystem Analysis

**Goal**: Identify template duplication and drift.

**Key findings**:
- `build-python.yml` exists in three locations with different behavior
- Legacy templates diverge from central versions
- Service-local template forks exist
- Release templates have environment-specific variants

**Demonstrates**: Cross-repository template analysis.

---

## Scenario 5: GitHub Actions Migration

**Goal**: Generate equivalent GitHub Actions workflows.

**Considerations**:
- Map ADO tasks to GitHub Actions equivalents
- Handle template references → reusable workflows
- Convert variable syntax
- Handle environment/deployment gates

**Demonstrates**: Automated YAML transformation.

---

## Scenario 6: Validation Planning

**Goal**: Define validation checks for each migrated pipeline.

**Validation types**:
- Artifact comparison (file counts, types, sizes)
- Test count comparison (pass rates, coverage)
- Deployment verification
- Compliance attestation equivalence

**Demonstrates**: Migration safety planning.

---

## Scenario 7: Non-Build Workload Detection

**Goal**: Identify pipelines that should NOT migrate to GitHub Actions.

**Expected non-build workloads**:
- `notebook-executor` — Jupyter notebook execution
- `scenario-runner` — Monte Carlo simulations
- `night-jobs/compute/var-scenario-sweep.yml` — VaR calculations
- `night-jobs/business/daily-positions-export.yml` — data export
- `night-jobs/compliance/attestation-backfill.yml` — compliance backfill

**Demonstrates**: Workload classification and migration scoping.
