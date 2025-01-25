## 去广告
#### [源地址：如果有帮助，请您支持我一下😘！](https://lingeringsound.github.io/10007)
#### [蓝奏云下载](https://keytoolazy.lanzn.com/b03j67j0f)，密码:`666`
#### [小米智能服务](https://keytoolazy.lanzn.com/b007t52m1i)，密码：`666`

- ***模块原理说明***
 > hosts拦截域名，host相当于一个本地的dns，理论上并不会影响网速，甚至还能加快(屏蔽了不需要的ip)节省流量，缺点就是不支持屏蔽二级域名和支持通配符。
 >> chattr +i 命令能够锁定文件不被删除/修改，能够有效屏蔽毒瘤的sdk写入上传信息。
 >>> iptables具体去百度一下，用法很多，目前我用来屏蔽某些网站的次级域名，补充一些host的不足。
 >>>> pm(cmd package)，安卓上通用的禁用应用组件方式，屏蔽不必要的流氓行为。

>v183
 - 记住有个SB叫[刺客边风](https://m.bilibili.com/space/21131684)！！！
>v238
 - 添加一个mount_hosts挂载hosts文件，源码在模块里，可以自己修改。
 > 配置文件在/data/adb/modules/GGAT_10007/mod/mount_hosts/配置包名.prop，会自动读取顶层应用包名挂载hosts
 >> 优点就是①自动放行需要添加的广告应用②游戏之类的，把广告奖励自己在配置文件改成`recovery`后，网络波动应该不大了(不玩游戏，自测)③ksu/Apatch应该不会检测到挂载，因为用了`mount --bind`，可以用`cat /proc/mounts | grep hosts`查看挂载情况。
 >>> 缺点是有点**卡顿**，用了`dumpsys`命令获取顶层应用，耗电自测，默认不开启。

