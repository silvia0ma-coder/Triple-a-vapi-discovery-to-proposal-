#!/usr/bin/env python3
"""Fail if docs, examples or scripts contain real-looking secrets, webhook URLs, phone numbers or private words."""
import os, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKIP = {"check_docs_sanitized.py", "check_sanitized.py"}
EXT = {".md", ".json", ".py", ".yml", ".yaml", ".txt", ".example"}
PATTERNS = {
    "n8n cloud host": r"[a-z0-9-]+\.app\.n8n\.cloud",
    "webhook URL with long token": r"/webhook(?:-test)?/(?![A-Za-z0-9_-]*(?:REPLACE|YOUR_))[A-Za-z0-9_-]{24,}",
    "make.com hook": r"hook\.[a-z0-9]+\.make\.com/[A-Za-z0-9]+",
    "email address": r"[A-Za-z0-9._%+-]+@(?!example\.com)[A-Za-z0-9-]+\.(com|net|org|io)",
    "phone number ": r"\+(?!1555)\d{10,14}\b",
    "Vapi/OpenAI-style key": r"sk-[A-Za-z0-9]{20,}|Bearer\s+[A-Za-z0-9._-]{20,}",
    "real-looking UUID (use 00000000-0000-4000-8000-...)": r"\b(?!00000000-)[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b",
}
# Optional: set SANITIZE_BLOCKLIST to a regex of private words (brand, client names) to block them.
_extra = os.environ.get("SANITIZE_BLOCKLIST")
if _extra:
    PATTERNS["blocklisted text"] = "(?i)" + _extra
errors = []
for f in ROOT.rglob("*"):
    if not f.is_file() or ".git" in f.parts or f.name in SKIP:
        continue
    if f.suffix not in EXT and f.name not in {".env.example"}:
        continue
    text = f.read_text(encoding="utf-8", errors="ignore")
    for label, rx in PATTERNS.items():
        if label.startswith("real-looking UUID") and f.relative_to(ROOT).parts[0] == "workflows":
            continue  # n8n node ids are UUIDs; workflows have their own checker
        m = re.search(rx, text)
        if m:
            errors.append(f"{f.relative_to(ROOT)}: possible {label}: {m.group(0)[:40]}")
if errors:
    print("FAILED docs sanitization check:")
    print("\n".join(" - " + e for e in errors))
    sys.exit(1)
print("OK: docs, examples and scripts are sanitized")
