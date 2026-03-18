# frontend-workbench: ADO-to-GitHub Actions Migration Verification

## Pipeline Overview

| Field               | Value                                                         |
|---------------------|---------------------------------------------------------------|
| **Service**         | frontend-workbench                                            |
| **Stack**           | Node.js 18.x (React) with SSR                                |
| **ADO Pipeline**    | `services/frontend-workbench/azure-pipelines.yml`             |
| **GH Workflow**     | `.github/workflows/frontend-workbench-ci.yml`                 |
| **Template Source** | `alt-templates/frontend/` from `team/frontend-custom` branch  |
| **Templates Used**  | `frontend-build.yml`, `frontend-deploy.yml`                   |
| **Pool**            | `vmImage: ubuntu-latest` -> `runs-on: ubuntu-latest`          |
| **Owner**           | team-frontend                                                 |

---

## Architecture Diagram

```
ADO Pipeline (Expanded)                    GitHub Actions Workflow
========================================   ========================================

services/frontend-workbench/               .github/workflows/
  azure-pipelines.yml                        frontend-workbench-ci.yml

trigger:                                   on:
  branches: [main, feature/*]               push:
  paths: [services/frontend-workbench/**]      branches: [main, feature/*]
                                               paths: [services/frontend-workbench/**]
                                             pull_request:          <-- ADDED
                                               branches: [main, feature/*]
                                               paths: [services/frontend-workbench/**]
                                             workflow_dispatch:     <-- ADDED

variables:                                 env:
  artifactName: frontend-workbench-bundle    ARTIFACT_NAME: frontend-workbench-bundle

+---------------------+                   +---------------------+
| Stage: Build        |                   | Job: build          |
| (frontend-build.yml |                   |                     |
|  template expanded) |                   |                     |
+---------------------+                   +---------------------+
| NodeTool@0 18.x     | ───────────────>  | setup-node@v4 18.x  |
| npm ci               | ───────────────>  | npm ci               |
| npm run lint         | ───────────────>  | npm run lint         |
| npm run build:react  | ───────────────>  | npm run build:react  |
| npm run build:ssr    | ───────────────>  | npm run build:ssr    |
| npm test --ci --cov  | ───────────────>  | npm test --ci --cov  |
| ArchiveFiles@2       | ───────────────>  | zip command          |
| lhci autorun         | ───────────────>  | lhci autorun         |
| PublishBuildArt@1    | ───────────────>  | upload-artifact@v4   |
+---------------------+                   +---------------------+
         |                                          |
         v                                          v
+---------------------+                   +---------------------+
| Stage: Deploy_Dev   |                   | Job: deploy-dev     |
| dependsOn: Build    |                   | needs: build        |
| (frontend-deploy.yml|                   | environment:        |
|  env=dev)           |                   |   dev-frontend      |
+---------------------+                   +---------------------+
| download: current    | ───────────────>  | download-artifact@v4|
| Upload to CDN        | ───────────────>  | Upload to CDN       |
| Purge CDN cache      | ───────────────>  | Purge CDN cache     |
| Health check (curl)  | ───────────────>  | Health check (curl) |
+---------------------+                   +---------------------+
         |                                          |
         v                                          v
+---------------------+                   +---------------------+
| Stage: Deploy_Stag  |                   | Job: deploy-staging |
| dependsOn: Deploy_  |                   | needs: deploy-dev   |
|   Dev               |                   | if: main && push    |
| condition:          |                   | environment:        |
|   main branch only  |                   |   staging-frontend  |
+---------------------+                   +---------------------+
| download: current    | ───────────────>  | download-artifact@v4|
| Upload to CDN        | ───────────────>  | Upload to CDN       |
| Purge CDN cache      | ───────────────>  | Purge CDN cache     |
| Health check (curl)  | ───────────────>  | Health check (curl) |
+---------------------+                   +---------------------+
```

---

## Step-by-Step Comparison

### Build Stage / Job

| # | ADO Step (Expanded from frontend-build.yml) | GH Actions Step | Verdict | Notes |
|---|---------------------------------------------|-----------------|---------|-------|
| 1 | *(implicit checkout)* | `actions/checkout@v4` | ADDED | ADO checks out automatically; GH Actions requires explicit checkout action |
| 2 | `NodeTool@0` (versionSpec: 18.x) | `actions/setup-node@v4` (node-version: 18.x) | MATCH | Direct equivalent |
| 3 | `script: npm ci` | `run: npm ci` | MATCH | Identical command |
| 4 | `script: npm run lint` | `run: npm run lint` | MATCH | Identical command |
| 5 | `script: npm run build:react` | `run: npm run build:react` | MATCH | Parameter `framework: react` expanded at template compile time |
| 6 | `script: npm run build:ssr` (conditional: enableSSR=true) | `run: npm run build:ssr` | MATCH | Condition evaluates to true (enableSSR=true), so step always runs for this pipeline |
| 7 | `script: npm test -- --ci --coverage` | `run: npm test -- --ci --coverage` | MATCH | Identical command |
| 8 | `ArchiveFiles@2` (zip build/ -> staging dir) | `run: zip -r ...` + `mkdir staging` | MATCH | Equivalent behavior; shell zip replaces ADO task |
| 9 | `script: npx lhci autorun ... \|\| true` | `run: npx lhci autorun ... \|\| true` | MATCH | Identical command with same `|| true` failure suppression |
| 10 | `PublishBuildArtifacts@1` | `actions/upload-artifact@v4` | MATCH | Artifact name pattern: `{name}-{run_id}` preserved |

### Deploy Dev Stage / Job

| # | ADO Step (Expanded from frontend-deploy.yml) | GH Actions Step | Verdict | Notes |
|---|----------------------------------------------|-----------------|---------|-------|
| 1 | `download: current` (artifact) | `actions/download-artifact@v4` | MATCH | Downloads artifact from build job |
| 2 | `script: echo "Uploading static assets..."` | `run: echo "Uploading static assets..."` | MATCH | Placeholder CDN upload |
| 3 | `script: echo "Purging CDN cache..."` (conditional: cdnPurge=true) | `run: echo "Purging CDN cache..."` | MATCH | cdnPurge defaults to true, condition evaluates to true |
| 4 | `script: curl -sf https://dev.example.com/health` | `run: curl -sf https://dev.example.com/health` | MATCH | Identical health check |

### Deploy Staging Stage / Job

| # | ADO Step (Expanded from frontend-deploy.yml) | GH Actions Step | Verdict | Notes |
|---|----------------------------------------------|-----------------|---------|-------|
| 1 | `download: current` (artifact) | `actions/download-artifact@v4` | MATCH | Downloads artifact from build job |
| 2 | `script: echo "Uploading static assets..."` | `run: echo "Uploading static assets..."` | MATCH | Placeholder CDN upload |
| 3 | `script: echo "Purging CDN cache..."` (conditional: cdnPurge=true) | `run: echo "Purging CDN cache..."` | MATCH | cdnPurge defaults to true |
| 4 | `script: curl -sf https://staging.example.com/health` | `run: curl -sf https://staging.example.com/health` | MATCH | Identical health check |

### Stage Dependencies and Conditions

| ADO | GH Actions | Verdict |
|-----|------------|---------|
| `Deploy_Dev.dependsOn: Build` | `deploy-dev.needs: build` | MATCH |
| `Deploy_Staging.dependsOn: Deploy_Dev` | `deploy-staging.needs: deploy-dev` | MATCH |
| `Deploy_Staging.condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))` | `deploy-staging.if: github.ref == 'refs/heads/main' && github.event_name == 'push'` | MATCH | Added `event_name == 'push'` to exclude PR runs, which is the correct GH Actions equivalent |

---

## Summary Scorecard

| Metric | Count |
|--------|-------|
| **Total ADO steps (expanded)** | 18 (10 build + 4 dev deploy + 4 staging deploy) |
| **Matched steps** | 18 |
| **Removed steps** | 0 |
| **Added steps** | 1 (explicit checkout in build job) |
| **Total GH Actions steps** | 19 |

---

## Intentional Differences

| # | Difference | Justification |
|---|------------|---------------|
| 1 | Added `on.pull_request` trigger | Standard GH Actions practice for CI validation on PRs. ADO pipelines typically rely on branch policies for PR validation. |
| 2 | Added `workflow_dispatch` trigger | Enables manual workflow runs from GH Actions UI, useful for debugging and re-runs. |
| 3 | Added explicit `actions/checkout@v4` step | ADO implicitly checks out the repository; GH Actions requires an explicit checkout action. |
| 4 | `ArchiveFiles@2` replaced with shell `zip` command | No direct GH Actions equivalent for ArchiveFiles task. Shell zip produces identical output. |
| 5 | ADO `deployment` job type mapped to regular job with `environment:` | GH Actions uses `environment:` on jobs instead of a dedicated deployment job type. Provides equivalent protection rules and approval gates. |
| 6 | ADO environment names mapped to `{env}-frontend` | Matches ADO pattern `{environment}-frontend` from the deploy template (`${{ parameters.environment }}-frontend`). |
| 7 | `working-directory` added to build steps | ADO pipeline runs in repo root with source in working directory; GH Actions needs explicit `working-directory` since the service code is nested under `services/frontend-workbench/`. |
| 8 | Deploy_Staging `if:` adds `github.event_name == 'push'` | ADO condition only checks branch. In GH Actions, PRs targeting main would also have `refs/heads/main` as the base, so `event_name` check prevents unwanted staging deploys on PRs. |

---

## Template Parameters Resolution

### frontend-build.yml

| Parameter | Passed Value | Default | Resolved |
|-----------|-------------|---------|----------|
| `nodeVersion` | `'18.x'` | `'18.x'` | `18.x` |
| `framework` | `'react'` | `'react'` | `react` |
| `enableSSR` | `true` | `true` | `true` — SSR build step **included** |
| `artifactName` | `$(artifactName)` | `'frontend-bundle'` | `frontend-workbench-bundle` (from pipeline variable) |

### frontend-deploy.yml (Dev invocation)

| Parameter | Passed Value | Default | Resolved |
|-----------|-------------|---------|----------|
| `environment` | `'dev'` | *(required)* | `dev` |
| `artifactName` | `$(artifactName)` | `'frontend-bundle'` | `frontend-workbench-bundle` |
| `cdnPurge` | *(not passed)* | `true` | `true` — CDN purge step **included** |

### frontend-deploy.yml (Staging invocation)

| Parameter | Passed Value | Default | Resolved |
|-----------|-------------|---------|----------|
| `environment` | `'staging'` | *(required)* | `staging` |
| `artifactName` | `$(artifactName)` | `'frontend-bundle'` | `frontend-workbench-bundle` |
| `cdnPurge` | *(not passed)* | `true` | `true` — CDN purge step **included** |

---

## Build-Tools Script Dependencies

**None.** The frontend-workbench pipeline templates (`frontend-build.yml`, `frontend-deploy.yml`) do not reference any `build-tools/` scripts. All steps use ADO built-in tasks or inline shell commands. No ADO environment variable mapping for build-tools scripts is required.

---

## Open Items Requiring Runtime Validation

| # | Item | Risk | Validation Method |
|---|------|------|-------------------|
| 1 | `npm run build:react` script exists in `services/frontend-workbench/package.json` | Medium | Verify package.json has `build:react` script |
| 2 | `npm run build:ssr` script exists in `services/frontend-workbench/package.json` | Medium | Verify package.json has `build:ssr` script |
| 3 | `build/` directory is created by the build step and contains deployable assets | Medium | Run build locally and verify output directory |
| 4 | Lighthouse CI (`lhci`) configuration exists or `autorun` works without config | Low | The `\|\| true` suppresses failures, but verify lhci is configured |
| 5 | Artifact zip structure matches ADO `ArchiveFiles@2` output | Low | Compare zip contents from both pipelines |
| 6 | GH Actions `environment:` protection rules configured for `dev-frontend` and `staging-frontend` | High | Must configure environments in GitHub repo settings |
| 7 | Health check URLs (`dev.example.com`, `staging.example.com`) are reachable from GH-hosted runners | Medium | These are placeholder URLs in the template; verify actual endpoints |
| 8 | `dorny/test-reporter` or similar not needed since tests output to stdout | Low | Confirm test output format is sufficient without formal test reporting |
| 9 | Third-party action `actions/upload-artifact@v4` and `actions/download-artifact@v4` approved by org | Low | Standard GitHub-maintained actions, but verify org policy |
