# Bulk Reprocess Trades — Migration Verification

**Source:** `adhoc/bulk-reprocess-trades.yml`
**Target:** `.github/workflows/bulk-reprocess-trades-ci.yml`
**Stack:** Python 3.11
**Template source:** NONE (fully inline)
**Pool:** `vmImage: ubuntu-latest` (hosted) -> `runs-on: ubuntu-latest`

---

## Architecture Diagram

```
ADO Pipeline (adhoc/bulk-reprocess-trades.yml)     GitHub Actions (.github/workflows/bulk-reprocess-trades-ci.yml)
================================================    ===============================================================

trigger: none                                   =>  on: workflow_dispatch
parameters:                                     =>    inputs:
  - startDate (string, '2024-01-01')            =>      startDate (string, '2024-01-01')
  - endDate   (string, '2024-01-31')            =>      endDate   (string, '2024-01-31')
  - tradeTypes (string, 'all')                  =>      tradeTypes (string, 'all')

pool: vmImage 'ubuntu-latest'                   =>  runs-on: ubuntu-latest

jobs:                                           =>  jobs:
  ReprocessTrades (timeout: 480m)               =>    reprocess-trades (timeout: 480m)
  |                                             =>    |
  +-- UsePythonVersion@0 (3.11)                 =>    +-- actions/checkout@v4            [ADDED]
  |                                             =>    +-- actions/setup-python@v5 (3.11)
  +-- script: pip install ...                   =>    +-- run: pip install ...
  |                                             =>    +-- run: mkdir staging dir         [ADDED]
  +-- script: reprocess_trades.py (420m)        =>    +-- run: reprocess_trades.py (420m)
  +-- PublishBuildArtifacts@1                    =>    +-- actions/upload-artifact@v4
```

---

## Step-by-Step Comparison

| # | ADO Step | GH Actions Step | Verdict | Notes |
|---|----------|-----------------|---------|-------|
| 0 | *(implicit checkout)* | `actions/checkout@v4` | ADDED | ADO checks out automatically; GH Actions requires explicit checkout step |
| 1 | `UsePythonVersion@0` (versionSpec: 3.11) | `actions/setup-python@v5` (python-version: 3.11) | MATCH | Direct equivalent |
| 2 | `script: pip install pandas requests pyarrow` | `run: pip install pandas requests pyarrow` | MATCH | Identical command |
| 3 | *(implicit)* | `run: mkdir -p staging dir` | ADDED | GH Actions needs explicit directory creation; ADO provides `$(Build.ArtifactStagingDirectory)` automatically |
| 4 | `script: reprocess_trades.py` (timeout: 420m) | `run: reprocess_trades.py` (timeout-minutes: 420) | MATCH | Same script invocation; parameters passed via `env:` block and referenced as quoted shell variables (`"$START_DATE"`, etc.) to prevent script injection; output path mapped from `$(Build.ArtifactStagingDirectory)` to `${{ runner.temp }}/staging` |
| 5 | `PublishBuildArtifacts@1` (artifactName: reprocessed-trades) | `actions/upload-artifact@v4` (name: reprocessed-trades) | MATCH | Direct equivalent; artifact name preserved |

---

## Summary Scorecard

| Metric | Count |
|--------|-------|
| Total ADO steps | 4 |
| Total GH Actions steps | 6 |
| Matched (1:1 equivalent) | 4 |
| Removed | 0 |
| Added (with justification) | 2 |

---

## Intentional Differences

| Difference | Justification |
|------------|---------------|
| **Added `actions/checkout@v4` step** | ADO pipelines automatically check out the repository. GitHub Actions requires an explicit checkout step. |
| **Added staging directory creation step** | ADO provides `$(Build.ArtifactStagingDirectory)` as a pre-existing directory. GitHub Actions has no equivalent, so `${{ runner.temp }}/staging` is created explicitly. |
| **`trigger: none` -> `on: workflow_dispatch` only** | ADO `trigger: none` means manual-only. The GitHub Actions equivalent is `workflow_dispatch` with no other triggers. No `pull_request` trigger added since this is an ad-hoc operational pipeline, not a CI build. |
| **ADO `parameters` -> `workflow_dispatch.inputs`** | ADO runtime parameters map directly to GitHub Actions `workflow_dispatch` inputs with the same names, types, and defaults. |
| **Variable syntax change** | `${{ parameters.X }}` -> `${{ inputs.X }}` (passed via step `env:` block as `$START_DATE` / `$END_DATE` / `$TRADE_TYPES` for safe shell interpolation); `$(Build.ArtifactStagingDirectory)` -> `${{ runner.temp }}/staging` |

---

## Open Items Requiring Runtime Validation

| Item | Detail |
|------|--------|
| **Artifact parity** | Verify that `actions/upload-artifact@v4` captures the same directory structure as `PublishBuildArtifacts@1` with `pathToPublish: $(Build.ArtifactStagingDirectory)`. The GH Actions step uploads from `${{ runner.temp }}/staging`. |
| **Script path resolution** | Confirm `adhoc/scripts/reprocess_trades.py` resolves correctly from `${{ github.workspace }}` (the checkout root). ADO resolves from `$(Build.SourcesDirectory)` which is equivalent. |
| **Parameter quoting** | Inputs are passed via `env:` and quoted in shell (`"$START_DATE"`, etc.) to prevent injection. Verify comma-separated `tradeTypes` values (e.g., `equity,fx`) are parsed correctly by `reprocess_trades.py`. |
| **8-hour timeout** | Confirm GitHub Actions allows 480-minute job timeout on the repository's plan. GitHub-hosted runners support up to 6 hours (360 minutes) on free plans but longer on paid plans. The organization may need to verify this limit. |
| **Step-level timeout** | Verify `timeout-minutes: 420` on the reprocess step behaves consistently with ADO's `timeoutInMinutes: 420`. |

---

## Build-Tools Script Dependencies

**None.** This pipeline does not invoke any `build-tools/` scripts. The only script referenced is `adhoc/scripts/reprocess_trades.py`, which is a project-specific operational script, not a shared build tool.

---

## Third-Party Actions Review

| Action | Version | Notes |
|--------|---------|-------|
| `actions/checkout@v4` | v4 | Official GitHub action |
| `actions/setup-python@v5` | v5 | Official GitHub action |
| `actions/upload-artifact@v4` | v4 | Official GitHub action |

All actions are official GitHub-maintained actions. No third-party actions requiring org policy verification.
