# “智算云”赛道材料索引

项目名：**RWKV State Agent + StatePool Cloud Plugin**

统一叙事：

> 助手常驻，但 GPU 不必常驻；每个人长期拥有一个 AI 助手，而不需要长期占用一张 GPU。

本目录中的“已实现/已验证/待验证”必须和
[`docs/RELATED_WORK.md`](../docs/RELATED_WORK.md) 的 Claim Matrix 一致。

- [`submission-summary.md`](submission-summary.md)：报名摘要与评分映射；
- [`technical-whitepaper.md`](technical-whitepaper.md)：技术白皮书与证据边界；
- [`architecture.md`](architecture.md)：一页架构与创新边界；
- [`demo-script.md`](demo-script.md)：答辩演示脚本；
- [`presentation-outline.md`](presentation-outline.md)：12 页答辩 PPT 结构；
- [`evaluation-protocol.md`](evaluation-protocol.md)：A/B/C 可复现实验；
- [`evidence-register.md`](evidence-register.md)：实测、估算、待测证据台账。

当前代码和证据可以演示：默认关闭兼容、插件握手、Worker
注册/Placement、Lease/fencing、PostgreSQL/S3 Snapshot/Restore、旧 Lease
拒绝、RTX 4080 强杀进程后恢复续写、Drain admission、Prometheus 指标，以及
kind/KEDA 0→1→3→0。另有独立的 k3s 真实 GPU Pod 闭环：固定
vLLM 0.8.5.post1、Qwen2.5-0.5B immutable revision 和 V100，强制删除 Pod 后
40.565 秒恢复 Ready，并通过新 Worker 重放 transcript 得到正确结果。

100 Session A/B/C 仍是明确标注的仿真回放；同一 k3s Deployment 上另有
live A/B/C 单样本，用于证明三条恢复路径可运行，而不是 P95、吞吐或成本结论。
OpenAI-compatible 路线严格为 `affinity_only`，只重放 transcript，不宣称
Transformer KV cache 可迁移；kind/KEDA 非 GPU 控制面与 k3s GPU Pod 证据也
不得拼成已经完成 KEDA GPU 0→N。
