# 证据台账

| ID | 能力/结论 | 类型 | 当前状态 | 证据 |
|---|---|---|---|---|
| E01 | 插件关闭时不构造 HTTP Client并走原路径 | 自动测试 | 已验证 | `cloud_plugin::tests::disabled_plugin_never_builds_http_and_returns_original_local_path` |
| E02 | 完整 Workspace Rust 检查 | 远程命令 | 已验证 | WZU_Server `cargo check --workspace --all-targets`，2026-08-27，见 E23 bundle |
| E03 | Runtime 71、mock 17、plugin 15、API 8 等完整 Workspace 回归 | 远程测试 | 已验证 | `bench/artifacts/statepool-openai-worker-20260827/remote-cargo-test.txt` |
| E04 | StatePool lifecycle、wire、Lease、Worker drain 回归 | 远程测试 | 已验证 | 同 E03 |
| E05 | Snapshot/Restore bytes、checksum、CAS、stale fence | 自动测试 | 已验证 | `snapshot_restore_round_trip_uses_cas_checksum_and_fencing` |
| E06 | 两个容器目标 release build、live/metrics/help smoke | 远程容器 | 已验证 | `evidence/remote-container-smoke-2026-08-26.md` |
| E07 | JSON Schema/OpenAPI fixtures | 静态验证 | 已验证 | `scripts/check_statepool_contracts.py` |
| E08 | Compose/Helm/KEDA/Dashboard 结构 | 静态验证 | 已验证 | `scripts/check_statepool_deploy.py`、Helm 3.19 lint/template |
| E09 | 既有 RWKV AMD/V100/100-State 结果 | 历史实测 | 可复用，非云结果 | 主 README 与原 `bench/` evidence |
| E10 | live RWKV State export/import | RTX 4080 GPU 实测 | 已验证（同一物理 GPU、不同进程） | `bench/artifacts/statepool-4080-worker-kill-20260827/` |
| E11 | Worker kill→fresh compatible process→restore→continue | RTX 4080 GPU 故障实验 | 已验证 | `evidence/real-gpu-worker-kill-2026-08-27.md` |
| E12 | PostgreSQL distributed Lease/CAS | 双连接真实 17.6 容器集成测试 | 已验证 | `evidence/durable-adapters-2026-08-27.md` |
| E13 | S3/MinIO immutable Cold State | 真实 MinIO 容器集成测试 | 已验证 | `evidence/durable-adapters-2026-08-27.md` |
| E14 | KEDA 0→1→3→0 safe drain | kind/Kubernetes 控制面实测 | 已验证（协议 Worker 仿真，非 GPU Pod） | `bench/artifacts/statepool-keda-kind-20260827/` |
| E15 | A/B/C GPU-hours、空闲分钟、Prefill、State I/O 与估算成本 | 100 Session 仿真回放 | 已验证（非 live GPU benchmark） | `bench/artifacts/statepool-abc-replay-20260827/` |
| E16 | Albatross CPU snapshot→release→restore→continue | 自动测试 | 已验证 | `tests/test_state_runtime.py::test_safe_snapshot_release_restore_continue_roundtrip`、`crates/state-runtime/tests/rwkv_http.rs` |
| E17 | V100/4080 远程环境与模型可用性探测 | 环境清单，非性能证据 | 已记录 | `evidence/gpu-environment-probe-2026-08-26.md` |
| E18 | Cloud Lite PostgreSQL+MinIO 跨插件重启恢复 | 真实 Compose 服务闭环 | 已验证（通用 State bytes，非 GPU） | `evidence/cloud-lite-compose-restart-2026-08-27.txt` |
| E19 | Worker 注册/心跳/排空意图与安全停止 | 跨进程控制面实测 | 已验证（非 GPU、非 Kubernetes） | `evidence/worker-adapter-2026-08-27.md` |
| E20 | Controller 自动 acquire→continue→snapshot→commit→release→restore | Rust mock 全路径测试 | 已验证（确定性 CPU/mock State，非 GPU） | `evidence/controller-lifecycle-2026-08-27.md`、`direct_chat_persists_releases_restores_and_advances_fenced_state` |
| E21 | 提交状态不确定时禁止自动重复执行 | 故障注入测试 | 已验证 | `evidence/controller-lifecycle-2026-08-27.md`、`uncertain_lifecycle_commit_blocks_automatic_double_execution` |
| E22 | Helm Controller/Worker/KEDA/多副本安全门 | Helm 3.19 + Compose 静态渲染 | 已验证（非 Kubernetes 实测） | `evidence/helm-controller-keda-2026-08-27.md` |
| E23 | OpenAI-compatible/vLLM Adapter、三种 State capability、affinity/drain | fake upstream + 远程 Rust/OCI/Helm 审计 | Adapter 协议与发布形态已验证 | `evidence/openai-worker-adapter-2026-08-27.md`、`bench/artifacts/statepool-openai-worker-20260827/` |
| E24 | 固定 Qwen2.5-0.5B revision 经 vLLM 0.8.5.post1 接入 StatePool | V100 host live inference | 已验证；`affinity_only`、完整 transcript replay | `bench/artifacts/statepool-vllm-v100-live-20260827/` |
| E25 | `nvidia.com/gpu: 1` Pod 强制删除后新 Pod/Worker 恢复并续写 | 单节点 k3s + NVIDIA device plugin + V100 | 已验证；40.565 s Ready，Worker UID 已替换，输出 `CLOUD-2719` | `bench/artifacts/statepool-k3s-vllm-recovery-20260827/` |
| E26 | Sticky / Stateless recycle / StatePool managed recycle 三路径 | 同一 k3s Deployment、模型与 V100 级别的 live 单样本 | 已验证可运行；分别 140.959 / 594.176 / 597.921 ms，冷启动约 39–40 s；不是 P95/成本/利用率结论 | `bench/artifacts/statepool-k3s-vllm-recovery-20260827/live-abc-recovery-summary.json` |
| E27 | v0.1.0 release regression | WZU_Server 远程 Rust/Python/Helm/Compose 审计 | 23 Rust + 22 Python tests，fmt/clippy/release build/package/render 全通过；服务器已清理 | `bench/artifacts/statepool-release-audit-20260828/` |

规则：临时 `/tmp` 日志不算发布证据；正式提交前需要把去敏后的完整输出放入
`bench/artifacts/`，填写 commit 和 checksum。
