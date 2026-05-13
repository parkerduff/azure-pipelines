# risk-batch-ci — ADO to GHA Migration Mapping

**Pipeline:** risk-batch-ci  
**ADO ID:** 104  
**Category:** 1 (Central Template Consumer)  
**Stack:** Python 3.11  
**Source YAML:** `services/risk-batch/azure-pipelines.yml`  
**Template branch:** `staging/preprod`  
**GHA Workflow:** `.github/workflows/risk-batch-ci.yml`

---

## 1. Trigger Mapping

| Aspect | ADO | GHA | Notes |
|---|---|---|---|
| Push branches | `main` | `main` | Identical |
| Push paths | `services/risk-batch/**` | `services/risk-batch/**` | Identical |
| PR trigger | *(none)* | `pull_request` on `main` + same paths | **Intentional addition** — provides earlier CI feedback on PRs |

## 2. Stage → Job Mapping

| ADO Stage | GHA Job | Dependencies | Condition |
|---|---|---|---|
| `Build` (displayName: "Build risk-batch") | `build` | *(none)* | *(always)* |
| `Release` (displayName: "Deploy to dev", dependsOn: Build) | `deploy-dev` | `needs: build` | `github.ref == 'refs/heads/main' && github.event_name == 'push'` |

## 3. Task Mapping — Build Job

### From `templates/build/build-python.yml` (staging/preprod)

Parameters passed: `pythonVersion: '3.11'`, `requirementsFile: 'services/risk-batch/requirements.txt'`, `artifactName: 'risk-batch-dist'`

Defaults applied: `runTests: true`, `enableLinting: true`, `publishArtifacts: true`, `testRetryCount: 3`

| # | ADO Task/Step | GHA Step | Notes |
|---|---|---|---|
| 1 | `UsePythonVersion@0` (3.11) | `actions/setup-python@v5` (3.11) | |
| 2 | Script: `pip install -r requirements.txt` | `run: pip install ...` | |
| 3 | Script: `flake8 + black --check` (linting) | `run: flake8 + black --check` | |
| 4 | Script: `pytest` with retry loop (`testRetryCount: 3`, `--reruns 2`) | `run: pytest` with retry loop | **staging/preprod-specific retry logic** preserved |
| 5 | `PublishTestResults@2` (condition: always) | `actions/upload-artifact@v4` (if: always()) | GHA lacks native test results tab; uploaded as artifact |
| 6 | Script: `python setup.py sdist bdist_wheel` | `run: python setup.py sdist bdist_wheel` | |
| 7 | `PublishBuildArtifacts@1` | `actions/upload-artifact@v4` | |
| 8 | Script: `publish_artifact.py` | `run: python publish_artifact.py` | **Guarded to push-only** (`if: github.event_name == 'push'`) |
| 9 | Script: Stamp preprod validation marker | `run: echo ...` | |

### From `templates/test/run-tests.yml` (staging/preprod)

Parameters passed: `testFramework: 'pytest'`

Defaults applied: `testResultsDir: '$(Build.ArtifactStagingDirectory)/test-results'`, `publishResults: true`, `failOnTestFailure: true`

| # | ADO Task/Step | GHA Step | Notes |
|---|---|---|---|
| 1 | Script: `mkdir -p` test results dir | `run: mkdir -p ...` | |
| 2 | Script: `pytest --junitxml` | `run: pytest --junitxml ...` | |
| 3 | `PublishTestResults@2` (condition: always) | `actions/upload-artifact@v4` (if: always()) | GHA test results uploaded as artifact |
| 4 | Script: `normalize_test_results.py` (condition: always) | `run: python normalize_test_results.py` (if: always()) | |

## 4. Task Mapping — Deploy Job

### From `templates/release/release-standard.yml` (staging/preprod)

Parameters passed: `environment: 'dev'`, `artifactName: 'risk-batch-dist'`

Defaults applied: `deployStrategy: 'rolling'`, `requireApproval: false`, `notifyReleaseOrchestrator: true`

| # | ADO Task/Step | GHA Step | Notes |
|---|---|---|---|
| 1 | `download: current` artifact | `actions/download-artifact@v4` | |
| 2 | Script: echo deploy | `run: echo deploy` | |
| 3 | Script: `notify_release_orchestrator.py` | `run: python notify_release_orchestrator.py` | Uses `PIPELINE_URL` env var shim |
| 4 | Script: `generate_attestation.py` | `run: python generate_attestation.py` | Uses env var shims |

## 5. Variable Mapping

| ADO Variable | GHA Equivalent | Used By |
|---|---|---|
| `$(Build.SourceBranch)` | `${{ github.ref }}` → `BUILD_SOURCEBRANCH` env | publish_artifact.py, generate_attestation.py |
| `$(Build.SourceVersion)` | `${{ github.sha }}` → `BUILD_SOURCEVERSION` env | publish_artifact.py, generate_attestation.py |
| `$(Build.BuildId)` | `${{ github.run_id }}` → `BUILD_BUILDID` env | publish_artifact.py, CLI args |
| `$(Build.ArtifactStagingDirectory)` | `${{ runner.temp }}/staging` → `BUILD_ARTIFACTSTAGINGDIRECTORY` env | publish_artifact.py, generate_attestation.py |
| `$(Build.SourcesDirectory)` | `${{ github.workspace }}` → `BUILD_SOURCESDIRECTORY` env | Script path references |
| `$(Agent.Name)` | `${{ runner.name }}` → `AGENT_NAME` env | publish_artifact.py |
| `$(Agent.OS)` | `${{ runner.os }}` → `AGENT_OS` env | generate_attestation.py |
| `$(Build.RequestedFor)` | `${{ github.actor }}` → `BUILD_REQUESTEDFOR` env | notify_release_orchestrator.py |
| `$(Build.DefinitionName)` | `${{ github.workflow }}` → `BUILD_DEFINITIONNAME` env | generate_attestation.py |
| `$(System.TeamFoundationCollectionUri)` | `${{ github.server_url }}/` → `SYSTEM_TEAMFOUNDATIONCOLLECTIONURI` env | notify_release_orchestrator.py (URL construction) |
| `$(System.TeamProject)` | `${{ github.repository }}` → `SYSTEM_TEAMPROJECT` env | notify_release_orchestrator.py (URL construction) |
| Pipeline URL (ADO format) | `PIPELINE_URL` env with GHA format | notify_release_orchestrator.py (updated to prefer `PIPELINE_URL`) |

## 6. Condition Mapping

| ADO Condition | GHA `if:` | Context |
|---|---|---|
| `dependsOn: Build` (implicit success) | `needs: build` | Deploy depends on build success |
| ADO `deployment` + `environment: dev` | GHA `environment: dev` | Deploy to dev environment |
| `condition: always()` on PublishTestResults | `if: always()` on upload steps | Capture test results even on failure |
| Artifact registration (implicit: all triggers) | `if: github.event_name == 'push'` | **Guard added** — prevent artifact registration on PR builds |
| Deploy stage (implicit: main branch via ADO default) | `if: github.ref == 'refs/heads/main' && github.event_name == 'push'` | Only deploy on push to main |

## 7. Integration Points

| Integration | ADO Mechanism | GHA Mechanism | Notes |
|---|---|---|---|
| Artifactory | `publish_artifact.py` called unconditionally | `publish_artifact.py` guarded to `push` events only | Prevents PR builds from registering artifacts |
| D2 (release orchestrator) | `notify_release_orchestrator.py` (constructs ADO URL) | Same script with `PIPELINE_URL` env var shim | Script updated to prefer `PIPELINE_URL` if set, falling back to ADO URL construction |
| Compliance attestation | `generate_attestation.py` | Same script with env var shims | Backward compatible |
| Test result normalization | `normalize_test_results.py` | Same script | No env var dependencies |

## 8. Known Gaps & Behavioral Differences

| Gap | Description | Impact |
|---|---|---|
| Native test results tab | ADO `PublishTestResults@2` populates the Tests tab; GHA has no built-in equivalent | Test results uploaded as artifacts. Consider adding `dorny/test-reporter@v1` for richer in-PR reporting. |
| Pipeline URL format | ADO scripts construct `CollectionUri + Project + /_build/results?buildId=X`; GHA uses `server_url/repository/actions/runs/run_id` | `notify_release_orchestrator.py` updated to prefer `PIPELINE_URL` env var with fallback to ADO format |
| Branch glob scope | ADO `services/risk-batch/**` matches recursively (same in GHA) | No difference for this pipeline |
| Preprod stamp | ADO writes `preprod-stamp.txt` inside staging dir | Preserved identically in GHA |
| Test retry logic | `staging/preprod`-specific: outer retry loop (`testRetryCount: 3`) + inner `--reruns 2` | Preserved identically — this is the key differentiator from `main` branch templates |
| Duplicate test execution | ADO pipeline runs tests twice (once in `build-python.yml`, once in `run-tests.yml`) | **Pre-existing behavior preserved** — not fixed during migration |

## 9. Secrets Required

The following secrets must be configured in the GitHub repository settings for the workflow to function in a production environment:

| Secret | Used By | Purpose |
|---|---|---|
| *(none currently)* | — | Helper scripts use simulated API calls. When connecting to real Artifactory/D2/attestation-database APIs, add the relevant API keys as repository secrets. |

## 10. Helper Script Updates

| Script | Change | Backward Compatible? |
|---|---|---|
| `notify_release_orchestrator.py` | Added `PIPELINE_URL` env var support with fallback to ADO URL construction | Yes — ADO pipelines don't set `PIPELINE_URL`, so the fallback path is used |
| `publish_artifact.py` | No changes needed | N/A |
| `generate_attestation.py` | No changes needed | N/A |
| `normalize_test_results.py` | No changes needed | N/A |
