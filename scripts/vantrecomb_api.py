#!/usr/bin/env python3
"""Call Vantrecomb's AI procurement API without relying on curl."""

import argparse
import json
import os
import sys
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen

API_ORIGIN = "https://api.vantrecomb.com"
AI_PATH_PREFIX = "/api/v1/ai/"


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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--token", default=os.getenv("VANTRECOMB_API_TOKEN"), help="API token; defaults to VANTRECOMB_API_TOKEN")
    parser.add_argument("--timeout", type=int, default=30)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("guide", help="Read the AI procurement workflow")
    catalog = commands.add_parser("catalog", help="Read an AI catalog collection")
    catalog.add_argument("collection", choices=["products", "materials", "crafts", "capabilities", "product-families", "existing-styles", "solutions", "faqs", "project-stories", "pages", "blog"])
    request = commands.add_parser("request", help="Call an allowed AI endpoint")
    request.add_argument("method", choices=["GET", "POST"])
    request.add_argument("path", help="Relative /api/v1/ai/ path")
    request.add_argument("--data", help="JSON request object")
    request.add_argument("--idempotency-key", help="Required for write requests")
    args = parser.parse_args()

    if args.command == "guide":
        path, method, payload, key = "/api/v1/ai/guide", "GET", None, None
    elif args.command == "catalog":
        path, method, payload, key = f"/api/v1/ai/catalog/{args.collection}", "GET", None, None
    else:
        path, method, payload, key = args.path, args.method, parse_json_argument(args.data), args.idempotency_key
        if method == "POST" and not key:
            parser.error("POST requests require --idempotency-key")

    result = VantrecombClient(args.token, args.timeout).request_json(method, path, payload, key)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, RuntimeError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(1)
