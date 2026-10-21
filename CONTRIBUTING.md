# Contributing

1. Fork and create a branch (`feature/short-description`).
2. Export your n8n changes, then **sanitize**: empty `pinData`, replace credential IDs with `REPLACE_ME`, replace folder, table and webhook identifiers with placeholders, remove workflow, version and instance IDs.
3. Run `python3 scripts/check_sanitized.py`. It must pass.
4. Update `docs/` and `CHANGELOG.md` for any behaviour change.
5. Open a pull request using the template.

Use clear commit messages (`feat:`, `fix:`, `docs:`, `chore:`).
