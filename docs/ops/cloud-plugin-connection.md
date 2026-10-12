# VANTRE Procurement 续期与网页交接包

本次只同步既有插件的技能/引用文档与版本，不新增业务功能。采购源码基线为 main `c4c5cfa5c0b30c57e9365d1ad5671f3e690b4800`。OAuth refresh 已合并于网站 main [2c02a645032754e0d690ae56ad6f8e4daa09fe58](https://github.com/hx123321/vantreCombB2B/commit/2c02a645032754e0d690ae56ad6f8e4daa09fe58)；正常网页登录交接说明依据 [Draft PR #286](https://github.com/hx123321/vantreCombB2B/pull/286) 的实际候选 head `1929a9969abb8850e48d3f1d2a8c38899554a058`。PR286 正在最终独审，尚未合并/部署；父任务后续补最终 merge/deploy SHA，再定稿包。

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

### 正常官网 SSO 候选说明（PR286 最终独审中）

已读取候选的 [真实工具 schema/实现](https://github.com/hx123321/vantreCombB2B/blob/1929a9969abb8850e48d3f1d2a8c38899554a058/backend/cmd/server/procurement_browser.go) 和 [机制文档](https://github.com/hx123321/vantreCombB2B/blob/1929a9969abb8850e48d3f1d2a8c38899554a058/docs/design/procurement-browser-sso.md)。新 scope 为 `me:web:login`，明确同意完整账户的正常网站权限、期限、续期与撤销边界。旧 `me:web` 不满足新工具，不能自动或通过管理 PATCH 升级；必须用户本人真实 OAuth 同意。插件 API scopes 保持原限制，网站 session 使用原账户正常权限与对象归属；AI 每个业务动作仍按有效用户授权、原安全确认和业务校验执行，不以登录代替业务授权。

技能必须要求独立/无痕浏览器上下文，不能只另开共享用户原上下文的标签，也不能借用已有其它账户的原上下文。无法建立独立上下文或开页/点击/读 DOM 时停止并告知；不清凭据、不退出用户、不静默覆盖。独立上下文中已核实同账户有效登录可直接进入原官网；重复交接沿用同账户有效 access/refresh 登录而不改凭据。有效异账户 access、refresh-only 或在途 refresh lineage 均不能静默覆盖，须换新独立上下文；过期 refresh 重放不是有效登录。

`open_procurement_browser` prepare 的可选 target 仍仅 `home/profile/quotes/orders/shipments/folder`，默认原官网首页；locale 默认 en。固定 browser_url 无 token/flow/密码，私有 flow_id 留在原 MCP；原标签 Begin 生成新 `#challenge` → 同 MCP authorization/access reference bind → 原标签 Continue 原子单次 complete，随即进入原官网目标及原功能。禁止任意 URL/redirect/path、聊天/外页 challenge 和 AI 手动搬运任何凭据。prepare 120 秒、challenge 90 秒限制交接票据，不限制完成后的普通网站期限；旧/已消费票据不能重放。

完成后复用正常持久化网站 session：网站短 access 30 分钟、普通 refresh 30 天，沿用普通轮换/idle/退出，与手动登录一致。网站退出/过期后插件仍授权时可取新票据重新交接，无需重复 consent。撤销插件阻止新的 prepare/bind/complete，不注销已建立的普通网站 session 或阻止其正常 refresh；需要退出网页时使用独立上下文内正常 logout。网站退出不撤销插件 grant。

OAuth access/refresh 不进入网页/URL/JS/localStorage；网页仅通过原辅助函数取得普通网站短 access 与 refresh Cookie，由网站自己管理，不让 AI 提取/复制/记录/装入。旧逐页面委托、只读 JSON reader、第二套业务认证/下载及报价夹专用 scope 的使用指导已移除。普通原页面/表单/下载与权限完全沿现有业务链。

用户已明确确认上述语义，并批准两端 TEST 启用；批准不代表设置已部署。源码仍默认关闭、空 client 名单拒绝。父任务须确认最终 merge/deploy SHA、精确 MCP client 名单、TEST API/site origins、同源 rewrite、Cookie/Set-Cookie、Origin、`X-Vantre-Handoff` 与禁止缓存；真实用户 consent 留给本人完成。交接接口现为 `/api/v1/auth/procurement-browser/{begin,complete}`，使正常 refresh Cookie Path 可参与异账户校验；prepare/bind/complete 要求同实例，完成后普通 session 沿原持久化链。

候选精确 head 的两个真实 CI 已通过；原作者本地合成 HTTPS Chromium 与原页面功能验证通过。这些不是本任务真实业务操作，也不是实际 TEST/ChatGPT 宿主验收。当前文档先按候选提交，最终上线状态等待父任务证据，不更新账号插件。

## 打包与父任务更新

以下为最终 SSO 定稿后的既有打包命令；本 Draft 不生成可发布包。结构校验可用临时 archive，不能用于账号更新：

```bash
python3 scripts/package_plugin.py --output /tmp/vantrecomb-procurement-cloud-bound-0.1.3.zip --app-overlay-output /tmp/vantrecomb-test-skills-overlay-1.0.2.zip
```

完整源包单根 `vantrecomb-procurement-plugin/`，有 portable/兼容 manifests、真实 App 绑定、技能及品牌资源。目标更新包单根 `dev-6acc06a725048191bbf860d0b7a72642/`，仅有原兼容 manifest 与完整原技能/支持文件，不含 root manifest、.app.json、MCP 配置、品牌资源或凭据。它是定向 overlay，不能单独安装或 create_plugin。ZIP 不入 Git；可从本次精确 head 重建。

父任务最终审核/合并官网 PR286 后提供 merge/deploy SHA；核对最终 head 与本次正常网页登录候选章节/schema 一致，补齐真实状态后再重建 release-ready overlay。版本 1.0.2 / 0.1.3 当前仅为准备值，不表示已保存或可发布。然后用 get_plugin_files 重新读取目标当前 release。若 release 变化，先重新核对/协调内容，再以新观察值作 `expected_release_id` 更新同一 `plugin_id`，不直接复用过时 guard。仅上传 App overlay，`delete_paths` 留空，保留所有未上传 App-owned 文件。保存后回读 manifest/技能及真实 .app.json，确认版本与原身份/连接/范围保留。用户重新激活不等同于获得 refresh 或 `me:web:login`，仍需本人授权页新同意。

## 验证范围

只做文档契约核对、manifest/引用、身份与 App 绑定保留、既有打包器和 ZIP 结构校验。没有逐文件 hash/匹配流程、复杂验证框架、真实 OAuth、业务写入或真实账户读取。既有 read 与 write 仍按现账户权限、用户授权、scope/归属、确认、幂等、业务验证和 CAPTCHA 执行；不额外封禁授权写入，不通过管理旧 grant 冒充新的正常网页登录 consent。

本任务返回独立 Draft PR、精确 head 和包源码/重建命令。SSO 使用章节已按 PR286 正常登录候选 `1929a9969abb8850e48d3f1d2a8c38899554a058` 统一更新；最终 merge/deploy 状态及可发布包仍待父任务确认，未自行合并、账号更新、发布或部署。
