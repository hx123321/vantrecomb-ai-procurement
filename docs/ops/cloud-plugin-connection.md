# PRIVATE TEST App 技能 1.0.5 修订候选

本次在采购插件 main `9ce7a3a59edb9470c0a99c96e1b4f36520e8dd7f` 上准备下一版技能和说明，交由主线程独立审核、合并。**尚未发布插件；必须等主线程确认本批 TEST 部署生效后再更新同一私有插件。** 不新建插件、连接、任务或 ERP 技能，不修改权限、DNS、CORS、allowlist，不生成真实 OAuth grant，不执行真实报价放弃。

| 当前已读取的账号版本 | 值 |
| --- | --- |
| 插件 | `plugin_asdk_app_6acc06a725048191bbf860d0b7a72642` |
| App | `asdk_app_6acc06a725048191bbf860d0b7a72642` |
| 包名 / mapping | `dev-6acc06a725048191bbf860d0b7a72642` |
| 当前版本 / 范围 | 1.0.4 / USER / PRIVATE |
| 当前 release，后续发布须重新读取核对 | `pluginrel_6acd5b13875c8191831a1bb58d99efe5` |
| 目标 App 技能 overlay 版本 | 1.0.5 |
| 通用源码包版本（独立版本序列） | 0.1.5 |

## 真实合并契约

B2B [PR #298](https://github.com/hx123321/vantreCombB2B/pull/298) 已合并为 `e99108c22a5efb11d46fa26f6e77b6a19f2a0d71`；ERP [PR #133](https://github.com/hx123321/CombManager/pull/133) 已合并为 `4cb8cbcc0f5d3c493e9a42c1c7e880246c33e308`。本批 TEST 发布由既有部署任务按 B2B 后端 → ERP 后端 → 两端 UI 推进，本修订不执行部署，也不把合并当作部署成功。ERP 技能已存在且采用发现式接口，本仓库不追加 ERP 技能或静态业务接口清单。

采购技能按 B2B 最终合并代码修订：

- 报价放弃是现有 `respond_quote` 的 `action=abandon`，不是新工具。使用 `id`、`payload.note` 原因、`buyer_confirmed=true` 和必填 `idempotency_key`，受 `me:quotes:respond` 和记录归属限制。仅未确认下单且未关联订单时可主动放弃；成功立即关闭并释放进行中询价额度，保留历史，送 ERP 检查。操作后回读，409 先读当前状态，不用新键掩盖不确定结果，不能代替订单取消。详见 packaged `references/procurement-workflow.md`，不另复制状态/参数表。
- 网页 SSO 优先无痕，不可用时可用普通浏览器。保留 prepare → 原标签 challenge → 同 MCP bind → 原页一次性消费。异账号在可信页面显示当前/目标姓名及邮箱；只有明确授权本次切换才确认。取消/关闭/后退保留原登录，批准切换仅影响本站当前浏览器会话，不全局注销、不撤销其他 session/grant。同账号 access/refresh-only 登录沿用；会话变化、过期或重放重新核对。仍需真实 `me:web:login` consent，API scopes 不扩大，长令牌不进入网页或 AI 输出。
- preview 新增公开 summary 的 `outputSchema`，私有 snapshot/Logo 仍在组件 `_meta`；禁用附件诊断只返回 `observed_attachment_hostname`，不 fetch/DNS/存储或输出临时签名 URL。部署后再读实际 metadata/结果；诊断不批准 host、不等于上传成功。

## 当前 TEST 3D 状态和保留能力

UI gate 已启用，专用 `ui.domain=https://gpt-preview.vantrecomb.com`，资源来源仅 `https://test.vantrecomb.com`。主会话已发现 render 工具；真实 TEST 设计 version 1 几何 `succeeded`，但 root 的 `include_widget` 返回 `widget unavailable`，内嵌尚未验收。直接 Logo host file 仍返回 `attachment_ingress_not_enabled`，实际附件 hostname 未批准。所有 packaged 技能/reference 已移除“UI gate 仍关闭”的过时说法，仍保留准确的网页 fallback 和未通过边界。

保留完整 StudioSnapshot v2 高级参数发现、one_sentence/guided 两模式、英文解释与用户对话语言、正式尺寸/组合验证、同设计版本并发回读、Logo 幂等恢复及网页回退、RFQ 精确版本/联系人/授权。保存不重建、不自动询价；只有客户请求预览才准备精确版本，复用相同几何/已有任务，遵守 CD 和显式失败重试。几何成功与真实 renderer 完成分别证明，不以工具暴露、ACK 或部署冒充渲染成功。不新增复制维护的参数表。

## 后续同一私有版本更新

沿用 `scripts/package_plugin.py`：完整通用源码包 0.1.5 仅供源码复用，**不能用于覆盖目标 App 或另一独立技能**。真正可更新来源是 `overlays/vantrecomb-test/.codex-plugin/plugin.json`（1.0.5）加 `plugins/vantrecomb-procurement-plugin/skills/`，打包为 skills-only App overlay。它仅带原 legacy manifest 的版本提升及技能/支持文件，不带 `.app.json`、root manifest、MCP/OAuth 配置或 App 展示资产；省略文件由更新工具保留，`delete_paths` 留空。原技能名和兼容 Python 支持文件保留，根独立技能和 ERP 技能不改，无用户凭据嵌入。

本次只做必要文档/manifest/引用及打包结构检查，不重跑后端/前端测试或真实业务动作。主线程独审合并且确认 TEST 部署生效后，重新读取同一插件的 current release 和 App-owned metadata，协调任何并发更新；仅用当时有效的 `expected_release_id` 更新同一 PRIVATE 插件，保留 App 绑定、MCP、OAuth 和展示。成功后回读目标技能/版本/绑定，工具成功才说明版本已保存。用户随后 Refresh 或重新激活，必要时开新会话；仅技能变更不需要额外 consent，实际缺 scope 则走真实授权。

保存插件版本不等于真实 SSO、widget、附件导入或全部业务闭环已验收。发布前不得将本批尚未确认部署的新 SSO 描述为线上已生效。
