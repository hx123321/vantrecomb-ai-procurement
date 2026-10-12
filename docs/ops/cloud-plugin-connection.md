# VANTRE Procurement 续期与网页交接包

本次只同步既有插件的技能/引用文档与版本，不新增业务功能。采购源码基线为 main `c4c5cfa5c0b30c57e9365d1ad5671f3e690b4800`；网站能力以已合并 main [2c02a645032754e0d690ae56ad6f8e4daa09fe58](https://github.com/hx123321/vantreCombB2B/commit/2c02a645032754e0d690ae56ad6f8e4daa09fe58) 为准，包含 refresh（#285，`c3573e6e4018353f45bc165e5a0781866b94513a`）。原官网 SSO 使用说明依据尚在独立审核的 [Draft PR #286](https://github.com/hx123321/vantreCombB2B/pull/286)，head `b63417ebe1c0d2f6ceebdf175ee11946cd18b1dd`、base main `2c02a645032754e0d690ae56ad6f8e4daa09fe58`，不将其写成已合并或已部署。

## 本次目标与身份

| 字段 | 已读取当前值 |
| --- | --- |
| 目标插件 ID | `plugin_asdk_app_6acc06a725048191bbf860d0b7a72642` |
| 已观察 release guard | `pluginrel_6acc09cbf44081918621572c690ccc61` |
| 已观察版本 / 更新包版本 | 1.0.1 / 1.0.2 |
| 原 scope / 可见性 | USER / PRIVATE |
| 包名及 .app.json mapping key | `dev-6acc06a725048191bbf860d0b7a72642` |
| 实际 App ID | `asdk_app_6acc06a725048191bbf860d0b7a72642` |

本次只准备此 App-backed 私有插件的技能 overlay。其完整原兼容 manifest 位于 `overlays/vantrecomb-test/.codex-plugin/plugin.json`，仅提升版本，保留 `apps`、`skills`、App developer、VANTRE Procurement TEST、Other、空 capabilities、null defaultPrompt 及其它原字段。插件/App ID 不可互换。上传时不写 .app.json，不改 App-owned MCP/连接、展示、权限、受众或私人范围，不删除文件。

`plugins/vantrecomb-procurement-plugin/` 继续与技能共处本仓；可复用完整源包版本同步为 0.1.3，保留其原身份、品牌、默认提示和真实 App 绑定。该完整包不用于覆盖目标 App 插件，也不授权更新另一既有独立技能插件 `plugins_6ac5698a6b9c8191b317d7b2e5d8bcfe`。仓库根部独立 SKILL.md、references、agents 和本地客户端保持原样。

## 能力与线上状态

TEST API 是 `https://test-api.vantrecomb.com`，网站是 `https://test.vantrecomb.com`；`api.vantrecomb.com` 不是此次 TEST。此前真实云连接的资料读取证据仅覆盖合成注册账户，不能推导新 refresh、SSO 或完整业务均已验收。

代码合并与部署/启用分开：本任务未部署、未设置 TEST 配置、未生成真实 OAuth grant。父任务负责最终部署状态、代理/安全配置与真实宿主验收；用户随后重新激活并通过真实 OAuth 同意。技能依据实际工具、schema、采购 guide 与 metadata 动态发现，不把所有业务接口写成必然可用清单。

### 自动续期

[真实 refresh 说明](https://github.com/hx123321/vantreCombB2B/blob/2c02a645032754e0d690ae56ad6f8e4daa09fe58/docs/ops/procurement-oauth-refresh.md)：access 为 15 分钟；用户明确勾选“保持连接”并同意后，宿主串行刷新、安全保存轮换后的最新凭据。每次成功 refresh 续 30 天闲置，活跃无固定总期限，可在 API Tokens 页面撤销，正常数据库支持的服务重启保留状态。

旧 client/grant 不自动升级，需重新同意；宿主缓存旧 authcode-only metadata 或不能重新启动同意时，可能需移除并重建连接。强制终止、响应丢失或旧 refresh 重放可导致需要重连。不得教 AI 提取、记录、手动兑换令牌或另建刷新循环，不在包中放用户凭据。

### 原官网 SSO 使用说明（PR286 待审核）

已核查 [真实 schema](https://github.com/hx123321/vantreCombB2B/blob/b63417ebe1c0d2f6ceebdf175ee11946cd18b1dd/backend/cmd/server/procurement_browser.go)、身份/业务权限实现和 [机制文档](https://github.com/hx123321/vantreCombB2B/blob/b63417ebe1c0d2f6ceebdf175ee11946cd18b1dd/docs/design/procurement-browser-sso.md)。PR286 把交接页收敛为登录交接，完成后进入原官网页面，删除此前只读 JSON reader 与 data API；本技能不再指导使用只读专页。

宿主须创建全新独立浏览器上下文，保留用户原上下文普通登录；另开普通上下文标签不够。prepare 的可选 target 仅 `home/profile/quotes/orders/shipments/folder`，默认官网首页，可分别进入原资料、报价、订单、出货、报价夹。原页 Begin 生成 challenge → 原 MCP 同 authorization/access reference bind → 原标签 Continue 一次性 complete，再在同上下文继续官网导航。不能使用任意 URL/redirect、他人 challenge 或 AI 手工搬运 Cookie/令牌；已有普通 access/refresh Cookie 的上下文拒绝交接，不能退出或覆盖普通登录来绕过。

网页/插件的实际权限都是 OAuth scopes 与原账户/资源业务规则的交集；`me:web` 不扩大业务权限。原资料保存、报价回复/确认、下载等仍需对应 scope、有效用户授权和原业务校验。报价夹新增 `me:quote-folder:read/write`，旧 grant 不能自动或经管理 PATCH 扩大，须用户新同意；不推断报价夹新增 MCP 工具。登录/密码/API-token/grant 管理留在普通上下文。

prepare 120 秒、challenge 90 秒、委托最长十分钟且受原 access 到期限制，不滑动续期；宿主 OAuth refresh 不延长网页 TTL。公共标签 selector 不是 bearer credential，由官网自行管理；委托 Cookie、CSRF 与正常登录保持隔离。失效、撤销、混入普通凭据或标签重建时拒绝，不回落、不静默换身份。网页下载沿原按钮和单用途/IP/次数规则，且绑定临时委托会话，不能分享成永久匿名链接。

原作者已用本地合成账户/HTTPS Chromium 验证原界面保存、报价回复、订单/出货与权限隔离；这不是本任务的真实业务操作，也不代表真实 TEST/ChatGPT 宿主验收。PR286 仍为 Draft、未合并/部署，默认关闭与空名单不变。父任务负责复审后的最终 head、TEST 安全配置与真实用户 `me:web`／报价夹新 scopes 同意；包在最终审核/合并状态明确后定稿。

## 打包与父任务更新

以下为最终 SSO 定稿后的既有打包命令；本 Draft 不生成可发布包。结构校验可用临时 archive，不能用于账号更新：

```bash
python3 scripts/package_plugin.py --output /tmp/vantrecomb-procurement-cloud-bound-0.1.3.zip --app-overlay-output /tmp/vantrecomb-test-skills-overlay-1.0.2.zip
```

完整源包单根 `vantrecomb-procurement-plugin/`，有 portable/兼容 manifests、真实 App 绑定、技能及品牌资源。目标更新包单根 `dev-6acc06a725048191bbf860d0b7a72642/`，仅有原兼容 manifest 与完整原技能/支持文件，不含 root manifest、.app.json、MCP 配置、品牌资源或凭据。它是定向 overlay，不能单独安装或 create_plugin。ZIP 不入 Git；可从本次精确 head 重建。

父任务先审核/合并官网 PR286，核对最终 head 与本次已补齐的 SSO 章节/schema 是否一致；若后续修正接口，先同步文档，再重建 release-ready overlay。版本 1.0.2 / 0.1.3 当前仅为准备值，不表示已保存或可发布。然后用 get_plugin_files 重新读取目标当前 release。若 release 变化，先重新核对/协调内容，再以新观察值作 `expected_release_id` 更新同一 `plugin_id`，不直接复用过时 guard。仅上传 App overlay，`delete_paths` 留空，保留所有未上传 App-owned 文件。保存后回读 manifest/技能及真实 .app.json，确认版本与原身份/连接/范围保留。用户重新激活不等同于获得 refresh 或 `me:web`，仍需授权页新同意。

## 验证范围

只做文档契约核对、manifest/引用、身份与 App 绑定保留、既有打包器和 ZIP 结构校验。没有逐文件 hash/匹配流程、复杂验证框架、真实 OAuth、业务写入或真实账户读取。既有 read 与 write 仍按现账户权限、用户授权、scope/归属、确认、幂等、业务验证和 CAPTCHA 执行；不额外封禁授权写入，也不为 SSO 扩权限。

本任务返回独立 Draft PR、精确 head 和包源码/重建命令。SSO 使用章节已按 PR286 当前真实候选补齐；最终源码状态及可发布更新包仍等待复审合并，未自行合并、账号更新、发布或部署。
