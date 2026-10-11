#!/usr/bin/env python3
"""Call the Vantrecomb AI procurement API without relying on curl."""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urljoin, urlsplit
from urllib.request import Request
from procurement_auth import (urlopen, SameOriginRedirectHandler, load_config, redact, save_session,
                              read_session, clear_session, auth_device, oauth_form, SCOPES)

load_config()

DEFAULT_API_ORIGIN = "https://api.vantrecomb.com"
AI_PATH_PREFIX = "/api/v1/ai/"
PRIVATE_DOWNLOAD_PREFIX = "/api/v1/private-downloads/"


def validate_origin(origin: str) -> str:
    parsed = urlsplit(origin)
    is_loopback = parsed.hostname in {"127.0.0.1", "localhost", "::1"}
    if parsed.username or parsed.password or not parsed.netloc or parsed.path not in {"", "/"} or parsed.query or parsed.fragment:
        raise ValueError("origin must contain only a scheme and host")
    if parsed.scheme != "https" and not (parsed.scheme == "http" and is_loopback):
        raise ValueError("origin must use HTTPS; HTTP is allowed only for loopback testing")
    return origin.rstrip("/")


class VantrecombClient:
    def __init__(
        self,
        token: str | None = None,
        rfq_token: str | None = None,
        timeout: int = 30,
        origin: str = DEFAULT_API_ORIGIN,
    ):
        self.token = token
        self.rfq_token = rfq_token
        self.timeout = timeout
        self.origin = validate_origin(origin)

    def build_request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
        idempotency_key: str | None = None,
    ) -> Request:
        parsed = urlsplit(path)
        if parsed.scheme or parsed.netloc or parsed.fragment or not path.startswith(AI_PATH_PREFIX) or any(part in {".", ".."} for part in parsed.path.split("/")) or "%2e" in path.lower() or "%2f" in path.lower():
            raise ValueError("path must be a relative /api/v1/ai/ endpoint")
        headers = {"Accept": "application/json, text/markdown;q=0.9, text/plain;q=0.8"}
        body = None
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        if self.rfq_token:
            headers["X-RFQ-Token"] = self.rfq_token
        if payload is not None:
            headers["Content-Type"] = "application/json"
            body = json.dumps(payload).encode("utf-8")
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        return Request(urljoin(self.origin + "/", path.lstrip("/")), data=body, headers=headers, method=method.upper())

    def request(self, method: str, path: str, payload: dict[str, Any] | None = None, idempotency_key: str | None = None) -> Any:
        request = self.build_request(method, path, payload, idempotency_key)
        try:
            with urlopen(request, timeout=self.timeout) as response:
                body = response.read()
                content_type = response.headers.get_content_type()
                if content_type == "application/json" or content_type.endswith("+json"):
                    return json.loads(body.decode("utf-8"))
                return body.decode("utf-8")
        except HTTPError as error:
            if error.code == 401:
                clear_session(self.origin)
            raise RuntimeError(f"API returned HTTP {error.code}: {redact(error.read().decode('utf-8', errors='replace'))}") from None
        except URLError as error:
            raise RuntimeError(f"API request failed: {error.reason}") from error

    def request_json(self, method, path, payload=None, idempotency_key=None):
        return self.request(method, path, payload, idempotency_key)

    def download(self, document_id: str, destination: Path, idempotency_key: str) -> Path:
        if destination.exists():
            raise ValueError(f"refusing to overwrite existing file: {destination}")
        endpoint = f"/api/v1/ai/me/files/{quote(document_id, safe='')}/download-link"
        result = self.request("POST", endpoint, {}, idempotency_key)
        if not isinstance(result, dict) or not isinstance(result.get("download_url"), str):
            raise RuntimeError("API response did not contain download_url")
        download_path = result["download_url"]
        parsed = urlsplit(download_path)
        if parsed.scheme or parsed.netloc or not parsed.path.startswith(PRIVATE_DOWNLOAD_PREFIX):
            raise RuntimeError("API returned an unsafe download URL")
        request = Request(urljoin(self.origin + "/", download_path.lstrip("/")), headers={"Accept": "*/*"}, method="GET")
        try:
            with urlopen(request, timeout=self.timeout) as response:
                data = response.read()
        except HTTPError as error:
            raise RuntimeError(f"download returned HTTP {error.code}: {error.read().decode('utf-8', errors='replace')}") from error
        except URLError as error:
            raise RuntimeError(f"download failed: {error.reason}") from error
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
        return destination


def parse_json_argument(value: str | None) -> dict[str, Any] | None:
    if value is None:
        return None
    parsed = json.loads(value)
    if not isinstance(parsed, dict):
        raise ValueError("--data must be a JSON object")
    return parsed


def print_result(result: Any) -> None:
    result = redact(result)
    if isinstance(result, str):
        print(result)
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--origin", default=os.getenv("VANTRECOMB_API_ORIGIN", DEFAULT_API_ORIGIN), help="API origin; HTTP is accepted only for localhost")
    parser.add_argument("--timeout", type=int, default=30)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("guide", help="Read the AI procurement workflow")
    catalog = subparsers.add_parser("catalog", help="Search the AI product catalog")
    catalog.add_argument("collection", choices=["products"])
    product = subparsers.add_parser("product", help="Read one product's structured AI view")
    product.add_argument("identifier", help="Product sku, style_id or slug")
    product.add_argument("--locale", default="en", help="Language code, e.g. en/zh-CN/pt-BR")
    subparsers.add_parser("files", help="List downloadable ERP/site files for the account")
    download = subparsers.add_parser("download", help="Download an authorized ERP/site file")
    download.add_argument("document_id", help="File reference returned by the files command")
    download.add_argument("--output", required=True, type=Path, help="Local output path")
    download.add_argument("--idempotency-key", required=True)
    download.add_argument("--confirm", action="store_true", required=True, help="Buyer approved the document request")
    request = subparsers.add_parser("request", help="Call an allowed AI endpoint")
    request.add_argument("method", choices=["GET", "POST", "PATCH"])
    request.add_argument("path", help="Relative /api/v1/ai/ path")
    request.add_argument("--data", help="JSON request object")
    request.add_argument("--idempotency-key", help="Required for POST/PATCH requests")
    request.add_argument("--confirm", action="store_true", help="Buyer approved the exact write payload")
    subparsers.add_parser("scopes", help="List protected scopes")
    auth = subparsers.add_parser("auth", help="Secure account connection")
    flows = auth.add_subparsers(dest="auth_command", required=True)
    for command in ("login", "device"):
        flow = flows.add_parser(command, help="Approve through Vantrecomb's device authorization page")
        flow.add_argument("--scope", required=True)
        flow.add_argument("--client-id", default=os.getenv("VANTRECOMB_OAUTH_CLIENT_ID", "client_procurement_copilot"))
        flow.add_argument("--no-browser", action="store_true")
    flows.add_parser("status")
    flows.add_parser("logout", help="Clear the local session; server grants remain until revoked")
    flows.add_parser("revoke", help="Explain how to revoke in the buyer account")
    args = parser.parse_args(argv)
    args.origin = validate_origin(args.origin)
    if args.command == "scopes":
        print("\n".join(SCOPES))
        return 0
    if args.command == "auth":
        if args.auth_command in {"login", "device"}:
            return auth_device(args)
        if args.auth_command == "logout":
            clear_session(args.origin)
            print("Local session cleared. Server authorization has not been revoked.")
            return 0
        if args.auth_command == "revoke":
            print("Sign in to Vantrecomb and revoke the authorized app through API Tokens, then run auth logout locally.")
            return 0
    session = read_session(args.origin)
    args.token = os.getenv("VANTRECOMB_API_TOKEN") if "VANTRECOMB_API_TOKEN" in os.environ else session.get("access_token")
    args.rfq_token = os.getenv("VANTRECOMB_RFQ_TOKEN")
    if args.command == "request" and args.method in {"POST", "PATCH"} and not args.confirm:
        parser.error("write requests require --confirm after explicit buyer approval")

    client = VantrecombClient(args.token, args.rfq_token, args.timeout, args.origin)
    if args.command == "auth":
        if not args.token:
            raise ValueError("No active session. Run auth login with minimal scopes.")
        scope = session.get("scope", "").split()
        endpoints = [SCOPES[s] for s in scope if s in SCOPES and SCOPES[s]] or ["/api/v1/ai/me/profile", "/api/v1/ai/me/quotes", "/api/v1/ai/me/files"]
        for endpoint in endpoints:
            try:
                client.request("GET", endpoint)
                print("Session verified; buyer-owned endpoint accessible.")
                return 0
            except RuntimeError as error:
                if "HTTP 403" in str(error):
                    continue
                raise
        raise ValueError("No read scope available to verify; authorize the read scope needed for the task.")
    if args.command == "guide":
        print_result(client.request("GET", "/api/v1/ai/guide"))
    elif args.command == "catalog":
        print_result(client.request("GET", f"/api/v1/ai/catalog/{args.collection}"))
    elif args.command == "product":
        path = f"/api/v1/ai/catalog/products/{quote(args.identifier, safe='')}"
        print_result(client.request("GET", f"{path}?locale={quote(args.locale)}"))
    elif args.command == "files":
        print_result(client.request("GET", "/api/v1/ai/me/files"))
    elif args.command == "download":
        print(client.download(args.document_id, args.output, args.idempotency_key).resolve())
    else:
        if args.method in {"POST", "PATCH"} and not args.idempotency_key:
            parser.error(f"{args.method} requests require --idempotency-key")
        print_result(client.request(args.method, args.path, parse_json_argument(args.data), args.idempotency_key))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, RuntimeError, json.JSONDecodeError, OSError) as error:
        print(f"error: {redact(str(error))}", file=sys.stderr)
        raise SystemExit(1)
