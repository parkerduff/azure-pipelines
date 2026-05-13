# portfolio-api-ci — ADO → GitHub Actions Migration Mapping

**Pipeline:** portfolio-api-ci  
**ADO ID:** 102  
**Category:** 1 (Central Template Consumer)  
**Stack:** Java 17 / Maven  
**ADO YAML:** `services/portfolio-api/azure-pipelines.yml`  
**GHA Workflow:** `.github/workflows/portfolio-api-ci.yml`  
**Template branch:** `master` (legacy — not `main`)  

---

## Trigger Mapping

| Aspect | ADO | GHA | Notes |
|---|---|---|---|
| Push branches | `main`, `master` | `main`, `master` | Identical |
| Push paths | `services/portfolio-api/**` | `services/portfolio-api/**` | Identical |
| PR trigger | _(none)_ | `pull_request` on `main` | **Added** — provides earlier CI feedback on PRs |

---

## Stage → Job Mapping

| ADO Stage | GHA Job | Dependencies | Runner |
|---|---|---|---|
| `Build` (displayName: "Build portfolio-api") | `build` | — | `ubuntu-latest` |
| `Deploy_staging` (from `release-standard.yml`) | `deploy-staging` | `needs: build` | `ubuntu-latest` |

---

## Step-by-Step Task Mapping

### Build Job

| # | ADO Task | GHA Step | Details |
|---|---|---|---|
| 1 | _(implicit)_ | `actions/checkout@v4` | Source checkout |
| 2 | `JavaToolInstaller@0` | `actions/setup-java@v4` | `java-version: 17`, `distribution: temurin` (ADO used `PreInstalled`; GHA installs Temurin) |
| 3 | `Maven@4` (goal: `package`) | `mvn -B -DskipTests=false package` | Direct CLI invocation; ADO task wrapper not needed |
| 4 | `Maven@4` (`publishJUnitResults: true`) | `actions/upload-artifact@v4` (test-results) | GHA has no native test-results tab; results uploaded as artifact. `if: always()` ensures upload on test failure. |
| 5 | Script: stage artifacts | `cp target/*.jar|*.war` → `runner.temp/staging` | `mkdir -p` added for fresh runner safety |
| 6 | `PublishBuildArtifacts@1` | `actions/upload-artifact@v4` | Artifact name: `portfolio-api-dist` |
| 7 | Script: `publish_artifact.py` | Same script, with env shims | Guarded with `if: github.event_name == 'push'` to prevent PR artifact registration |

### Deploy-Staging Job

| # | ADO Task | GHA Step | Details |
|---|---|---|---|
| 1 | _(implicit)_ | `actions/checkout@v4` | Needed for helper scripts in `build-tools/scripts/` |
| 2 | `download: current` artifact | `actions/download-artifact@v4` | Downloads `portfolio-api-dist` to `runner.temp/staging` |
| 3 | Script: execute deployment | `echo` deployment info | Placeholder — same as ADO |
| 4 | Script: `notify_release_orchestrator.py` | Same script, with env shims + `PIPELINE_URL` | Script updated to prefer `PIPELINE_URL` over ADO-format URL construction |
| 5 | Script: `generate_attestation.py` | Same script, with env shims | `mkdir -p` added for staging dir on fresh runner |

---

## Variable Mapping

| ADO Variable / Expression | GHA Equivalent | Used By |
|---|---|---|
| `$(artifactName)` / `portfolio-api-dist` | `${{ env.ARTIFACT_NAME }}` | All jobs |
| `$(Build.SourceBranch)` | `${{ github.ref }}` | `publish_artifact.py`, `generate_attestation.py` |
| `$(Build.SourceVersion)` | `${{ github.sha }}` | `publish_artifact.py`, `generate_attestation.py` |
| `$(Build.BuildId)` | `${{ github.run_id }}` | All helper scripts |
| `$(Build.ArtifactStagingDirectory)` | `${{ runner.temp }}/staging` | `publish_artifact.py`, `generate_attestation.py` |
| `$(Agent.Name)` | `${{ runner.name }}` | `publish_artifact.py` |
| `$(Agent.OS)` | `${{ runner.os }}` | `generate_attestation.py` |
| `$(Build.RequestedFor)` | `${{ github.actor }}` | `notify_release_orchestrator.py` |
| `$(Build.DefinitionName)` | `${{ github.workflow }}` | `generate_attestation.py` |
| `$(System.TeamFoundationCollectionUri)` | `${{ github.server_url }}/` | `notify_release_orchestrator.py` |
| `$(System.TeamProject)` | `${{ github.repository }}` | `notify_release_orchestrator.py` |
| Pipeline URL (ADO format) | `${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}` | `notify_release_orchestrator.py` via `PIPELINE_URL` |

---

## Condition Mapping

| ADO Condition | GHA `if:` | Context |
|---|---|---|
| `dependsOn: Build` | `needs: build` | Deploy-staging depends on build |
| _(ADO: `requireApproval: false`)_ | GHA `environment: staging` | Environment protection rules can be configured in repo settings |
| _(none — runs on all triggers)_ | `if: github.event_name == 'push'` | **Added** — guards artifact registration to prevent PR builds from registering |

---

## Integration Points

| Integration | ADO Behavior | GHA Behavior |
|---|---|---|
| **Artifact Registry** | `publish_artifact.py` called unconditionally | Guarded with `if: github.event_name == 'push'` — PR builds skip registration |
| **D2 (release orchestrator)** | `notify_release_orchestrator.py` with ADO-format URL | Same script; `PIPELINE_URL` env var provides GHA-format URL; fallback to ADO format preserved |
| **Compliance Attestation** | `generate_attestation.py` in deploy stage | Same script with env shims; `mkdir -p` ensures staging dir exists on fresh runner |

---

## Helper Script Changes

### `build-tools/scripts/notify_release_orchestrator.py`

**Change:** Pipeline URL construction now prefers the `PIPELINE_URL` environment variable when set, falling back to ADO-format URL construction (`SYSTEM_TEAMFOUNDATIONCOLLECTIONURI + SYSTEM_TEAMPROJECT + /_build/results?buildId=`) when `PIPELINE_URL` is not set.

**Backward compatibility:** Fully backward compatible. ADO pipelines do not set `PIPELINE_URL`, so the fallback path executes unchanged.

### `build-tools/scripts/publish_artifact.py`

**No changes required.** All ADO env vars (`BUILD_SOURCEBRANCH`, `BUILD_SOURCEVERSION`, `AGENT_NAME`, `BUILD_ARTIFACTSTAGINGDIRECTORY`) are shimmed via `env:` blocks in the GHA workflow.

### `build-tools/scripts/generate_attestation.py`

**No changes required.** All ADO env vars (`BUILD_SOURCEBRANCH`, `BUILD_SOURCEVERSION`, `BUILD_DEFINITIONNAME`, `AGENT_OS`, `BUILD_ARTIFACTSTAGINGDIRECTORY`) are shimmed via `env:` blocks in the GHA workflow.

---

## Known Gaps & Behavioral Differences

| Gap | Description | Severity |
|---|---|---|
| **Test result viewer** | ADO `PublishTestResults@2` shows results in a native test tab. GHA has no equivalent — test results are uploaded as artifacts. Consider adding `dorny/test-reporter@v1` for richer reporting. | Low |
| **JDK source** | ADO uses `jdkSourceOption: PreInstalled` (agent-provided JDK). GHA installs Temurin via `actions/setup-java@v4`. Functionally equivalent but different JDK distribution. | Low |
| **Branch glob scope** | ADO `services/portfolio-api/**` and GHA `services/portfolio-api/**` behave identically for path triggers. No change needed. | None |
| **Environment approvals** | ADO `environment: staging` gates are configured in ADO. GHA `environment: staging` protection rules must be configured separately in GitHub repository settings. | Medium — requires manual configuration |
| **Maven POM path** | ADO template hardcodes `mavenPomFile: 'pom.xml'` (repo root). GHA uses the same default. If the POM is at `services/portfolio-api/pom.xml`, a `working-directory` may be needed. | Low — verify POM location |

---

## Secrets Required

The following secrets must be configured in GitHub repository settings for full functionality:

| Secret | Purpose | Notes |
|---|---|---|
| _(none currently)_ | — | Helper scripts do not use explicit secrets; they rely on env vars shimmed from GHA context. If artifact-registry or D2 require API keys in production, add them as repository secrets. |

---

## ADO Templates Inlined

| Template Path (from `master` branch) | Inlined Into |
|---|---|
| `templates/build/build-java.yml` | `build` job steps |
| `templates/release/release-standard.yml` | `deploy-staging` job |
