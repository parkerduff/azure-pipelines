# ops-control-plane-ci — ADO-to-GHA Migration Mapping

**Pipeline:** ops-control-plane-ci  
**ADO ID:** 109  
**Category:** 4 (Custom Inline — no shared templates)  
**Stack:** Go 1.22  
**Owner:** platform-team  
**Source YAML:** `services/ops-control-plane/azure-pipelines.yml`  
**GHA Workflow:** `.github/workflows/ops-control-plane-ci.yml`

---

## Trigger Mapping

| Aspect | ADO | GHA | Notes |
|---|---|---|---|
| Push branches | `main` | `main` | Direct mapping |
| Push paths | `services/ops-control-plane/**` | `services/ops-control-plane/**` | Direct mapping |
| PR trigger | *(none)* | `pull_request` on `main` with same path filter | **Intentional addition** — provides earlier CI feedback on PRs |

---

## Stage / Job Mapping

| ADO Stage | ADO Job | GHA Job | `needs:` | Notes |
|---|---|---|---|---|
| `Build` (`Build ops-control-plane`) | `build_go` (`Go build and test`) | `build` (`Build ops-control-plane`) | *(none)* | Single stage → single job |

---

## Step-by-Step Task Mapping

| # | ADO Step | ADO Task / Script | GHA Step | GHA Action / Command | Notes |
|---|---|---|---|---|---|
| 0 | *(implicit)* | *(auto-checkout)* | Checkout repository | `actions/checkout@v4` | ADO checks out automatically; GHA requires explicit checkout |
| 1 | Install Go 1.22 | `GoTool@0` (version: `1.22`) | Install Go 1.22 | `actions/setup-go@v5` (go-version: `1.22`) | Direct equivalent |
| 2 | Download modules | `script\|` block: `go mod download` / `go mod verify` | Download modules | `run\|` block: `go mod download` / `go mod verify` | Both use multiline block; failure on any line fails the step |
| 3 | Vet | `script: go vet ./...` | Vet | `run: go vet ./...` | Direct translation |
| 4 | Run tests | `script: go test ./... -v -coverprofile=coverage.out` | Run tests | `run: go test ./... -v -coverprofile=coverage.out` | Direct translation |
| 5 | Build binary | `script: CGO_ENABLED=0 ... go build ... -o $(Build.ArtifactStagingDirectory)/ops-control-plane ./cmd/server` | Build binary | `run: mkdir -p ... && CGO_ENABLED=0 ... go build ... -o ${{ runner.temp }}/staging/ops-control-plane ./cmd/server` | `$(Build.ArtifactStagingDirectory)` → `${{ runner.temp }}/staging`; added `mkdir -p` for fresh runner |
| 6 | Publish binary | `PublishBuildArtifacts@1` (artifactName: `ops-control-plane-binary`) | Publish binary | `actions/upload-artifact@v4` (name: `ops-control-plane-binary`) | Direct equivalent |

---

## Variable Mapping

| ADO Variable | ADO Value | GHA Variable | GHA Value | Notes |
|---|---|---|---|---|
| `GOPATH` | `$(system.defaultWorkingDirectory)/go` | `GOPATH` | `${{ github.workspace }}/go` | `system.defaultWorkingDirectory` → `github.workspace` |
| `GOBIN` | `$(GOPATH)/bin` | `GOBIN` | `${{ github.workspace }}/go/bin` | Resolved at workflow level |
| `modulePath` | `services/ops-control-plane` | `MODULE_PATH` | `services/ops-control-plane` | Renamed to SCREAMING_SNAKE for GHA env convention |

---

## Condition Mapping

No conditions are used in this pipeline — all steps run unconditionally.

---

## Integration Points

| Integration | ADO Behavior | GHA Behavior | Notes |
|---|---|---|---|
| Artifactory | Not used | Not used | Pipeline does not register artifacts externally |
| D2 notifications | Not used | Not used | No deployment stages |
| Compliance attestation | Not used | Not used | No attestation steps |
| Helper scripts | Not used | Not used | No `build-tools/scripts/` references |

---

## Known Gaps & Behavioral Differences

| # | Gap | Impact | Mitigation |
|---|---|---|---|
| 1 | ADO `PublishBuildArtifacts` publishes the entire staging directory; GHA `upload-artifact` publishes the staging directory path | Artifact structure may differ slightly for downstream consumers | Downstream tools must query GHA artifacts API instead of ADO |
| 2 | PR trigger added in GHA (not present in ADO) | More CI runs than ADO (runs on PRs too) | Intentional improvement — catches issues before merge |
| 3 | ADO `GoTool@0` vs GHA `actions/setup-go@v5` | Minor version resolution may differ | Both pin to `1.22`; GHA resolves latest patch within `1.22.x` |
| 4 | Custom `GOPATH` set under `github.workspace` | `actions/setup-go@v5` caching uses `GOPATH` for module cache; workspace is cleaned between runs | setup-go's Actions cache handles persistence; on-disk cache is ephemeral |

---

## Secrets Required

This workflow requires **no secrets** configured in GitHub repository settings. All steps use public actions and local build commands.

---

## Pre-Existing Issues

None identified. The ADO pipeline has no known issues (last result: succeeded, 25 runs in 90 days).

---

## Script Changes

No helper scripts in `build-tools/scripts/` are referenced by this pipeline. No script changes are required.
