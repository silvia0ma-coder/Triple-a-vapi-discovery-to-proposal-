#!/usr/bin/env python3
"""Send a sample Vapi end-of-call-report to your n8n webhook, without making a phone call.

Usage:
    export N8N_WEBHOOK_URL="https://<your-n8n-host>/webhook-test/<your-webhook-path>"
    python3 scripts/send_test_payload.py
    python3 scripts/send_test_payload.py --dry-run

Notes:
    * The URL is read from the environment (or --url) and is never stored in the repo.
    * Each run uses a fresh call_id so the Data Table upsert does not overwrite an earlier test row.
    * Uses only the Python standard library.
"""
import argparse
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request
import uuid

DEFAULT_PAYLOAD = pathlib.Path(__file__).resolve().parent.parent / "examples" / "sample-end-of-call-report.json"


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--url", default=os.environ.get("N8N_WEBHOOK_URL"), help="Webhook URL (default: $N8N_WEBHOOK_URL)")
    p.add_argument("--payload", type=pathlib.Path, default=DEFAULT_PAYLOAD, help="JSON file to send")
    p.add_argument("--header", action="append", default=[], metavar="'Name: value'",
                   help="Extra HTTP header, repeatable (for example if you add webhook authentication)")
    p.add_argument("--keep-call-id", action="store_true", help="Do not replace the call id with a fresh one")
    p.add_argument("--timeout", type=int, default=30, help="Seconds to wait for a response")
    p.add_argument("--dry-run", action="store_true", help="Print the payload and exit without sending")
    args = p.parse_args()

    try:
        payload = json.loads(args.payload.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Cannot read payload {args.payload}: {exc}", file=sys.stderr)
        return 2

    message = payload.get("message", {})
    if message.get("type") != "end-of-call-report":
        print("Payload must have message.type == 'end-of-call-report'.", file=sys.stderr)
        return 2
    if not args.keep_call_id:
        message.setdefault("call", {})["id"] = str(uuid.uuid4())

    body = json.dumps(payload).encode("utf-8")
    if args.dry_run:
        print(json.dumps(payload, indent=2))
        print(f"\n(dry run: {len(body)} bytes, nothing sent)")
        return 0

    if not args.url:
        print("Set N8N_WEBHOOK_URL or pass --url.", file=sys.stderr)
        return 2

    headers = {"Content-Type": "application/json"}
    for h in args.header:
        name, sep, value = h.partition(":")
        if not sep:
            print(f"Bad header (expected 'Name: value'): {h}", file=sys.stderr)
            return 2
        headers[name.strip()] = value.strip()

    req = urllib.request.Request(args.url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=args.timeout) as resp:
            print(f"HTTP {resp.status} - call_id {message['call']['id']}")
            print(resp.read().decode("utf-8", "replace")[:500])
            return 0
    except urllib.error.HTTPError as exc:
        print(f"HTTP {exc.code}: {exc.read().decode('utf-8', 'replace')[:500]}", file=sys.stderr)
        if exc.code == 404:
            print("404 usually means the workflow is inactive (production URL) or not listening (test URL).", file=sys.stderr)
        return 1
    except urllib.error.URLError as exc:
        print(f"Could not reach the webhook: {exc.reason}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
