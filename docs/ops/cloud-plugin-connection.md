# VANTRE Procurement 已验证云连接与包交付

既有私人技能插件为 `plugins_6ac5698a6b9c8191b317d7b2e5d8bcfe`，包名 `vantrecomb-procurement-plugin`。源基线为账号 release `pluginrel_6ac56e1a3ff881919abd6064bb670336`（0.1.1），来自只读 get_plugin_files，本包版本为 0.1.2。保留发布者、品牌、defaultPrompt 数组、技能及本地辅助文件；父任务审核后更新原插件，不创建同名插件。

## 当前 TEST 与验证边界

网站 [PR #279](https://github.com/hx123321/vantreCombB2B/pull/279) 的采购 MCP 已合并；原集成契约来自 [main b86e85ce](https://github.com/hx123321/vantreCombB2B/blob/b86e85cee8d92cb7dfb6180e353b08f2b344e087/docs/ops/procurement-mcp-integration.md)。固定 19 个工具映射已有 handler，不是任意 REST 自动发现。此前未找到实现/未部署/DCR 未批准/app ID 缺失的记录已被下述实际接入证据取代。

父任务确认当前实际 TEST 版本为 `ae1ff0bdbc906b8d1d21f0fed0ed4b53318c23ff`，API 为 `https://test-api.vantrecomb.com`，网站为 `https://test.vantrecomb.com`；`api.vantrecomb.com` 不是此次 TEST。包含已批准 DCR、PR #280 安全诊断及 PR #281 的 AuthCode+refresh 请求协商为 AuthCode-only。没有实现或验收刷新令牌。

父任务已创建并授权 VANTRE Procurement TEST 云连接，并通过其原生 `customer_profile` 成功读取合成 TEST 注册账户。此证据说明真实 OAuth 资料读取已通过；不是本云再次进行的业务调用，也不能推断其它工具、写业务、撤销/过期、文件下载、完整业务链路或所有宿主均通过。其它只读业务检查仍由父任务进行。

| 身份 | 父任务已核实值 |
| --- | --- |
| 新 App-backed 插件 ID | `plugin_asdk_app_6acc06a725048191bbf860d0b7a72642` |
| 观察到的 release | `PluginRelease_aa9a077898988191a4eaa221e67652c2` |
| .app.json 的 mapping key | `dev-6acc06a725048191bbf860d0b7a72642` |
| 实际 App ID | `asdk_app_6acc06a725048191bbf860d0b7a72642` |

插件 ID 与 .app.json 内的 App ID 不同，不能互换。采购源码 .app.json 原样使用父任务提供的真实 mapping；根 `extensions.com.openai.apps` 与兼容 `apps` 均指向 `./.app.json`。

## 两个审核包

```bash
python3 scripts/package_plugin.py --output .tmp/vantrecomb-procurement-cloud-bound-0.1.2.zip --app-overlay-output .tmp/vantrecomb-test-skills-overlay-1.0.1.zip
```

完整包给既有技能插件使用：单根 `vantrecomb-procurement-plugin/`，含根 manifest、兼容 manifest、真实 .app.json、技能/支持文件及原品牌资源。没有直接 mcp.json/.mcp.json、文档、打包器、原独立技能、.env 或本地会话。缺失/空/占位绑定仍拒绝打包；ID 语法不证明注册状态，真实绑定的证据来自父任务实际读取。无逐文件匹配/哈希机制。

最小 overlay 给上述新 App-backed 插件补技能：单根 `dev-6acc06a725048191bbf860d0b7a72642/`，只含完整的原兼容 manifest（增加 `skills: "./skills"`、版本 1.0.0 → 1.0.1）与同一套技能/支持文件。兼容 manifest 源码位于 `overlays/vantrecomb-test/.codex-plugin/plugin.json`，保留 App developer、VANTRE Procurement TEST、Other、空 capabilities、null defaultPrompt 及其它所有原字段。沿用受支持 legacy 入口，不增加会遮蔽其配置的根 manifest。

Overlay 不含 .app.json、root plugin.json、MCP 配置、品牌资源或新的身份/展示设置；通过更新接口保留既有 App-owned 文件与真实连接。它是定向更新补丁，不能单独安装、不能 create_plugin，也不要求重新创建连接或再次授权。

## 父任务审核与更新

1. 复核源码/两个 ZIP，并用 get_plugin_files 重新观察两个目标插件的最新 release；若 release 已变化，先核对再更新，不能只替换 expected_release_id。
2. 完整包更新 `plugins_6ac5698a6b9c8191b317d7b2e5d8bcfe`，须显式 `delete_paths=["mcp.json",".mcp.json"]`，移除旧直接路由。部分上传默认保留未提供文件，省略这两个删除参数会留下重复路由。
3. 最小 overlay 更新 `plugin_asdk_app_6acc06a725048191bbf860d0b7a72642`；以最新已观察 release 作 guard，`delete_paths` 留空，不删除或改写 .app.json/MCP/连接。保留 App-owned 描述、展示、身份、受众、权限和私人可见性。
4. 更新后回读技能文件与 manifest；既有技能插件确认旧 MCP 文件已删除，新 App 插件确认 .app.json 和 App-owned 值保留。检查技能可加载及实际宿主工具；不以保存成功宣称全业务验收，不让用户重复创建或授权。

## 业务规则保持

六写工具全部必需 `idempotency_key`。`create_rfq_session`、`update_profile`、`document_link` 和 `respond_quote/messages` 无必需 `buyer_confirmed`；`submit_rfq`、`submit_quote_folder`、`respond_quote/accept` 与 `request-revision` 必需 `buyer_confirmed=true`。有效的同目标/动作/数据明确授权可沿用；scope、归属、业务校验、CAPTCHA、幂等及必要审批均保留。

`document_link` 返回 `delivery_mode=caller_ip_bound`；临时 URL 绑定调用 IP。给买家实际返回的 `website_download_entry`，不直接跟随或承诺跨浏览器下载；MCP 不取回、附上或流式传输文件 bytes。

本仓原 standalone 技能/脚本/引用/agents 保持不变；ERP、后端、FSC、OAuth grant、DCR/客户端配置均未修改。本任务只提交源码和两个审核包，不安装、更新账号插件、合并、部署或公开发布。最小验证包括 manifest/入口/引用、真实绑定、overlay 配置保留及 ZIP 结构，不重复跑其它项目测试。
