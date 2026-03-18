# portfolio-api canary — Migration Verification

## Source

- **ADO Pipeline:** `services/portfolio-api/azure-pipelines-canary.yml`
- **GH Actions Workflow:** `.github/workflows/portfolio-api-canary-ci.yml`
- **Stack:** Java 17 / Maven
- **Owner:** team-quant
- **Pool:** `vmImage: 'ubuntu-latest'` (hosted) -> `runs-on: ubuntu-latest`

## Architecture Diagram

```
ADO Pipeline (expanded)                         GH Actions Workflow
======================================          ======================================

trigger: none                                   on: workflow_dispatch
parameters:                                       inputs:
  templateBranch (4 values)         ->              templateBranch (choice, 4 options)

resources:                                      (no equivalent — see note below)
  repositories: [4 refs]

variables:                                      env:
  artifactName: portfolio-api-canary ->           ARTIFACT_NAME: portfolio-api-canary

Stage: Build                                    Job: build
  Job: build                                      runs-on: ubuntu-latest
  ┌─────────────────────────────────┐           ┌─────────────────────────────────┐
  │ (conditional template select)   │           │                                 │
  │ -> build-java.yml@templates_*   │           │ Checkout repository             │
  │                                 │    ->     │   actions/checkout@v4           │
  │ Step 1: JavaToolInstaller@0     │           │                                 │
  │   versionSpec: 17               │    ->     │ Install JDK 17                  │
  │   jdkSourceOption: PreInstalled │           │   actions/setup-java@v4         │
  │                                 │           │   distribution: temurin         │
  │ Step 2: Maven@4                 │           │                                 │
  │   goals: clean package          │    ->     │ Maven clean package             │
  │   options: -B -DskipTests=false │           │   mvn clean package -B ...      │
  │   publishJUnitResults: true     │           │                                 │
  │   testResultsFiles: **/TEST-*   │    ->     │ Publish test results            │
  │                                 │           │   dorny/test-reporter@v1        │
  │ Step 3: script (stage jars/wars)│    ->     │ Create staging directory        │
  │   cp -> ArtifactStagingDir      │           │ Stage build artifacts           │
  │                                 │           │   cp -> runner.temp/staging     │
  │ Step 4: PublishBuildArtifacts@1 │    ->     │ Upload artifacts                │
  │   artifactName: portfolio-api-  │           │   actions/upload-artifact@v4    │
  │                  canary         │           │                                 │
  │ Step 5: publish_artifact.py     │    ->     │ Register artifact in Artifactory│
  │   --registry Artifactory        │           │   publish_artifact.py + env:    │
  │   --build-id $(Build.BuildId)   │           │   --build-id github.run_id      │
  └─────────────────────────────────┘           └─────────────────────────────────┘
```

## Step-by-Step Comparison

| # | ADO Step | GH Actions Step | Verdict | Notes |
|---|----------|-----------------|---------|-------|
| 0 | *(implicit)* | `actions/checkout@v4` | ADDED | GH Actions requires explicit checkout; ADO checks out automatically |
| 1 | `JavaToolInstaller@0` (JDK 17, PreInstalled) | `actions/setup-java@v4` (temurin, 17) | MATCH | Equivalent JDK setup; temurin is the standard OSS distribution |
| 2 | `Maven@4` (clean package, -B -DskipTests=false) | `mvn clean package -B -DskipTests=false -f pom.xml` | MATCH | Same Maven goals and options; `-f pom.xml` explicit for clarity |
| 3 | `Maven@4` publishJUnitResults=true | `dorny/test-reporter@v1` (java-junit) | MATCH | ADO Maven task has built-in test publishing; GH Actions uses dedicated action |
| 4 | `script: cp target/*.jar *.war -> ArtifactStagingDir` | `run: cp target/*.jar *.war -> runner.temp/staging` | MATCH | Same copy logic; staging directory path mapped |
| 5 | `PublishBuildArtifacts@1` | `actions/upload-artifact@v4` | MATCH | Same artifact upload with matching artifact name |
| 6 | `script: publish_artifact.py` | `run: publish_artifact.py` + `env:` block | MATCH | Same script; ADO env vars mapped to GH equivalents |

## Summary Scorecard

| Metric | Count |
|--------|-------|
| ADO steps (template expanded) | 6 |
| GH Actions steps | 8 |
| Matched | 6 |
| Removed | 0 |
| Added | 2 |

### Added Steps (justification)

1. **Checkout repository** (`actions/checkout@v4`) — GH Actions jobs do not automatically check out the repository. This is required for any workflow.
2. **Create staging directory** (`mkdir -p`) — The ADO `$(Build.ArtifactStagingDirectory)` exists automatically. In GH Actions, `${{ runner.temp }}/staging` must be created explicitly.

### Removed Steps

None.

## Intentional Differences

| # | Difference | Rationale |
|---|-----------|-----------|
| 1 | **No `on.push` or `on.pull_request` trigger** | ADO pipeline has `trigger: none` (manual only). Preserved as `workflow_dispatch` only. Unlike standard CI pipelines, this canary pipeline is intentionally manual — adding automatic triggers would change its purpose. |
| 2 | **Conditional template selection collapsed to single path** | ADO uses 4 `resources.repositories` with different `ref:` values and `${{ if eq() }}` conditionals to select which branch's template to use. GH Actions has no equivalent repository-resource mechanism. Since `templates/build/build-java.yml` is currently identical across all 4 branches (main, master, staging/preprod, staging/release-hardening), the steps are inlined. The `templateBranch` input is preserved for traceability. |
| 3 | **`templateBranch` preserved as informational input** | The workflow_dispatch input documents which template branch was being tested. If the templates diverge in the future, this workflow would need to be updated with conditional logic or a reusable workflow pattern. |
| 4 | **JDK distribution set to `temurin`** | ADO `JavaToolInstaller@0` uses `PreInstalled` JDK. `actions/setup-java@v4` requires an explicit distribution; `temurin` (Eclipse Adoptium) is the standard OSS equivalent. |
| 5 | **Test results via `dorny/test-reporter@v1`** | ADO Maven@4 has built-in `publishJUnitResults`. GH Actions requires a separate action for test result publishing. |

## ADO Environment Variable Mapping for build-tools Scripts

### `publish_artifact.py`

| ADO Env Var | GH Actions Equivalent | Used In |
|-------------|----------------------|---------|
| `BUILD_SOURCEBRANCH` | `${{ github.ref }}` | `publish_artifact.py` line 23 |
| `BUILD_SOURCEVERSION` | `${{ github.sha }}` | `publish_artifact.py` line 24 |
| `AGENT_NAME` | `github-actions` (literal) | `publish_artifact.py` line 25 |
| `BUILD_ARTIFACTSTAGINGDIRECTORY` | `${{ runner.temp }}/staging` | `publish_artifact.py` line 36 |

## Open Items Requiring Runtime Validation

| # | Item | Risk | Validation Method |
|---|------|------|-------------------|
| 1 | **Glob pattern `**/surefire-reports/TEST-*.xml`** | `dorny/test-reporter` glob resolution may differ from ADO Maven@4 task | Run workflow and verify test count matches expected |
| 2 | **Artifact contents parity** | Verify that `upload-artifact@v4` captures the same jar/war files as ADO `PublishBuildArtifacts@1` | Compare artifact manifest from a canary run |
| 3 | **`publish_artifact.py` manifest output** | Verify manifest JSON written to correct path with correct metadata | Inspect `portfolio-api-canary-manifest.json` in workflow run artifacts |
| 4 | **`dorny/test-reporter@v1` pinning** | Third-party action — verify against org policy for allowed actions | Review with security/platform team |
| 5 | **Template drift detection** | If `build-java.yml` diverges across branches in the future, this single-path workflow will not reflect the differences | Periodic comparison or consolidation of template branches |
