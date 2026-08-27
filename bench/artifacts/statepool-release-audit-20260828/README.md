# StatePool Cloud v0.1.0 remote release audit — 2026-08-28

## Classification

Release-candidate verification executed on `WZU_Server` against source commit
`126cf6fd56ad752f3d3c5a7176c28bd7994238ec`. No Rust command was executed on
the local workstation.

## Results

- `cargo fmt --all -- --check`: passed;
- `cargo test --workspace --all-targets --locked`: 23 passed, 2 environment-gated
  PostgreSQL/S3 tests ignored (their real container runs are archived separately);
- `cargo clippy --workspace --all-targets --locked -- -D warnings`: passed;
- `cargo build --workspace --release --locked`: passed;
- Python: Ruff passed, 22 pytest tests passed, contracts/deploy checks passed,
  sdist and wheel built;
- Docker Compose config, Helm lint and both Helm render profiles: passed.

The server-state record includes binary/package checksums and final cleanup:
no GPU compute process, no matching StatePool test container, k3s uninstalled.
Existing durable PostgreSQL/S3, OCI smoke, GPU and Kubernetes proofs remain in
the linked evidence register; this audit is a release regression, not a rerun
of every hardware experiment.

## Files

- `remote-cargo-*.txt`: exact remote Rust command output;
- `remote-python.txt`: remote Python/package checks;
- `remote-deploy.txt`: remote Compose/Helm validation;
- `server-state.txt`: toolchain, hardware, build hashes and cleanup state;
- `control-plane-cleanup.txt`: test container removal;
- `manifest.json`, `SHA256SUMS`: audit metadata and integrity.
