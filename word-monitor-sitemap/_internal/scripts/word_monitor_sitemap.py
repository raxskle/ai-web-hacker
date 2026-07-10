#!/usr/bin/env python3
"""监控多站点 sitemap，发现新增内页并提取关键词候选（MVP）。

Usage:
  python3 word-monitor-sitemap/_internal/scripts/word_monitor_sitemap.py run
  python3 word-monitor-sitemap/_internal/scripts/word_monitor_sitemap.py run --all-sites
  python3 word-monitor-sitemap/_internal/scripts/word_monitor_sitemap.py run --site onlinegames_io
  python3 word-monitor-sitemap/_internal/scripts/word_monitor_sitemap.py rebuild-reports
  python3 word-monitor-sitemap/_internal/scripts/word_monitor_sitemap.py validate-report --report word-monitor-sitemap/report/latest.md
"""

from __future__ import annotations

import argparse
import gzip
import json
import re
import shutil
import time
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, urlunsplit
from urllib.request import Request, urlopen

PROJECT_DIR = Path(__file__).resolve().parents[2]

DEFAULT_SITES_CONFIG = PROJECT_DIR / "data" / "sites.json"
DEFAULT_DATA_ROOT = PROJECT_DIR / "data"
DEFAULT_SNAPSHOT_ROOT = PROJECT_DIR / "_internal" / "snapshots"
DEFAULT_REPORT_ROOT = PROJECT_DIR / "report"
DEFAULT_REPORT_HISTORY_ROOT = DEFAULT_REPORT_ROOT / "history"
DEFAULT_REPORT_LATEST_ROOT = DEFAULT_REPORT_ROOT

SITEMAP_RETRY = 2
RETRY_BACKOFF_SECONDS = [0.8, 1.6]
SITEMAP_TIMEOUT_SECONDS = 30
MAX_SITEMAPS_PER_SITE = 300

TOP_NEW_URLS_IN_REPORT = 80
TOP_NEW_PATTERNS_IN_REPORT = 40
TOP_KEYWORDS_IN_REPORT = 60

SNAPSHOT_RE = re.compile(r"^snapshot-(\d{8}-\d{6})\.json$")
TOKEN_SPLIT_RE = re.compile(r"[^a-z0-9]+")
NUMERIC_RE = re.compile(r"^\d+$")
HEXISH_RE = re.compile(r"^[a-f0-9]{16,}$", re.IGNORECASE)
UUIDISH_RE = re.compile(r"^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$", re.IGNORECASE)

REQUIRED_SECTIONS = [
    "## 摘要",
    "## Sitemap 概览",
    "## 新增内页",
    "## 新增路由模式",
    "## 新关键词候选",
    "## 备注",
]

REQUIRED_REMARKS = [
    "本报告基于 sitemap 可见 URL 与路由推断，不等于全站完整索引",
    "新增内页基于与最近一次同站点快照对比得出",
    "关键词候选来自新增 URL slug 分词，为机会线索而非搜索引擎全量词库",
]

MERGED_LATEST_FILE = "latest.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="监控 sitemap 并输出新增内页关键词报告")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="抓 sitemap + 快照 + 对比 + 报告（默认运行 sites.json 中 enabled=true 的站点）")
    run_group = run_parser.add_mutually_exclusive_group(required=False)
    run_group.add_argument("--site", help="仅运行单站（site id）")
    run_group.add_argument("--all-sites", action="store_true", help="运行 sites.json 中全部站点（包含 enabled=false）")
    run_parser.add_argument("--sites-config", default=str(DEFAULT_SITES_CONFIG))
    run_parser.add_argument("--data-root", default=str(DEFAULT_DATA_ROOT))
    run_parser.add_argument("--snapshot-root", default=str(DEFAULT_SNAPSHOT_ROOT))
    run_parser.add_argument("--report-history-root", default=str(DEFAULT_REPORT_HISTORY_ROOT))
    run_parser.add_argument("--report-latest-root", default=str(DEFAULT_REPORT_LATEST_ROOT))

    rebuild_parser = subparsers.add_parser("rebuild-reports", help="根据快照重建历史报告")
    rebuild_parser.add_argument("--site", help="仅重建单站（默认重建所有）")
    rebuild_parser.add_argument("--sites-config", default=str(DEFAULT_SITES_CONFIG))
    rebuild_parser.add_argument("--snapshot-root", default=str(DEFAULT_SNAPSHOT_ROOT))
    rebuild_parser.add_argument("--report-history-root", default=str(DEFAULT_REPORT_HISTORY_ROOT))
    rebuild_parser.add_argument("--report-latest-root", default=str(DEFAULT_REPORT_LATEST_ROOT))

    validate_parser = subparsers.add_parser("validate-report", help="校验 Markdown 报告结构")
    validate_parser.add_argument(
        "--report",
        default=str(DEFAULT_REPORT_LATEST_ROOT / MERGED_LATEST_FILE),
        help="报告路径（默认校验 report/latest.md）",
    )

    return parser.parse_args()


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def safe_int(value) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def to_int_if_possible(v: float) -> str:
    if abs(v - round(v)) < 1e-9:
        return str(int(round(v)))
    return f"{v:.2f}"


def _md_table(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> List[str]:
    if not rows:
        return ["（无）"]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return lines


def _local_name(tag: str) -> str:
    if not isinstance(tag, str):
        return ""
    if tag.startswith("{") and "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def _iter_loc_texts(root: ET.Element, mode: str) -> List[str]:
    if mode == "urlset":
        xpath = ".//{*}url/{*}loc"
    elif mode == "sitemapindex":
        xpath = ".//{*}sitemap/{*}loc"
    else:
        xpath = ".//{*}loc"

    locs = []
    for node in root.findall(xpath):
        text = (node.text or "").strip()
        if text:
            locs.append(text)

    # 兜底：某些站点命名空间异常时，按本地名扫描。
    if locs:
        return locs

    if mode == "urlset":
        parent_name = "url"
    elif mode == "sitemapindex":
        parent_name = "sitemap"
    else:
        parent_name = None

    for parent in root.iter():
        if parent_name and _local_name(parent.tag) != parent_name:
            continue
        for child in list(parent):
            if _local_name(child.tag) != "loc":
                continue
            text = (child.text or "").strip()
            if text:
                locs.append(text)
    return locs


def _decode_http_body(raw: bytes, headers: dict, url: str) -> str:
    data = raw
    content_encoding = (headers.get("Content-Encoding") or "").lower()
    if "gzip" in content_encoding or url.lower().endswith(".gz") or data[:2] == b"\x1f\x8b":
        try:
            data = gzip.decompress(data)
        except OSError:
            pass

    for enc in ("utf-8", "utf-8-sig", "gb18030", "latin-1"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def fetch_url_text_with_retry(url: str, timeout_seconds: int = SITEMAP_TIMEOUT_SECONDS) -> dict:
    last_error: Optional[Exception] = None
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/125.0 Safari/537.36 sitemap-monitor/1.0",
        "Accept": "application/xml,text/xml,application/xhtml+xml,text/html;q=0.8,*/*;q=0.5",
        "Accept-Language": "en-US,en;q=0.9",
    }

    for attempt in range(SITEMAP_RETRY + 1):
        req = Request(url, headers=headers, method="GET")
        try:
            with urlopen(req, timeout=timeout_seconds) as resp:
                status = int(getattr(resp, "status", 200) or 200)
                body_bytes = resp.read()
                body_text = _decode_http_body(body_bytes, dict(resp.headers), str(resp.geturl()))
                return {
                    "url": url,
                    "finalUrl": str(resp.geturl()),
                    "status": status,
                    "attempt": attempt + 1,
                    "headers": {k: v for k, v in resp.headers.items()},
                    "bytes": len(body_bytes),
                    "body": body_text,
                }
        except HTTPError as exc:
            body = b""
            if hasattr(exc, "read"):
                try:
                    body = exc.read()
                except Exception:
                    body = b""
            decoded = _decode_http_body(body, dict(getattr(exc, "headers", {}) or {}), url)
            last_error = RuntimeError(f"HTTP {exc.code} {exc.reason}; body={decoded[:200]}")
        except (URLError, TimeoutError, OSError) as exc:
            last_error = exc

        if attempt < SITEMAP_RETRY:
            time.sleep(RETRY_BACKOFF_SECONDS[min(attempt, len(RETRY_BACKOFF_SECONDS) - 1)])

    raise RuntimeError(f"抓取 sitemap 失败: {url}: {last_error}")


def normalize_url_for_queue(raw_url: str) -> Optional[str]:
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

    host = (parsed.hostname or "").strip().lower().rstrip(".")
    if not host:
        return None

    path = parsed.path or "/"
    query = parsed.query or ""
    scheme = (parsed.scheme or "https").lower()
    if scheme not in {"http", "https"}:
        scheme = "https"

    normalized = urlunsplit((scheme, host, path, query, ""))
    return normalized


def crawl_sitemaps(site: dict) -> Tuple[List[str], dict]:
    site_id = str(site.get("id", "")).strip()
    start_urls = site.get("sitemapUrls") or []
    if not isinstance(start_urls, list) or not start_urls:
        raise RuntimeError(f"站点 {site_id} 未配置 sitemapUrls")

    queue: List[Tuple[str, int, Optional[str]]] = []
    visited = set()
    fetches: List[dict] = []
    page_urls: List[str] = []

    for raw in start_urls:
        normalized = normalize_url_for_queue(str(raw))
        if normalized and normalized not in visited:
            queue.append((normalized, 0, None))
            visited.add(normalized)

    if not queue:
        raise RuntimeError(f"站点 {site_id} 的 sitemapUrls 无有效 URL")

    discovered_sitemap_urls = 0

    while queue:
        if len(fetches) >= MAX_SITEMAPS_PER_SITE:
            raise RuntimeError(
                f"站点 {site_id} sitemap 数量超过上限 {MAX_SITEMAPS_PER_SITE}，可能存在异常膨胀或循环引用"
            )

        sitemap_url, depth, parent = queue.pop(0)
        fetched = fetch_url_text_with_retry(sitemap_url)

        try:
            root = ET.fromstring(fetched["body"])
        except ET.ParseError as exc:
            raise RuntimeError(f"解析 XML 失败: {sitemap_url}: {exc}") from exc

        root_name = _local_name(root.tag)
        if root_name == "urlset":
            mode = "urlset"
            locs = _iter_loc_texts(root, "urlset")
            page_urls.extend(locs)
            child_sitemaps = 0
        elif root_name == "sitemapindex":
            mode = "sitemapindex"
            locs = _iter_loc_texts(root, "sitemapindex")
            child_sitemaps = len(locs)
            for raw in locs:
                normalized = normalize_url_for_queue(raw)
                if not normalized or normalized in visited:
                    continue
                queue.append((normalized, depth + 1, sitemap_url))
                visited.add(normalized)
                discovered_sitemap_urls += 1
        else:
            mode = "unknown"
            locs = _iter_loc_texts(root, "generic")
            page_urls.extend(locs)
            child_sitemaps = 0

        fetches.append(
            {
                "url": sitemap_url,
                "finalUrl": fetched.get("finalUrl"),
                "status": fetched.get("status"),
                "attempt": fetched.get("attempt"),
                "depth": depth,
                "parent": parent,
                "type": mode,
                "locCount": len(locs),
                "childSitemaps": child_sitemaps,
                "bytes": fetched.get("bytes", 0),
            }
        )

    deduped = sorted({u.strip() for u in page_urls if isinstance(u, str) and u.strip()})

    crawl_meta = {
        "siteId": site_id,
        "startSitemapUrls": start_urls,
        "sitemapsFetched": len(fetches),
        "sitemapUrlsDiscovered": discovered_sitemap_urls,
        "ignoredByDepthLimit": 0,
        "rawPageUrlCount": len(page_urls),
        "dedupedPageUrlCount": len(deduped),
        "fetches": fetches,
        "limits": {
            "maxSitemapsPerSite": MAX_SITEMAPS_PER_SITE,
        },
    }
    return deduped, crawl_meta


def normalize_page_url(raw_url: str) -> Optional[dict]:
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

    host = (parsed.hostname or "").strip().lower().rstrip(".")
    if not host:
        return None

    path = parsed.path or "/"
    if path != "/":
        path = "/" + path.lstrip("/")
        path = path.rstrip("/") or "/"

    canonical = f"https://{host}{path}"
    segments = [seg for seg in path.split("/") if seg]
    slug = segments[-1] if segments else ""

    return {
        "url": canonical,
        "host": host,
        "path": path,
        "segments": segments,
        "slug": slug,
        "depth": len(segments),
    }


def compile_path_rules(regex_list: Iterable[str]) -> List[re.Pattern]:
    compiled = []
    for idx, item in enumerate(regex_list, start=1):
        pattern = str(item or "").strip()
        if not pattern:
            continue
        try:
            compiled.append(re.compile(pattern))
        except re.error as exc:
            raise RuntimeError(f"excludePathRegexes 第 {idx} 条正则非法: {pattern}; {exc}") from exc
    return compiled


def normalize_site_config(site: dict) -> dict:
    site_id = str(site.get("id", "")).strip()
    if not site_id:
        raise RuntimeError("site.id 不能为空")

    sitemap_urls = site.get("sitemapUrls") or []
    if not isinstance(sitemap_urls, list) or not sitemap_urls:
        raise RuntimeError(f"site={site_id} 缺少 sitemapUrls")

    include_hosts = [str(x).strip().lower() for x in (site.get("includeHosts") or []) if str(x).strip()]
    if not include_hosts:
        raise RuntimeError(f"site={site_id} 缺少 includeHosts")

    exclude_regexes = site.get("excludePathRegexes") or []
    if not isinstance(exclude_regexes, list):
        raise RuntimeError(f"site={site_id} excludePathRegexes 必须是数组")

    keyword_rules = site.get("keywordRules") or {}
    stop_tokens = keyword_rules.get("stopTokens") or []
    min_token_length = safe_int(keyword_rules.get("minTokenLength") or 2)
    if min_token_length <= 0:
        min_token_length = 2

    return {
        "id": site_id,
        "enabled": bool(site.get("enabled", True)),
        "displayName": str(site.get("displayName") or site_id),
        "sitemapUrls": sitemap_urls,
        "includeHosts": include_hosts,
        "excludePathRegexes": [str(x) for x in exclude_regexes],
        "compiledExcludePathRegexes": compile_path_rules(exclude_regexes),
        "keywordRules": {
            "stopTokens": [str(t).strip().lower() for t in stop_tokens if str(t).strip()],
            "minTokenLength": min_token_length,
            "dropNumericOnlyToken": bool(keyword_rules.get("dropNumericOnlyToken", True)),
        },
    }


def load_sites_config(path: Path) -> Dict[str, dict]:
    payload = load_json(path)
    sites = payload.get("sites")
    if not isinstance(sites, list) or not sites:
        raise RuntimeError(f"sites 配置为空: {path}")

    result: Dict[str, dict] = {}
    for raw_site in sites:
        if not isinstance(raw_site, dict):
            continue
        site = normalize_site_config(raw_site)
        site_id = site["id"]
        if site_id in result:
            raise RuntimeError(f"sites 配置存在重复 id: {site_id}")
        result[site_id] = site
    if not result:
        raise RuntimeError(f"sites 配置无有效站点: {path}")
    return result


def filter_and_normalize_urls(raw_urls: List[str], site: dict) -> Tuple[List[dict], dict]:
    include_hosts = set(site.get("includeHosts") or [])
    exclude_rules: List[re.Pattern] = site.get("compiledExcludePathRegexes") or []

    stats = {
        "rawUrls": len(raw_urls),
        "invalidUrls": 0,
        "nonTargetHostUrls": 0,
        "excludedByPathRules": 0,
        "dedupedUrls": 0,
    }

    deduped: Dict[str, dict] = {}

    for raw in raw_urls:
        item = normalize_page_url(raw)
        if item is None:
            stats["invalidUrls"] += 1
            continue

        if item["host"] not in include_hosts:
            stats["nonTargetHostUrls"] += 1
            continue

        excluded = False
        for rule in exclude_rules:
            if rule.search(item["path"]):
                excluded = True
                break
        if excluded:
            stats["excludedByPathRules"] += 1
            continue

        deduped[item["url"]] = item

    rows = list(deduped.values())
    rows.sort(key=lambda x: x["url"])

    stats["dedupedUrls"] = len(rows)
    return rows, stats


def segment_shape(seg: str) -> str:
    text = str(seg or "").strip().lower()
    if not text:
        return "{seg}"
    if NUMERIC_RE.match(text):
        return "{num}"
    if HEXISH_RE.match(text) or UUIDISH_RE.match(text):
        return "{id}"

    if re.match(r"^[a-z0-9]+(?:-[a-z0-9]+)*$", text):
        tokens = text.split("-")
        if len(tokens) == 1:
            return "{token}"
        return "-".join(["{token}"] * len(tokens))

    return "{seg}"


def infer_patterns(rows: List[dict]) -> List[dict]:
    grouped: Dict[str, dict] = {}

    for row in rows:
        segments = row.get("segments") or []
        if not segments:
            pattern = "/"
        else:
            shaped = [segment_shape(seg) for seg in segments]
            pattern = "/" + "/".join(shaped) + "/"

        item = grouped.setdefault(
            pattern,
            {
                "pattern": pattern,
                "count": 0,
                "exampleUrls": [],
            },
        )
        item["count"] += 1
        if len(item["exampleUrls"]) < 3:
            item["exampleUrls"].append(row.get("url", ""))

    patterns = list(grouped.values())
    patterns.sort(key=lambda x: (-safe_int(x.get("count")), x.get("pattern", "")))
    return patterns


def build_comparison(today_rows: List[dict], baseline_rows: List[dict], today_patterns: List[dict], baseline_patterns: List[dict]) -> dict:
    baseline_map = {row.get("url"): row for row in baseline_rows}
    today_map = {row.get("url"): row for row in today_rows}

    newly_added_urls = [row for row in today_rows if row.get("url") not in baseline_map]
    removed_urls = [row for row in baseline_rows if row.get("url") not in today_map]

    baseline_pattern_map = {item.get("pattern"): item for item in baseline_patterns}
    new_patterns = [item for item in today_patterns if item.get("pattern") not in baseline_pattern_map]

    return {
        "newlyAddedUrls": newly_added_urls,
        "removedUrls": removed_urls,
        "newPatterns": new_patterns,
    }


def _clean_tokens(slug_text: str, keyword_rules: dict) -> List[str]:
    stop_tokens = set(keyword_rules.get("stopTokens") or [])
    min_token_length = safe_int(keyword_rules.get("minTokenLength") or 2)
    drop_numeric_only = bool(keyword_rules.get("dropNumericOnlyToken", True))

    raw_tokens = [t for t in TOKEN_SPLIT_RE.split((slug_text or "").lower()) if t]
    cleaned = []
    for t in raw_tokens:
        if t in stop_tokens:
            continue
        if drop_numeric_only and NUMERIC_RE.match(t):
            continue
        if len(t) < min_token_length:
            continue
        cleaned.append(t)
    return cleaned


def extract_keywords(new_urls: List[dict], keyword_rules: dict) -> dict:
    phrase_counter: Counter = Counter()
    token_counter: Counter = Counter()
    bigram_counter: Counter = Counter()

    phrase_urls: Dict[str, set] = defaultdict(set)
    token_urls: Dict[str, set] = defaultdict(set)
    bigram_urls: Dict[str, set] = defaultdict(set)

    for row in new_urls:
        slug = str(row.get("slug") or "").strip().lower()
        if not slug:
            continue

        cleaned = _clean_tokens(slug, keyword_rules)
        if not cleaned:
            continue

        source_url = row.get("url", "")

        phrase = " ".join(cleaned)
        if phrase:
            phrase_counter[phrase] += 1
            phrase_urls[phrase].add(source_url)

        for token in cleaned:
            token_counter[token] += 1
            token_urls[token].add(source_url)

        for i in range(len(cleaned) - 1):
            bigram = f"{cleaned[i]} {cleaned[i + 1]}"
            bigram_counter[bigram] += 1
            bigram_urls[bigram].add(source_url)

    entries = []

    def append_entries(kind: str, counter: Counter, url_map: Dict[str, set], weight: float) -> None:
        for kw, count in counter.items():
            urls = sorted({u for u in url_map.get(kw, set()) if u})
            url_count = len(urls)
            score = round(float(count) * weight + float(url_count) * 0.3, 3)
            entries.append(
                {
                    "type": kind,
                    "keyword": kw,
                    "count": int(count),
                    "urlCount": url_count,
                    "score": score,
                    "exampleUrls": urls[:3],
                }
            )

    append_entries("phrase", phrase_counter, phrase_urls, 1.2)
    append_entries("bigram", bigram_counter, bigram_urls, 1.0)
    append_entries("token", token_counter, token_urls, 0.8)

    entries.sort(key=lambda x: (-float(x.get("score", 0.0)), -safe_int(x.get("urlCount")), x.get("keyword", ""), x.get("type", "")))

    return {
        "topKeywordsFromNewUrls": entries[:TOP_KEYWORDS_IN_REPORT],
        "counters": {
            "phrase": phrase_counter.most_common(120),
            "bigram": bigram_counter.most_common(120),
            "token": token_counter.most_common(200),
        },
    }


def build_snapshot(
    *,
    stamp: str,
    site: dict,
    crawl_meta: dict,
    normalize_stats: dict,
    rows: List[dict],
    patterns: List[dict],
    baseline_stamp: Optional[str],
    baseline_mode: bool,
    comparison: dict,
    keyword_result: dict,
) -> dict:
    return {
        "meta": {
            "generatedAt": datetime.now().isoformat(timespec="seconds"),
            "stamp": stamp,
            "baselineMode": baseline_mode,
            "site": {
                "id": site.get("id"),
                "displayName": site.get("displayName"),
                "sitemapUrls": site.get("sitemapUrls"),
                "includeHosts": site.get("includeHosts"),
            },
            "crawl": {
                "sitemapsFetched": crawl_meta.get("sitemapsFetched", 0),
                "sitemapUrlsDiscovered": crawl_meta.get("sitemapUrlsDiscovered", 0),
                "ignoredByDepthLimit": crawl_meta.get("ignoredByDepthLimit", 0),
                "rawPageUrlCount": crawl_meta.get("rawPageUrlCount", 0),
                "dedupedPageUrlCount": crawl_meta.get("dedupedPageUrlCount", 0),
            },
            "normalize": normalize_stats,
            "effectiveUrlCount": len(rows),
            "patternCount": len(patterns),
            "baselineStamp": baseline_stamp,
        },
        "urls": rows,
        "patterns": patterns,
        "comparison": {
            "baselineStamp": baseline_stamp,
            "newlyAddedUrls": comparison.get("newlyAddedUrls", []),
            "removedUrls": comparison.get("removedUrls", []),
            "newPatterns": comparison.get("newPatterns", []),
        },
        "keywords": {
            "topKeywordsFromNewUrls": keyword_result.get("topKeywordsFromNewUrls", []),
            "counters": keyword_result.get("counters", {}),
        },
    }


def render_report(snapshot: dict) -> str:
    meta = snapshot.get("meta") or {}
    site_meta = meta.get("site") or {}
    comparison = snapshot.get("comparison") or {}

    urls = snapshot.get("urls") or []
    patterns = snapshot.get("patterns") or []
    new_urls = comparison.get("newlyAddedUrls") or []
    removed_urls = comparison.get("removedUrls") or []
    new_patterns = comparison.get("newPatterns") or []
    top_keywords = (snapshot.get("keywords") or {}).get("topKeywordsFromNewUrls") or []

    depth_counter = Counter()
    for row in urls:
        depth_counter[safe_int(row.get("depth"))] += 1

    lines: List[str] = []
    lines.append(f"# Sitemap 监控报告（{site_meta.get('id', '-')}｜{meta.get('stamp', '-')}）")
    lines.append("")

    lines.append("## 摘要")
    lines.append("")
    lines.append(f"- 站点：{site_meta.get('displayName', '-')}")
    lines.append(f"- sitemap 抓取数：{(meta.get('crawl') or {}).get('sitemapsFetched', 0)}")
    lines.append(f"- URL 原始数：{(meta.get('crawl') or {}).get('rawPageUrlCount', 0)}")
    lines.append(f"- URL 去重数：{(meta.get('crawl') or {}).get('dedupedPageUrlCount', 0)}")
    lines.append(f"- 有效内页数：{meta.get('effectiveUrlCount', 0)}")
    lines.append(f"- 路由模式数：{meta.get('patternCount', 0)}")

    if meta.get("baselineMode"):
        lines.append("- 基线：无历史快照（本次仅建立基线）")
    else:
        lines.append(f"- 基线：{meta.get('baselineStamp', '-')}")

    lines.append(f"- 新增内页数：{len(new_urls)}")
    lines.append(f"- 移除内页数：{len(removed_urls)}")
    lines.append(f"- 新增路由模式数：{len(new_patterns)}")
    lines.append(f"- 新关键词候选数：{len(top_keywords)}")
    lines.append("")

    lines.append("## Sitemap 概览")
    lines.append("")
    lines.append(f"- includeHosts: {', '.join(site_meta.get('includeHosts') or [])}")
    lines.append(
        "- pathDepth 分布: "
        + ", ".join([f"depth={depth}: {count}" for depth, count in sorted(depth_counter.items())])
        if depth_counter
        else "- pathDepth 分布: （无）"
    )
    lines.append("")

    lines.append("## 新增内页")
    lines.append("")
    if meta.get("baselineMode"):
        lines.append("本次仅建立基线，不输出新增内页。")
    else:
        rows = []
        for row in new_urls[:TOP_NEW_URLS_IN_REPORT]:
            rows.append(
                [
                    row.get("url", "-"),
                    row.get("path", "-"),
                    row.get("slug", "-") or "-",
                    str(row.get("depth", "-")),
                ]
            )
        lines.extend(_md_table(["url", "path", "slug", "depth"], rows))
    lines.append("")

    lines.append("## 新增路由模式")
    lines.append("")
    if meta.get("baselineMode"):
        lines.append("本次仅建立基线，不输出新增路由模式。")
    else:
        rows = []
        for row in new_patterns[:TOP_NEW_PATTERNS_IN_REPORT]:
            rows.append(
                [
                    row.get("pattern", "-"),
                    str(row.get("count", 0)),
                    "<br>".join(row.get("exampleUrls") or []),
                ]
            )
        lines.extend(_md_table(["pattern", "count", "examples"], rows))
    lines.append("")

    lines.append("## 新关键词候选")
    lines.append("")
    if meta.get("baselineMode"):
        lines.append("本次仅建立基线，不输出关键词候选。")
    else:
        rows = []
        for kw in top_keywords[:TOP_KEYWORDS_IN_REPORT]:
            rows.append(
                [
                    kw.get("type", "-"),
                    kw.get("keyword", "-"),
                    f"{float(kw.get('score', 0.0)):.2f}",
                    str(kw.get("urlCount", 0)),
                    "<br>".join(kw.get("exampleUrls") or []),
                ]
            )
        lines.extend(_md_table(["type", "keyword", "score", "urlCount", "examples"], rows))
    lines.append("")

    lines.append("## 备注")
    lines.append("")
    for remark in REQUIRED_REMARKS:
        lines.append(f"- {remark}")
    lines.append("")

    # 方便排查：附主模式 Top 10（不作为必需 section）
    lines.append("## 附录：主路由模式（Top 10）")
    lines.append("")
    rows = []
    for p in patterns[:10]:
        rows.append(
            [
                p.get("pattern", "-"),
                str(p.get("count", 0)),
                "<br>".join(p.get("exampleUrls") or []),
            ]
        )
    lines.extend(_md_table(["pattern", "count", "examples"], rows))
    lines.append("")

    return "\n".join(lines)


def render_merged_report(*, stamp: str, site_results: List[dict]) -> str:
    total_effective = sum(safe_int(r.get("effectiveUrlCount")) for r in site_results)
    total_new = sum(safe_int(r.get("newlyAddedCount")) for r in site_results)
    total_removed = sum(safe_int(r.get("removedCount")) for r in site_results)
    total_patterns = sum(safe_int(r.get("newPatternCount")) for r in site_results)
    total_keywords = sum(safe_int(r.get("keywordCount")) for r in site_results)

    lines: List[str] = []
    lines.append(f"# Sitemap 合并监控报告（{stamp}）")
    lines.append("")

    lines.append("## 摘要")
    lines.append("")
    lines.append(f"- 站点数：{len(site_results)}")
    lines.append("- 站点列表：" + ", ".join([r.get("siteId", "-") for r in site_results]))
    lines.append(f"- 有效内页总数：{total_effective}")
    lines.append(f"- 新增内页总数：{total_new}")
    lines.append(f"- 移除内页总数：{total_removed}")
    lines.append(f"- 新增路由模式总数：{total_patterns}")
    lines.append(f"- 新关键词候选总数：{total_keywords}")
    lines.append("")

    lines.append("## Sitemap 概览")
    lines.append("")
    overview_rows = []
    for r in site_results:
        overview_rows.append(
            [
                r.get("siteId", "-"),
                str(r.get("effectiveUrlCount", 0)),
                str(r.get("patternCount", 0)),
                "yes" if r.get("baselineMode") else str(r.get("baselineStamp") or "no"),
            ]
        )
    lines.extend(_md_table(["siteId", "effectiveUrls", "patterns", "baseline"], overview_rows))
    lines.append("")

    lines.append("## 新增内页")
    lines.append("")
    new_rows = []
    for r in site_results:
        for item in (r.get("newlyAddedUrls") or [])[:TOP_NEW_URLS_IN_REPORT]:
            new_rows.append(
                [
                    r.get("siteId", "-"),
                    item.get("url", "-"),
                    item.get("path", "-"),
                    item.get("slug", "-") or "-",
                    str(item.get("depth", "-")),
                ]
            )
    lines.extend(_md_table(["siteId", "url", "path", "slug", "depth"], new_rows))
    lines.append("")

    lines.append("## 新增路由模式")
    lines.append("")
    pattern_rows = []
    for r in site_results:
        for item in (r.get("newPatterns") or [])[:TOP_NEW_PATTERNS_IN_REPORT]:
            pattern_rows.append(
                [
                    r.get("siteId", "-"),
                    item.get("pattern", "-"),
                    str(item.get("count", 0)),
                    "<br>".join(item.get("exampleUrls") or []),
                ]
            )
    lines.extend(_md_table(["siteId", "pattern", "count", "examples"], pattern_rows))
    lines.append("")

    lines.append("## 新关键词候选")
    lines.append("")
    keyword_rows = []
    for r in site_results:
        for kw in (r.get("topKeywords") or [])[:TOP_KEYWORDS_IN_REPORT]:
            keyword_rows.append(
                [
                    r.get("siteId", "-"),
                    kw.get("type", "-"),
                    kw.get("keyword", "-"),
                    f"{float(kw.get('score', 0.0)):.2f}",
                    str(kw.get("urlCount", 0)),
                    "<br>".join(kw.get("exampleUrls") or []),
                ]
            )
    lines.extend(_md_table(["siteId", "type", "keyword", "score", "urlCount", "examples"], keyword_rows))
    lines.append("")

    lines.append("## 备注")
    lines.append("")
    for remark in REQUIRED_REMARKS:
        lines.append(f"- {remark}")
    lines.append("")

    return "\n".join(lines)


def write_merged_report(*, stamp: str, site_results: List[dict], report_history_root: Path, report_latest_root: Path) -> Tuple[Path, Path]:
    merged_history_dir = report_history_root
    merged_latest_path = report_latest_root / MERGED_LATEST_FILE

    ensure_dir(merged_history_dir)
    ensure_dir(merged_latest_path.parent)

    merged_text = render_merged_report(stamp=stamp, site_results=site_results)
    history_path = merged_history_dir / f"report-{stamp}.md"

    history_path.write_text(merged_text, encoding="utf-8")
    merged_latest_path.write_text(merged_text, encoding="utf-8")

    return history_path, merged_latest_path


def cleanup_legacy_report_layout(*, report_history_root: Path, report_latest_root: Path) -> None:
    legacy_latest_dir = report_latest_root / "latest"
    legacy_latest_merged = legacy_latest_dir / "merged.md"
    latest_path = report_latest_root / MERGED_LATEST_FILE

    if legacy_latest_merged.exists() and not latest_path.exists():
        latest_path.write_text(legacy_latest_merged.read_text(encoding="utf-8"), encoding="utf-8")

    legacy_merged_history = report_history_root / "merged"
    if legacy_merged_history.exists():
        for p in sorted(legacy_merged_history.glob("report-*.md")):
            target = report_history_root / p.name
            if not target.exists():
                shutil.move(str(p), str(target))

    if legacy_latest_dir.exists():
        shutil.rmtree(legacy_latest_dir, ignore_errors=True)
    if legacy_merged_history.exists():
        shutil.rmtree(legacy_merged_history, ignore_errors=True)


def purge_per_site_reports(*, site_ids: Sequence[str], report_history_root: Path, report_latest_root: Path) -> None:
    for site_id in site_ids:
        history_dir = report_history_root / site_id
        latest_path = report_latest_root / f"{site_id}.md"

        if history_dir.exists():
            for p in history_dir.glob("report-*.md"):
                p.unlink(missing_ok=True)
            shutil.rmtree(history_dir, ignore_errors=True)
        latest_path.unlink(missing_ok=True)


def list_snapshot_files(snapshot_dir: Path) -> List[Path]:
    if not snapshot_dir.exists():
        return []
    files = []
    for p in snapshot_dir.iterdir():
        if p.is_file() and SNAPSHOT_RE.match(p.name):
            files.append(p)
    files.sort(key=lambda p: p.name)
    return files


def find_latest_baseline(snapshot_dir: Path, current_stamp: str) -> Tuple[Optional[dict], Optional[Path]]:
    files = list_snapshot_files(snapshot_dir)
    for path in reversed(files):
        m = SNAPSHOT_RE.match(path.name)
        if not m:
            continue
        stamp = m.group(1)
        if stamp >= current_stamp:
            continue
        snapshot = load_json(path)
        return snapshot, path
    return None, None


def build_site_result_from_snapshot(site_id: str, site: Optional[dict], snapshot: Optional[dict]) -> dict:
    display_name = (site or {}).get("displayName") or site_id
    if not snapshot:
        return {
            "siteId": site_id,
            "siteDisplayName": display_name,
            "effectiveUrlCount": 0,
            "patternCount": 0,
            "newlyAddedCount": 0,
            "removedCount": 0,
            "newPatternCount": 0,
            "keywordCount": 0,
            "baselineMode": True,
            "baselineStamp": None,
            "newlyAddedUrls": [],
            "newPatterns": [],
            "topKeywords": [],
        }

    meta = snapshot.get("meta") or {}
    comparison = snapshot.get("comparison") or {}
    keywords = snapshot.get("keywords") or {}

    newly = comparison.get("newlyAddedUrls") or []
    removed = comparison.get("removedUrls") or []
    new_patterns = comparison.get("newPatterns") or []
    top_keywords = keywords.get("topKeywordsFromNewUrls") or []

    return {
        "siteId": site_id,
        "siteDisplayName": display_name,
        "effectiveUrlCount": safe_int(meta.get("effectiveUrlCount")),
        "patternCount": safe_int(meta.get("patternCount")),
        "newlyAddedCount": len(newly),
        "removedCount": len(removed),
        "newPatternCount": len(new_patterns),
        "keywordCount": len(top_keywords),
        "baselineMode": bool(meta.get("baselineMode", False)),
        "baselineStamp": meta.get("baselineStamp"),
        "newlyAddedUrls": newly,
        "newPatterns": new_patterns,
        "topKeywords": top_keywords,
    }


def load_latest_snapshot_for_site(snapshot_root: Path, site_id: str) -> Tuple[Optional[dict], Optional[str]]:
    snapshot_dir = snapshot_root / site_id
    files = list_snapshot_files(snapshot_dir)
    if not files:
        return None, None

    path = files[-1]
    snapshot = load_json(path)
    meta = snapshot.get("meta") or {}
    stamp = meta.get("stamp")
    if not isinstance(stamp, str) or not stamp:
        m = SNAPSHOT_RE.match(path.name)
        stamp = m.group(1) if m else None
    return snapshot, stamp


def run_single_site(
    *,
    site: dict,
    stamp: str,
    data_root: Path,
    snapshot_root: Path,
    report_latest_root: Path,
) -> dict:
    site_id = site["id"]

    site_data_dir = data_root / site_id
    site_snapshot_dir = snapshot_root / site_id
    site_latest_path = report_latest_root / f"{site_id}.md"

    ensure_dir(site_data_dir)
    ensure_dir(site_snapshot_dir)
    ensure_dir(site_latest_path.parent)

    baseline_snapshot, baseline_path = find_latest_baseline(site_snapshot_dir, stamp)
    baseline_mode = baseline_snapshot is None

    raw_urls, crawl_meta = crawl_sitemaps(site)
    rows, normalize_stats = filter_and_normalize_urls(raw_urls, site)
    patterns = infer_patterns(rows)

    if baseline_mode:
        comparison = {
            "newlyAddedUrls": [],
            "removedUrls": [],
            "newPatterns": [],
        }
        keyword_result = {"topKeywordsFromNewUrls": [], "counters": {}}
        baseline_stamp = None
    else:
        baseline_rows = (baseline_snapshot.get("urls") or [])
        baseline_patterns = (baseline_snapshot.get("patterns") or [])

        comparison = build_comparison(rows, baseline_rows, patterns, baseline_patterns)
        keyword_result = extract_keywords(comparison.get("newlyAddedUrls") or [], site.get("keywordRules") or {})
        baseline_stamp = ((baseline_snapshot.get("meta") or {}).get("stamp") if baseline_snapshot else None)

    snapshot = build_snapshot(
        stamp=stamp,
        site=site,
        crawl_meta=crawl_meta,
        normalize_stats=normalize_stats,
        rows=rows,
        patterns=patterns,
        baseline_stamp=baseline_stamp,
        baseline_mode=baseline_mode,
        comparison=comparison,
        keyword_result=keyword_result,
    )

    # 全流程内存完成后再落盘，避免部分失败污染。
    fetch_archive_path = site_data_dir / f"fetch-{stamp}.json"
    snapshot_path = site_snapshot_dir / f"snapshot-{stamp}.json"

    dump_json(
        fetch_archive_path,
        {
            "meta": {
                "generatedAt": datetime.now().isoformat(timespec="seconds"),
                "stamp": stamp,
                "siteId": site_id,
            },
            "crawl": crawl_meta,
            "rawUrls": raw_urls,
        },
    )
    dump_json(snapshot_path, snapshot)

    # 仅输出 merged 报告，不再落盘分站报告。
    site_latest_path.unlink(missing_ok=True)

    return {
        "siteId": site_id,
        "siteDisplayName": site.get("displayName") or site_id,
        "fetchArchive": fetch_archive_path,
        "snapshot": snapshot_path,
        "reportHistory": None,
        "reportLatest": None,
        "effectiveUrlCount": len(rows),
        "patternCount": len(patterns),
        "newlyAddedCount": len(comparison.get("newlyAddedUrls") or []),
        "removedCount": len(comparison.get("removedUrls") or []),
        "newPatternCount": len(comparison.get("newPatterns") or []),
        "keywordCount": len((keyword_result.get("topKeywordsFromNewUrls") or [])),
        "baselineMode": baseline_mode,
        "baselineStamp": baseline_stamp,
        "baselinePath": baseline_path,
        "newlyAddedUrls": comparison.get("newlyAddedUrls") or [],
        "newPatterns": comparison.get("newPatterns") or [],
        "topKeywords": keyword_result.get("topKeywordsFromNewUrls") or [],
    }


def run_pipeline(args: argparse.Namespace) -> int:
    sites_config = Path(args.sites_config).resolve()
    data_root = Path(args.data_root).resolve()
    snapshot_root = Path(args.snapshot_root).resolve()
    report_history_root = Path(args.report_history_root).resolve()
    report_latest_root = Path(args.report_latest_root).resolve()

    ensure_dir(data_root)
    ensure_dir(snapshot_root)
    ensure_dir(report_history_root)
    ensure_dir(report_latest_root)

    cleanup_legacy_report_layout(report_history_root=report_history_root, report_latest_root=report_latest_root)

    sites = load_sites_config(sites_config)

    if args.site:
        if args.site not in sites:
            raise SystemExit(f"未找到 site: {args.site}")
        selected = [sites[args.site]]
    elif args.all_sites:
        selected = [site for site in sites.values()]
    else:
        selected = [site for site in sites.values() if site.get("enabled", True)]

    if not selected:
        raise SystemExit("没有可运行的站点：请检查 sites.json 的 enabled 配置")

    stamp = now_stamp()

    results = []
    for site in selected:
        site_id = site["id"]
        print(f"[run] site={site_id} ...")
        result = run_single_site(
            site=site,
            stamp=stamp,
            data_root=data_root,
            snapshot_root=snapshot_root,
            report_latest_root=report_latest_root,
        )
        results.append(result)

        print(f"[done] site          : {result['siteId']}")
        print(f"[done] fetch archive : {result['fetchArchive']}")
        print(f"[done] snapshot      : {result['snapshot']}")
        print(f"[done] effective urls: {result['effectiveUrlCount']}")
        print(f"[done] newly added   : {result['newlyAddedCount']}")
        print(f"[done] new patterns  : {result['newPatternCount']}")
        print(f"[done] keywords      : {result['keywordCount']}")
        if result["baselineMode"]:
            print("[done] baseline      : none (first run)")
        else:
            print(f"[done] baseline      : {result['baselinePath']}")

    merged_history_path, merged_latest_path = write_merged_report(
        stamp=stamp,
        site_results=results,
        report_history_root=report_history_root,
        report_latest_root=report_latest_root,
    )

    purge_per_site_reports(
        site_ids=[site["id"] for site in selected],
        report_history_root=report_history_root,
        report_latest_root=report_latest_root,
    )

    print(f"[done] merged history: {merged_history_path}")
    print(f"[done] merged latest : {merged_latest_path}")
    print(f"[done] sites total: {len(results)}")
    return 0


def rebuild_single_site_reports(
    *,
    site: Optional[dict],
    site_id: str,
    snapshot_root: Path,
    report_history_root: Path,
    report_latest_root: Path,
) -> None:
    snapshot_dir = snapshot_root / site_id
    history_dir = report_history_root / site_id
    latest_path = report_latest_root / f"{site_id}.md"

    ensure_dir(snapshot_dir)
    ensure_dir(latest_path.parent)

    files = list_snapshot_files(snapshot_dir)
    if not files:
        print(f"[skip] site={site_id} 无快照: {snapshot_dir}")
        # 即使无快照，也清理历史分站报告文件
        if history_dir.exists():
            for p in history_dir.glob("report-*.md"):
                p.unlink(missing_ok=True)
        latest_path.unlink(missing_ok=True)
        return

    baseline_snapshot: Optional[dict] = None

    for path in files:
        snapshot = load_json(path)

        today_rows = snapshot.get("urls") or []
        today_patterns = snapshot.get("patterns") or []

        if baseline_snapshot is None:
            baseline_mode = True
            baseline_stamp = None
            comparison = {
                "newlyAddedUrls": [],
                "removedUrls": [],
                "newPatterns": [],
            }
            keyword_result = {"topKeywordsFromNewUrls": [], "counters": {}}
        else:
            baseline_mode = False
            baseline_stamp = (baseline_snapshot.get("meta") or {}).get("stamp")
            comparison = build_comparison(
                today_rows,
                baseline_snapshot.get("urls") or [],
                today_patterns,
                baseline_snapshot.get("patterns") or [],
            )
            keyword_rules = (site or {}).get("keywordRules") or {}
            keyword_result = extract_keywords(comparison.get("newlyAddedUrls") or [], keyword_rules)

        meta = snapshot.get("meta") or {}
        meta["baselineMode"] = baseline_mode
        meta["baselineStamp"] = baseline_stamp
        snapshot["meta"] = meta
        snapshot["comparison"] = {
            "baselineStamp": baseline_stamp,
            "newlyAddedUrls": comparison.get("newlyAddedUrls") or [],
            "removedUrls": comparison.get("removedUrls") or [],
            "newPatterns": comparison.get("newPatterns") or [],
        }
        snapshot["keywords"] = {
            "topKeywordsFromNewUrls": keyword_result.get("topKeywordsFromNewUrls") or [],
            "counters": keyword_result.get("counters") or {},
        }

        dump_json(path, snapshot)
        baseline_snapshot = snapshot

    # 仅保留 merged 报告，清理分站报告产物
    if history_dir.exists():
        for p in history_dir.glob("report-*.md"):
            p.unlink(missing_ok=True)
    latest_path.unlink(missing_ok=True)


def rebuild_reports(args: argparse.Namespace) -> int:
    sites_config = Path(args.sites_config).resolve()
    snapshot_root = Path(args.snapshot_root).resolve()
    report_history_root = Path(args.report_history_root).resolve()
    report_latest_root = Path(args.report_latest_root).resolve()

    ensure_dir(snapshot_root)
    ensure_dir(report_history_root)
    ensure_dir(report_latest_root)

    cleanup_legacy_report_layout(report_history_root=report_history_root, report_latest_root=report_latest_root)

    sites = load_sites_config(sites_config)

    if args.site:
        if args.site not in sites:
            raise SystemExit(f"未找到 site: {args.site}")
        selected_ids = [args.site]
    else:
        # 重建包含：配置中所有 site + snapshot 目录里已有 site（防止配置调整后历史丢失）。
        selected_ids = sorted(set(list(sites.keys()) + [p.name for p in snapshot_root.iterdir() if p.is_dir()]))

    for site_id in selected_ids:
        site = sites.get(site_id)
        rebuild_single_site_reports(
            site=site,
            site_id=site_id,
            snapshot_root=snapshot_root,
            report_history_root=report_history_root,
            report_latest_root=report_latest_root,
        )

    merged_results: List[dict] = []
    merged_stamps: List[str] = []

    # 合并报告默认覆盖当前配置中的所有站点（无论 enabled），
    # 若某站还没有快照则在合并结果中显示为 0。
    merged_site_ids = sorted(sites.keys())
    for site_id in merged_site_ids:
        site = sites.get(site_id)
        latest_snapshot, stamp = load_latest_snapshot_for_site(snapshot_root, site_id)
        if stamp:
            merged_stamps.append(stamp)
        merged_results.append(build_site_result_from_snapshot(site_id, site, latest_snapshot))

    merged_stamp = max(merged_stamps) if merged_stamps else now_stamp()
    merged_history_path, merged_latest_path = write_merged_report(
        stamp=merged_stamp,
        site_results=merged_results,
        report_history_root=report_history_root,
        report_latest_root=report_latest_root,
    )
    print(f"[done] rebuilt merged history: {merged_history_path}")
    print(f"[done] rebuilt merged latest : {merged_latest_path}")

    return 0


def validate_report(args: argparse.Namespace) -> int:
    report_path = Path(args.report).resolve()

    if not report_path.exists():
        raise SystemExit(f"报告不存在: {report_path}")

    text = report_path.read_text(encoding="utf-8")

    missing = [sec for sec in REQUIRED_SECTIONS if sec not in text]
    missing += [line for line in REQUIRED_REMARKS if line not in text]

    if missing:
        print("[failed] 报告校验失败，缺少内容：")
        for item in missing:
            print(f"- {item}")
        return 1

    print(f"[ok] 报告结构校验通过: {report_path}")
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
