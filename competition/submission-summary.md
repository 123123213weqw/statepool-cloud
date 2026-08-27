# 报名摘要与评分映射

## 200 字摘要

RWKV State Agent 是一个本地优先、State 原生的个人助手。StatePool Cloud
Plugin 在不改变原默认行为的前提下，把长期 Agent recurrent State 变成可选
的云原生调度对象：本地电脑作为隐私根和边缘 Worker，云 GPU 作为弹性
Worker；控制面依据隐私、State 位置、模型/Tokenizer/State ABI、队列、SLO、
恢复代价和 GPU 价格做可解释 Placement。系统通过单写 Lease、单调 fencing
token、不可变 Snapshot、版本 CAS 和安全 Drain 防止双写；通过 KEDA、
Prometheus/Grafana、可选 HAMi/AIBrix 适配实现弹性与 FinOps。核心主张是：
**助手常驻，但 GPU 不必常驻。**

为避免把项目锁死在单一模型，Worker 契约同时定义 `replay_only`、
`affinity_only`、`native_export`：RWKV 走可迁移 recurrent State；现成
vLLM/OpenAI-compatible 上游通过可选 Adapter 接入，走 transcript replay 和
同 Worker cache hint，绝不把 Transformer KV 冒充可迁移 State。

## 痛点

长期个人 Agent 的请求稀疏但上下文有价值。Sticky Worker 让 GPU 在用户离开
时空转；Stateless re-prefill 虽可释放 Worker，却在用户回来时重复处理历史。
通用 GPU 调度器看见 Pod/GPU，通用推理平台看见请求/模型/KV cache，但通常
没有看见 owner-scoped、可版本化、可恢复的 RWKV recurrent State。

## 技术方案

```text
Local/Edge/Cloud Worker
    ↕ WorkerCapability + heartbeat + drain
StatePool Cloud Plugin
    ├─ explainable placement
    ├─ Session Lease + fencing + version CAS
    ├─ Hot / Warm / Cold State lifecycle
    ├─ State-aware demand and FinOps metrics
    └─ adapters: PostgreSQL / S3 / KEDA / AIBrix / HAMi
    ↕ versioned HTTP contract
rwkv-agent Controller (plugin disabled by default)
```

## 相对已有方案的创新（30%）

不是重做 Kubernetes、GPU 虚拟化或 LLM Gateway，而是补上长期 Agent State
这一层：

1. `model_id + revision + tokenizer + state_abi` 全等才迁移原始 State；
2. owner-scoped 单写 Lease + 单调 fencing token + version CAS；
3. Hot/Warm/Cold 与 restore cost 进入 Placement；
4. Drain 的安全条件包含在途请求为 0 且脏 State 明确为 0；
5. FinOps 统计 GPU-seconds、Prefill tokens avoided、State I/O、命中层级和
   分币种估算费用。
6. API/model support 与 State portability 分层声明；跨模型只能传 Transcript
   或 Context Capsule，不能迁移原始 State/KV。

## 场景落地（30%）

现有主仓库已有真实 RWKV Agent、Sidecar、多 Session State pool 和 AMD/V100
实验。本插件不是纸面新仓库：协议、服务、PostgreSQL/S3、部署镜像、Compose、
Helm、KEDA、ServiceMonitor、Dashboard 已进入同一仓库。RTX 4080 已完成
12,911,277 字节 State 的强杀进程、冷存、fresh Worker restore/continue/release；
kind/KEDA 已实测 0→1→3→0 和三个安全 preStop。

100 Session A/B/C 容量回放已按统一公式给出 GPU-hours、空闲分钟、Prefill、
State I/O 和估算费用，并在每行标记 `simulation_replay`。按公开假设，C 相比 A
减少 45.151% modeled GPU-hours，相比 B 避免 51,200 Prefill tokens。该结果不是
live 100 Session GPU benchmark，后续可用同协议实测替换。

独立 `rwkv-openai-worker` 已完成 fake-upstream 协议闭环、健康门、模型名映射、
StatePool 心跳、affinity header 和安全排空。另有一个固定运行档案：vLLM
0.8.5.post1、Qwen2.5-0.5B immutable revision 与 V100 已在 host 和单节点 k3s
GPU Pod 中运行；强制删 Pod 后 40.565 秒恢复 Ready，新 Worker 重放完整
transcript 得到正确结果。它严格属于 `affinity_only`，不算 KV 迁移认证。

同一 k3s Deployment、模型和 V100 级别还完成了 live A/B/C 单样本：Sticky
二轮 140.959 ms；Stateless recycle 冷启动 39.924 s、二轮 594.176 ms；
StatePool managed recycle 冷启动 39.085 s、二轮 597.921 ms，另加 0.911 ms
Placement plan。该组数据只证明路径可部署、可恢复、可测试，不替代三次重复、
P95、吞吐、GPU utilization 或真实账单实验。

## 开源治理（20%）

- 主仓库 MIT；第三方组件不 vendoring、不 Fork；
- `third_party/COMPONENTS.yaml` 记录许可证、版本、接入形式和状态；
- JSON Schema/OpenAPI 固化协议，兼容窗口写入 `COMPATIBILITY.md`；
- ADR、贡献指南、安全边界、治理规则、Issue/PR 模板和发布清单齐全；
- 上游只通过协议、镜像、Chart values、Adapter 接入。

## 长期发展（20%）

维护对象限定为 State/session contract、Placement、Lifecycle、FinOps 和适配器
接口，而非维护 Kubernetes/KEDA/HAMi/AIBrix Fork。Roadmap 以证据门槛推进：
LocalFS 单进程 → PostgreSQL/S3 Cloud Lite → 固定 vLLM/Qwen2.5/V100 实测 →
单节点真实 GPU Pod 恢复（均已完成）→ KEDA 驱动真实 GPU 0→N、多节点重复实验
→ 可选 AIBrix/HAMi 集成。

## 当前诚实边界

已经实现不等于可以扩大结论。PostgreSQL Lease/CAS、S3 adapter、RTX 4080
Worker 进程强杀恢复、kind/KEDA 0→1→3→0、单节点 k3s V100 Pod 替换均有原始
证据，但用途不同：RWKV GPU 实验是同一物理卡 sequential fresh process；
kind/KEDA 是非 GPU 协议 Worker 仿真；k3s 实验是真 GPU Pod，但未由 KEDA
触发、未跨节点，Transformer 恢复靠 transcript replay。答辩不得把它们拼成
“KEDA GPU 跨节点 State/KV 迁移”，也不得把单样本或 SSH 隧道下的 S3 时延
写成生产 SLO。
