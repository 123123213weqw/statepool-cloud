# Real Kubernetes GPU Pod recovery and live A/B/C — 2026-08-27

## Classification

**Live same-node, same-Deployment, same-model GPU Kubernetes evidence.** A
single-node k3s cluster advertised two Tesla V100 GPUs through NVIDIA Device
Plugin `v0.19.3`. The tested Deployment requested `nvidia.com/gpu: 1` and ran
vLLM beside the StatePool OpenAI adapter in one Pod.

## Stack

- k3s `v1.36.3+k3s1`, containerd `2.3.2-k3s2`;
- NVIDIA runtime + device plugin `v0.19.3`;
- Tesla V100-PCIE-32GB, driver 580.173.02;
- vLLM 0.8.5.post1 / PyTorch 2.6.0+cu124 / XFormers;
- `Qwen/Qwen2.5-0.5B-Instruct` at revision
  `7ae557604adf67be50417f59c2c2f167def9a775`;
- StatePool source commit `71ee1d1a13c04da28e897e2c4645c1e1697f0513`.

`gpu-smoke-nvidia-smi.txt` proves GPU visibility inside a real Pod;
`node-gpu-capacity.json` records Kubernetes capacity and allocatable resources.

## Forced Pod replacement

The first experiment force-deleted Pod
`statepool-vllm-d5449cdd6-rprsd` / Worker
`bdc987a9-a4e3-4ebb-8a83-37cd0dcfb5c0`. Deployment reconciliation created
`statepool-vllm-d5449cdd6-nntgg` / Worker
`0e85d4e3-4faa-444c-9d77-e548e9010a78`. Both containers became Ready after
40.565 seconds. A full transcript replay through a new StatePool plan returned
`CLOUD-2719`; `worker_replaced=true` and `transcript_replay_verified=true`.

## Live A/B/C recovery sample

Each scenario used the same Deployment, model revision, one requested V100 and
a two-turn dialogue with full transcript on turn two.

| Scenario | Policy | Ready after delete | Turn-two request | Plan | Worker replaced | Context |
|---|---|---:|---:|---:|---|---|
| A | sticky warm Worker, 10 s idle | 0 ms | 140.959 ms | 0 ms | no | `CLOUD-A2719` |
| B | direct stateless recycle | 39,924.086 ms | 594.176 ms | 0 ms | yes | `CLOUD-B2719` |
| C | StatePool-managed recycle | 39,085.117 ms | 597.921 ms | 0.911 ms | yes | `CLOUD-C2719` |

This is one measured sample per scenario, not a percentile study. The observed
cold-ready maximum, 39.924 seconds, is a break-even input: scale-to-zero saves
allocated GPU time only when avoided idle exceeds shutdown/startup overhead.
C adds exact-identity placement and stale-affinity failover; it does not claim
less model compute than B.

## Reproduce and audit

- `statepool-vllm-deployment.yaml`: exact Pod/sidecar manifest;
- `runtimeclass-nvidia.yaml`, `nvidia-device-plugin.yaml`;
- `live_abc_recovery_benchmark.py` and `live-abc-recovery-summary.json`;
- `before-failure.json`, `after-recovery.json`, Pod YAML and container logs;
- `kubernetes-events-final.txt`, NVIDIA telemetry and StatePool Worker views;
- `cleanup.txt`: Deployment removal, k3s uninstall and empty final GPU process
  list;
- `manifest.json` and `SHA256SUMS`.

## Claim boundary

The OpenAI/vLLM route is `affinity_only`. Dialogue continuity comes from full
client transcript replay; no portable Transformer KV cache was exported. This
does not prove KEDA 0→N GPU scaling, cross-node migration, production restore
P95, average GPU utilization, or cost savings. Native RWKV State
snapshot/restore remains a separate evidence path.
