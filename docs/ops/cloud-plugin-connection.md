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

## 本次 GPT 3D 源码已核对的候选

已读取网站 [Draft #287](https://github.com/hx123321/vantreCombB2B/pull/287)，head `601162ba431f1bfddf93efbce24b0b84fdfb73b9`，实际 private_design_tools/保存/Logo/RFQ handlers、原网站预览宿主页及 [契约文档](https://github.com/hx123321/vantreCombB2B/blob/601162ba431f1bfddf93efbce24b0b84fdfb73b9/docs/design/gpt-private-design-contract.md)；读取其依赖 Product3DPipeline [Draft #67](https://github.com/hx123321/Product3DPipeline/pull/67)，head `c92f18749a3395d2aac107a42441672edddc694e` 的源码 worker 契约。两 PR 仍待独审/合并，不声明已部署/已验。

- capabilities 从 exact ERP绑定与正式包取得 `snapshot`、TypeScript投影的 `snapshot_schema`、中文 `field_table`、recipe/parameterShape/rules、`packaging_rules` 和 `customer_upload_policy`。字段/范围不复制第二套表，空数组/可选/全部客户高级参数均保留。ERP审核/开发检查器、客户矢量/浮雕上传不开放，factory-review意图不当成批准。
- create/update `payload` 均必填 sku/base_version/完整snapshot/原requirements/mode；create base_version=0，update当前版本，top-level id选择旧设计，SKU/template不能移动。list仅摘要，历史 query.version 仅read。所有写必填幂等key；同数据重试保留key，改数据换key，409幂等冲突与版本冲突区分，422按实际fields纠正，不用默认替换非法值。
- Logo 必填 top-level design_id 和 idempotency_key，官方 file 可选，内必填 download_url/file_id，mime_type/file_name可选。无附件/入口未启用返回 upload_mode=website 与同设计 website_upload_entry（edit）；不是成功上传。静态 PNG/JPEG/WebP、512KiB/2048边长与decoded检查按实际policy；private canonical resource需放到合法完整snapshot并另保存。临时URL/fileID不存入设计，无泛化任意URL。精确HTTPS443 hostname名单默认空，仍未批准/真实宿主验收。
- 保存返回私有账户 preview_url=/designs/preview?design_id=…&version=…，历史版本固定；网页普通session与资产归属控制，原Studio INIT恢复，新网页保存产生私有版本供AI读取，第二设备须同账户认证。链接不自动为聊天iframe，聊天MCP Apps UI后补；保存/预览不自动询价、不覆盖ERP/旧报价。
- submit_design_rfq 使用read scope加buyer_confirmed=true、idempotency_key与正version/quantity/对应用户contact.email；原报价事务冻结设计版本/原要求/图像，保留私有草稿及普通报价夹。不增RFQ write scope、不把read scope当成无确认写授权。

浏览器正向仍未通过：原customer Studio CSP阻止Draco Wasm与blob纹理，READY/INIT/customized ACK/加载进度不等于RENDERED。`PROCUREMENT_DESIGN_STUDIO_CSP_ENABLED` 默认false；候选仅 `/3d/studio/customer/index.html` 增 script wasm-unsafe-eval 和 connect blob:，保留其它指令与精确origin/framing；需核清后具体批准与重新正向验证，不由技能打开、不写成已验。

`me:designs:read` / `me:designs:write`、`PROCUREMENT_DESIGNS_ENABLED`、Studio CSP及`PROCUREMENT_DESIGN_ATTACHMENT_HOSTS`精确来源仍待具体批准。旧grant不自动获得，真实consent由用户完成。ERP授权页独立修复不属于本插件文档变更，不能借此扩大范围。

## 父任务最终核对与验证边界

本次已按两个候选真实 schema/契约核对。独审修正及最终合并 head 返回后再复核差异，具体feature/scopes/CSP/附件host批准后再决定必要版本和包；当前不发布插件。分别记录代码合并、TEST启用部署、宿主工具可见、真实附件/预览/UI验收，不把某一成功扩大为其余成功。账号更新仍使用同一插件/App、原 USER / PRIVATE 范围，审核前不得上传；届时重新读取当前 release，不能只复用此处观察值。

本 Draft 只做文档内容/引用及差异范围检查，不写测试框架、复杂流程、逐文件匹配/hash清单；不重复其他项目测试，不调用设计写/上传/询价，不打包最终发布。Git 提交保留源码与技能同仓，原脚本/品牌/绑定/独立技能不变。
