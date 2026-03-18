# Azure DevOps Pipeline Inventory & Classification Report

**Repository:** `parkerduff/azure-pipelines`
**Date:** 2026-03-18
**Purpose:** Migration planning from Azure DevOps to GitHub Actions

---

## 1. Pipeline Inventory Table

### Services

| File Path | Service/Job Name | Tech Stack | Trigger Type | Agent Pool | Timeout |
|-----------|-----------------|------------|--------------|------------|---------|
| `services/pricing-engine/azure-pipelines.yml` | pricing-engine | .NET 8 | CI on push (`main`, `release/*`) | Hosted (`ubuntu-latest`) | Not set |
| `services/portfolio-api/azure-pipelines.yml` | portfolio-api | Java 17 / Maven | CI on push (`main`, `master`) | Hosted (`ubuntu-latest`) | Not set |
| `services/portfolio-api/azure-pipelines-canary.yml` | portfolio-api (canary) | Java 17 / Maven | Manual (`trigger: none`) | Hosted (`ubuntu-latest`) | Not set |
| `services/risk-batch/azure-pipelines.yml` | risk-batch | Python 3.11 | CI on push (`main`) | Hosted (`ubuntu-latest`) | Not set |
| `services/risk-batch/azure-pipelines-legacy.yml` | risk-batch (legacy) | Python 3.9 | Disabled (`trigger: none`) | Hosted (`ubuntu-20.04`) | Not set |
| `services/frontend-workbench/azure-pipelines.yml` | frontend-workbench | Node.js 18.x (React) | CI on push (`main`, `feature/*`) | Hosted (`ubuntu-latest`) | Not set |
| `services/notebook-executor/azure-pipelines.yml` | notebook-executor | Python 3.10 | Scheduled (cron `0 2 * * *` daily) | **Self-hosted** (`linux-build-workers`) | **180 min** |
| `services/scenario-runner/azure-pipelines.yml` | scenario-runner | Python 3.11 | Scheduled (cron `0 22 * * 5` Fridays) + Manual | **Self-hosted** (`high-memory-pool`) | **360 min** |
| `services/market-sim/azure-pipelines.yml` | market-sim | Rust (stable) | CI on push (`main`) | Hosted (`ubuntu-latest`) | 30 min |
| `services/ops-control-plane/azure-pipelines.yml` | ops-control-plane | Go 1.22 | CI on push (`main`) | Hosted (`ubuntu-latest`) | Not set |
| `services/regulatory-reporting/azure-pipelines.yml` | regulatory-reporting | Python 3.11 | CI on push (`main`) + Scheduled (cron `0 6 * * 1-5` weekdays) | Hosted (`ubuntu-latest`) | 90 min (GenerateReports stage) |

### Night Jobs

| File Path | Service/Job Name | Tech Stack | Trigger Type | Agent Pool | Timeout |
|-----------|-----------------|------------|--------------|------------|---------|
| `night-jobs/compute/var-scenario-sweep.yml` | VaR Scenario Sweep | Python 3.11 | Scheduled (cron `0 1 * * 1-5` weeknights) | **Self-hosted** (`high-memory-pool`) | **240 min** |
| `night-jobs/business/daily-positions-export.yml` | Daily Positions Export | Python 3.11 | Scheduled (cron `0 23 * * 1-5` weekdays) | **Self-hosted** (`linux-build-workers`) | **120 min** |
| `night-jobs/compliance/attestation-backfill.yml` | Attestation Backfill | Python 3.11 | Scheduled (cron `0 3 * * 0` Sundays) | **Self-hosted** (`linux-build-workers`) | **180 min** |

### Ad-Hoc

| File Path | Service/Job Name | Tech Stack | Trigger Type | Agent Pool | Timeout |
|-----------|-----------------|------------|--------------|------------|---------|
| `adhoc/bulk-reprocess-trades.yml` | Bulk Reprocess Trades | Python 3.11 | Manual (`trigger: none`) | Hosted (`ubuntu-latest`) | **480 min** |
| `adhoc/onetime-data-migration.yml` | One-time Data Migration | Python 3.11 | Manual (`trigger: none`) | Hosted (`ubuntu-latest`) | **300 min** |

### Deprecated

| File Path | Service/Job Name | Tech Stack | Trigger Type | Agent Pool | Timeout |
|-----------|-----------------|------------|--------------|------------|---------|
| `deprecated/old-pricing-pipeline.yml` | old-pricing-pipeline | .NET 6 | Disabled (`trigger: none`) | Hosted (`ubuntu-20.04`) | Not set |
| `deprecated/batch-runner-v1.yml` | batch-runner-v1 | Python 3.8 | Disabled (`trigger: none`) | Hosted (`ubuntu-20.04`) | 300 min |

### Archived (not a pipeline; included for completeness)

| File Path | Service/Job Name | Tech Stack | Trigger Type | Agent Pool | Timeout |
|-----------|-----------------|------------|--------------|------------|---------|
| `archive/old-release-workflow.yml` | old-release-workflow | N/A | Disabled (`trigger: none`) | Hosted (`ubuntu-20.04`) | Not set |

**Total pipeline YAML files:** 18 (11 services + 3 night-jobs + 2 adhoc + 2 deprecated) plus 1 archived stub.

---

## 2. Pipeline Classification

| File Path | Classification | Rationale |
|-----------|---------------|-----------|
| `services/pricing-engine/azure-pipelines.yml` | **Central Template Consumer** | Uses `templates/build/build-dotnet.yml`, `templates/test/run-tests.yml`, `templates/release/release-standard.yml` from `main` branch |
| `services/portfolio-api/azure-pipelines.yml` | **Central Template Consumer** | Uses `templates/build/build-java.yml`, `templates/release/release-standard.yml` from `master` branch |
| `services/portfolio-api/azure-pipelines-canary.yml` | **Central Template Consumer** | Uses `templates/build/build-java.yml` from multiple branches via runtime parameter selection (canary pattern) |
| `services/risk-batch/azure-pipelines.yml` | **Central Template Consumer** | Uses `templates/build/build-python.yml`, `templates/test/run-tests.yml`, `templates/release/release-standard.yml` from `staging/preprod` branch |
| `services/risk-batch/azure-pipelines-legacy.yml` | **Deprecated** | Trigger disabled. Uses `templates/legacy/build-python-legacy.yml` from `legacy/master-support`. Comment says "Still triggered by some downstream jobs. Do not remove yet." |
| `services/frontend-workbench/azure-pipelines.yml` | **Alt-Template Consumer** | Uses `alt-templates/frontend/frontend-build.yml` and `alt-templates/frontend/frontend-deploy.yml` from `team/frontend-custom` branch |
| `services/notebook-executor/azure-pipelines.yml` | **Non-Build Workload** | Fully inline. Executes Jupyter notebooks on CI as cheap compute. Does not build software. |
| `services/scenario-runner/azure-pipelines.yml` | **Non-Build Workload** | Fully inline. Runs Monte Carlo simulations. Uses CI as a free compute grid. |
| `services/market-sim/azure-pipelines.yml` | **Custom/Standalone** | Fully inline Rust build. No shared template references. |
| `services/ops-control-plane/azure-pipelines.yml` | **Custom/Standalone** | Fully inline Go build. No shared template references. Comment notes Go template was added to central after this pipeline existed. |
| `services/regulatory-reporting/azure-pipelines.yml` | **Hybrid** | Uses `alt-templates/team-overrides/team-build-custom.yml` from `team/reporting-hotfix` PLUS inline steps that call `build-tools/compliance/generate_metadata.py` and `build-tools/scripts/generate_attestation.py` directly. |
| `night-jobs/compute/var-scenario-sweep.yml` | **Non-Build Workload** | Fully inline. VaR scenario calculations on CI compute. |
| `night-jobs/business/daily-positions-export.yml` | **Non-Build Workload** | Fully inline. Data export to downstream reporting systems. |
| `night-jobs/compliance/attestation-backfill.yml` | **Non-Build Workload** | Fully inline. Scans and backfills missing compliance attestations. Also calls `build-tools/compliance/generate_metadata.py`. |
| `adhoc/bulk-reprocess-trades.yml` | **Non-Build Workload** | Fully inline. Manual trade reprocessing. |
| `adhoc/onetime-data-migration.yml` | **Non-Build Workload** | Fully inline. One-time database migration that was never cleaned up. |
| `deprecated/old-pricing-pipeline.yml` | **Deprecated** | Explicitly marked deprecated. Trigger disabled. Uses `legacy/master-support` ref but has mostly inline steps. |
| `deprecated/batch-runner-v1.yml` | **Deprecated** | Explicitly marked deprecated. Trigger disabled. Fully inline. |

### Classification Summary

| Category | Count | Pipelines |
|----------|-------|-----------|
| Central Template Consumer | 4 | pricing-engine, portfolio-api, portfolio-api-canary, risk-batch |
| Alt-Template Consumer | 1 | frontend-workbench |
| Hybrid | 1 | regulatory-reporting |
| Custom/Standalone | 2 | market-sim, ops-control-plane |
| Non-Build Workload | 7 | notebook-executor, scenario-runner, var-scenario-sweep, daily-positions-export, attestation-backfill, bulk-reprocess-trades, onetime-data-migration |
| Deprecated | 3 | risk-batch-legacy, old-pricing-pipeline, batch-runner-v1 |

### Ambiguous Pipelines Flagged

**`services/regulatory-reporting/azure-pipelines.yml`** -- This pipeline is classified as **Hybrid** but is flagged as ambiguous. Despite having a "ComplianceBuild" stage that looks like a software build, the pipeline's own comments state it "does NOT produce a deployable artifact." It generates regulatory reports, validates compliance metadata, and uploads attestation records to `compliance-store`. It could alternatively be classified as a **Non-Build Workload** that happens to use a shared template for its first stage. **Recommendation:** Treat as a compliance workflow during migration, not a standard build pipeline. It will need special handling because it straddles both categories.

**`services/risk-batch/azure-pipelines-legacy.yml`** -- Classified as Deprecated, but comments say "Still triggered by some downstream jobs. Do not remove yet." This needs investigation to find and update those downstream dependencies before deletion.

---

## 3. Template Dependency Map

### Pipeline-to-Template References

| Pipeline | ref: (branch) | Templates Consumed | Multi-Branch? |
|----------|---------------|-------------------|---------------|
| `services/pricing-engine/azure-pipelines.yml` | `main` | `templates/build/build-dotnet.yml`, `templates/test/run-tests.yml`, `templates/release/release-standard.yml` | No |
| `services/portfolio-api/azure-pipelines.yml` | `master` | `templates/build/build-java.yml`, `templates/release/release-standard.yml` | No |
| `services/portfolio-api/azure-pipelines-canary.yml` | `main`, `master`, `staging/preprod`, `staging/release-hardening` | `templates/build/build-java.yml` (from whichever branch is selected at runtime) | **Yes** (4 branches) |
| `services/risk-batch/azure-pipelines.yml` | `staging/preprod` | `templates/build/build-python.yml`, `templates/test/run-tests.yml`, `templates/release/release-standard.yml` | No |
| `services/risk-batch/azure-pipelines-legacy.yml` | `legacy/master-support` | `templates/legacy/build-python-legacy.yml` | No |
| `services/frontend-workbench/azure-pipelines.yml` | `team/frontend-custom` | `alt-templates/frontend/frontend-build.yml`, `alt-templates/frontend/frontend-deploy.yml` | No |
| `services/regulatory-reporting/azure-pipelines.yml` | `team/reporting-hotfix` | `alt-templates/team-overrides/team-build-custom.yml` | No |
| `deprecated/old-pricing-pipeline.yml` | `legacy/master-support` | (None consumed via template syntax -- has inline steps but declares the repo resource) | No |

### Template Branch Consumer Summary

| Branch (ref:) | # Pipelines Pointing To It | Consumers |
|---------------|---------------------------|-----------|
| `main` | 2 | pricing-engine, portfolio-api-canary (one of 4 options) |
| `master` | 2 | portfolio-api, portfolio-api-canary (one of 4 options) |
| `staging/preprod` | 2 | risk-batch, portfolio-api-canary (one of 4 options) |
| `staging/release-hardening` | 1 | portfolio-api-canary (one of 4 options) |
| `team/frontend-custom` | 1 | frontend-workbench |
| `team/reporting-hotfix` | 1 | regulatory-reporting |
| `legacy/master-support` | 2 | risk-batch-legacy, old-pricing-pipeline (deprecated) |
| `team/quant-experiments` | 0 | (No pipelines on main branch reference this -- may be consumed from another branch or unused) |

### Template File Consumption Frequency

| Template File | # Pipelines Using It |
|---------------|---------------------|
| `templates/build/build-java.yml` | 3 (portfolio-api, portfolio-api-canary x4 conditional) |
| `templates/release/release-standard.yml` | 3 (pricing-engine, portfolio-api, risk-batch) |
| `templates/build/build-dotnet.yml` | 1 (pricing-engine) |
| `templates/build/build-python.yml` | 1 (risk-batch) |
| `templates/test/run-tests.yml` | 2 (pricing-engine, risk-batch) |
| `templates/legacy/build-python-legacy.yml` | 1 (risk-batch-legacy) |
| `alt-templates/frontend/frontend-build.yml` | 1 (frontend-workbench) |
| `alt-templates/frontend/frontend-deploy.yml` | 1 (frontend-workbench, used twice for dev + staging) |
| `alt-templates/team-overrides/team-build-custom.yml` | 1 (regulatory-reporting) |

### Canary Pattern Note

`portfolio-api-canary` declares **4 repository resources** pointing to 4 different branches (`main`, `master`, `staging/preprod`, `staging/release-hardening`) and uses ADO runtime expressions (`${{ if eq(parameters.templateBranch, '...') }}`) to conditionally select which template repository alias to use. This is the only pipeline using the canary/multi-branch pattern and will need special attention during migration since GitHub Actions reusable workflows don't support this pattern natively.

---

## 4. Non-Build Workload Analysis

| Pipeline | What It Does | Agent Pool | Schedule | Internal System Access | Why It Can't Move to GHA Hosted Runners |
|----------|-------------|------------|----------|----------------------|----------------------------------------|
| `services/notebook-executor/azure-pipelines.yml` | Executes Jupyter notebooks for quant model validation overnight using `papermill`. Converts outputs to HTML. | `linux-build-workers` (self-hosted) | Daily at 02:00 UTC | None explicitly, but notebooks may access internal data sources at runtime | Self-hosted pool required for network access to internal data; 180-min timeout exceeds GHA hosted runner 6-hour limit marginally but the real blocker is network access |
| `services/scenario-runner/azure-pipelines.yml` | Runs Monte Carlo simulations (parameterized by scenario count, model version, output format). Aggregates results to JSON. | `high-memory-pool` (self-hosted) | Fridays at 22:00 UTC + manual | None explicitly, but simulation scripts likely need internal data feeds | Requires high-memory agents (not available on GHA hosted); **360-min timeout**; network access to internal systems assumed |
| `night-jobs/compute/var-scenario-sweep.yml` | Runs Value-at-Risk scenario calculations (50,000 scenarios at 3 confidence levels). Uploads results to **data warehouse**. | `high-memory-pool` (self-hosted) | Weeknights (Mon-Fri) at 01:00 UTC | **data-warehouse** (explicit upload step) | Requires high-memory agents; **240-min timeout**; writes to internal data warehouse requiring network access |
| `night-jobs/business/daily-positions-export.yml` | Exports current positions data to Parquet, generates XLSX summary, distributes reports to downstream teams. | `linux-build-workers` (self-hosted) | Weekdays at 23:00 UTC (7 PM ET) | Positions database (via `pyodbc`/`sqlalchemy`); downstream report distribution system | Requires network access to internal positions database and report distribution endpoints; `pyodbc` implies SQL Server/ODBC driver on agent |
| `night-jobs/compliance/attestation-backfill.yml` | Scans **compliance-store** for missing attestations (30-day lookback), regenerates them, records backfill metadata. | `linux-build-workers` (self-hosted) | Sundays at 03:00 UTC | **compliance-store** (read + write) | Requires network access to compliance-store; **180-min timeout**; regulatory data access |
| `adhoc/bulk-reprocess-trades.yml` | Reprocesses historical trade data for a parameterized date range and trade type set. | Hosted (`ubuntu-latest`) | Manual only | Trade data system (implied by script) | **480-min timeout** (8 hours) far exceeds GHA hosted runner limits. Though on hosted pool currently, the extreme timeout is a problem. |
| `adhoc/onetime-data-migration.yml` | Migrates data between databases (`legacy-positions-db` to `positions-db-v2`). Supports dry-run mode. | Hosted (`ubuntu-latest`) | Manual only | **legacy-positions-db**, **positions-db-v2** (via `pyodbc`/`sqlalchemy`) | Database network access required; **300-min timeout**; should probably be deleted (see comments: "should have been deleted afterward") |

### Non-Build Workload Summary

- **7 total non-build workloads** consuming CI infrastructure
- **5 on self-hosted pools** requiring internal network access (the primary migration blocker)
- **2 on hosted pools** but with extreme timeouts (480 min, 300 min)
- **3 access internal databases/warehouses** explicitly (`data-warehouse`, `compliance-store`, `positions-db`)
- All use Python as the execution runtime

**Migration recommendation:** These workloads need dedicated compute infrastructure (e.g., Azure Container Instances, Azure Functions, Kubernetes CronJobs, or GitHub Actions self-hosted runners with network access). They cannot simply be converted to GHA hosted runner workflows.

---

## 5. Ownership Summary

Cross-referencing `# Owner:` comments in pipeline YAML headers with `docs/ownership-gaps.md`:

### Pipelines with Confirmed Owners

| Pipeline | Owner | Confidence | Source |
|----------|-------|------------|--------|
| `services/risk-batch/azure-pipelines.yml` | team-quant | High | YAML header + ownership doc |
| `services/frontend-workbench/azure-pipelines.yml` | team-frontend | High | YAML header + ownership doc |
| `services/regulatory-reporting/azure-pipelines.yml` | team-reporting | High | YAML header + ownership doc |
| `services/portfolio-api/azure-pipelines.yml` | team-quant | Medium | YAML header + ownership doc (but "may not own the codebase") |
| `services/portfolio-api/azure-pipelines-canary.yml` | team-quant | Medium | YAML header |
| `services/ops-control-plane/azure-pipelines.yml` | platform-team | Medium | YAML header + ownership doc |

### Pipelines with Unknown/Missing Owners

| Pipeline | Owner in YAML | Ownership Doc Says | Notes |
|----------|--------------|-------------------|-------|
| `services/pricing-engine/azure-pipelines.yml` | `unknown` | "Original team disbanded. Maintained by shared-ci-platform as best-effort." | **Orphaned.** No real owner. |
| `services/notebook-executor/azure-pipelines.yml` | `?` | "No owner identified. Runs nightly but nobody claims it." | **Orphaned.** Runs unattended nightly. |
| `services/scenario-runner/azure-pipelines.yml` | `?` | "No owner identified. Appears to be a team-quant project." | **Likely team-quant** but unconfirmed. |
| `services/market-sim/azure-pipelines.yml` | `team-quant?` | "Built independently, no template usage, unclear maintenance" | **Uncertain.** Low confidence. |
| `night-jobs/compute/var-scenario-sweep.yml` | (none) | "team-quant? Uses high-memory compute pool" | **Uncertain.** |
| `night-jobs/business/daily-positions-export.yml` | (none) | "team-reporting? Business data export" | **Uncertain.** |
| `night-jobs/compliance/attestation-backfill.yml` | (none) | "shared-ci-platform? Compliance automation" | **Uncertain.** |
| `adhoc/bulk-reprocess-trades.yml` | (none) | "unknown. Triggered manually, unclear frequency" | **No owner.** |
| `adhoc/onetime-data-migration.yml` | (none) | "unknown. Should probably be deleted" | **No owner.** Deletion candidate. |
| `deprecated/old-pricing-pipeline.yml` | (none) | N/A | Deprecated. No owner needed. |
| `deprecated/batch-runner-v1.yml` | (none) | N/A | Deprecated. No owner needed. |
| `services/risk-batch/azure-pipelines-legacy.yml` | (none) | N/A | Legacy/deprecated but still referenced. |

### Pipelines That Should Probably Be Deleted

| Pipeline | Reason |
|----------|--------|
| `adhoc/onetime-data-migration.yml` | Comments explicitly say "should have been deleted afterward" and "probably unused but nobody wants to remove it" |
| `deprecated/old-pricing-pipeline.yml` | Replaced by `services/pricing-engine/azure-pipelines.yml`. Last used 2023-06. Comments say "DO NOT ENABLE." |
| `deprecated/batch-runner-v1.yml` | Replaced by `services/risk-batch` and `night-jobs/compute`. |
| `archive/old-release-workflow.yml` | Archived Q3 2022. Contains only a stub `echo` step. |
| `services/risk-batch/azure-pipelines-legacy.yml` | Trigger disabled; should be deleted **after** downstream dependency investigation (comments warn "Still triggered by some downstream jobs"). |

---

## 6. Template Duplication Findings

### Duplicate Set 1: Python Build Templates (4 locations)

| Location | File | Key Differences |
|----------|------|-----------------|
| `templates/build/build-python.yml` | Central template | Python 3.11 default; includes linting (flake8, black, mypy); uses pytest with coverage; publishes to `artifact-registry`; full-featured |
| `templates/legacy/build-python-legacy.yml` | Legacy template | Python 3.9 default; **no linting**; uses `unittest` instead of pytest; **no artifact-registry integration**; simpler |
| `alt-templates/data-science/build-python.yml` | Data science fork | Python 3.10 default; **adds conda support** and Jupyter notebook execution; installs numpy/pandas/scipy/scikit-learn; uses pytest but no coverage; **no artifact-registry integration** |
| `services/risk-batch/pipeline-fragments/build-python-local.yml` | Service-local fork | Python 3.11 default; **adds custom retry logic** (configurable retry count); configurable timeout; uses `PublishBuildArtifacts@1` directly; **no linting, no artifact-registry** |

**Key gaps driving duplication:**
- Central template lacks conda/Jupyter support (data science need)
- Central template lacks retry logic (batch workload need)
- Legacy template kept for backward compatibility with Python 3.9 and unittest

### Duplicate Set 2: Data Science Python Templates (3 near-identical files)

| Location | File | Differences from siblings |
|----------|------|--------------------------|
| `alt-templates/data-science/build-python.yml` | DS build | Has `condaEnvironment` param; has `runNotebooks` option for Jupyter execution |
| `alt-templates/data-science/ds-model-build.yml` | DS model build | Nearly identical to `build-python.yml` but **without** conda and notebook params. Comments say "nobody remembers why three exist." |
| `alt-templates/data-science/notebook-package-build.yml` | Notebook package | Nearly identical to `ds-model-build.yml` but adds `jupyter` to pip install. Comments say "Appears to have been copied and renamed for a specific project." |

**Recommendation:** These three should be consolidated into a single parameterized template.

### Duplicate Set 3: Batch/Retry Logic (2 locations)

| Location | File | Notes |
|----------|------|-------|
| `alt-templates/data-science/python-batch.yml` | DS batch template | Retry logic with configurable count and 30s sleep between retries; generic script execution |
| `services/risk-batch/pipeline-fragments/build-python-local.yml` | Service-local fork | Very similar retry logic (10s sleep vs 30s); also adds build/package steps |

### Duplicate Set 4: Release Templates (3 locations)

| Location | File | Notes |
|----------|------|-------|
| `templates/release/release-standard.yml` | Central release | Full-featured: `release-orchestrator` notification, compliance attestation, deployment strategy options |
| `templates/legacy/release-old.yml` | Legacy release | **No** `release-orchestrator` integration; **no** compliance attestation; uses older `DownloadBuildArtifacts@1` |
| `templates/release/release-preprod.yml` | Pre-prod release | Simplified version; no compliance attestation; adds smoke tests |

---

## 7. Risk Flags for Migration

### 7.1 Self-Hosted Pool Dependencies

| Pipeline | Pool | Why It Matters |
|----------|------|---------------|
| `services/notebook-executor/azure-pipelines.yml` | `linux-build-workers` | Needs internal network access for notebook data sources |
| `services/scenario-runner/azure-pipelines.yml` | `high-memory-pool` | Needs high-memory agents + internal network |
| `night-jobs/compute/var-scenario-sweep.yml` | `high-memory-pool` | Needs high-memory agents + writes to `data-warehouse` |
| `night-jobs/business/daily-positions-export.yml` | `linux-build-workers` | Needs network access to positions database (ODBC) |
| `night-jobs/compliance/attestation-backfill.yml` | `linux-build-workers` | Needs network access to `compliance-store` |

**Impact:** 5 pipelines require self-hosted runners in GitHub Actions with equivalent network access. GHA hosted runners cannot replace these.

### 7.2 Long Timeouts (>60 min)

| Pipeline | Timeout | Risk |
|----------|---------|------|
| `adhoc/bulk-reprocess-trades.yml` | **480 min (8 hrs)** | Exceeds GHA default 6-hour limit for hosted runners |
| `services/scenario-runner/azure-pipelines.yml` | **360 min (6 hrs)** | At the GHA hosted runner limit |
| `adhoc/onetime-data-migration.yml` | **300 min (5 hrs)** | Should be deleted; moot point |
| `deprecated/batch-runner-v1.yml` | **300 min (5 hrs)** | Deprecated; moot point |
| `night-jobs/compute/var-scenario-sweep.yml` | **240 min (4 hrs)** | Long but within limits if on self-hosted |
| `night-jobs/compliance/attestation-backfill.yml` | **180 min (3 hrs)** | Manageable |
| `services/notebook-executor/azure-pipelines.yml` | **180 min (3 hrs)** | Manageable |
| `night-jobs/business/daily-positions-export.yml` | **120 min (2 hrs)** | Manageable |
| `services/regulatory-reporting/azure-pipelines.yml` | **90 min** | Manageable |

### 7.3 ADO-Specific Features Requiring Migration Effort

| Feature | Pipelines Using It | Migration Complexity |
|---------|-------------------|---------------------|
| `##vso[task.prependpath]` | market-sim, templates/build/build-rust.yml | Replace with `echo "path" >> $GITHUB_PATH` |
| `##vso[task.logissue]` | notebook-executor | Replace with `echo "::warning::"` workflow command |
| `PublishBuildArtifacts@1` task | **13+ pipelines/templates** (nearly all) | Replace with `actions/upload-artifact@v4` |
| `PublishTestResults@2` task | templates/build/build-python.yml, templates/test/run-tests.yml | Replace with third-party test reporting action |
| `DownloadBuildArtifacts@1` task | templates/legacy/release-old.yml | Replace with `actions/download-artifact@v4` |
| Runtime expressions `${{ if eq(...) }}` | portfolio-api-canary, all templates with conditional logic | GHA supports similar `${{ if }}` but syntax differences exist |
| `$[format()]` runtime expressions | var-scenario-sweep, daily-positions-export | No direct GHA equivalent; use shell date commands |
| `resources.repositories` (external repo checkout) | 8 pipelines | Replace with `actions/checkout` with `repository:` parameter |
| ADO-specific tasks (`UsePythonVersion@0`, `UseDotNet@2`, `JavaToolInstaller@0`, `GoTool@0`, `NodeTool@0`, `Maven@4`, `NuGetCommand@2`, `DotNetCoreCLI@2`, `ArchiveFiles@2`) | Widespread across all templates | Replace with GHA `setup-*` actions (setup-python, setup-dotnet, setup-java, setup-go, setup-node) |
| `deployment` job type with `strategy.runOnce` | release-standard.yml, frontend-deploy.yml, release-prod.yml, release-hotfix.yml, release-preprod.yml | GHA has no native equivalent of ADO deployment jobs/environments with approval gates. Use GHA environments with protection rules. |
| Template parameters with `values:` constraint | Multiple templates | GHA `workflow_call` inputs support `options:` for `choice` type but not for all types |

### 7.4 Deprecated Pipelines Still Referenced

| Pipeline | Status | Concern |
|----------|--------|---------|
| `services/risk-batch/azure-pipelines-legacy.yml` | Trigger disabled but comments say "Still triggered by some downstream jobs" | **Must identify downstream dependencies** before migration. If downstream jobs are in other ADO projects, they need updating. |
| `deprecated/old-pricing-pipeline.yml` | References `legacy/master-support` branch | Branch may be deleted during migration cleanup; verify no other consumers first. |
| `deprecated/batch-runner-v1.yml` | Replaced by `services/risk-batch` + `night-jobs/compute` | Safe to skip during migration. |

### 7.5 Template Branch Drift Risk

8 long-lived branches with no protection and no merge cadence. During migration:
- Templates must be **consolidated to a single branch** (or a single set of reusable workflows)
- Differences between branches must be resolved (especially `staging/preprod` retry logic and `team/frontend-custom` SSR support)
- The canary pattern in `portfolio-api-canary` must be redesigned for GHA

### 7.6 External System Integration Risk

The following external systems are called from templates and pipelines. Migration must ensure GHA self-hosted runners have equivalent network access:

| System | Called By | Script |
|--------|----------|--------|
| `artifact-registry` | All central build templates | `build-tools/scripts/publish_artifact.py` |
| `release-orchestrator` | `release-standard.yml`, `release-prod.yml` | `build-tools/scripts/notify_release_orchestrator.py` |
| `compliance-store` | `regulatory-reporting`, `attestation-backfill`, `team-build-custom.yml` | `build-tools/compliance/generate_metadata.py`, `build-tools/scripts/generate_attestation.py` |
| `data-warehouse` | `var-scenario-sweep` | `night-jobs/compute/scripts/upload_results.py` |
| Internal positions DB | `daily-positions-export` | `night-jobs/business/scripts/export_positions.py` (via pyodbc) |
| `legacy-positions-db` / `positions-db-v2` | `onetime-data-migration` | `adhoc/scripts/migrate_data.py` (via pyodbc) |

---

## 8. ADO-to-GitHub Actions Structural Gaps

Beyond feature-level mappings, the following **architectural differences** between Azure DevOps Pipelines and GitHub Actions require significant restructuring during migration.

### 8.1 Step-Level Templates Have No Direct GHA Equivalent

This is the **single largest migration effort**. All 8 template-consuming pipelines use ADO's `template: path.yml@alias` syntax to include shared *steps* from another repository. GitHub Actions reusable workflows (`uses: org/repo/.github/workflows/x.yml@ref`) only operate at the **job level** -- they cannot inject steps into an existing job.

The closest GHA equivalent is **composite actions**, but these:
- Require a specific directory structure (`action.yml` at the repository root or in a dedicated directory)
- Cannot live at arbitrary paths like `templates/build/build-python.yml`
- Use a different parameter syntax (`inputs:` instead of `parameters:`)

**Impact:** All 26 template files must be converted to either composite actions (for step-level reuse) or reusable workflows (for job-level reuse), or their logic must be inlined into consuming workflows.

### 8.2 ADO Stages Do Not Exist in GHA

10 of 18 pipelines use multi-stage pipelines (`stages:` with `dependsOn:`). GitHub Actions has no "stages" concept. Each ADO stage must become either:
- A separate **job** with `needs:` dependencies within one workflow, or
- A separate **workflow** triggered by workflow completion events

Affected pipelines: pricing-engine, portfolio-api, portfolio-api-canary, risk-batch, market-sim, ops-control-plane, frontend-workbench, regulatory-reporting, old-pricing-pipeline (deprecated), old-release-workflow (archived).

### 8.3 Deployment Jobs and Strategies

5 release templates use ADO's `deployment:` job type with `strategy: runOnce` and `environment:` bindings. These provide:
- Built-in artifact download (`download: current`)
- Pre/post deployment hooks
- Deployment strategies (rolling, blue-green, canary)
- Environment approvals tied to the deployment job

GHA has **no deployment job primitive**. The migration path is:
- Use `environment:` on a regular GHA job (for approval gates via protection rules)
- Replace `download: current` with explicit `actions/download-artifact@v4`
- Implement deployment strategies manually (rolling, blue-green, canary have no built-in GHA support)
- Pre/post hooks must be modeled as separate jobs with `needs:` dependencies

### 8.4 Compile-Time vs Runtime Expression Split

ADO has two distinct expression syntaxes:
- **Compile-time:** `${{ }}` -- evaluated when the pipeline YAML is parsed
- **Runtime:** `$[ ]` -- evaluated during pipeline execution

Two pipelines use runtime expressions:
- `night-jobs/compute/var-scenario-sweep.yml`: `$[format('{0:yyyy-MM-dd}', pipeline.startTime)]`
- `night-jobs/business/daily-positions-export.yml`: `$[format('{0:yyyy-MM-dd}', pipeline.startTime)]`

GHA only has `${{ }}` which is evaluated at workflow parse time (with some runtime context available). The `$[format()]` pattern and `pipeline.startTime` variable have no equivalent and must be replaced with shell commands (e.g., `date +%Y-%m-%d`).

### 8.5 ADO Predefined Variables Mapping

| ADO Variable | Used In | GHA Equivalent | Notes |
|---|---|---|---|
| `$(Build.ArtifactStagingDirectory)` | Nearly all pipelines/templates | No equivalent | Use `$RUNNER_TEMP` or explicit paths like `$GITHUB_WORKSPACE/artifacts` |
| `$(Build.SourcesDirectory)` | regulatory-reporting, attestation-backfill, all release templates | `$GITHUB_WORKSPACE` | Direct mapping |
| `$(Build.BuildId)` | All templates calling `publish_artifact.py`, `generate_metadata.py`, etc. | `${{ github.run_id }}` | Direct mapping |
| `$(Build.BuildNumber)` | regulatory-reporting, batch-runner-v1 | `${{ github.run_number }}` | Format may differ |
| `$(Build.SourceBranch)` | pricing-engine, market-sim, frontend-workbench (in conditions) | `${{ github.ref }}` | Both use `refs/heads/...` format |
| `$(Build.Reason)` | common-setup.yml | `${{ github.event_name }}` | Values differ (ADO: `IndividualCI`, GHA: `push`) |
| `$(Agent.MachineName)` | common-setup.yml | No equivalent | Not available on hosted runners |
| `$(Agent.OS)` | common-setup.yml, pool demands | `${{ runner.os }}` | Direct mapping |
| `$(pipeline.startTime)` | var-scenario-sweep, daily-positions-export | No equivalent | Use shell `date` command |
| `$(System.StageName)` | publish-helpers.yml | No equivalent | No stages in GHA |
| `$(system.defaultWorkingDirectory)` | ops-control-plane | `$GITHUB_WORKSPACE` | Direct mapping |

### 8.6 Pool Demands vs Runner Labels

3 pipelines use ADO `demands:` to require specific agent capabilities:
- `notebook-executor`: `Agent.OS -equals Linux`, `python3`
- `scenario-runner`: `Agent.OS -equals Linux`
- `var-scenario-sweep`: `Agent.OS -equals Linux`

GHA self-hosted runners use **labels** instead. The `runs-on:` key accepts a list of labels that the runner must match. The organization will need to:
1. Configure GHA self-hosted runners with equivalent labels (e.g., `linux`, `high-memory`, `python3`)
2. Replace `pool.demands` with `runs-on: [self-hosted, linux, high-memory]` syntax

### 8.7 Pipeline-Level Parameters for Manual Triggers

4 pipelines use ADO `parameters:` with type constraints and `values:` lists for manual/parameterized runs:
- `portfolio-api-canary`: `templateBranch` (string with values list)
- `scenario-runner`: `scenarioCount` (number), `modelVersion` (string), `outputFormat` (string with values)
- `bulk-reprocess-trades`: `startDate`, `endDate` (string), `tradeTypes` (string)
- `onetime-data-migration`: `sourceDb`, `targetDb` (string), `dryRun` (boolean)

GHA equivalent is `workflow_dispatch.inputs:` with `type: choice` and `options:` for constrained values. Key syntax differences:
- ADO: `${{ parameters.paramName }}` -- GHA: `${{ inputs.paramName }}`
- ADO: `type: number` -- GHA: `type: number` (same, but supported only in reusable workflows; `workflow_dispatch` inputs are always strings)
- ADO: `values:` list -- GHA: `type: choice` with `options:` list
- ADO: `type: boolean` with `default: true` -- GHA: `type: boolean` with `default: true` (similar but rendered differently in UI)

### 8.8 Condition Syntax Differences

ADO `condition:` expressions appear on 5+ steps and stages and use a different function syntax than GHA `if:`:

| ADO Syntax | GHA Equivalent |
|---|---|
| `condition: always()` | `if: always()` |
| `condition: succeeded()` | `if: success()` |
| `condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))` | `if: success() && github.ref == 'refs/heads/main'` |

While conceptually similar, every `condition:` expression must be manually translated.

### 8.9 Cross-Repository Template Consumption Architecture

ADO's `resources.repositories` pattern allows a pipeline to declare a dependency on another repository at a specific branch and then reference templates from it using the `@alias` syntax. This is the backbone of the shared template architecture in this repo.

GHA has no direct equivalent of this pattern. The migration options are:
1. **Reusable workflows** in a central `.github/workflows/` directory -- but these only work at job level
2. **Composite actions** published from the shared repo -- requires restructuring all templates into `action.yml` format
3. **Organization-level workflow templates** -- starter templates only, not reusable at runtime

The canary pattern in `portfolio-api-canary` (4 repo resources pointing to 4 branches with runtime selection) has **no GHA equivalent whatsoever** and must be completely redesigned, likely as a matrix strategy or separate workflow files per branch.

---

## Appendix: Template Inventory (Not Pipelines)

For completeness, these are shared template files that are **consumed** by pipelines but are not pipelines themselves:

| File Path | Type | Maintained By |
|-----------|------|--------------|
| `templates/build/build-python.yml` | Build template | shared-ci-platform |
| `templates/build/build-dotnet.yml` | Build template | shared-ci-platform |
| `templates/build/build-java.yml` | Build template | shared-ci-platform |
| `templates/build/build-node.yml` | Build template | shared-ci-platform |
| `templates/build/build-go.yml` | Build template | shared-ci-platform |
| `templates/build/build-rust.yml` | Build template | shared-ci-platform |
| `templates/test/run-tests.yml` | Test template | shared-ci-platform |
| `templates/release/release-standard.yml` | Release template | shared-ci-platform |
| `templates/release/release-prod.yml` | Release template | shared-ci-platform |
| `templates/release/release-hotfix.yml` | Release template | shared-ci-platform |
| `templates/release/release-preprod.yml` | Release template | shared-ci-platform |
| `templates/legacy/build-python-legacy.yml` | Legacy build template | None (frozen) |
| `templates/legacy/release-old.yml` | Legacy release template | None (frozen) |
| `templates/language/setup-python.yml` | Language setup | shared-ci-platform |
| `templates/language/setup-node.yml` | Language setup | shared-ci-platform |
| `templates/language/setup-dotnet.yml` | Language setup | shared-ci-platform |
| `alt-templates/data-science/build-python.yml` | Alt build template | team-quant |
| `alt-templates/data-science/ds-model-build.yml` | Alt build template | team-quant |
| `alt-templates/data-science/python-batch.yml` | Alt batch template | team-quant |
| `alt-templates/data-science/notebook-package-build.yml` | Alt build template | team-quant |
| `alt-templates/frontend/frontend-build.yml` | Alt build template | team-frontend |
| `alt-templates/frontend/frontend-deploy.yml` | Alt deploy template | team-frontend |
| `alt-templates/team-overrides/team-build-custom.yml` | Override template | team-reporting |
| `build-tools/yaml/common-setup.yml` | Setup helper | shared-ci-platform |
| `build-tools/yaml/publish-helpers.yml` | Publish helper | shared-ci-platform |
| `build-tools/release/release-notify.yml` | Notification helper | shared-ci-platform |
| `services/risk-batch/pipeline-fragments/build-python-local.yml` | Service-local fork | team-quant (assumed) |
