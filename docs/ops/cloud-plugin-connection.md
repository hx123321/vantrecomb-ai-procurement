# VANTRE Procurement 云连接适配

既有私人插件为 `plugins_6ac5698a6b9c8191b317d7b2e5d8bcfe`，包名 `vantrecomb-procurement-plugin`。本次源基线为账号 release `pluginrel_6ac56e1a3ff881919abd6064bb670336`（0.1.1），通过只读 get_plugin_files 取得完整运行文件，保存在已有专用仓库的 `plugins/vantrecomb-procurement-plugin/`，版本适配为 0.1.2。未调用 create_plugin，不创建同名重复插件；父任务只更新原插件。

## 源归属与未验证能力

本仓原 main `5a4c26686950f504178c553d36c7eb33fa909985` 只有旧 Python 技能，没有插件目录；其原技能/脚本/引用保持不变。新目录承接已保存账号包的实际源码，不重新实现包内 Python 客户端，不复制旧技能作为另一安装包。账号包的品牌、defaultPrompt 数组和本地 OAuth 辅助文件保留。

服务器应属于已有 `hx123321/vantreCombB2B`，本云核对最新 main `4a421c904e701d277a39cf29bf268d6d51b092b9`：

- `backend/cmd/server/oauth_authorization.go` 的 defaultOAuthClients 是预注册客户端 map；默认示例 client/callback 不能用于本插件。
- `oauth_authorization.go`、`oauth_device.go` 和 `openapi_discovery.go` 提供 PKCE/AuthCode、Device 和 OAuth metadata（token auth none）；资源 metadata 指向 /api/v1/ai/me，未描述 /mcp。未找到 MCP、DCR 注册实现或 registration_endpoint。
- `oauth_origin.go` 支持 API 与浏览器域分离；旧默认把浏览器入口指向 API 域，不能据此宣称真实网站登录可用。
- 本云对 `https://api.vantrecomb.com/mcp` 和两个 well-known metadata 的无凭据严格 TLS 请求均返回 envoy 503（remote connection failure），不能证明源站部署状态。

因此采购 MCP endpoint、DCR、线上 OAuth 契约、账户工具发现均未独立验证。包内固定工具说明来自既有 release，不是本次 tools/list 结果。父任务须定位实际运行 MCP 的源码/部署版本并验证 metadata；不能把技能或包声明当已部署能力。本次不改独立站后端、权限、客户端、部署或 FSC。

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
| MCP URL | 既有 release 声明 https://api.vantrecomb.com/mcp；实际可达和工具待核 |
| issuer / authorize / token | 从实际 metadata 读取；浏览器入口须跳转真实网站登录 |
| client registration | DCR 未证实；不先选择 DCR。若预注册，取得管理页精确回调并经批准登记 public client |
| OAuth | 现有源码 PKCE S256、AuthCode；云 MCP 实际契约须重新核 |
| scopes | 仅当前任务需要的 me:quotes:read 等；不请求全部八项 |
| app binding | 云连接真实 ID；不借用其他账户或示例客户端 |

父任务更新原私人插件时必须移除旧 release 的 `mcp.json` / `.mcp.json`，仅上传新文件而保留旧文件不会完成路由迁移。保留插件 ID、私人可见性、旧条目和技能。随后由用户自己登录/同意，分别在网页和桌面验证工具发现、公开 guide、获授权只读记录及 401/403 边界；不能为验收创建 RFQ、发送邮件、响应报价或改资料。

本次验证范围：manifest schema、入口同步、技能引用、打包器语法与无 ID/占位 ID 阻塞、旧技能未改、git diff。真实 ID 最终打包、云 importer、OAuth、账户 scope/归属和双端实用均待父任务验收；未合并、部署或更新账号插件。
