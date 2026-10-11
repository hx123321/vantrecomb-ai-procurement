# VANTRE Procurement 云连接适配

既有私人插件为 `plugins_6ac5698a6b9c8191b317d7b2e5d8bcfe`，包名 `vantrecomb-procurement-plugin`。本次源基线为账号 release `pluginrel_6ac56e1a3ff881919abd6064bb670336`（0.1.1），通过只读 get_plugin_files 取得完整运行文件，保存在已有专用仓库的 `plugins/vantrecomb-procurement-plugin/`，版本适配为 0.1.2。未调用 create_plugin，不创建同名重复插件；父任务只更新原插件。

## 源归属、已合并契约与接入状态

本仓原 main `5a4c26686950f504178c553d36c7eb33fa909985` 只有旧 Python 技能，没有插件目录；其原技能/脚本/引用保持不变。新目录承接已保存账号包的实际源码，不重新实现包内 Python 客户端，不复制旧技能作为另一安装包。账号包的品牌、defaultPrompt 数组和本地 OAuth 辅助文件保留。

服务器来源已由网站 [PR #279](https://github.com/hx123321/vantreCombB2B/pull/279) 明确：网站 main `b86e85cee8d92cb7dfb6180e353b08f2b344e087` 已合并已审 head `f727519f353120c696b5897ceb87c47d36426165`。本次只读核对该 main 的 [integration contract](https://github.com/hx123321/vantreCombB2B/blob/b86e85cee8d92cb7dfb6180e353b08f2b344e087/docs/ops/procurement-mcp-integration.md) 与 `backend/cmd/server/mcp_procurement.go`；未修改网站工作区。

此前 `4a421c904e701d277a39cf29bf268d6d51b092b9` 未找到 MCP/DCR、resource 仅指向 `/api/v1/ai/me` 的观察属于旧基线。此前对 `api.vantrecomb.com` 的 envoy 503 也是旧环境结果，不能用于判断这次 TEST。PR #279 现已实现 `/mcp`、专用 resource metadata、可选 DCR、OAuth resource 绑定与固定 19 工具，复用已有业务 handler；不是任意 REST 自动发现。

本次 TEST API 为 `https://test-api.vantrecomb.com`，网站为 `https://test.vantrecomb.com`，两 origin 已由父任务只读核实；不能替换为 `https://api.vantrecomb.com`。服务仍未部署，DCR 启用尚未取得用户批准，真实云 app ID 尚未取得。源码合并及服务 CI/审核通过不等于线上 tools/list、OAuth 登录或双端接入成功。

六写工具全部必需 `idempotency_key`。`create_rfq_session`、`update_profile`、`document_link` 和 `respond_quote/messages` 无必需 `buyer_confirmed`；`submit_rfq`、`submit_quote_folder`、`respond_quote/accept` 与 `request-revision` 必需 `buyer_confirmed=true`。仍有效的同目标/动作/数据明确授权可沿用，保留 scope、归属、业务校验、CAPTCHA、幂等及必要审批。

`document_link` 返回 `delivery_mode=caller_ip_bound`；临时 API URL 绑定调用 IP，不能承诺给买家跨浏览器使用或直接跟随。向买家提供实际返回的 `website_download_entry`，由买家在网站登录后按已有受控流程下载；MCP 不取回、附上或流式传输 bytes，不得声称文件已取得。

本次仅同步采购包文档、技能说明和两个 manifest longDescription；原 standalone 技能、ERP、后端、权限、客户端、部署与 FSC 均未修改。

## 源码适配及最终包

根 manifest 用 `extensions.com.openai.apps: "./.app.json"`，兼容 manifest 同步 `apps`；兼容文件不再声明 mcpServers。最终 .app.json 为单一 `apps → vantrecomb-procurement → id` 映射，指向父任务创建并核实的真实 `plugin_asdk_app...`。根 OpenAI extension 不会与 overlay 合并，两个入口都已同步。

直接 mcp.json/.mcp.json 不再分发，工具和 OAuth 由云连接提供，避免网页没有连接以及桌面 HTTP OAuth 配置解析故障/重复路由。网页和桌面 Connect 让买家跳转网站登录并同意，随后工具按该账户 scope 与记录归属调用。原本地客户端仅保留既有独立用法，云连接错误不允许降级绕过。

本阶段无真实 app ID，故没有空 .app.json、伪造客户端或安装 ZIP，源码目录不能直接安装。父任务在[官方云连接流程](https://developers.openai.com/plugins/build/plugins#create-and-test-a-plugin-locally-with-an-mcp-server)中创建连接，先核实它确实指向采购服务器，再执行：

```bash
python3 scripts/package_plugin.py --app-id "$PROCUREMENT_CLOUD_APP_ID" --output .tmp/vantrecomb-procurement-plugin.zip
```

打包器只收集运行技能/品牌资源并生成两个 manifest 与 .app.json；无逐文件匹配/哈希机制，不含文档、打包器、旧技能、直接 MCP、.env 或本地会话。ID 格式校验不是归属或注册校验。

## 父任务最小安全配置及验收

| 项目 | 当前依据 / 需确认 |
| --- | --- |
| MCP URL | 合并源码部署后预期 https://test-api.vantrecomb.com/mcp；当前未部署 |
| issuer / authorize / token | 源配置 API=https://test-api.vantrecomb.com、Browser=https://test.vantrecomb.com；部署后核实际 metadata 和网站登录 |
| client registration | DCR 已实现，默认禁用；启用仍待用户明确批准，不执行注册或猜测 clientId/回调 |
| OAuth | 已合并源码：AuthCode + PKCE S256/auth none、精确 API-origin /mcp resource、15分钟 token、无 refresh；实际连接待验收 |
| scopes | 仅当前任务需要的 me:quotes:read 等；不请求全部八项 |
| app binding | 云连接真实 ID；不借用其他账户或示例客户端 |

父任务更新原私人插件时必须移除旧 release 的 `mcp.json` / `.mcp.json`，仅上传新文件而保留旧文件不会完成路由迁移。保留插件 ID、私人可见性、旧条目和技能。随后由用户自己登录/同意，分别在网页和桌面验证工具发现、公开 guide、获授权只读记录及 401/403 边界；不能为验收创建 RFQ、发送邮件、响应报价或改资料。

本次验证范围：manifest schema、入口同步、技能引用、打包器语法与无 ID/占位 ID 阻塞、旧技能未改、git diff。部署、DCR 启用批准、真实 ID 最终打包、云 importer、OAuth、账户 scope/归属和双端实用均待父任务验收；未合并、部署或更新账号插件。
