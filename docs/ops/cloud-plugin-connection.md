# VANTRE Procurement 续期与网页交接包

本次只同步既有插件的技能/引用文档与版本，不新增业务功能。采购源码基线为 main `c4c5cfa5c0b30c57e9365d1ad5671f3e690b4800`；网站能力以已合并 main [2c02a645032754e0d690ae56ad6f8e4daa09fe58](https://github.com/hx123321/vantreCombB2B/commit/2c02a645032754e0d690ae56ad6f8e4daa09fe58) 为准，包含 refresh（#285，`c3573e6e4018353f45bc165e5a0781866b94513a`）与隔离网页 SSO（#284，审核 head `df50f47d4809770e959664dfc716217d0dffaf0f`）。

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

### 网页 SSO 等待最终官网接口

已合并的初版 [网页实现](https://github.com/hx123321/vantreCombB2B/blob/2c02a645032754e0d690ae56ad6f8e4daa09fe58/docs/design/procurement-browser-sso.md) 只支持独立只读采购页，不能以委托身份进入完整 `/track/*`、`/account/*`。用户已明确需要直接打开现有官网页面；父任务正在另一个 PR 补官网委托认证。因此初版只读专页不是最终产品方向，也不作为本次最终发布包。SSO 使用章节须等最终真实代码/schema 后定稿，不推测跳转、参数或权限。

当前默认关闭不变；TEST 安全配置与真实用户 `me:web` 新同意未完成。精确客户端名单、API/browser origins、代理、宿主浏览器能力、现账户业务 scopes 等仍由父任务核实。普通登录、插件授权与委托凭据必须保持隔离，不提取令牌、不嵌入长令牌 URL、不覆盖普通登录、不用其它账户回落，也不能以网页 scope 扩大业务权限。

## 打包与父任务更新

以下为最终 SSO 定稿后的既有打包命令；本 Draft 不生成可发布包。结构校验可用临时 archive，不能用于账号更新：

```bash
python3 scripts/package_plugin.py --output /tmp/vantrecomb-procurement-cloud-bound-0.1.3.zip --app-overlay-output /tmp/vantrecomb-test-skills-overlay-1.0.2.zip
```

完整源包单根 `vantrecomb-procurement-plugin/`，有 portable/兼容 manifests、真实 App 绑定、技能及品牌资源。目标更新包单根 `dev-6acc06a725048191bbf860d0b7a72642/`，仅有原兼容 manifest 与完整原技能/支持文件，不含 root manifest、.app.json、MCP 配置、品牌资源或凭据。它是定向 overlay，不能单独安装或 create_plugin。ZIP 不入 Git；可从本次精确 head 重建。

父任务先合并/审核最终官网委托认证，并补齐本 Draft 的 SSO 使用章节、复核真实 schema，再重建 release-ready overlay。版本 1.0.2 / 0.1.3 当前仅为准备值，不表示已保存或可发布。然后用 get_plugin_files 重新读取目标当前 release。若 release 变化，先重新核对/协调内容，再以新观察值作 `expected_release_id` 更新同一 `plugin_id`，不直接复用过时 guard。仅上传 App overlay，`delete_paths` 留空，保留所有未上传 App-owned 文件。保存后回读 manifest/技能及真实 .app.json，确认版本与原身份/连接/范围保留。用户重新激活不等同于获得 refresh 或 `me:web`，仍需授权页新同意。

## 验证范围

只做文档契约核对、manifest/引用、身份与 App 绑定保留、既有打包器和 ZIP 结构校验。没有逐文件 hash/匹配流程、复杂验证框架、真实 OAuth、业务写入或真实账户读取。既有 read 与 write 仍按现账户权限、用户授权、scope/归属、确认、幂等、业务验证和 CAPTCHA 执行；不额外封禁授权写入，也不为 SSO 扩权限。

本任务返回独立 Draft PR、精确 head 和包源码/重建命令。最终 SSO 使用说明及可发布更新包等待官网后续 PR，未自行合并、账号更新、发布或部署。
