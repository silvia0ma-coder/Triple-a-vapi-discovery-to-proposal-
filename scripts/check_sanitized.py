#!/usr/bin/env python3
"""Fail if workflow JSON files contain pinned data, real credential IDs or PII-like values."""
import json, re, sys, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
errors = []

PATTERNS = {
    "n8n cloud host": r"[a-z0-9-]+\.app\.n8n\.cloud",
    "signed URL": r"X-Amz-",
    "cloud storage URL": r"cloudflarestorage\.com|amazonaws\.com/",
    "email address": r"[A-Za-z0-9._%+-]+@(?!example\.com)[A-Za-z0-9-]+\.(com|net|org|io)",
    "API key": r"sk-[A-Za-z0-9]{20,}|Bearer\s+[A-Za-z0-9._-]{20,}",
}
ID_RX = re.compile(r"(?<![A-Za-z0-9_-])[A-Za-z0-9_-]{33,}(?![A-Za-z0-9_-])")
SAFE = ("REPLACE", "YOUR_", "predefined", "attemptToConvert", "convertFields")

for f in ROOT.glob("workflows/*.json"):
    text = f.read_text(encoding="utf-8")
    try:
        d = json.loads(text)
    except Exception as e:
        errors.append(f"{f.name}: invalid JSON ({e})")
        continue
    if d.get("pinData"):
        errors.append(f"{f.name}: pinData must be empty")
    for k in ("id", "versionId"):
        if k in d:
            errors.append(f"{f.name}: remove top-level '{k}'")
    if d.get("meta", {}).get("instanceId"):
        errors.append(f"{f.name}: remove meta.instanceId")
    if d.get("active"):
        errors.append(f"{f.name}: workflow must be inactive")
    for n in d.get("nodes", []):
        if n.get("webhookId"):
            errors.append(f"{f.name}: node '{n['name']}' has webhookId")
        for ctype, c in (n.get("credentials") or {}).items():
            if c.get("id") not in (None, "REPLACE_ME"):
                errors.append(f"{f.name}: node '{n['name']}' has real credential id")
        if n["type"].endswith(".webhook") and "REPLACE" not in n["parameters"].get("path", ""):
            errors.append(f"{f.name}: webhook path must be a placeholder")
    for tok in set(ID_RX.findall(text)):
        if any(w in tok for w in SAFE):
            continue
        # real Drive/Docs IDs mix upper, lower and digits; skip plain words and slugs
        if re.search(r"[A-Z]", tok) and re.search(r"[a-z]", tok) and re.search(r"\d", tok):
            errors.append(f"{f.name}: possible Google ID/secret: {tok[:12]}...")
    for label, rx in PATTERNS.items():
        m = re.search(rx, text)
        if m:
            errors.append(f"{f.name}: possible {label}: {m.group(0)[:40]}")

if errors:
    print("FAILED sanitization check:")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print("OK: workflows are sanitized")
