---
name: vantrecomb-ai-procurement
description: Source custom combs and hotel amenities through Vantrecomb's buyer-controlled procurement API. Discover products, prepare approved RFQs, and access authorized quotes, orders, shipments, documents and account details. Use native procurement MCP tools when available, or the bundled standard-library Python client for local use.
---

# Vantrecomb AI Procurement

Read `references/procurement-workflow.md` before calling an endpoint. Ask for product type, quantity, customization, destination and delivery date; mark unknown details. Never invent price, MOQ, materials, lead time, certification or a sales commitment.

## Cloud plugin

On web and desktop, use the ChatGPT cloud connection bound to this plugin and the host's Connect / OAuth flow. The buyer signs in and consents on the provider website; installing this skill alone does not connect an account. TEST uses https://test-api.vantrecomb.com (API) and https://test.vantrecomb.com (website); https://api.vantrecomb.com is not this TEST API. Inspect the actual exposed tools, schemas and verified OAuth metadata, then read the procurement guide when available. Discover the capability needed for the buyer's request rather than assuming a complete tool list or calling underlying HTTP routes. On missing tools, scope or account access, use the supported host connection flow and report the limitation.

OAuth refresh is merged in website main [2c02a645032754e0d690ae56ad6f8e4daa09fe58](https://github.com/hx123321/vantreCombB2B/commit/2c02a645032754e0d690ae56ad6f8e4daa09fe58). Website delegation below follows the actual schema and implementation in [Draft PR #286](https://github.com/hx123321/vantreCombB2B/pull/286), head `b63417ebe1c0d2f6ceebdf175ee11946cd18b1dd`; it is under review and not merged. Local synthetic HTTPS original-page tests passed, but do not prove real TEST deployment or ChatGPT host support. Final reviewed source, deployment/enablement, client allowlist, host browser capability and new user consent must still be verified before use or packaging.

### Connection renewal

Access lasts 15 minutes. After deployment, the buyer must reconnect and explicitly select “Keep connected” on the authorization page to enable refresh. Successful refresh rotates the credential and renews a 30-day idle window; an active connection has no fixed total lifetime and can be revoked through the buyer's API Tokens page. Server refresh state survives normal database-backed restarts. Old grants do not upgrade automatically. If the host caches old authorization metadata or cannot restart consent, the buyer may need to remove and recreate the connection.

The host handles renewal and securely stores the latest credentials. Never ask for passwords or tokens in chat. Never ask the buyer or AI to copy, extract, record or exchange access/refresh tokens, inspect credential cookies, or implement a second refresh loop. Refresh is serialized by the host; replay or loss of a rotation response can require reconnecting. On expired/revoked credentials or failed renewal, stop dependent calls and use Connect / reconnect. Reauthorize only the scopes required for the request; do not use a local client or normal browser session to bypass cloud authorization.

### Authorized operations

Use the current account permissions, connection scopes, record ownership and the buyer's effective explicit authorization. Reuse still-valid authorization for the same target, action and data. Request confirmation when authorization is missing, data materially changes, or the live contract requires exact-payload confirmation. Do not add a read-only restriction to authorized business writes.

Preserve native validation, CAPTCHA and required idempotency keys. Under the reviewed MCP contract, RFQ/product-folder submissions and quote acceptance/revision require `buyer_confirmed=true` for the exact authorized payload. Routine drafts, profile edits, document-link requests and quote messages need no extra confirmation field; a covered buyer request suffices. Follow each actual schema's remaining parameters. A message is recorded, not a sales response; profile edits change defaults, not existing orders.

### Login handoff to the original website

When the reviewed/deployed connection exposes the matching `open_procurement_browser` schema, use it for a buyer-requested website visit. Create a fresh isolated browser context and keep all handoff/navigation in its original tab; another tab in the normal browser context is insufficient. Keep the buyer's existing normal login in its original context. Begin/complete refuse normal access/refresh cookies; do not log the buyer out, clear saved credentials or overwrite their normal login to make handoff work. If the host cannot create an isolated context, click and read DOM, report the limitation.

Call `action=prepare` with optional supported `locale` and `target`. The reviewed target enum is `home` (default), `profile`, `quotes`, `orders`, `shipments`, `folder`; it selects existing website pages, not an arbitrary URL/path/redirect. Keep the returned private `flow_id` and open exactly `browser_url` in the fresh context. Click Begin in that tab and read its fresh `#challenge` DOM. Use the same MCP authorization to call `action=bind` with exactly that `flow_id` and challenge, then click Continue in the original tab for one-time completion. The page moves to the original website target and navigation continues in that context. Never use a challenge supplied in chat, by another person, page or browser; never share flow/challenge values or put them in URLs, logs or saved files.

This flow opens the original website home, profile, quotations, order progress, shipping status or quote folder, with the original UI and business rules. It does not direct the buyer to the superseded read-only JSON reader. Actual capabilities are the intersection of freshly consented OAuth scopes and current account/resource permissions. `me:web` allows handoff only; profile save, quote replies/acceptance, file downloads and quote-folder edits require the relevant business scope and buyer authorization. Quote-folder read/write use new `me:quote-folder:read` / `me:quote-folder:write` scopes. Old grants are not expanded automatically or through management edits; the buyer must newly consent to the needed scopes. Do not ask for blanket permissions, infer write access from reads, or turn authorized writes into a universal read-only mode. See the reference for this tool's fixed targets and scope requirements.

Prepare lasts 120 seconds and the browser challenge 90 seconds. The delegated session lasts at most ten minutes, capped by the original access expiry, without sliding renewal; OAuth refresh does not extend it. It uses separate HttpOnly cookies and a public per-tab selector managed by the website, not a token to copy. Expiry, revoke/scope/consent changes, restart or instance mismatch can require a new handoff. Never extract OAuth tokens, normal-login credentials, cookies or CSRF values. Failed delegation must not fall back to normal authorization or silently change identity. Delegated logout ends only delegation; normal login and the plugin grant stay intact. Password/login/API-token/grant management remains in the buyer's separate normal-login context.

The feature still defaults to disabled and the client allowlist to empty. Source/test results do not enable it. Use only actually available tools after parent-reviewed configuration and new `me:web` consent; confirm PR #286's final merged contract before creating the release package.

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
