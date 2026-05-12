# Pipeline Inventory & Classification Report

**Organization:** Contoso Financial (`contoso-financial`)
**Project:** `shared-ci-platform`
**Generated:** 2026-05-12
**Source:** ADO REST API responses (`docs/samples/ado-api-responses.json`) + repository YAML cross-reference
**Purpose:** Authoritative inventory for ADO → GitHub Actions migration planning

---

## Table of Contents

1. [Pipeline Inventory Table](#1-pipeline-inventory-table)
2. [Pipeline Classification](#2-pipeline-classification)
3. [Template Dependency Map](#3-template-dependency-map)
4. [Non-Build Workload Analysis](#4-non-build-workload-analysis)
5. [Ownership Summary](#5-ownership-summary)
6. [Template Duplication Findings](#6-template-duplication-findings)
7. [Risk Flags for Migration](#7-risk-flags-for-migration)
8. [Branch Analysis with Actual Diffs](#8-branch-analysis-with-actual-diffs)
9. [Variable Group & Secret Mapping](#9-variable-group--secret-mapping)
10. [Service Connection Mapping](#10-service-connection-mapping)
11. [Environment & Approval Gate Mapping](#11-environment--approval-gate-mapping)
12. [Agent Pool & Infrastructure Requirements](#12-agent-pool--infrastructure-requirements)

---

## 1. Pipeline Inventory Table

18 pipeline definitions registered in ADO. Cross-referenced with YAML files on disk.

| ID | Pipeline Name | YAML Path | ADO Status | Trigger | Last Run Date | Runs (90d) | Success Rate | Avg Duration | Owner | Dead? |
|----|---------------|-----------|------------|---------|---------------|------------|--------------|--------------|-------|-------|
| 101 | pricing-engine-ci | `services/pricing-engine/azure-pipelines.yml` | enabled | CI (main, release/*) | 2026-03-14 | 47 | 93.6% (44/47) | 7.5 min | unknown | No |
| 102 | portfolio-api-ci | `services/portfolio-api/azure-pipelines.yml` | enabled | CI (main, master) | 2026-03-12 | 31 | 93.5% (29/31) | 9.8 min | team-quant | No |
| 103 | portfolio-api-canary | `services/portfolio-api/azure-pipelines-canary.yml` | enabled | Manual only | 2026-02-28 | 5 | 100% (5/5) | 8.5 min | team-quant | No |
| 104 | risk-batch-ci | `services/risk-batch/azure-pipelines.yml` | enabled | CI (main) | 2026-03-15 | 38 | 92.1% (35/38) | 13.7 min | team-quant | No |
| 105 | risk-batch-legacy | `services/risk-batch/azure-pipelines-legacy.yml` | enabled | None (ext. triggered) | 2026-01-10 | 2 | 100% (2/2) | 8.7 min | team-quant | No* |
| 106 | frontend-workbench-ci | `services/frontend-workbench/azure-pipelines.yml` | enabled | CI (main, feature/*) | 2026-03-16 | 62 | 93.5% (58/62) | 12.3 min | team-frontend | No |
| 107 | regulatory-reporting-ci | `services/regulatory-reporting/azure-pipelines.yml` | enabled | CI + Schedule (weekdays 06:00 UTC) | 2026-03-17 | 65 | 93.8% (61/65) | 82.4 min | team-reporting | No |
| 108 | market-sim-ci | `services/market-sim/azure-pipelines.yml` | enabled | CI (main) | 2026-03-08 | 18 | 88.9% (16/18) | 23.4 min | team-quant | No |
| 109 | ops-control-plane-ci | `services/ops-control-plane/azure-pipelines.yml` | enabled | CI (main) | 2026-03-13 | 25 | 96.0% (24/25) | 7.8 min | platform-team | No |
| 110 | notebook-executor-nightly | `services/notebook-executor/azure-pipelines.yml` | enabled | Schedule (daily 02:00 UTC) | 2026-03-17 | 90 | 80.0% (72/90)† | 165.2 min | unknown | No |
| 111 | scenario-runner-weekly | `services/scenario-runner/azure-pipelines.yml` | enabled | Schedule (Fri 22:00 UTC) + Manual | 2026-03-14 | 13 | 84.6% (11/13) | 228.1 min | unknown | No |
| 112 | var-scenario-sweep-nightly | `night-jobs/compute/var-scenario-sweep.yml` | enabled | Schedule (weeknights 01:00 UTC) | 2026-03-17 | 65 | 92.3% (60/65) | 172.2 min | team-quant | No |
| 113 | daily-positions-export | `night-jobs/business/daily-positions-export.yml` | enabled | Schedule (weekdays 23:00 UTC) | 2026-03-16 | 65 | 96.9% (63/65) | 75.5 min | team-reporting | No |
| 114 | attestation-backfill-weekly | `night-jobs/compliance/attestation-backfill.yml` | enabled | Schedule (Sun 03:00 UTC) | 2026-03-16 | 13 | 100% (13/13) | 93.3 min | shared-ci-platform | No |
| 115 | bulk-reprocess-trades | `adhoc/bulk-reprocess-trades.yml` | enabled | Manual only | 2026-02-25 | 3 | 100% (3/3) | 325.1 min | unknown | No |
| 116 | onetime-data-migration | `adhoc/onetime-data-migration.yml` | **paused** | Manual only | 2024-08-20 | 1 | 100% (1/1) | 222.8 min | unknown | **YES** |
| 117 | old-pricing-pipeline | `deprecated/old-pricing-pipeline.yml` | **disabled** | None | 2023-06-15 | 0 | N/A | N/A | none | **YES** |
| 118 | batch-runner-v1 | `deprecated/batch-runner-v1.yml` | **disabled** | None | 2023-02-01 | 0 | N/A | N/A | none | **YES** |

† Pipeline 110 has 18 `partiallySucceeded` runs (not counted as failures).

\* Pipeline 105 (risk-batch-legacy) has only 2 runs in 90 days but is still externally triggered — not fully dead.

**Dead Pipeline Summary (skip during migration):**
- **ID 116** — `onetime-data-migration`: Paused, last run Aug 2024 (>18 months ago). One-time pipeline that was never cleaned up.
- **ID 117** — `old-pricing-pipeline`: Disabled, 0 runs in 90 days, last run Jun 2023. Replaced by ID 101.
- **ID 118** — `batch-runner-v1`: Disabled, 0 runs in 90 days, last run (failed) Feb 2023. Replaced by risk-batch-ci + night-jobs.

---

## 2. Pipeline Classification

Pipelines are classified into 6 categories based on template usage, workload type, and relationship to the central template library.

### Category 1: Central Template Consumers
Pipelines that use `templates/build/` or `templates/release/` from the shared-ci-platform repo.

| ID | Pipeline | Template Branch | Templates Used |
|----|----------|----------------|----------------|
| 101 | pricing-engine-ci | `main` | `build-dotnet.yml`, `run-tests.yml`, `release-standard.yml` |
| 102 | portfolio-api-ci | `master` ⚠️ | `build-java.yml`, `release-standard.yml` |
| 103 | portfolio-api-canary | Parameterized (main/master/preprod/hardened) | `build-java.yml` |
| 104 | risk-batch-ci | `staging/preprod` ⚠️ | `build-python.yml`, `run-tests.yml`, `release-standard.yml` |
| 105 | risk-batch-legacy | `legacy/master-support` ⚠️ | `build-python-legacy.yml` |

### Category 2: Alt-Template Consumers
Pipelines using team-maintained alternative templates from `alt-templates/`.

| ID | Pipeline | Template Branch | Templates Used |
|----|----------|----------------|----------------|
| 106 | frontend-workbench-ci | `team/frontend-custom` | `frontend-build.yml`, `frontend-deploy.yml` |

### Category 3: Hybrid (Central + Custom)
Pipelines mixing shared templates with team-specific inline steps or override templates.

| ID | Pipeline | Template Branch | Templates Used |
|----|----------|----------------|----------------|
| 107 | regulatory-reporting-ci | `team/reporting-hotfix` | `team-build-custom.yml` (wraps central) + inline compliance steps |

### Category 4: Custom Inline
Pipelines with fully inline YAML — no shared templates at all.

| ID | Pipeline | Stack | Notes |
|----|----------|-------|-------|
| 108 | market-sim-ci | Rust | Built independently by team-quant. Central `build-rust.yml` now exists but was never adopted. |
| 109 | ops-control-plane-ci | Go | Predates central `build-go.yml`. Never migrated. |

### Category 5: Non-Build Workloads
Pipelines that do not build software — they use CI infrastructure for compute, data processing, or business operations.

| ID | Pipeline | Workload Type | Pool | Timeout |
|----|----------|--------------|------|---------|
| 110 | notebook-executor-nightly | Jupyter notebook execution | linux-build-workers (self-hosted) | 180 min |
| 111 | scenario-runner-weekly | Monte Carlo simulations | high-memory-pool (self-hosted) | 360 min |
| 112 | var-scenario-sweep-nightly | VaR calculations | high-memory-pool (self-hosted) | 240 min |
| 113 | daily-positions-export | Data export / reporting | linux-build-workers (self-hosted) | 120 min |
| 114 | attestation-backfill-weekly | Compliance backfill | linux-build-workers (self-hosted) | 180 min |
| 115 | bulk-reprocess-trades | Trade reprocessing | Azure Pipelines (hosted) | 480 min |

### Category 6: Deprecated / Dead
Pipelines that are disabled, paused, or have 0 runs in 90 days.

| ID | Pipeline | ADO Status | Last Run | Replacement |
|----|----------|-----------|----------|-------------|
| 116 | onetime-data-migration | **paused** | 2024-08-20 | None (one-time) |
| 117 | old-pricing-pipeline | **disabled** | 2023-06-15 | pricing-engine-ci (ID 101) |
| 118 | batch-runner-v1 | **disabled** | 2023-02-01 | risk-batch-ci (ID 104) + night-jobs |

---

## 3. Template Dependency Map

Shows which template branches are consumed by which pipelines.

| Template Branch | Pipelines Consuming | Templates Referenced |
|----------------|---------------------|---------------------|
| `main` | 101 (pricing-engine-ci), 103 (canary option) | `build-dotnet.yml`, `run-tests.yml`, `release-standard.yml`, `build-java.yml` |
| `master` | 102 (portfolio-api-ci), 103 (canary option) | `build-java.yml`, `release-standard.yml` |
| `staging/preprod` | 104 (risk-batch-ci), 103 (canary option) | `build-python.yml` (modified with retry logic), `run-tests.yml`, `release-standard.yml` |
| `staging/release-hardening` | 103 (canary option) | `release-standard.yml` (modified with pre-deploy validation + health checks) |
| `team/frontend-custom` | 106 (frontend-workbench-ci) | `frontend-build.yml`, `frontend-deploy.yml` (alt-templates), `build-node.yml` (modified) |
| `team/quant-experiments` | None currently (experimental) | `build-python.yml` (modified with conda/GPU/timeout) |
| `team/reporting-hotfix` | 107 (regulatory-reporting-ci) | `team-build-custom.yml` (modified with audit trail + pre-build validation) |
| `legacy/master-support` | 105 (risk-batch-legacy), 117 (old-pricing-pipeline) | `build-python-legacy.yml`, `build-dotnet.yml` (frozen at .NET 6) |

**Consolidation opportunity:** 5 of 8 branches modify `build-python.yml`. These customizations (retry logic, conda support, extended timeouts) should be merged into a single parameterized template during migration.

---

## 4. Non-Build Workload Analysis

7 distinct non-build workloads identified across 6 pipelines (pipeline 107 is classified as hybrid but is functionally a compliance workflow).

### 4.1 Jupyter Notebook Execution (ID 110)
- **Schedule:** Nightly at 02:00 UTC
- **Pool:** `linux-build-workers` (self-hosted, 16 GB RAM, 4 cores)
- **Timeout:** 180 min
- **Dependencies:** jupyter, nbconvert, papermill, numpy, pandas, scipy, scikit-learn
- **Network:** Requires internal network access
- **Migration path:** Cannot move to GHA hosted runners. Needs dedicated compute (K8s CronJob, Azure Container Instances, or AWS Batch).

### 4.2 Monte Carlo Simulations (ID 111)
- **Schedule:** Friday 22:00 UTC + manual with parameters (scenarioCount, modelVersion, outputFormat)
- **Pool:** `high-memory-pool` (self-hosted, 128 GB RAM, 32 cores)
- **Timeout:** 360 min (6 hours)
- **Dependencies:** numpy, pandas, scipy, pyarrow
- **Migration path:** Requires dedicated high-memory compute. GHA hosted runners max at 7 GB RAM. Recommend dedicated K8s jobs or Azure Batch.

### 4.3 VaR Scenario Sweep (ID 112)
- **Schedule:** Weeknights at 01:00 UTC (50,000 scenarios)
- **Pool:** `high-memory-pool` (self-hosted, 128 GB RAM, 32 cores)
- **Timeout:** 240 min
- **Dependencies:** numpy, pandas, scipy, pyarrow, requests
- **Output:** Uploads to `data-warehouse`
- **Migration path:** Same as 4.2 — dedicated high-memory compute + internal network access.

### 4.4 Daily Positions Export (ID 113)
- **Schedule:** Weekdays 23:00 UTC (7 PM ET)
- **Pool:** `linux-build-workers` (self-hosted)
- **Timeout:** 120 min
- **Dependencies:** pandas, pyodbc, sqlalchemy, openpyxl, requests
- **Output:** Parquet raw data + Excel summary report → distributed to team-reporting and team-quant
- **Network:** Requires internal DB access via pyodbc
- **Migration path:** GHA self-hosted runner with network peering, or dedicated ETL tool (Azure Data Factory, Airflow).

### 4.5 Compliance Attestation Backfill (ID 114)
- **Schedule:** Sunday 03:00 UTC
- **Pool:** `linux-build-workers` (self-hosted)
- **Timeout:** 180 min
- **Dependencies:** requests, pandas
- **Output:** Attestation records → `attestation-database`
- **Retention:** 365 days (audit requirement)
- **Migration path:** GHA self-hosted runner with network access to `attestation-database`.

### 4.6 Bulk Trade Reprocessing (ID 115)
- **Schedule:** Manual only (parameterized: startDate, endDate, tradeTypes)
- **Pool:** Azure Pipelines (hosted)
- **Timeout:** 480 min (8 hours)
- **Dependencies:** pandas, requests, pyarrow
- **Migration path:** Can migrate to GHA workflow_dispatch, but 8-hour timeout exceeds hosted runner limits (6h max). Needs self-hosted or larger runner.

### 4.7 Regulatory Compliance Reporting (ID 107 — hybrid)
- **Schedule:** Weekday CI + weekday 06:00 UTC schedule
- **Pool:** Azure Pipelines (hosted)
- **Timeout:** 90 min (for GenerateReports stage)
- **Dependencies:** Compliance metadata generation, attestation records → `attestation-database`
- **Retention:** 365 days (audit requirement)
- **Migration path:** Can migrate to GHA with environment secrets + protection rules. Needs OIDC for Azure access.

---

## 5. Ownership Summary

### Confirmed Owners

| Team | Pipelines Owned | IDs |
|------|----------------|-----|
| team-quant | portfolio-api-ci, portfolio-api-canary, risk-batch-ci, risk-batch-legacy, market-sim-ci, var-scenario-sweep-nightly | 102, 103, 104, 105, 108, 112 |
| team-frontend | frontend-workbench-ci | 106 |
| team-reporting | regulatory-reporting-ci, daily-positions-export | 107, 113 |
| platform-team | ops-control-plane-ci | 109 |
| shared-ci-platform | attestation-backfill-weekly | 114 |

### Unknown Owners

| Pipeline | ID | Last Modified By | Notes |
|----------|----|-----------------|-------|
| pricing-engine-ci | 101 | contractor-account@contoso.com | Original team disbanded. Maintained best-effort by shared-ci-platform. |
| notebook-executor-nightly | 110 | unknown-service-account@contoso.com | No owner identified. Uses self-hosted pool. |
| scenario-runner-weekly | 111 | unknown-service-account@contoso.com | No owner identified. Uses high-memory pool. |
| bulk-reprocess-trades | 115 | unknown-service-account@contoso.com | Unclear ownership. Ad-hoc manual pipeline. |
| onetime-data-migration | 116 | unknown-service-account@contoso.com | Should have been deleted. No owner. |

### Deprecated (No Owner)

| Pipeline | ID | Notes |
|----------|----|-------|
| old-pricing-pipeline | 117 | Replaced by ID 101. Last modified by contractor-account. |
| batch-runner-v1 | 118 | Replaced by ID 104 + night-jobs. Last modified by contractor-account. |

---

## 6. Template Duplication Findings

4 duplicate template sets identified.

### Duplicate Set 1: Python Build Templates (4 copies)

| File | Location | Default Python | Linting | Test Runner | Key Difference |
|------|----------|---------------|---------|-------------|----------------|
| `templates/build/build-python.yml` | Central | 3.11 | Yes (flake8, black, mypy) | pytest | Canonical. Artifact registry integration. |
| `templates/legacy/build-python-legacy.yml` | Central (legacy) | 3.9 | No | unittest | Uses unittest, not pytest. No linting. |
| `alt-templates/data-science/build-python.yml` | Alt (data science) | 3.10 | No | pytest | Adds conda, numpy/scipy/scikit-learn. Same filename as central — causes confusion. |
| `services/risk-batch/pipeline-fragments/build-python-local.yml` | Service-local fork | 3.11 | No | pytest | Adds retry logic + extended timeouts. Service-local fork to avoid central template breakage. |

**Recommendation:** Consolidate into a single parameterized `build-python.yml` with flags for `useConda`, `enableLinting`, `retryCount`, `timeoutMinutes`. The `staging/preprod` branch already adds retry logic to the central template — merge this upstream.

### Duplicate Set 2: Data Science Templates (3 near-identical copies)

| File | Default Artifact Name | Key Difference |
|------|-----------------------|----------------|
| `alt-templates/data-science/build-python.yml` | `ds-package` | Has `runNotebooks` parameter |
| `alt-templates/data-science/ds-model-build.yml` | `ds-model-package` | Nearly identical to above, minus notebook support |
| `alt-templates/data-science/notebook-package-build.yml` | `notebook-package` | Nearly identical; adds jupyter to pip install |

**Recommendation:** Consolidate into a single data science template. The comment in `ds-model-build.yml` literally states: "Nobody remembers why three exist."

### Duplicate Set 3: Node.js Build Templates (2 copies)

| File | Default Node | SSR | Storybook | Key Difference |
|------|-------------|-----|-----------|----------------|
| `templates/build/build-node.yml` | 20.x | No | No | Central canonical template |
| `alt-templates/frontend/frontend-build.yml` | 18.x | Yes | No | Fork from Q2 2023. Adds SSR, Lighthouse CI, framework selection. |

**Recommendation:** The `team/frontend-custom` branch also modifies the central `build-node.yml` to add SSR + Storybook. Merge these capabilities into the central template with feature flags.

### Duplicate Set 4: Release Templates (2 copies)

| File | Pre-deploy Validation | Health Check | Approval Default |
|------|-----------------------|--------------|-----------------|
| `templates/release/release-standard.yml` (main) | No | No | `false` |
| `templates/release/release-standard.yml` (staging/release-hardening) | Yes | Yes (5 retries) | `true` |

**Recommendation:** Merge the hardening branch improvements into main. The pre-deploy validation and health checks should be opt-in parameters, not branch-specific modifications.

---

## 7. Risk Flags for Migration

### 7.1 Self-Hosted Agent Pools
| Risk | Pipelines Affected | Impact |
|------|--------------------|--------|
| `linux-build-workers` (self-hosted, internal network) | 110, 113, 114 | Cannot use GHA hosted runners. Require self-hosted GHA runners with network peering. |
| `high-memory-pool` (128 GB RAM, 32 cores) | 111, 112 | GHA hosted runners max 7 GB RAM. These workloads should NOT migrate to GHA at all. |
| `windows-build-workers` (legacy, half offline) | None currently | Not referenced by any active YAML but may have ADO-level pool overrides. Candidate for decommission. |

### 7.2 Long Timeouts (Exceeding GHA 6-Hour Limit)
| Pipeline | Timeout | Notes |
|----------|---------|-------|
| 111 (scenario-runner-weekly) | 360 min (6h) | At GHA limit |
| 115 (bulk-reprocess-trades) | 480 min (8h) | Exceeds GHA limit |
| 118 (batch-runner-v1, deprecated) | 300 min | N/A (dead) |

### 7.3 ADO-Specific Features Requiring Replacement
| Feature | Pipelines | GHA Equivalent |
|---------|-----------|----------------|
| `##vso[task.prependpath]` | 108 (market-sim) | `echo "$PATH_ENTRY" >> $GITHUB_PATH` |
| `##vso[task.logissue]` | 110 (notebook-executor) | `echo "::warning::message"` |
| `$[format('{0:yyyy-MM-dd}', pipeline.startTime)]` | 112, 113 | `${{ github.event.schedule }}` or `date` command |
| `PublishBuildArtifacts@1` | All build pipelines | `actions/upload-artifact@v4` |
| `PublishTestResults@2` | 101, 104, 106 (via templates) | Third-party test reporter actions or native OIDC |
| `UsePythonVersion@0` | Multiple | `actions/setup-python@v5` |
| `UseDotNet@2` | 101 (via template), 117 | `actions/setup-dotnet@v4` |
| `NodeTool@0` | 106 (via template) | `actions/setup-node@v4` |
| `GoTool@0` | 109 | `actions/setup-go@v5` |
| `JavaToolInstaller@0` | 102 (via template) | `actions/setup-java@v4` |
| `Maven@4` | 102 (via template) | Direct `mvn` commands |
| `NuGetToolInstaller@1` / `NuGetCommand@2` | 101 (via template) | `dotnet restore` or `nuget` CLI |
| `ArchiveFiles@2` | 106 (via template) | `tar` / `zip` commands |
| `deployment` job + `environment` | 101, 102, 104, 106, 107 (via templates) | GHA `environment` key + protection rules |
| `schedules` (YAML cron) | 107, 110, 111, 112, 113, 114 | `on: schedule: cron:` |
| `resources.repositories` (template refs) | 101-107 | Reusable workflows (`uses: org/repo/.github/workflows/x.yml@ref`) or composite actions |
| `Agent.OS` demands | 110, 111, 112, 113 | Runner labels |
| `condition: and(succeeded(), eq(...))` | 101, 106, 108 | `if:` expressions |

### 7.4 Compliance & Audit Concerns
| Concern | Pipelines | Notes |
|---------|-----------|-------|
| 365-day retention (audit) | 107, 114 | GHA artifact retention max 400 days (enterprise). Verify org policy. |
| Compliance attestation generation | 107, 114, all releases (via `release-standard.yml`) | `generate_attestation.py` and `generate_metadata.py` scripts must be ported. |
| `attestation-database` network access | 107, 114 | Requires self-hosted runner or VPN-connected hosted runner. |
| `compliance-store` network access | 107, 114 | Same as above. |

### 7.5 Template Branch Drift
- 5 of 8 long-lived branches modify `build-python.yml` — consolidation needed before migration.
- `master` branch still referenced by portfolio-api-ci (ID 102) — legacy ref that should be updated to `main`.
- `staging/preprod` branch actively consumed by risk-batch-ci (ID 104) — changes need to be merged to main.

---

## 8. Branch Analysis with Actual Diffs

### 8.1 `master` vs `main`

Changes to 2 templates. The `master` branch represents the pre-rename default branch with older defaults.

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

**Summary:** `master` has older defaults — .NET 6 instead of 8, Python 3.10 instead of 3.11, linting disabled by default. Pipeline 102 (portfolio-api-ci) references this branch for Java templates, but the Java template is unchanged between branches.

---

### 8.2 `staging/preprod` vs `main`

Adds retry logic to Python test execution and a preprod validation stamp.

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

**Summary:** Adds `testRetryCount` parameter (default 3), wraps pytest in a retry loop with `pytest-rerunfailures`, and stamps a preprod validation marker on artifacts. Actively consumed by risk-batch-ci (ID 104).

---

### 8.3 `staging/release-hardening` vs `main`

Adds pre-deploy validation and post-deploy health checks to the release template.

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

**Summary:** Changes `requireApproval` default to `true`. Adds `runPreDeployValidation` (artifact baseline comparison) and `healthCheckRetries` (post-deploy health check with 5 retries). Not currently consumed by any pipeline in production — used only by canary testing (ID 103).

---

### 8.4 `team/frontend-custom` vs `main`

Modifies the central Node.js template and adds Lighthouse CI to the frontend build.

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

**Summary:** Adds Lighthouse CI audit step (non-blocking `|| true`), appends build ID to artifact name, and adds `enableSSR` + `buildStorybook` parameters to the central Node template. Downgrades default Node from 20.x to 18.x. Consumed by frontend-workbench-ci (ID 106).

---

### 8.5 `team/quant-experiments` vs `main`

Adds conda support, GPU pool option, and extended timeouts to the Python build template.

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

**Summary:** Adds `useConda`, `condaEnvironmentFile`, `useGpuPool`, and `timeoutMinutes` parameters. Makes pip/conda install conditional. Not currently consumed by any pipeline — experimental branch.

---

### 8.6 `team/reporting-hotfix` vs `main`

Adds audit trail logging and pre-build compliance validation to the team override template.

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

**Summary:** Enhances compliance logging with audit trail (BuildId, RequestedFor, SourceBranch, timestamp). Adds pre-build compliance validation step that generates metadata before the build runs. Writes a JSON audit-trail record. Consumed by regulatory-reporting-ci (ID 107).

---

### 8.7 `legacy/master-support` vs `main`

Frozen compatibility branch with older tool versions and disabled features.

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

**Summary:** Explicitly marked `FROZEN`. .NET downgraded to 6.0.x, Python to 3.8. Linting disabled. Artifact name changed to `python-legacy-dist`. Last reviewed 2022-12. Consumed by risk-batch-legacy (ID 105) and old-pricing-pipeline (ID 117, dead).

---

## 9. Variable Group & Secret Mapping

9 variable groups configured at the ADO project level. Mapped to GitHub Actions equivalents.

| ID | Variable Group | Variables | Secrets? | Pipelines Using | GHA Equivalent |
|----|---------------|-----------|----------|----------------|----------------|
| 201 | `shared-ci-secrets` | `NUGET_FEED_URL`, `NUGET_API_KEY` (secret), `PIP_INDEX_URL`, `NPM_REGISTRY`, `NPM_TOKEN` (secret) | Yes | 101, 102, 103, 104, 105, 106, 107, 109 | **Organization secrets** (`NUGET_API_KEY`, `NPM_TOKEN`) + **Organization variables** (`NUGET_FEED_URL`, `PIP_INDEX_URL`, `NPM_REGISTRY`) |
| 205 | `artifact-registry-credentials` | `ARTIFACT_REGISTRY_URL`, `ARTIFACT_REGISTRY_TOKEN` (secret) | Yes | 101, 102, 104 | **Organization secrets** (`ARTIFACT_REGISTRY_TOKEN`) + **Organization variables** (`ARTIFACT_REGISTRY_URL`) |
| 206 | `compliance-store-credentials` | `COMPLIANCE_STORE_URL`, `COMPLIANCE_STORE_TOKEN` (secret), `COMPLIANCE_STORE_CERT_THUMBPRINT` (secret) | Yes | 107, 114 | **Environment secrets** on `prod` environment (`COMPLIANCE_STORE_TOKEN`, `COMPLIANCE_STORE_CERT_THUMBPRINT`) + **Environment variables** (`COMPLIANCE_STORE_URL`) |
| 207 | `internal-network-credentials` | `INTERNAL_SVC_ACCOUNT`, `INTERNAL_SVC_PASSWORD` (secret), `INTERNAL_CA_CERT_PATH` | Yes | 110, 111, 112, 113, 115 | **Organization secrets** (`INTERNAL_SVC_PASSWORD`) + **Organization variables** (`INTERNAL_SVC_ACCOUNT`, `INTERNAL_CA_CERT_PATH`). Requires self-hosted runner for network access. |
| 208 | `risk-batch-config` | `RISK_DB_CONNECTION_STRING` (secret), `RISK_MODEL_VERSION`, `RISK_BATCH_MAX_RETRIES` | Yes | 104 | **Repository secrets** (`RISK_DB_CONNECTION_STRING`) + **Repository variables** (`RISK_MODEL_VERSION`, `RISK_BATCH_MAX_RETRIES`) |
| 209 | `regulatory-reporting-config` | `REPORTING_DB_CONNECTION_STRING` (secret), `REPORTING_SMTP_SERVER`, `REPORTING_DISTRIBUTION_LIST` | Yes | 107 | **Repository secrets** (`REPORTING_DB_CONNECTION_STRING`) + **Repository variables** (`REPORTING_SMTP_SERVER`, `REPORTING_DISTRIBUTION_LIST`) |
| 210 | `frontend-cdn-config` | `CDN_ENDPOINT`, `CDN_STORAGE_ACCOUNT`, `CDN_STORAGE_KEY` (secret), `CDN_PURGE_API_KEY` (secret) | Yes | 106 | **Environment secrets** on `dev-frontend`/`staging-frontend` (`CDN_STORAGE_KEY`, `CDN_PURGE_API_KEY`) + **Environment variables** (`CDN_ENDPOINT`, `CDN_STORAGE_ACCOUNT`). Consider **OIDC** for Azure Blob storage access. |
| 211 | `ops-infra-credentials` | `K8S_CLUSTER_URL`, `K8S_SERVICE_ACCOUNT_TOKEN` (secret), `K8S_NAMESPACE` | Yes | 109 | **Repository secrets** (`K8S_SERVICE_ACCOUNT_TOKEN`) + **Repository variables** (`K8S_CLUSTER_URL`, `K8S_NAMESPACE`). Consider **OIDC** with Azure AD for K8s auth. |
| 212 | `data-warehouse-credentials` | `DW_CONNECTION_STRING` (secret), `DW_SCHEMA` | Yes | 112 | **Repository secrets** (`DW_CONNECTION_STRING`) + **Repository variables** (`DW_SCHEMA`) |
| 213 | `positions-db-credentials` | `POSITIONS_DB_CONNECTION_STRING` (secret), `POSITIONS_DB_READONLY_STRING` (secret) | Yes | 113, 116 | **Repository secrets** (both). Pipeline 116 is dead — only 113 needs these. |

### OIDC Migration Opportunities

The following service principal-based authentications should migrate to **GitHub Actions OIDC** (OpenID Connect) with Azure AD federated credentials, eliminating stored secrets:

| Current Secret | Current Auth | OIDC Replacement |
|---------------|-------------|-----------------|
| `AzureSubscription-Dev` SP key | Service principal + secret | `azure/login@v2` with OIDC federated credential |
| `AzureSubscription-Staging` SP key | Service principal + secret | `azure/login@v2` with OIDC federated credential |
| `AzureSubscription-Prod` SP key | Service principal + secret | `azure/login@v2` with OIDC federated credential |
| `ContainerRegistry-ACR` SP key | Service principal | `azure/login@v2` + `docker/login-action@v3` with OIDC |
| `CDN_STORAGE_KEY` | Storage account key | OIDC + Azure RBAC (Storage Blob Data Contributor) |
| `K8S_SERVICE_ACCOUNT_TOKEN` | K8s service account | OIDC + Azure AD Workload Identity for AKS |

---

## 10. Service Connection Mapping

5 service connections configured at the ADO project level.

| ADO Connection | Type | Auth Scheme | Pipelines Using | GHA Equivalent | Migration Notes |
|----------------|------|-------------|----------------|----------------|-----------------|
| `AzureSubscription-Dev` | `azurerm` | Service Principal (key) | 101, 104, 106 | **OIDC** via `azure/login@v2` with federated identity credential. Configure subject claim: `repo:org/repo:environment:dev` | Create Azure AD app registration → add federated credential for GHA → grant Contributor role on Dev subscription |
| `AzureSubscription-Staging` | `azurerm` | Service Principal (key) | 102, 106 | **OIDC** via `azure/login@v2`. Subject claim: `repo:org/repo:environment:staging` | Same pattern as Dev. Separate federated credential for staging. |
| `AzureSubscription-Prod` | `azurerm` | Service Principal (key) | 107 | **OIDC** via `azure/login@v2`. Subject claim: `repo:org/repo:environment:prod`. Require GHA environment protection rules. | Highest sensitivity. Lock to `prod` environment with required reviewers. |
| `ContainerRegistry-ACR` | `dockerregistry` | Service Principal | 108, 109 | **OIDC** via `azure/login@v2` + `docker/login-action@v3`. Login server: `contosofinancial.azurecr.io` | Or use ACR admin credentials as repo secrets (less secure). |
| `GitHub-SourceMirror` | `github` | Personal Access Token | None (0 pipelines) | **Not needed.** After migration, source is already on GitHub. | Can be decommissioned. |

---

## 11. Environment & Approval Gate Mapping

6 ADO environments mapped to GHA environments with equivalent protection rules.

| ADO Environment | Checks | Pipelines Using | GHA Environment | GHA Protection Rules |
|----------------|--------|----------------|-----------------|---------------------|
| `dev` | None | 101, 104 | `dev` | No protection rules needed. Auto-deploy on push. |
| `staging` | Approval: `shared-ci-platform-team` (1 approver min). Instructions: "Verify staging test results before proceeding" | 102 | `staging` | **Required reviewers**: `shared-ci-platform-team` (1 min). Add **deployment branches** filter: `main` only. |
| `preprod` | Approval: `shared-ci-platform-team` + `release-managers` (2 approvers min). Instructions: "Review compliance attestation and artifact baseline comparison". **Business hours**: EST 09:00–17:00 Mon–Fri. | None currently | `preprod` | **Required reviewers**: `shared-ci-platform-team`, `release-managers` (2 min). **Deployment branches**: `main`. No native business-hours gate in GHA — implement via custom workflow step: `if: github.event_name != 'workflow_dispatch' && (steps.check_hours.outputs.in_hours == 'true')`. |
| `prod` | Approval: `release-managers` + `service-owner` (2 approvers min). Instructions: "Production deployment requires release manager AND service owner approval. Verify compliance attestation is present." **Business hours**: EST 09:00–16:00 Mon–Thu. **Exclusive lock**: Only one production deployment at a time. | 107 | `prod` | **Required reviewers**: `release-managers`, `service-owner` (2 min). **Deployment branches**: `main`. **Concurrency**: `concurrency: group: prod-deploy` (only one at a time). Business hours: custom step (same as preprod). |
| `dev-frontend` | None | 106 | `dev-frontend` | No protection rules needed. |
| `staging-frontend` | Approval: `team-frontend` (1 approver min). Instructions: "Verify SSR bundle and CDN purge before promoting" | 106 | `staging-frontend` | **Required reviewers**: `team-frontend` (1 min). **Deployment branches**: `main`. |

### Business Hours Gate Implementation (GHA)

GHA does not natively support business-hours restrictions. Implement as a reusable workflow step:

```yaml
- name: Check business hours
  id: check_hours
  run: |
    HOUR=$(TZ="America/New_York" date +%H)
    DAY=$(TZ="America/New_York" date +%u)  # 1=Mon, 7=Sun
    if [[ $DAY -le 4 && $HOUR -ge 9 && $HOUR -lt 16 ]]; then
      echo "in_hours=true" >> $GITHUB_OUTPUT
    else
      echo "in_hours=false" >> $GITHUB_OUTPUT
      echo "::error::Deployment blocked: outside business hours (EST Mon-Thu 09:00-16:00)"
      exit 1
    fi
```

### Exclusive Lock Implementation (GHA)

Use `concurrency` to enforce only one production deployment:

```yaml
concurrency:
  group: prod-deploy
  cancel-in-progress: false
```

---

## 12. Agent Pool & Infrastructure Requirements

4 agent pools configured in the ADO organization.

### Pool 1: Azure Pipelines (Hosted)

| Property | Value |
|----------|-------|
| Pool ID | 9 |
| Type | **Hosted** (Microsoft-managed) |
| VM Images | ubuntu-latest, ubuntu-20.04, windows-latest, macos-latest |
| Pipelines Using | 101, 102, 103, 104, 105, 106, 107, 108, 109, 115, 116, 117, 118 |
| GHA Equivalent | `runs-on: ubuntu-latest` / `windows-latest` / `macos-latest` |
| Migration Concern | **None.** Direct 1:1 mapping to GitHub-hosted runners. |

### Pool 2: linux-build-workers (Self-Hosted)

| Property | Value |
|----------|-------|
| Pool ID | 15 |
| Type | **Self-hosted** |
| Size | 8 agents (6 online, 2 offline) |
| OS | Ubuntu 22.04 |
| Specs | 16 GB RAM, 4 cores, 200 GB disk |
| Installed Tools | python3.10, python3.11, docker, jupyter, conda |
| Network Access | compliance-store, positions-db, internal-smtp, data-warehouse |
| Pipelines Using | 110 (notebook-executor), 113 (positions-export), 114 (attestation-backfill) |
| GHA Equivalent | **Self-hosted GHA runners** deployed in the same network segment. Label: `self-hosted, linux, internal-network`. |
| Migration Concern | **Medium.** Requires provisioning self-hosted GHA runners with identical network access. 2 agents offline — should be investigated before migration. |

### Pool 3: high-memory-pool (Self-Hosted)

| Property | Value |
|----------|-------|
| Pool ID | 18 |
| Type | **Self-hosted** |
| Size | 4 agents (all online) |
| OS | Ubuntu 22.04 |
| Specs | **128 GB RAM**, **32 cores**, 1 TB disk |
| Installed Tools | python3.11, docker, numpy, scipy, pyarrow |
| Network Access | compliance-store, positions-db, internal-smtp, data-warehouse, **compute-cluster** |
| Pipelines Using | 111 (scenario-runner), 112 (VaR sweep) |
| GHA Equivalent | **NOT recommended for GHA migration.** These are compute workloads, not CI. Migrate to dedicated compute infrastructure: K8s jobs, Azure Container Instances, or AWS Batch. |
| Migration Concern | **High.** GHA hosted runners max at 7 GB RAM (standard) or 64 GB (larger runners, enterprise). 128 GB exceeds even larger runners. These workloads need dedicated infrastructure. |

### Pool 4: windows-build-workers (Self-Hosted, Legacy)

| Property | Value |
|----------|-------|
| Pool ID | 22 |
| Type | **Self-hosted** (legacy) |
| Size | 2 agents (1 online, 1 offline running Windows Server 2019) |
| OS | Windows Server 2022 / 2019 |
| Specs | 32 GB RAM, 8 cores, 500 GB disk |
| Installed Tools | dotnet-6.0, dotnet-8.0, nuget, msbuild |
| Network Access | internal-smtp only |
| Pipelines Using | **None currently** |
| GHA Equivalent | N/A |
| Migration Concern | **None.** Not referenced by any active pipeline. Candidate for decommission. May be used by pipelines with ADO-level pool overrides — verify before decommissioning. |

### Infrastructure Migration Summary

| Migration Path | Pipelines | Action Required |
|---------------|-----------|-----------------|
| Direct to GHA hosted runners | 101, 102, 103, 104, 105, 106, 107, 108, 109, 115 | None — use `runs-on: ubuntu-latest` |
| Self-hosted GHA runners (internal network) | 110, 113, 114 | Deploy GHA runners in same network segment as current `linux-build-workers` |
| Dedicated compute (NOT GHA) | 111, 112 | Migrate to K8s CronJobs, Azure Batch, or ACI with 128 GB RAM |
| Skip (dead) | 116, 117, 118 | No migration needed |
| Decommission | windows-build-workers pool | Verify no ADO-level overrides, then decommission |
