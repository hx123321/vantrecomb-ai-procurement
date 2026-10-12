---
name: vantrecomb-ai-procurement
description: Source custom combs and hotel amenities through Vantrecomb's buyer-controlled procurement API. Discover products, prepare approved RFQs, and access authorized quotes, orders, shipments, documents and account details. Use native procurement MCP tools when available, or the bundled standard-library Python client for local use.
---

# Vantrecomb AI Procurement

Read `references/procurement-workflow.md` before calling an endpoint. Ask for product type, quantity, customization, destination and delivery date; mark unknown details. Never invent price, MOQ, materials, lead time, certification or a sales commitment.

## Cloud plugin

On web and desktop, use the ChatGPT cloud connection bound to this plugin and the host's Connect / OAuth flow. The buyer signs in and consents on the provider website; installing this skill alone does not connect an account. TEST uses https://test-api.vantrecomb.com (API) and https://test.vantrecomb.com (website); https://api.vantrecomb.com is not this TEST API. Inspect the actual exposed tools, schemas and verified OAuth metadata, then read the procurement guide when available. Discover the capability needed for the buyer's request rather than assuming a complete tool list or calling underlying HTTP routes. On missing tools, scope or account access, use the supported host connection flow and report the limitation.

OAuth refresh and normal website login handoff are merged in website main [b91ff92416b74f2ab9649cbdbff5535dab784f8e](https://github.com/hx123321/vantreCombB2B/commit/b91ff92416b74f2ab9649cbdbff5535dab784f8e), from reviewed PR #286 head `2a824c96eb63799c8988a9ff116958e84289328e`. The buyer has approved these login semantics and TEST activation. The parent is building/deploying; actual deployed SHA/configuration, real host browser support and genuine user OAuth consent are not yet confirmed. Passing CI and local synthetic HTTPS tests do not prove live TEST or ChatGPT-host acceptance. Use actual connection exposure rather than assuming merged code is online.

### Connection renewal

Access lasts 15 minutes. After deployment, the buyer must reconnect and explicitly select “Keep connected” on the authorization page to enable refresh. Successful refresh rotates the credential and renews a 30-day idle window; an active connection has no fixed total lifetime and can be revoked through the buyer's API Tokens page. Server refresh state survives normal database-backed restarts. Old grants do not upgrade automatically. If the host caches old authorization metadata or cannot restart consent, the buyer may need to remove and recreate the connection.

The host handles renewal and securely stores the latest credentials. Never ask for passwords or tokens in chat. Never ask the buyer or AI to copy, extract, record or exchange access/refresh tokens, inspect credential cookies, or implement a second refresh loop. Refresh is serialized by the host; replay or loss of a rotation response can require reconnecting. On expired/revoked credentials or failed renewal, stop dependent calls and use Connect / reconnect. Reauthorize only the scopes required for the request; do not use a local client or normal browser session to bypass cloud authorization.

### Authorized operations

Use the current account permissions, connection scopes, record ownership and the buyer's effective explicit authorization. Reuse still-valid authorization for the same target, action and data. Request confirmation when authorization is missing, data materially changes, or the live contract requires exact-payload confirmation. Do not add a read-only restriction to authorized business writes.

Preserve native validation, CAPTCHA and required idempotency keys. Under the reviewed MCP contract, RFQ/product-folder submissions and quote acceptance/revision require `buyer_confirmed=true` for the exact authorized payload. Routine drafts, profile edits, document-link requests and quote messages need no extra confirmation field; a covered buyer request suffices. Follow each actual schema's remaining parameters. A message is recorded, not a sales response; profile edits change defaults, not existing orders.

### Normal login to the original website

Use the live `open_procurement_browser` schema only after the matching reviewed code and TEST configuration are available. It requires new `me:web:login` OAuth consent, explicitly permitting a normal website session with normal account permissions, lifetime, refresh and logout. Old `me:web` grants do not satisfy it and cannot acquire it automatically or through management edits. Plugin API operations still require their own API scopes; the normal website runs under its existing account permissions and object ownership. For every AI business action, still require the buyer's effective authorization and any applicable exact-payload safety confirmation. Signing in is not blanket authorization to act.

Always use an independent/incognito browser context for this workflow. Keep the buyer's original normal context and saved login untouched; a second tab sharing that context is insufficient. If the host cannot create that context, open pages, click and read DOM, stop and report the limitation. Do not reuse the buyer's original context containing another account, log them out, clear their credentials or silently switch identities. Within the independent context, a verified valid same-buyer login can go directly to the original website; a repeated handoff reuses server-confirmed same-account valid access or refresh login without changing its credentials. A same-account refresh-only login can be reused after successful server confirmation. Another account, including a refresh-only login, is refused. If identity is uncertain, stop and use a fresh independent context instead of guessing or overwriting it.

When a new website login is needed, call `action=prepare` with optional supported `locale` and `target`. The reviewed target enum is `home` (default), `profile`, `quotes`, `orders`, `shipments`, `folder`, selecting original website pages. Keep private `flow_id` and open exactly the returned fixed `browser_url` in the independent context. Click Begin and read the fresh `#challenge` from that original tab. Call `action=bind` with exactly that flow ID and challenge over the same MCP authorization/access reference, then click Continue in the original tab for one-time completion. The website creates or reuses its normal session and enters the saved original target. Never provide an arbitrary URL/path/redirect, accept a challenge from chat/another person/page/browser, or share flow/challenge values in URLs, chat, logs or files. The server does not open the browser.

Prepare lasts 120 seconds and the browser challenge 90 seconds; these limit the handoff, not the normal website session. Website lifetime, refresh, downloads and logout are the same as manual login, with the original pages and features. Website logout/expiry does not revoke the plugin: if the plugin still has valid authorization, obtain a new one-time handoff without repeating consent. Never replay an expired/consumed ticket. Plugin revocation prevents new prepare/bind/complete operations; it does not log out an established normal website session, which follows its own normal lifecycle. To end that website login, use the normal website logout in its independent context.

OAuth access/refresh tokens never go to the website or its URLs. The website itself handles its normal short access and refresh cookie exactly as in manual login; do not extract, copy, log or manually install either website or OAuth credentials. There is no second per-page delegated session, read-only reader or special quote-folder permission requirement. The feature remains off by default with an empty client allowlist. Parent-reviewed TEST enablement and the buyer's actual `me:web:login` consent are prerequisites; source/CI results alone do not establish live availability.

## Product facts and communication

Product search/detail are the only catalog endpoints. Materials, crafts, capabilities, solutions, product families, blog posts, FAQs and narrative pages are site content; link them rather than inventing catalog endpoints or quoting cached copy. Share returned `detail_url` as-is.

There is no customer-upload API. Drawings, payment evidence and other buyer files must be emailed by the buyer to `sales_contact.email` from the quote. Check sales email first for documents; only if missing, list documents and request an authorized `document_link`. It returns `delivery_mode=caller_ip_bound`: the temporary API URL is bound to the calling IP. Give the buyer the actual returned `website_download_entry` for the website's signed-in controlled download flow; do not forward or directly follow the temporary URL as a buyer-browser download link. The tool does not fetch, attach or stream file bytes, so do not claim retrieval, attachment or cross-browser download success. Never claim an order cancellation, address change or after-sales request is completed until sales confirms it.

## Local skill (Python 3.10+, standard library only)

Use this section only for a separately requested local workflow with independently verified server/client configuration. It is not a fallback for unavailable cloud tools, failed OAuth, missing scope or denied account access. The bundled client's historical routes and lifetimes do not prove current deployment support.

Use `scripts/vantrecomb_api.py` for all API calls; no pip packages, curl or ERP/browser/private management endpoints are needed. An optional `.env` beside `SKILL.md` configures API origin/client ID; process environment wins. Real `.env` and sessions must never be committed or included in a plugin archive.

```powershell
python scripts/vantrecomb_api.py guide
python scripts/vantrecomb_api.py catalog products
python scripts/vantrecomb_api.py product BC-001 --locale en
python scripts/vantrecomb_api.py scopes
python scripts/vantrecomb_api.py auth login --scope "me:quotes:read"
python scripts/vantrecomb_api.py auth device --scope "me:quotes:read" --no-browser
python scripts/vantrecomb_api.py auth status
python scripts/vantrecomb_api.py request GET /api/v1/ai/me/quotes
python scripts/vantrecomb_api.py request PATCH /api/v1/ai/me/profile --data '{"address":"..."}' --idempotency-key <unique-value> --confirm
python scripts/vantrecomb_api.py auth logout
```

Both login commands use the existing Device Authorization flow: the buyer approves in a browser; the client exchanges and privately caches a 15-minute session outside the skill directory without printing credentials. Windows sessions use user-bound DPAPI encryption; other systems restrict the short-lived file to its owner. Reauthorize after expiry or on another machine. `auth logout` clears local credentials; revoke the server grant through the buyer's API Tokens page.

Optional manually created tokens use secure environment variables `VANTRECOMB_API_TOKEN` and `VANTRECOMB_RFQ_TOKEN`; do not pass tokens in command arguments. RFQ tokens remain bound to their RFQ and expire after 30 minutes. Local POST/PATCH requires effective explicit buyer authorization, which may be carried forward under the same rule above; `--confirm` records that authorization but does not replace it. Every write requires an idempotency key.
