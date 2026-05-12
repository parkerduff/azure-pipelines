# pricing-engine-ci: ADO → GitHub Actions Migration Mapping

**Pipeline:** pricing-engine-ci (ADO ID 101)  
**Category:** Central Template Consumer  
**Stack:** .NET 8  
**Source:** `services/pricing-engine/azure-pipelines.yml`  
**Target:** `.github/workflows/pricing-engine-ci.yml`

---

## 1. Template Resolution

The ADO pipeline uses three central templates via a repository resource:

```yaml
resources:
  repositories:
    - repository: templates
      type: git
      name: shared-ci-platform
      ref: main
```

| ADO Template | What It Does | GHA Equivalent |
|---|---|---|
| `templates/build/build-dotnet.yml@templates` | .NET SDK setup, NuGet restore, build, test, publish, Artifactory registration | Inlined into `build` job |
| `templates/test/run-tests.yml@templates` | Test result creation, publishing, normalisation | Inlined into `test` job |
| `templates/release/release-standard.yml@templates` | Artifact download, deploy, D2 notification, compliance attestation | Inlined into `deploy-dev` job |

Since the templates live in the *same* repository, there is no need for a GHA repository resource.  All template logic is inlined directly into the workflow jobs.  If templates are later extracted into a shared repo, use [reusable workflows](https://docs.github.com/en/actions/using-workflows/reusing-workflows) with `workflow_call`.

---

## 2. Trigger Mapping

| Concept | ADO | GHA |
|---|---|---|
| Branch filter | `trigger.branches.include: [main, release/*]` | `on.push.branches: [main, release/**]` |
| Path filter | `trigger.paths.include: [services/pricing-engine/**]` | `on.push.paths: [services/pricing-engine/**]` |
| PR trigger | Implicit (ADO default) | Explicit `on.pull_request` added |

> **Note:** ADO uses `release/*` (single-level glob). GHA uses `release/**` (recursive glob) so nested branches like `release/v1/hotfix` are also matched.

---

## 3. Task-to-Action Mapping

### Build Stage

| ADO Task | GHA Step | Notes |
|---|---|---|
| `UseDotNet@2` | `actions/setup-dotnet@v4` | Direct equivalent |
| `NuGetToolInstaller@1` | *(removed)* | NuGet CLI is bundled with .NET SDK |
| `NuGetCommand@2` (restore) | `dotnet restore` | Native CLI replaces dedicated task |
| `DotNetCoreCLI@2` (build) | `dotnet build --no-restore` | Same flags |
| `DotNetCoreCLI@2` (test) | `dotnet test --collect:"XPlat Code Coverage"` | Added `--results-directory` and TRX logger for GHA compatibility |
| `DotNetCoreCLI@2` (publish) with `publishWebProjects: true` | `grep` for `Microsoft.NET.Sdk.Web` + per-project `dotnet publish` | ADO filters to web SDK projects; replicated via grep loop |
| `PublishBuildArtifacts@1` | `actions/upload-artifact@v4` | Pipeline artifacts → GHA artifacts |
| `publish_artifact.py` | Same script, env vars remapped | See variable mapping below |

### Test Stage

| ADO Task | GHA Step | Notes |
|---|---|---|
| `mkdir -p` test-results dir | *(implicit)* | `dotnet test --results-directory` creates the directory |
| `PublishTestResults@2` | `actions/upload-artifact@v4` | GHA has no built-in test results tab; artifact download or `dorny/test-reporter` recommended |
| `normalize_test_results.py` | Same script, env vars remapped | Unchanged |

### Deploy Stage

| ADO Task | GHA Step | Notes |
|---|---|---|
| `deployment` job with `environment:` | `jobs.deploy-dev.environment: dev` | Direct equivalent; GHA environments support protection rules & required reviewers |
| `download: current` | `actions/download-artifact@v4` | Same concept |
| Deploy script | Inline `run:` | Unchanged |
| `notify_release_orchestrator.py` | Same script, `PIPELINE_URL` env var override | Script updated to prefer `PIPELINE_URL` over ADO-style URL construction |
| `generate_attestation.py` | Same script, env vars remapped, `mkdir -p` added | Staging dir must be pre-created since GHA deploy job runs on a fresh runner |

---

## 4. Variable & Expression Mapping

| ADO Variable / Expression | GHA Equivalent |
|---|---|
| `$(buildConfiguration)` | `${{ env.BUILD_CONFIGURATION }}` |
| `$(artifactName)` | `${{ env.ARTIFACT_NAME }}` |
| `$(Build.BuildId)` | `${{ github.run_id }}` |
| `$(Build.SourceBranch)` | `${{ github.ref }}` |
| `$(Build.SourceVersion)` | `${{ github.sha }}` |
| `$(Build.SourcesDirectory)` | `${{ github.workspace }}` (implicit with `actions/checkout`) |
| `$(Build.ArtifactStagingDirectory)` | `${{ runner.temp }}/staging` |
| `$(Build.DefinitionName)` | `${{ github.workflow }}` |
| `$(Build.RequestedFor)` | `${{ github.actor }}` |
| `$(Agent.Name)` | `${{ runner.name }}` |
| `$(Agent.OS)` | `${{ runner.os }}` |
| `$(System.TeamFoundationCollectionUri)` | `${{ github.server_url }}/` |
| `$(System.TeamProject)` | `${{ github.repository }}` |

### Condition Mapping

| ADO Condition | GHA `if:` |
|---|---|
| `and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))` | `github.ref == 'refs/heads/main' && github.event_name == 'push'` |
| `${{ if eq(parameters.runTests, true) }}` | Always true (parameter defaulted to `true`) — inlined unconditionally |
| `${{ if eq(parameters.publishArtifacts, true) }}` | Always true — inlined unconditionally |

---

## 5. Stage → Job Dependency Mapping

```
ADO Stages (sequential):          GHA Jobs (needs):
┌─────────┐                       ┌─────────┐
│  Build   │                      │  build   │
└────┬─────┘                      └────┬─────┘
     │ dependsOn                       │ needs
┌────▼─────┐                      ┌────▼─────┐
│   Test   │                      │   test   │
└────┬─────┘                      └────┬─────┘
     │ dependsOn + condition           │ needs + if
┌────▼──────────┐                 ┌────▼──────────┐
│  Deploy_Dev   │                 │  deploy-dev   │
│ (main only)   │                 │ (main only)   │
└───────────────┘                 └───────────────┘
```

---

## 6. Integration Points

| Integration | ADO Mechanism | GHA Mechanism | Migration Notes |
|---|---|---|---|
| **Artifactory** | `publish_artifact.py` with ADO env vars | Same script with GHA env var shims | Script reads `BUILD_SOURCEBRANCH` etc. — mapped via `env:` block |
| **D2** | `notify_release_orchestrator.py` | Same script with GHA env var shims | Pipeline URL format changes from ADO to `github.server_url` |
| **Attestation DB** | `generate_attestation.py` | Same script with GHA env var shims | No changes needed beyond env var mapping |
| **Test results** | `PublishTestResults@2` (built-in ADO tab) | `actions/upload-artifact@v4` | GHA lacks a native test results tab; consider `dorny/test-reporter@v1` for PR annotations |

---

## 7. What Changed

1. **Template repository resource eliminated** — templates are in the same repo, so logic is inlined.
2. **NuGet tasks collapsed** — `NuGetToolInstaller@1` + `NuGetCommand@2` replaced by `dotnet restore`.
3. **PR trigger added** — ADO only triggered on push; GHA workflow also runs on PRs to `main` for earlier feedback.
4. **Test result publishing** — ADO's built-in test tab replaced by artifact upload; add `dorny/test-reporter` for richer PR-level reporting if desired.
5. **Deployment environment** — ADO `environment:` maps directly to GHA `environment:` with support for protection rules.
6. **ADO env vars shimmed** — Helper scripts expect ADO-specific env vars (`BUILD_SOURCEBRANCH`, etc.); these are mapped in each job's `env:` block so scripts run unmodified.
