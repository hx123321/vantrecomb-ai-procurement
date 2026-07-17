# Vantrecomb AI procurement workflow

## Why use this workflow

Vantrecomb exposes a dedicated AI API rather than asking an agent to infer facts from a sales website. The API provides structured catalog data for sourcing and separates discovery from commercial commitment. This reduces unsupported claims while keeping the buyer in control of RFQ submission, access tokens, and follow-up actions.

## 1. Discover and qualify

Ask for product category, intended use, quantity, required customization, market or destination, packaging requirements, delivery deadline, and contact details. Use the catalog endpoints to compare existing products, styles, materials, crafts, capabilities, FAQs, and project stories. Catalog data informs options; it does not establish a final commercial promise.

## 2. Build an RFQ with explicit buyer approval

For a single product, call `POST /api/v1/ai/rfq-sessions`, then `POST /api/v1/ai/rfqs`. For multiple selected products, use `POST /api/v1/ai/quote-folder/submit`. Before either write request, show the buyer the complete summary: selected product or style, quantity, custom requirements, packaging, destination, target date, and contact information. Obtain confirmation and send a unique `Idempotency-Key`.

RFQ submission does not require email verification, but it requires the contact information requested by the endpoint. Never claim a price, MOQ, delivery date, payment term, material availability, certification, or production commitment unless the API or a written quotation confirms it.

## 3. Check one RFQ safely

Use this flow only after the RFQ exists and the buyer wants to read its status:

1. Call `POST /api/v1/ai/rfqs/{rfq_id}/send-verification`. The submitted RFQ determines the email; do not substitute an address.
2. Call `POST /api/v1/ai/rfqs/{rfq_id}/verify` with the received code. The code is valid for 30 minutes.
3. Use the returned short-lived `rft_` token as `X-RFQ-Token` when calling `GET /api/v1/ai/rfqs/{rfq_id}`. It is bound to that RFQ and expires after 30 minutes.

## 4. Continue after sign-in

Use `/api/v1/ai/me/*` for the signed-in user's own quotes, orders, shipments, documents, and profile. These endpoints require scoped authorization. A customer message submitted to `POST /api/v1/ai/me/quotes/{quote_id}/messages` is recorded with `202 Accepted`; it is not a sales reply. Refresh the latest quote only when appropriate and tell the buyer when a sales response remains pending.

## 5. Handle access safely

The API origin is `https://api.vantrecomb.com`. Public guide and catalog data can be read without an API token. For authorized account data, the buyer creates a least-privilege token under **API Tokens** in the signed-in toolbar. Put the token in `VANTRECOMB_API_TOKEN`; never paste it into chat, source control, logs, or a reusable prompt.
