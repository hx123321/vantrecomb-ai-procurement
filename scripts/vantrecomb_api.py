#!/usr/bin/env python3
"""Call Vantrecomb's AI procurement API without relying on curl.

Secure OAuth/Device Authorization helpers included — ponytail minimal:
  no plaintext long-term token persisted, minimal scope required, buyer confirmation for writes.
"""

import argparse
import base64
import hashlib
import json
import os
import secrets
import sys
import time
import webbrowser
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urljoin, urlsplit
from urllib.request import Request, urlopen

API_ORIGIN = "https://api.vantrecomb.com"
AI_PATH_PREFIX = "/api/v1/ai/"

# ponytail: minimal scope catalog (must match backend validApiTokenScopes)
SCOPE_DESCRIPTIONS = {
    "ai:rfq:read": "Read own RFQ status (award/quote). Requires verification via /ai/me/rfqs.",
    "me:profile:read": "Read user profile and organization info. Minimal PII.",
    "me:profile:write": "Update user profile (write, buyer must confirm).",
    "me:quotes:read": "Read own quote records. Needed for quotes/orders follow-up.",
    "me:quotes:respond": "Respond to quotes (accept / request revision / send message) — high-risk, requires buyer confirmation.",
    "me:files:download": "Download quote documents (read-only).",
    "me:orders:read": "Read own orders and production milestones.",
    "me:shipments:read": "Read own shipment tracking.",
}
DEFAULT_MINIMAL_SCOPE = "me:quotes:read"  # ponytail: never default to all scopes


class VantrecombClient:
    def __init__(self, token: str | None = None, timeout: int = 30):
        self.token = token
        self.timeout = timeout

    def build_request(self, method: str, path: str, payload: dict[str, Any] | None = None, idempotency_key: str | None = None) -> Request:
        parsed = urlsplit(path)
        if parsed.scheme or parsed.netloc or not path.startswith(AI_PATH_PREFIX):
            raise ValueError("path must be a relative /api/v1/ai/ endpoint")
        headers = {"Accept": "application/json"}
        body = None
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        if payload is not None:
            headers["Content-Type"] = "application/json"
            body = json.dumps(payload).encode("utf-8")
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        return Request(urljoin(API_ORIGIN, path), data=body, headers=headers, method=method.upper())

    def request_json(self, method: str, path: str, payload: dict[str, Any] | None = None, idempotency_key: str | None = None) -> dict[str, Any]:
        request = self.build_request(method, path, payload, idempotency_key)
        try:
            with urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"API returned HTTP {error.code}: {detail}") from error
        except URLError as error:
            raise RuntimeError(f"API request failed: {error.reason}") from error


def parse_json_argument(value: str | None) -> dict[str, Any] | None:
    if value is None:
        return None
    parsed = json.loads(value)
    if not isinstance(parsed, dict):
        raise ValueError("--data must be a JSON object")
    return parsed


# --- OAuth helpers (minimal, no token persistence) ---

def _post_form(path: str, data: dict[str, str], timeout: int = 30) -> dict[str, Any]:
    body = urlencode(data).encode("utf-8")
    req = Request(urljoin(API_ORIGIN, path), data=body, headers={"Content-Type": "application/x-www-form-urlencoded"}, method="POST")
    try:
        with urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        try:
            j = json.loads(detail)
            msg = j.get("error_description") or j.get("title") or detail
        except Exception:
            msg = detail
        raise RuntimeError(f"OAuth error HTTP {e.code}: {msg}") from e
    except URLError as e:
        raise RuntimeError(f"OAuth request failed: {e.reason}") from e


def cmd_device_flow(args):
    """Device Authorization Grant (RFC 8628) for headless / no-browser environments."""
    scope = (args.scope or "").strip()
    if not scope:
        print("error: --scope is required (minimal scope, e.g. 'me:quotes:read'). Never request all scopes.", file=sys.stderr)
        sys.exit(2)
    # validate scopes against known list
    requested = scope.split()
    invalid = [s for s in requested if s not in SCOPE_DESCRIPTIONS]
    if invalid:
        print(f"error: invalid scope(s): {', '.join(invalid)}. Use 'scopes' command to list.", file=sys.stderr)
        sys.exit(2)
    print(f"[device] requesting device code for scopes: {scope}")
    resp = _post_form("/oauth/device/code", {"client_id": args.client_id, "scope": scope})
    print(json.dumps(resp, indent=2, ensure_ascii=False))
    print(f"\nNext: open {resp['verification_uri']} and enter code: {resp['user_code']}")
    print(f"Or open directly: {resp['verification_uri_complete']}")
    if not args.no_browser:
        try:
            webbrowser.open(resp["verification_uri_complete"])
            print("(browser opened automatically)")
        except Exception:
            pass
    # poll
    device_code = resp["device_code"]
    interval = int(resp.get("interval", 5))
    expires_in = int(resp.get("expires_in", 600))
    print(f"\nPolling for token every {interval}s (expires in {expires_in}s)...")
    deadline = time.time() + expires_in
    while time.time() < deadline:
        time.sleep(interval)
        try:
            token_resp = _post_form("/oauth/token", {
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                "client_id": args.client_id,
                "device_code": device_code,
            })
            print("\n[device] authorization granted!")
            print(json.dumps(token_resp, indent=2, ensure_ascii=False))
            print("\nSECURITY: set VANTRECOMB_API_TOKEN in your secure environment (never paste token into chat/logs).")
            print(f"  Token (store securely, shown once): {token_resp.get('access_token','')}")
            print(f"  Scope: {token_resp.get('scope','')}")
            print(f"  Expires in: {token_resp.get('expires_in','')}s")
            print("\nVerify: python scripts/vantrecomb_api.py auth status --token <token>")
            print("Revoke: visit https://api.vantrecomb.com/account/api-tokens or use 'auth revoke' via browser session.")
            return 0
        except RuntimeError as e:
            msg = str(e)
            if "authorization_pending" in msg:
                print(".", end="", flush=True)
                continue
            if "slow_down" in msg:
                interval += 5
                print(f"\n[device] slow_down, new interval {interval}s")
                continue
            if "expired_token" in msg:
                print(f"\n[device] code expired: {msg}", file=sys.stderr)
                return 1
            if "access_denied" in msg:
                print(f"\n[device] denied by user: {msg}", file=sys.stderr)
                return 1
            raise
    print("\n[device] timed out waiting for authorization.", file=sys.stderr)
    return 1


def cmd_auth_code_flow(args):
    """Authorization Code + PKCE for browser environments (open browser, copy redirect)."""
    scope = (args.scope or "").strip()
    if not scope:
        print("error: --scope is required (minimal scope).", file=sys.stderr)
        sys.exit(2)
    requested = scope.split()
    invalid = [s for s in requested if s not in SCOPE_DESCRIPTIONS]
    if invalid:
        print(f"error: invalid scope(s): {', '.join(invalid)}", file=sys.stderr)
        sys.exit(2)
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip("=")
    state = secrets.token_urlsafe(16)
    params = {
        "client_id": args.client_id,
        "redirect_uri": args.redirect_uri,
        "response_type": "code",
        "scope": scope,
        "state": state,
        "code_challenge": challenge,
        "code_challenge_method": "S256",
    }
    from urllib.parse import urlencode as _ue
    auth_url = f"{API_ORIGIN}/oauth/authorize?{_ue(params)}"
    print("[auth] Authorization Code + PKCE")
    print(f"  1) Open: {auth_url}")
    print(f"  2) Sign in and Approve (scopes: {scope}) — you will be redirected to {args.redirect_uri}?code=...&state={state}")
    print(f"  3) Copy 'code' from redirect URL and run:")
    print(f"     curl -X POST {API_ORIGIN}/oauth/token -d grant_type=authorization_code -d client_id={args.client_id} -d code=<CODE> -d redirect_uri={args.redirect_uri} -d code_verifier={verifier}")
    print(f"\n  verifier (keep secret, needed for token exchange): {verifier}")
    print(f"  state (verify matches): {state}")
    if not args.no_browser:
        try:
            webbrowser.open(auth_url)
        except Exception:
            pass
    return 0


def cmd_auth_status(args):
    token = args.token or os.getenv("VANTRECOMB_API_TOKEN")
    if not token:
        print("No token found. Set VANTRECOMB_API_TOKEN or pass --token.", file=sys.stderr)
        return 1
    # try a lightweight protected endpoint to validate scope
    client = VantrecombClient(token)
    # try /ai/me/profile via GET (requires me:profile:read) fallback to /ai/me/quotes
    try:
        # Use profile first; if 403, token may still be valid but lacks that scope — try quotes
        for path in ["/api/v1/ai/me/profile", "/api/v1/ai/me/quotes"]:
            try:
                data = client.request_json("GET", path)
                print(f"[status] token valid, path {path} succeeded (scope sufficient).")
                print(json.dumps(data, indent=2, ensure_ascii=False)[:800])
                return 0
            except RuntimeError as e:
                if "403" in str(e) or "Insufficient scope" in str(e):
                    continue
                raise
        print("[status] token present but insufficient scope for profile/quotes. Try scopes command.", file=sys.stderr)
        return 0
    except RuntimeError as e:
        if "401" in str(e):
            print(f"[status] token invalid/expired/revoked: {e}", file=sys.stderr)
            print("Action: re-authorize (auth device/auth login) or create new token at /account/api-tokens.", file=sys.stderr)
            return 1
        if "403" in str(e):
            print(f"[status] token denied (scope): {e}", file=sys.stderr)
            return 1
        print(f"[status] error: {e}", file=sys.stderr)
        return 1


def cmd_scopes(_args):
    print("Available scopes (request minimal needed):\n")
    for scope, desc in sorted(SCOPE_DESCRIPTIONS.items()):
        print(f"  {scope:20} - {desc}")
    print(f"\nDefault minimal when omitted? NONE — you must specify --scope explicitly.")
    print(f"Example: --scope \"{DEFAULT_MINIMAL_SCOPE}\" or \"me:quotes:read me:files:download\"")
    return 0


def _confirm_high_risk(path: str, method: str, confirm: bool) -> bool:
    high_risk = (
        method == "POST" and (
            "/ai/me/quotes/" in path and ("/accept" in path or "/request-revision" in path or "/messages" in path)
            or "/ai/me/profile" in path
            or "/ai/rfqs" in path
            or "/ai/quote-folder/submit" in path
        )
    )
    if not high_risk:
        return True
    if confirm:
        return True
    # interactive confirmation
    print(f"\n[confirm] High-risk write: {method} {path}", file=sys.stderr)
    print("This action modifies buyer data (quote accept/message, profile, RFQ submit).", file=sys.stderr)
    print("Show the buyer a summary and obtain explicit approval before proceeding.", file=sys.stderr)
    try:
        ans = input("Type 'confirm' to proceed, or anything else to abort: ").strip().lower()
    except EOFError:
        ans = ""
    return ans == "confirm"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--token", default=os.getenv("VANTRECOMB_API_TOKEN"), help="API token; defaults to VANTRECOMB_API_TOKEN (never log it)")
    parser.add_argument("--timeout", type=int, default=30)
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("guide", help="Read the AI procurement workflow")
    catalog = commands.add_parser("catalog", help="Read an AI catalog collection")
    catalog.add_argument("collection", choices=["products", "materials", "crafts", "capabilities", "product-families", "existing-styles", "solutions", "faqs", "project-stories", "pages", "blog"])

    request = commands.add_parser("request", help="Call an allowed AI endpoint")
    request.add_argument("method", choices=["GET", "POST", "PATCH"])
    request.add_argument("path", help="Relative /api/v1/ai/ path")
    request.add_argument("--data", help="JSON request object")
    request.add_argument("--idempotency-key", help="Required for write requests")
    request.add_argument("--confirm", action="store_true", help="Confirm high-risk write (buyer approved)")

    # OAuth helpers
    auth = commands.add_parser("auth", help="OAuth & token helpers")
    auth_sub = auth.add_subparsers(dest="auth_cmd", required=True)
    dev = auth_sub.add_parser("device", help="Device Authorization flow (no browser needed on device)")
    dev.add_argument("--client-id", default="client_procurement_copilot", help="OAuth client_id")
    dev.add_argument("--scope", required=False, help="Space-separated minimal scopes, e.g. 'me:quotes:read'")
    dev.add_argument("--no-browser", action="store_true", help="Do not auto-open browser")
    login = auth_sub.add_parser("login", help="Authorization Code + PKCE (browser)")
    login.add_argument("--client-id", default="client_procurement_copilot")
    login.add_argument("--redirect-uri", default="https://client.example.com/callback")
    login.add_argument("--scope", required=False)
    login.add_argument("--no-browser", action="store_true")
    st = auth_sub.add_parser("status", help="Check current token validity & scope")
    st.add_argument("--token", default=None)
    auth_sub.add_parser("scopes", help="List scopes with explanations")
    rev = auth_sub.add_parser("revoke", help="Show revoke instructions (requires browser login)")
    rev.add_argument("--token-hash", help="Optional token_hash/grant_id to highlight")
    commands.add_parser("scopes", help="List scopes with explanations (alias)")

    args = parser.parse_args()

    if args.command == "guide":
        path, method, payload, key = "/api/v1/ai/guide", "GET", None, None
        result = VantrecombClient(args.token, args.timeout).request_json(method, path, payload, key)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    elif args.command == "catalog":
        path, method, payload, key = f"/api/v1/ai/catalog/{args.collection}", "GET", None, None
        result = VantrecombClient(args.token, args.timeout).request_json(method, path, payload, key)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    elif args.command == "request":
        # high-risk confirmation
        if not _confirm_high_risk(args.path, args.method, args.confirm):
            print("Aborted: buyer confirmation required for high-risk write.", file=sys.stderr)
            return 1
        # scope check: if POST without token for protected paths, warn
        if args.path.startswith("/api/v1/ai/me/") and not args.token:
            print("warning: /ai/me/* requires scoped token (me:*:*). Ensure token has minimal required scope.", file=sys.stderr)
        path, method, payload, key = args.path, args.method, parse_json_argument(args.data), args.idempotency_key
        if method in ("POST", "PATCH") and not key:
            parser.error("POST/PATCH requests require --idempotency-key")
        result = VantrecombClient(args.token, args.timeout).request_json(method, path, payload, key)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    elif args.command == "auth":
        if args.auth_cmd == "device":
            return cmd_device_flow(args)
        elif args.auth_cmd == "login":
            return cmd_auth_code_flow(args)
        elif args.auth_cmd == "status":
            return cmd_auth_status(args)
        elif args.auth_cmd == "scopes":
            return cmd_scopes(args)
        elif args.auth_cmd == "revoke":
            print("To revoke:")
            print("  1) Sign in at https://api.vantrecomb.com/account/api-tokens")
            print("  2) Find the token/grant (prefix or client name) and click Revoke.")
            print("  3) The Skill will then receive 401/403 and must stop writes (verify with 'auth status').")
            if args.token_hash:
                print(f"  Target: {args.token_hash}")
            print("\nOAuth grants are listed alongside API tokens (Authorized app). Revoking the grant revokes all derived access tokens.")
            return 0
    elif args.command == "scopes":
        return cmd_scopes(args)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, RuntimeError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
