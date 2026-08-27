# StatePool Cloud

> 助手常驻，但 GPU 不必常驻。

StatePool Cloud 是面向长期运行 AI 助手的状态感知型本地、边缘与云端调度层。
它把会话状态的所有权和 GPU 进程解耦：请求到来时恢复状态并调度兼容
Worker；空闲时持久化状态并安全释放 GPU。

本仓库不实现新的模型推理引擎。它通过版本化 HTTP 合同接入
[rwkv-agent](https://github.com/123123213weqw/rwkv-agent)、vLLM 以及其他
OpenAI-compatible 服务，并复用 Kubernetes、KEDA、PostgreSQL、S3、
Prometheus 和 Grafana。

## 已实现

- Local / Edge / Cloud Worker 注册、心跳、Placement 与安全 Drain；
- Lease、CAS、fencing token 和提交状态不确定性保护；
- Hot / Warm / Cold State 生命周期；
- PostgreSQL 元数据和 S3/MinIO 不可变 State 对象；
- `native_export`、`affinity_only`、`replay_only` 三种能力模式；
- 独立 OpenAI/vLLM Worker Adapter；
- Compose、Helm、KEDA、Prometheus、Grafana 与 FinOps 回放；
- RWKV Worker 故障恢复和 Kubernetes 弹性证据。

## 仓库边界

| 仓库 | 职责 |
|---|---|
| `rwkv-agent` | 个人助手、RWKV Runtime、最小 State/插件客户端接口 |
| `statepool-cloud` | 云控制面、Worker Adapter、部署、基准和可观测性 |
| 上游推理服务 | vLLM、RWKV Runtime、SGLang、llama.cpp 等实际推理 |

两仓库只通过 [`contracts/`](contracts/) 中的稳定 API 和容器镜像连接，
不使用 Git submodule，也不复制上游推理引擎。

## 快速开始

```bash
docker compose -f deploy/statepool/compose.yaml up --build statepool
curl --fail http://127.0.0.1:8130/health
```

接入现有 OpenAI-compatible 服务：

```bash
export RWKV_STATEPOOL_URL=http://127.0.0.1:8130
export RWKV_WORKER_ID=vllm-local-01
export RWKV_WORKER_MODEL_ID=your-model
export RWKV_WORKER_MODEL_REVISION=immutable-revision
export RWKV_WORKER_TOKENIZER=immutable-tokenizer-revision
export RWKV_WORKER_STATE_ABI=context-replay.v1
export RWKV_OPENAI_UPSTREAM_URL=http://127.0.0.1:8000
export RWKV_OPENAI_UPSTREAM_MODEL=your-upstream-model
statepool-openai-worker
```

完整部署说明见 [`deploy/statepool/README.md`](deploy/statepool/README.md)，
协议见 [`contracts/statepool-plugin-v1.openapi.json`](contracts/statepool-plugin-v1.openapi.json)，
验证边界见 [`competition/evidence-register.md`](competition/evidence-register.md)。

## 开发验证

```bash
python -m pip install -e '.[dev]'
ruff check src tests scripts
pytest -q
python scripts/check_statepool_contracts.py
python scripts/check_statepool_deploy.py
```

Rust 编译和测试由 CI 或远程构建机完成。

## 治理

- License: MIT
- 贡献流程：[`CONTRIBUTING.md`](CONTRIBUTING.md)
- 治理：[`GOVERNANCE.md`](GOVERNANCE.md)
- 安全报告：[`SECURITY.md`](SECURITY.md)
- 路线图：[`ROADMAP.md`](ROADMAP.md)
- 维护者：[`MAINTAINERS.md`](MAINTAINERS.md)
- 第三方依赖：[`third_party/NOTICE.md`](third_party/NOTICE.md)

