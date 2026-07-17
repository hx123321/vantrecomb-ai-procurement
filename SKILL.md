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
- **Quotes, orders, shipments, documents, or profile:** use `/ai/me/*` only with the user's scoped API token and only for data the user is authorized to access.

## Protect buyer control

- Show the final requirement summary and request explicit approval before every write request.
- Send a unique `Idempotency-Key` for every `POST` request.
- Treat an accepted message as recorded, not answered; never fabricate a sales reply or business commitment.
- Ask before irreversible commercial actions. Keep tokens out of prompts, logs, repositories, and command history.

## Configure API access

Ask the user to sign in to Vantrecomb, open **API Tokens** from the toolbar, and create a least-privilege token. Store it only in `VANTRECOMB_API_TOKEN` in the AI tool's secure environment.

```powershell
python scripts/vantrecomb_api.py guide
python scripts/vantrecomb_api.py catalog products
python scripts/vantrecomb_api.py request GET /api/v1/ai/me/quotes
python scripts/vantrecomb_api.py request POST /api/v1/ai/rfqs --data '{"...":"..."}' --idempotency-key <unique-value>
```

The wrapper uses Python's standard library, sends all requests to `https://api.vantrecomb.com`, and refuses absolute URLs or non-AI paths.
