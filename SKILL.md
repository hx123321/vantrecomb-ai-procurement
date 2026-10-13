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

## Design preview and response language

Answer in the language the buyer uses in the conversation. Parameter descriptions are English; keep all parameter keys, allowed values and the complete advanced StudioSnapshot schema unchanged.

Save multi-turn edits as private design versions without rebuilding geometry. Request a preview only when the buyer asks to view the design. Wait for that exact version's geometry state to be `succeeded` before describing it as rendered. Reuse unchanged geometry and queued/running tasks. Explain queue position and the existing cooldown's retry delay; do not repeatedly resubmit after failure, cancellation or timeout. Retry only after an explicit request. Keep the saved design and website preview link. Preview never creates an RFQ.

Geometry cache GLBs are shared public artifacts. Logo artwork, full snapshots and account records retain their existing ownership checks; credentials never appear in artifact URLs.

## Buyer Logo attachments and Library files

Before `upload_design_logo`, call the current `design_capabilities` for the selected SKU and read `customer_upload_policy`, the actual tool description and file schema. Explain the returned formats, encoded byte limit, edge/pixel/decoded-byte limits and static-image requirement in the buyer's conversation language. Do not maintain a separate numeric limit table in this skill. Inspect authorized metadata when available; reject a known unsupported format, animation, oversized file or excessive dimensions before calling. Missing size/dimension metadata is unknown, not a successful check; the server still validates bytes and decoded budgets. Never silently resize, compress, convert, crop or replace artwork. Obtain explicit authorization for any proposed transformation.

Use the official [Plugins file APIs](https://developers.openai.com/plugins/reference#file-apis). Both a buyer chat attachment and an authorized ChatGPT Library selection use the same `_meta["openai/fileParams"]=["file"]` chain. Top-level `file` has required `file_id` and `download_url`, optional `mime_type` and `file_name`; use the actual exposed host input (including an authorized prepared local path if that host expects one) and let the host inject the official fields. Never invent IDs/URLs, accept an arbitrary pasted URL as a host file, use GPT Actions `openaiFileIdRefs`, or assume a fixed signed-URL lifetime. A genuine current host download URL can be refreshed for the same file identity. Do not log, persist or share the signed URL.

Buyer OAuth, design ownership, a file ID and URL shape do not prove the caller is OpenAI. The reviewed provider policy requires separately verified OpenAI Connectors mTLS identity, using the published CA chain, client-auth usage and exact client SAN, on supplied files and receipt replay. In `verified_openai` mode, one reviewed deployment/configuration supports regional official temporary hosts without per-buyer hostname changes. HTTPS/TLS validation, all-address public-IP checks, a pinned resolved target, no redirects/proxies/credential forwarding, total timeout, byte and actual-format limits remain enforced. Never enable ingress or change CA trust, network, permissions, allowlists or the four preview settings from this skill.

Use the linked buyer's owned saved `design_id`, `me:designs:write`, an authorized file and a unique `idempotency_key`. Save first when needed. Existing successful private receipts recover under the same design/file identity, stable metadata and key before refetching an expired URL; current OAuth/ownership and verified host transport still apply. Changed artwork or metadata needs a separately authorized new key. A refreshed URL alone does not change file identity. Report `openai_file_caller_unverified`, format/size/download failures and website fallback as their actual stages, never upload success. Without a file, use the returned same-design website entry; a verified host file can also receive `attachment_ingress_not_enabled` while the operator gate is off. Only a successful private canonical asset receipt proves import. Place that canonical resource through an authorized complete snapshot update; upload does not create an RFQ, a design version or a rendered model.

Confirm matching deployed server code, current live schema and one-time secure ingress configuration before claiming availability. Source changes, local synthetic tests, a prepared Library file and real chat-file acceptance are separate evidence. If host file support, identity transport or deployment is missing, retain the actual private website fallback and explain the missing stage. See [official client identification](https://developers.openai.com/plugins/build/auth#client-identification); do not treat OAuth client labels as mTLS proof.
