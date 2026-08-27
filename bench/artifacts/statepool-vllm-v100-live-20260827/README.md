# Live vLLM + Qwen2.5 + V100 — 2026-08-27

## Classification

**Live single-node GPU integration evidence.** This bundle proves that the
standalone StatePool control plane and OpenAI Worker adapter selected and
proxied a real vLLM model server on a Tesla V100. It is not a throughput or
production-SLO benchmark.

## Frozen stack

- GPU: 2 × Tesla V100-PCIE-32GB; one GPU used by the server;
- driver: 580.173.02;
- vLLM: 0.8.5.post1, V0 engine, XFormers, eager execution;
- PyTorch: 2.6.0+cu124; Transformers: 4.51.3;
- model: `Qwen/Qwen2.5-0.5B-Instruct`;
- immutable model revision: `7ae557604adf67be50417f59c2c2f167def9a775`;
- State capability: `affinity_only`, `context-replay.v1`.

The model was downloaded on the server from the pinned revision. The weight
and tokenizer file checksums are in `model-files.sha256`.

## Results

Three direct vLLM requests returned the requested sentinel text in 645, 192 and
191 ms. StatePool then returned a `remote` plan for Worker `vllm-v100-01`; the
adapter response carried the same Worker ID and returned
`statepool-vllm-v100-ok` in 184.391 ms with 43 prompt and 11 completion tokens.

Primary files:

- `direct-completion-{1,2,3}.json` and `direct-elapsed-ms-{1,2,3}.txt`;
- `statepool/statepool-completion.json`;
- `statepool/workers.json` and `statepool/adapter-ready.json`;
- `vllm.log`, `versions.txt`, `nvidia-processes.csv`;
- `manifest.json` and `SHA256SUMS`.

## Claim boundary

This certifies one model/runtime/hardware profile and the adapter path. vLLM
owns its KV cache. StatePool advertises affinity and requires transcript replay;
this run does **not** prove portable KV snapshot/restore, multi-node throughput,
or a production latency percentile.
