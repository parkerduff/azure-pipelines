# risk-batch Legacy Pipeline — Migration Verification

## Source

- **ADO Pipeline**: `services/risk-batch/azure-pipelines-legacy.yml`
- **Template**: `templates/legacy/build-python-legacy.yml` (branch: `legacy/master-support`)
- **GH Actions Workflow**: `.github/workflows/risk-batch-ci.yml`

---

## Architecture Diagram

```
ADO Pipeline (Expanded)                       GitHub Actions Workflow
===================================           ===================================
services/risk-batch/                          .github/workflows/
  azure-pipelines-legacy.yml                    risk-batch-ci.yml

trigger: none                                 on:
pool: vmImage ubuntu-20.04                      workflow_dispatch: {}
                                                pull_request:
                                                  paths: [services/risk-batch/**]

stages:                                       jobs:
  - stage: Build                                legacy-build:
    jobs:                                         runs-on: ubuntu-20.04
      - job: legacy_build
        steps:                                    steps:
          (template expanded below)
                                                  +-------------------------------+
                                                  | Checkout repository           |
                                                  | (ADDED — GH Actions requires |
                                                  |  explicit checkout)           |
                                                  +-------------------------------+
          +-------------------------------+             |
          | UsePythonVersion@0            |       +-------------------------------+
          | versionSpec: '3.9'            | ----> | actions/setup-python@v5       |
          +-------------------------------+       | python-version: '3.9'         |
                    |                             +-------------------------------+
          +-------------------------------+             |
          | script: pip install --upgrade |       +-------------------------------+
          |   pip && pip install -r       | ----> | run: pip install --upgrade    |
          |   requirements.txt            |       |   pip && pip install -r       |
          +-------------------------------+       |   requirements.txt            |
                    |                             +-------------------------------+
          +-------------------------------+             |
          | script: python -m unittest    |       +-------------------------------+
          |   discover -s tests           | ----> | run: python -m unittest       |
          |   -p "test_*.py" -v           |       |   discover -s tests           |
          +-------------------------------+       |   -p "test_*.py" -v           |
                    |                             +-------------------------------+
          +-------------------------------+             |
          | script: python setup.py       |       +-------------------------------+
          |   sdist bdist_wheel           | ----> | run: python setup.py          |
          +-------------------------------+       |   sdist bdist_wheel           |
                    |                             +-------------------------------+
          +-------------------------------+             |
          | PublishBuildArtifacts@1        |       +-------------------------------+
          | pathToPublish: dist/          | ----> | actions/upload-artifact@v4    |
          | artifactName:                 |       | name: risk-batch-legacy       |
          |   risk-batch-legacy           |       | path: dist/                   |
          +-------------------------------+       +-------------------------------+
```

---

## Step-by-Step Comparison

| # | ADO Step (Template Expanded) | GH Actions Step | Verdict | Notes |
|---|------------------------------|-----------------|---------|-------|
| — | *(implicit checkout)* | `actions/checkout@v4` | ADDED | GH Actions requires explicit checkout; ADO auto-checks-out |
| 1 | `UsePythonVersion@0` (versionSpec: 3.9) | `actions/setup-python@v5` (python-version: 3.9) | MATCH | Direct equivalent |
| 2 | `script: pip install --upgrade pip && pip install -r requirements.txt` | `run: python -m pip install --upgrade pip && pip install -r requirements.txt` | MATCH | Identical commands |
| 3 | `script: python -m unittest discover -s tests -p "test_*.py" -v` | `run: python -m unittest discover -s tests -p "test_*.py" -v 2>&1 \| tee test-output.txt` | MATCH | Same command; tee preserved from template |
| 4 | `script: python setup.py sdist bdist_wheel` | `run: python setup.py sdist bdist_wheel` | MATCH | Identical command |
| 5 | `PublishBuildArtifacts@1` (dist/, risk-batch-legacy) | `actions/upload-artifact@v4` (dist/, risk-batch-legacy) | MATCH | Direct equivalent; artifact name preserved |

---

## Summary Scorecard

| Metric | Count |
|--------|-------|
| **Total ADO steps (template expanded)** | 5 |
| **Matched steps** | 5 |
| **Removed steps** | 0 |
| **Added steps** | 1 |
| **Total GH Actions steps** | 6 |

---

## Intentional Differences

| Difference | Justification |
|------------|---------------|
| **Added `actions/checkout@v4`** | GH Actions jobs do not auto-checkout the repo. ADO does this implicitly. Required for functional parity. |
| **Added `on.pull_request` trigger** | Standard GH Actions practice for CI validation on PRs. ADO pipeline had `trigger: none`. The `workflow_dispatch` trigger preserves the "triggered by downstream" behavior. |
| **Added `paths` filter on `pull_request`** | Scoped to `services/risk-batch/**` to avoid unnecessary runs. |
| **Runner: `ubuntu-20.04`** | Matches original ADO `vmImage: 'ubuntu-20.04'`. Note: Ubuntu 20.04 is reaching EOL on GitHub Actions runners — a future upgrade to `ubuntu-22.04` or `ubuntu-latest` is recommended. |

---

## Open Items Requiring Runtime Validation

| Item | Risk | Validation Approach |
|------|------|---------------------|
| **`requirements.txt` path** | Template uses bare `requirements.txt` — must exist at repo root or working directory | Verify file location in repo; may need path adjustment to `services/risk-batch/requirements.txt` |
| **`tests/` directory location** | `unittest discover -s tests` assumes `tests/` in working directory | Confirm `tests/` exists at repo root or adjust `-s` path |
| **`setup.py` location** | `python setup.py sdist` assumes `setup.py` in working directory | Confirm file exists at expected path |
| **Artifact contents parity** | `dist/` glob may resolve differently between ADO and GH Actions | Compare artifact contents from both pipelines during parallel-run period |
| **`ubuntu-20.04` runner availability** | GitHub is deprecating Ubuntu 20.04 runners | Monitor GH Actions runner deprecation notices; plan upgrade |
| **Downstream job trigger compatibility** | ADO downstream jobs trigger via ADO API; GH Actions requires `workflow_dispatch` API call | Downstream jobs must be updated to call GH Actions API instead of ADO API |
| **`tee test-output.txt` side effect** | Template pipes test output to `test-output.txt` but never publishes it | Non-functional; included for parity but file is ephemeral |

---

## build-tools/ Script Dependencies

**None.** The legacy template (`templates/legacy/build-python-legacy.yml`) does not invoke any `build-tools/` scripts. All steps are inline commands or ADO built-in tasks.

---

## Template Parameters (Resolved)

| Parameter | Default | Value Passed | Used In |
|-----------|---------|-------------|---------|
| `pythonVersion` | `'3.9'` | `'3.9'` | `UsePythonVersion@0` / `actions/setup-python@v5` |
| `requirementsFile` | `'requirements.txt'` | *(default)* | `pip install -r` step |
| `artifactName` | `'python-package'` | `'risk-batch-legacy'` | `PublishBuildArtifacts@1` / `actions/upload-artifact@v4` |
