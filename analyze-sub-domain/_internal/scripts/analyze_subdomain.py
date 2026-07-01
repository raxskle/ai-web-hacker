#!/usr/bin/env python3
"""深度分析 monitor 候选子域名并输出建站机会报告。

Usage:
  python3 analyze-sub-domain/_internal/scripts/analyze_subdomain.py run
  python3 analyze-sub-domain/_internal/scripts/analyze_subdomain.py rebuild-reports
  python3 analyze-sub-domain/_internal/scripts/analyze_subdomain.py validate-report --report analyze-sub-domain/reports/latest.md
"""

from __future__ import annotations

import argparse
import html
import importlib.util
import json
import re
import sys
from collections import Counter, deque
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

ANALYSIS_FILE_RE = re.compile(r"^analysis-(?P<date>\d{8})-(?P<hhmm>\d{4})\.json$")
MIN_REPORT_TOP_ITEMS = 12
DEFAULT_MAX_PAGES = 8
DEFAULT_MAX_DEPTH = 2
DEFAULT_TIMEOUT = 4
DEFAULT_FETCH_BYTES = 150_000

SCRIPT_STYLE_RE = re.compile(r"<(script|style)[^>]*>.*?</\1>", re.IGNORECASE | re.DOTALL)
TAG_RE = re.compile(r"<[^>]+>")
HREF_RE = re.compile(r"href=[\"\'](.*?)[\"\']", re.IGNORECASE)
TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.IGNORECASE | re.DOTALL)
DESC_RE = re.compile(
    r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']',
    re.IGNORECASE | re.DOTALL,
)
WORD_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9\-]{2,}")

EN_STOP_WORDS = {
    "the", "and", "for", "with", "from", "that", "this", "your", "you", "our", "are", "was",
    "what", "when", "where", "how", "have", "has", "had", "into", "about", "home", "page",
    "site", "official", "welcome", "best", "new", "all", "get", "more", "use", "using", "via",
    "will", "can", "not", "but", "than", "their", "them", "they", "its", "it's", "just",
}

INTENT_RULES = [
    ("工具型", ["calculator", "converter", "generator", "checker", "tracker", "tool", "editor", "template", "api"]),
    ("信息型", ["guide", "tutorial", "how", "wiki", "learn", "article", "blog", "tips", "what is"]),
    ("商业调研型", ["best", "vs", "compare", "comparison", "review", "top", "alternative"]),
    ("交易型", ["buy", "price", "deal", "discount", "coupon", "order", "shop", "download"]),
    ("导航型", ["login", "official", "dashboard", "console", "portal", "app", "docs", "pricing"]),
]

EXCLUSION_RULES = [
    ("个人博客/作品集", ["portfolio", "resume", "about me", "my work", "personal blog", "dribbble", "behance"]),
    ("产品官网/品牌导航", ["official", "login", "pricing", "dashboard", "console", "platform", "sign in", "webapp", "staging", "nextjs"]),
    ("纯文档站", ["api reference", "changelog", "documentation", "docs", "sdk", "reference", "developer docs"]),
    ("活动落地页", ["conference", "summit", "event", "register", "2026", "2025"]),
    ("本地企业展示站", ["clinic", "restaurant", "hotel", "menu", "reservation", "appointment", "local"]),
]

SECRET_HEX_RE = re.compile(r"(?i)(secret\s*[:=]\s*)([a-f0-9]{16,})")
LONG_HEX_RE = re.compile(r"(?i)\b[a-f0-9]{24,}\b")


class AnalyzeError(Exception):
    pass


def load_monitor_module(project_root: Path):
    script_path = project_root / "monitor-new-sub-domain" / "_internal" / "scripts" / "monitor_new_subdomain.py"
    if not script_path.exists():
        raise AnalyzeError(f"monitor script not found: {script_path}")

    spec = importlib.util.spec_from_file_location("monitor_new_subdomain_shared", script_path)
    if spec is None or spec.loader is None:
        raise AnalyzeError(f"failed to load monitor script: {script_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def parse_args() -> argparse.Namespace:
    project_dir = Path(__file__).resolve().parents[2]
    repo_root = project_dir.parent

    parser = argparse.ArgumentParser(description="深度分析候选子域名并生成建站建议报告")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="执行完整分析流程")
    run_parser.add_argument(
        "--monitor-snapshot-dir",
        default=str(repo_root / "monitor-new-sub-domain" / "_internal" / "snapshots"),
    )
    run_parser.add_argument("--analysis-data-dir", default=str(project_dir / "data" / "history"))
    run_parser.add_argument("--report-dir", default=str(project_dir / "reports" / "history"))
    run_parser.add_argument("--latest-report-path", default=str(project_dir / "reports" / "latest.md"))
    run_parser.add_argument("--max-pages", type=int, default=DEFAULT_MAX_PAGES)
    run_parser.add_argument("--max-depth", type=int, default=DEFAULT_MAX_DEPTH)

    rebuild_parser = subparsers.add_parser("rebuild-reports", help="根据历史分析 JSON 重建报告")
    rebuild_parser.add_argument("--analysis-data-dir", default=str(project_dir / "data" / "history"))
    rebuild_parser.add_argument("--report-dir", default=str(project_dir / "reports" / "history"))
    rebuild_parser.add_argument("--latest-report-path", default=str(project_dir / "reports" / "latest.md"))

    validate_parser = subparsers.add_parser("validate-report", help="校验报告结构")
    validate_parser.add_argument("--report", required=True)

    return parser.parse_args()


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def clean_html_fragment(fragment: str) -> str:
    fragment = SCRIPT_STYLE_RE.sub(" ", fragment)
    fragment = TAG_RE.sub(" ", fragment)
    fragment = html.unescape(fragment)
    fragment = re.sub(r"\s+", " ", fragment).strip()
    return fragment


def fetch_html_page(url: str, timeout: int = DEFAULT_TIMEOUT, max_bytes: int = DEFAULT_FETCH_BYTES) -> dict:
    result = {
        "opened": False,
        "requested_url": url,
        "final_url": "",
        "http_status": 0,
        "error_type": "",
        "error_message": "",
        "html": "",
    }

    req = Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; AnalyzeSubDomain/1.0)",
        },
    )

    try:
        with urlopen(req, timeout=timeout) as resp:
            raw = resp.read(max_bytes)
            charset = resp.headers.get_content_charset() or "utf-8"
            result["opened"] = True
            result["final_url"] = resp.geturl() if hasattr(resp, "geturl") else url
            result["http_status"] = int(getattr(resp, "status", 0) or 0)
            result["html"] = raw.decode(charset, errors="ignore")
    except HTTPError as exc:
        result["error_type"] = "http_error"
        result["error_message"] = str(exc.reason or exc)
        result["http_status"] = int(getattr(exc, "code", 0) or 0)
    except URLError as exc:
        result["error_type"] = "url_error"
        result["error_message"] = str(exc.reason or exc)
    except TimeoutError as exc:
        result["error_type"] = "timeout"
        result["error_message"] = str(exc)
    except Exception as exc:
        result["error_type"] = "fetch_error"
        result["error_message"] = str(exc)

    return result


def extract_page_signals(html_text: str) -> dict:
    title_match = TITLE_RE.search(html_text)
    desc_match = DESC_RE.search(html_text)
    h1_match = H1_RE.search(html_text)

    return {
        "title": clean_html_fragment(title_match.group(1)) if title_match else "",
        "description": clean_html_fragment(desc_match.group(1)) if desc_match else "",
        "h1": clean_html_fragment(h1_match.group(1)) if h1_match else "",
    }


def extract_body_keywords(html_text: str) -> List[str]:
    text = clean_html_fragment(html_text).lower()
    if not text:
        return []

    counter = Counter()
    for token in WORD_RE.findall(text):
        token = token.strip("-_")
        if len(token) < 3:
            continue
        if token in EN_STOP_WORDS:
            continue
        counter[token] += 1

    return [item for item, _ in counter.most_common(30)]


def extract_links(html_text: str, base_url: str, allowed_host: str) -> List[str]:
    links: List[str] = []
    seen: Set[str] = set()

    for href in HREF_RE.findall(html_text):
        if not href:
            continue
        href = href.strip()
        if href.startswith("#") or href.startswith("mailto:") or href.startswith("javascript:"):
            continue

        absolute = urljoin(base_url, href)
        parts = urlsplit(absolute)
        if parts.scheme not in {"http", "https"}:
            continue
        host = (parts.hostname or "").lower().strip(".")
        if host != allowed_host:
            continue

        normalized = f"{parts.scheme}://{host}{parts.path or '/'}"
        if parts.query:
            normalized = f"{normalized}?{parts.query}"

        if normalized in seen:
            continue
        seen.add(normalized)
        links.append(normalized)

    return links


def dedupe_keywords(values: List[str]) -> List[str]:
    seen = set()
    result: List[str] = []
    for value in values:
        if not isinstance(value, str):
            continue
        token = value.strip().lower()
        if not token:
            continue
        if token in seen:
            continue
        seen.add(token)
        result.append(token)
    return result


def sanitize_keyword(value: str) -> str:
    if not isinstance(value, str):
        return ""
    token = value.strip()
    if not token:
        return ""
    token = SECRET_HEX_RE.sub(r"\1[REDACTED]", token)
    token = LONG_HEX_RE.sub("[HEX_REDACTED]", token)
    return token


def sanitize_keyword_list(values: List[str], limit: int) -> List[str]:
    sanitized = [sanitize_keyword(value) for value in values if isinstance(value, str)]
    sanitized = [item for item in sanitized if item]
    return dedupe_keywords(sanitized)[:limit]


def crawl_site(
    host_info: dict,
    monitor,
    max_pages: int,
    max_depth: int,
) -> dict:
    host = host_info.get("host", "")
    seed_url = monitor.normalize_clickable_url(host_info.get("top_url") or host)
    seed_parts = urlsplit(seed_url)
    seed_host = (seed_parts.hostname or "").lower().strip(".")

    if not seed_url or not seed_host:
        return {
            "seed_url": seed_url,
            "pages": [],
            "crawl_error": "invalid_seed",
            "keywords_discovered": [],
            "signals": {"title": "", "description": "", "h1": ""},
        }

    queue = deque([(seed_url, 0)])
    visited: Set[str] = set()
    pages: List[dict] = []
    merged_keywords: List[str] = []

    while queue and len(pages) < max_pages:
        url, depth = queue.popleft()
        if url in visited:
            continue
        visited.add(url)

        fetched = fetch_html_page(url)
        page_item = {
            "url": url,
            "depth": depth,
            "opened": fetched.get("opened", False),
            "http_status": fetched.get("http_status", 0),
            "error_type": fetched.get("error_type", ""),
            "error_message": fetched.get("error_message", ""),
            "signals": {"title": "", "description": "", "h1": ""},
            "keywords": [],
        }

        if fetched.get("opened"):
            html_text = fetched.get("html", "")
            signals = extract_page_signals(html_text)
            signal_keywords = monitor.extract_page_keywords(signals)
            body_keywords = extract_body_keywords(html_text)
            page_keywords = dedupe_keywords(signal_keywords + body_keywords)

            page_item["signals"] = signals
            page_item["keywords"] = page_keywords[:20]
            merged_keywords.extend(page_keywords)

            if depth < max_depth:
                for next_url in extract_links(html_text, fetched.get("final_url") or url, seed_host):
                    if next_url not in visited:
                        queue.append((next_url, depth + 1))

        pages.append(page_item)

    opened_pages = [page for page in pages if page.get("opened")]
    root_signals = opened_pages[0]["signals"] if opened_pages else {"title": "", "description": "", "h1": ""}

    if opened_pages:
        crawl_error = ""
    else:
        first_page = pages[0] if pages else {}
        error_type = first_page.get("error_type") or "crawl_failed"
        error_message = first_page.get("error_message") or ""
        crawl_error = error_type if not error_message else f"{error_type}: {error_message}"

    return {
        "seed_url": seed_url,
        "pages": pages,
        "crawl_error": crawl_error,
        "keywords_discovered": dedupe_keywords(merged_keywords),
        "signals": root_signals,
    }


def collect_history_keyword_freq(data_dir: Path, monitor, current_stamp: str) -> Counter:
    freq = Counter()
    for timed in monitor.list_timed_files(data_dir, ANALYSIS_FILE_RE):
        if timed.stamp >= current_stamp:
            continue
        payload = load_json(timed.path)
        for item in payload.get("candidates", []):
            for kw in item.get("keyword_cluster", []):
                if isinstance(kw, str) and kw.strip():
                    freq[kw.strip().lower()] += 1
    return freq


def classify_intent(keyword_cluster: List[str], text_blob: str) -> dict:
    combined = " ".join(keyword_cluster + [text_blob.lower()])
    best_label = "信息型"
    best_hits: List[str] = []

    for label, words in INTENT_RULES:
        hits = [word for word in words if word in combined]
        if len(hits) > len(best_hits):
            best_label = label
            best_hits = hits

    if best_hits:
        confidence = min(95, 45 + len(best_hits) * 12)
    else:
        confidence = 40

    return {
        "intent_label": best_label,
        "intent_confidence": confidence,
        "intent_evidence": best_hits[:6],
    }


def detect_exclusion(keyword_cluster: List[str], text_blob: str) -> dict:
    combined = " ".join(keyword_cluster + [text_blob.lower()])

    for category, words in EXCLUSION_RULES:
        hits = [word for word in words if word in combined]
        if hits:
            return {
                "excluded": True,
                "exclusion_category": category,
                "exclusion_reason": f"命中 {category} 规则",
                "exclusion_evidence": "、".join(hits[:6]),
            }

    return {
        "excluded": False,
        "exclusion_category": "",
        "exclusion_reason": "",
        "exclusion_evidence": "",
    }


def compute_novelty_score(
    keyword_cluster: List[str],
    clicks_sum: float,
    rise_growth_ratio: float,
    history_freq: Counter,
    intent_label: str,
) -> int:
    if not keyword_cluster:
        return 0

    fresh_count = sum(1 for kw in keyword_cluster if history_freq.get(kw.lower(), 0) == 0)
    fresh_ratio = fresh_count / max(1, len(keyword_cluster))
    fresh_score = fresh_ratio * 40

    rarity_values = [1 / (1 + history_freq.get(kw.lower(), 0)) for kw in keyword_cluster]
    rarity_score = (sum(rarity_values) / max(1, len(rarity_values))) * 25

    clicks_norm = min(1.0, clicks_sum / 5000.0)
    rise_norm = min(1.0, max(0.0, rise_growth_ratio) / 1.5)
    momentum_score = clicks_norm * 20 + rise_norm * 10

    penalty = 0
    if intent_label == "导航型":
        penalty -= 20

    score = int(round(max(0, min(100, fresh_score + rarity_score + momentum_score + penalty))))
    return score


def infer_problem_solution(intent_label: str, primary_keyword: str) -> dict:
    keyword = primary_keyword or "该主题"

    if intent_label == "工具型":
        return {
            "problem_statement": f"用户希望快速完成 {keyword} 相关任务，且不想经过复杂学习流程。",
            "current_solution": "当前站点多以在线工具/生成器方式直接给结果。",
            "build_site_type": "工具站",
            "mvp_pages": ["首页（工具入口）", "核心工具页", "使用指南", "FAQ", "相关模板页"],
            "monetization_path": ["广告", "订阅增值", "模板付费"],
        }

    if intent_label == "商业调研型":
        return {
            "problem_statement": f"用户在 {keyword} 方向做方案对比，缺少结构化决策信息。",
            "current_solution": "现有页面多为单点评测，横向比较不系统。",
            "build_site_type": "评测/对比站",
            "mvp_pages": ["榜单首页", "对比页", "单项深评", "选型指南", "价格与功能库"],
            "monetization_path": ["联盟分佣", "广告", "线索分发"],
        }

    if intent_label == "交易型":
        return {
            "problem_statement": f"用户具有明确交易意图，希望快速找到 {keyword} 的最优方案。",
            "current_solution": "当前多为导购或品牌落地页，信息分散。",
            "build_site_type": "导购/聚合站",
            "mvp_pages": ["首页", "价格聚合页", "优惠页", "品牌对比页", "常见问题"],
            "monetization_path": ["联盟分佣", "商家合作", "广告"],
        }

    if intent_label == "导航型":
        return {
            "problem_statement": f"用户主要在寻找 {keyword} 的官方入口，信息增量空间有限。",
            "current_solution": "官方站/导航词已占据主要需求。",
            "build_site_type": "不建议建站",
            "mvp_pages": ["N/A"],
            "monetization_path": ["N/A"],
        }

    return {
        "problem_statement": f"用户希望理解并解决 {keyword} 相关问题，需要清晰、可执行的信息。",
        "current_solution": "当前站点以教程/文章形式提供答案，但系统性不足。",
        "build_site_type": "内容站",
        "mvp_pages": ["主题总览", "核心教程", "常见问题", "模板/清单页", "更新日志"],
        "monetization_path": ["广告", "联盟", "数字产品"],
    }


def compute_track_score(
    clicks_sum: float,
    rise_growth_ratio: float,
    intent_label: str,
    excluded: bool,
    novelty_score: int,
) -> Tuple[int, str]:
    demand_score = min(30.0, (clicks_sum / 5000.0) * 30.0)
    growth_score = min(25.0, max(0.0, rise_growth_ratio) * 20.0 + 5.0)

    intent_value_map = {
        "工具型": 20,
        "信息型": 16,
        "商业调研型": 17,
        "交易型": 15,
        "导航型": 6,
    }
    intent_score = float(intent_value_map.get(intent_label, 12))

    replicability_score = 0.0 if excluded else 15.0
    monetize_map = {
        "工具型": 9,
        "信息型": 7,
        "商业调研型": 8,
        "交易型": 10,
        "导航型": 3,
    }
    monetization_score = float(monetize_map.get(intent_label, 6))

    total = demand_score + growth_score + intent_score + replicability_score + monetization_score
    total += min(8.0, novelty_score * 0.08)
    total = max(0.0, min(100.0, total))
    score = int(round(total))

    if score >= 80:
        grade = "A"
    elif score >= 65:
        grade = "B"
    elif score >= 50:
        grade = "C"
    else:
        grade = "D"

    return score, grade


def recommend_action(track_grade: str, excluded: bool) -> str:
    if excluded:
        return "排除：不作为建站关键词"
    if track_grade == "A":
        return "立即立项：1周内完成 MVP 验证"
    if track_grade == "B":
        return "进入候选池：先做低成本落地页测试"
    if track_grade == "C":
        return "继续观察：跟踪 1-2 周趋势后再决策"
    return "暂不投入：记录并等待新信号"


def build_candidate_analysis(
    host_info: dict,
    source_type: str,
    crawl: dict,
    history_freq: Counter,
    monitor,
) -> dict:
    similarweb_keywords_raw = [
        item.strip().lower()
        for item in (host_info.get("keywords") or [])
        if isinstance(item, str) and item.strip()
    ]
    if not similarweb_keywords_raw:
        top_kw = (host_info.get("top_keyword") or "").strip().lower()
        if top_kw:
            similarweb_keywords_raw = [top_kw]

    similarweb_keywords = sanitize_keyword_list(similarweb_keywords_raw, 15)
    discovered_keywords = sanitize_keyword_list(crawl.get("keywords_discovered", []), 20)
    keyword_cluster = sanitize_keyword_list(similarweb_keywords + discovered_keywords, 12)

    root_signals = crawl.get("signals", {}) if isinstance(crawl.get("signals"), dict) else {}
    text_blob = " ".join(
        [
            root_signals.get("title", "") or "",
            root_signals.get("description", "") or "",
            root_signals.get("h1", "") or "",
            host_info.get("host", "") or "",
            host_info.get("top_url", "") or "",
            crawl.get("seed_url", "") or "",
            " ".join(keyword_cluster),
        ]
    )

    intent = classify_intent(keyword_cluster, text_blob)
    exclusion = detect_exclusion(keyword_cluster, text_blob)

    clicks_sum = monitor.safe_float(host_info.get("clicks_sum"))
    rise_growth_ratio = monitor.safe_float(host_info.get("rise_growth_ratio"))
    novelty_score = compute_novelty_score(
        keyword_cluster=keyword_cluster,
        clicks_sum=clicks_sum,
        rise_growth_ratio=rise_growth_ratio,
        history_freq=history_freq,
        intent_label=intent["intent_label"],
    )

    problem_solution = infer_problem_solution(intent["intent_label"], keyword_cluster[0] if keyword_cluster else "")

    page_items = crawl.get("pages", [])
    opened_count = len([item for item in page_items if item.get("opened")])

    if opened_count == 0:
        exclusion.update(
            {
                "excluded": True,
                "exclusion_category": "抓取失败",
                "exclusion_reason": "无法获得页面信号，避免无依据判定",
                "exclusion_evidence": crawl.get("crawl_error", "crawl_failed"),
            }
        )

    track_score, track_grade = compute_track_score(
        clicks_sum=clicks_sum,
        rise_growth_ratio=rise_growth_ratio,
        intent_label=intent["intent_label"],
        excluded=exclusion["excluded"],
        novelty_score=novelty_score,
    )
    recommendation_action = recommend_action(track_grade, exclusion["excluded"])

    return {
        "host": host_info.get("host", ""),
        "source_type": source_type,
        "clicks_sum": round(clicks_sum, 4),
        "trend_status": monitor.classify_trend_status(host_info.get("trend_13w_sum") or {}),
        "rise_window": (
            f"{monitor.short_date(host_info.get('rise_window_start'))}~{monitor.short_date(host_info.get('rise_window_end'))}"
            if host_info.get("rise_window_start") and host_info.get("rise_window_end")
            else "-"
        ),
        "rise_growth_ratio": round(rise_growth_ratio, 6),
        "seed_url": crawl.get("seed_url", ""),
        "pages_crawled": len(page_items),
        "pages_opened": opened_count,
        "keywords_similarweb": similarweb_keywords[:15],
        "keywords_discovered": discovered_keywords[:20],
        "keyword_cluster": keyword_cluster,
        "intent_label": intent["intent_label"],
        "intent_confidence": intent["intent_confidence"],
        "intent_evidence": intent["intent_evidence"],
        "novelty_score": novelty_score,
        "problem_statement": problem_solution["problem_statement"],
        "current_solution": problem_solution["current_solution"],
        "build_site_type": problem_solution["build_site_type"],
        "mvp_pages": problem_solution["mvp_pages"],
        "monetization_path": problem_solution["monetization_path"],
        "track_score": track_score,
        "track_grade": track_grade,
        "recommendation_action": recommendation_action,
        "excluded": exclusion["excluded"],
        "exclusion_category": exclusion["exclusion_category"],
        "exclusion_reason": exclusion["exclusion_reason"],
        "exclusion_evidence": exclusion["exclusion_evidence"],
        "page_signals": {
            "title": root_signals.get("title", "") or "",
            "h1": root_signals.get("h1", "") or "",
        },
    }


def render_markdown_report(analysis: dict, monitor) -> str:
    stamp = analysis.get("meta", {}).get("sourceStamp", "-")
    candidates = analysis.get("candidates", [])
    included = [item for item in candidates if not item.get("excluded")]
    excluded = [item for item in candidates if item.get("excluded")]

    included_sorted = sorted(included, key=lambda item: (-monitor.safe_float(item.get("track_score")), -monitor.safe_float(item.get("novelty_score")), item.get("host", "")))
    top_items = included_sorted[:MIN_REPORT_TOP_ITEMS]

    grade_counts = Counter(item.get("track_grade", "D") for item in included)

    lines: List[str] = []
    lines.append(f"# 子域名建站机会分析报告（{stamp}）")
    lines.append("")
    lines.append("## 执行摘要")
    lines.append("")
    lines.append(f"- 候选总数：**{len(candidates)}**")
    lines.append(f"- 通过筛选：**{len(included)}**")
    lines.append(f"- 排除数量：**{len(excluded)}**")
    lines.append(f"- 赛道等级分布：A={grade_counts.get('A', 0)} / B={grade_counts.get('B', 0)} / C={grade_counts.get('C', 0)} / D={grade_counts.get('D', 0)}")
    lines.append(f"- 数据来源：`{analysis.get('meta', {}).get('monitorSnapshotPath', '-')}`")
    lines.append("")

    lines.append("## Top 建站机会")
    lines.append("")
    if not top_items:
        lines.append("当前无可直接推荐的建站机会。")
        lines.append("")
    else:
        for idx, item in enumerate(top_items, start=1):
            host = monitor.escape_md_cell(item.get("host", ""))
            primary_kw = item.get("keyword_cluster", [])[:5]
            kw_text = monitor.join_keywords(primary_kw)
            lines.append(f"{idx}. {host}")
            lines.append(f"   - 关键词簇：{monitor.escape_md_cell(kw_text)}")
            lines.append(f"   - 新词分：**{item.get('novelty_score', 0)}**")
            lines.append(f"   - 搜索意图：**{item.get('intent_label', '-') }**（置信度 {item.get('intent_confidence', 0)}）")
            lines.append(f"   - 用户问题：{monitor.escape_md_cell(item.get('problem_statement', '-'))}")
            lines.append(f"   - 当前解法：{monitor.escape_md_cell(item.get('current_solution', '-'))}")
            lines.append(f"   - 赛道分：**{item.get('track_score', 0)} ({item.get('track_grade', 'D')})**")
            lines.append(f"   - 建议站型：{monitor.escape_md_cell(item.get('build_site_type', '-'))}")
            lines.append(f"   - MVP 页面建议：{monitor.escape_md_cell(monitor.join_keywords(item.get('mvp_pages', [])))}")
            lines.append(f"   - 变现路径：{monitor.escape_md_cell(monitor.join_keywords(item.get('monetization_path', [])))}")
            lines.append(f"   - 建议动作：**{monitor.escape_md_cell(item.get('recommendation_action', '-'))}**")
            lines.append("")

    lines.append("## 候选清单总览")
    lines.append("")
    lines.append("| # | host | 来源 | 点击量 | 新词分 | 意图 | 赛道分 | 等级 | 建议动作 |")
    lines.append("|---|---|---:|---:|---:|---|---:|---:|---|")
    for idx, item in enumerate(included_sorted, start=1):
        lines.append(
            "| {idx} | {host} | {source} | {clicks} | {novel} | {intent} | {score} | {grade} | {action} |".format(
                idx=idx,
                host=monitor.escape_md_cell(item.get("host", "-")),
                source=monitor.escape_md_cell(item.get("source_type", "-")),
                clicks=monitor.to_clicks_str(item.get("clicks_sum")),
                novel=item.get("novelty_score", 0),
                intent=monitor.escape_md_cell(item.get("intent_label", "-")),
                score=item.get("track_score", 0),
                grade=monitor.escape_md_cell(item.get("track_grade", "D")),
                action=monitor.escape_md_cell(item.get("recommendation_action", "-")),
            )
        )
    lines.append("")

    lines.append("## 排除清单（不适合建站）")
    lines.append("")
    if not excluded:
        lines.append("本次无排除项。")
        lines.append("")
    else:
        excluded_sorted = sorted(excluded, key=lambda item: (-monitor.safe_float(item.get("clicks_sum")), item.get("host", "")))
        for idx, item in enumerate(excluded_sorted, start=1):
            lines.append(f"{idx}. {monitor.escape_md_cell(item.get('host', '-'))}")
            lines.append(f"   - 排除类别：{monitor.escape_md_cell(item.get('exclusion_category', '-'))}")
            lines.append(f"   - 排除原因：{monitor.escape_md_cell(item.get('exclusion_reason', '-'))}")
            lines.append(f"   - 命中证据：{monitor.escape_md_cell(item.get('exclusion_evidence', '-'))}")
            lines.append("")

    lines.append("## 附录")
    lines.append("")
    lines.append("- 评分规则版本：`v0.1`")
    lines.append("- 新词分口径：新鲜度 + 稀有度 + 动量 - 导航惩罚")
    lines.append("- 赛道分口径：需求强度 + 增长质量 + 意图价值 + 可复制性 + 变现潜力")
    lines.append("- 过滤口径：个人博客/作品集、产品官网/品牌导航、纯文档站、活动落地页、本地企业展示站")

    return "\n".join(lines)


def analyze_run(args: argparse.Namespace) -> int:
    project_dir = Path(__file__).resolve().parents[2]
    repo_root = project_dir.parent
    monitor = load_monitor_module(repo_root)

    monitor_snapshot_dir = Path(args.monitor_snapshot_dir).resolve()
    analysis_data_dir = Path(args.analysis_data_dir).resolve()
    report_dir = Path(args.report_dir).resolve()
    latest_report_path = Path(args.latest_report_path).resolve()

    ensure_dir(analysis_data_dir)
    ensure_dir(report_dir)
    ensure_dir(latest_report_path.parent)

    snapshots = monitor.list_timed_files(monitor_snapshot_dir, monitor.SNAPSHOT_FILE_RE)
    if not snapshots:
        raise SystemExit(f"No monitor snapshots found in {monitor_snapshot_dir}")

    current = snapshots[-1]
    current_snapshot = load_json(current.path)

    previous_snapshot = load_json(snapshots[-2].path) if len(snapshots) >= 2 else None

    new_hosts = monitor.collect_new_hosts(current_snapshot, previous_snapshot)
    new_host_set = {
        item.get("host")
        for item in new_hosts
        if isinstance(item, dict) and isinstance(item.get("host"), str)
    }
    rising_hosts = monitor.collect_rising_hosts(
        current_snapshot=current_snapshot,
        previous_snapshot=previous_snapshot,
        exclude_hosts=new_host_set,
    )

    targets: List[Tuple[str, dict]] = []
    seen_hosts = set()
    for source_type, items in [("新增", new_hosts), ("持续上涨", rising_hosts)]:
        for item in items:
            host = item.get("host") if isinstance(item, dict) else ""
            if not isinstance(host, str) or not host or host in seen_hosts:
                continue
            seen_hosts.add(host)
            targets.append((source_type, item))

    history_freq = collect_history_keyword_freq(analysis_data_dir, monitor, current.stamp)

    candidates = []
    for source_type, host_info in targets:
        crawl = crawl_site(
            host_info=host_info,
            monitor=monitor,
            max_pages=max(1, args.max_pages),
            max_depth=max(0, args.max_depth),
        )
        item = build_candidate_analysis(
            host_info=host_info,
            source_type=source_type,
            crawl=crawl,
            history_freq=history_freq,
            monitor=monitor,
        )
        candidates.append(item)

    analysis_payload = {
        "meta": {
            "generatedAt": datetime.now().isoformat(timespec="seconds"),
            "sourceStamp": current.stamp,
            "monitorSnapshotPath": str(current.path),
            "monitorPreviousSnapshotPath": str(snapshots[-2].path) if len(snapshots) >= 2 else "",
            "rulesVersion": "v0.1",
            "targets": len(targets),
            "maxPages": args.max_pages,
            "maxDepth": args.max_depth,
        },
        "summary": {
            "totalCandidates": len(candidates),
            "excluded": len([item for item in candidates if item.get("excluded")]),
            "included": len([item for item in candidates if not item.get("excluded")]),
        },
        "candidates": candidates,
    }

    analysis_path = analysis_data_dir / f"analysis-{current.stamp}.json"
    dump_json(analysis_path, analysis_payload)

    report_content = render_markdown_report(analysis_payload, monitor)
    report_path = report_dir / f"analyze-report-{current.stamp}.md"
    report_path.write_text(report_content, encoding="utf-8")
    latest_report_path.write_text(report_content, encoding="utf-8")

    print(f"[done] monitor snapshot  : {current.path}")
    print(f"[done] analysis json     : {analysis_path}")
    print(f"[done] report history    : {report_path}")
    print(f"[done] report latest     : {latest_report_path}")
    print(f"[done] candidates total  : {len(candidates)}")
    print(f"[done] candidates include: {analysis_payload['summary']['included']}")
    print(f"[done] candidates exclude: {analysis_payload['summary']['excluded']}")

    return 0


def rebuild_reports(args: argparse.Namespace) -> int:
    project_dir = Path(__file__).resolve().parents[2]
    repo_root = project_dir.parent
    monitor = load_monitor_module(repo_root)

    analysis_data_dir = Path(args.analysis_data_dir).resolve()
    report_dir = Path(args.report_dir).resolve()
    latest_report_path = Path(args.latest_report_path).resolve()

    ensure_dir(analysis_data_dir)
    ensure_dir(report_dir)
    ensure_dir(latest_report_path.parent)

    files = monitor.list_timed_files(analysis_data_dir, ANALYSIS_FILE_RE)
    if not files:
        raise SystemExit(f"No analysis files found in {analysis_data_dir}")

    latest_content = ""
    latest_stamp = ""
    for timed in files:
        payload = load_json(timed.path)
        content = render_markdown_report(payload, monitor)
        report_path = report_dir / f"analyze-report-{timed.stamp}.md"
        report_path.write_text(content, encoding="utf-8")
        latest_content = content
        latest_stamp = timed.stamp
        print(f"[done] rebuilt report    : {report_path}")

    latest_report_path.write_text(latest_content, encoding="utf-8")
    print(f"[done] latest updated    : {latest_report_path} (stamp={latest_stamp})")
    return 0


def validate_report(args: argparse.Namespace) -> int:
    report_path = Path(args.report).resolve()
    if not report_path.exists():
        raise SystemExit(f"Report not found: {report_path}")

    content = report_path.read_text(encoding="utf-8")
    required_sections = [
        "## 执行摘要",
        "## Top 建站机会",
        "## 候选清单总览",
        "## 排除清单（不适合建站）",
        "## 附录",
    ]

    missing = [section for section in required_sections if section not in content]
    if missing:
        raise SystemExit("Report validation failed, missing sections: " + ", ".join(missing))

    required_fields = ["建议动作", "关键词簇", "赛道分", "排除类别"]
    missing_fields = [field for field in required_fields if field not in content]
    if missing_fields:
        raise SystemExit("Report validation failed, missing fields: " + ", ".join(missing_fields))

    print(f"[done] report valid: {report_path}")
    return 0


def main() -> int:
    args = parse_args()
    if args.command == "run":
        return analyze_run(args)
    if args.command == "rebuild-reports":
        return rebuild_reports(args)
    if args.command == "validate-report":
        return validate_report(args)
    raise SystemExit(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    raise SystemExit(main())
