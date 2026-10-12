# VANTRE Procurement 当前连接事实与 GPT 3D 技能准备

本次从采购插件仓库已合 main `080e8791a6414ce6905c68d5cac24b4755384466`（PR #2）继续，仅提交新的技能/引用文档 Draft。实际私有 App 插件已经更新 1.0.2；本次不更新账号插件，不改 manifest/版本/账户配置，不构建最终发布包，不合并、启用设计开关或生成真实 grant。

## 当前身份与已验证事实

| 字段 | 当前已读取值 |
| --- | --- |
| 插件 ID | `plugin_asdk_app_6acc06a725048191bbf860d0b7a72642` |
| App ID | `asdk_app_6acc06a725048191bbf860d0b7a72642` |
| 原 mapping key / 包名 | `dev-6acc06a725048191bbf860d0b7a72642` |
| 账号版本 / scope / 可见性 | 1.0.2 / USER / PRIVATE |
| 已观察 release | `pluginrel_6acc3f84f9948191823420f4f948f165` |

真实 .app.json、App-owned 连接/展示/权限/受众、兼容 manifest、全部已有技能/辅助脚本及根部独立技能均保留。另一独立技能插件 `plugins_6ac5698a6b9c8191b317d7b2e5d8bcfe` 不在本次更新范围。当前仓库完整源包版本仍为 0.1.3，目标 App overlay manifest 仍为 1.0.2；这次候选文档不会借相同版本覆盖已安装包。

父任务已核实：TEST API `https://test-api.vantrecomb.com` 与网站 `https://test.vantrecomb.com` 两端部署完成；采购客户 profile 真实可读；一次宿主自动 refresh 已对上数据库轮换时间。本任务不重复读取客户数据/令牌。当前具体部署 SHA 和真实时间值未在本次委托中提供，不编造。上次“仍构建发布”的文字已过时，应由这些已确认事实替换。

网页登录工具目前服务端采购目录 20 项、宿主仍 19 项，待宿主工具 Refresh；这是此次观察，不是技能固定完整接口清单。工具缺失不能用手工 API 或另一个账户绕过。实际宿主网页 SSO、真实浏览器交接并未通过验收，不能把 profile 或一次 refresh 成功推为全功能通过。先检查宿主新暴露的 schema 与独立/无痕浏览器能力。

## 保留续期与网页登录语义

网站合并 main [b91ff92416b74f2ab9649cbdbff5535dab784f8e](https://github.com/hx123321/vantreCombB2B/commit/b91ff92416b74f2ab9649cbdbff5535dab784f8e) 已包含 refresh 与正常网站交接。插件 OAuth access 15 分钟；明确“保持连接”同意后每次成功刷新轮换续 30 天闲置，活跃无固定总期限，可撤销、正常数据库支持的重启保存。宿主处理续期和安全存储，AI 不提取/记录/兑换令牌；旧 grant 不自动升级，旧 metadata 缓存可能需重建连接。

`me:web:login` 明确同意完整账户正常网站权限、期限及退出；旧 `me:web` 不满足且不能管理 PATCH 升级。交接须独立/无痕上下文，无法建立/开页/点击/读 DOM 时停止；不覆盖普通登录/其它账户。prepare 固定入口 → 原页新 challenge → 同 MCP authorization bind → 原标签一次 complete，完成后原官网原功能。正常网页登录 30 分钟 access、30 天 refresh 及原续期/logout；插件撤销仅阻止新交接，不注销既有网页登录。网站退出/过期而插件仍授权可取新票据，不重复 consent、不重放旧票据。相同账户正常 refresh 可经服务端成功确认复用；异账户/身份不确定时不覆盖。

正常网站权限不等于 AI 有任意写业务授权，每个动作仍按用户有效授权、所需确认及原业务规则；插件 API scopes 保持各自限制。原独立上下文 SSO 指导与动态工具发现保持。源码默认关闭/空名单与已配置 TEST 状态区分；不通过技能修改部署配置或授予 scope。

## 本次 GPT 3D 文档候选

核心网站/3D WIP 由父任务协调，最终核心 PR 尚未交付。本 Draft 在 packaged SKILL 中加入入口，并新增 `references/gpt-design-workflow.md`。它按父任务候选整理，不声称已审、已合并、已部署或真实宿主可用：

- 先工具/Logo上传/已有私有预览链接，后续 MCP Apps UI 才提供聊天内嵌控件；链接不自动成为 iframe。
- `design_capabilities(query.sku)` 应直接返回官方客户 JSON 规则、完整默认 v2 snapshot 和中文字段类型/范围说明；技能由响应生成解释，不复制第二套参数 JSON/能力表。要求完整当前客户高级参数覆盖，不仅基础；ERP审核/内部配置及客户禁用矢量/浮雕上传不开放。
- `one_sentence` / `guided` 两模式共享完整参数能力；同一 design ID 重复修改，客户网页改动后先读当前版本。create/update 使用完整 snapshot、sku、requirements、mode 与实际 schema；update 用观察到的 base_version，不猜初始版本。
- `422 fields` 按实际字段反馈纠正；`409 design_version_conflict` 读最新再合并授权 delta，冲突同字段问客户，不强制覆盖或循环重试。
- Logo 候选必填 design_id，官方 openai/fileParams 附件能力/HTTPS精确来源待核；无附件时用工具实际返回的同设计网页上传入口，随后读回。不能泛化任意URL，不能声称真实聊天附件上传已验。
- preview_url 对应设计/版本的私有原预览页。保存/预览不自动询价、不覆盖ERP方案或旧报价；submit_design_rfq 必须指定确切设计版本、数量/联系数据和用户明确确认，沿用现报价业务。

`me:designs:read` / `me:designs:write` 与 TEST 设计开关仍待父任务具体批准；旧 grant 不自动获得，真实 consent 由用户完成。文件参数注解、允许来源、工具参数/结果名、完整参数覆盖和版本语义须在最终核心代码/schema 下核对。本文没有猜测实际附件、URL来源或核心部署SHA。

## 父任务最终核对与验证边界

最终核心 PR 到达后，以真实工具 schema、权威 JSON/验证器与机制文档核对候选，再决定必要版本更新和包准备。分别记录代码合并、TEST启用部署、宿主工具可见、真实附件/预览/UI验收，不把某一成功扩大为其余成功。账号更新仍使用同一插件/App、原 USER / PRIVATE 范围，审核前不得上传；届时重新读取当前 release，不能只复用此处观察值。

本 Draft 只做文档内容/引用及差异范围检查，不写测试框架、复杂流程、逐文件匹配/hash清单；不重复其他项目测试，不调用设计写/上传/询价，不打包最终发布。Git 提交保留源码与技能同仓，原脚本/品牌/绑定/独立技能不变。
