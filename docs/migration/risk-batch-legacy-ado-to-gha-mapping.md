# risk-batch-legacy — ADO-to-GHA Migration Mapping

**Pipeline:** risk-batch-legacy  
**ADO ID:** 105  
**Category:** 1 (Central Template Consumer)  
**Stack:** Python (legacy)  
**Owner:** team-quant  
**Source YAML:** `services/risk-batch/azure-pipelines-legacy.yml`  
**Template branch:** `legacy/master-support` (FROZEN)  
**GHA workflow:** `.github/workflows/risk-batch-legacy.yml`

---

## 1. Trigger Mapping

| Aspect | ADO | GHA | Notes |
|---|---|---|---|
| Push trigger | `trigger: none` | — | ADO pipeline is manually / downstream triggered; no push trigger |
| Manual trigger | Implicit (run from ADO UI) | `workflow_dispatch` | Preserves manual trigger capability |
| PR trigger | None | `on.pull_request` (main, `services/risk-batch/**`) | **Intentional addition** — provides earlier CI feedback on PRs |

---

## 2. Pool / Runner Mapping

| ADO | GHA |
|---|---|
| `vmImage: 'ubuntu-20.04'` | `runs-on: ubuntu-latest` |

> **Note:** ADO used `ubuntu-20.04` (EOL April 2025). GHA migrated to `ubuntu-latest` for continued support. If exact OS parity is required, use `ubuntu-22.04`.

---

## 3. Stage / Job Mapping

| ADO Stage | ADO Job | GHA Job | Dependencies | Conditions |
|---|---|---|---|---|
| `Build` | `legacy_build` | `build` | None | None |

This is a single-stage, single-job pipeline. No deploy stages.

---

## 4. Template Resolution

The pipeline references one template from the FROZEN `legacy/master-support` branch:

| Template | Parameters Passed |
|---|---|
| `templates/legacy/build-python-legacy.yml@templates` | `pythonVersion: '3.9'`, `artifactName: 'risk-batch-legacy'` |

The template was inlined directly into the GHA workflow. No template parameters are needed in GHA — the values are resolved at migration time.

---

## 5. Step-by-Step Task Mapping

| # | ADO Task / Step | ADO Inputs | GHA Step | GHA Action / Command |
|---|---|---|---|---|
| 1 | `UsePythonVersion@0` | `versionSpec: 3.9` | Set up Python 3.9 | `actions/setup-python@v5` with `python-version: 3.9` |
| 2 | `script` (Install dependencies) | `pip install -r requirements.txt` | Install dependencies | `run: python -m pip install --upgrade pip && pip install -r requirements.txt` |
| 3 | `script` (Run tests) | `python -m unittest discover -s tests -p "test_*.py" -v` | Run tests (unittest) | `run: python -m unittest discover -s tests -p "test_*.py" -v 2>&1 \| tee test-output.txt` |
| 4 | `script` (Build package) | `python setup.py sdist bdist_wheel` | Build package | `run: python setup.py sdist bdist_wheel` |
| 5 | `PublishBuildArtifacts@1` | `pathToPublish: dist/`, `artifactName: risk-batch-legacy` | Upload build artifacts | `actions/upload-artifact@v4` with `name: risk-batch-legacy`, `path: dist/` |

---

## 6. Variable Mapping

| ADO Variable / Source | GHA Equivalent |
|---|---|
| Template parameter `pythonVersion: '3.9'` | `env.PYTHON_VERSION: '3.9'` |
| Template parameter `artifactName: 'risk-batch-legacy'` | `env.ARTIFACT_NAME: 'risk-batch-legacy'` |

No ADO-specific variables (e.g., `BUILD_SOURCEBRANCH`) are referenced directly by this pipeline or its template. No env var shims are required.

---

## 7. Variable Groups / Secrets

The ADO pipeline is linked to variable group `shared-ci-secrets` (ID 201) which provides:

| Variable | Secret? | GHA Equivalent | Needed? |
|---|---|---|---|
| `PIP_INDEX_URL` | No | `secrets.PIP_INDEX_URL` or repository variable | **Possibly** — only needed if `requirements.txt` uses a private PyPI index |
| `NUGET_FEED_URL` | No | — | No (not a Python dependency) |
| `NUGET_API_KEY` | Yes | — | No |
| `NPM_REGISTRY` | No | — | No |
| `NPM_TOKEN` | Yes | — | No |

### Secrets Required in GitHub

If the `requirements.txt` file references a private package index:
- **`PIP_INDEX_URL`** — configure as a repository secret and add to the `Install dependencies` step:
  ```yaml
  env:
    PIP_INDEX_URL: ${{ secrets.PIP_INDEX_URL }}
  ```

If not (public PyPI only), no secrets are required.

---

## 8. Integration Points

| Integration | ADO Behavior | GHA Behavior |
|---|---|---|
| Artifactory registration | Not present in this pipeline | Not applicable |
| D2 notifications | Not present in this pipeline | Not applicable |
| Compliance attestation | Not present in this pipeline | Not applicable |

This is a minimal legacy build pipeline with no release stages or integration points.

---

## 9. Known Gaps & Behavioral Differences

| Gap | Description | Severity |
|---|---|---|
| **Ubuntu version change** | ADO used `ubuntu-20.04` (EOL). GHA uses `ubuntu-latest`. May affect system-level dependencies if any. | Low |
| **Test result reporting** | ADO does not use `PublishTestResults@2` in this template (results piped to `test-output.txt` only). GHA preserves this behavior. No native test tab in either platform for this pipeline. | Low — pre-existing |
| **Linting disabled** | The FROZEN `legacy/master-support` branch had linting disabled. This is preserved in the GHA migration (no lint step). | Low — pre-existing |
| **`setup.py` build** | Uses `python setup.py sdist bdist_wheel` which is deprecated in favor of `python -m build`. Preserved as-is to maintain behavioral parity. | Low — pre-existing |
| **No push trigger** | ADO had `trigger: none`. GHA adds `workflow_dispatch` + `pull_request` but no `push` trigger. Downstream jobs that triggered this pipeline in ADO will need a new trigger mechanism (e.g., `workflow_dispatch` via API). | Medium — operational |

---

## 10. Helper Scripts

No helper scripts from `build-tools/scripts/` are referenced by this pipeline or its template. No script updates are required.

---

## 11. Risk Flags (from Inventory Report)

- **FROZEN branch** (`legacy/master-support`): Template source is frozen and will not receive updates
- **Python 3.8 (EOL)**: Branch default is 3.8, but this pipeline overrides to 3.9
- **Linting disabled**: No lint step in the legacy template
- **Very low activity**: Only 2 runs in the last 90 days
- **Legacy build tooling**: Uses `setup.py` instead of modern `pyproject.toml` / `python -m build`
