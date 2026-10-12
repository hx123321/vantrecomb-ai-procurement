# VANTRE Procurement 当前连接事实与 GPT 3D 技能准备

本次从采购插件仓库已合 main `080e8791a6414ce6905c68d5cac24b4755384466`（PR #2）继续，准备技能源码及 1.0.3 私有审核 overlay。实际私有 App 仍为 1.0.2；本次只改技能/引用文档与包版本，不更新账号插件/账户配置，不合并本 PR、部署或生成真实 grant。

## 当前身份与已验证事实

| 字段 | 当前已读取值 |
| --- | --- |
| 插件 ID | `plugin_asdk_app_6acc06a725048191bbf860d0b7a72642` |
| App ID | `asdk_app_6acc06a725048191bbf860d0b7a72642` |
| 原 mapping key / 包名 | `dev-6acc06a725048191bbf860d0b7a72642` |
| 账号版本 / scope / 可见性 | 1.0.2 / USER / PRIVATE |
| 已观察 release | `pluginrel_6acc3f84f9948191823420f4f948f165` |

真实 .app.json、App-owned 连接/展示/权限/受众、兼容 manifest 版本以外的值、全部已有技能/辅助脚本及根部独立技能均保留。另一独立技能插件 `plugins_6ac5698a6b9c8191b317d7b2e5d8bcfe` 不在本次更新范围。本次目标 App overlay 版本准备为 1.0.3，可复用完整源包/兼容manifest同步为 0.1.4；均仅准备源码/审核包，实际账号插件仍1.0.2。

父任务已核实：此前采购SSO/refresh的 TEST API `https://test-api.vantrecomb.com` 与网站 `https://test.vantrecomb.com` 两端部署完成；新3D本轮TEST部署已安排但未完成。此前采购客户 profile 真实可读；一次宿主自动 refresh 已对上数据库轮换时间。本任务不重复读取客户数据/令牌。当前具体部署 SHA 和真实时间值未在本次委托中提供，不编造。上次“仍构建发布”的文字已过时，应由这些已确认事实替换。

此前观察网页登录工具服务端采购目录 20 项、宿主19项待Refresh；须以当前重新发现结果为准，这是先前连接验证观察，不是技能固定完整接口清单。工具缺失不能用手工 API 或另一个账户绕过。实际宿主网页 SSO、真实浏览器交接并未通过验收，不能把 profile 或一次 refresh 成功推为全功能通过。先检查宿主新暴露的 schema 与独立/无痕浏览器能力。

## 保留续期与网页登录语义

网站合并 main [b91ff92416b74f2ab9649cbdbff5535dab784f8e](https://github.com/hx123321/vantreCombB2B/commit/b91ff92416b74f2ab9649cbdbff5535dab784f8e) 已包含 refresh 与正常网站交接。插件 OAuth access 15 分钟；明确“保持连接”同意后每次成功刷新轮换续 30 天闲置，活跃无固定总期限，可撤销、正常数据库支持的重启保存。宿主处理续期和安全存储，AI 不提取/记录/兑换令牌；旧 grant 不自动升级，旧 metadata 缓存可能需重建连接。

`me:web:login` 明确同意完整账户正常网站权限、期限及退出；旧 `me:web` 不满足且不能管理 PATCH 升级。交接须独立/无痕上下文，无法建立/开页/点击/读 DOM 时停止；不覆盖普通登录/其它账户。prepare 固定入口 → 原页新 challenge → 同 MCP authorization bind → 原标签一次 complete，完成后原官网原功能。正常网页登录 30 分钟 access、30 天 refresh 及原续期/logout；插件撤销仅阻止新交接，不注销既有网页登录。网站退出/过期而插件仍授权可取新票据，不重复 consent、不重放旧票据。相同账户正常 refresh 可经服务端成功确认复用；异账户/身份不确定时不覆盖。

正常网站权限不等于 AI 有任意写业务授权，每个动作仍按用户有效授权、所需确认及原业务规则；插件 API scopes 保持各自限制。原独立上下文 SSO 指导与动态工具发现保持。源码默认关闭/空名单与已配置 TEST 状态区分；不通过技能修改部署配置或授予 scope。

## 本次 GPT 3D 正式合并源码

已读取网站 [已合 #287](https://github.com/hx123321/vantreCombB2B/pull/287)，main `7f0a2b2eab3a0cf0a26dd7f69e7165d09e69fec9`，实际 private_design_tools/保存/Logo/RFQ handlers、原网站预览宿主页及 [契约文档](https://github.com/hx123321/vantreCombB2B/blob/7f0a2b2eab3a0cf0a26dd7f69e7165d09e69fec9/docs/design/gpt-private-design-contract.md)；读取其依赖 Product3DPipeline [已合 #67](https://github.com/hx123321/Product3DPipeline/pull/67)，main `1814e48c35dc86ef552599247a6f40f57cfcad7c` 的源码 worker 契约。两PR已独审GO并合并；本轮新3D TEST部署未完成，不声明上线或真实GPT/file/高级Blender/聊天UI已验。

- capabilities 从 exact ERP绑定与正式包取得 `snapshot`、TypeScript投影的 `snapshot_schema`、中文 `field_table`（唯一path、中文类型/单位/默认/required/范围/step/组合引用）、producer recipe_design_default、recipe/parameterShape/rules、`packaging_rules` 和 `customer_upload_policy`。字段/范围不复制第二套表，空数组/可选/全部客户高级参数均保留。ERP审核/开发检查器、客户矢量/浮雕上传不开放，factory-review意图不当成批准。
- create/update `payload` 均必填 sku/base_version/完整snapshot/原requirements/mode；create base_version=0，update当前版本，top-level id选择旧设计，SKU/template不能移动。list仅摘要，历史 query.version 仅read。所有写必填幂等key；同数据重试保留key，改数据换key，409幂等冲突与版本冲突区分，422按实际fields纠正，不用默认替换非法值。深层schema拒未知资源/高级字段；原高级range与包装resolver/承印面组合继续验证，packaging review_range之外是需审核意图，不虚构硬边界。最终尺寸检查从正式配方基线与dimensionRange导出，错误可定位extensions.photoRecipe.parameters.dimensionsMm.length；有无design都不能以两字段同时改绕过，带design须与原compiler输出尺寸一致。
- Logo 必填 top-level design_id 和 idempotency_key，官方 file 可选，内必填 download_url/file_id，mime_type/file_name可选。无附件/入口未启用返回 upload_mode=website 与同设计 website_upload_entry（edit）；不是成功上传。静态 PNG/JPEG/WebP、512KiB/2048边长与decoded检查按实际policy；private canonical resource需放到合法完整snapshot并另保存。临时URL/fileID不存入设计，无泛化任意URL。成功持久receipt在临时URL下载前返回；同design/fileID/MIME/name/key的过期URL或host换新URL可恢复，变更文件身份用旧key冲突，不确定成功不能另换key造重复上传。精确HTTPS443 hostname名单默认空，仍未批准/真实宿主验收。
- 保存返回私有账户 preview_url=/designs/preview?design_id=…&version=…，历史版本固定；网页普通session与资产归属控制，原Studio INIT恢复，新网页保存产生私有版本供AI读取，第二设备须同账户认证。链接不自动为聊天iframe，聊天MCP Apps UI后补；保存/预览不自动询价、不覆盖ERP/旧报价。
- submit_design_rfq 使用read scope加buyer_confirmed=true、idempotency_key与正version/quantity/对应用户contact.email；原报价事务冻结设计版本/原要求/图像与用户实际确认联系人，保留私有草稿及普通报价夹。确认姓名/电话/地址与profile不同不替换、不改profile；email仍须匹配linked buyer，403 account_contact_mismatch停下澄清新payload，不静默换账户或邮箱。不增RFQ write scope、不把read scope当成无确认写授权。

用户于 2026-10-12 05:16 明确批准新的 `me:designs:read` / `me:designs:write` 与审后TEST启用，以及仅共享 `/3d/studio/customer/index.html` 的窄策略：script `wasm-unsafe-eval`、connect `blob:`；其它指令/frame-ancestors/精确origin保留，无ordinary unsafe-eval/远程origin/ERP改变。该customer文档也用于既有PDP/quote。源码默认关闭，核心独审/合并已完成；本轮操作员TEST部署已安排但未完成，旧grant不自动升级、真实同意仍用户本人完成。

作者本地梳/刷/镜实际RENDERED、Logo修改、SQL不可变版本保存、新context/空内存服务恢复通过（合成账户、实际handler/MySQL与生产Next/Studio，非真实TEST用户）。高级参数来自fixture、photo-recipe模拟不可用，不能当成高级几何编辑→真实Blender重建→变化预览通过。ACK/INIT/进度不能替代RENDERED。未部署、真实GPT/file、Blender重建、聊天UI未验，不把本地正向扩大为这些验收。

附件 `PROCUREMENT_DESIGN_ATTACHMENT_HOSTS` 仍空、hostname未批，真实宿主附件未验；无file或入口关闭仍返回同设计网页编辑/上传回退。ERP授权页独立修复不属于本插件文档范围。实际API错误包括MCP isError的API_HTTP_400/422/409/403等包装与Logo bare error；区分version/key冲突、非法contact、validator/storage不可用，按原same-key重试收据恢复，不重复询价。

## 1.0.3 审核 overlay 与边界

本次已按正式两个main的真实schema/契约及最终尺寸代码定稿，插件PR仍供父任务独审、不自行合并。既有打包器从本PR精确head可重建；输出在源码目录外：

```bash
python3 scripts/package_plugin.py --output /tmp/vantrecomb-procurement-cloud-bound-0.1.4.zip --app-overlay-output /tmp/vantrecomb-test-skills-overlay-1.0.3.zip
```

目标更新只用 `vantrecomb-test-skills-overlay-1.0.3.zip`：单根 `dev-6acc06a725048191bbf860d0b7a72642/`，含完整原兼容manifest（仅version 1.0.2→1.0.3）及skills/全部支持文件、新3D引用文档，不含.app.json、portable root manifest、MCP配置或新App身份。通过定向update保留App-owned文件与真实连接，delete_paths留空；不能单独安装或create_plugin。完整0.1.4源包不用于覆盖目标App，也不更新另一个独立技能。

父任务审核后若更新同一私有插件，先重新读取当前release/source；此处guard只是已观察值，变化时先协调内容，不仅换guard。保持真实App/插件身份、USER/PRIVATE、账户配置及defaultPrompt等展示值。保存账号版本不代表3D已部署/真实宿主验收；新scope真实同意由用户本人完成，附件host空不自动导入GPT文件。具体TEST部署/工具可见/真实host/file/高级Blender/UI证据分别记录。

仅做必要文档引用、manifest版本以外值、真实绑定和ZIP结构校验，不写新测试框架/复杂流程/逐文件匹配hash清单，不重复核心suite或调用设计写/上传/询价。Git保留源码与技能同仓；本任务只提交独立Draft、精确head、1.0.3审核包，不更新真实插件、公开发布或部署。ERP授权页修复不在范围。
