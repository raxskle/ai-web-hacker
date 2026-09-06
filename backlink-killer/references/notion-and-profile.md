# Notion and profile notes

## Credentials

Use an authorized integration token from `NOTION_TOKEN`, loaded at runtime from the repository-root `.env` when present. Never place a token in this file, a profile, git history, or tool output. The database/view URL is configuration, not a credential. Confirm the integration has access before attempting writes.

## Matching logic

The target record is identified by its target URL (normalize only the trailing slash and URL fragment). The selected site is identified by the column whose name equals the profile `base_url` or `display_name`, depending on the database's existing convention. Inspect existing rows first and preserve that convention. Do not create a new column automatically.

Write the value `1` only after the target site reports a successful submission. Do not write `1` for a draft, a blocked form, a queued comment, a paid listing, or a badge-only change.

## Suggested local audit record

```yaml
timestamp: 2026-01-01T00:00:00Z
target_url: https://directory.example/submit
site_profile: example-site
kind: directory # or blog-comment
status: submitted
confirmation: Confirmation text or URL, with secrets removed
notion_updated: true
notes: Human-readable reason or follow-up
```
