---
name: vantrecomb-ai-procurement
description: Source custom combs and hotel amenities through Vantrecomb's buyer-controlled procurement API. Discover products, prepare approved RFQs, and access authorized quotes, orders, shipments, documents and account details. Use native procurement MCP tools when available, or the bundled standard-library Python client for local use.
---

# Vantrecomb AI Procurement

Read `references/procurement-workflow.md` before calling an endpoint. Ask for product type, quantity, customization, destination and delivery date; mark unknown details. Never invent price, MOQ, materials, lead time, certification or a sales commitment.

## Cloud plugin

On web and desktop, use the ChatGPT cloud connection bound to this plugin and the host's Connect / OAuth flow for the buyer to sign in and consent on the provider website. Installing the skill alone does not connect an account. The source contract is implemented in [website PR #279](https://github.com/hx123321/vantreCombB2B/pull/279), merged at main b86e85cee8d92cb7dfb6180e353b08f2b344e087, and the current deployed TEST version is ae1ff0bdbc906b8d1d21f0fed0ed4b53318c23ff. The parent has created and authorized the VANTRE Procurement TEST cloud connection, including approved DCR, and successfully read a synthetic registered TEST account through the native customer_profile tool. This validates that OAuth profile read, not every business capability or a refresh-token flow. This task's TEST origins are https://test-api.vantrecomb.com (API) and https://test.vantrecomb.com (website), as verified by the parent; https://api.vantrecomb.com is not this TEST API. Before calling anything, inspect the actual connected tools and schemas and verified OAuth metadata; merged source does not establish live availability. If connection or tools are missing, report that state and wait for the supported host connection flow; do not switch to a local client, browser session headers, manual token or another account to bypass it.

Use the plugin's MCP tools when available; cloud use does not require Python on a buyer's device. PR #279 implements a fixed catalog of 19 tools mapped to existing business handlers, not automatic discovery of arbitrary REST operations. The guidance below follows that reviewed source contract, not a live tools/list result. Use it only when the actual connection exposes matching tools and schemas; do not invent absent tools or guess endpoints.

- Start with `procurement_guide`, then `search_products` / `product_detail`.
- For customer data, use the host's Connect / OAuth flow. The buyer signs into Vantrecomb and approves only the scopes needed. Never ask for a password or token in chat.
- Use `list_quotes` / `quote_detail`, `list_rfqs` / `rfq_detail`, `list_orders` / `order_detail`, `list_shipments` / `shipment_detail`, `customer_profile`, and `list_documents` for buyer-owned records.
- For all six write tools (`create_rfq_session`, `submit_rfq`, `submit_quote_folder`, `respond_quote`, `update_profile`, `document_link`), supply a unique required `idempotency_key` and preserve native scope, ownership, business validation, CAPTCHA and any necessary approval. Reuse the buyer's still-valid explicit authorization for the same target, action and data; request confirmation only when authorization is missing, the target/action/data materially changes, or a high-risk operation requires confirmation for each action under the live contract. Execute covered creates and updates without adding a read-only restriction or repeating routine-write confirmation; do not broaden the grant or treat read-only authorization as write authorization. `submit_rfq`, `submit_quote_folder` and `respond_quote` with `action=accept` or `request-revision` require `buyer_confirmed=true` once effective explicit authorization covers the exact payload. `create_rfq_session`, `update_profile`, `document_link` and `respond_quote` with `action=messages` have no required `buyer_confirmed` field; a covered buyer request suffices. Preserve the actual schema's remaining parameters.
- `respond_quote` accepts only `accept`, `request-revision`, or `messages`. A message is recorded, not a sales response. Profile edits change default contact/address details, not an existing order.
- On missing scope, reauthorize only the required scope. On expired/revoked authorization, stop writes and reconnect. Do not use the local Python client to bypass cloud authentication.

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
