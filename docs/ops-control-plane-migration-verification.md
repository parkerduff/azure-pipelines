# ops-control-plane: ADO → GitHub Actions Migration Verification

## Pipeline Classification

| Field             | Value                                        |
|-------------------|----------------------------------------------|
| Service           | ops-control-plane                            |
| Stack             | Go 1.22                                      |
| Template source   | CUSTOM (inline YAML — no shared templates)   |
| Owner             | platform-team                                |
| Pool              | vmImage: ubuntu-latest (hosted)              |
| Pipeline type     | Real CI/CD build                             |
| Stages            | 1 (Build)                                    |

## Architecture Diagram

```
ADO Pipeline                                  GitHub Actions Workflow
(services/ops-control-plane/                  (.github/workflows/
 azure-pipelines.yml)                          ops-control-plane-ci.yml)
─────────────────────────────                 ─────────────────────────────

trigger:                                      on:
  branches: [main]                              push:
  paths: [services/ops-control-plane/**]          branches: [main]
                                                  paths: [services/ops-control-plane/**]
                                                pull_request:        <── ADDED
                                                  branches: [main]
                                                  paths: [services/ops-control-plane/**]

pool: ubuntu-latest                           runs-on: ubuntu-latest

variables:                                    env:
  GOPATH: $(system.defaultWorkingDirectory)/go  GOPATH: ${{ github.workspace }}/go
  GOBIN: $(GOPATH)/bin                          GOBIN: ${{ github.workspace }}/go/bin
  modulePath: services/ops-control-plane        MODULE_PATH: services/ops-control-plane

stage: Build                                  job: build
├─ GoTool@0 (1.22)                            ├─ actions/checkout@v4     <── ADDED
├─ script: go mod download/verify             ├─ actions/setup-go@v5 (1.22)
├─ script: go vet ./...                       ├─ run: go mod download / go mod verify
├─ script: go test ./... -v                   ├─ run: go vet ./...
├─ script: go build -ldflags ...              ├─ run: go test ./... -v -coverprofile=coverage.out
└─ PublishBuildArtifacts@1                    ├─ run: mkdir staging dir  <── ADDED
                                              ├─ run: go build -ldflags ...
                                              └─ actions/upload-artifact@v4
```

## Step-by-Step Comparison

| # | ADO Step                                  | GH Actions Step                           | Verdict | Notes                                            |
|---|-------------------------------------------|-------------------------------------------|---------|--------------------------------------------------|
| — | (implicit)                                | actions/checkout@v4                       | ADDED   | GH Actions requires explicit checkout            |
| 1 | GoTool@0 (version: 1.22)                 | actions/setup-go@v5 (go-version: '1.22') | MATCH   | Direct equivalent                                |
| 2 | script: go mod download / go mod verify   | run: go mod download / go mod verify      | MATCH   | Same commands, same working directory             |
| 3 | script: go vet ./...                      | run: go vet ./...                         | MATCH   | Identical                                        |
| 4 | script: go test ./... -v -coverprofile    | run: go test ./... -v -coverprofile       | MATCH   | Identical flags and output                       |
| — | (implicit staging dir exists in ADO)      | run: mkdir -p staging                     | ADDED   | GH Actions needs explicit staging dir creation   |
| 5 | script: go build ... -o $(Build.Artifact..)| run: go build ... -o runner.temp/staging  | MATCH   | Output path mapped from ADO variable             |
| 6 | PublishBuildArtifacts@1                   | actions/upload-artifact@v4                | MATCH   | Artifact name preserved: ops-control-plane-binary|

## Summary Scorecard

| Metric            | Count |
|-------------------|-------|
| Total ADO steps   | 6     |
| Matched           | 6     |
| Removed           | 0     |
| Added             | 3     |

### Added Steps (Justification)

| Step                       | Reason                                                              |
|----------------------------|---------------------------------------------------------------------|
| actions/checkout@v4        | GH Actions jobs start with empty workspace; explicit checkout needed|
| on.pull_request trigger    | Standard GH Actions practice for CI validation on PRs              |
| mkdir staging directory    | ADO provides Build.ArtifactStagingDirectory automatically; GH Actions does not |

### Removed Steps

None. All ADO steps have a 1:1 equivalent in the GH Actions workflow.

## Intentional Differences

1. **Added `pull_request` trigger** — ADO pipeline only triggered on `push` to `main`. The GH Actions workflow adds `pull_request` targeting `main` with the same path filter. This is standard GH Actions practice to validate PRs before merge.

2. **Variable naming convention** — ADO uses `$(variableName)` syntax with camelCase; GH Actions uses `${{ env.VARIABLE_NAME }}` with UPPER_SNAKE_CASE (`modulePath` → `MODULE_PATH`).

3. **Staging directory creation** — ADO automatically provides `$(Build.ArtifactStagingDirectory)` as a pre-existing directory. In GH Actions, `${{ runner.temp }}/staging` must be explicitly created before writing the binary.

4. **No `NuGetToolInstaller` equivalent needed** — Not applicable for Go pipelines.

## Open Items Requiring Runtime Validation

| Item                           | Risk    | How to Validate                                             |
|--------------------------------|---------|-------------------------------------------------------------|
| Go module cache behavior       | Low     | Verify `setup-go@v5` caching works with `GOPATH` override  |
| Binary output path correctness | Low     | Run workflow and confirm artifact contains the binary       |
| Path filter glob matching      | Low     | ADO and GH Actions both support `**` globs similarly        |
| Artifact upload completeness   | Low     | Download artifact from GH Actions and compare to ADO output |
| `GOPATH`/`GOBIN` env vars      | Low     | Confirm `setup-go@v5` respects custom GOPATH set in env     |

## Third-Party Actions Used

| Action                        | Version | Pinned | Notes                              |
|-------------------------------|---------|--------|------------------------------------|
| actions/checkout              | v4      | Tag    | GitHub-maintained, widely trusted  |
| actions/setup-go              | v5      | Tag    | GitHub-maintained, widely trusted  |
| actions/upload-artifact       | v4      | Tag    | GitHub-maintained, widely trusted  |

All actions are first-party GitHub actions. No third-party actions are used.
