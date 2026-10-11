---
name: vantrecomb-ai-procurement
description: Source custom combs and hotel amenities through Vantrecomb's buyer-controlled procurement API. Discover products, prepare approved RFQs, and access authorized quotes, orders, shipments, documents and account details. Use native procurement MCP tools when available, or the bundled standard-library Python client for local use.
---

# Vantrecomb AI Procurement

Read `references/procurement-workflow.md` before calling an endpoint. Ask for product type, quantity, customization, destination and delivery date; mark unknown details. Never invent price, MOQ, materials, lead time, certification or a sales commitment.

## Cloud plugin

On web and desktop, use the ChatGPT cloud connection bound to this plugin and the host's Connect / OAuth flow for the buyer to sign in and consent on the provider website. Installing the skill alone does not connect an account. Before calling anything, inspect the actual connected tools and their schemas; use the connection's verified metadata for OAuth endpoints, client registration, resource and scopes. This package has not verified the deployed procurement MCP service or DCR. Do not assume that /mcp, /oauth/register or any historical resource binding is available. If connection or tools are missing, report that state and wait for the supported host connection flow; do not switch to a local client, browser session headers, manual token or another account to bypass it.

Use the plugin's MCP tools when available; cloud use does not require Python on a buyer's device. The names and capabilities below are historical package guidance, not a live tools/list result. Use them only when the actual connection exposes a matching tool and contract; do not invent absent tools or guess endpoints.

- Start with `procurement_guide`, then `search_products` / `product_detail`.
- For customer data, use the host's Connect / OAuth flow. The buyer signs into Vantrecomb and approves only the scopes needed. Never ask for a password or token in chat.
- Use `list_quotes` / `quote_detail`, `list_rfqs` / `rfq_detail`, `list_orders` / `order_detail`, `list_shipments` / `shipment_detail`, `customer_profile`, and `list_documents` for buyer-owned records.
- Before `create_rfq_session`, `submit_rfq`, `submit_quote_folder`, `respond_quote`, `update_profile`, or `document_link`, summarize the exact operation and payload and obtain explicit buyer approval. Only then set `buyer_confirmed=true` and a unique `idempotency_key` if those fields are supported by the live tool schema; otherwise follow its actual confirmation and idempotency contract.
- `respond_quote` accepts only `accept`, `request-revision`, or `messages`. A message is recorded, not a sales response. Profile edits change default contact/address details, not an existing order.
- On missing scope, reauthorize only the required scope. On expired/revoked authorization, stop writes and reconnect. Do not use the local Python client to bypass cloud authentication.

## Product facts and communication

Product search/detail are the only catalog endpoints. Materials, crafts, capabilities, solutions, product families, blog posts, FAQs and narrative pages are site content; link them rather than inventing catalog endpoints or quoting cached copy. Share returned `detail_url` as-is.

There is no customer-upload API. Drawings, payment evidence and other buyer files must be emailed by the buyer to `sales_contact.email` from the quote. Check sales email first for documents; only if missing, list documents and request an authorized download link. Never claim an order cancellation, address change or after-sales request is completed until sales confirms it.

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

Optional manually created tokens use secure environment variables `VANTRECOMB_API_TOKEN` and `VANTRECOMB_RFQ_TOKEN`; do not pass tokens in command arguments. RFQ tokens remain bound to their RFQ and expire after 30 minutes. Always obtain explicit buyer confirmation before local POST/PATCH; `--confirm` records that approval but does not replace it. Every write requires an idempotency key.
