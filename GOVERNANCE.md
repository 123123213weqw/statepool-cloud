# Governance

StatePool Cloud 采用 maintainer-led 的公开治理模式。

- API、数据格式、存储语义和安全边界变更必须通过 PR 与 ADR。
- 至少一名维护者批准并且必需 CI 通过后方可合并。
- 性能和成本声明必须能追溯到 `evidence/` 或 `bench/artifacts/`。
- 发布由维护者签发 tag，并由 GitHub Actions 构建不可变制品。
- 当活跃维护者达到三人时，关键 API 变更改为两名维护者批准。

维护者和职责见 `MAINTAINERS.md`。

