# Pricing-Engine Migration Verification

## Pipeline Architecture Comparison

```
ADO Pipeline (azure-pipelines.yml)          GitHub Actions (pricing-engine-ci.yml)
==========================================  ==========================================

  azure-pipelines.yml                         .github/workflows/pricing-engine-ci.yml
  |                                           |
  +-- resources:                              +-- (no external repo needed --
  |     repository: templates                 |    templates inlined directly)
  |     ref: main                             |
  |                                           |
  +-- Stage: Build                            +-- Job: build
  |   +-- build-dotnet.yml@templates --.      |   +-- actions/checkout@v4
  |       |                            |      |   +-- actions/setup-dotnet@v4
  |       |  (template expansion)      |      |   +-- dotnet restore
  |       v                            |      |   +-- dotnet build
  |   +-- UseDotNet@2          --------+----> |   +-- dotnet test
  |   +-- NuGetToolInstaller@1 --------+----> |   +-- dotnet publish
  |   +-- NuGetCommand@2       --------+----> |   +-- actions/upload-artifact@v4
  |   +-- DotNetCoreCLI@2 build -------+----> |   +-- publish_artifact.py
  |   +-- DotNetCoreCLI@2 test  -------+----> |
  |   +-- DotNetCoreCLI@2 publish -----+----> |
  |   +-- PublishBuildArtifacts@1 -----+----> |
  |   +-- publish_artifact.py   -------+----> |
  |                                           |
  +-- Stage: Test                             +-- Job: test (needs: build)
  |   +-- run-tests.yml@templates --.         |   +-- actions/checkout@v4
  |       |                         |         |   +-- actions/setup-dotnet@v4
  |       |  (template expansion)   |         |   +-- mkdir test-results
  |       v                         |         |   +-- dotnet test (junit)
  |   +-- mkdir test-results -------+-------> |   +-- dorny/test-reporter@v1
  |   +-- (generic: no runner) -----+-------> |   +-- normalize_test_results.py
  |   +-- PublishTestResults@2 -----+-------> |
  |   +-- normalize_test_results.py +-------> |
  |                                           |
  +-- Stage: Deploy_Dev                       +-- Job: deploy-dev (needs: test)
      condition: main branch only                 if: main branch + push only
      +-- release-standard.yml@templates --.      +-- actions/download-artifact@v4
          |                                |      +-- actions/checkout@v4
          |  (template expansion)          |      +-- echo "Deploying..."
          v                                |      +-- notify_release_orchestrator.py
      +-- download: current ---------------+----> +-- generate_attestation.py
      +-- echo "Deploying..." -------------+----> |
      +-- notify_release_orchestrator.py ---+----> environment: dev
      +-- generate_attestation.py ----------+---->
      environment: dev
```

---

## Step-by-Step Structural Verification

### 1. Trigger Configuration

| Aspect | ADO Pipeline | GH Actions | Match? |
|--------|-------------|------------|--------|
| Branch: main | `trigger.branches.include: [main]` | `on.push.branches: [main]` | YES |
| Branch: release/* | `trigger.branches.include: [release/*]` | `on.push.branches: ['release/*']` | YES |
| Path filter | `paths.include: [services/pricing-engine/**]` | `paths: ['services/pricing-engine/**']` | YES |
| PR trigger | (not configured) | `on.pull_request` added | ADDED |

> **Note**: `pull_request` trigger was intentionally added for GH Actions CI validation on PRs. ADO didn't have this. This is additive, not a behavioral change to the build/deploy logic.

### 2. Variables

| ADO Variable | ADO Value | GH Actions Env Var | GH Value | Match? |
|-------------|-----------|-------------------|----------|--------|
| `buildConfiguration` | `'Release'` | `BUILD_CONFIGURATION` | `Release` | YES |
| `artifactName` | `'pricing-engine-drop'` | `ARTIFACT_NAME` | `pricing-engine-drop` | YES |
| (in template param) | `'8.0.x'` | `DOTNET_VERSION` | `'8.0.x'` | YES |

### 3. Runner

| Aspect | ADO Pipeline | GH Actions | Match? |
|--------|-------------|------------|--------|
| Pool | `vmImage: 'ubuntu-latest'` | `runs-on: ubuntu-latest` | YES |

---

## Stage-by-Stage Detailed Comparison

### Stage 1: Build

Source: `templates/build/build-dotnet.yml` with parameters:
- `solution: 'services/pricing-engine/**/*.sln'`
- `buildConfiguration: 'Release'`
- `dotnetVersion: '8.0.x'`
- `artifactName: 'pricing-engine-drop'`
- `publishArtifacts: true` (default)
- `runTests: true` (default)

```
ADO Template Step                          GH Actions Step
========================================   ========================================

1. UseDotNet@2                             1. actions/setup-dotnet@v4
   inputs:                                    with:
     packageType: sdk                           dotnet-version: 8.0.x
     version: 8.0.x
   ----------------------------------------   ----------------------------------------
   VERDICT: EQUIVALENT
   UseDotNet@2 with packageType=sdk is the
   same as actions/setup-dotnet with
   dotnet-version. Both install the SDK.

2. NuGetToolInstaller@1                    2. (not needed)
   ----------------------------------------   ----------------------------------------
   VERDICT: SAFELY REMOVED
   The dotnet CLI includes built-in NuGet
   support. `dotnet restore` replaces both
   the NuGet installer and NuGetCommand@2.

3. NuGetCommand@2                          3. dotnet restore
   inputs:                                    services/pricing-engine/**/*.sln
     restoreSolution:
       services/pricing-engine/**/*.sln
   ----------------------------------------   ----------------------------------------
   VERDICT: EQUIVALENT
   Same solution glob pattern. `dotnet
   restore` is the modern equivalent of
   `nuget restore` for .NET Core projects.

4. DotNetCoreCLI@2 (build)                4. dotnet build
   inputs:                                    services/pricing-engine/**/*.sln
     command: build                           --configuration Release
     projects:                                --no-restore
       services/pricing-engine/**/*.sln
     arguments:
       --configuration Release
       --no-restore
   ----------------------------------------   ----------------------------------------
   VERDICT: EQUIVALENT
   Same project glob, same configuration,
   same --no-restore flag.

5. DotNetCoreCLI@2 (test)                 5. dotnet test
   [runTests=true, so included]               **/*Tests/*.csproj
   inputs:                                    --configuration Release
     command: test                            --collect:"XPlat Code Coverage"
     projects: **/*Tests/*.csproj             --results-directory .../test-results
     arguments:                               --logger "trx;..."
       --configuration Release
       --collect:"XPlat Code Coverage"
   ----------------------------------------   ----------------------------------------
   VERDICT: EQUIVALENT + ENHANCED
   Same test glob, same config, same
   coverage collection. GH version adds
   --results-directory and --logger for
   explicit result output (needed since GH
   doesn't have ADO's auto test publishing).

6. DotNetCoreCLI@2 (publish)              6. for proj in **/*.csproj;
   [publishArtifacts=true, so included]       grep 'Microsoft.NET.Sdk.Web';
   inputs:                                    dotnet publish "$proj"
     command: publish                           --configuration Release
     publishWebProjects: true                   --output $RUNNER_TEMP/staging
     arguments:
       --configuration Release
       --output $(Build.ArtifactStagingDir)
   ----------------------------------------   ----------------------------------------
   VERDICT: EQUIVALENT
   ADO's publishWebProjects: true only
   publishes projects using the Web SDK.
   GH version replicates this by scanning
   .csproj files for Microsoft.NET.Sdk.Web
   and publishing only those. Same config,
   same output directory mapping.

7. PublishBuildArtifacts@1                 7. actions/upload-artifact@v4
   inputs:                                    with:
     pathToPublish:                             name: pricing-engine-drop
       $(Build.ArtifactStagingDirectory)        path: $RUNNER_TEMP/staging
     artifactName:
       pricing-engine-drop
   ----------------------------------------   ----------------------------------------
   VERDICT: EQUIVALENT
   Same artifact name. Path mapped to GH
   equivalent. upload-artifact@v4 is the
   standard GH replacement for
   PublishBuildArtifacts@1.

8. publish_artifact.py                     8. publish_artifact.py
   --name pricing-engine-drop                 --name pricing-engine-drop
   --registry artifact-registry               --registry artifact-registry
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

### Stage 2: Test

Source: `templates/test/run-tests.yml` with parameters:
- `testFramework: 'generic'`
- `testResultsDir: '$(Build.ArtifactStagingDirectory)/test-results'` (default)
- `publishResults: true` (default)
- `failOnTestFailure: true` (default)

```
ADO Template Step                          GH Actions Step
========================================   ========================================

1. mkdir -p $testResultsDir                1. mkdir -p $RUNNER_TEMP/test-results
   ----------------------------------------   ----------------------------------------
   VERDICT: EQUIVALENT
   Same command. Directory path mapped.

2. (testFramework='generic' -> no runner)  2. dotnet test (with junit logger)
   ----------------------------------------   ----------------------------------------
   VERDICT: ENHANCED
   ADO's 'generic' framework doesn't run
   any test command (it relies on the build
   template having already run tests). The
   GH version explicitly runs dotnet test
   here to produce JUnit XML output for
   the test reporter. This ensures test
   results are available for publishing
   even as a separate job.

3. PublishTestResults@2                    3. dorny/test-reporter@v1
   inputs:                                    with:
     testResultsFormat: JUnit                   reporter: java-junit
     testResultsFiles: .../**/*.xml             path: .../**/*.xml
     failTaskOnFailedTests: true                fail-on-error: true
   condition: always()                        if: always()
   ----------------------------------------   ----------------------------------------
   VERDICT: EQUIVALENT
   Same format (JUnit), same glob for XML
   files, same fail-on-error behavior, same
   always() condition. dorny/test-reporter
   is the standard GH replacement for
   PublishTestResults@2.

4. normalize_test_results.py               4. normalize_test_results.py
   --input-dir $testResultsDir                --input-dir $RUNNER_TEMP/test-results
   --output .../normalized-results.json       --output .../normalized-results.json
   condition: always()                        if: always()
   ----------------------------------------   ----------------------------------------
   VERDICT: EQUIVALENT
   Same script, same args, same always()
   condition. Directory paths mapped.
```

### Stage 3: Deploy to Dev

Source: `templates/release/release-standard.yml` with parameters:
- `environment: 'dev'`
- `artifactName: 'pricing-engine-drop'`
- `deployStrategy: 'rolling'` (default)
- `requireApproval: false` (default)
- `notifyReleaseOrchestrator: true` (default)

```
ADO Template Step                          GH Actions Step
========================================   ========================================

0. Stage condition (from pipeline):        0. Job condition:
   and(succeeded(),                           if: github.ref ==
     eq(variables['Build.SourceBranch'],         'refs/heads/main'
       'refs/heads/main'))                      && github.event_name == 'push'
   ----------------------------------------   ----------------------------------------
   VERDICT: EQUIVALENT
   Both restrict deployment to main branch.
   GH version also checks event_name=push
   to exclude PR events (since we added a
   pull_request trigger).

1. download: current                       1. actions/download-artifact@v4
   artifact: pricing-engine-drop              with:
                                                name: pricing-engine-drop
                                                path: $RUNNER_TEMP/deploy
   ----------------------------------------   ----------------------------------------
   VERDICT: EQUIVALENT
   Same artifact name. download-artifact@v4
   is the GH replacement for ADO's
   `download: current`.

2. echo "Deploying ... to dev"             2. echo "Deploying ... to dev"
   echo "Strategy: rolling"                   echo "Strategy: rolling"
   ----------------------------------------   ----------------------------------------
   VERDICT: IDENTICAL

3. notify_release_orchestrator.py          3. notify_release_orchestrator.py
   [notifyReleaseOrchestrator=true]           --service pricing-engine-drop
   --service pricing-engine-drop              --env dev
   --env dev                                  --build-id ${{ github.run_id }}
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
   is now correct (GH Actions URL) instead
   of broken ADO-format URL. Script updated
   to check PIPELINE_URL first (backward-
   compatible with ADO).

4. generate_attestation.py                 4. generate_attestation.py
   --artifact pricing-engine-drop             --artifact pricing-engine-drop
   --env dev                                  --env dev
   --build-id $(Build.BuildId)                --build-id ${{ github.run_id }}
                                              env:
   (reads from ADO env vars:                    BUILD_SOURCEBRANCH: github.ref
     BUILD_SOURCEBRANCH                         BUILD_SOURCEVERSION: github.sha
     BUILD_SOURCEVERSION                        BUILD_DEFINITIONNAME:
     BUILD_DEFINITIONNAME                         pricing-engine CI
     AGENT_OS                                   BUILD_ARTIFACTSTAGINGDIRECTORY:
     BUILD_ARTIFACTSTAGINGDIRECTORY)              $RUNNER_TEMP/deploy
                                                AGENT_OS: Linux
   ----------------------------------------   ----------------------------------------
   VERDICT: EQUIVALENT
   Same script, same CLI args. All env vars
   mapped. Attestation metadata will contain
   correct values.

5. environment: dev                        5. environment: dev
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
| Build: SDK setup           |    1     |    1     | MATCH     |
| Build: NuGet install       |    1     |    0     | REMOVED   |
| Build: NuGet restore       |    1     |    1     | MATCH     |
| Build: Compile             |    1     |    1     | MATCH     |
| Build: Unit tests          |    1     |    1     | MATCH     |
| Build: Publish             |    1     |    1     | MATCH     |
| Build: Upload artifacts    |    1     |    1     | MATCH     |
| Build: Register artifact   |    1     |    1     | MATCH     |
| Test: mkdir                |    1     |    1     | MATCH     |
| Test: Run tests            |    0     |    1     | ADDED     |
| Test: Publish results      |    1     |    1     | MATCH     |
| Test: Normalize results    |    1     |    1     | MATCH     |
| Deploy: Branch gate        |    1     |    1     | MATCH     |
| Deploy: Download artifact  |    1     |    1     | MATCH     |
| Deploy: Execute            |    1     |    1     | MATCH     |
| Deploy: Notify orchestrator|    1     |    1     | MATCH     |
| Deploy: Attestation        |    1     |    1     | MATCH     |
| Deploy: Environment        |    1     |    1     | MATCH     |
+----------------------------+----------+----------+-----------+
| TOTAL                      |   17     |   17     |           |
| Matched                    |          |          | 15        |
| Safely removed             |          |          | 1         |
| Added (enhancement)        |          |          | 1         |
+----------------------------+----------+----------+-----------+
```

### Removed: NuGetToolInstaller@1
The `dotnet` CLI includes built-in NuGet support. `dotnet restore` handles
package restoration without a separate NuGet binary. This is standard
practice for .NET Core / .NET 5+ projects.

### Added: Explicit test runner in Test job
ADO's `testFramework: 'generic'` doesn't execute any test command (relies
on the build stage). The GH Actions test job explicitly runs `dotnet test`
to produce JUnit XML for the test reporter, since GH Actions jobs are
independent and don't share state.

---

## Known Differences (Intentional)

| # | Difference | Reason |
|---|-----------|--------|
| 1 | `pull_request` trigger added | Enables CI validation on PRs (best practice for GH Actions) |
| 2 | `NuGetToolInstaller@1` removed | Redundant with `dotnet restore` for .NET Core |
| 3 | Test job runs tests explicitly | GH Actions jobs are isolated; can't rely on build job state |
| 4 | `PIPELINE_URL` env var (new) | Produces correct GH Actions URL instead of broken ADO URL |
| 5 | `$(Build.BuildId)` -> `github.run_id` | Different ID systems; both are unique per-run identifiers |
| 6 | `shopt -s globstar` added to all run steps | GH Actions bash doesn't enable globstar by default; ADO tasks use minimatch |
| 7 | Web project filtering via grep | Replicates ADO's `publishWebProjects: true` without the DotNetCoreCLI task |

## Open Items for Runtime Validation

These cannot be verified structurally and require running both pipelines:

- [ ] Glob patterns resolve identically (`shopt -s globstar` is set)
- [ ] Published artifact contents match (file count, sizes, checksums)
- [ ] Test result counts match (pass/fail/skip)
- [ ] Compliance attestation JSON schema matches
- [ ] Artifact registry manifest fields match
