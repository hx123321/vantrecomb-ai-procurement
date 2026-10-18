# Separately requested local API transport

This reference applies only to explicit local API tasks; connected procurement work uses native MCP and the core SKILL rules. Runtime `procurement_guide`/OpenAPI own current endpoints, schemas, scopes and temporary RFQ authorization; do not maintain a second endpoint table here.

Use `scripts/vantrecomb_api.py guide`, then its `request METHOD /api/v1/ai/...` command with the discovered contract. `--data` carries JSON; writes require `--idempotency-key`. File delivery uses the wrapper's `files`/`download` commands and actual returned document ID, MIME and same-origin download link; no upload endpoint is implied.

The default origin is `https://api.vantrecomb.com`; only separately authorized local verification may set `VANTRECOMB_API_ORIGIN` to loopback HTTP. The wrapper rejects non-AI routes. Existing least-privilege credentials belong only in secure `VANTRECOMB_API_TOKEN` or temporary `VANTRECOMB_RFQ_TOKEN` environment configuration, never chat, source or history. Do not switch to manual tokens to evade native MCP conversation decisions or other denials. Missing credentials require the authorized connection flow, not collection from the user.
