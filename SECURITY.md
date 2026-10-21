# Security Policy

## Handling secrets and data
- This repository must never contain API keys, OAuth credentials, webhook URLs or secret paths, Drive IDs, or customer data.
- n8n exports can include **pinned execution data** (names, emails, phone numbers, recording URLs). Remove it before committing.
- Run `python3 scripts/check_sanitized.py` before every commit. CI runs the same check.

## If a secret is exposed
1. Rotate it immediately (new webhook path, reconnect Google credentials, regenerate API keys).
2. Remove it from the repo history (not just the latest commit).
3. Review n8n and Vapi logs for unexpected activity.

## Reporting a vulnerability
Please do not open a public issue. Email the maintainer or use GitHub's private vulnerability reporting (Security tab > Report a vulnerability).
