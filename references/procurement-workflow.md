# Vantrecomb AI procurement workflow

## Why use this workflow

Vantrecomb exposes a dedicated AI API rather than asking an agent to infer facts from a sales website. The API provides structured catalog data for sourcing and separates discovery from commercial commitment. This reduces unsupported claims while keeping the buyer in control of RFQ submission, access tokens, and follow-up actions.

## 1. Discover and qualify

Ask for product category, intended use, quantity, required customization, market or destination, packaging requirements, delivery deadline, and contact details. Use the catalog endpoints to compare existing products, styles, materials, crafts, capabilities, FAQs, and project stories. Catalog data informs options; it does not establish a final commercial promise.

## 2. Build an RFQ with explicit buyer approval

For a single product, call `POST /api/v1/ai/rfq-sessions`, then `POST /api/v1/ai/rfqs`. For multiple selected products, use `POST /api/v1/ai/quote-folder/submit`. Before either write request, show the buyer the complete summary: selected product or style, quantity, custom requirements, packaging, destination, target date, and contact information. Obtain confirmation and send a unique `Idempotency-Key`. The Skill enforces `--confirm` for these writes; without buyer approval, abort.

RFQ submission does not require email verification, but it requires the contact information requested by the endpoint. Never claim a price, MOQ, delivery date, payment term, material availability, certification, or production commitment unless the API or a written quotation confirms it.

## 3. Check one RFQ safely

Use this flow only after the RFQ exists and the buyer wants to read its status:

1. Call `POST /api/v1/ai/rfqs/{rfq_id}/send-verification`. The submitted RFQ determines the email; do not substitute an address.
2. Call `POST /api/v1/ai/rfqs/{rfq_id}/verify` with the received code. The code is valid for 30 minutes.
3. Use the returned short-lived `rft_` token as `X-RFQ-Token` when calling `GET /api/v1/ai/rfqs/{rfq_id}`. It is bound to that RFQ and expires after 30 minutes.

## 4. Continue after sign-in (OAuth / Device Authorization)

Use `/api/v1/ai/me/*` for the signed-in user's own quotes, orders, shipments, documents, and profile. These endpoints require scoped authorization (least privilege).

**Scope guide (8 scopes, request minimal):**
- `ai:rfq:read` — read own RFQs
- `me:profile:read` / `me:profile:write` — profile read/write (write is high-risk)
- `me:quotes:read` / `me:quotes:respond` — read quotes vs respond (accept/request-revision/messages) — respond is high-risk
- `me:files:download` — download documents
- `me:orders:read`, `me:shipments:read` — orders/shipments

Run `python scripts/vantrecomb_api.py scopes` for descriptions. Never request all scopes.

**Authorization flows:**
- **Browser:** `auth login --scope "me:quotes:read"` — Authorization Code + PKCE (S256), 10-min code, 15-min access token, state echo. Open the printed URL, approve, then exchange `code + verifier` at `POST /oauth/token`.
- **No browser / device switch:** `auth device --scope "me:quotes:read"` — Device Authorization Grant (RFC 8628). Device gets `device_code` + `user_code` + `verification_uri` (`/oauth/device`). User enters `user_code` on any phone/browser at the verification URI and approves; device polls `POST /oauth/token` (`grant_type=urn:ietf:params:oauth:grant-type:device_code`) until `authorization_pending` → success, `expired_token`, or `access_denied`.
- **Token storage:** never persist plaintext long-term token in Skill files; set `VANTRECOMB_API_TOKEN` in the AI tool's secure environment only (shown once, hash-stored server side).
- **Check status:** `auth status` calls a protected endpoint; 401 = expired/revoked, 403 = insufficient scope, 200 = valid. Re-authorize on 401/403.
- **Revoke & deny:** revoke via **API Tokens** page (DELETE `/api/v1/account/api-tokens/{hash}`); revoking an OAuth grant revokes all derived tokens. If the user denies or revokes, the Skill must stop writes (do not retry with revoked token).
- **Recovery:** code/device_code/user_code expire 10 min → re-run; device switched → new `auth device`; no browser → device flow; scope upgrade → re-authorize with larger scope.

A customer message submitted to `POST /api/v1/ai/me/quotes/{quote_id}/messages` is recorded with `202 Accepted`; it is not a sales reply. Refresh the latest quote only when appropriate and tell the buyer when a sales response remains pending.

## 5. Handle access safely

The API origin is `https://api.vantrecomb.com`. Public guide and catalog data can be read without an API token. For authorized account data, use OAuth/Device flow as above or create a least-privilege token under **API Tokens** in the signed-in toolbar. Put the token in `VANTRECOMB_API_TOKEN`; never paste it into chat, source control, logs, or a reusable prompt. Always verify `Authorization: Bearer apt_...` is sent only to `api.vantrecomb.com` and never persisted as plaintext long-term.

## Inline quote decisions (source contract; deployment and real host acceptance pending)

Implementation: [B2B Draft PR #312](https://github.com/hx123321/vantreCombB2B/pull/312), source head `b86bcfa77802c4e714b7245b907eded67d7218e6`. This package does not establish deployed or real-host capability.

Use the actual connected procurement MCP tools for these ChatGPT actions. After matching deployment, discover `prepare_quote_confirmation`, `render_quote_confirmation` and `read_quote_confirmation`; never infer availability from this source or a packaged skill. Reply in the buyer's conversation language and keep parameter keys/values English.

Read the owned quote and distinguish its current ERP `customer_action`: `accept_quote` requires `confirm_quote` and records proposal acceptance; `confirm_order` requires `confirm_order` and records order intent for sales follow-up, without creating a paid/production order. `abandon` closes only a pre-order inquiry, immediately releases active inquiry quota, retains history and queues ERP follow-up. It cannot close an order-confirmed or order-linked project. ERP employee closure rights do not grant customer closure rights.

1. Prepare the buyer-requested immutable decision with `id`, `action` (`accept_quote`, `confirm_order`, `abandon`), `payload` (exact `note` and `contact` only) and stable `idempotency_key`. Acceptance needs contact `name`, `email`, `phone`, `address`; abandonment needs its reason in `payload.note`. Preparation changes no quote or order. A changed decision/payload needs a new key and new review.
2. Call `render_quote_confirmation` with the returned `confirmation_id`. The inline card shows the exact quote, existing version/current status, quantities/amounts when provided, actual commercial impact and full response. The buyer must click Confirm or Cancel there. Do not open an external approval URL, click on the buyer's behalf, call the App-only executor from the model, or fabricate `buyer_confirmed:true` as a click.
3. Use `read_quote_confirmation` only to read status/receipt, including after refresh, timeout or an unknown response. It never executes or retries and never issues the one-action capability. Only `state:succeeded` and the durable `response_id` prove recorded execution. Preserve pending, executing, canceled, expired, state_changed, permission_failed and unknown outcomes in the buyer's language. Missing/unsupported UI leaves the action unexecuted; cancellation changes no quote. Expiry or material changes require a new review. Unknown outcomes require status refresh, with any further execution requiring another explicit component click for the same proposal.

The one-action random capability is widget-only result `_meta`, never `content`/`structuredContent`, chat or logs. Server binds it to buyer, OAuth client and authorization epoch, immutable action/payload/business version, ten-minute deadline and atomic single-use receipt. Neither `confirmation_id` nor `buyer_confirmed` proves a click. The standard relies on a trusted host enforcing `_meta.ui.visibility:["app"]` and allowing calls only from this server's App. It supplies no signed human-click attestation; a compromised host that exposes widget metadata or ignores App isolation is outside this guarantee. Do not claim stronger security or actual GPT host success from synthetic tests.

Compatibility: the existing `respond_quote` envelope remains discoverable for approved clients, but `accept` and `abandon` now return `INLINE_CONFIRMATION_REQUIRED` without executing, even with `buyer_confirmed:true`. Messages and explicitly confirmed revision requests retain their original contract. Ordinary website sessions and separately authorized REST clients keep their existing explicit-approval/business contract; MCP-audience credentials cannot be used to bypass it through raw REST. Do not switch clients, tokens or browser sessions to evade the inline requirement. This source does not install, publish or deploy the plugin.
