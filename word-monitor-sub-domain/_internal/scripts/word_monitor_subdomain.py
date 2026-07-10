#!/usr/bin/env python3
"""监控子域名落地页样本并输出对比报告（MVP）。

Usage:
  python3 word-monitor-sub-domain/_internal/scripts/word_monitor_subdomain.py run
  python3 word-monitor-sub-domain/_internal/scripts/word_monitor_subdomain.py rebuild-reports
  python3 word-monitor-sub-domain/_internal/scripts/word_monitor_subdomain.py validate-report
"""

from __future__ import annotations

import argparse
import json
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

PROJECT_DIR = Path(__file__).resolve().parents[2]
LOCAL_SERVICE_TOKEN_PATH = PROJECT_DIR / "local-service" / "bridge_token.txt"

DEFAULT_API_BASE = "http://127.0.0.1:17311"
DEFAULT_ENDPOINT = "/sim/api/websiteOrganicLandingPagesV2"

MAX_RETRIES = 2
RETRY_BACKOFF_SECONDS = [0.8, 1.6]
REQUEST_TIMEOUT_SECONDS = 180

PAGE_NEW_MIN_CLICKS = 100.0
PAGE_RISING_MIN_CLICKS = 100.0
PAGE_RISING_MIN_DELTA = 30.0
PAGE_RISING_MIN_GROWTH = 0.05

SUBDOMAIN_NEW_MIN_CLICKS = 150.0
SUBDOMAIN_RISING_MIN_CLICKS = 150.0
SUBDOMAIN_RISING_MIN_DELTA = 50.0
SUBDOMAIN_RISING_MIN_GROWTH = 0.05

SNAPSHOT_RE = re.compile(r"^snapshot-(\d{8}-\d{6})\.json$")

REQUIRED_REMARKS = [
    "当前监控仅覆盖 ClicksShare 排序下前8页样本",
    "“新进入样本”不等于全站首次出现",
    "子域名流量是样本内观测值，不代表全站完整总量",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="监控子域名落地页样本并生成日报")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="抓取 + 快照 + 对比 + 报告")
    run_parser.add_argument("--api-base", default=DEFAULT_API_BASE)
    run_parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    run_parser.add_argument("--token-path", default=str(LOCAL_SERVICE_TOKEN_PATH))

    run_parser.add_argument("--key", default="vercel.app")
    run_parser.add_argument("--country", default="999")
    run_parser.add_argument("--latest", default="28d")
    run_parser.add_argument("--web-source", default="Total")
    run_parser.add_argument("--source-type", default="organic")
    run_parser.add_argument("--sort", default="ClicksShare")
    run_parser.add_argument("--asc", action="store_true", default=False)
    run_parser.add_argument("--include-subdomains", action="store_true", default=True)
    run_parser.add_argument("--is-window", action="store_true", default=True)
    run_parser.add_argument("--search-type", default="domain")
    run_parser.add_argument("--start-page", type=int, default=1)
    run_parser.add_argument("--end-page", type=int, default=8)

    run_parser.add_argument("--data-dir", default=str(PROJECT_DIR / "data"))
    run_parser.add_argument("--snapshot-dir", default=str(PROJECT_DIR / "_internal" / "snapshots"))
    run_parser.add_argument("--report-dir", default=str(PROJECT_DIR / "report" / "history"))
    run_parser.add_argument("--latest-report-path", default=str(PROJECT_DIR / "report" / "latest.md"))

    rebuild_parser = subparsers.add_parser("rebuild-reports", help="根据快照重建历史报告")
    rebuild_parser.add_argument("--snapshot-dir", default=str(PROJECT_DIR / "_internal" / "snapshots"))
    rebuild_parser.add_argument("--report-dir", default=str(PROJECT_DIR / "report" / "history"))
    rebuild_parser.add_argument("--latest-report-path", default=str(PROJECT_DIR / "report" / "latest.md"))

    validate_parser = subparsers.add_parser("validate-report", help="校验 Markdown 报告结构")
    validate_parser.add_argument("--report", default=str(PROJECT_DIR / "report" / "latest.md"))

    return parser.parse_args()


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def safe_float(value) -> float:
    try:
        if value is None:
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def to_int_if_possible(v: float) -> str:
    if abs(v - round(v)) < 1e-9:
        return str(int(round(v)))
    return f"{v:.2f}"


def to_pct(ratio: float) -> str:
    return f"{ratio * 100:.1f}%"


def read_token(path: Path) -> str:
    token = path.read_text(encoding="utf-8").strip()
    if not token:
        raise RuntimeError(f"token 文件为空: {path}")
    return token


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def normalize_landing_page_url(raw_url: str) -> Optional[Tuple[str, str]]:
    if not isinstance(raw_url, str):
        return None
    text = raw_url.strip()
    if not text:
        return None

    if "://" not in text:
        text = f"https://{text}"

    try:
        parsed = urlsplit(text)
    except ValueError:
        return None

    hostname = (parsed.hostname or "").strip().lower().rstrip(".")
    if not hostname:
        return None

    path = parsed.path or "/"
    if path != "/":
        path = "/" + path.lstrip("/")
        path = path.rstrip("/") or "/"

    query = parsed.query.strip()
    canonical = f"https://{hostname}{path}"
    if query:
        canonical += f"?{query}"

    return canonical, hostname


def extract_subdomain(hostname: str, key: str) -> Optional[str]:
    key = key.strip().lower()
    suffix = f".{key}"
    if hostname == key:
        return None
    if not hostname.endswith(suffix):
        return None
    subdomain = hostname[: -len(suffix)]
    if not subdomain:
        return None
    return subdomain


def _post_json(url: str, headers: dict, payload: dict, timeout_seconds: int) -> Tuple[int, str]:
    req = Request(
        url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urlopen(req, timeout=timeout_seconds) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return int(getattr(resp, "status", 0) or 0), body
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace") if hasattr(exc, "read") else ""
        return int(getattr(exc, "code", 0) or 0), body


def fetch_page_with_retry(
    *,
    api_url: str,
    headers: dict,
    base_payload: dict,
    page: int,
) -> dict:
    payload = dict(base_payload)
    payload["page"] = page

    last_error = None
    for attempt in range(MAX_RETRIES + 1):
        try:
            status_code, raw_body = _post_json(
                api_url,
                headers=headers,
                payload=payload,
                timeout_seconds=REQUEST_TIMEOUT_SECONDS,
            )

            wrapper = json.loads(raw_body)
            if not isinstance(wrapper, dict):
                raise RuntimeError("本地服务返回非 JSON 对象")
            if not wrapper.get("ok"):
                err = wrapper.get("error") or {}
                raise RuntimeError(f"本地服务错误: {err.get('code', 'UNKNOWN')} {err.get('message', '')}".strip())

            data = wrapper.get("data") or {}
            upstream_status = int(data.get("status", status_code) or 0)
            if upstream_status != 200:
                raise RuntimeError(f"上游状态码非 200: {upstream_status}")

            upstream_body_raw = data.get("body")
            if not isinstance(upstream_body_raw, str):
                raise RuntimeError("上游 body 缺失或类型错误")
            upstream = json.loads(upstream_body_raw)
            rows = upstream.get("Data")
            if not isinstance(rows, list):
                raise RuntimeError("上游响应 Data 非数组")

            return {
                "page": page,
                "attempt": attempt + 1,
                "requestPayload": payload,
                "wrapper": wrapper,
                "upstream": upstream,
                "rowsCount": len(rows),
            }
        except (RuntimeError, ValueError, json.JSONDecodeError, URLError) as exc:
            last_error = exc
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF_SECONDS[min(attempt, len(RETRY_BACKOFF_SECONDS) - 1)])
                continue
            break

    raise RuntimeError(f"page={page} 抓取失败（已重试 {MAX_RETRIES} 次）: {last_error}")


def fetch_pages(args: argparse.Namespace, token: str) -> Tuple[List[dict], dict]:
    api_url = args.api_base.rstrip("/") + args.endpoint
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    base_payload = {
        "key": args.key,
        "country": args.country,
        "latest": args.latest,
        "webSource": args.web_source,
        "sourceType": args.source_type,
        "sort": args.sort,
        "asc": bool(args.asc),
        "includeSubDomains": bool(args.include_subdomains),
        "isWindow": bool(args.is_window),
        "searchType": args.search_type,
    }

    page_results: List[dict] = []
    for page in range(args.start_page, args.end_page + 1):
        result = fetch_page_with_retry(
            api_url=api_url,
            headers=headers,
            base_payload=base_payload,
            page=page,
        )
        page_results.append(result)

    meta = {
        "apiUrl": api_url,
        "pagesRequested": list(range(args.start_page, args.end_page + 1)),
        "basePayload": base_payload,
    }
    return page_results, meta


def normalize_rows(page_results: List[dict], key: str) -> Tuple[List[dict], dict]:
    rows: List[dict] = []

    stats = {
        "rawRows": 0,
        "invalidUrlRows": 0,
        "nonTargetRows": 0,
    }

    for result in page_results:
        page_num = result["page"]
        upstream = result.get("upstream") or {}
        data_rows = upstream.get("Data") or []

        for idx, item in enumerate(data_rows, start=1):
            stats["rawRows"] += 1
            if not isinstance(item, dict):
                stats["invalidUrlRows"] += 1
                continue

            normalized = normalize_landing_page_url(item.get("Url", ""))
            if not normalized:
                stats["invalidUrlRows"] += 1
                continue

            landing_page_url, hostname = normalized
            subdomain = extract_subdomain(hostname, key)
            if not subdomain:
                stats["nonTargetRows"] += 1
                continue

            rows.append(
                {
                    "landingPageUrl": landing_page_url,
                    "hostname": hostname,
                    "subdomain": subdomain,
                    "clicks": safe_float(item.get("Clicks")),
                    "clicksShare": safe_float(item.get("ClicksShare")),
                    "clicksChangeApi": safe_float(item.get("ClicksChange")),
                    "topKeyword": (item.get("TopKeyword") or "") if isinstance(item.get("TopKeyword"), str) else "",
                    "page": page_num,
                    "rankInPage": idx,
                }
            )

    return rows, stats


def _is_better_sample(candidate: dict, existing: dict) -> bool:
    return (candidate["page"], candidate["rankInPage"]) < (existing["page"], existing["rankInPage"])


def dedupe_rows(rows: List[dict]) -> List[dict]:
    deduped: Dict[str, dict] = {}
    for row in rows:
        key = row["landingPageUrl"]
        old = deduped.get(key)
        if old is None or _is_better_sample(row, old):
            deduped[key] = row

    result = list(deduped.values())
    result.sort(key=lambda r: (-safe_float(r.get("clicks")), r.get("landingPageUrl", "")))
    return result


def aggregate_subdomains(rows: List[dict]) -> List[dict]:
    grouped: Dict[str, dict] = {}
    for row in rows:
        subdomain = row.get("subdomain", "")
        item = grouped.setdefault(
            subdomain,
            {
                "subdomain": subdomain,
                "observedSubdomainClicks": 0.0,
                "landingPagesCount": 0,
            },
        )
        item["observedSubdomainClicks"] += safe_float(row.get("clicks"))
        item["landingPagesCount"] += 1

    result = list(grouped.values())
    result.sort(key=lambda x: (-safe_float(x.get("observedSubdomainClicks")), x.get("subdomain", "")))
    return result


def list_snapshot_files(snapshot_dir: Path) -> List[Path]:
    if not snapshot_dir.exists():
        return []
    files = []
    for p in snapshot_dir.iterdir():
        if p.is_file() and SNAPSHOT_RE.match(p.name):
            files.append(p)
    files.sort(key=lambda p: p.name)
    return files


def snapshot_matches_target(snapshot: dict, target: dict) -> bool:
    meta = snapshot.get("meta") or {}
    meta_target = meta.get("target") or {}
    meta_request = meta.get("request") or {}
    return (
        str(meta_target.get("key", "")) == str(target.get("key", ""))
        and str(meta_target.get("country", "")) == str(target.get("country", ""))
        and str(meta_target.get("latest", "")) == str(target.get("latest", ""))
        and str(meta_target.get("sourceType", "")) == str(target.get("sourceType", ""))
        and int(meta_request.get("startPage", 1) or 1) == int(target.get("startPage", 1) or 1)
        and int(meta_request.get("endPage", 8) or 8) == int(target.get("endPage", 8) or 8)
    )


def find_latest_baseline(snapshot_dir: Path, target: dict, current_stamp: str) -> Tuple[Optional[dict], Optional[Path]]:
    candidates = list_snapshot_files(snapshot_dir)
    for path in reversed(candidates):
        m = SNAPSHOT_RE.match(path.name)
        if not m:
            continue
        stamp = m.group(1)
        if stamp >= current_stamp:
            continue
        snapshot = load_json(path)
        if snapshot_matches_target(snapshot, target):
            return snapshot, path
    return None, None


def build_page_comparison(today_rows: List[dict], baseline_rows: List[dict]) -> Tuple[List[dict], List[dict]]:
    baseline_map = {row["landingPageUrl"]: row for row in baseline_rows}
    newly: List[dict] = []
    rising: List[dict] = []

    for row in today_rows:
        url = row["landingPageUrl"]
        today_clicks = safe_float(row.get("clicks"))
        old = baseline_map.get(url)

        if old is None:
            if today_clicks >= PAGE_NEW_MIN_CLICKS:
                newly.append(row)
            continue

        old_clicks = safe_float(old.get("clicks"))
        delta = today_clicks - old_clicks
        if old_clicks <= 0:
            continue
        growth = delta / old_clicks

        if (
            today_clicks >= PAGE_RISING_MIN_CLICKS
            and delta >= PAGE_RISING_MIN_DELTA
            and growth > PAGE_RISING_MIN_GROWTH
        ):
            item = dict(row)
            item.update(
                {
                    "baseClicks": old_clicks,
                    "deltaClicks": delta,
                    "growthRate": growth,
                }
            )
            rising.append(item)

    newly.sort(key=lambda x: (-safe_float(x.get("clicks")), x.get("landingPageUrl", "")))
    rising.sort(key=lambda x: (-safe_float(x.get("deltaClicks")), x.get("landingPageUrl", "")))
    return newly, rising


def build_subdomain_comparison(today_subdomains: List[dict], baseline_subdomains: List[dict]) -> Tuple[List[dict], List[dict]]:
    baseline_map = {row["subdomain"]: row for row in baseline_subdomains}
    newly: List[dict] = []
    rising: List[dict] = []

    for row in today_subdomains:
        subdomain = row["subdomain"]
        today_clicks = safe_float(row.get("observedSubdomainClicks"))
        old = baseline_map.get(subdomain)

        if old is None:
            if today_clicks >= SUBDOMAIN_NEW_MIN_CLICKS:
                newly.append(row)
            continue

        old_clicks = safe_float(old.get("observedSubdomainClicks"))
        delta = today_clicks - old_clicks
        if old_clicks <= 0:
            continue
        growth = delta / old_clicks

        if (
            today_clicks >= SUBDOMAIN_RISING_MIN_CLICKS
            and delta >= SUBDOMAIN_RISING_MIN_DELTA
            and growth > SUBDOMAIN_RISING_MIN_GROWTH
        ):
            item = dict(row)
            item.update(
                {
                    "baseObservedSubdomainClicks": old_clicks,
                    "deltaClicks": delta,
                    "growthRate": growth,
                }
            )
            rising.append(item)

    newly.sort(key=lambda x: (-safe_float(x.get("observedSubdomainClicks")), x.get("subdomain", "")))
    rising.sort(key=lambda x: (-safe_float(x.get("deltaClicks")), x.get("subdomain", "")))
    return newly, rising


def _path_from_url(raw_url: str) -> str:
    if not isinstance(raw_url, str) or not raw_url:
        return "-"
    try:
        parsed = urlsplit(raw_url)
    except ValueError:
        return "-"

    path = parsed.path or "/"
    if path != "/":
        path = "/" + path.lstrip("/")
        path = path.rstrip("/") or "/"

    if parsed.query:
        return f"{path}?{parsed.query}"
    return path


def build_subdomain_keywords_map(rows: List[dict], *, max_keywords: int = 3) -> Dict[str, str]:
    grouped: Dict[str, List[dict]] = {}
    for row in rows:
        subdomain = row.get("subdomain") or ""
        if not subdomain:
            continue
        grouped.setdefault(subdomain, []).append(row)

    result: Dict[str, str] = {}
    for subdomain, items in grouped.items():
        sorted_items = sorted(
            items,
            key=lambda item: (-safe_float(item.get("clicks")), item.get("landingPageUrl", "")),
        )
        keywords: List[str] = []
        seen = set()
        for item in sorted_items:
            keyword = (item.get("topKeyword") or "").strip()
            if not keyword or keyword in seen:
                continue
            seen.add(keyword)
            keywords.append(keyword)
            if len(keywords) >= max_keywords:
                break
        result[subdomain] = " / ".join(keywords) if keywords else "-"

    return result


def _page_report_row(row: dict, *, trend: str) -> dict:
    growth = safe_float(row.get("growthRate")) if trend == "上涨" else None
    trend_label = trend if growth is None else f"{trend}（+{to_pct(growth)}）"
    return {
        "entityType": "page",
        "trend": trend,
        "trendLabel": trend_label,
        "subdomain": row.get("subdomain", "-") or "-",
        "path": _path_from_url(row.get("landingPageUrl", "")),
        "clicks": safe_float(row.get("clicks")),
        "topKeywords": (row.get("topKeyword") or "-").strip() or "-",
    }


def _subdomain_report_row(row: dict, *, trend: str, subdomain_keywords: Dict[str, str]) -> dict:
    growth = safe_float(row.get("growthRate")) if trend == "上涨" else None
    trend_label = trend if growth is None else f"{trend}（+{to_pct(growth)}）"
    subdomain = row.get("subdomain", "-") or "-"
    return {
        "entityType": "subdomain",
        "trend": trend,
        "trendLabel": trend_label,
        "subdomain": subdomain,
        "path": "-",
        "clicks": safe_float(row.get("observedSubdomainClicks")),
        "topKeywords": subdomain_keywords.get(subdomain, "-"),
    }


def build_report_rows(
    *,
    today_rows: List[dict],
    today_subdomains: List[dict],
    baseline_rows: List[dict],
    baseline_subdomains: List[dict],
) -> List[dict]:
    new_page, rising_page = build_page_comparison(today_rows, baseline_rows)
    new_sub, rising_sub = build_subdomain_comparison(today_subdomains, baseline_subdomains)
    subdomain_keywords = build_subdomain_keywords_map(today_rows)

    report_rows: List[dict] = []
    report_rows.extend(_subdomain_report_row(row, trend="新增", subdomain_keywords=subdomain_keywords) for row in new_sub)
    report_rows.extend(_subdomain_report_row(row, trend="上涨", subdomain_keywords=subdomain_keywords) for row in rising_sub)
    report_rows.extend(_page_report_row(row, trend="新增") for row in new_page)
    report_rows.extend(_page_report_row(row, trend="上涨") for row in rising_page)

    trend_order = {"上涨": 0, "新增": 1}
    entity_order = {"subdomain": 0, "page": 1}
    report_rows.sort(
        key=lambda row: (
            trend_order.get(row.get("trend", ""), 9),
            entity_order.get(row.get("entityType", ""), 9),
            -safe_float(row.get("clicks")),
            row.get("subdomain", ""),
            row.get("path", ""),
        )
    )
    return report_rows


def _md_table(headers: List[str], rows: List[List[str]]) -> List[str]:
    if not rows:
        return ["（无）"]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return lines


def render_report(snapshot: dict) -> str:
    meta = snapshot.get("meta") or {}
    target = meta.get("target") or {}
    comparison = snapshot.get("comparison") or {}

    report_rows = comparison.get("reportRows") or []
    rising_count = sum(1 for row in report_rows if row.get("trend") == "上涨")
    new_count = sum(1 for row in report_rows if row.get("trend") == "新增")

    lines: List[str] = []
    lines.append(f"# 子域名落地页监控报告（{target.get('key', '-') }｜{meta.get('stamp', '-') }）")
    lines.append("")
    lines.append("## 摘要")
    lines.append("")
    lines.append(f"- 抓取页数：{meta.get('pagesFetched', 0)}（page={meta.get('startPage', 1)}..{meta.get('endPage', 8)}）")
    lines.append(f"- 原始行数：{meta.get('rawRows', 0)}")
    lines.append(f"- 去重后页面数：{meta.get('dedupedRows', 0)}")
    lines.append(f"- 观测子域名数：{meta.get('subdomainCount', 0)}")

    if meta.get("baselineMode"):
        lines.append("- 基线：无历史快照（本次仅建立基线）")
    else:
        lines.append(f"- 基线：{comparison.get('baselineStamp', '-')}")

    lines.append(f"- 新增数量：{new_count}")
    lines.append(f"- 上涨数量：{rising_count}")
    lines.append("")

    lines.append("## 监控结果")
    lines.append("")

    if meta.get("baselineMode"):
        lines.append("本次仅建立基线，不输出新增/上涨结论。")
        lines.append("")
    else:
        table_rows = [
            [
                row.get("subdomain", "-"),
                row.get("path", "-"),
                to_int_if_possible(safe_float(row.get("clicks"))),
                row.get("trendLabel", row.get("trend", "-")) or "-",
                row.get("topKeywords", "-") or "-",
            ]
            for row in report_rows
        ]
        lines.extend(_md_table(["subdomain", "path", "clicks", "trend", "top keywords"], table_rows))
        lines.append("")

    lines.append("## 备注")
    lines.append("")
    for remark in REQUIRED_REMARKS:
        lines.append(f"- {remark}")
    lines.append("")

    return "\n".join(lines)


def build_snapshot(
    *,
    stamp: str,
    args: argparse.Namespace,
    rows: List[dict],
    subdomains: List[dict],
    comparison: dict,
    baseline_mode: bool,
    fetch_meta: dict,
    normalize_stats: dict,
) -> dict:
    return {
        "meta": {
            "generatedAt": datetime.now().isoformat(timespec="seconds"),
            "stamp": stamp,
            "baselineMode": baseline_mode,
            "target": {
                "key": args.key,
                "country": args.country,
                "latest": args.latest,
                "webSource": args.web_source,
                "sourceType": args.source_type,
            },
            "request": {
                "sort": args.sort,
                "asc": bool(args.asc),
                "includeSubDomains": bool(args.include_subdomains),
                "isWindow": bool(args.is_window),
                "searchType": args.search_type,
                "startPage": args.start_page,
                "endPage": args.end_page,
            },
            "api": fetch_meta,
            "pagesFetched": args.end_page - args.start_page + 1,
            "startPage": args.start_page,
            "endPage": args.end_page,
            "rawRows": normalize_stats["rawRows"],
            "dedupedRows": len(rows),
            "subdomainCount": len(subdomains),
            "invalidUrlRows": normalize_stats["invalidUrlRows"],
            "nonTargetRows": normalize_stats["nonTargetRows"],
        },
        "rows": rows,
        "subdomains": subdomains,
        "comparison": comparison,
    }


def run_pipeline(args: argparse.Namespace) -> int:
    data_dir = Path(args.data_dir).resolve()
    snapshot_dir = Path(args.snapshot_dir).resolve()
    report_dir = Path(args.report_dir).resolve()
    latest_report_path = Path(args.latest_report_path).resolve()
    token_path = Path(args.token_path).resolve()

    ensure_dir(data_dir)
    ensure_dir(snapshot_dir)
    ensure_dir(report_dir)
    ensure_dir(latest_report_path.parent)

    stamp = now_stamp()

    target = {
        "key": args.key,
        "country": args.country,
        "latest": args.latest,
        "sourceType": args.source_type,
        "startPage": args.start_page,
        "endPage": args.end_page,
    }
    baseline_snapshot, baseline_path = find_latest_baseline(snapshot_dir, target, current_stamp=stamp)
    baseline_rows = baseline_snapshot.get("rows", []) if baseline_snapshot else []
    baseline_subs = baseline_snapshot.get("subdomains", []) if baseline_snapshot else []

    token = read_token(token_path)

    # 先抓取并在内存中处理；任一页失败会抛错并整次退出，不落任何文件。
    page_results, fetch_meta = fetch_pages(args, token)

    normalized_rows, normalize_stats = normalize_rows(page_results, args.key)
    deduped_rows = dedupe_rows(normalized_rows)
    subdomains = aggregate_subdomains(deduped_rows)

    baseline_mode = baseline_snapshot is None
    if baseline_mode:
        comparison = {
            "baselineStamp": None,
            "reportRows": [],
        }
    else:
        comparison = {
            "baselineStamp": ((baseline_snapshot.get("meta") or {}).get("stamp") if baseline_snapshot else None),
            "reportRows": build_report_rows(
                today_rows=deduped_rows,
                today_subdomains=subdomains,
                baseline_rows=baseline_rows,
                baseline_subdomains=baseline_subs,
            ),
        }

    snapshot = build_snapshot(
        stamp=stamp,
        args=args,
        rows=deduped_rows,
        subdomains=subdomains,
        comparison=comparison,
        baseline_mode=baseline_mode,
        fetch_meta=fetch_meta,
        normalize_stats=normalize_stats,
    )

    report = render_report(snapshot)

    # 到这里才落盘，保证抓取失败不会产生污染文件。
    fetch_archive_path = data_dir / f"fetch-{stamp}.json"
    snapshot_path = snapshot_dir / f"snapshot-{stamp}.json"
    report_history_path = report_dir / f"report-{stamp}.md"

    fetch_archive_payload = {
        "meta": {
            "generatedAt": datetime.now().isoformat(timespec="seconds"),
            "stamp": stamp,
            "target": target,
            "request": fetch_meta,
        },
        "pages": page_results,
    }

    dump_json(fetch_archive_path, fetch_archive_payload)
    dump_json(snapshot_path, snapshot)
    report_history_path.write_text(report, encoding="utf-8")
    latest_report_path.write_text(report, encoding="utf-8")

    print(f"[done] fetch archive : {fetch_archive_path}")
    print(f"[done] snapshot      : {snapshot_path}")
    print(f"[done] report history: {report_history_path}")
    print(f"[done] report latest : {latest_report_path}")
    print(f"[done] deduped rows  : {len(deduped_rows)}")
    print(f"[done] subdomains    : {len(subdomains)}")
    if baseline_mode:
        print("[done] baseline      : none (first run)")
    else:
        print(f"[done] baseline      : {baseline_path}")

    return 0


def rebuild_reports(args: argparse.Namespace) -> int:
    snapshot_dir = Path(args.snapshot_dir).resolve()
    report_dir = Path(args.report_dir).resolve()
    latest_report_path = Path(args.latest_report_path).resolve()

    ensure_dir(snapshot_dir)
    ensure_dir(report_dir)
    ensure_dir(latest_report_path.parent)

    files = list_snapshot_files(snapshot_dir)
    if not files:
        raise SystemExit(f"未找到快照文件: {snapshot_dir}")

    latest_content = ""
    last_for_target: Dict[str, dict] = {}

    for path in files:
        snapshot = load_json(path)
        meta = snapshot.get("meta") or {}
        target = meta.get("target") or {}
        request_meta = meta.get("request") or {}
        target_key = json.dumps(
            {
                "key": target.get("key"),
                "country": target.get("country"),
                "latest": target.get("latest"),
                "sourceType": target.get("sourceType"),
                "startPage": request_meta.get("startPage", meta.get("startPage", 1)),
                "endPage": request_meta.get("endPage", meta.get("endPage", 8)),
            },
            sort_keys=True,
            ensure_ascii=False,
        )

        baseline = last_for_target.get(target_key)
        if baseline is None:
            comparison = {
                "baselineStamp": None,
                "reportRows": [],
            }
            snapshot["meta"]["baselineMode"] = True
        else:
            comparison = {
                "baselineStamp": (baseline.get("meta") or {}).get("stamp"),
                "reportRows": build_report_rows(
                    today_rows=snapshot.get("rows", []),
                    today_subdomains=snapshot.get("subdomains", []),
                    baseline_rows=baseline.get("rows", []),
                    baseline_subdomains=baseline.get("subdomains", []),
                ),
            }
            snapshot["meta"]["baselineMode"] = False

        snapshot["comparison"] = comparison
        dump_json(path, snapshot)

        stamp = meta.get("stamp", path.stem)
        report_content = render_report(snapshot)
        out = report_dir / f"report-{stamp}.md"
        out.write_text(report_content, encoding="utf-8")
        print(f"[done] rebuilt: {out}")

        latest_content = report_content
        last_for_target[target_key] = snapshot

    latest_report_path.write_text(latest_content, encoding="utf-8")
    print(f"[done] latest : {latest_report_path}")
    return 0


def validate_report(args: argparse.Namespace) -> int:
    path = Path(args.report).resolve()
    if not path.exists():
        raise SystemExit(f"报告不存在: {path}")

    text = path.read_text(encoding="utf-8")
    required_sections = [
        "## 摘要",
        "## 监控结果",
        "## 备注",
    ]

    missing = [item for item in required_sections if item not in text]
    missing += [item for item in REQUIRED_REMARKS if item not in text]

    if (
        "无历史快照（本次仅建立基线）" not in text
        and "| subdomain | path | clicks | trend | top keywords |" not in text
        and "## 监控结果\n\n（无）" not in text
    ):
        missing.append("| subdomain | path | clicks | trend | top keywords |")

    if missing:
        print("[failed] 报告校验失败，缺少内容：")
        for item in missing:
            print(f"- {item}")
        return 1

    print(f"[ok] 报告结构校验通过: {path}")
    return 0


def main() -> int:
    args = parse_args()
    if args.command == "run":
        return run_pipeline(args)
    if args.command == "rebuild-reports":
        return rebuild_reports(args)
    if args.command == "validate-report":
        return validate_report(args)
    raise SystemExit(f"未知命令: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
