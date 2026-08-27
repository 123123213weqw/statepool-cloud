# Releasing

1. 更新版本、CHANGELOG 和证据台账。
2. 确认 `main` CI 全绿。
3. 创建 `vX.Y.Z` annotated tag 并推送。
4. Release workflow 构建 Python wheel、Rust 二进制 checksum 和 OCI 镜像。
5. GitHub Release 只引用由 CI 生成的制品。

