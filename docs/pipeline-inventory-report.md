# Pipeline Inventory & Classification Report

**Repository:** `parkerduff/azure-pipelines` (shared-ci-platform)
**Organization:** contoso-financial
**Generated:** 2026-03-18
**Purpose:** ADO-to-GitHub-Actions migration planning for ~30,000 repo enterprise CI platform

---

## 1. Pipeline Inventory Table

18 pipeline definitions registered in Azure DevOps, cross-referenced with YAML files on disk.

| ID | Pipeline Name | YAML Path | ADO Folder | Queue Status | Pool | Last Run Date | Last Result | Runs (90d) | Avg Duration | Classification |
|----|--------------|-----------|------------|-------------|------|--------------|-------------|-----------|-------------|---------------|
| 101 | pricing-engine-ci | `services/pricing-engine/azure-pipelines.yml` | `\Services\pricing-engine` | **enabled** | Azure Pipelines (hosted) | 2026-03-14 | succeeded | 47 | 7.5 min | central-template-consumer |
| 102 | portfolio-api-ci | `services/portfolio-api/azure-pipelines.yml` | `\Services\portfolio-api` | **enabled** | Azure Pipelines (hosted) | 2026-03-12 | succeeded | 31 | 9.8 min | central-template-consumer |
| 103 | portfolio-api-canary | `services/portfolio-api/azure-pipelines-canary.yml` | `\Services\portfolio-api` | **enabled** | Azure Pipelines (hosted) | 2026-02-28 | succeeded | 5 | 8.5 min | central-template-consumer |
| 104 | risk-batch-ci | `services/risk-batch/azure-pipelines.yml` | `\Services\risk-batch` | **enabled** | Azure Pipelines (hosted) | 2026-03-15 | succeeded | 38 | 13.7 min | central-template-consumer |
| 105 | risk-batch-legacy | `services/risk-batch/azure-pipelines-legacy.yml` | `\Services\risk-batch` | **enabled** | Azure Pipelines (hosted) | 2026-01-10 | succeeded | 2 | 8.7 min | central-template-consumer |
| 106 | frontend-workbench-ci | `services/frontend-workbench/azure-pipelines.yml` | `\Services\frontend-workbench` | **enabled** | Azure Pipelines (hosted) | 2026-03-16 | succeeded | 62 | 12.3 min | alt-template-consumer |
| 107 | regulatory-reporting-ci | `services/regulatory-reporting/azure-pipelines.yml` | `\Services\regulatory-reporting` | **enabled** | Azure Pipelines (hosted) | 2026-03-17 | succeeded | 65 | 82.4 min | hybrid |
| 108 | market-sim-ci | `services/market-sim/azure-pipelines.yml` | `\Services\market-sim` | **enabled** | Azure Pipelines (hosted) | 2026-03-08 | succeeded | 18 | 23.4 min | custom-inline |
| 109 | ops-control-plane-ci | `services/ops-control-plane/azure-pipelines.yml` | `\Services\ops-control-plane` | **enabled** | Azure Pipelines (hosted) | 2026-03-13 | succeeded | 25 | 7.8 min | custom-inline |
| 110 | notebook-executor-nightly | `services/notebook-executor/azure-pipelines.yml` | `\Night Jobs\notebook-executor` | **enabled** | linux-build-workers (self-hosted) | 2026-03-17 | partiallySucceeded | 90 | 165.2 min | non-build-workload |
| 111 | scenario-runner-weekly | `services/scenario-runner/azure-pipelines.yml` | `\Night Jobs\scenario-runner` | **enabled** | high-memory-pool (self-hosted) | 2026-03-14 | succeeded | 13 | 228.1 min | non-build-workload |
| 112 | var-scenario-sweep-nightly | `night-jobs/compute/var-scenario-sweep.yml` | `\Night Jobs\Compute` | **enabled** | high-memory-pool (self-hosted) | 2026-03-17 | succeeded | 65 | 172.2 min | non-build-workload |
| 113 | daily-positions-export | `night-jobs/business/daily-positions-export.yml` | `\Night Jobs\Business` | **enabled** | linux-build-workers (self-hosted) | 2026-03-16 | succeeded | 65 | 75.5 min | non-build-workload |
| 114 | attestation-backfill-weekly | `night-jobs/compliance/attestation-backfill.yml` | `\Night Jobs\Compliance` | **enabled** | linux-build-workers (self-hosted) | 2026-03-16 | succeeded | 13 | 93.3 min | non-build-workload |
| 115 | bulk-reprocess-trades | `adhoc/bulk-reprocess-trades.yml` | `\Ad Hoc` | **enabled** | Azure Pipelines (hosted) | 2026-02-25 | succeeded | 3 | 325.1 min | adhoc |
| 116 | onetime-data-migration | `adhoc/onetime-data-migration.yml` | `\Ad Hoc` | **paused** | Azure Pipelines (hosted) | 2024-08-20 | succeeded | 1 | 222.8 min | adhoc-stale |
| 117 | old-pricing-pipeline | `deprecated/old-pricing-pipeline.yml` | `\Deprecated` | **disabled** | Azure Pipelines (hosted) | 2023-06-15 | succeeded | 0 | -- | deprecated |
| 118 | batch-runner-v1 | `deprecated/batch-runner-v1.yml` | `\Deprecated` | **disabled** | Azure Pipelines (hosted) | 2023-02-01 | failed | 0 | -- | deprecated |

### Dead Pipelines (skip in migration)

The following pipelines are **dead** (0 runs in 90 days AND disabled/paused state) and can be safely skipped during migration:

| ID | Name | Status | Last Run | Reason |
|----|------|--------|----------|--------|
| 116 | onetime-data-migration | **paused** | 2024-08-20 (19 months ago) | One-time migration, should have been deleted. |
| 117 | old-pricing-pipeline | **disabled** | 2023-06-15 (33 months ago) | Replaced by pricing-engine-ci (ID 101). |
| 118 | batch-runner-v1 | **disabled** | 2023-02-01 (37 months ago) | Replaced by risk-batch-ci + night-jobs. Last run failed. |

### Near-Dead Pipelines (verify before skipping)

| ID | Name | Status | Last Run | 90d Runs | Concern |
|----|------|--------|----------|----------|---------|
| 105 | risk-batch-legacy | enabled | 2026-01-10 (67 days ago) | 2 | Trigger disabled in YAML but still externally triggered. Verify downstream dependencies before removing. |

---

## 2. Pipeline Classification

### Category 1: Central Template Consumers (5 pipelines)
Use templates from `templates/` via repository resource references.

| Pipeline | Template Branch | Templates Used |
|----------|----------------|---------------|
| pricing-engine-ci (101) | `main` | `templates/build/build-dotnet.yml`, `templates/test/run-tests.yml`, `templates/release/release-standard.yml` |
| portfolio-api-ci (102) | `master` (legacy) | `templates/build/build-java.yml`, `templates/release/release-standard.yml` |
| portfolio-api-canary (103) | `main`/`master`/`staging/preprod`/`staging/release-hardening` (parameterized) | `templates/build/build-java.yml` |
| risk-batch-ci (104) | `staging/preprod` | `templates/build/build-python.yml`, `templates/test/run-tests.yml`, `templates/release/release-standard.yml` |
| risk-batch-legacy (105) | `legacy/master-support` | `templates/legacy/build-python-legacy.yml` |

### Category 2: Alt-Template Consumers (1 pipeline)
Use templates from `alt-templates/` maintained by team branches.

| Pipeline | Template Branch | Templates Used |
|----------|----------------|---------------|
| frontend-workbench-ci (106) | `team/frontend-custom` | `alt-templates/frontend/frontend-build.yml`, `alt-templates/frontend/frontend-deploy.yml` |

### Category 3: Hybrid (1 pipeline)
Combines team-override templates with inline steps.

| Pipeline | Template Branch | Templates Used | Inline Steps |
|----------|----------------|---------------|-------------|
| regulatory-reporting-ci (107) | `team/reporting-hotfix` | `alt-templates/team-overrides/team-build-custom.yml` | Report generation, compliance metadata upload, attestation generation |

### Category 4: Custom Inline (2 pipelines)
Fully inline YAML with no shared template usage.

| Pipeline | Language | Notes |
|----------|---------|-------|
| market-sim-ci (108) | Rust | Built independently by team-quant. Deploys to compute cluster outside release-orchestrator. |
| ops-control-plane-ci (109) | Go | Central templates now have `build-go.yml` but this predates it. Candidate for template migration. |

### Category 5: Non-Build Workloads (5 pipelines)
Operational jobs misusing CI infrastructure for compute. **Should NOT migrate to GHA hosted runners.**

| Pipeline | Workload Type | Pool | Schedule | Timeout |
|----------|-------------|------|----------|---------|
| notebook-executor-nightly (110) | Jupyter notebook execution | linux-build-workers | Daily 02:00 UTC | 180 min |
| scenario-runner-weekly (111) | Monte Carlo simulations | high-memory-pool | Fridays 22:00 UTC | 360 min |
| var-scenario-sweep-nightly (112) | VaR calculations (50K scenarios) | high-memory-pool | Weeknights 01:00 UTC | 240 min |
| daily-positions-export (113) | Data export (positions DB) | linux-build-workers | Weekdays 23:00 UTC | 120 min |
| attestation-backfill-weekly (114) | Compliance backfill | linux-build-workers | Sundays 03:00 UTC | 180 min |

### Category 6: Ad-Hoc & Deprecated (3 pipelines)

| Pipeline | Sub-Type | Status | Recommendation |
|----------|---------|--------|---------------|
| bulk-reprocess-trades (115) | adhoc | enabled | Keep as manual workflow; last used Feb 2026 |
| onetime-data-migration (116) | adhoc-stale | **paused** | **DELETE** -- one-time job from Aug 2024 |
| old-pricing-pipeline (117) | deprecated | **disabled** | **SKIP** -- replaced by ID 101 |
| batch-runner-v1 (118) | deprecated | **disabled** | **SKIP** -- replaced by risk-batch + night-jobs |

---

## 3. Template Dependency Map

### Branch-to-Consumer Mapping

| Branch | Templates Modified (vs main) | Consuming Pipelines | Status |
|--------|----------------------------|---------------------|--------|
| `main` | Canonical (reference) | pricing-engine-ci (101), portfolio-api-canary (103, default) | Active, maintained |
| `master` | `build-python.yml` (Python 3.10, linting off), `build-dotnet.yml` (.NET 6.0) | portfolio-api-ci (102), portfolio-api-canary (103, option) | Legacy, should merge to main |
| `staging/preprod` | `build-python.yml` (retry logic, preprod stamp) | risk-batch-ci (104), portfolio-api-canary (103, option) | Active, unmaintained |
| `staging/release-hardening` | `release-standard.yml` (mandatory approvals, pre-deploy validation, health checks) | portfolio-api-canary (103, option) | Unclear, may be unused |
| `team/frontend-custom` | `frontend-build.yml` (Lighthouse CI, build-ID suffix), `build-node.yml` (SSR, Storybook) | frontend-workbench-ci (106) | Active |
| `team/quant-experiments` | `build-python.yml` (conda support, GPU pool, extended timeouts) | Possibly scenario-runner, notebook-executor | Unknown status |
| `team/reporting-hotfix` | `team-build-custom.yml` (audit trail, pre-build compliance validation) | regulatory-reporting-ci (107) | Active |
| `legacy/master-support` | `build-python.yml` (Python 3.8, linting off, FROZEN), `build-dotnet.yml` (.NET 6.0, FROZEN) | risk-batch-legacy (105), old-pricing-pipeline (117, deprecated) | Frozen |

### Template Files and Their Consumers

| Template File | Location | Consumed By (Pipeline IDs) |
|---------------|----------|--------------------------|
| `templates/build/build-dotnet.yml` | Central | 101 |
| `templates/build/build-java.yml` | Central | 102, 103 |
| `templates/build/build-python.yml` | Central | 104 (via staging/preprod) |
| `templates/build/build-node.yml` | Central | (consumed via team/frontend-custom branch) |
| `templates/build/build-go.yml` | Central | Not currently consumed (ops-control-plane uses inline Go) |
| `templates/build/build-rust.yml` | Central | Not currently consumed (market-sim uses inline Rust) |
| `templates/test/run-tests.yml` | Central | 101, 104 |
| `templates/release/release-standard.yml` | Central | 101, 102, 104 |
| `templates/release/release-prod.yml` | Central | Not currently consumed |
| `templates/release/release-hotfix.yml` | Central | Not currently consumed |
| `templates/release/release-preprod.yml` | Central | Not currently consumed |
| `templates/legacy/build-python-legacy.yml` | Legacy | 105 |
| `templates/legacy/release-old.yml` | Legacy | Not currently consumed |
| `alt-templates/frontend/frontend-build.yml` | Alt | 106 |
| `alt-templates/frontend/frontend-deploy.yml` | Alt | 106 |
| `alt-templates/team-overrides/team-build-custom.yml` | Alt | 107 |
| `alt-templates/data-science/build-python.yml` | Alt | Not currently consumed by any registered pipeline |
| `alt-templates/data-science/ds-model-build.yml` | Alt | Not currently consumed |
| `alt-templates/data-science/python-batch.yml` | Alt | Not currently consumed |
| `alt-templates/data-science/notebook-package-build.yml` | Alt | Not currently consumed |
| `build-tools/yaml/common-setup.yml` | Helper | Not directly referenced in any pipeline YAML |
| `build-tools/yaml/publish-helpers.yml` | Helper | Not directly referenced in any pipeline YAML |
| `build-tools/release/release-notify.yml` | Helper | Not directly referenced in any pipeline YAML |
| `services/risk-batch/pipeline-fragments/build-python-local.yml` | Service-local fork | Not currently referenced (fallback only) |

---

## 4. Non-Build Workload Analysis

7 pipelines are non-build workloads that should NOT migrate to GitHub Actions hosted runners.

### 4.1 Jupyter Notebook Execution (ID 110: notebook-executor-nightly)
- **What:** Executes model validation Jupyter notebooks nightly using `papermill`
- **Pool:** linux-build-workers (self-hosted, 16GB RAM, internal network)
- **Schedule:** Daily at 02:00 UTC
- **Timeout:** 180 min (avg 165.2 min)
- **Dependencies:** jupyter, nbconvert, papermill, numpy, pandas, scipy, scikit-learn
- **Network needs:** Internal network access
- **Migration target:** Dedicated Kubernetes CronJob or Azure Container Instances

### 4.2 Monte Carlo Simulations (ID 111: scenario-runner-weekly)
- **What:** Runs parameterized Monte Carlo simulations (default: 10,000 scenarios)
- **Pool:** high-memory-pool (self-hosted, 128GB RAM, 32 cores)
- **Schedule:** Fridays at 22:00 UTC + manual with custom parameters
- **Timeout:** 360 min (avg 228.1 min)
- **Dependencies:** numpy, pandas, scipy, pyarrow
- **Network needs:** Internal network + high-memory compute + compute-cluster access
- **Migration target:** AWS Batch / Azure Batch / K8s Jobs with high-memory nodes

### 4.3 VaR Scenario Sweep (ID 112: var-scenario-sweep-nightly)
- **What:** Nightly VaR calculations across 50,000 scenarios at 95/99/99.9% confidence
- **Pool:** high-memory-pool (self-hosted, 128GB RAM, 32 cores)
- **Schedule:** Weeknights at 01:00 UTC
- **Timeout:** 240 min (avg 172.2 min)
- **Dependencies:** numpy, pandas, scipy, pyarrow, requests
- **Network needs:** Internal network, data-warehouse upload
- **Migration target:** AWS Batch / Azure Batch / K8s Jobs

### 4.4 Daily Positions Export (ID 113: daily-positions-export)
- **What:** Exports positions data to downstream reporting via pyodbc + generates Excel summaries
- **Pool:** linux-build-workers (self-hosted, internal network)
- **Schedule:** Weekdays at 23:00 UTC (7 PM ET)
- **Timeout:** 120 min (avg 75.5 min)
- **Dependencies:** pandas, pyodbc, sqlalchemy, openpyxl, requests
- **Network needs:** positions-db, internal-smtp
- **Migration target:** Scheduled Azure Function / AWS Lambda + Step Functions / K8s CronJob

### 4.5 Attestation Backfill (ID 114: attestation-backfill-weekly)
- **What:** Scans compliance-store for attestation gaps and regenerates missing records
- **Pool:** linux-build-workers (self-hosted, internal network)
- **Schedule:** Sundays at 03:00 UTC
- **Timeout:** 180 min (avg 93.3 min)
- **Dependencies:** requests, pandas, `build-tools/compliance/generate_metadata.py`
- **Network needs:** compliance-store (attestation-database)
- **Migration target:** K8s CronJob with compliance-store network access

### 4.6 Bulk Trade Reprocessing (ID 115: bulk-reprocess-trades)
- **What:** Manual pipeline for reprocessing trades after data corrections
- **Pool:** Azure Pipelines (hosted)
- **Schedule:** Manual only
- **Timeout:** 480 min (avg 325.1 min)
- **Migration target:** Manual GHA workflow_dispatch or dedicated data pipeline

### 4.7 Regulatory Reporting (ID 107: regulatory-reporting-ci -- partial)
- **What:** Classified as "hybrid" -- looks like a build but is really a compliance reporting workflow
- **Schedule:** Weekdays at 06:00 UTC + CI trigger
- **Timeout:** 90 min for report generation stage (avg 82.4 min total)
- **Notes:** Generates regulatory reports, validates compliance metadata, uploads attestation records. Does NOT produce a deployable artifact. 365-day retention for audit.

---

## 5. Ownership Summary

### Confirmed Owners

| Owner | Pipelines | Templates | Confidence |
|-------|-----------|-----------|-----------|
| team-frontend | frontend-workbench-ci (106) | alt-templates/frontend/, templates/build/build-node.yml (on team/frontend-custom branch) | **High** |
| team-reporting | regulatory-reporting-ci (107), daily-positions-export (113) | alt-templates/team-overrides/ (on team/reporting-hotfix branch) | **High** |
| team-quant | portfolio-api-ci (102), portfolio-api-canary (103), risk-batch-ci (104), risk-batch-legacy (105), market-sim-ci (108), var-scenario-sweep (112) | staging/preprod branch, team/quant-experiments branch, alt-templates/data-science/ | **Medium-High** |
| platform-team | ops-control-plane-ci (109) | -- | **Medium** |
| shared-ci-platform | attestation-backfill-weekly (114) | Central templates (templates/) | **Medium** |

### Unknown / Unconfirmed Owners

| Pipeline | ADO Metadata | Last Modified By | Notes |
|----------|-------------|-----------------|-------|
| pricing-engine-ci (101) | owner: unknown | contractor-account@contoso.com | Original team disbanded. shared-ci-platform maintains as best-effort. |
| notebook-executor-nightly (110) | owner: unknown | unknown-service-account@contoso.com | No owner identified. Runs nightly, nobody claims it. |
| scenario-runner-weekly (111) | owner: unknown | unknown-service-account@contoso.com | Appears to be team-quant but unconfirmed. |
| bulk-reprocess-trades (115) | owner: unknown | unknown-service-account@contoso.com | Unclear ownership. |
| onetime-data-migration (116) | owner: unknown | unknown-service-account@contoso.com | Should be deleted. |

### Action Items
- Confirm pricing-engine ownership (currently orphaned)
- Assign owner to notebook-executor or schedule decommission
- Confirm scenario-runner belongs to team-quant
- Delete onetime-data-migration (paused, 19 months stale)

---

## 6. Template Duplication Findings

### Duplicate Set 1: Python Build Templates (4 copies)

| Location | Python Default | Linting | Test Framework | Retry Logic | Conda | Artifact Registry |
|----------|---------------|---------|---------------|-------------|-------|------------------|
| `templates/build/build-python.yml` (main) | 3.11 | flake8+black+mypy | pytest | No | No | Yes |
| `templates/legacy/build-python-legacy.yml` | 3.9 | **None** | **unittest** | No | No | **No** |
| `alt-templates/data-science/build-python.yml` | 3.10 | **None** | pytest | No | **Param** | **No** |
| `services/risk-batch/pipeline-fragments/build-python-local.yml` | 3.11 | **None** | pytest | **Yes (configurable)** | No | **No** |

**Recommendation:** Consolidate into single `build-python.yml` with parameters for retry, conda, and linting toggles.

### Duplicate Set 2: Data Science Templates (3 near-identical copies)

| Location | Purpose | Differences from build-python.yml |
|----------|---------|----------------------------------|
| `alt-templates/data-science/build-python.yml` | DS Python build | Adds `runNotebooks` parameter, installs DS packages |
| `alt-templates/data-science/ds-model-build.yml` | DS model packaging | Near-identical to build-python.yml without notebook support |
| `alt-templates/data-science/notebook-package-build.yml` | Notebook packaging | Near-identical to ds-model-build.yml, adds jupyter install |

**Recommendation:** Merge into single `data-science-build.yml` with feature toggles. NOTE: None of these are referenced by any registered pipeline.

### Duplicate Set 3: Release Templates (4 variants)

| Location | Approval Gate | Compliance Attestation | Release-Orchestrator Notify | Health Check |
|----------|-------------|----------------------|---------------------------|-------------|
| `templates/release/release-standard.yml` | Configurable | Yes | Yes | No |
| `templates/release/release-prod.yml` | Implicit (prod env) | Validation only | Yes | No |
| `templates/release/release-hotfix.yml` | None (bypass) | Configurable (hotfix mode) | No | No |
| `templates/legacy/release-old.yml` | None | **No** | **No** | No |

**Recommendation:** Consolidate into single release workflow with environment-based behavior.

### Duplicate Set 4: Node.js Build Templates (2 divergent copies)

| Location | Branch | SSR Support | Storybook | Lighthouse CI | Node Default |
|----------|--------|-------------|-----------|--------------|-------------|
| `templates/build/build-node.yml` (main) | main | No | No | No | 20.x |
| `templates/build/build-node.yml` (team/frontend-custom) | team/frontend-custom | **Yes** | **Yes** | No | 18.x |
| `alt-templates/frontend/frontend-build.yml` (team/frontend-custom) | team/frontend-custom | **Yes** | No | **Yes** | 18.x |

**Recommendation:** Merge SSR/Storybook into central `build-node.yml` with optional parameters.

---

## 7. Risk Flags for Migration

### Critical Risks

| Risk | Affected Pipelines | Impact | Mitigation |
|------|-------------------|--------|-----------|
| **Self-hosted pools with internal network** | 110, 111, 112, 113, 114 | Cannot use GHA hosted runners. Need network peering or self-hosted GHA runners. | Deploy self-hosted GHA runners in same network segment, or migrate workloads to dedicated infrastructure. |
| **High-memory compute requirements** | 111, 112 | 128GB RAM, 32 cores needed. GHA `ubuntu-latest` has 7GB RAM. Even `ubuntu-latest-16-cores` maxes at 64GB. | Use dedicated compute (K8s, AWS Batch) instead of GHA. These are non-build workloads. |
| **Long timeouts exceeding GHA limits** | 111 (360m), 115 (480m), 116 (300m), 112 (240m), 110 (180m) | GHA hosted runners have 6-hour max. Self-hosted have no limit. 115's 480 min is close to the 6hr limit. | Move long-running workloads off GHA entirely. |
| **ADO-specific tasks with no direct GHA equivalent** | All template consumers | `UsePythonVersion@0`, `UseDotNet@2`, `JavaToolInstaller@0`, `GoTool@0`, `Maven@4`, `NuGetCommand@2`, `PublishBuildArtifacts@1`, `PublishTestResults@2`, `ArchiveFiles@2`, `DownloadBuildArtifacts@1` | Map to GHA equivalents: `actions/setup-python`, `actions/setup-dotnet`, `actions/setup-java`, `actions/setup-go`, `actions/upload-artifact`, etc. |

### High Risks

| Risk | Affected Pipelines | Impact |
|------|-------------------|--------|
| **Template branch drift** | 102, 103, 104, 105, 106, 107 | 7 branches with divergent template logic. Must decide which variant becomes the canonical GHA reusable workflow. |
| **Variable-driven template selection** | 103 (canary) | Uses `${{ parameters.templateBranch }}` to conditionally select from 4 template branches. No direct GHA equivalent for dynamic workflow selection. |
| **ADO variable syntax** | All pipelines | `$(Build.BuildId)`, `$(Build.SourceBranch)`, `$(Agent.MachineName)`, `$(system.defaultWorkingDirectory)`, `$[format()]` must be converted to `${{ github.run_id }}`, `${{ github.ref }}`, etc. |
| **Deployment jobs with environment gates** | 101, 102, 104, 106, 107 | ADO `deployment` job type with `environment:` and `strategy: runOnce` must map to GHA environment protection rules. |
| **365-day retention** | 107, 114 | ADO supports per-pipeline retention. GHA artifact retention max is 90 days. Need external artifact storage for audit compliance. |

### Medium Risks

| Risk | Affected Pipelines |
|------|-------------------|
| `##vso[task.prependpath]` and `##vso[task.logissue]` logging commands | 108 (market-sim), 110 (notebook-executor) |
| `pool.demands` for agent capabilities | 110, 111, 112, 113 |
| `scheduleOnlyWithChanges: false` (run even without changes) | 107, 110, 111, 112, 113, 114 |
| Pipeline parameters with `values:` constraint | 103, 108, 111 |
| `DownloadBuildArtifacts@1` vs `download: current` pattern | 117 (legacy) |

---

## 8. Branch Analysis with Actual Diffs

### 8.1 `main` (canonical reference)
No diff -- this is the canonical branch. All other branches are compared against it.

### 8.2 `master` vs `main`

```diff
diff --git a/templates/build/build-dotnet.yml b/templates/build/build-dotnet.yml
index d035442..44aaeb9 100644
--- a/templates/build/build-dotnet.yml
+++ b/templates/build/build-dotnet.yml
@@ -1,6 +1,6 @@
 # Central .NET build template
 # Maintained by: shared-ci-platform team
-# Last reviewed: 2024-08
+# Last reviewed: 2023-09
 
 parameters:
   - name: solution
@@ -11,7 +11,7 @@ parameters:
     default: 'Release'
   - name: dotnetVersion
     type: string
-    default: '8.0.x'
+    default: '6.0.x'
   - name: publishArtifacts
     type: boolean
     default: true
diff --git a/templates/build/build-python.yml b/templates/build/build-python.yml
index beae707..c6bb061 100644
--- a/templates/build/build-python.yml
+++ b/templates/build/build-python.yml
@@ -1,11 +1,11 @@
 # Central Python build template
 # Maintained by: shared-ci-platform team
-# Last reviewed: 2024-06
+# Last reviewed: 2023-11
 
 parameters:
   - name: pythonVersion
     type: string
-    default: '3.11'
+    default: '3.10'
   - name: requirementsFile
     type: string
     default: 'requirements.txt'
@@ -23,10 +23,10 @@ parameters:
     default: true
   - name: artifactName
     type: string
-    default: 'python-dist'
+    default: 'python-package'
   - name: enableLinting
     type: boolean
-    default: true
+    default: false
```

**Summary:** `master` is behind `main`. Python defaults to 3.10 (vs 3.11), linting disabled, .NET defaults to 6.0 (vs 8.0). portfolio-api-ci (102) still references this branch.

### 8.3 `staging/preprod` vs `main`

```diff
diff --git a/templates/build/build-python.yml b/templates/build/build-python.yml
index beae707..6e5b560 100644
--- a/templates/build/build-python.yml
+++ b/templates/build/build-python.yml
@@ -1,6 +1,7 @@
 # Central Python build template
 # Maintained by: shared-ci-platform team
 # Last reviewed: 2024-06
+# Modified on staging/preprod: added retry logic for flaky tests (team-quant request)
 
 parameters:
   - name: pythonVersion
@@ -27,6 +28,9 @@ parameters:
   - name: enableLinting
     type: boolean
     default: true
+  - name: testRetryCount
+    type: number
+    default: 3
 
 steps:
   - task: UsePythonVersion@0
@@ -48,12 +52,23 @@ steps:
 
   - ${{ if eq(parameters.runTests, true) }}:
     - script: |
-        pip install pytest pytest-cov pytest-junitxml
-        pytest tests/ \
+        pip install pytest pytest-cov pytest-junitxml pytest-rerunfailures
+        RETRY=0
+        MAX_RETRY=${{ parameters.testRetryCount }}
+        until pytest tests/ \
           --junitxml=$(Build.ArtifactStagingDirectory)/test-results.xml \
           --cov=src/ \
-          --cov-report=xml:$(Build.ArtifactStagingDirectory)/coverage.xml
-      displayName: 'Run tests with coverage'
+          --cov-report=xml:$(Build.ArtifactStagingDirectory)/coverage.xml \
+          --reruns 2 --reruns-delay 5; do
+          RETRY=$((RETRY + 1))
+          if [ $RETRY -ge $MAX_RETRY ]; then
+            echo "Tests failed after $MAX_RETRY retries"
+            exit 1
+          fi
+          echo "Test retry $RETRY of $MAX_RETRY..."
+          sleep 10
+        done
+      displayName: 'Run tests with coverage (retry-enabled)'
 
     - task: PublishTestResults@2
       displayName: 'Publish test results'
@@ -80,3 +95,8 @@ steps:
           --registry artifact-registry \
           --build-id $(Build.BuildId)
       displayName: 'Register artifact in artifact-registry'
+
+    - script: |
+        echo "Preprod artifact validation stamp"
+        echo "$(Build.BuildId)" > $(Build.ArtifactStagingDirectory)/preprod-stamp.txt
+      displayName: 'Stamp preprod validation marker'
```

**Summary:** Adds test retry logic (`testRetryCount` param, pytest-rerunfailures, shell retry loop) and a preprod validation stamp to the Python build template. Consumed by risk-batch-ci (104).

### 8.4 `staging/release-hardening` vs `main`

```diff
diff --git a/templates/release/release-standard.yml b/templates/release/release-standard.yml
index 7f5c07d..8fb5935 100644
--- a/templates/release/release-standard.yml
+++ b/templates/release/release-standard.yml
@@ -1,5 +1,6 @@
 # Central release pipeline template
 # Maintained by: shared-ci-platform team
+# Modified on staging/release-hardening: added pre-deploy validation and mandatory approvals
 
 parameters:
   - name: environment
@@ -19,10 +20,16 @@ parameters:
       - canary
   - name: requireApproval
     type: boolean
-    default: false
+    default: true
   - name: notifyReleaseOrchestrator
     type: boolean
     default: true
+  - name: runPreDeployValidation
+    type: boolean
+    default: true
+  - name: healthCheckRetries
+    type: number
+    default: 5
 
 stages:
   - stage: Deploy_${{ parameters.environment }}
@@ -42,11 +49,33 @@ stages:
                 - download: current
                   artifact: ${{ parameters.artifactName }}
 
+                - ${{ if eq(parameters.runPreDeployValidation, true) }}:
+                  - script: |
+                      echo "Running pre-deploy validation..."
+                      python $(Build.SourcesDirectory)/build-tools/scripts/compare_build_outputs.py \
+                        --artifact ${{ parameters.artifactName }} \
+                        --baseline $(Build.SourcesDirectory)/validation/baselines/
+                    displayName: 'Pre-deploy artifact validation'
+
                 - script: |
                     echo "Deploying ${{ parameters.artifactName }} to ${{ parameters.environment }}"
                     echo "Strategy: ${{ parameters.deployStrategy }}"
                   displayName: 'Execute deployment'
 
+                - script: |
+                    RETRY=0
+                    MAX_RETRY=${{ parameters.healthCheckRetries }}
+                    until curl -sf http://localhost:8080/health; do
+                      RETRY=$((RETRY + 1))
+                      if [ $RETRY -ge $MAX_RETRY ]; then
+                        echo "Health check failed after $MAX_RETRY attempts"
+                        exit 1
+                      fi
+                      echo "Health check retry $RETRY/$MAX_RETRY..."
+                      sleep 15
+                    done
+                  displayName: 'Post-deploy health check (hardened)'
+
                 - ${{ if eq(parameters.notifyReleaseOrchestrator, true) }}:
                   - script: |
                       python $(Build.SourcesDirectory)/build-tools/scripts/notify_release_orchestrator.py \
```

**Summary:** Hardens `release-standard.yml` with: mandatory approval default, pre-deploy artifact baseline validation, post-deploy health check with retries. No confirmed consumers -- may be unused.

### 8.5 `team/frontend-custom` vs `main`

```diff
diff --git a/alt-templates/frontend/frontend-build.yml b/alt-templates/frontend/frontend-build.yml
index 5adba85..c2243bf 100644
--- a/alt-templates/frontend/frontend-build.yml
+++ b/alt-templates/frontend/frontend-build.yml
@@ -51,8 +51,12 @@ steps:
       archiveType: 'zip'
       archiveFile: '$(Build.ArtifactStagingDirectory)/${{ parameters.artifactName }}.zip'
 
+  - script: |
+      npx lhci autorun --collect.staticDistDir=build/ || true
+    displayName: 'Run Lighthouse CI audit'
+
   - task: PublishBuildArtifacts@1
     displayName: 'Upload frontend bundle'
     inputs:
       pathToPublish: '$(Build.ArtifactStagingDirectory)'
-      artifactName: ${{ parameters.artifactName }}
+      artifactName: '${{ parameters.artifactName }}-$(Build.BuildId)'
diff --git a/templates/build/build-node.yml b/templates/build/build-node.yml
index 5f7c374..0fd769f 100644
--- a/templates/build/build-node.yml
+++ b/templates/build/build-node.yml
@@ -1,11 +1,12 @@
 # Central Node.js build template
 # Maintained by: shared-ci-platform team
 # Last reviewed: 2024-07
+# Modified by team-frontend: SSR support, Storybook build, custom webpack
 
 parameters:
   - name: nodeVersion
     type: string
-    default: '20.x'
+    default: '18.x'
   - name: packageManager
     type: string
     default: 'npm'
@@ -24,6 +25,12 @@ parameters:
   - name: artifactName
     type: string
     default: 'node-dist'
+  - name: enableSSR
+    type: boolean
+    default: true
+  - name: buildStorybook
+    type: boolean
+    default: false
 
 steps:
   - task: NodeTool@0
@@ -42,6 +49,14 @@ steps:
   - script: ${{ parameters.packageManager }} run ${{ parameters.buildScript }}
     displayName: 'Build project'
 
+  - ${{ if eq(parameters.enableSSR, true) }}:
+    - script: ${{ parameters.packageManager }} run build:ssr
+      displayName: 'Build SSR bundle'
+
+  - ${{ if eq(parameters.buildStorybook, true) }}:
+    - script: ${{ parameters.packageManager }} run build-storybook
+      displayName: 'Build Storybook'
+
   - ${{ if eq(parameters.runTests, true) }}:
     - script: ${{ parameters.packageManager }} test -- --ci --reporters=jest-junit
       displayName: 'Run tests'
```

**Summary:** Two changes: (1) `frontend-build.yml` adds Lighthouse CI audit step and appends build ID to artifact name. (2) `build-node.yml` adds SSR and Storybook build parameters, defaults Node to 18.x. Consumed by frontend-workbench-ci (106).

### 8.6 `team/quant-experiments` vs `main`

```diff
diff --git a/templates/build/build-python.yml b/templates/build/build-python.yml
index beae707..d986ba1 100644
--- a/templates/build/build-python.yml
+++ b/templates/build/build-python.yml
@@ -1,6 +1,7 @@
 # Central Python build template
 # Maintained by: shared-ci-platform team
 # Last reviewed: 2024-06
+# Modified by team-quant: added conda support, GPU pool option, extended timeouts
 
 parameters:
   - name: pythonVersion
@@ -27,6 +28,18 @@ parameters:
   - name: enableLinting
     type: boolean
     default: true
+  - name: useConda
+    type: boolean
+    default: false
+  - name: condaEnvironmentFile
+    type: string
+    default: 'environment.yml'
+  - name: useGpuPool
+    type: boolean
+    default: false
+  - name: timeoutMinutes
+    type: number
+    default: 60
 
 steps:
   - task: UsePythonVersion@0
@@ -34,10 +47,17 @@ steps:
     inputs:
       versionSpec: ${{ parameters.pythonVersion }}
 
-  - script: |
-      python -m pip install --upgrade pip setuptools wheel
-      pip install -r ${{ parameters.requirementsFile }}
-    displayName: 'Install dependencies'
+  - ${{ if eq(parameters.useConda, true) }}:
+    - script: |
+        conda env create -f ${{ parameters.condaEnvironmentFile }} || conda env update -f ${{ parameters.condaEnvironmentFile }}
+        conda activate $(basename ${{ parameters.condaEnvironmentFile }} .yml)
+      displayName: 'Setup conda environment'
+
+  - ${{ if eq(parameters.useConda, false) }}:
+    - script: |
+        python -m pip install --upgrade pip setuptools wheel
+        pip install -r ${{ parameters.requirementsFile }}
+      displayName: 'Install dependencies'
 
   - ${{ if eq(parameters.enableLinting, true) }}:
     - script: |
```

**Summary:** Adds conda environment support (`useConda`, `condaEnvironmentFile`), GPU pool option, and extended timeout parameters to `build-python.yml`. Dependency install becomes conditional (conda vs pip). No confirmed consumers.

### 8.7 `team/reporting-hotfix` vs `main`

```diff
diff --git a/alt-templates/team-overrides/team-build-custom.yml b/alt-templates/team-overrides/team-build-custom.yml
index 942902e..fd826cb 100644
--- a/alt-templates/team-overrides/team-build-custom.yml
+++ b/alt-templates/team-overrides/team-build-custom.yml
@@ -2,6 +2,7 @@
 # Created by: team-reporting
 # Reason: Needed extra compliance metadata generation that central templates don't provide
 # This template wraps the central build and adds compliance steps
+# HOTFIX: Added audit trail logging and pre-build compliance validation (2024-07)
 
 parameters:
   - name: language
@@ -27,7 +28,18 @@ steps:
   - script: |
       echo "Build initiated with compliance level: ${{ parameters.complianceLevel }}"
       echo "Language: ${{ parameters.language }}"
-    displayName: 'Log compliance context'
+      echo "Audit trail: $(Build.BuildId) | $(Build.RequestedFor) | $(Build.SourceBranch)"
+      echo "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
+    displayName: 'Log compliance context with audit trail'
+
+  - script: |
+      echo "Pre-build compliance validation..."
+      python $(Build.SourcesDirectory)/build-tools/compliance/generate_metadata.py \
+        --artifact pre-build-check \
+        --compliance-level ${{ parameters.complianceLevel }} \
+        --build-id $(Build.BuildId) \
+        --store compliance-store
+    displayName: 'Pre-build compliance validation'
 
   - ${{ if eq(parameters.language, 'python') }}:
     - task: UsePythonVersion@0
@@ -58,6 +70,12 @@ steps:
           --store compliance-store
       displayName: 'Generate compliance metadata'
 
+    - script: |
+        echo "Generating audit trail record..."
+        echo '{"build_id": "$(Build.BuildId)", "compliance_level": "${{ parameters.complianceLevel }}", "status": "complete"}' \
+          > $(Build.ArtifactStagingDirectory)/audit-trail.json
+      displayName: 'Write audit trail record'
+
   - task: PublishBuildArtifacts@1
     displayName: 'Publish artifacts'
     inputs:
```

**Summary:** Adds audit trail logging (build ID, requester, branch, timestamp), pre-build compliance validation step, and post-build audit trail JSON record to `team-build-custom.yml`. Consumed by regulatory-reporting-ci (107).

### 8.8 `legacy/master-support` vs `main`

```diff
diff --git a/templates/build/build-dotnet.yml b/templates/build/build-dotnet.yml
index d035442..a2f4e4b 100644
--- a/templates/build/build-dotnet.yml
+++ b/templates/build/build-dotnet.yml
@@ -1,6 +1,7 @@
 # Central .NET build template
 # Maintained by: shared-ci-platform team
-# Last reviewed: 2024-08
+# Last reviewed: 2022-12
+# FROZEN: This branch is for legacy compatibility only. Do not modify.
 
 parameters:
   - name: solution
@@ -11,7 +12,7 @@ parameters:
     default: 'Release'
   - name: dotnetVersion
     type: string
-    default: '8.0.x'
+    default: '6.0.x'
   - name: publishArtifacts
     type: boolean
     default: true
diff --git a/templates/build/build-python.yml b/templates/build/build-python.yml
index beae707..74d49dc 100644
--- a/templates/build/build-python.yml
+++ b/templates/build/build-python.yml
@@ -1,11 +1,12 @@
 # Central Python build template
 # Maintained by: shared-ci-platform team
-# Last reviewed: 2024-06
+# Last reviewed: 2022-12
+# FROZEN: This branch is for legacy compatibility only. Do not modify.
 
 parameters:
   - name: pythonVersion
     type: string
-    default: '3.11'
+    default: '3.8'
   - name: requirementsFile
     type: string
     default: 'requirements.txt'
@@ -23,10 +24,10 @@ parameters:
     default: true
   - name: artifactName
     type: string
-    default: 'python-dist'
+    default: 'python-legacy-dist'
   - name: enableLinting
     type: boolean
-    default: true
+    default: false
```

**Summary:** FROZEN branch. Python defaults to 3.8 (vs 3.11), linting disabled, artifact name `python-legacy-dist`. .NET defaults to 6.0 (vs 8.0). Last reviewed 2022-12. Consumed by risk-batch-legacy (105) and deprecated old-pricing-pipeline (117).

---

## 9. Variable Group & Secret Mapping

9 ADO variable groups must be migrated to GitHub Actions secrets/variables.

| ID | Variable Group | Type | Variables | Secrets | Consuming Pipelines | GHA Equivalent |
|----|---------------|------|-----------|---------|--------------------|-|
| 201 | shared-ci-secrets | Shared | `NUGET_FEED_URL`, `PIP_INDEX_URL`, `NPM_REGISTRY` | `NUGET_API_KEY`, `NPM_TOKEN` | 101, 102, 103, 104, 105, 106, 107, 109 | **Organization secrets** (shared across all repos) |
| 205 | artifact-registry-credentials | Shared | `ARTIFACT_REGISTRY_URL` | `ARTIFACT_REGISTRY_TOKEN` | 101, 102, 104 | **Organization secrets** |
| 206 | compliance-store-credentials | Shared | `COMPLIANCE_STORE_URL` | `COMPLIANCE_STORE_TOKEN`, `COMPLIANCE_STORE_CERT_THUMBPRINT` | 107, 114 | **Organization secrets** + environment secrets for `prod` (cert thumbprint) |
| 207 | internal-network-credentials | Shared | `INTERNAL_SVC_ACCOUNT`, `INTERNAL_CA_CERT_PATH` | `INTERNAL_SVC_PASSWORD` | 110, 111, 112, 113, 115 | **Organization secrets** (only accessible from self-hosted runners) |
| 208 | risk-batch-config | Private | `RISK_MODEL_VERSION`, `RISK_BATCH_MAX_RETRIES` | `RISK_DB_CONNECTION_STRING` | 104 | **Repository secrets** (risk-batch repo) |
| 209 | regulatory-reporting-config | Private | `REPORTING_SMTP_SERVER`, `REPORTING_DISTRIBUTION_LIST` | `REPORTING_DB_CONNECTION_STRING` | 107 | **Repository secrets** (regulatory-reporting repo) |
| 210 | frontend-cdn-config | Private | `CDN_ENDPOINT`, `CDN_STORAGE_ACCOUNT` | `CDN_STORAGE_KEY`, `CDN_PURGE_API_KEY` | 106 | **Repository secrets** + consider **OIDC** for Azure CDN access |
| 211 | ops-infra-credentials | Private | `K8S_CLUSTER_URL`, `K8S_NAMESPACE` | `K8S_SERVICE_ACCOUNT_TOKEN` | 109 | **Repository secrets** + consider **OIDC** for K8s (Azure AD Workload Identity) |
| 212 | data-warehouse-credentials | Private | `DW_SCHEMA` | `DW_CONNECTION_STRING` | 112 | **Repository secrets** or **environment secrets** for compute jobs |
| 213 | positions-db-credentials | Private | -- | `POSITIONS_DB_CONNECTION_STRING`, `POSITIONS_DB_READONLY_STRING` | 113, 116 | **Repository secrets** (for positions-related workflows) |

### Migration Strategy

| ADO Construct | GHA Equivalent | Notes |
|--------------|---------------|-------|
| Shared variable group (isShared=true) | **Organization-level secrets** (`Settings > Secrets > Organization secrets`) | Scoped to selected repositories. Reduces duplication. |
| Private variable group (isShared=false) | **Repository-level secrets** (`Settings > Secrets > Actions`) | One set per consuming repo. |
| Non-secret variables (URLs, paths, config) | **Organization/repo variables** (`Settings > Variables`) | Use GHA variables (not secrets) for non-sensitive values. |
| Secret variables (isSecret=true) | **GitHub secrets** (encrypted, write-only) | Direct mapping. Reference as `${{ secrets.NAME }}`. |
| Certificate paths (INTERNAL_CA_CERT_PATH) | **Self-hosted runner configuration** | Pre-install CA certs on self-hosted runners. Not a secret per se. |
| Service account + password pattern | **OIDC (recommended)** or secrets | For Azure services, migrate to OIDC (`azure/login` action) to eliminate stored credentials. |

---

## 10. Service Connection Mapping

5 ADO service connections must be mapped to GHA authentication mechanisms.

| ADO Connection | Type | Auth Scheme | Consuming Pipelines | GHA Equivalent | Recommended Approach |
|---------------|------|-------------|--------------------|-|-|
| AzureSubscription-Dev | `azurerm` | ServicePrincipal (spnKey) | 101, 104, 106 | **OIDC with `azure/login`** | Configure Azure AD federated credentials for GHA. Use `azure/login@v2` with `client-id`, `tenant-id`, `subscription-id`. No stored secrets needed. |
| AzureSubscription-Staging | `azurerm` | ServicePrincipal (spnKey) | 102, 106 | **OIDC with `azure/login`** | Same as Dev but scoped to staging subscription. Use GHA environment `staging` to restrict access. |
| AzureSubscription-Prod | `azurerm` | ServicePrincipal (spnKey) | 107 | **OIDC with `azure/login`** + **environment protection** | Require `prod` environment approval before `azure/login`. Restrict federated credential to `environment:prod`. |
| ContainerRegistry-ACR | `dockerregistry` | ServicePrincipal | 108, 109 | **OIDC with `azure/docker-login`** or `docker/login-action` | Use `azure/docker-login@v2` with OIDC. Alternatively, store ACR admin credentials as repo secrets. |
| GitHub-SourceMirror | `github` | PersonalAccessToken | (none currently) | **Not needed** | After migration to GitHub, source is already on GitHub. This connection becomes unnecessary. |

### OIDC Migration Pattern (recommended for all Azure connections)

```yaml
# GHA equivalent of ADO AzureSubscription-Dev service connection
- name: Azure Login
  uses: azure/login@v2
  with:
    client-id: ${{ secrets.AZURE_CLIENT_ID }}
    tenant-id: ${{ secrets.AZURE_TENANT_ID }}
    subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
```

**Benefits:** No stored secrets (SPN keys). Tokens are short-lived. Scoped by repo/branch/environment via federated credential subject claims.

---

## 11. Environment & Approval Gate Mapping

6 ADO environments with approval/check configurations must be recreated as GitHub Environments.

| ADO Environment | Checks | Pipelines Using | GHA Environment | GHA Protection Rules |
|----------------|--------|----------------|----------------|---------------------|
| **dev** | None | 101, 104 | `dev` | No protection rules (auto-deploy) |
| **staging** | 1 approver (shared-ci-platform-team) | 102 | `staging` | **Required reviewers:** shared-ci-platform-team (1 reviewer). |
| **preprod** | 2 approvers (shared-ci-platform-team + release-managers) + Business hours (M-F 9-5 ET) | (none currently) | `preprod` | **Required reviewers:** shared-ci-platform-team + release-managers (2 min). **Deployment branches:** main only. *Note: GHA has no native business-hours gate; use custom action or branch protection schedule.* |
| **prod** | 2 approvers (release-managers + service-owner) + Business hours (M-Th 9-4 ET) + Exclusive lock | 107 | `prod` | **Required reviewers:** release-managers + service-owner (2 min). **Deployment branches:** main only. **Concurrency:** use `concurrency: group: prod-deploy` in workflow to enforce exclusive lock. *Note: Business hours must be enforced via custom action or OPA policy.* |
| **dev-frontend** | None | 106 | `dev-frontend` | No protection rules (auto-deploy) |
| **staging-frontend** | 1 approver (team-frontend) | 106 | `staging-frontend` | **Required reviewers:** team-frontend (1 reviewer). |

### ADO Check to GHA Mapping

| ADO Check Type | GHA Equivalent | Gap? |
|---------------|---------------|------|
| `approval` (min approvers, named groups) | **Required reviewers** on GHA environment | No gap -- direct mapping. Set min reviewers count. |
| `businessHours` (timezone, days, time window) | **No native equivalent** | **GAP.** Options: (1) Custom GitHub Action that checks time before proceeding, (2) Branch deploy action with time check, (3) External policy engine (OPA/Styra). |
| `exclusiveLock` (one deployment at a time) | **`concurrency` key** in workflow YAML | No gap. Use `concurrency: { group: "deploy-prod", cancel-in-progress: false }` to queue deployments. |

---

## 12. Agent Pool & Infrastructure Requirements

4 ADO agent pools with varying capabilities and migration implications.

### Pool 1: Azure Pipelines (Hosted)

| Property | Value |
|----------|-------|
| **Pool ID** | 9 |
| **Type** | Microsoft-hosted |
| **VM Images** | ubuntu-latest, ubuntu-20.04, windows-latest, macos-latest |
| **Pipelines Using** | 101, 102, 103, 104, 105, 106, 107, 108, 109, 115, 116, 117, 118 (13 pipelines) |
| **GHA Equivalent** | `runs-on: ubuntu-latest` (or `windows-latest`, `macos-latest`) |
| **Migration Concern** | **None.** Direct 1:1 mapping to GitHub-hosted runners. |

### Pool 2: linux-build-workers (Self-Hosted)

| Property | Value |
|----------|-------|
| **Pool ID** | 15 |
| **Type** | Self-hosted |
| **Size** | 8 agents (6 online, 2 offline) |
| **OS** | Ubuntu 22.04 |
| **Specs** | 16GB RAM, 4 CPU cores, 200GB disk |
| **Installed Tools** | python3.10, python3.11, docker, jupyter, conda |
| **Network Access** | compliance-store, positions-db, internal-smtp, data-warehouse |
| **Pipelines Using** | 110 (notebook-executor), 113 (daily-positions-export), 114 (attestation-backfill) |
| **GHA Equivalent** | **Self-hosted GHA runners** deployed in the same network segment |
| **Migration Concern** | **HIGH.** Internal network access required. Must deploy self-hosted GHA runners with equivalent network peering, OR migrate these workloads off CI entirely (recommended for non-build workloads). |

### Pool 3: high-memory-pool (Self-Hosted)

| Property | Value |
|----------|-------|
| **Pool ID** | 18 |
| **Type** | Self-hosted |
| **Size** | 4 agents (all online) |
| **OS** | Ubuntu 22.04 |
| **Specs** | **128GB RAM, 32 CPU cores, 1TB disk** |
| **Installed Tools** | python3.11, docker, numpy, scipy, pyarrow |
| **Network Access** | compliance-store, positions-db, internal-smtp, data-warehouse, compute-cluster |
| **Pipelines Using** | 111 (scenario-runner), 112 (var-scenario-sweep) |
| **GHA Equivalent** | **NOT GitHub Actions.** These are non-build compute workloads. |
| **Migration Concern** | **CRITICAL.** 128GB RAM far exceeds any GHA runner tier. These workloads should migrate to dedicated compute: **Kubernetes Jobs** (with high-memory node pools), **AWS Batch**, or **Azure Container Instances**. Do NOT attempt to run on GHA runners. |

### Pool 4: windows-build-workers (Self-Hosted, Legacy)

| Property | Value |
|----------|-------|
| **Pool ID** | 22 |
| **Type** | Self-hosted (legacy) |
| **Size** | 2 agents (1 online, 1 offline on Windows Server 2019) |
| **OS** | Windows Server 2022 / 2019 |
| **Specs** | 32GB RAM, 8 CPU cores, 500GB disk |
| **Installed Tools** | dotnet-6.0, dotnet-8.0, nuget, msbuild |
| **Network Access** | internal-smtp only |
| **Pipelines Using** | **None currently** (may be used via ADO-level pool overrides) |
| **GHA Equivalent** | `runs-on: windows-latest` (if no network dependency) |
| **Migration Concern** | **LOW.** No active consumers. Candidate for decommission after confirming no ADO-level pool overrides reference it. Half the agents are offline. |

### Infrastructure Summary

| Migration Path | Pipelines | Count | Action |
|---------------|-----------|-------|--------|
| GHA hosted runners (direct mapping) | 101-109, 115-118 | 13 | Standard migration |
| Self-hosted GHA runners (network access) | 113, 114 | 2 | Deploy runners in internal network |
| Dedicated compute (K8s/Batch) | 110, 111, 112 | 3 | Migrate off CI platform entirely |
| Decommission | windows-build-workers pool | 0 pipelines | Verify and decommission |

---

## Appendix: Summary Statistics

| Metric | Value |
|--------|-------|
| Total registered pipelines | 18 |
| Active (runs in last 90d) | 15 |
| Dead (skip in migration) | 3 (IDs 116, 117, 118) |
| CI/CD build pipelines (migrate to GHA) | 10 |
| Non-build workloads (migrate to dedicated infra) | 5 |
| Ad-hoc operational | 2 |
| Deprecated | 2 |
| Long-lived template branches | 8 |
| Template YAML files | 24 (templates/ + alt-templates/ + build-tools/yaml/) |
| Variable groups to migrate | 9 (34 variables, 14 secrets) |
| Service connections to migrate | 5 (4 Azure, 1 GitHub -- GitHub one can be dropped) |
| Environments to recreate | 6 |
| Agent pools | 4 (1 hosted, 2 self-hosted active, 1 self-hosted legacy) |
| Known owner teams | 5 |
| Pipelines with unknown ownership | 5 |
