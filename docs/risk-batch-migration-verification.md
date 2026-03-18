# risk-batch ADO-to-GitHub Actions Migration Verification

## Source Pipeline

- **ADO pipeline**: `services/risk-batch/azure-pipelines.yml`
- **GH Actions workflow**: `.github/workflows/risk-batch-ci.yml`
- **Stack**: Python 3.11
- **Template branch**: `staging/preprod` (central templates with retry logic additions)
- **Owner**: team-quant

## Architecture Diagram

```
ADO Pipeline (expanded)                        GH Actions Workflow
==================================             ==================================

Stage: Build                                   Job: build
  Job: build                                     runs-on: ubuntu-latest
  ┌──────────────────────────────┐             ┌──────────────────────────────┐
  │ [build-python.yml template]  │             │                              │
  │                              │             │ actions/checkout@v4           │
  │ UsePythonVersion@0           │ ──────────> │ actions/setup-python@v5      │
  │ pip install                  │ ──────────> │ run: pip install             │
  │ flake8 + black (lint)        │ ──────────> │ run: flake8 + black          │
  │ pytest w/ retry + coverage   │ ──────────> │ run: pytest w/ retry + cov   │
  │ PublishTestResults@2         │ ──────────> │ dorny/test-reporter@v1       │
  │ setup.py sdist bdist_wheel   │ ──────────> │ run: setup.py sdist bdist    │
  │ PublishBuildArtifacts@1      │ ──────────> │ actions/upload-artifact@v4   │
  │ publish_artifact.py          │ ──────────> │ run: publish_artifact.py     │
  │ preprod stamp (staging only) │ ──────────> │ run: preprod stamp           │
  │                              │             │                              │
  │ [run-tests.yml template]     │             │                              │
  │ mkdir test-results           │ ──────────> │ run: mkdir test-results      │
  │ pytest (plain)               │ ──────────> │ run: pytest (plain)          │
  │ PublishTestResults@2         │ ──────────> │ dorny/test-reporter@v1       │
  │ normalize_test_results.py    │ ──────────> │ run: normalize_test_results  │
  └──────────────────────────────┘             └──────────────────────────────┘
           │                                              │
           │ dependsOn: Build                             │ needs: build
           ▼                                              ▼
Stage: Release                                 Job: release-dev
  [release-standard.yml template]                runs-on: ubuntu-latest
  ┌──────────────────────────────┐               environment: dev
  │ download: current            │             ┌──────────────────────────────┐
  │                              │             │ actions/checkout@v4           │
  │                              │             │ actions/setup-python@v5      │
  │ download artifact            │ ──────────> │ actions/download-artifact@v4 │
  │ echo deploy                  │ ──────────> │ run: echo deploy             │
  │ notify_release_orchestrator  │ ──────────> │ run: notify_release_orch.py  │
  │ generate_attestation.py      │ ──────────> │ run: generate_attestation.py │
  └──────────────────────────────┘             └──────────────────────────────┘
```

## Step-by-Step Comparison

| # | ADO Step (Expanded) | Source Template | GH Actions Step | Verdict | Notes |
|---|---------------------|-----------------|-----------------|---------|-------|
| 1 | *(implicit checkout)* | ADO auto | `actions/checkout@v4` | ADDED | GH Actions requires explicit checkout |
| 2 | *(implicit)* | — | Create staging directory | ADDED | GH Actions has no `ArtifactStagingDirectory`; must create manually |
| 3 | `UsePythonVersion@0` (3.11) | build-python.yml | `actions/setup-python@v5` (3.11) | MATCH | |
| 4 | `pip install -r requirements.txt` | build-python.yml | `run: pip install -r requirements.txt` | MATCH | |
| 5 | `flake8 + black --check` (lint) | build-python.yml | `run: flake8 + black --check` | MATCH | enableLinting=true (default) |
| 6 | pytest with retry loop + coverage | build-python.yml | `run: pytest` with retry loop + coverage | MATCH | staging/preprod retry logic preserved: MAX_RETRY=3, --reruns 2, --reruns-delay 5 |
| 7 | `PublishTestResults@2` (JUnit XML) | build-python.yml | `dorny/test-reporter@v1` | MATCH | `if: always()` preserved |
| 8 | `setup.py sdist bdist_wheel` | build-python.yml | `run: setup.py sdist bdist_wheel` | MATCH | |
| 9 | `PublishBuildArtifacts@1` | build-python.yml | `actions/upload-artifact@v4` | MATCH | |
| 10 | `publish_artifact.py` | build-python.yml | `run: publish_artifact.py` | MATCH | env: BUILD_SOURCEBRANCH, BUILD_SOURCEVERSION, AGENT_NAME, BUILD_ARTIFACTSTAGINGDIRECTORY |
| 11 | Stamp preprod validation marker | build-python.yml (staging/preprod) | `run: echo stamp` | MATCH | staging/preprod-specific step |
| 12 | `mkdir -p test-results` | run-tests.yml | `run: mkdir -p test-results` | MATCH | |
| 13 | `pytest tests/ --junitxml --tb=short` | run-tests.yml | `run: pytest tests/ --junitxml --tb=short` | MATCH | Second pytest run (no retry/coverage) |
| 14 | `PublishTestResults@2` (run-tests) | run-tests.yml | `dorny/test-reporter@v1` | MATCH | `if: always()` preserved, failOnTestFailure=true |
| 15 | `normalize_test_results.py` | run-tests.yml | `run: normalize_test_results.py` | MATCH | `if: always()` preserved |
| 16 | `download: current` artifact | release-standard.yml | `actions/download-artifact@v4` | MATCH | |
| 17 | *(implicit checkout)* | — | `actions/checkout@v4` | ADDED | Needed for build-tools scripts in release job |
| 18 | *(implicit)* | — | `actions/setup-python@v5` | ADDED | Needed to run Python scripts in release job |
| 19 | Echo deploy message | release-standard.yml | `run: echo deploy` | MATCH | |
| 20 | `notify_release_orchestrator.py` | release-standard.yml | `run: notify_release_orchestrator.py` | MATCH | env: PIPELINE_URL (override), BUILD_REQUESTEDFOR |
| 21 | `generate_attestation.py` | release-standard.yml | `run: generate_attestation.py` | MATCH | env: BUILD_SOURCEBRANCH, BUILD_SOURCEVERSION, BUILD_DEFINITIONNAME, AGENT_OS, BUILD_ARTIFACTSTAGINGDIRECTORY |

## ADO Task Removal Log

| ADO Task | Reason |
|----------|--------|
| `NuGetToolInstaller@1` | Not used (Python pipeline) |
| `NuGetCommand@2` | Not used (Python pipeline) |

No ADO tasks were removed from this pipeline. All tasks present in the expanded templates are mapped.

## Summary Scorecard

| Metric | Count |
|--------|-------|
| **Total ADO steps (expanded)** | 15 |
| **Matched GH Actions steps** | 15 |
| **Removed (with justification)** | 0 |
| **Added (with justification)** | 6 |

### Added Steps (justification)

1. **`actions/checkout@v4`** (build job) — GH Actions requires explicit repository checkout; ADO does this implicitly.
2. **Create staging directory** (build job) — GH Actions has no `Build.ArtifactStagingDirectory`; created at `${{ runner.temp }}/staging`.
3. **`actions/checkout@v4`** (release job) — GH Actions jobs are isolated; release job needs repo access for `build-tools/` scripts.
4. **`actions/setup-python@v5`** (release job) — GH Actions jobs are isolated; release job needs Python to run scripts.
5. **Create staging directory** (release job) — Same as build job; needed for attestation output path.
6. **`on.pull_request` trigger** — Standard GH Actions practice for CI validation on PRs. ADO pipeline had no PR trigger.

## Intentional Differences

1. **PR trigger added**: `on.pull_request` added for standard CI validation. ADO pipeline only triggered on `push` to `main`.
2. **`workflow_dispatch` added**: Enables manual runs from the GH Actions UI.
3. **`PIPELINE_URL` env var**: `notify_release_orchestrator.py` updated to accept `PIPELINE_URL` override (backward-compatible with ADO). In GH Actions, this is set to the correct Actions run URL instead of constructing from `SYSTEM_TEAMFOUNDATIONCOLLECTIONURI`.
4. **Duplicate test execution preserved**: The ADO pipeline runs pytest twice — once from `build-python.yml` (with retry + coverage) and once from `run-tests.yml` (plain). This duplication is preserved for behavioral parity but should be reviewed by the team for potential consolidation.
5. **`dorny/test-reporter@v1`** used instead of `PublishTestResults@2` — third-party action; see review checklist.

## build-tools/ Script Env Var Mapping

### `publish_artifact.py`
| ADO Env Var | GH Actions Equivalent | Used For |
|-------------|----------------------|----------|
| `BUILD_SOURCEBRANCH` | `${{ github.ref }}` | Source branch metadata |
| `BUILD_SOURCEVERSION` | `${{ github.sha }}` | Source commit metadata |
| `AGENT_NAME` | `github-actions` (literal) | Agent identification |
| `BUILD_ARTIFACTSTAGINGDIRECTORY` | `${{ runner.temp }}/staging` | Manifest output path |

### `notify_release_orchestrator.py`
| ADO Env Var | GH Actions Equivalent | Used For |
|-------------|----------------------|----------|
| `SYSTEM_TEAMFOUNDATIONCOLLECTIONURI` + `SYSTEM_TEAMPROJECT` | `PIPELINE_URL` override | Pipeline run URL |
| `BUILD_REQUESTEDFOR` | `${{ github.actor }}` | Who triggered the build |

### `generate_attestation.py`
| ADO Env Var | GH Actions Equivalent | Used For |
|-------------|----------------------|----------|
| `BUILD_SOURCEBRANCH` | `${{ github.ref }}` | Source branch metadata |
| `BUILD_SOURCEVERSION` | `${{ github.sha }}` | Source commit metadata |
| `BUILD_DEFINITIONNAME` | `risk-batch CI` (literal) | Pipeline name |
| `AGENT_OS` | `Linux` (literal) | Agent OS |
| `BUILD_ARTIFACTSTAGINGDIRECTORY` | `${{ runner.temp }}/staging` | Attestation output path |

### `normalize_test_results.py`
No ADO env var dependencies. Uses only CLI arguments (`--input-dir`, `--output`).

## Open Items Requiring Runtime Validation

1. **Glob pattern for test-reporter**: `${{ runner.temp }}/staging/test-results/**/*.xml` — verify glob resolves correctly on GH-hosted runners.
2. **Artifact parity**: Validate that `actions/upload-artifact@v4` / `actions/download-artifact@v4` produce equivalent artifact content to `PublishBuildArtifacts@1` / `download: current`.
3. **Test counts**: Confirm that the two pytest invocations produce the expected test counts (duplication may inflate totals).
4. **Compliance JSON schema**: Verify `generate_attestation.py` output matches schema version 2.1 when running with GH Actions env vars.
5. **`dorny/test-reporter@v1`**: Third-party action — verify it is approved per org security policy. Consider pinning to a specific SHA.
6. **preprod stamp file**: Confirm `preprod-stamp.txt` is included in the uploaded artifact and accessible in the release job if needed.
7. **`publish_artifact.py` registry call**: In production this POSTs to artifact-registry — verify connectivity from GH-hosted runners.

## Human Review Checklist

- [ ] Verify glob patterns resolve correctly (`**/*.xml` in test-reporter)
- [ ] Confirm `dorny/test-reporter@v1` is approved for org use (third-party action)
- [ ] Review duplicate pytest execution — consolidate if not intentional
- [ ] Validate artifact content parity between ADO and GH Actions
- [ ] Confirm `PIPELINE_URL` override in `notify_release_orchestrator.py` is backward-compatible
- [ ] Verify compliance attestation JSON schema compatibility
- [ ] End-to-end validation: trigger workflow on a test branch and compare outputs
