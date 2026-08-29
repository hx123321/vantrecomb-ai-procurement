---
name: vantrecomb-ai-procurement
description: Guide B2B buyers through Vantrecomb's AI-enabled sourcing workflow for custom combs and hotel amenities. Use when sourcing products, comparing materials or crafts, preparing a buyer-approved RFQ, checking authorized quotes, orders, shipments, documents, or configuring Vantrecomb API access without curl.
---

# Vantrecomb AI Procurement

Turn a buyer's requirements into a grounded sourcing workflow. Vantrecomb combines an AI-ready catalog with a controlled RFQ and post-quote workflow: the agent can discover and structure options, while the buyer remains in control of any submission or account action.

## Begin every procurement task

1. Read `references/procurement-workflow.md` before calling any endpoint.
2. Ask for the product type, quantity, customization, destination, target delivery date, and business contact. Mark unknown details instead of assuming them.
3. Call `python scripts/vantrecomb_api.py guide`, then query only `/api/v1/ai/*` endpoints.
4. Explain options using returned data. Never invent MOQ, material availability, price, lead time, certification, or sales commitment.

## Choose the right workflow

- **Explore a direction:** use `catalog` for products, styles, materials, crafts, capabilities, FAQs, or project stories.
- **One product RFQ:** create an RFQ session, present a concise buyer-facing summary, obtain confirmation, then submit the RFQ.
- **Several selected products:** use the AI quote-folder submission workflow after confirmation.
- **Check one submitted RFQ:** send the verification code, verify it, then use the short-lived RFQ token exactly as documented.
- **Quotes, orders, shipments, documents, or profile:** use `/ai/me/*` only with the user's scoped token and only for data the user is authorized to access.

## Protect buyer control

- Show the final requirement summary and request explicit approval before every write request.
- Send a unique `Idempotency-Key` for every `POST`/`PATCH` request.
- Treat an accepted message as recorded, not answered; never fabricate a sales reply or business commitment.
- Ask before irreversible commercial actions. Keep tokens out of prompts, logs, repositories, and command history.
- For `/ai/me/*` writes (`accept`, `request-revision`, `messages`, `PATCH profile`, `rfqs/quote-folder submit`), the Skill requires `--confirm` and an explicit buyer confirmation; denied/revoked tokens must stop writes.

## Configure API access (OAuth + least-privilege)

Use OAuth or Device Authorization — never handle plaintext long-term tokens in Skill files.

1. **Pick minimal scopes:** run `python scripts/vantrecomb_api.py scopes` to see 8 scopes. Always request the smallest set needed, never all. Example: `me:quotes:read` for reading quotes; add `me:files:download` only if files needed.
2. **Browser available:** `python scripts/vantrecomb_api.py auth login --scope "me:quotes:read" --redirect-uri https://client.example.com/callback` (PKCE S256). The Skill opens the authorization URL, user signs in, approves, then the Skill exchanges the code for a 15-minute `apt_` token (hash-stored server side).
3. **No browser / headless / device switch:** `python scripts/vantrecomb_api.py auth device --scope "me:quotes:read"` — shows `user_code` + `verification_uri` (`https://api.vantrecomb.com/oauth/device`). User completes approval on any phone/browser; device polls until granted/denied/expired.
4. **Legacy manual token (optional):** sign in → **API Tokens** (toolbar) → create least-privilege token → store only in `VANTRECOMB_API_TOKEN` secure env (never commit). Tokens are `apt_` and shown once.
5. **Check & revoke:** `python scripts/vantrecomb_api.py auth status` verifies token; `auth revoke` explains revocation via **API Tokens** page (revoking a grant revokes all derived tokens). After deny/revoke, Skill stops writes (expects 401/403).

**Boundaries & recovery:**
- `code` / `device_code` / `user_code` expire in 10 min → rerun `auth device`/`auth login`.
- Device switched or no browser → use Device flow on new device, same `user_code` verification works from any browser.
- Scope upgrade → re-authorize with larger scope (new device code or new auth URL).
- Expired/revoked token → `auth status` shows 401/403; re-authorize.

```powershell
python scripts/vantrecomb_api.py scopes
python scripts/vantrecomb_api.py auth device --scope "me:quotes:read"
python scripts/vantrecomb_api.py auth status
python scripts/vantrecomb_api.py guide
python scripts/vantrecomb_api.py catalog products
python scripts/vantrecomb_api.py request GET /api/v1/ai/me/quotes
python scripts/vantrecomb_api.py request POST /api/v1/ai/me/quotes/Q123/messages --data '{"note":"hello"}' --idempotency-key <unique> --confirm
```

The wrapper uses Python's standard library, sends all requests to `https://api.vantrecomb.com`, refuses absolute URLs or non-AI paths, never persists plaintext tokens, and enforces buyer confirmation for high-risk writes.
