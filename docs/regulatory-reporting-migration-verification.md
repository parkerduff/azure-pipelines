# regulatory-reporting — ADO to GitHub Actions Migration Verification

## Pipeline Overview

| Field               | Value                                                            |
|---------------------|------------------------------------------------------------------|
| **Service**         | regulatory-reporting                                             |
| **Stack**           | Python 3.11                                                      |
| **Template Source**  | HYBRID — `alt-templates/team-overrides/team-build-custom.yml` + inline steps |
| **Template Branch** | `team/reporting-hotfix`                                          |
| **Owner**           | team-reporting                                                   |
| **Pool**            | `vmImage: ubuntu-latest` (hosted)                                |
| **Classification**  | Compliance/reporting workflow (not a deployable artifact)         |
| **ADO Pipeline**    | `services/regulatory-reporting/azure-pipelines.yml`              |
| **GH Workflow**     | `.github/workflows/regulatory-reporting-ci.yml`                  |

---

## Architecture Diagram

```
ADO Pipeline (Expanded)                          GitHub Actions Workflow
═══════════════════════════════════════           ═══════════════════════════════════
                                                  on: push (main, paths), pull_request,
trigger: main, paths                                  schedule (0 6 * * 1-5),
schedules: 0 6 * * 1-5                               workflow_dispatch

┌─── Stage: ComplianceBuild ──────────┐           ┌─── Job: compliance-build ──────────┐
│                                     │           │                                    │
│  [team-build-custom.yml expanded]   │           │  checkout                          │
│                                     │           │  Log compliance context             │
│  1. Log compliance context          │  ──────►  │  setup-python@v5 (3.11)            │
│  2. UsePythonVersion@0 (3.11)       │           │  Create staging directory           │
│  3. pip install + pytest + sdist    │           │  pip install + pytest + sdist       │
│  4. generate_metadata.py            │           │  generate_metadata.py (env mapped)  │
│     (regulatory-compliance-pkg)     │           │  upload-artifact@v4                 │
│  5. PublishBuildArtifacts@1         │           │    (regulatory-compliance-pkg)      │
│                                     │           │                                    │
└─────────────────────────────────────┘           └────────────────────────────────────┘
               │                                                  │
               ▼ dependsOn                                        ▼ needs
┌─── Stage: GenerateReports ──────────┐           ┌─── Job: generate-reports ───────────┐
│  timeout: 90 min                    │           │  timeout-minutes: 90                │
│                                     │           │                                    │
│  1. UsePythonVersion@0 (3.11)       │           │  checkout                          │
│  2. pip install (requirements.txt)  │  ──────►  │  setup-python@v5 (3.11)            │
│  3. generate_reports.py             │           │  Create staging directory           │
│  4. generate_metadata.py            │           │  pip install (requirements.txt)    │
│     (regulatory-reports)            │           │  generate_reports.py               │
│  5. generate_attestation.py         │           │  generate_metadata.py (env mapped) │
│  6. PublishBuildArtifacts@1         │           │  generate_attestation.py (env map) │
│                                     │           │  upload-artifact@v4                │
│                                     │           │    (regulatory-reports)            │
└─────────────────────────────────────┘           └────────────────────────────────────┘
```

---

## Step-by-Step Comparison

### Stage: ComplianceBuild → Job: compliance-build

Template expanded: `alt-templates/team-overrides/team-build-custom.yml`
Parameters: `language=python`, `complianceLevel=elevated`, `artifactName=regulatory-compliance-pkg`, `generateMetadata=true`

| # | ADO Step (Expanded)                            | GH Actions Step                              | Verdict  | Notes |
|---|------------------------------------------------|----------------------------------------------|----------|-------|
| — | *(implicit checkout)*                          | `actions/checkout@v4`                        | ADDED    | GH Actions requires explicit checkout |
| 1 | `echo "Build initiated..."` (Log context)      | `Log compliance context` (run: echo)         | MATCH    | |
| 2 | `UsePythonVersion@0` (3.11)                    | `actions/setup-python@v5` (3.11)             | MATCH    | Task → action mapping |
| — | *(ADO staging dir exists by default)*           | `Create staging directory` (mkdir -p)        | ADDED    | GH Actions needs explicit dir creation |
| 3 | `pip install + pytest + sdist`                 | `Build and test (Python)` (same commands)    | MATCH    | |
| 4 | `generate_metadata.py` (compliance metadata)   | `Generate compliance metadata` (env mapped)  | MATCH    | ADO env vars mapped to GH equivalents |
| 5 | `PublishBuildArtifacts@1`                       | `actions/upload-artifact@v4`                 | MATCH    | Task → action mapping |

### Stage: GenerateReports → Job: generate-reports

| # | ADO Step                                       | GH Actions Step                              | Verdict  | Notes |
|---|------------------------------------------------|----------------------------------------------|----------|-------|
| — | *(implicit checkout)*                          | `actions/checkout@v4`                        | ADDED    | GH Actions jobs are isolated |
| 1 | `UsePythonVersion@0` (3.11)                    | `actions/setup-python@v5` (3.11)             | MATCH    | |
| — | *(ADO staging dir exists by default)*           | `Create staging directory` (mkdir -p)        | ADDED    | GH Actions needs explicit dir creation |
| 2 | `pip install -r .../requirements.txt`          | `Install dependencies`                       | MATCH    | |
| 3 | `generate_reports.py` (--output-dir, etc.)     | `Generate regulatory reports`                | MATCH    | ADO vars substituted with GH equivalents |
| 4 | `generate_metadata.py` (regulatory-reports)    | `Upload compliance metadata` (env mapped)    | MATCH    | |
| 5 | `generate_attestation.py` (prod attestation)   | `Generate attestation record` (env mapped)   | MATCH    | |
| 6 | `PublishBuildArtifacts@1`                       | `actions/upload-artifact@v4`                 | MATCH    | |

---

## Summary Scorecard

| Metric                     | Count |
|----------------------------|-------|
| **Total ADO steps**        | 11    |
| **Matched steps**          | 11    |
| **Removed steps**          | 0     |
| **Added steps**            | 4     |
| **Total GH Actions steps** | 15    |

### Added Steps (with justification)

| Step                        | Justification                                                          |
|-----------------------------|------------------------------------------------------------------------|
| `actions/checkout@v4` (x2)  | GH Actions requires explicit checkout; ADO does it implicitly          |
| `Create staging directory` (x2) | ADO provides `Build.ArtifactStagingDirectory` pre-created; GH does not |

### Removed Steps

None. All ADO steps have a 1:1 equivalent.

---

## Trigger Mapping

| ADO Trigger                                     | GH Actions Trigger                                | Verdict  |
|-------------------------------------------------|---------------------------------------------------|----------|
| `trigger.branches.include: [main]`              | `on.push.branches: [main]`                        | MATCH    |
| `trigger.paths.include: [services/regulatory-reporting/**]` | `on.push.paths: ['services/regulatory-reporting/**']` | MATCH |
| `schedules[].cron: '0 6 * * 1-5'`              | `on.schedule[].cron: '0 6 * * 1-5'`              | MATCH    |
| *(no PR trigger)*                                | `on.pull_request` (main, same paths)              | ADDED    |
| *(no manual trigger)*                            | `on.workflow_dispatch`                             | ADDED    |

---

## Environment Variable Mapping for build-tools Scripts

### `generate_metadata.py`

| ADO Env Var                        | GH Actions Mapping                          | Used By Script |
|------------------------------------|---------------------------------------------|----------------|
| `BUILD_DEFINITIONNAME`             | `regulatory-reporting CI` (literal)          | Line 25        |
| `BUILD_REPOSITORY_NAME`           | `${{ github.repository }}`                   | Line 26        |
| `BUILD_SOURCEBRANCH`              | `${{ github.ref }}`                          | Line 27        |
| `BUILD_SOURCEVERSION`             | `${{ github.sha }}`                          | Line 28        |
| `AGENT_NAME`                      | `github-actions` (literal)                   | Line 29        |
| `BUILD_ARTIFACTSTAGINGDIRECTORY`  | `${{ runner.temp }}/staging`                 | Line 39        |

### `generate_attestation.py`

| ADO Env Var                        | GH Actions Mapping                          | Used By Script |
|------------------------------------|---------------------------------------------|----------------|
| `BUILD_SOURCEBRANCH`              | `${{ github.ref }}`                          | Line 26        |
| `BUILD_SOURCEVERSION`             | `${{ github.sha }}`                          | Line 27        |
| `BUILD_DEFINITIONNAME`            | `regulatory-reporting CI` (literal)          | Line 28        |
| `AGENT_OS`                        | `Linux` (literal)                            | Line 29        |
| `BUILD_ARTIFACTSTAGINGDIRECTORY`  | `${{ runner.temp }}/staging`                 | Line 47        |

---

## Intentional Differences

1. **`on.pull_request` trigger added** — Standard GH Actions practice for CI validation on PRs. ADO pipeline only triggered on push to main and on schedule.
2. **`on.workflow_dispatch` added** — Enables manual triggering from the GH Actions UI, useful for ad-hoc compliance runs.
3. **Explicit `actions/checkout@v4`** — ADO implicitly checks out code; GH Actions requires an explicit step.
4. **Explicit staging directory creation** — ADO provides `Build.ArtifactStagingDirectory` as a pre-existing path; GH Actions requires manual directory creation.
5. **Template expansion** — ADO `team-build-custom.yml` template reference is expanded inline in GH Actions since reusable workflows have different semantics. All template logic is preserved.

---

## Open Items Requiring Runtime Validation

| Item | Description | Risk |
|------|-------------|------|
| **Glob patterns** | ADO task globs (`pathToPublish`) vs GH `upload-artifact` `path:` — verify `${{ runner.temp }}/staging` captures the correct files | Low |
| **Artifact parity** | Confirm `regulatory-compliance-pkg` and `regulatory-reports` artifacts contain the same files as ADO equivalents | Medium |
| **Test counts** | `pytest tests/ -v` output should show same test count as ADO runs | Low |
| **Compliance JSON schema** | `generate_metadata.py` output must conform to schema v1.3; `generate_attestation.py` to schema v2.1 — verify `"pipeline"` field reads `"regulatory-reporting CI"` instead of `"unknown"` | Medium |
| **Schedule precision** | Cron `0 6 * * 1-5` in GH Actions may have up to ~15 min delay vs ADO scheduling — acceptable for compliance runs | Low |
| **`requirements.txt` path** | ComplianceBuild job runs `pip install -r requirements.txt` (relative, from repo root). Verify this file exists at repo root or adjust path. GenerateReports job uses `services/regulatory-reporting/requirements.txt` (explicit path). | Medium |
| **`setup.py`** | ComplianceBuild runs `python setup.py sdist bdist_wheel` — verify `setup.py` exists at repo root | Medium |
| **Third-party actions** | `actions/checkout@v4`, `actions/setup-python@v5`, `actions/upload-artifact@v4` — verify these are approved per org policy | Low |
