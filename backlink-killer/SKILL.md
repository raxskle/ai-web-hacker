---
name: backlink-killer
description: Assist with website directory submissions and relevant blog outreach using Playwright, persistent browser sessions, site profiles, and Notion status tracking.
---

# Backlink Killer

Use this skill when the user asks to review a directory or blog opportunity and submit a site or publish a genuinely relevant outreach comment.

## Inputs

1. Read the target rows from the user's Notion database/view when an authorized Notion integration is available. Load the repository-root `.env` only through the runtime's environment loader, then use `NOTION_TOKEN`; never print, persist, or hard-code the token. Interpret each row as a target URL plus its submission type and one or more site columns.
2. Read site profiles from [`site-profiles/`](site-profiles/). Use [`references/site-profile.template.yaml`](references/site-profile.template.yaml) as the schema. Keep logos and OG images inside each profile directory. Do not commit secrets, cookies, storage states, API keys, or passwords.
3. If a target is ambiguous, duplicated, inaccessible, irrelevant, or already marked complete for the selected site, record `skipped` with a reason instead of guessing.

## Browser and login state

Use Playwright in a persistent context, one isolated state directory per account or identity:

```text
backlink-killer/.playwright/
  <account-name>/storage-state.json
```

The state directory is local-only and must be gitignored. Reuse the same context on later runs; do not log in repeatedly. Prefer a visible browser for first login and user verification. Never extract or print cookies or tokens.

## Directory workflow

For each eligible target:

1. Open the target and locate the official submit/add-listing path. Confirm the site is relevant and the listing is free before entering data.
2. Fill only fields supported by the selected site profile. Use the site's requested category and the profile's truthful description; do not keyword-stuff.
3. If a badge is genuinely required for a free listing, stop and ask the user to confirm that requirement and provide the authorized local repository. If confirmed, make the smallest matching homepage change, run the repository's existing checks, and prepare the change for review. Push to `main` only after explicit confirmation; then wait for the repository's deployment signal or a reasonable user-specified timeout.
4. Before clicking the final submit button, present the target, fields, cost, account, and any badge change and request confirmation. After submission, capture the confirmation URL/text without collecting sensitive data.
5. Update only the matching Notion cell for the selected site profile to `1` after a successful submission. If the Notion API is unavailable, write a pending audit entry and do not claim success.

## Blog workflow

1. Read the article title, relevant headings, and a few paragraphs. Check that the site accepts comments and that a link is allowed by its stated policy.
2. Draft one short, concrete comment (roughly 25–45 words) that contributes an observation or useful clarification. Mention the user's site only when it naturally solves a problem discussed in the article; use the requested language and a plain, accurate link.
3. Show the article summary and proposed comment to the user. Do not submit until the user explicitly approves that exact text and target.
4. If approved, fill the form manually through Playwright, stop for any CAPTCHA or moderation gate, and record whether the comment was submitted, queued, or rejected. Only mark the corresponding Notion cell `1` if the site reports successful submission; a pending moderation state is not success.

## Status and audit

Use statuses such as `planned`, `needs-login`, `needs-review`, `submitted`, `pending-moderation`, `skipped`, and `failed`. Keep local audit logs free of credentials and page contents. A Notion cell should be changed to `1` only for the exact `(target URL, site profile)` pair that succeeded.

For Notion field mapping and the local profile schema, read [`references/notion-and-profile.md`](references/notion-and-profile.md) when needed.
