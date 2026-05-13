# market-sim-ci — ADO to GitHub Actions Migration Mapping

**Pipeline:** market-sim-ci  
**ADO ID:** 108  
**Category:** 4 (Custom Inline — no shared templates)  
**Stack:** Rust  
**Owner:** team-quant  
**Source YAML:** `services/market-sim/azure-pipelines.yml`  
**GHA Workflow:** `.github/workflows/market-sim-ci.yml`

---

## Trigger Mapping

| Aspect | ADO | GHA | Notes |
|--------|-----|-----|-------|
| Push branches | `main` | `main` | Direct mapping |
| Path filter | `services/market-sim/**` | `services/market-sim/**` | Direct mapping |
| PR trigger | None | `pull_request` on `main` with same path filter | **Intentional addition** — provides earlier CI feedback on PRs |

---

## Stage → Job Mapping

| ADO Stage | GHA Job | Dependencies | Condition |
|-----------|---------|--------------|-----------|
| `Build` (displayName: "Build market-sim") | `build` | None | Always |
| `Deploy` (displayName: "Deploy market-sim") | `deploy` | `needs: build` | Push to `main` only (`github.event_name == 'push' && github.ref == 'refs/heads/main'`) |

---

## Task / Step Mapping

### Build Job

| # | ADO Step | GHA Step | Notes |
|---|----------|----------|-------|
| 1 | (implicit checkout) | `actions/checkout@v4` | Explicit in GHA |
| 2 | `script: curl ... rustup.rs` (Install Rust) | `dtolnay/rust-toolchain@stable` with `components: clippy` | Replaced curl-based install with official GHA action for caching, speed, and reliability |
| 3 | `script: cargo fetch` (Fetch dependencies) | `run: cargo fetch` | Direct mapping, `working-directory` preserved |
| 4 | `script: cargo clippy -- -D warnings` (Lint with clippy) | `run: cargo clippy -- -D warnings` | Direct mapping |
| 5 | `script: cargo build --release` (Build release binary) | `run: cargo build --release` | Direct mapping |
| 6 | `script: cargo test -- --test-threads=1` (Run tests) | `run: cargo test -- --test-threads=1` | Direct mapping |
| 7 | `script: cp target/release/market-sim $(Build.ArtifactStagingDirectory)/` (Stage binary) | `run: mkdir -p ... && cp ...` | Uses `${{ runner.temp }}/staging` instead of ADO staging dir; added `mkdir -p` for fresh runner |
| 8 | `PublishBuildArtifacts@1` (Publish market-sim binary) | `actions/upload-artifact@v4` | Artifact name preserved: `market-sim-binary` |

### Deploy Job

| # | ADO Step | GHA Step | Notes |
|---|----------|----------|-------|
| 1 | (implicit checkout) | `actions/checkout@v4` | Explicit in GHA |
| 2 | `script: echo "Deploying..."` (Deploy to cluster) | `run: echo "Deploying..."` | Direct mapping — placeholder deployment step |

---

## Variable Mapping

| ADO Variable | GHA Equivalent | Scope |
|---|---|---|
| `CARGO_TERM_COLOR: 'always'` | `env.CARGO_TERM_COLOR: always` | Top-level `env:` |
| `RUST_BACKTRACE: 1` | `env.RUST_BACKTRACE: 1` | Top-level `env:` |
| `$(Build.ArtifactStagingDirectory)` | `${{ runner.temp }}/staging` | Used in "Stage binary" step |
| `$(Build.SourceBranch)` | `${{ github.ref }}` | Used in deploy condition |

---

## Condition Mapping

| ADO Condition | GHA `if:` Expression |
|---|---|
| `and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))` | `github.event_name == 'push' && github.ref == 'refs/heads/main'` |

The GHA condition additionally checks `github.event_name == 'push'` to prevent deployment on pull_request events (which was not a concern in ADO since PR triggers were not configured).

---

## Integration Points

| Integration | ADO Behavior | GHA Behavior |
|---|---|---|
| Artifactory | Not used by this pipeline | N/A |
| D2 | Not used ("managed outside D2") | N/A |
| Attestation | Not used | N/A |

---

## Known Gaps & Behavioral Differences

| # | Gap | Impact | Notes |
|---|-----|--------|-------|
| 1 | Rust install method differs | Low | ADO used `rustup.sh` curl script; GHA uses `dtolnay/rust-toolchain` action. Functionally equivalent but faster in GHA due to action caching. |
| 2 | PR trigger added | Positive | ADO had no PR trigger; GHA adds `on.pull_request` for earlier feedback. This is intentional. |
| 3 | Deploy `environment` added | Low | GHA uses `environment: production` for protection rules. ADO did not use the `deployment` job type or environment approvals. Requires GHA environment to be configured in repo settings. |
| 4 | Test results not published to UI | Low | ADO had no `PublishTestResults` step either. Both rely on console output for test results. |

---

## Secrets Required

This pipeline does **not** require any secrets to be configured in the repository settings for the CI (build) job. The deploy job is currently a placeholder (`echo`) and will need secrets configured when real deployment logic is added.

---

## Helper Scripts

No helper scripts from `build-tools/scripts/` are referenced by this pipeline. No script updates required.
