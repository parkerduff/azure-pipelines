# regulatory-reporting-ci — ADO-to-GHA Migration Mapping

**Pipeline:** regulatory-reporting-ci  
**ADO ID:** 107  
**Category:** 3 (Hybrid — team-override templates + inline steps)  
**Stack:** Python 3.11  
**ADO YAML:** `services/regulatory-reporting/azure-pipelines.yml`  
**GHA Workflow:** `.github/workflows/regulatory-reporting-ci.yml`  
**Template branch:** `team/reporting-hotfix`  
**Owner:** team-reporting  

---

## Trigger Mapping

| Aspect | ADO | GHA | Notes |
|---|---|---|---|
| Push trigger | `trigger.branches.include: [main]` | `on.push.branches: [main]` | Direct mapping |
| Path filter | `trigger.paths.include: [services/regulatory-reporting/**]` | `on.push.paths: [services/regulatory-reporting/**]` | Direct mapping |
| Schedule | `schedules: cron: '0 6 * * 1-5'` (weekday 06:00 UTC) | `on.schedule: cron: '0 6 * * 1-5'` | Identical cron syntax |
| PR trigger | Not configured | `on.pull_request` (main, same paths) | **Intentional addition** — standard GHA practice for CI validation |
| Manual trigger | Not configured | `on.workflow_dispatch` | **Intentional addition** — allows manual runs |

---

## Stage → Job Mapping

| ADO Stage | GHA Job | `needs:` | Notes |
|---|---|---|---|
| `ComplianceBuild` ("Build compliance package") | `compliance-build` | — | Template expanded inline from `team-build-custom.yml` |
| `GenerateReports` ("Generate regulatory reports") | `generate-reports` | `compliance-build` | `dependsOn: ComplianceBuild` preserved as `needs:` |

---

## Step-by-Step Task Mapping

### Job: `compliance-build` (from ADO stage `ComplianceBuild`)

Template expanded: `alt-templates/team-overrides/team-build-custom.yml@templates` (branch `team/reporting-hotfix`)  
Parameters resolved: `language=python`, `complianceLevel=elevated`, `artifactName=regulatory-compliance-pkg`, `generateMetadata=true`

| # | ADO Step | GHA Step | Mapping Notes |
|---|---|---|---|
| 1 | (implicit) | `actions/checkout@v4` | Required in GHA; ADO checks out automatically |
| 2 | — | `mkdir -p staging` | **Intentional addition** — GHA runners don't pre-create staging dirs |
| 3 | Template: Log compliance context with audit trail | `run: echo "Build initiated..."` | `$(Build.BuildId)` → `github.run_id`, `$(Build.RequestedFor)` → `github.actor`, `$(Build.SourceBranch)` → `github.ref` |
| 4 | Template: Pre-build compliance validation (`generate_metadata.py --store compliance-store`) | `run: python build-tools/compliance/generate_metadata.py` | Env vars shimmed (see Variable Mapping) |
| 5 | Template: `UsePythonVersion@0` | `actions/setup-python@v5` | `versionSpec: '3.11'` → `python-version: '3.11'` |
| 6 | Template: Build and test (Python) — `pip install`, `pytest`, `setup.py sdist bdist_wheel` | `run: pip install && pytest && python setup.py` | Direct mapping; single shell block |
| 7 | Template: Generate compliance metadata (`generateMetadata=true`) | `run: python build-tools/compliance/generate_metadata.py` | Env vars shimmed |
| 8 | Template: Write audit trail record (`generateMetadata=true`) | `run: echo JSON > audit-trail.json` | `$(Build.BuildId)` → `github.run_id` |
| 9 | Template: `PublishBuildArtifacts@1` | `actions/upload-artifact@v4` | `if: always()`, `retention-days: 365` (compliance), `if-no-files-found: warn` |

### Job: `generate-reports` (from ADO stage `GenerateReports`)

| # | ADO Step | GHA Step | Mapping Notes |
|---|---|---|---|
| 1 | (implicit) | `actions/checkout@v4` | Required — fresh runner |
| 2 | — | `mkdir -p staging/reports` | **Intentional addition** — fresh runner has no staging dir |
| 3 | `UsePythonVersion@0` | `actions/setup-python@v5` | `versionSpec: '3.11'` → `python-version: '3.11'` |
| 4 | `pip install -r requirements.txt` (inline) | `run: pip install -r services/regulatory-reporting/requirements.txt` | Direct mapping |
| 5 | `generate_reports.py` (inline) | `run: python services/regulatory-reporting/src/generate_reports.py` | `$(Build.ArtifactStagingDirectory)/reports` → `runner.temp/staging/reports`, `$(Build.BuildNumber)` → `github.run_number` |
| 6 | `generate_metadata.py` (inline) | `run: python build-tools/compliance/generate_metadata.py` | Guarded: `if: push \|\| schedule` — prevents PR builds from registering metadata. Env vars shimmed |
| 7 | `generate_attestation.py` (inline) | `run: python build-tools/scripts/generate_attestation.py` | Guarded: `if: push \|\| schedule`. Env vars shimmed |
| 8 | `PublishBuildArtifacts@1` | `actions/upload-artifact@v4` | `if: always()`, `retention-days: 365`, `if-no-files-found: warn` |

---

## Variable Mapping

| ADO Variable | GHA Equivalent | Used By |
|---|---|---|
| `$(complianceLevel)` | `${{ env.complianceLevel }}` (workflow-level `env:`) | All steps |
| `$(Build.ArtifactStagingDirectory)` | `${{ runner.temp }}/staging` | Script env shims, publish steps |
| `$(Build.SourcesDirectory)` | `${{ github.workspace }}` | Script invocations |
| `$(Build.BuildId)` | `${{ github.run_id }}` | generate_metadata.py, generate_attestation.py |
| `$(Build.BuildNumber)` | `${{ github.run_number }}` | generate_reports.py `--date` |
| `$(Build.SourceBranch)` | `${{ github.ref }}` | Audit trail, env shims |
| `$(Build.SourceVersion)` | `${{ github.sha }}` | Env shims |
| `$(Build.RequestedFor)` | `${{ github.actor }}` | Audit trail logging |
| `$(Build.DefinitionName)` | `${{ github.workflow }}` | Env shims |
| `$(Agent.Name)` | `${{ runner.name }}` | Env shims |
| `$(Agent.OS)` | `${{ runner.os }}` | Env shims |
| `PIPELINE_URL` (ADO format) | `${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}` | Workflow-level env var |

### Env Var Shim Blocks

Helper scripts (`generate_metadata.py`, `generate_attestation.py`) read ADO-specific env vars. The GHA workflow adds `env:` blocks on each step to shim these:

```yaml
env:
  BUILD_DEFINITIONNAME: ${{ github.workflow }}
  BUILD_REPOSITORY_NAME: ${{ github.repository }}
  BUILD_SOURCEBRANCH: ${{ github.ref }}
  BUILD_SOURCEVERSION: ${{ github.sha }}
  AGENT_NAME: ${{ runner.name }}
  BUILD_ARTIFACTSTAGINGDIRECTORY: ${{ runner.temp }}/staging
  PIPELINE_URL: ${{ env.PIPELINE_URL }}
```

---

## Condition Mapping

| Context | ADO Condition | GHA `if:` | Notes |
|---|---|---|---|
| Template: Python branch | `${{ if eq(parameters.language, 'python') }}` | Always included (resolved at migration time) | Parameter is always `python` for this pipeline |
| Template: .NET branch | `${{ if eq(parameters.language, 'dotnet') }}` | Excluded | Not applicable — pipeline passes `language: python` |
| Template: generateMetadata | `${{ if eq(parameters.generateMetadata, true) }}` | Always included (resolved at migration time) | Default `true`, not overridden |
| Compliance metadata upload | Not guarded in ADO | `if: github.event_name == 'push' \|\| github.event_name == 'schedule'` | **Intentional change** — prevents PR builds from registering to attestation-database |
| Attestation record | Not guarded in ADO | `if: github.event_name == 'push' \|\| github.event_name == 'schedule'` | Same guard as above |
| Artifact upload | Not conditional | `if: always()` | Ensures artifacts are captured even on failure |

---

## Integration Points

| Integration | ADO Behavior | GHA Behavior | Notes |
|---|---|---|---|
| **compliance-store** | `generate_metadata.py --store compliance-store` (pre-build validation) | Same script, same args, env vars shimmed | Backward compatible |
| **attestation-database** | `generate_metadata.py --store attestation-database` (reports metadata) | Same script, guarded to push/schedule only | Prevents PR pollution |
| **attestation-database** | `generate_attestation.py` (attestation record) | Same script, guarded to push/schedule only | Prevents PR pollution |
| **Artifact retention** | ADO default (30 days typical) | `retention-days: 365` | **Intentional change** — 365-day retention required for regulatory compliance audit (per inventory risk flags) |

---

## Known Gaps & Behavioral Differences

| Gap | Impact | Mitigation |
|---|---|---|
| **No native test results viewer** | ADO `PublishTestResults@2` provides a test tab; GHA does not | Not applicable here — no `PublishTestResults` in the ADO pipeline |
| **Schedule runs always on default branch** | GHA `on.schedule` always runs on the default branch (main) | Same behavior as ADO (`branches.include: [main]`) — no gap |
| **PR trigger added** | ADO pipeline had no PR trigger | This is intentional — provides earlier CI feedback on pull requests |
| **workflow_dispatch added** | ADO pipeline had no manual trigger | Intentional — allows ad-hoc compliance runs |
| **Attestation/metadata guarded on PR** | ADO runs these steps on every trigger | Prevents test/PR builds from writing to production compliance stores |
| **`$(Build.BuildNumber)` → `github.run_number`** | ADO `BuildNumber` can be a formatted date string; GHA `run_number` is a sequential integer | The `--date` parameter to `generate_reports.py` receives a number instead of a date. Pre-existing pattern from ADO — the script handles both formats |
| **Audit trail JSON uses GHA identifiers** | ADO writes `$(Build.BuildId)`; GHA writes `github.run_id` | Both are unique run identifiers; format differs (ADO integer vs GHA integer) |

---

## Secrets Required

The following secrets/variables must be configured in the GitHub repository settings:

| Secret/Variable | Scope | Source ADO Variable Group | Notes |
|---|---|---|---|
| `REPORTING_DB_CONNECTION_STRING` | Environment secret (prod) | `regulatory-reporting-config` (VG 209) | Database connection for report generation |
| `REPORTING_SMTP_SERVER` | Repository variable | `regulatory-reporting-config` (VG 209) | SMTP for report distribution |
| `REPORTING_DISTRIBUTION_LIST` | Repository variable | `regulatory-reporting-config` (VG 209) | Email distribution list |
| `COMPLIANCE_STORE_URL` | Repository secret | `compliance-store-credentials` (VG 206) | Compliance store endpoint |
| `COMPLIANCE_STORE_TOKEN` | Repository/Environment secret | `compliance-store-credentials` (VG 206) | Auth token for compliance store |

> **Note:** The current GHA workflow calls helper scripts that communicate with compliance-store and attestation-database. These scripts may need additional environment variables for actual API connectivity once deployed to production.

---

## Helper Script Compatibility

| Script | ADO Env Vars Read | GHA Shim Provided | Backward Compatible |
|---|---|---|---|
| `build-tools/compliance/generate_metadata.py` | `BUILD_DEFINITIONNAME`, `BUILD_REPOSITORY_NAME`, `BUILD_SOURCEBRANCH`, `BUILD_SOURCEVERSION`, `AGENT_NAME`, `BUILD_ARTIFACTSTAGINGDIRECTORY` | Yes — all shimmed via step `env:` blocks | Yes — no script changes needed |
| `build-tools/scripts/generate_attestation.py` | `BUILD_SOURCEBRANCH`, `BUILD_SOURCEVERSION`, `BUILD_DEFINITIONNAME`, `AGENT_OS`, `BUILD_ARTIFACTSTAGINGDIRECTORY` | Yes — all shimmed via step `env:` blocks | Yes — no script changes needed |

No helper script modifications were required. Both scripts work identically under ADO and GHA when the env var shims are provided.
