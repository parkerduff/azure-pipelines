# portfolio-api: ADO → GitHub Actions Migration Verification

## Pipeline Identity

| Field                | Value                                              |
|----------------------|----------------------------------------------------|
| Service              | portfolio-api                                      |
| Stack                | Java 17 / Maven                                    |
| ADO Pipeline         | `services/portfolio-api/azure-pipelines.yml`       |
| GH Actions Workflow  | `.github/workflows/portfolio-api-ci.yml`           |
| Template Source      | central (`templates/`) from `master` branch (legacy)|
| Owner                | team-quant                                         |
| Pool                 | `vmImage: ubuntu-latest` (hosted)                  |
| ADO Stages           | Build → Release (staging)                          |
| GH Actions Jobs      | build → deploy-staging                             |

---

## Architecture Diagram

```
ADO Pipeline (expanded)                       GitHub Actions Workflow
================================              ================================

services/portfolio-api/                       .github/workflows/
  azure-pipelines.yml                           portfolio-api-ci.yml
       |                                             |
       v                                             v
  trigger:                                      on:
    branches: [main, master]                      push:
    paths: [services/portfolio-api/**]              branches: [main, master]
                                                    paths: [services/portfolio-api/**]
                                                  pull_request:           <-- ADDED
                                                    branches: [main]
                                                    paths: [services/portfolio-api/**]
       |                                             |
       v                                             v
  ┌─ Stage: Build ───────────────┐            ┌─ Job: build ──────────────────┐
  │                              │            │                               │
  │  build-java.yml@templates    │            │  actions/checkout@v4          │
  │  (master branch)             │            │  actions/setup-java@v4        │
  │                              │            │    (temurin, JDK 17)          │
  │  ┌─ JavaToolInstaller@0 ──┐ │            │  mvn package -B               │
  │  │  JDK 17, x64           │ │ ────────── │    -DskipTests=false          │
  │  └────────────────────────┘ │            │  cp target/*.jar|*.war        │
  │  ┌─ Maven@4 ──────────────┐ │            │    → $RUNNER_TEMP/staging     │
  │  │  goal: package          │ │ ────────── │  actions/upload-artifact@v4   │
  │  │  options: -B            │ │            │    name: portfolio-api-dist   │
  │  │    -DskipTests=false    │ │            │  publish_artifact.py          │
  │  │  publishJUnitResults:   │ │            │    --registry Artifactory     │
  │  │    true                 │ │            │    env: BUILD_SOURCEBRANCH,   │
  │  └────────────────────────┘ │            │      BUILD_SOURCEVERSION,     │
  │  ┌─ Stage artifacts ──────┐ │            │      BUILD_ARTIFACTSTAGING.., │
  │  │  cp *.jar/*.war to     │ │ ────────── │      AGENT_NAME               │
  │  │  $(ArtifactStagingDir) │ │            │                               │
  │  └────────────────────────┘ │            └───────────────────────────────┘
  │  ┌─ PublishBuildArtifacts ─┐ │                       |
  │  │  artifact:              │ │                       | needs: build
  │  │   portfolio-api-dist    │ │                       v
  │  └────────────────────────┘ │            ┌─ Job: deploy-staging ──────────┐
  │  ┌─ publish_artifact.py ──┐ │            │  if: refs/heads/main && push   │
  │  │  --registry Artifactory │ │            │  environment: staging          │
  │  │  --build-id $(BuildId) │ │            │                               │
  │  └────────────────────────┘ │            │  actions/download-artifact@v4  │
  └──────────────────────────────┘            │    name: portfolio-api-dist   │
       |                                      │  actions/checkout@v4          │
       | dependsOn: Build                     │  echo "Deploying ... to      │
       v                                      │    staging / rolling"        │
  ┌─ Stage: Release ─────────────┐            │  notify_release_orchestrator  │
  │  release-standard.yml        │            │    .py                        │
  │  (master branch)             │            │    env: BUILD_REQUESTEDFOR,   │
  │                              │            │      PIPELINE_URL             │
  │  environment: staging        │ ────────── │  generate_attestation.py      │
  │  strategy: runOnce           │            │    env: BUILD_SOURCEBRANCH,   │
  │  requireApproval: false      │            │      BUILD_SOURCEVERSION,     │
  │  notifyReleaseOrch: true     │            │      BUILD_DEFINITIONNAME,    │
  │                              │            │      BUILD_ARTIFACTSTAGING.., │
  │  ┌─ download: current ────┐ │            │      AGENT_OS                 │
  │  │  artifact:              │ │ ────────── │                               │
  │  │   portfolio-api-dist    │ │            └───────────────────────────────┘
  │  └────────────────────────┘ │
  │  ┌─ Execute deployment ───┐ │
  │  │  echo "Deploying to    │ │
  │  │   staging / rolling"   │ │
  │  └────────────────────────┘ │
  │  ┌─ notify_release_orch ──┐ │
  │  │  --service portfolio-  │ │
  │  │    api-dist             │ │
  │  │  --env staging          │ │
  │  │  --status success       │ │
  │  └────────────────────────┘ │
  │  ┌─ generate_attestation ─┐ │
  │  │  --artifact portfolio- │ │
  │  │    api-dist             │ │
  │  │  --env staging          │ │
  │  └────────────────────────┘ │
  └──────────────────────────────┘
```

---

## Step-by-Step Comparison

### Stage 1: Build

Source: `templates/build/build-java.yml` with parameters:
- `jdkVersion: '17'`
- `mavenGoal: 'package'` (maps to `mavenGoals` in current template)
- `mavenOptions: '-B -DskipTests=false'` (default)
- `runTests: true` (default)
- `publishArtifacts: true` (default)
- `artifactName: 'portfolio-api-dist'`

```
ADO Template Step                          GH Actions Step
========================================   ========================================

1. (implicit) Checkout                     1. actions/checkout@v4
   ----------------------------------------   ----------------------------------------
   VERDICT: EQUIVALENT
   ADO checks out automatically in build
   jobs. GH Actions requires explicit
   checkout step.

2. JavaToolInstaller@0                     2. actions/setup-java@v4
   inputs:                                    with:
     versionSpec: 17                            distribution: temurin
     jdkArchitectureOption: x64                 java-version: 17
     jdkSourceOption: PreInstalled
   ----------------------------------------   ----------------------------------------
   VERDICT: EQUIVALENT
   Both install JDK 17 for x64. GH Actions
   uses Temurin (Adoptium) distribution as
   the standard open-source JDK provider.

3. Maven@4                                 3. mvn package -B -DskipTests=false
   inputs:                                    -f pom.xml
     mavenPomFile: pom.xml
     goals: package
     options: -B -DskipTests=false
     publishJUnitResults: true
     testResultsFiles:
       **/surefire-reports/TEST-*.xml
   ----------------------------------------   ----------------------------------------
   VERDICT: EQUIVALENT
   Same goal (package), same options (-B,
   -DskipTests=false), same POM file. Both
   run tests as part of the Maven lifecycle.
   Note: ADO's publishJUnitResults auto-
   publishes test results; GH Actions does
   not have this built-in (see Known
   Differences section).

4. cp target/*.jar|*.war to staging        4. cp target/*.jar|*.war to staging
   $(Build.ArtifactStagingDirectory)          ${{ runner.temp }}/staging
   [publishArtifacts=true, so included]
   ----------------------------------------   ----------------------------------------
   VERDICT: EQUIVALENT
   Same copy commands with same error
   suppression (2>/dev/null || true).
   Directory path mapped to GH equivalent.

5. PublishBuildArtifacts@1                 5. actions/upload-artifact@v4
   inputs:                                    with:
     pathToPublish:                             name: portfolio-api-dist
       $(Build.ArtifactStagingDirectory)        path: $RUNNER_TEMP/staging
     artifactName:
       portfolio-api-dist
   ----------------------------------------   ----------------------------------------
   VERDICT: EQUIVALENT
   Same artifact name. Path mapped to GH
   equivalent. upload-artifact@v4 is the
   standard GH replacement for
   PublishBuildArtifacts@1.

6. publish_artifact.py                     6. publish_artifact.py
   --name portfolio-api-dist                  --name portfolio-api-dist
   --registry Artifactory                     --registry Artifactory
   --build-id $(Build.BuildId)                --build-id ${{ github.run_id }}
                                              env:
   (reads from ADO env vars:                    BUILD_SOURCEBRANCH: github.ref
     BUILD_SOURCEBRANCH                         BUILD_SOURCEVERSION: github.sha
     BUILD_SOURCEVERSION                        BUILD_ARTIFACTSTAGINGDIRECTORY:
     BUILD_ARTIFACTSTAGINGDIRECTORY               $RUNNER_TEMP/staging
     AGENT_NAME)                                AGENT_NAME: github-actions
   ----------------------------------------   ----------------------------------------
   VERDICT: EQUIVALENT
   Same script, same CLI args. ADO env vars
   explicitly mapped via env: block so the
   script produces correct metadata.
```

### Stage 2: Release to Staging

Source: `templates/release/release-standard.yml` with parameters:
- `environment: 'staging'`
- `artifactName: 'portfolio-api-dist'`
- `deployStrategy: 'rolling'` (default)
- `requireApproval: false` (default)
- `notifyReleaseOrchestrator: true` (default)

```
ADO Template Step                          GH Actions Step
========================================   ========================================

0. Stage dependency & condition            0. Job dependency & condition
   dependsOn: Build                           needs: build
   requireApproval: false                     if: github.ref ==
   (no condition applied since                  'refs/heads/main'
    requireApproval is false)                   && github.event_name == 'push'
   ----------------------------------------   ----------------------------------------
   VERDICT: EQUIVALENT + IMPROVED
   ADO has no branch condition when
   requireApproval is false. GH Actions
   version restricts to main branch pushes
   to prevent deploy on PR events (since
   we added a pull_request trigger).

1. download: current                       1. actions/download-artifact@v4
   artifact: portfolio-api-dist               with:
                                                name: portfolio-api-dist
                                                path: $RUNNER_TEMP/deploy
   ----------------------------------------   ----------------------------------------
   VERDICT: EQUIVALENT
   Same artifact name. download-artifact@v4
   is the GH replacement for ADO's
   `download: current`.

2. echo "Deploying ... to staging"         2. echo "Deploying ... to staging"
   echo "Strategy: rolling"                   echo "Strategy: rolling"
   ----------------------------------------   ----------------------------------------
   VERDICT: IDENTICAL

3. notify_release_orchestrator.py          3. notify_release_orchestrator.py
   [notifyReleaseOrchestrator=true]           --service portfolio-api-dist
   --service portfolio-api-dist               --env staging
   --env staging                              --build-id ${{ github.run_id }}
   --build-id $(Build.BuildId)                --status success
   --status success                           env:
                                                BUILD_REQUESTEDFOR: github.actor
   (reads from ADO env vars:                    PIPELINE_URL: (correct GH URL)
     SYSTEM_TEAMFOUNDATIONCOLLECTIONURI
     SYSTEM_TEAMPROJECT
     BUILD_REQUESTEDFOR)
   ----------------------------------------   ----------------------------------------
   VERDICT: EQUIVALENT + IMPROVED
   Same script, same CLI args. Pipeline URL
   is now correct (GH Actions URL) via the
   PIPELINE_URL env var override instead of
   the broken ADO-format URL concatenation.

4. generate_attestation.py                 4. generate_attestation.py
   --artifact portfolio-api-dist              --artifact portfolio-api-dist
   --env staging                              --env staging
   --build-id $(Build.BuildId)                --build-id ${{ github.run_id }}
                                              env:
   (reads from ADO env vars:                    BUILD_SOURCEBRANCH: github.ref
     BUILD_SOURCEBRANCH                         BUILD_SOURCEVERSION: github.sha
     BUILD_SOURCEVERSION                        BUILD_DEFINITIONNAME:
     BUILD_DEFINITIONNAME                         portfolio-api CI
     AGENT_OS                                   BUILD_ARTIFACTSTAGINGDIRECTORY:
     BUILD_ARTIFACTSTAGINGDIRECTORY)              $RUNNER_TEMP/deploy
                                                AGENT_OS: Linux
   ----------------------------------------   ----------------------------------------
   VERDICT: EQUIVALENT
   Same script, same CLI args. All env vars
   mapped. Attestation metadata will contain
   correct values.

5. environment: staging                    5. environment: staging
   (ADO Environment with                     (GitHub Environment with
    optional approval gates)                  optional protection rules)
   ----------------------------------------   ----------------------------------------
   VERDICT: EQUIVALENT
   Both use platform-native environment
   concepts for deployment tracking and
   optional approval gates. Configuration
   is done in the platform UI, not YAML.
```

---

## Summary Scorecard

```
+----------------------------+----------+----------+-----------+
| Category                   | ADO Steps| GH Steps | Status    |
+----------------------------+----------+----------+-----------+
| Build: Checkout            |    0*    |    1     | ADDED     |
| Build: JDK setup           |    1     |    1     | MATCH     |
| Build: Maven package       |    1     |    1     | MATCH     |
| Build: Stage artifacts     |    1     |    1     | MATCH     |
| Build: Upload artifacts    |    1     |    1     | MATCH     |
| Build: Register artifact   |    1     |    1     | MATCH     |
| Release: Branch gate       |    0*    |    1     | ADDED     |
| Release: Download artifact |    1     |    1     | MATCH     |
| Release: Checkout          |    0*    |    1     | ADDED     |
| Release: Execute deploy    |    1     |    1     | MATCH     |
| Release: Notify D2         |    1     |    1     | MATCH     |
| Release: Attestation       |    1     |    1     | MATCH     |
| Release: Environment       |    1     |    1     | MATCH     |
+----------------------------+----------+----------+-----------+
| TOTAL                      |   10     |   13     |           |
| Matched                    |          |          | 8         |
| Added (required by GH)     |          |          | 3         |
| Added (best practice)      |          |          | 2         |
| Removed                    |          |          | 0         |
+----------------------------+----------+----------+-----------+

*  ADO performs checkout implicitly; GH Actions requires explicit checkout.
*  ADO requireApproval=false has no branch condition; GH Actions adds
   one to prevent deploy on PR events.
```

### Added Steps (Justification)

| # | Step | Reason |
|---|------|--------|
| 1 | `actions/checkout@v4` (build job) | GH Actions requires explicit checkout; ADO does this implicitly |
| 2 | `actions/checkout@v4` (deploy job) | Needed to access `build-tools/` scripts in the deploy job |
| 3 | `mkdir -p staging` | GH Actions needs the staging directory created before `cp` |
| 4 | Branch condition on deploy job | Prevents deploy on `pull_request` events (since PR trigger was added) |
| 5 | `pull_request` trigger | Standard GH Actions practice for CI validation on PRs |

---

## Known Differences (Intentional)

| # | Difference | Reason |
|---|-----------|--------|
| 1 | `pull_request` trigger added | Enables CI validation on PRs (standard GH Actions practice) |
| 2 | `master` branch kept in push triggers | Matches ADO pipeline; both `main` and `master` are triggered |
| 3 | `PIPELINE_URL` env var used | Provides correct GH Actions run URL instead of broken ADO-format URL concatenation |
| 4 | `$(Build.BuildId)` → `github.run_id` | Different ID systems; both are unique per-run identifiers |
| 5 | Explicit `actions/checkout` steps | ADO implicit checkout vs GH Actions explicit requirement |
| 6 | Deploy restricted to `main` branch only | Prevents accidental deploy from `master` push; `master` is legacy |
| 7 | Maven `publishJUnitResults` not replicated | ADO Maven@4 auto-publishes JUnit results; no direct GH equivalent (see Open Items) |
| 8 | `actions/setup-java` uses Temurin distribution | ADO uses `PreInstalled`; GH Actions Temurin is the standard open-source equivalent |

---

## ADO Environment Variable Mapping for build-tools Scripts

### publish_artifact.py

| ADO Variable | GH Actions Equivalent | Script Usage |
|---|---|---|
| `BUILD_SOURCEBRANCH` | `${{ github.ref }}` | Records source branch in artifact manifest |
| `BUILD_SOURCEVERSION` | `${{ github.sha }}` | Records commit SHA in artifact manifest |
| `BUILD_ARTIFACTSTAGINGDIRECTORY` | `${{ runner.temp }}/staging` | Output path for manifest JSON |
| `AGENT_NAME` | `github-actions` (literal) | Records agent identity in manifest |

### notify_release_orchestrator.py

| ADO Variable | GH Actions Equivalent | Script Usage |
|---|---|---|
| `SYSTEM_TEAMFOUNDATIONCOLLECTIONURI` | *(not mapped — see PIPELINE_URL)* | Constructs pipeline URL |
| `SYSTEM_TEAMPROJECT` | *(not mapped — see PIPELINE_URL)* | Constructs pipeline URL |
| `BUILD_REQUESTEDFOR` | `${{ github.actor }}` | Records who triggered the build |
| `PIPELINE_URL` (override) | `${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}` | Direct URL to GH Actions run |

### generate_attestation.py

| ADO Variable | GH Actions Equivalent | Script Usage |
|---|---|---|
| `BUILD_SOURCEBRANCH` | `${{ github.ref }}` | Records source branch in attestation |
| `BUILD_SOURCEVERSION` | `${{ github.sha }}` | Records commit SHA in attestation |
| `BUILD_DEFINITIONNAME` | `portfolio-api CI` (literal) | Records pipeline name in attestation |
| `AGENT_OS` | `Linux` (literal) | Records agent OS in attestation |
| `BUILD_ARTIFACTSTAGINGDIRECTORY` | `${{ runner.temp }}/deploy` | Output path for attestation JSON |

---

## Open Items for Runtime Validation

These cannot be verified structurally and require running both pipelines:

- [ ] Maven build output matches (JAR/WAR files produced identically)
- [ ] Published artifact contents match (file count, sizes, checksums)
- [ ] JUnit test results: ADO Maven@4 `publishJUnitResults` auto-publishes surefire reports; GH Actions workflow does not replicate this — consider adding `dorny/test-reporter@v1` if test result visibility in PRs is required
- [ ] Compliance attestation JSON schema matches (schema version 2.1)
- [ ] Artifact registry manifest fields match (source_branch, source_commit, agent_name)
- [ ] D2 notification payload contains correct pipeline URL
- [ ] Glob patterns in `cp target/*.jar` resolve identically on GH-hosted runners
