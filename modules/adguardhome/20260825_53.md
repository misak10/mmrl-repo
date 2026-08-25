# Changelog

- 同步 AdGuard Home v0.107.79
- Sync with AdGuard Home v0.107.79
- 修复在重定向端口 53 前未等待 DNS 监听器的问题 (#77, by @Aliyerki)
- Wait for the DNS listener before redirecting port 53 (#77, by @Aliyerki)
- 修复拒绝 IPv6 DNS 而不是丢弃它的问题 (#78, by @Aliyerki)
- Reject IPv6 DNS instead of dropping it (#78, by @Aliyerki)
- 纠正 `debug.sh` 中的 ip6tables 命令
- Correct ip6tables command in `debug.sh`
- 注意此版本 `settings.conf` 新增了 startup_timeout 字段，若需要使用此字段请手动添加
- Note that the startup_timeout field has been added to `settings.conf` in this version, please add it manually if you need to use this field