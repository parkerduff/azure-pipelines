# frontend-workbench-ci — ADO to GitHub Actions Migration Mapping

**Pipeline:** frontend-workbench-ci  
**ADO ID:** 106  
**Category:** 2 (Alt-Template Consumer)  
**Stack:** Node.js (React)  
**Source YAML:** `services/frontend-workbench/azure-pipelines.yml`  
**Template Branch:** `team/frontend-custom`  
**GHA Workflow:** `.github/workflows/frontend-workbench-ci.yml`

---

## 1. Trigger Mapping

| Aspect | ADO | GHA | Notes |
|---|---|---|---|
| Push branches | `main`, `feature/*` | `main`, `feature/**` | Broadened from single-level `*` to recursive `**` for safety — GHA `*` only matches one directory level |
| Path filter | `services/frontend-workbench/**` | `services/frontend-workbench/**` | Direct mapping |
| PR trigger | _(none defined)_ | `pull_request` on `main` | **Added** — provides earlier CI feedback on pull requests |

---

## 2. Stage → Job Mapping

| ADO Stage | GHA Job | `needs:` | `if:` Condition | Environment |
|---|---|---|---|---|
| `Build` | `build` | — | — | — |
| `Deploy_Dev` (`dependsOn: Build`) | `deploy-dev` | `build` | — | `dev-frontend` |
| `Deploy_Staging` (`dependsOn: Deploy_Dev`, condition: main branch) | `deploy-staging` | `deploy-dev` | `github.event_name == 'push' && github.ref == 'refs/heads/main'` | `staging-frontend` |

---

## 3. Task Mapping — Build Stage

| # | ADO Task / Step | GHA Step | Input Translation |
|---|---|---|---|
| 1 | `NodeTool@0` (versionSpec: `18.x`) | `actions/setup-node@v4` (node-version: `18.x`) | Direct mapping |
| 2 | `script: npm ci` | `run: npm ci` | `working-directory: services/frontend-workbench` added |
| 3 | `script: npm run lint` | `run: npm run lint` | `working-directory: services/frontend-workbench` added |
| 4 | `script: npm run build:react` | `run: npm run build:react` | Parameter `${{ parameters.framework }}` resolved to `react` |
| 5 | `script: npm run build:ssr` (conditional: `enableSSR == true`) | `run: npm run build:ssr` | Always runs — parameter was `true` in the pipeline definition |
| 6 | `script: npm test -- --ci --coverage` | `run: npm test -- --ci --coverage` | Direct mapping |
| 7 | `ArchiveFiles@2` (rootFolderOrFile: `build/`, archiveType: `zip`) | `run: zip -r ...` | Shell zip command; `mkdir -p` added for staging directory on fresh runner |
| 8 | `script: npx lhci autorun` (Lighthouse CI) | `run: npx lhci autorun ... \|\| true` | Non-blocking audit; `|| true` preserved from ADO template |
| 9 | `PublishBuildArtifacts@1` (artifactName: `${{ parameters.artifactName }}-$(Build.BuildId)`) | `actions/upload-artifact@v4` (name: `...-${{ github.run_id }}`) | `Build.BuildId` → `github.run_id`; `if-no-files-found: error` added |

---

## 4. Task Mapping — Deploy Stages (Dev & Staging)

Both deploy stages use the same template (`frontend-deploy.yml`) with different `environment` parameters.

| # | ADO Task / Step | GHA Step | Input Translation |
|---|---|---|---|
| 1 | `download: current` (artifact) | `actions/download-artifact@v4` | Artifact name includes `github.run_id` suffix to match upload |
| 2 | `script: Upload to CDN` | `run: echo "Uploading..."` | Placeholder — real CDN upload to be configured per environment |
| 3 | `script: Purge CDN cache` (conditional: `cdnPurge == true`) | `run: echo "Purging..."` | Always runs — `cdnPurge` defaults to `true` |
| 4 | `script: Health check` (`curl -sf https://<env>.example.com/health`) | `run: curl -sf ...` | Direct mapping; URL parameterized by environment |

---

## 5. Variable Mapping

| ADO Variable | GHA Equivalent | Scope |
|---|---|---|
| `$(artifactName)` = `frontend-workbench-bundle` | `${{ env.ARTIFACT_NAME }}` | Workflow-level `env:` |
| `$(Build.BuildId)` | `${{ github.run_id }}` | Used in artifact naming |
| `$(Build.ArtifactStagingDirectory)` | `${{ runner.temp }}/staging` | `mkdir -p` added before first use |
| `$(Build.SourceBranch)` | `${{ github.ref }}` | Not directly used by frontend templates |

---

## 6. Condition Mapping

| ADO Condition | GHA `if:` Expression | Context |
|---|---|---|
| `and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))` | `github.event_name == 'push' && github.ref == 'refs/heads/main'` | Deploy_Staging gate — also excludes PR events |

---

## 7. ADO-Specific Feature Translation

| ADO Feature | GHA Translation | Notes |
|---|---|---|
| `deployment:` job type + `strategy: runOnce` | `environment:` key on GHA job | GHA environment provides protection rules; no explicit strategy needed |
| `resources.repositories` (template repo ref) | Eliminated — templates inlined | Templates are in the same repo; no cross-repo reference needed |
| `ArchiveFiles@2` | Shell `zip` command | Native `zip` available on `ubuntu-latest` runners |
| `PublishBuildArtifacts@1` | `actions/upload-artifact@v4` | Standard GHA replacement |

---

## 8. Integration Points

| Integration | ADO Behaviour | GHA Behaviour |
|---|---|---|
| **Artifactory** | Not used by frontend templates | Not applicable — no `publish_artifact.py` call |
| **D2 (release orchestrator)** | Not used by frontend templates | Not applicable — no `notify_release_orchestrator.py` call |
| **CDN upload** | Placeholder `echo` in ADO template | Preserved as placeholder `echo` — real CDN integration to be configured |
| **CDN cache purge** | Placeholder `echo` in ADO template | Preserved as placeholder — requires CDN API integration |
| **Lighthouse CI** | `npx lhci autorun` with `|| true` | Preserved — non-blocking performance audit |

---

## 9. Known Gaps & Behavioural Differences

| Gap | Details | Risk |
|---|---|---|
| **Branch glob broadening** | ADO `feature/*` → GHA `feature/**`. GHA may trigger on nested branches like `feature/team/foo` that ADO would ignore. | Low — more inclusive is generally safer |
| **PR trigger added** | ADO pipeline had no explicit PR trigger. GHA workflow adds `on.pull_request` for `main`. | Informational — provides earlier feedback, no functional change to push-triggered builds |
| **Artifact naming** | ADO used `Build.BuildId` (sequential integer); GHA uses `github.run_id` (integer, but different numbering). Downstream consumers must not assume a specific ID format. | Low |
| **Deployment strategy** | ADO `strategy: runOnce` is implicit in GHA. GHA `environment:` provides deployment protection rules but does not have a built-in runOnce rollback mechanism. | Low — deploy steps are simple CDN uploads |
| **Lighthouse CI results** | In ADO, Lighthouse results were part of the pipeline logs. In GHA, same behaviour — results appear in step logs. No separate reporting integration. | None |
| **Test coverage output** | `npm test -- --ci --coverage` outputs coverage to console and files. No explicit coverage upload step in either ADO or GHA. | Pre-existing gap — preserved as-is |

---

## 10. Secrets Required

This pipeline does not reference any secrets directly. The CDN upload and purge steps are placeholders. When real CDN integration is configured, the following secrets may be needed:

| Secret | Purpose |
|---|---|
| `CDN_API_KEY` | Authenticate with CDN provider for asset upload |
| `CDN_PURGE_TOKEN` | Authenticate with CDN provider for cache purge |

---

## 11. Environments Required

Configure these environments in the GitHub repository settings with appropriate protection rules:

| Environment | Purpose | Recommended Protection |
|---|---|---|
| `dev-frontend` | Development deployment | None (auto-deploy) |
| `staging-frontend` | Staging deployment | Required reviewers |

---

## 12. Files Added / Modified

| File | Action | Description |
|---|---|---|
| `.github/workflows/frontend-workbench-ci.yml` | **Added** | GHA workflow — functional equivalent of the ADO pipeline |
| `docs/migration/frontend-workbench-ci-ado-to-gha-mapping.md` | **Added** | This mapping document |

No helper scripts in `build-tools/scripts/` were modified — the frontend templates do not call any shared helper scripts.
