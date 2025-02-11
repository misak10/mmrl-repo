## v7.2.2
- 从**v6**版本起，强烈建议**卸载重装**以获取最优体验，并**注意备份**好所需**数据**，建议更新！
- 整体细节优化增强
- 降低性能开销
- 新增 **Zash** 面板，可自行切换
- 配置文件重构(config.yaml)
   - 简洁高效
   - 便于维护
   - 支持多订阅、地区分类、负载均衡等...
- 临近搬砖，后续可能不再维护，祝大家开工大吉！
- [Windows版本](https://github.com/MoGuangYu/Surfing/releases/tag/Windows)

## v6.8.17
- 策略组节点分类
- 优化安装脚本提取订阅地址并插入新配置
  - 适用于使用默认配置的
- 祝大家新年快乐！

## v6.8.16
- 添加：UpdateScript.sh 同步最新提交
- 支持：WiFi / SSID 控制服务启停(box.config)
- 优化：安装逻辑提取并备份订阅地址 
- 默认使用透明代理

## v6.8.15
- Update the configuration file (config.yaml)
- SyncUpstrea Updates
  - Provides legacy Clash DNS forwarding compatibility for Mihomo transparent proxy
  - Fix local IP backflow prevention rules
  - Fix Mihomo DNS forwarding condition judgment error
  - Add USB tethering to the default ap_list

## v6.8.14
- 追随上游更新
  - 优化本机 IP 获取
  - 添加动态防回环规则插入支持
  - 修复 Singbox 的 Tun 热点分享
- 更新：Toolbox v9.0
- 更新：Clash 配置实例
  - 尝试降低内存使用

## v6.8.13
- 修复：首次安装无法启动 Inotify 进程
- 更新：Toolbox v5.0
  - 支持在线检测更新高度自定义版本控制
  - 优化操作逻辑
  - 基本已经完善...
- 此外将减少模块更新发布频率
- 开启养老模式

## v6.8.12
- Fix：更新模块时开关控制失效
- Update：首次安装无需重启设备
- Update：自此后续更新不再包含
  - Geo数据库
  - bin文件
  - Web资源
- Add：Toolbox v3.0
  - 重载配置
  - 清空数据库缓存
  - 更新 Web 面板
  - 更新 Apps 路由规则
  - 更新 Clash 核心
  - 进入 Telegram 频道
  - Web 面板访问入口
  - 整合 Magisk 更新状态
  - 更新 Surfing 模块
  - 禁止/启用 更新模块
- 开启模块时日志输出至文件夹路径 .xx/log
- 更新后如发打不开面板 脚本执行一下更新即可恢复
- 其它调整...

## v6.8.6
- More detailed diversion and WeChat FCM support
- Fix：sing tun hotspot
- Add：Telegram chat.sh
- Chore：add ipv6 tun forward support
- Chore：Configuration Optimization
- Update：Meta panel v1.141.1
- Update：Meta amd64 v1.18.6

## v6.8.5
- 支持 Mihomo of Clash
- 增加对 Hysteria 的支持
- 增加对 Kernelsu 快捷打开 Webui 管理接口
- Fix Hysteria 透明代理不应劫持 DNS
- Fix iptables 标记时使用或掩码，以避免更改 OEM 标记

## v6.8.4
- Fix config.yaml
- Update：amd64-v1.18.5 Metacore

## v6.8.3
- 修复应用进程感知
- 修复本地流量环路
- 修复 fakeip ICMP
- 修复应用程序不存在，导致expr输入意外结束
- 支持 APatch
- Update：amd64-v1.18.4 Metacore

## v6.8.2
- 同步最新分支
- Update Clash.Meta Core@v1.18.1
- 双 Web 面板 可在 config.yaml 切换
- 最后一版

## v6.8.1
- Update: Clash.Meta Core@v1.17.0
- 嫌加载外网慢的，把 DNS 的 fallback 删除

## v6.8.0
- Fix DNS
- Update Yacd@v0.3.7
- Update Clash.Meta Core@v1.16.0

## v6.7.9
- 启用域名嗅探，禁用 Tun 模式
- 优化 DNS 配置，节点使用体验直速上升
- 大陆绕行无感访问（推荐）
- 新增 country.mmdb 数据库文件
- 更新 UpdateGeo.sh 脚本同步新增数据库更新链接
- 应用分流增加中国抖音
- 部分应用分流规则调整为本机进程匹配，为以下应用
  - 网易音乐
  - 国际抖音
  - 中国抖音

## v6.7.8
- 拒绝本地链路回环，从而导致出现大量连接引发路由崩溃
- 移除动态更新，更新时默认备份 config.yaml、box.config 文件可自行选择重新配置合并，至原始路径
  - /data/adb/box_bll/clash/config.yaml.bak
  - /data/adb/box_bll/scripts/box.config.bak

## v6.7.7
- ~~启用 tun 高性能的透明代理，提升网络性能及隐私保护~~
  - 如非特殊要求，使用无意义
  - 已禁用

## v6.7.6
- ~~动态更新配置文件~~
  - ~~模块更新时，如 Clash.Meta 配置文件或用户配置文件无更新时则保留原始文件，如更新时则原路径备份原始文件，后缀为.bak~~
- 模块不再包含 Geo 数据库文件更新
- 新增一键更新 Geo 数据库脚本
  - /data/adb/box_bll/clash/
  - UpdateGeo.sh

## v6.7.5
- 修复模块更新后，模块开关控制失效
- ~~优化模块更新时，如 Clash.Meta 配置文件无更新时则保留原始文件~~
- 更新 Geo 数据库_Released on 202308262207

## v6.7.4
- 更贴切的使用体验
- 优化 Clash.Meta 配置文件
- 更新 Geo 数据库_Released on 202308252208

## v6.7.3
- 修复 APP 黑白名单匹配与 UID 计算
- 修复 v2fly/xray 核心 geo* 文件位置错误
- 优化 Clash.Meta 配置
- 支持 GID 黑白名单
- 更新 Geo 数据库_Released on 202308232208
- 新增 ClashM 核 v1.15.1
- 已基于全部最新跟进.

---

## Box4Magisk 更新日志

### v4.7
- 修复 APP 黑白名单匹配与 UID 计算
- 修复 v2fly/xray 核心 geo* 文件位置错误
- 修复 Clash.Meta 配置中的拼写错误
- 支持 GID 黑白名单

### v4.6
- 修复白名单未生效的错误
- 修复 Magisk 控制启停时黑白名单未获取的错误
- 更新部分核心示例配置
  - 修复 Clash.Meta 配置中的拼写错误
  - sing-box 使用 any 出站规则匹配出站服务器域名解析

### v4.5
- 添加 Box 核心 CPU 使用率显示
- 添加 KernelSU 安装支持
- 更新部分核心示例配置
  - Clash.Meta 的 DNS / 策略组配置
  - sing-box 的 fakedns / Proxy Providers 配置

### v4.4
- 修复因包名重复导致的 UID 错误
- 修复白名单 clash DNS 流量重定向
- 添加 xray 透明代理配置示例
- 移除路由表禁用 IPv6
- 优化 Box 服务启动脚本
  - 添加 Box 内核内存占用显示
  - 添加 Box 内核运行时间显示
  - 添加 Magisk Busybox 至 PATH
  - 增强 Box 服务存活检查

### v4.3
- 修复黑白名单打印错误
- 添加部分日志输出

### v4.2
- 修复初次安装环境缺失无法启动的错误
- 添加初次安装免重启可使用 Magisk Manager 启停控制
- 优化 libcap 使用时机
  - 增强 Box 用户用户组合法性检查
  - 添加 libcap 使用前判断

### v4.1
- 修复日志打印，重定向输出时不再输出颜色
- 修复透明代理前 Box 服务检查
- 修复 Magisk Manager 启停控制
- 添加通过路由表禁用 IPv6
- 添加启用/禁用 IPv6 命令参数
- 添加白名单默认透明代理 DNS

### v4.0
- 支持启动时检测本地 IP 并绕过透明代理
- 修复日志打印错误
- 修复 Box 用户检查
- 添加日志颜色输出

### v3.9
- 支持安卓多用户黑白名单
- 移除默认 libcap 安装
- 优化安装脚本
  - 备份用户 Box 服务配置
  - 增量更新用户 Box 服务配置

### v3.8
- 修复自定义用户用户组获取
- 修复 Magisk Manager 无法禁用透明代理的错误

### v3.7
- 支持自定义用户用户组启动 Box 服务
- 支持可选代理 USB 网络共享
- 修复 clash DNS 拦截
- 默认删除三天前日志

### v3.6
- 支持 IPv6 tproxy 透明代理
- 修复 Magisk Manager 更新日志显示错误
- 优化 box.config 配置定义
  - `network_mode` 改为 `proxy_method`

### v3.5
- 修复 TUN 设备检查
- 修复模块安装脚本

### v3.4
- 支持 Magisk 模块在线更新
- 修复 shell 解释器兼容
- 修复模块安装脚本

### v3.3
- 修复非 TUN 模式的启动
- 优化 Box 服务启动脚本
  - if 改为 case

### v3.2
- 修复 TUN 模式的热点代理

### v3.1
- 修复 DNS 拦截错误

### v3.0
- 支持透明代理黑白名单
- 支持仅启动核心模式（用来支持 TUN）
- 支持 REDIRECT 透明代理（可与 TUN 共用即混合模式代理）
- 修复内核状态与权限检查
- 修复局域网 DNS 拦截
- 添加 TPROXY 兼容性检查
- 添加 clash 内核日志
- 添加 Magisk Lite 版本适配
- 添加 README.md
- 添加模块构建脚本并使用 GitHub Action 自动发布版本
- 更新防回环规则
- 更新配置示例

### v2.0
- 支持开机启动，Magisk Manager 管理服务启停
- ~~支持 yq 修改用户配置~~
- 支持 sing-box，clash，xray，v2fly 的 TPROXY 透明代理
- 支持可选代理 WiFi 或热点
- 添加 sing-box，clash 透明代理配置示例
- 默认禁用 IPv6
- 初始版本