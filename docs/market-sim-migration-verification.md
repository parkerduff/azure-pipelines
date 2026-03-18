# market-sim Migration Verification

> **Source**: `services/market-sim/azure-pipelines.yml`
> **Target**: `.github/workflows/market-sim-ci.yml`
> **Stack**: Rust (stable toolchain)
> **Template source**: CUSTOM (inline YAML — no shared templates)

---

## Architecture Diagram

```
ADO Pipeline (Expanded)                  GitHub Actions Workflow
================================         ================================

trigger:                                 on:
  branches: [main]                         push:
  paths: [services/market-sim/**]            branches: [main]
                                             paths: [services/market-sim/**]
                                           pull_request:           <-- ADDED
                                             branches: [main]
                                             paths: [services/market-sim/**]

variables:                               env:
  CARGO_TERM_COLOR: always                 CARGO_TERM_COLOR: always
  RUST_BACKTRACE: 1                        RUST_BACKTRACE: 1

stage: Build                             jobs:
 job: build_rust                           build:
 ┌────────────────────────────────┐        ┌────────────────────────────────┐
 │                                │        │ Checkout repository     ADDED  │
 │ Install Rust (curl rustup.rs)  │───────>│ Install Rust (dtolnay/        │
 │                                │        │   rust-toolchain@stable)       │
 │                                │        │ Cache dependencies      ADDED  │
 │                                │        │   (Swatinem/rust-cache@v2)     │
 │ cargo fetch                    │───────>│ cargo fetch                    │
 │ cargo clippy -- -D warnings    │───────>│ cargo clippy -- -D warnings    │
 │ cargo build --release          │───────>│ cargo build --release          │
 │ cargo test -- --test-threads=1 │───────>│ cargo test -- --test-threads=1 │
 │ cp binary to staging dir       │───────>│ mkdir + cp to staging dir      │
 │ PublishBuildArtifacts@1        │───────>│ actions/upload-artifact@v4     │
 └────────────────────────────────┘        └────────────────────────────────┘
           │                                          │
           ▼                                          ▼
stage: Deploy                              deploy:
  dependsOn: Build                           needs: build
  condition: main branch only                if: main && push
 ┌────────────────────────────────┐        ┌────────────────────────────────┐
 │ echo "Deploying..."            │───────>│ echo "Deploying..."            │
 │ echo "managed outside          │───────>│ echo "managed outside          │
 │   release-orchestrator"        │        │   release-orchestrator"        │
 └────────────────────────────────┘        └────────────────────────────────┘
```

---

## Step-by-Step Comparison

| # | ADO Step | GH Actions Step | Verdict |
|---|----------|-----------------|---------|
| — | *(implicit checkout)* | `actions/checkout@v4` | **ADDED** — GHA requires explicit checkout |
| 1 | Install Rust via `curl rustup.rs` | `dtolnay/rust-toolchain@stable` with `clippy` component | **MATCH** — idiomatic GHA equivalent |
| — | *(no caching)* | `Swatinem/rust-cache@v2` | **ADDED** — performance optimization |
| 2 | `cargo fetch` | `cargo fetch` | **MATCH** — identical |
| 3 | `cargo clippy -- -D warnings` | `cargo clippy -- -D warnings` | **MATCH** — identical |
| 4 | `cargo build --release` | `cargo build --release` | **MATCH** — identical |
| 5 | `cargo test -- --test-threads=1` | `cargo test -- --test-threads=1` | **MATCH** — identical |
| 6 | `cp target/release/market-sim $(Build.ArtifactStagingDirectory)/` | `mkdir -p ${{ runner.temp }}/staging && cp ...` | **MATCH** — equivalent staging directory |
| 7 | `PublishBuildArtifacts@1` (artifact: `market-sim-binary`) | `actions/upload-artifact@v4` (name: `market-sim-binary`) | **MATCH** — equivalent artifact publish |
| 8 | Deploy stage: echo placeholder | Deploy job: echo placeholder | **MATCH** — identical behavior |

---

## Summary Scorecard

| Metric | Count |
|--------|-------|
| **Total ADO steps** | 8 (6 build + 1 publish + 1 deploy) |
| **Matched steps** | 8 |
| **Removed steps** | 0 |
| **Added steps** | 3 (see below) |

### Added Steps (justification)

| Step | Justification |
|------|---------------|
| `actions/checkout@v4` | GitHub Actions requires explicit checkout (implicit in ADO) |
| `dtolnay/rust-toolchain@stable` | Replaces manual curl-based install; idiomatic GHA approach |
| `Swatinem/rust-cache@v2` | Performance optimization; reduces build times by caching `~/.cargo` and `target/` |

### Removed Steps (justification)

None. All ADO steps have a direct equivalent in the GH Actions workflow.

---

## Intentional Differences

| Difference | Reason |
|-----------|--------|
| `on.pull_request` trigger added | Standard GHA practice for CI validation on PRs; ADO pipeline only triggered on push |
| Rust installed via `dtolnay/rust-toolchain` action | Replaces manual curl-based install; more reliable, cacheable, and idiomatic for GHA |
| Dependency caching via `Swatinem/rust-cache@v2` | Performance improvement; not available in ADO pipeline |
| Explicit `actions/checkout@v4` | Required by GHA; ADO checks out automatically |
| Staging dir uses `${{ runner.temp }}/staging` | Maps `$(Build.ArtifactStagingDirectory)` to GHA equivalent |
| Deploy job condition uses `github.event_name == 'push'` | Prevents deploy from running on PR builds (preserves ADO's main-branch-only condition) |

---

## Open Items Requiring Runtime Validation

| Item | Notes |
|------|-------|
| Binary artifact parity | Confirm `market-sim` binary is present and correctly named in the uploaded artifact |
| Cargo.toml / workspace layout | Confirm `services/market-sim/` contains a valid Rust project with expected binary target |
| Clippy warnings | Confirm same set of warnings/errors on GHA runner as on ADO hosted agent |
| Test count parity | Compare test counts between ADO and GHA runs |
| Deploy stage placeholder | No real deployment logic — purely echo statements; confirm this is intentional |
| `Swatinem/rust-cache@v2` | Third-party action — verify against org policy for pinning / allowlisting |
| `dtolnay/rust-toolchain@stable` | Third-party action — verify against org policy for pinning / allowlisting |

---

## Template & Build-Tools Dependencies

**Templates referenced**: None (fully inline pipeline)
**Build-tools scripts referenced**: None
**ADO environment variables used**: `$(Build.ArtifactStagingDirectory)` only (mapped to `${{ runner.temp }}/staging`)
