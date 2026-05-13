# bulk-reprocess-trades — ADO-to-GHA Migration Mapping

| Field | Value |
|---|---|
| **ADO Pipeline** | `bulk-reprocess-trades` (ID 115) |
| **ADO YAML** | `adhoc/bulk-reprocess-trades.yml` |
| **Category** | 6 — Active Ad-Hoc (manual trigger) |
| **Stack** | Python 3.11 (pandas, requests, pyarrow) |
| **GHA Workflow** | `.github/workflows/bulk-reprocess-trades.yml` |
| **Templates Inlined** | None (fully inline pipeline) |
| **Owner** | Unknown |

---

## 1. Trigger Mapping

| ADO | GHA | Notes |
|---|---|---|
| `trigger: none` | `on: workflow_dispatch` | ADO manual queue → GHA manual dispatch |
| ADO `parameters` (startDate, endDate, tradeTypes) | `workflow_dispatch.inputs` | Parameters become dispatch inputs with defaults preserved |

**Intentional change:** ADO parameters are typed as `string` with defaults. GHA `workflow_dispatch.inputs` uses the same `string` type with `default` values and adds `description` fields for better UI clarity.

---

## 2. Job Mapping

| ADO Job | GHA Job | Runner | Timeout |
|---|---|---|---|
| `ReprocessTrades` | `reprocess-trades` | `ubuntu-latest` | 480 min (job-level) |

**Notes:**
- ADO `pool.vmImage: 'ubuntu-latest'` maps directly to GHA `runs-on: ubuntu-latest`
- ADO `timeoutInMinutes: 480` maps to GHA `timeout-minutes: 480`

---

## 3. Step-by-Step Task Mapping

| # | ADO Step | GHA Step | Action / Command | Notes |
|---|---|---|---|---|
| 0 | _(implicit checkout)_ | `actions/checkout@v4` | Explicit checkout required in GHA | ADO checks out automatically; GHA requires explicit step |
| 1 | `UsePythonVersion@0` (versionSpec: 3.11) | `actions/setup-python@v5` (python-version: 3.11) | Setup Python | Direct equivalent |
| 2 | `script: pip install pandas requests pyarrow` | `run: pip install pandas requests pyarrow` | Install dependencies | Direct translation |
| 3 | `script: python adhoc/scripts/reprocess_trades.py ...` | `run: python adhoc/scripts/reprocess_trades.py ...` | Reprocess trades | See variable mapping below; `timeout-minutes: 420` preserved |
| 4 | `PublishBuildArtifacts@1` | `actions/upload-artifact@v4` | Archive results | `if: always()` added so artifacts upload even on failure |

---

## 4. Variable / Expression Mapping

| ADO Expression | GHA Expression | Context |
|---|---|---|
| `${{ parameters.startDate }}` | `${{ inputs.startDate }}` | Workflow dispatch input |
| `${{ parameters.endDate }}` | `${{ inputs.endDate }}` | Workflow dispatch input |
| `${{ parameters.tradeTypes }}` | `${{ inputs.tradeTypes }}` | Workflow dispatch input |
| `$(Build.ArtifactStagingDirectory)` | `${{ runner.temp }}/staging` | Output directory for artifacts |

---

## 5. ADO Variable Shims

The following environment variables are set at job level so that any helper scripts expecting ADO variables will work unmodified:

| Env Var | GHA Value |
|---|---|
| `BUILD_SOURCEBRANCH` | `${{ github.ref }}` |
| `BUILD_SOURCEVERSION` | `${{ github.sha }}` |
| `BUILD_BUILDID` | `${{ github.run_id }}` |
| `BUILD_ARTIFACTSTAGINGDIRECTORY` | `${{ runner.temp }}/staging` |
| `BUILD_SOURCESDIRECTORY` | `${{ github.workspace }}` |
| `AGENT_NAME` | `${{ runner.name }}` |
| `AGENT_OS` | `${{ runner.os }}` |
| `BUILD_REQUESTEDFOR` | `${{ github.actor }}` |
| `BUILD_DEFINITIONNAME` | `${{ github.workflow }}` |
| `SYSTEM_TEAMFOUNDATIONCOLLECTIONURI` | `${{ github.server_url }}/` |
| `SYSTEM_TEAMPROJECT` | `${{ github.repository }}` |
| `PIPELINE_URL` | `${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}` |

---

## 6. Key Translation Decisions

| Decision | Rationale |
|---|---|
| `mkdir -p` before reprocess step | GHA runners start fresh — `${{ runner.temp }}/staging/reprocessed/` does not exist by default |
| `if: always()` on artifact upload | Ensures partial results are captured even if the reprocess step fails or times out |
| Quoting `${{ inputs.* }}` in shell | Prevents word-splitting on dates/types containing spaces |
| `PIPELINE_URL` env var | Provides GHA-format run URL instead of ADO `_build/results` format |
| No `on.pull_request` trigger added | This is an ad-hoc manual pipeline — PR triggers would not be meaningful |

---

## 7. Known Gaps & Pre-existing Issues

| Gap | Impact | Mitigation |
|---|---|---|
| `adhoc/scripts/reprocess_trades.py` not in repo | Script referenced by pipeline but not present in this repo — likely deployed separately or stored elsewhere | Same gap exists in ADO; preserved as-is |
| No test result publishing | ADO pipeline has no test step — same in GHA | N/A |
| 8-hour timeout risk | GHA hosted runners have a 6-hour maximum for free-tier; this pipeline needs 480 min | Workflow will work on GitHub Teams/Enterprise (which support up to 72h). For free-tier orgs, consider self-hosted runners |

---

## 8. Secrets Required

This pipeline does **not** reference any secrets or variable groups. No repository secret configuration is needed.

If `reprocess_trades.py` requires credentials at runtime (e.g., database access, API keys), those would need to be configured as repository secrets and passed via `env:` blocks.

---

## 9. Integration Points

| Integration | ADO Behavior | GHA Behavior |
|---|---|---|
| Artifact storage | `PublishBuildArtifacts@1` → ADO artifact store | `actions/upload-artifact@v4` → GHA artifact store |
| Artifactory | Not used | Not used |
| D2 notifications | Not used | Not used |
| Compliance attestation | Not used | Not used |

---

## 10. Helper Script Impact

No helper scripts from `build-tools/scripts/` are referenced by this pipeline. No script updates are needed.
