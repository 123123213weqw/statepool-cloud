# Roadmap

## 0.1 — 可复现参赛版本

- 独立 StatePool 控制面和 Worker Adapter；
- RWKV native State 与 OpenAI/vLLM affinity 模式；
- Compose、Helm、KEDA、FinOps 和完整证据包；
- 固定 vLLM/Qwen2.5/V100 运行档案与单节点 k3s GPU Pod 故障恢复。

## 0.2 — 多集群

- Worker identity federation；
- 跨集群 State placement policy；
- GPU 成本和碳强度策略接口；
- KEDA 驱动的真实 GPU 0→1→N→0 与多节点重复实验。

## 0.3 — 稳定协议

- 插件合同兼容矩阵；
- 可插拔 metadata/object store；
- 多租户配额、审计和密钥轮换。
