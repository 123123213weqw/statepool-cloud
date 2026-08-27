# Compatibility matrix

StatePool Cloud is protocol-first: an entry is `runtime_verified` only when the
exact engine, model revision and hardware path has checked-in evidence.

| Component/profile | Version or identity | Status | Evidence / note |
|---|---|---|---|
| StatePool plugin API | `statepool-plugin.v1` | supported | JSON Schema/OpenAPI and Rust tests |
| Python Worker adapter | Python 3.10–3.12 | supported | pytest and container smoke |
| PostgreSQL | 17.6 | runtime verified | two-client Lease/CAS integration |
| MinIO / S3 API | `RELEASE.2025-04-22T22-12-26Z` | runtime verified | immutable object integration |
| Kubernetes/KEDA control plane | kind 0.30.0 / Kubernetes 1.34 / KEDA 2.20.1 | runtime verified with simulated Worker | not a GPU data-plane claim |
| Kubernetes GPU recovery | k3s 1.36.3+k3s1 / NVIDIA device plugin 0.19.3 / V100 | runtime verified, single node | `bench/artifacts/statepool-k3s-vllm-recovery-20260827/` |
| vLLM Qwen2.5 profile | vLLM 0.8.5.post1 / torch 2.6.0+cu124 / Qwen2.5-0.5B-Instruct@`7ae5576…` / V100 | runtime verified | `affinity_only`; transcript replay, not KV migration |
| Qwen3.5 candidate profile | operator supplied | candidate only | immutable revision and live evidence required |
| RWKV native State | RWKV-7 G1I 1.5B / RTX 4080 | process-loss restore verified | same physical GPU, fresh process; not cross-node |
| HAMi / AIBrix / KServe | external optional integrations | interface planned | no vendored source or compatibility claim |

## Compatibility rules

1. Native State restore requires exact `model_id`, immutable `revision`,
   `tokenizer` and `state_abi` equality.
2. OpenAI-compatible model support never implies portable KV-cache support.
3. Minor protocol additions must remain backward compatible for one minor
   release; breaking changes require a new contract version and migration ADR.
4. Upstream versions not listed above are unverified, not unsupported.
