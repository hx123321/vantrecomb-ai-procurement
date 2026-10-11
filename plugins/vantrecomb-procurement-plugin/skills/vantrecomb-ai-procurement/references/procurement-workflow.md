# Vantrecomb AI procurement workflow

The current source contract is [website PR #279](https://github.com/hx123321/vantreCombB2B/pull/279), merged at main b86e85cee8d92cb7dfb6180e353b08f2b344e087 from reviewed head f727519f353120c696b5897ceb87c47d36426165; see its [integration contract](https://github.com/hx123321/vantreCombB2B/blob/b86e85cee8d92cb7dfb6180e353b08f2b344e087/docs/ops/procurement-mcp-integration.md). It implements a fixed 19-tool mapping to existing business handlers, not automatic discovery of arbitrary REST operations. The earlier baseline with no MCP/DCR implementation is superseded. The service has not been deployed, enabling DCR has not been approved, and the real cloud app ID has not been obtained. For cloud use, inspect actual connected tools, schemas and verified metadata before calling anything; source implementation is not a live tools/list result. If no verified connection or matching tool exists, report the missing capability and wait for the host connection flow; do not guess a tool or call underlying HTTP routes as a substitute.

This task's TEST API is `https://test-api.vantrecomb.com` and TEST website is `https://test.vantrecomb.com`; the parent verified both origins read-only. `https://api.vantrecomb.com` is a historical package origin, not this TEST server. Use only the verified provider connection and read its procurement guide when available. Underlying REST routes and production copy-page URLs below describe business mappings; they are not permission to bypass MCP or substitute the historical API origin. A separately requested local workflow must independently verify its server/client configuration.

Use `/api/v1/ai/catalog/*` only for products: `GET /api/v1/ai/catalog/products` to search, `GET /api/v1/ai/catalog/products/{sku}` for one product (the path identifier accepts a `sku`, `style_id` or `slug`). A product card carries structured fields only — no marketing HTML and no ERP internal fields — and `three_d` exposes just `enabled` and `match_mode`. Product `detail_url` values are full `https://www.vantrecomb.com/products/styles/{slug}` URLs (en no prefix; ar/de/es/fr/ja/pt-BR/ru/zh-CN/zh-TW prefix the path). Do not use browser, ERP, or `/api/v1/public/*` endpoints.

Blog posts, FAQs, and site pages have no catalog endpoints; find them through site search and `llms.txt`.

Materials, crafts, capabilities, solutions, project stories, and product families have no catalog endpoints. Never quote that narrative from memory or catalog data. Link the buyer to the absolute copy pages instead:

`https://www.vantrecomb.com/products` (+ `/products/by-material`, `/products/by-scenario`, `/products/by-type`, `/products/cushion-hair-brushes`, `/products/comb-teeth-structures`) `https://www.vantrecomb.com/capabilities/materials-craft` `https://www.vantrecomb.com/capabilities/custom-development` `https://www.vantrecomb.com/capabilities/oem-odm-manufacturing` `https://www.vantrecomb.com/why-vantre/production-process` `https://www.vantrecomb.com/services` `https://www.vantrecomb.com/services/packaging` `https://www.vantrecomb.com/solutions/for-brands` `https://www.vantrecomb.com/solutions/for-hotels` `https://www.vantrecomb.com/solutions/for-salons` `https://www.vantrecomb.com/solutions/for-gifts-promotions` `https://www.vantrecomb.com/solutions/handcrafted` `https://www.vantrecomb.com/industries` `https://www.vantrecomb.com/why-vantre` `https://www.vantrecomb.com/why-vantre/custom-project-ai` `https://www.vantrecomb.com/resources/ai-procurement` `https://www.vantrecomb.com/resources` `https://www.vantrecomb.com/resources/blog` `https://www.vantrecomb.com/resources/faq` `https://www.vantrecomb.com/support` `https://www.vantrecomb.com/contact` `https://www.vantrecomb.com/inquiry`

For a write request, use the buyer's still-valid explicit authorization for the same target, action and data. Only when authorization is missing, there is a material change, or the live contract requires confirmation for each high-risk action, show the proposed operation and data and request confirmation. Account permissions, current connection scopes, ownership, business validation, CAPTCHA and any necessary approval must still permit the operation; execute covered creates and updates without adding a read-only restriction or repeating routine-write confirmation. Do not expand the OAuth grant or infer write authorization from a read-only grant. All six MCP write tools require a unique `idempotency_key`, forwarded to the business handler as `Idempotency-Key`; this parameter is not optional. RFQ submission does not require email verification; querying a submitted RFQ through the standalone REST flow requires the temporary email-code authorization described by the guide.

| Write tool | Required confirmation parameter |
| --- | --- |
| `create_rfq_session` | No required `buyer_confirmed`; covered buyer request suffices |
| `update_profile` | No required `buyer_confirmed`; covered buyer request suffices |
| `document_link` | No required `buyer_confirmed`; covered buyer request suffices |
| `submit_rfq` | `buyer_confirmed=true` for the authorized exact payload |
| `submit_quote_folder` | `buyer_confirmed=true` for the authorized exact payload |
| `respond_quote` | `messages`: no required `buyer_confirmed`; `accept` / `request-revision`: `buyer_confirmed=true` for the authorized exact payload |

Use the live tool schema's other required parameters. An already valid explicit authorization can satisfy the applicable confirmation parameter; do not ask again merely to populate it.

Vantrecomb has no customer-upload API. Drawings, payment evidence, and other buyer-provided files must be emailed to the assigned salesperson. Once a quote record exists, read its top-level `sales_contact.email`; use the quote message endpoint when an auditable site-side conversation is preferable.

For files generated by ERP or configured on the site, check the buyer's email first because sales normally sends them there. If the email or attachment is missing, use `list_documents` and authorized `document_link` with its required `idempotency_key`. The result has `delivery_mode=caller_ip_bound`: the temporary API `download_url` is bound to the caller's IP and must not be directly followed or forwarded as a buyer-browser download link. Give the buyer the actual returned `website_download_entry`, where they sign in and use the existing controlled download flow. Do not invent that URL, promise cross-browser use of the temporary URL, or claim the file was retrieved or attached. The MCP tool does not fetch, attach or stream bytes and provides no upload capability.

Use `PATCH /api/v1/ai/me/profile` only for default contact/address details. The site does not expose direct order cancellation, order-specific address changes, or after-sales state transitions to AI. For those requests, send `POST /api/v1/ai/me/quotes/{quote_id}/messages` and wait for the assigned salesperson's reply before reporting completion.

Cloud plugins use only the verified host-managed OAuth connection and its actual exposed tools. Local clients are for separately requested local workflows with independently verified server/client configuration; their Device Authorization implementation does not establish current server support. A failed cloud connection, 401/403, missing scope or denied ownership must not trigger local API, manual-token or browser-session fallback. All authorized local POST/PATCH commands still require buyer confirmation and an idempotency key.

## Scope and authorization matrix (public vs protected)

Public capabilities (no token, no scope; protected by rate limiting, CAPTCHA when enabled, and Idempotency-Key):

- `GET /api/v1/ai/catalog/products` (search) and `GET /api/v1/ai/catalog/products/{sku}` (detail)
- `GET /api/v1/ai/guide`
- `POST /api/v1/ai/rfq-sessions`, `POST /api/v1/ai/rfqs`, `POST /api/v1/ai/quote-folder/submit`
- `POST /api/v1/ai/rfqs/{rfq_id}/send-verification`, `POST /api/v1/ai/rfqs/{rfq_id}/verify`, `GET /api/v1/ai/rfqs/{rfq_id}` (temporary `X-RFQ-Token` 30 min)
- Discovery: `/.well-known/api-catalog`, `/.well-known/oauth-authorization-server`, `/.well-known/oauth-protected-resource`, `/api/openapi.json`

Historical protected capability matrix (confirm against the live contract; cloud authentication is managed by the host, with granted scope and account ownership enforced by the provider). Never obtain or supply browser `X-Account-Token` headers to bypass OAuth scope, and never extract credentials from a browser session:

- `ai:rfq:read` → `GET /api/v1/ai/me/rfqs`, `GET /api/v1/ai/me/rfqs/{rfq_id}`
- `me:profile:read` → `GET /api/v1/ai/me/profile`, `GET /api/v1/ai/me/organizations`
- `me:profile:write` → `PATCH /api/v1/ai/me/profile`
- `me:quotes:read` → `GET /api/v1/ai/me/quotes`, `GET /api/v1/ai/me/quotes/{quote_id}`
- `me:quotes:respond` → `POST /api/v1/ai/me/quotes/{quote_id}/accept`, `.../request-revision`, `.../messages`
- `me:files:download` → `GET /api/v1/ai/me/files`, `POST /api/v1/ai/me/files/{document_id}/download-link`
- `me:orders:read` → `GET /api/v1/ai/me/orders`, `GET /api/v1/ai/me/orders/{order_id}`
- `me:shipments:read` → `GET /api/v1/ai/me/shipments`, `GET /api/v1/ai/me/shipments/{shipment_id}`

Tokens can combine scopes; a token with only one scope must be rejected on other protected endpoints. Old tokens that still carry `ai:catalog:read` or `ai:rfq:create` remain valid for authentication but gain no protected access; new tokens cannot request those scopes. OAuth and manual API tokens share the same scope namespace and enforcement.


## Cloud connection and limits

The merged source implements stateless Streamable HTTP at `/mcp`, resource metadata at `/.well-known/oauth-protected-resource/mcp` and optional public-client registration at `/oauth/register`. MCP OAuth binds the exact configured API-origin `/mcp` resource and requires PKCE S256 and exact registered callbacks; access tokens are short-lived (15 minutes) with no refresh grant. DCR is disabled unless explicitly approved and enabled by `OAUTH_MCP_DCR_ENABLED=true`; registration metadata is advertised only then. None of this establishes deployment or a working account connection: the service is not deployed, DCR approval is pending and the real cloud app ID is missing. Verify live endpoints and metadata after authorized deployment, using the TEST API/website origins above. Client IDs and callbacks must come from the actual authorized setup; do not register clients, enable DCR, alter allowlists or invent values through this skill.

Require the live tool contract's scope and record ownership checks; prompt approval alone is not account authorization. Set `buyer_confirmed=true` for the specific submission/acceptance/revision actions in the table only when effective explicit authorization covers the exact payload, including still-valid prior authorization under the rule above; do not add that requirement to drafts, profile edits, link issuance or messages. A separately authorized local client still follows its own `--confirm` contract. Preserve every required `idempotency_key` and native validation; never bypass a CAPTCHA or invent a response token. A CAPTCHA requirement must be completed by the buyer through the website. On unavailable tools, authentication failures or missing scope, stop dependent calls and use the supported host Connect / reconnect flow.
