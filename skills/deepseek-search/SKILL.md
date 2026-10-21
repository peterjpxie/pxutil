---
name: deepseek-search
description: Search the live web and fetch web pages as Markdown through DeepSeek's Search & Fetch APIs. Use when the answer needs current information or the contents of a specific URL.
type: prompt
whenToUse: When the user asks about recent events, live web information, current documentation or releases, or wants a specific web page read — especially when no built-in web search/fetch tool is available.
---

Use DeepSeek's Search and Fetch APIs through the bundled helper:

```bash
python3 "${KIMI_SKILL_DIR}/scripts/deepseek_web.py" search "<query>" [--count N] [--content] [--json]
python3 "${KIMI_SKILL_DIR}/scripts/deepseek_web.py" fetch "<url>" [--json]
```

The helper reads `DEEPSEEK_API_KEY` from the environment and never prints it. Do not echo, log, or put the key in a command line argument.

## Workflow

1. `search` with a focused query. Results include `title`, `url`, `snippet`, `summary`, `date`, `site_name`, and `rerank_score`.
2. Read `summary` first; it is usually enough to judge relevance. Treat `rerank_score >= 1.5` as high quality and `authority >= 3` as highly authoritative.
3. If a result looks relevant but the summary is insufficient, re-run with `--content`, or `fetch` its URL to get the full page as Markdown.
4. Cite the source URLs you used in your answer.

## Query operators

The query passes through with search syntax intact:

| Operator | Example | Effect |
| --- | --- | --- |
| `site:` | `site:github.com` | Restrict to a site; combine with `OR`: `site:github.com OR site:huggingface.co` |
| `-site:` | `-site:example.com` | Exclude a site |
| `-term` / `-"phrase"` | `-advertisement` / `-"release notes"` | Exclude pages with the term/phrase |
| `"..."` | `"exact phrase"` | Exact-phrase match |
| `lang:` | `lang:zh,en` | Restrict language codes |
| `after:` / `before:` | `after:2025-01-01` / `before:2026` | Restrict publication date |

Combine multiple operators in one query, e.g. `DeepSeek site:github.com lang:en after:2025`.

## Options

- `--count N` — number of results, 1–50 (default 10). Price is per request, so ask for enough results in one call.
- `--content` — include full page content in each result (larger output; use only when summaries are insufficient).
- `--ori-question "..."` — the user's original question, between 1 and 128 characters, to improve query understanding.
- `--localization IP` — localize results by IP address.
- `--json` — raw API JSON, useful when you need fields like `site_icon` or `authority`.

## Fetching

`fetch` accepts an absolute HTTP(S) URL with a host and no embedded credentials. It returns the page `title` and `content` as Markdown. Fetching depends on the target site's availability and access policy; paywalled or blocked pages can fail with HTTP 404.

## Errors and limits

- `401` — missing or invalid key; confirm `DEEPSEEK_API_KEY` is exported in the shell environment.
- `402` — insufficient account balance; do not retry.
- `403` — Fetch rejected by security policy; do not retry.
- `404` — Fetch could not extract usable content; try a different URL or use Search content instead.
- `408`, `429`, `5xx` — wait briefly and retry; `429` means the per-account QPS limit was hit (Search 100 QPS, Fetch 25 QPS, plus a per-domain Fetch limit).
- Do not retry other 4xx errors unchanged.
- Billing is per successful request (Search $0.75 / 1,000, Fetch $0.75 / 1,000); an empty search result is not billed.
