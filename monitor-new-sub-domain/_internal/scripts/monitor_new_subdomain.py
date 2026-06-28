#!/usr/bin/env python3
"""监控 *.vercel.app 新增子域名并输出中文报告。

Usage:
  python3 monitor-new-sub-domain/_internal/scripts/monitor_new_subdomain.py run
  python3 monitor-new-sub-domain/_internal/scripts/monitor_new_subdomain.py rebuild-reports
"""

from __future__ import annotations

import argparse
import html
import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

RAW_FILE_RE = re.compile(r"^(?P<rule>.+)-(?P<date>\d{8})-(?P<hhmm>\d{4})\.json$")
SNAPSHOT_FILE_RE = re.compile(r"^subdomains-(?P<date>\d{8})-(?P<hhmm>\d{4})\.json$")
VERCEL_SUFFIX = ".vercel.app"

ANALYSIS_WORKERS = 8
PAGE_FETCH_TIMEOUT = 4
PAGE_FETCH_BYTES = 120_000

RISING_WINDOW_POINTS = 4
RISING_MIN_GROWTH_RATIO = 0.30
RISING_MIN_LATEST_CLICKS = 50.0

SCRIPT_STYLE_RE = re.compile(r"<(script|style)[^>]*>.*?</\1>", re.IGNORECASE | re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")
WORD_RE = re.compile(r"[\w\-]{3,}", re.UNICODE)

EN_STOP_WORDS = {
    "the", "and", "for", "with", "from", "that", "this", "your", "you", "our", "are", "was",
    "what", "when", "where", "how", "have", "has", "had", "into", "about", "home", "page",
    "site", "official", "welcome", "best", "new", "all", "get", "more", "use", "using", "via",
}


@dataclass(order=True)
class TimedFile:
    stamp: str  # YYYYMMDD-HHMM
    path: Path


def parse_args() -> argparse.Namespace:
    project_dir = Path(__file__).resolve().parents[2]
    internal_dir = project_dir / "_internal"

    parser = argparse.ArgumentParser(
        description="分析 *.vercel.app 新增子域名并生成中文报告"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="执行完整流程")
    run_parser.add_argument("--data-dir", default=str(project_dir / "data"))
    run_parser.add_argument("--snapshot-dir", default=str(internal_dir / "snapshots"))
    run_parser.add_argument("--report-dir", default=str(project_dir / "reports" / "history"))
    run_parser.add_argument(
        "--latest-report-path",
        default=str(project_dir / "reports" / "latest.md"),
        help="最新报告输出路径",
    )
    run_parser.add_argument(
        "--raw-file",
        default=None,
        help="可选：指定 raw JSON 文件。未指定时按文件名时间戳选择最新文件。",
    )

    rebuild_parser = subparsers.add_parser("rebuild-reports", help="根据快照重建全部历史报告")
    rebuild_parser.add_argument("--snapshot-dir", default=str(internal_dir / "snapshots"))
    rebuild_parser.add_argument("--report-dir", default=str(project_dir / "reports" / "history"))
    rebuild_parser.add_argument(
        "--latest-report-path",
        default=str(project_dir / "reports" / "latest.md"),
        help="最新报告输出路径",
    )

    return parser.parse_args()


def safe_float(value) -> float:
    try:
        if value is None:
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def parse_filename_stamp(path: Path, pattern: re.Pattern) -> Optional[str]:
    m = pattern.match(path.name)
    if not m:
        return None
    return f"{m.group('date')}-{m.group('hhmm')}"


def list_timed_files(directory: Path, pattern: re.Pattern) -> List[TimedFile]:
    items: List[TimedFile] = []
    if not directory.exists():
        return items
    for path in directory.iterdir():
        if not path.is_file():
            continue
        stamp = parse_filename_stamp(path, pattern)
        if not stamp:
            continue
        items.append(TimedFile(stamp=stamp, path=path))
    return sorted(items)


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def escape_md_cell(text: str) -> str:
    if not isinstance(text, str):
        text = str(text)
    text = text.replace("\n", " ").replace("\r", " ").strip()
    text = re.sub(r"\s+", " ", text)
    return text.replace("|", "\\|")


def to_clicks_str(value) -> str:
    num = safe_float(value)
    if abs(num - round(num)) < 1e-9:
        return str(int(round(num)))
    return f"{num:.2f}"


def short_date(date_str: str) -> str:
    if isinstance(date_str, str) and len(date_str) >= 10:
        return date_str[5:10]
    return date_str if isinstance(date_str, str) else "-"


def compact_text(value: str, max_chars: int) -> str:
    if not isinstance(value, str):
        return "-"
    text = re.sub(r"\s+", " ", value).strip()
    if not text:
        return "-"
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 1] + "…"


def normalize_clickable_url(raw_url: str) -> str:
    if not isinstance(raw_url, str):
        return ""
    url = raw_url.strip()
    if not url:
        return ""
    if "://" not in url:
        url = f"https://{url}"
    return url


def normalize_url(raw_url: str) -> Optional[dict]:
    if not isinstance(raw_url, str):
        return None
    stripped = raw_url.strip()
    if not stripped:
        return None

    candidate = stripped
    if "://" not in candidate:
        candidate = f"https://{candidate}"

    try:
        parts = urlsplit(candidate)
    except ValueError:
        return None

    host = (parts.hostname or "").strip().lower().rstrip(".")
    if not host.endswith(VERCEL_SUFFIX) or host == "vercel.app":
        return None

    subdomain = host[: -len(VERCEL_SUFFIX)]
    if not subdomain:
        return None

    path = parts.path or "/"
    if path != "/":
        path = "/" + path.lstrip("/")
        path = path.rstrip("/") or "/"

    path_segments = [seg for seg in path.split("/") if seg]
    path_slug = ""
    if path_segments:
        last_seg = path_segments[-1]
        path_slug = last_seg.rsplit(".", 1)[0]

    slug_tokens = [token for token in re.split(r"[-_.]+", subdomain) if token]

    return {
        "host": host,
        "subdomain": subdomain,
        "subdomain_slug": subdomain,
        "path": path,
        "path_slug": path_slug,
        "slug_tokens": slug_tokens,
    }


def parse_trend(value) -> Dict[str, float]:
    if not isinstance(value, dict):
        return {}
    result: Dict[str, float] = {}
    for key, num in value.items():
        if not isinstance(key, str):
            continue
        result[key] = safe_float(num)
    return result


def pick_stronger_row(existing: dict, candidate: dict) -> dict:
    existing_key = (existing["clicks"], existing["clicks_share"], existing["url"])
    candidate_key = (candidate["clicks"], candidate["clicks_share"], candidate["url"])
    if candidate_key > existing_key:
        return candidate
    return existing


def aggregate_host_rows(host: str, rows: List[dict]) -> dict:
    clicks_sum = sum(row["clicks"] for row in rows)
    clicks_share_sum = sum(row["clicks_share"] for row in rows)
    clicks_max = max((row["clicks"] for row in rows), default=0.0)

    top_row = max(rows, key=lambda r: (r["clicks"], r["clicks_share"], r["url"]))
    trend_sum: Dict[str, float] = {}
    for row in rows:
        for date_key, value in row["trend"].items():
            trend_sum[date_key] = trend_sum.get(date_key, 0.0) + value

    ordered_trend_sum = {key: trend_sum[key] for key in sorted(trend_sum)}

    keyword_stats: Dict[str, dict] = {}
    for row in rows:
        keyword = (row.get("top_keyword") or "").strip()
        if not keyword:
            continue
        entry = keyword_stats.setdefault(
            keyword,
            {"keyword": keyword, "clicks": 0.0, "clicks_share": 0.0, "count": 0},
        )
        entry["clicks"] += safe_float(row.get("clicks"))
        entry["clicks_share"] += safe_float(row.get("clicks_share"))
        entry["count"] += 1

    keywords = [
        item["keyword"]
        for item in sorted(
            keyword_stats.values(),
            key=lambda item: (-item["clicks"], -item["clicks_share"], item["keyword"].lower()),
        )
    ]

    return {
        "host": host,
        "subdomain": top_row["subdomain"],
        "subdomain_slug": top_row["subdomain_slug"],
        "slug_tokens": top_row["slug_tokens"],
        "rows_count": len(rows),
        "clicks_sum": round(clicks_sum, 4),
        "clicks_max": round(clicks_max, 4),
        "clicks_share_sum": round(clicks_share_sum, 8),
        "top_url": top_row["url"],
        "top_keyword": (keywords[0] if keywords else (top_row.get("top_keyword", "") or "")),
        "keywords": keywords,
        "path_slug": top_row.get("path_slug", "") or "",
        "trend_13w_sum": ordered_trend_sum,
    }


def build_snapshot_from_raw(raw_path: Path, stamp: str) -> Tuple[dict, dict]:
    payload = load_json(raw_path)
    records = payload.get("records") or []
    host_path_rows: Dict[str, Dict[str, dict]] = {}

    stats = {
        "records_total": len(records),
        "records_non_200": 0,
        "response_parse_failed": 0,
        "data_rows_total": 0,
        "data_rows_invalid_url": 0,
        "data_rows_non_vercel": 0,
    }

    for rec in records:
        status = rec.get("status")
        if status != 200:
            stats["records_non_200"] += 1
            continue

        response_body = rec.get("responseBody", "")
        if not isinstance(response_body, str):
            stats["response_parse_failed"] += 1
            continue

        try:
            response = json.loads(response_body)
        except json.JSONDecodeError:
            stats["response_parse_failed"] += 1
            continue

        data_rows = response.get("Data")
        if not isinstance(data_rows, list):
            continue

        for row in data_rows:
            stats["data_rows_total"] += 1
            if not isinstance(row, dict):
                stats["data_rows_invalid_url"] += 1
                continue

            normalized = normalize_url(row.get("Url", ""))
            if not normalized:
                raw_url = row.get("Url", "")
                if isinstance(raw_url, str) and raw_url.strip():
                    stats["data_rows_non_vercel"] += 1
                else:
                    stats["data_rows_invalid_url"] += 1
                continue

            candidate = {
                "url": row.get("Url", ""),
                "host": normalized["host"],
                "subdomain": normalized["subdomain"],
                "subdomain_slug": normalized["subdomain_slug"],
                "path": normalized["path"],
                "path_slug": normalized["path_slug"],
                "slug_tokens": normalized["slug_tokens"],
                "clicks": safe_float(row.get("Clicks")),
                "clicks_share": safe_float(row.get("ClicksShare")),
                "trend": parse_trend(row.get("Trend")),
                "top_keyword": row.get("TopKeyword") if isinstance(row.get("TopKeyword"), str) else "",
            }

            host_rows = host_path_rows.setdefault(candidate["host"], {})
            row_key = candidate["path"].lower()
            if row_key in host_rows:
                host_rows[row_key] = pick_stronger_row(host_rows[row_key], candidate)
            else:
                host_rows[row_key] = candidate

    hosts = [
        aggregate_host_rows(host, list(rows.values()))
        for host, rows in host_path_rows.items()
        if rows
    ]
    hosts.sort(key=lambda item: (-item["clicks_sum"], item["host"]))

    snapshot = {
        "meta": {
            "generatedAt": datetime.now().isoformat(timespec="seconds"),
            "sourceRawFile": str(raw_path),
            "sourceStamp": stamp,
            "sourceRule": (payload.get("meta") or {}).get("rule", ""),
            "hostsCount": len(hosts),
            "stats": stats,
        },
        "hosts": hosts,
    }

    return snapshot, stats


def load_previous_snapshot(snapshot_dir: Path, current_stamp: str) -> Tuple[Optional[dict], Optional[Path]]:
    candidates = [item for item in list_timed_files(snapshot_dir, SNAPSHOT_FILE_RE) if item.stamp < current_stamp]
    if not candidates:
        return None, None
    chosen = candidates[-1]
    return load_json(chosen.path), chosen.path


def render_trend_summary(trend_map: dict) -> str:
    if not isinstance(trend_map, dict) or not trend_map:
        return "-"

    points = sorted((k, safe_float(v)) for k, v in trend_map.items() if isinstance(k, str))
    if not points:
        return "-"

    latest_date, latest_clicks = points[-1]
    peak_date, peak_clicks = max(points, key=lambda item: item[1])
    return f"{to_clicks_str(latest_clicks)}({short_date(latest_date)}) / {to_clicks_str(peak_clicks)}({short_date(peak_date)})"


def classify_trend_status(trend_map: dict) -> str:
    if not isinstance(trend_map, dict) or not trend_map:
        return "数据不足"

    points = sorted((k, safe_float(v)) for k, v in trend_map.items() if isinstance(k, str))
    if not points:
        return "数据不足"

    latest = points[-1][1]
    prev = points[-2][1] if len(points) >= 2 else 0.0

    if prev <= 0 and latest > 0:
        return "上升中"

    if prev <= 0:
        return "持平"

    change_ratio = (latest - prev) / prev
    if change_ratio >= 0.15:
        return "上升中"
    if change_ratio <= -0.15:
        return "回落中"
    return "持平"


def infer_trend_window(hosts: List[dict]) -> Tuple[Optional[str], Optional[str]]:
    all_dates: List[str] = []
    for host_info in hosts:
        trend = host_info.get("trend_13w_sum")
        if isinstance(trend, dict):
            all_dates.extend(k for k in trend.keys() if isinstance(k, str))

    if not all_dates:
        return None, None

    ordered = sorted(set(all_dates))
    return ordered[0], ordered[-1]


def collect_new_hosts(current_snapshot: dict, previous_snapshot: Optional[dict]) -> List[dict]:
    current_hosts = current_snapshot.get("hosts") or []
    current_map = {item["host"]: item for item in current_hosts if isinstance(item, dict) and "host" in item}

    previous_hosts_set = set()
    if previous_snapshot:
        previous_hosts = previous_snapshot.get("hosts") or []
        previous_hosts_set = {
            item.get("host")
            for item in previous_hosts
            if isinstance(item, dict) and isinstance(item.get("host"), str)
        }

    new_hosts = [
        host_info
        for host, host_info in current_map.items()
        if host not in previous_hosts_set
    ]
    new_hosts.sort(key=lambda item: (-safe_float(item.get("clicks_sum")), item.get("host", "")))
    return new_hosts


def compute_rise_metrics(
    trend_map: dict,
    window_points: int = RISING_WINDOW_POINTS,
    min_growth_ratio: float = RISING_MIN_GROWTH_RATIO,
    min_latest_clicks: float = RISING_MIN_LATEST_CLICKS,
) -> Optional[dict]:
    if not isinstance(trend_map, dict) or not trend_map:
        return None

    points = sorted((k, safe_float(v)) for k, v in trend_map.items() if isinstance(k, str))
    if len(points) < window_points:
        return None

    window = points[-window_points:]
    values = [value for _, value in window]

    for idx in range(1, len(values)):
        if values[idx] <= values[idx - 1]:
            return None

    latest_clicks = values[-1]
    if latest_clicks < min_latest_clicks:
        return None

    first_clicks = values[0]
    growth_ratio = (latest_clicks - first_clicks) / max(first_clicks, 1.0)
    if growth_ratio < min_growth_ratio:
        return None

    return {
        "rise_window_start": window[0][0],
        "rise_window_end": window[-1][0],
        "rise_weeks": len(window),
        "rise_growth_ratio": round(growth_ratio, 6),
        "rise_series": [
            {"date": date_key, "value": round(value, 4)}
            for date_key, value in window
        ],
    }


def collect_rising_hosts(
    current_snapshot: dict,
    previous_snapshot: Optional[dict],
    exclude_hosts: Optional[Set[str]] = None,
) -> List[dict]:
    if not previous_snapshot:
        return []

    excluded = exclude_hosts or set()

    current_hosts = current_snapshot.get("hosts") or []
    current_map = {
        item["host"]: item
        for item in current_hosts
        if isinstance(item, dict) and isinstance(item.get("host"), str)
    }

    previous_hosts = previous_snapshot.get("hosts") or []
    previous_hosts_set = {
        item.get("host")
        for item in previous_hosts
        if isinstance(item, dict) and isinstance(item.get("host"), str)
    }

    rising_hosts: List[dict] = []
    for host, host_info in current_map.items():
        if host in excluded:
            continue
        if host not in previous_hosts_set:
            continue

        metrics = compute_rise_metrics(host_info.get("trend_13w_sum") or {})
        if not metrics:
            continue

        copied = dict(host_info)
        copied.update(metrics)
        rising_hosts.append(copied)

    rising_hosts.sort(
        key=lambda item: (
            -safe_float(item.get("rise_growth_ratio")),
            -safe_float(item.get("clicks_sum")),
            item.get("host", ""),
        )
    )
    return rising_hosts


def clean_html_fragment(fragment: str) -> str:
    fragment = SCRIPT_STYLE_RE.sub(" ", fragment)
    fragment = TAG_RE.sub(" ", fragment)
    fragment = html.unescape(fragment)
    fragment = re.sub(r"\s+", " ", fragment).strip()
    return fragment


def join_keywords(values: List[str]) -> str:
    normalized = [value.strip() for value in values if isinstance(value, str) and value.strip()]
    if not normalized:
        return "-"
    return "；".join(normalized)


def extract_page_keywords(page_signals: Dict[str, str]) -> List[str]:
    text = " ".join(
        [
            page_signals.get("title", "") or "",
            page_signals.get("description", "") or "",
            page_signals.get("h1", "") or "",
        ]
    ).lower()

    if not text.strip():
        return []

    result: List[str] = []
    seen = set()
    for token in WORD_RE.findall(text):
        token = token.strip("-_ ")
        if not token or len(token) < 3:
            continue
        if token in EN_STOP_WORDS:
            continue
        if token.startswith("http"):
            continue
        if token in seen:
            continue
        seen.add(token)
        result.append(token)

    return result


def render_fetch_status(fetch: dict) -> str:
    if not isinstance(fetch, dict):
        return "失败（fetch_info_missing）"

    if fetch.get("opened"):
        status_code = fetch.get("http_status")
        if status_code:
            return f"成功（HTTP {status_code}）"
        return "成功"

    error_type = fetch.get("error_type") or "unknown_error"
    error_message = fetch.get("error_message") or ""
    if error_message:
        return compact_text(f"失败（{error_type}: {error_message}）", 80)
    return f"失败（{error_type}）"


def fetch_page_context(url: str) -> dict:
    context = {
        "opened": False,
        "requested_url": url,
        "final_url": "",
        "http_status": 0,
        "error_type": "",
        "error_message": "",
        "signals": {
            "title": "",
            "description": "",
            "h1": "",
        },
    }

    if not url:
        context["error_type"] = "empty_url"
        return context

    req = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; SubdomainMonitor/1.0)"
        },
    )

    try:
        with urlopen(req, timeout=PAGE_FETCH_TIMEOUT) as resp:
            raw = resp.read(PAGE_FETCH_BYTES)
            charset = resp.headers.get_content_charset() or "utf-8"
            context["opened"] = True
            context["final_url"] = resp.geturl() if hasattr(resp, "geturl") else url
            context["http_status"] = int(getattr(resp, "status", 0) or 0)
    except HTTPError as exc:
        context["error_type"] = "http_error"
        context["error_message"] = str(exc.reason or exc)
        context["http_status"] = int(getattr(exc, "code", 0) or 0)
        return context
    except URLError as exc:
        context["error_type"] = "url_error"
        context["error_message"] = str(exc.reason or exc)
        return context
    except TimeoutError as exc:
        context["error_type"] = "timeout"
        context["error_message"] = str(exc)
        return context
    except ValueError as exc:
        context["error_type"] = "value_error"
        context["error_message"] = str(exc)
        return context

    text = raw.decode(charset, errors="ignore")
    text = text if isinstance(text, str) else ""

    title_match = re.search(r"<title[^>]*>(.*?)</title>", text, re.IGNORECASE | re.DOTALL)
    desc_match = re.search(
        r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']',
        text,
        re.IGNORECASE | re.DOTALL,
    )
    h1_match = re.search(r"<h1[^>]*>(.*?)</h1>", text, re.IGNORECASE | re.DOTALL)

    context["signals"] = {
        "title": clean_html_fragment(title_match.group(1)) if title_match else "",
        "description": clean_html_fragment(desc_match.group(1)) if desc_match else "",
        "h1": clean_html_fragment(h1_match.group(1)) if h1_match else "",
    }

    return context


def classify_site_purpose(page_signals: Dict[str, str], keywords: List[str]) -> Tuple[str, str]:
    combined = " ".join(
        [
            page_signals.get("title", "") or "",
            page_signals.get("description", "") or "",
            page_signals.get("h1", "") or "",
            " ".join(keywords),
        ]
    ).lower()

    def collect_hits(words: List[str]) -> List[str]:
        return [word for word in words if word in combined]

    rules = [
        (
            "网络安全/CTF内容站",
            ["ctf", "writeup", "forensic", "security", "pwn", "reverse", "webshell", "xss"],
        ),
        (
            "后台管理/数据看板",
            ["dashboard", "admin", "panel", "console", "backend", "cms", "manage", "analytics"],
        ),
        (
            "企业联系信息/目录页",
            ["iletisim", "contact", "company", "company info", "adres", "email", "telefon", "sigorta"],
        ),
        (
            "娱乐内容/游戏相关站",
            ["anime", "manga", "novel", "fifa", "game", "bloxd", "oyun", "mod"],
        ),
        (
            "汽车/摩托维修知识站",
            [
                "авто", "мото", "skoda", "nissan", "kia", "toyota", "ремонт", "articles/",
                "звездоч", "багаж", "инструкция", "двигател", "car", "motor",
            ],
        ),
        (
            "在线工具/效率应用站",
            ["calculator", "converter", "editor", "tool", "pdf", "generator", "checker", "tracker"],
        ),
        (
            "资讯教程内容站",
            ["blog", "article", "guide", "wiki", "教程", "文档", "how to"],
        ),
        (
            "个人作品集/个人主页",
            ["portfolio", "my work", "about me", "resume", "instagram", "behance", "dribbble", "作品", "sketches"],
        ),
    ]

    scored: List[Tuple[int, str, List[str]]] = []
    for label, words in rules:
        hits = collect_hits(words)
        if hits:
            scored.append((len(hits), label, hits))

    if scored:
        scored.sort(key=lambda item: (-item[0], item[1]))
        _, best_label, best_hits = scored[0]
        hits_preview = "、".join(best_hits[:5])
        return best_label, f"命中：{hits_preview}"

    title = page_signals.get("title", "").strip()
    h1 = page_signals.get("h1", "").strip()
    snippet = title or h1
    if snippet:
        return "内容站（待进一步确认）", f"页面线索：{compact_text(snippet, 36)}"

    return "内容站（待进一步确认）", "页面 title/desc/h1 信号不足"


def infer_site_insight_for_host(host_info: dict) -> dict:
    host = host_info.get("host", "")
    top_url = host_info.get("top_url", "")

    similarweb_keywords = [
        item.strip()
        for item in (host_info.get("keywords") or [])
        if isinstance(item, str) and item.strip()
    ]
    if not similarweb_keywords:
        top_keyword = host_info.get("top_keyword", "")
        if isinstance(top_keyword, str) and top_keyword.strip():
            similarweb_keywords = [top_keyword.strip()]

    url_to_fetch = normalize_clickable_url(top_url if top_url else host)
    page_fetch = fetch_page_context(url_to_fetch)
    page_signals = page_fetch.get("signals") if isinstance(page_fetch.get("signals"), dict) else {}
    page_keywords = extract_page_keywords(page_signals) if page_fetch.get("opened") else []

    classification_keywords: List[str] = []
    seen = set()
    for keyword in similarweb_keywords + page_keywords:
        if keyword in seen:
            continue
        seen.add(keyword)
        classification_keywords.append(keyword)

    if page_fetch.get("opened"):
        purpose_label, purpose_reason = classify_site_purpose(page_signals, classification_keywords)
        purpose_status = "已判定"
    else:
        purpose_label = "未判定"
        purpose_reason = f"页面抓取失败，{render_fetch_status(page_fetch)}"
        purpose_status = "未判定"

    return {
        "site_purpose": purpose_label if purpose_status == "已判定" else f"未判定（{render_fetch_status(page_fetch)}）",
        "site_purpose_status": purpose_status,
        "site_purpose_label": purpose_label,
        "site_purpose_reason": purpose_reason,
        "page_fetch": page_fetch,
        "page_signals": page_signals,
        "keywords_similarweb": similarweb_keywords,
        "keywords_page": page_keywords,
    }


def enrich_hosts_with_insight(hosts: List[dict]) -> List[dict]:
    enriched = []
    for host_info in hosts:
        copied = dict(host_info)
        copied["trend_status"] = classify_trend_status(copied.get("trend_13w_sum") or {})
        copied["site_purpose"] = "待判断"
        copied["site_purpose_status"] = "待判断"
        copied["site_purpose_reason"] = "-"
        copied["page_fetch"] = {}
        copied["page_signals"] = {"title": "", "description": "", "h1": ""}
        copied["keywords_similarweb"] = copied.get("keywords") or []
        copied["keywords_page"] = []
        enriched.append(copied)

    if not enriched:
        return enriched

    workers = min(ANALYSIS_WORKERS, max(1, len(enriched)))
    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_index = {
            executor.submit(infer_site_insight_for_host, host_info): idx
            for idx, host_info in enumerate(enriched)
        }
        for future in as_completed(future_to_index):
            idx = future_to_index[future]
            try:
                insight = future.result()
                enriched[idx].update(insight)
            except Exception as exc:
                enriched[idx]["site_purpose"] = f"未判定（失败（analysis_error: {compact_text(str(exc), 36)}））"
                enriched[idx]["site_purpose_status"] = "未判定"
                enriched[idx]["site_purpose_reason"] = "分析过程异常"
                enriched[idx]["page_fetch"] = {
                    "opened": False,
                    "requested_url": normalize_clickable_url(enriched[idx].get("top_url") or enriched[idx].get("host") or ""),
                    "final_url": "",
                    "http_status": 0,
                    "error_type": "analysis_error",
                    "error_message": str(exc),
                    "signals": {"title": "", "description": "", "h1": ""},
                }
                enriched[idx]["page_signals"] = {"title": "", "description": "", "h1": ""}
                enriched[idx]["keywords_page"] = []

    return enriched


def format_growth_ratio(value) -> str:
    ratio = safe_float(value)
    return f"{ratio * 100:+.1f}%"


def format_rise_window(item: dict) -> str:
    start = item.get("rise_window_start")
    end = item.get("rise_window_end")
    if isinstance(start, str) and isinstance(end, str):
        return f"{short_date(start)}~{short_date(end)}"
    return "-"


def format_rise_series(item: dict) -> str:
    series = item.get("rise_series")
    if not isinstance(series, list) or not series:
        return "-"

    parts = []
    for point in series:
        if not isinstance(point, dict):
            continue
        parts.append(f"{to_clicks_str(point.get('value'))}({short_date(point.get('date'))})")

    return " -> ".join(parts) if parts else "-"


def render_host_detail(lines: List[str], idx: int, item: dict, with_rise: bool = False) -> None:
    host = escape_md_cell(item.get("host", ""))
    clicks = to_clicks_str(item.get("clicks_sum"))
    trend_status = escape_md_cell(item.get("trend_status", "-"))
    trend = escape_md_cell(render_trend_summary(item.get("trend_13w_sum") or {}))
    purpose = escape_md_cell(item.get("site_purpose", "-"))
    fetch_status = escape_md_cell(render_fetch_status(item.get("page_fetch") or {}))

    page_signals = item.get("page_signals") if isinstance(item.get("page_signals"), dict) else {}
    page_title = escape_md_cell(page_signals.get("title", "") or "-")
    page_h1 = escape_md_cell(page_signals.get("h1", "") or "-")

    keywords_sw = item.get("keywords_similarweb") if isinstance(item.get("keywords_similarweb"), list) else []
    keywords_page = item.get("keywords_page") if isinstance(item.get("keywords_page"), list) else []

    lines.append(f"{idx}. **{host}**")
    lines.append(f"   - 点击量：{clicks}")
    lines.append(f"   - 趋势判断：{trend_status}（最新/峰值：{trend}）")
    if with_rise:
        lines.append(f"   - 连续上涨窗口：{escape_md_cell(format_rise_window(item))}")
        lines.append(f"   - 窗口涨幅：{escape_md_cell(format_growth_ratio(item.get('rise_growth_ratio')))}")
        lines.append(f"   - 持续上涨证据：{escape_md_cell(format_rise_series(item))}")
    lines.append(f"   - 页面抓取状态：{fetch_status}")
    lines.append(f"   - 网站用途：{purpose}")
    lines.append(f"   - 页面标题（抓取）：{page_title}")
    lines.append(f"   - 页面H1（抓取）：{page_h1}")
    lines.append(f"   - 关键词（SimilarWeb）：{escape_md_cell(join_keywords(keywords_sw))}")
    lines.append(f"   - 关键词（网站发现）：{escape_md_cell(join_keywords(keywords_page))}")
    lines.append("")


def render_report(
    current_snapshot: dict,
    previous_snapshot: Optional[dict],
    previous_stamp: Optional[str],
) -> Tuple[str, int]:
    current_hosts = current_snapshot.get("hosts") or []
    new_hosts = collect_new_hosts(current_snapshot, previous_snapshot)
    new_host_set = {
        item.get("host")
        for item in new_hosts
        if isinstance(item, dict) and isinstance(item.get("host"), str)
    }

    rising_hosts = collect_rising_hosts(
        current_snapshot=current_snapshot,
        previous_snapshot=previous_snapshot,
        exclude_hosts=new_host_set,
    )

    merged_targets: Dict[str, dict] = {}
    for item in new_hosts + rising_hosts:
        host = item.get("host") if isinstance(item, dict) else None
        if isinstance(host, str) and host:
            merged_targets[host] = item

    enriched_all_hosts = enrich_hosts_with_insight(list(merged_targets.values()))
    enriched_by_host = {
        item.get("host"): item
        for item in enriched_all_hosts
        if isinstance(item, dict) and isinstance(item.get("host"), str)
    }

    enriched_new_hosts = [
        enriched_by_host.get(item.get("host"), item)
        for item in new_hosts
    ]
    enriched_rising_hosts = [
        enriched_by_host.get(item.get("host"), item)
        for item in rising_hosts
    ]

    total_new_clicks = sum(safe_float(item.get("clicks_sum")) for item in enriched_new_hosts)
    total_rising_clicks = sum(safe_float(item.get("clicks_sum")) for item in enriched_rising_hosts)
    source_stamp = (current_snapshot.get("meta") or {}).get("sourceStamp", "-")
    start_date, end_date = infer_trend_window(current_hosts)

    lines: List[str] = []
    lines.append(f"# 新增子域名监控报告（{source_stamp}）")
    lines.append("")
    lines.append(f"- 本次新增子域名数量：**{len(enriched_new_hosts)}**")
    lines.append(f"- 新增子域名总点击量：**{to_clicks_str(total_new_clicks)}**")
    lines.append(f"- 本次持续上涨（非新增）子域名数量：**{len(enriched_rising_hosts)}**")
    lines.append(f"- 持续上涨（非新增）子域名总点击量：**{to_clicks_str(total_rising_clicks)}**")
    if start_date and end_date:
        lines.append(f"- 趋势统计窗口：**{start_date} ~ {end_date}**")
    lines.append(
        f"- 持续上涨判定口径：**最近{RISING_WINDOW_POINTS}周连续上涨 + 窗口涨幅≥{int(RISING_MIN_GROWTH_RATIO * 100)}% + 最新值≥{to_clicks_str(RISING_MIN_LATEST_CLICKS)}**"
    )
    if previous_stamp:
        lines.append(f"- 对比基线：**{previous_stamp}**")
    else:
        lines.append("- 说明：首次运行，无历史基线，本次按当前全量结果展示。")
    lines.append("")

    lines.append("## 新增子域名详情（关键词趋势 + 网站用途）")
    lines.append("")
    if not enriched_new_hosts:
        lines.append("本次无新增子域名。")
        lines.append("")
    else:
        for idx, item in enumerate(enriched_new_hosts, start=1):
            render_host_detail(lines, idx, item, with_rise=False)

    lines.append("## 最近点击量持续上涨的子域名详情（非新增，关键词趋势 + 网站用途）")
    lines.append("")
    if not previous_snapshot:
        lines.append("无历史基线，暂无法判断非新增子域名的持续上涨。")
        lines.append("")
    elif not enriched_rising_hosts:
        lines.append("本期无符合持续上涨条件的非新增子域名。")
        lines.append("")
    else:
        for idx, item in enumerate(enriched_rising_hosts, start=1):
            render_host_detail(lines, idx, item, with_rise=True)

    content = "\n".join(lines)
    return content, len(enriched_new_hosts)


def write_subdomain_list(snapshot: dict, out_path: Path) -> int:
    hosts = snapshot.get("hosts") or []
    subdomains = sorted(
        {
            item.get("subdomain", "")
            for item in hosts
            if isinstance(item, dict) and isinstance(item.get("subdomain"), str) and item.get("subdomain")
        }
    )
    out_path.write_text("\n".join(subdomains) + ("\n" if subdomains else ""), encoding="utf-8")
    return len(subdomains)


def run_pipeline(args: argparse.Namespace) -> int:
    data_dir = Path(args.data_dir).resolve()
    snapshot_dir = Path(args.snapshot_dir).resolve()
    report_dir = Path(args.report_dir).resolve()
    latest_report_path = Path(args.latest_report_path).resolve()

    ensure_dir(snapshot_dir)
    ensure_dir(report_dir)
    ensure_dir(latest_report_path.parent)

    raw_candidates = list_timed_files(data_dir, RAW_FILE_RE)
    if not raw_candidates:
        raise SystemExit(f"No raw JSON files found in {data_dir}")

    if args.raw_file:
        current_raw_path = Path(args.raw_file).resolve()
        current_stamp = parse_filename_stamp(current_raw_path, RAW_FILE_RE)
        if not current_stamp:
            raise SystemExit(
                "--raw-file must match filename pattern: [rule]-YYYYMMDD-HHMM.json"
            )
    else:
        current = raw_candidates[-1]
        current_raw_path = current.path
        current_stamp = current.stamp

    current_snapshot, _ = build_snapshot_from_raw(current_raw_path, current_stamp)
    current_snapshot_path = snapshot_dir / f"subdomains-{current_stamp}.json"
    dump_json(current_snapshot_path, current_snapshot)

    subdomain_list_path = snapshot_dir / f"subdomain-list-{current_stamp}.txt"
    subdomain_count = write_subdomain_list(current_snapshot, subdomain_list_path)

    previous_snapshot, previous_ref_path = load_previous_snapshot(snapshot_dir, current_stamp)

    # Fallback: if no previous snapshot, try previous raw file as baseline (without persisting it).
    if previous_snapshot is None:
        previous_raw_candidates = [item for item in raw_candidates if item.stamp < current_stamp]
        if previous_raw_candidates:
            prev_raw = previous_raw_candidates[-1]
            previous_snapshot, _ = build_snapshot_from_raw(prev_raw.path, prev_raw.stamp)
            previous_ref_path = prev_raw.path

    previous_stamp = None
    if previous_ref_path:
        previous_stamp = parse_filename_stamp(previous_ref_path, SNAPSHOT_FILE_RE)
    if not previous_stamp and previous_snapshot:
        previous_stamp = (previous_snapshot.get("meta") or {}).get("sourceStamp")

    report_path = report_dir / f"final-report-{current_stamp}.md"
    report_content, new_count = render_report(
        current_snapshot=current_snapshot,
        previous_snapshot=previous_snapshot,
        previous_stamp=previous_stamp,
    )
    report_path.write_text(report_content, encoding="utf-8")
    latest_report_path.write_text(report_content, encoding="utf-8")

    print(f"[done] current raw      : {current_raw_path}")
    print(f"[done] snapshot         : {current_snapshot_path}")
    print(f"[done] subdomain list   : {subdomain_list_path} ({subdomain_count})")
    print(f"[done] report history   : {report_path}")
    print(f"[done] report latest    : {latest_report_path}")
    print(f"[done] current hosts    : {len(current_snapshot.get('hosts', []))}")
    print(f"[done] new hosts        : {new_count}")
    if previous_ref_path:
        print(f"[done] previous baseline: {previous_ref_path}")
    else:
        print("[done] previous baseline: N/A (bootstrap run)")

    return 0


def rebuild_reports(args: argparse.Namespace) -> int:
    snapshot_dir = Path(args.snapshot_dir).resolve()
    report_dir = Path(args.report_dir).resolve()
    latest_report_path = Path(args.latest_report_path).resolve()

    ensure_dir(snapshot_dir)
    ensure_dir(report_dir)
    ensure_dir(latest_report_path.parent)

    snapshot_files = list_timed_files(snapshot_dir, SNAPSHOT_FILE_RE)
    if not snapshot_files:
        raise SystemExit(f"No snapshot files found in {snapshot_dir}")

    latest_content = ""
    latest_stamp = ""

    for idx, timed in enumerate(snapshot_files):
        current_snapshot = load_json(timed.path)

        previous_snapshot = None
        previous_stamp = None
        if idx > 0:
            prev_file = snapshot_files[idx - 1]
            previous_snapshot = load_json(prev_file.path)
            previous_stamp = prev_file.stamp

        report_content, new_count = render_report(
            current_snapshot=current_snapshot,
            previous_snapshot=previous_snapshot,
            previous_stamp=previous_stamp,
        )

        report_path = report_dir / f"final-report-{timed.stamp}.md"
        report_path.write_text(report_content, encoding="utf-8")
        print(f"[done] rebuilt report   : {report_path} (new_hosts={new_count})")

        latest_content = report_content
        latest_stamp = timed.stamp

    latest_report_path.write_text(latest_content, encoding="utf-8")
    print(f"[done] latest updated   : {latest_report_path} (stamp={latest_stamp})")

    return 0


def main() -> int:
    args = parse_args()
    if args.command == "run":
        return run_pipeline(args)
    if args.command == "rebuild-reports":
        return rebuild_reports(args)
    raise SystemExit(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
