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
