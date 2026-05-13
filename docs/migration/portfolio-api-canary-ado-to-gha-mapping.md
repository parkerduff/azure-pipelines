# portfolio-api-canary — ADO-to-GHA Migration Mapping

**Pipeline:** portfolio-api-canary  
**ADO ID:** 103  
**Category:** 1 (Central Template Consumer)  
**Stack:** Java 17 / Maven  
**Owner:** team-quant  
**Source YAML:** `services/portfolio-api/azure-pipelines-canary.yml`  
**GHA Workflow:** `.github/workflows/portfolio-api-canary.yml`

---

## 1. Trigger Mapping

| ADO | GHA | Notes |
|-----|-----|-------|
| `trigger: none` (manual only, with `templateBranch` parameter) | `on.workflow_dispatch` with `templateBranch` choice input | Preserves manual-only semantics. The `templateBranch` parameter maps to a GHA choice input with the same 4 values. |
| *(no PR trigger)* | `on.pull_request` on `main` for `services/portfolio-api/**` paths | **Intentional addition** — provides CI feedback on PRs touching the portfolio-api service or its templates. Build-only (deploy is skipped on PRs). |
| *(no environment param)* | `on.workflow_dispatch.inputs.environment` choice (dev/staging/prod) | **Intentional addition** — ADO environment was likely selected via release template parameters or manual override. Making it an explicit input improves visibility. |

---

## 2. Stage / Job Mapping

| ADO Stage | GHA Job | Dependencies | Condition |
|-----------|---------|-------------|-----------|
| `Build` (display: "Build portfolio-api (canary — \<branch\>)") | `build` | — | Always runs |
| *(release-standard.yml consumption — implicit in ADO)* | `deploy` | `needs: build` | `github.event_name == 'workflow_dispatch'` (skipped on PRs) |

### ADO Multi-Branch Template Selection → GHA Conditionals

The ADO pipeline used a parameter to select which repository's template to consume:
```yaml
# ADO: 4 separate resource repositories, each pointing to a different branch
resources:
  repositories:
    - repository: templates_main       # ref: main
    - repository: templates_master     # ref: master
    - repository: templates_preprod    # ref: staging/preprod
    - repository: templates_hardened   # ref: staging/release-hardening
```

In GHA, templates are inlined. Branch-specific differences are handled with `if:` conditionals on the `templateBranch` input:

| Template Branch | build-java.yml Differences | release-standard.yml Differences |
|----------------|---------------------------|--------------------------------|
| `main` | `mavenGoals: 'clean package'`, registry: `Artifactory` | Standard (requireApproval=false, no health checks) |
| `master` | `mavenGoal: 'package'`, registry: `artifact-registry` | Standard (same as main) |
| `staging/preprod` | Same as master | Standard (same as main) |
| `staging/release-hardening` | Same as master | **Enhanced:** requireApproval=true, pre-deploy validation via `compare_build_outputs.py`, retrying health checks (5 attempts, 15s interval) |

---

## 3. Task Mapping — Build Job

| # | ADO Task / Step | GHA Step | Input Translation |
|---|----------------|----------|-------------------|
| 1 | `JavaToolInstaller@0` (jdkVersion: 17, PreInstalled) | `actions/setup-java@v4` (distribution: temurin, java-version: 17) | ADO `jdkSourceOption: PreInstalled` → GHA downloads if needed |
| 2 | `Maven@4` (goals vary by branch, options: `-B -DskipTests=false`) | `run: mvn ...` with branch-conditional goals | main: `clean package`; others: `package`. Uses `find` to locate `pom.xml` (no glob patterns). |
| 3 | *(Maven@4 publishJUnitResults)* | `actions/upload-artifact@v4` (test-results) | ADO natively publishes to Test tab; GHA uploads as artifact. `if: always()` ensures capture on test failure. |
| 4 | `script: cp target/*.jar ...` (stage artifacts) | `run: find ... -exec cp` | Replaced `cp target/*.jar $(Build.ArtifactStagingDirectory)/` with `find` to avoid glob issues. |
| 5 | `PublishBuildArtifacts@1` | `actions/upload-artifact@v4` | `pathToPublish` → `path`, `artifactName` → `name` |
| 6 | `script: python publish_artifact.py` | `run: python publish_artifact.py` | Guarded with `if: github.event_name != 'pull_request'`. Registry varies by branch (main=Artifactory, others=artifact-registry). |

---

## 4. Task Mapping — Deploy Job

| # | ADO Task / Step | GHA Step | Notes |
|---|----------------|----------|-------|
| 1 | `download: current` | `actions/download-artifact@v4` | |
| 2 | `compare_build_outputs.py` (pre-deploy validation) | `run: python compare_build_outputs.py` | **Only on staging/release-hardening** (`if: inputs.templateBranch == '...'`) |
| 3 | `script: echo "Deploying..."` | `run: echo "Deploying..."` | Placeholder deployment step |
| 4 | Health check with retries | `run: curl retry loop` | **Only on staging/release-hardening** — 5 retries, 15s interval |
| 5 | `notify_release_orchestrator.py` (D2) | `run: python notify_release_orchestrator.py` | Script updated to prefer `PIPELINE_URL` env var over ADO-style URL construction |
| 6 | `generate_attestation.py` | `run: python generate_attestation.py` | `mkdir -p` added for staging dir on fresh runner |

---

## 5. Variable Mapping

| ADO Variable | GHA Equivalent | Used By |
|-------------|---------------|---------|
| `$(Build.SourceBranch)` / `BUILD_SOURCEBRANCH` | `${{ github.ref }}` | publish_artifact.py, generate_attestation.py |
| `$(Build.SourceVersion)` / `BUILD_SOURCEVERSION` | `${{ github.sha }}` | publish_artifact.py, generate_attestation.py |
| `$(Build.BuildId)` / `BUILD_BUILDID` | `${{ github.run_id }}` | publish_artifact.py, generate_attestation.py, notify_release_orchestrator.py |
| `$(Build.ArtifactStagingDirectory)` / `BUILD_ARTIFACTSTAGINGDIRECTORY` | `${{ runner.temp }}/staging` | publish_artifact.py, generate_attestation.py, compare_build_outputs.py |
| `$(Build.SourcesDirectory)` | `${{ github.workspace }}` | Template script paths (resolved via checkout) |
| `$(Agent.Name)` / `AGENT_NAME` | `${{ runner.name }}` | publish_artifact.py |
| `$(Agent.OS)` / `AGENT_OS` | `${{ runner.os }}` | generate_attestation.py |
| `$(Build.RequestedFor)` / `BUILD_REQUESTEDFOR` | `${{ github.actor }}` | notify_release_orchestrator.py |
| `$(Build.DefinitionName)` / `BUILD_DEFINITIONNAME` | `${{ github.workflow }}` | generate_attestation.py |
| `$(System.TeamFoundationCollectionUri)` | `${{ github.server_url }}/` | notify_release_orchestrator.py (shimmed) |
| `$(System.TeamProject)` | `${{ github.repository }}` | notify_release_orchestrator.py (shimmed) |
| Pipeline URL (ADO format) | `PIPELINE_URL` env var with GHA format | notify_release_orchestrator.py (updated to prefer PIPELINE_URL) |
| `$(artifactName)` (pipeline variable) | `${{ env.ARTIFACT_NAME }}` | Throughout workflow |

---

## 6. Condition Mapping

| ADO Condition | GHA `if:` Expression | Context |
|--------------|---------------------|---------|
| `${{ if eq(parameters.templateBranch, 'main') }}` | `if: github.event.inputs.templateBranch == 'main'` or shell `if` | Branch-conditional build goals and registry |
| `${{ if eq(parameters.templateBranch, 'staging/release-hardening') }}` | `if: github.event.inputs.templateBranch == 'staging/release-hardening'` | Pre-deploy validation and health checks |
| *(release-standard.yml requireApproval condition)* | `if: github.event_name == 'workflow_dispatch'` | Deploy job only runs on manual dispatch, not on PR |
| *(ADO trigger: none — all runs are intentional)* | `if: github.event_name != 'pull_request'` | Artifact registration guarded to non-PR events |

---

## 7. Integration Points

| Integration | ADO Mechanism | GHA Mechanism |
|------------|--------------|---------------|
| **Artifactory / artifact-registry** | `publish_artifact.py` called with `--registry Artifactory` or `artifact-registry` | Same script, same args. Registry selected by branch conditional. Guarded to non-PR events. |
| **D2 (release orchestrator)** | `notify_release_orchestrator.py` with ADO env vars | Same script, env vars shimmed. Script updated to prefer `PIPELINE_URL` env var. |
| **Compliance attestation** | `generate_attestation.py` with ADO env vars | Same script, env vars shimmed. `mkdir -p` for staging dir on fresh runner. |
| **Pre-deploy validation** | `compare_build_outputs.py` (staging/release-hardening only) | Same script, only runs when `templateBranch == 'staging/release-hardening'`. |

---

## 8. Known Gaps & Behavioral Differences

| # | Gap | Details | Severity |
|---|-----|---------|----------|
| 1 | **Test results viewer** | ADO `Maven@4` with `publishJUnitResults: true` renders results in the Test tab. GHA has no native equivalent; results are uploaded as artifacts. Consider adding `dorny/test-reporter@v1` for richer reporting. | Low |
| 2 | **Branch glob broadening** | ADO pipeline had `trigger: none`. The new `pull_request` trigger uses `services/portfolio-api/**` which is recursive. This is an intentional enhancement, not a regression. | Info |
| 3 | **JDK source** | ADO used `jdkSourceOption: PreInstalled`; GHA downloads the JDK via `actions/setup-java@v4`. Functionally equivalent but JDK source differs. | Low |
| 4 | **Maven goals parameter name** | `main` branch template uses `mavenGoals` (plural); other branches use `mavenGoal` (singular). Both accept default values. In GHA, the goals are hardcoded per branch conditional. | Info |
| 5 | **Pipeline URL format** | ADO used `CollectionUri + Project + /_build/results?buildId=X`. GHA uses `server_url/repository/actions/runs/run_id`. Script updated with backward-compatible `PIPELINE_URL` support. | Resolved |
| 6 | **Staging directory on fresh runners** | Each GHA job runs on a fresh runner. Deploy job adds `mkdir -p` for `${{ runner.temp }}/staging` before scripts that write there. | Resolved |
| 7 | **Deployment environment approvals** | ADO `staging/release-hardening` branch defaults `requireApproval: true`. In GHA, configure environment protection rules in repository settings for the `dev`/`staging`/`prod` environments. | Action Required |

---

## 9. Secrets Required

Configure these in **Repository Settings → Secrets and variables → Actions**:

| Secret | Used By | Notes |
|--------|---------|-------|
| *(none currently)* | — | All helper scripts currently write local manifests. When connected to real Artifactory/D2/attestation-database APIs, secrets will be needed for those endpoints. |

**Environment protection rules** (configure in Repository Settings → Environments):

| Environment | Recommended Rules |
|------------|------------------|
| `dev` | None (auto-deploy) |
| `staging` | Required reviewers |
| `prod` | Required reviewers + wait timer |

---

## 10. Script Changes

### `build-tools/scripts/notify_release_orchestrator.py`

**Change:** Added `PIPELINE_URL` env var support with fallback to ADO-style URL construction.

**Backward compatible:** Yes — when `PIPELINE_URL` is not set (i.e., when called from ADO pipelines), the script falls back to the existing `SYSTEM_TEAMFOUNDATIONCOLLECTIONURI + SYSTEM_TEAMPROJECT + /_build/results?buildId=X` pattern.

```python
# Before:
"pipeline_url": os.environ.get("SYSTEM_TEAMFOUNDATIONCOLLECTIONURI", "")
    + os.environ.get("SYSTEM_TEAMPROJECT", "")
    + "/_build/results?buildId=" + build_id,

# After:
"pipeline_url": os.environ.get(
    "PIPELINE_URL",
    os.environ.get("SYSTEM_TEAMFOUNDATIONCOLLECTIONURI", "")
    + os.environ.get("SYSTEM_TEAMPROJECT", "")
    + "/_build/results?buildId=" + build_id,
),
```
