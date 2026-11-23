# LibreTV to TVBox 自动同步订阅源

通过 GitHub Actions 每天 UTC 20:00（北京时间次日 04:00）自动拉取 [yifanwang-yet/libretv-sources.json](https://gist.github.com/yifanwang-yet/dbb7af044d90b5f51c1f32d0e0a200f6) 最新版本，并转换为 TVBox Desktop（`tvbox-desktop.json`）与标准 TVBox（`tvbox.json`）格式。

- **TVBox Desktop 订阅链接**：使用本仓库 `main` 分支中 `tvbox-desktop.json` 的 Raw 链接
- **标准 TVBox 订阅链接**：使用本仓库 `main` 分支中 `tvbox.json` 的 Raw 链接
