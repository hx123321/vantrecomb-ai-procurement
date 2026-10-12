# PRIVATE TEST App 3D 技能发布记录

本次从最新采购插件 main `c980f45db5f56a43408a51527c6405a846f4482f`（已合PR3/4）准备用户明确授权的3D技能更新。PR4的回答语言/精确版本预览指导原在根技能，此次同步到App实际加载的packaged skill，根独立技能不修改。只提升当前账号1.0.2至1.0.3，保留插件/App/MCP/OAuth/展示、USER/PRIVATE范围；不创建插件、不公开发布、不改生产/DNS/权限。

| 更新前实际读取 | 值 |
| --- | --- |
| 插件 | `plugin_asdk_app_6acc06a725048191bbf860d0b7a72642` |
| App | `asdk_app_6acc06a725048191bbf860d0b7a72642` |
| 包名/mapping | `dev-6acc06a725048191bbf860d0b7a72642` |
| 版本/范围 | 1.0.2 / USER / PRIVATE |
| expected release guard | `pluginrel_6acc3f84f9948191823420f4f948f165` |
| 本次技能版本 | 1.0.3 |

发布内容从上述main保留全StudioSnapshot高级能力、两模式、严格参数/尺寸/包装组合、错误纠正/并发读回、Logo网页回退、RFQ真实确认联系人及幂等恢复；不降为基础参数。字段说明正文已英文（legacy description_zh/fields_zh键可继续保留），用户回答跟随对话语言，技术键/枚举不翻改。保存不重建、不询价；仅用户请求预览时显式准备精确版本，等待其geometry succeeded及真实renderer完成，复用相同几何/队列任务，不重复失败重试。公共geometry缓存与私有Logo/完整snapshot/账户信息分开，URL不带凭据。

当前已部署TEST证据：website backend `63bb81b`、frontend `5dd80e22`、Pipeline `e39cd11`，TEST rebuild服务运行且有真实Blender成功样本。原生MCP当前实际暴露设计capabilities/list/read/create/update/Logo/RFQ；本次read-only测试刷款capabilities成功，608字段、完整snapshot/schema/高级字段/packaging/upload policy与英文response guidance均返回；list_designs成功且当前0条。此证据不证明每个写/精确版本渲染、dense高级组合或真实GPT UI/附件已验。

`PROCUREMENT_DESIGN_UI_ENABLED`仍关闭，attachment hostname名单空。普通预览link不自动iframe；不开UI、不注册域名/DNS、不添加CORS/CSP能力。原native设计工具按actualschema及账户授权执行；缺scope仍走用户真实consent，旧grant不自动升级。一般文件不改设计Logo通道的用途边界。SSO修复在另一个任务，当前技能保持现行prepare/challenge/bind/complete和异账户拒绝的行为描述，不抢先写异账户确认切换。

本包用原legacy manifest（仅version提高）和完整技能/支持文件，新gpt-design reference保留；不放.app.json/root manifest/MCP配置，上传overlay保留App-owned文件，delete_paths留空。现有0.1.4完整源包仅可复用源码，不能用于覆盖目标App或另一独立技能。版本按实际1.0.2严格递增，无凭据或真实grant嵌入。

先结构/manifest/引用检查，再用上表expected_release_id调用Plugin Creator update同一private App；若release变动先协调源内容，不盲换guard。成功后回读版本/release、skill/reference和.app绑定/展示，只有工具成功结果证明保存。最终返回插件链接与新release，用户若仍加载旧技能需Refresh或重新激活；已有设计原生工具无需为仅技能更新重复授权，缺scope另行真实consent。

不做逐文件匹配/hash清单、不重复全量构建/备份，不调用RFQ/业务提交、不部署服务器。发布后的真实3D写/预览验证按明确客户要求和实际tool schema完成，不把保存插件等同全部3D功能通过。
