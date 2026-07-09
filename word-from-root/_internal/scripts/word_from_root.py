#!/usr/bin/env python3
"""按词根抓取 SIM / SEM 关键词并导出 Excel。

Usage:
  python3 word-from-root/_internal/scripts/word_from_root.py run --keyword "image to text"
  python3 word-from-root/_internal/scripts/word_from_root.py rebuild-reports
  python3 word-from-root/_internal/scripts/word_from_root.py validate-report
"""

from __future__ import annotations

import argparse
import json
import math
import re
from datetime import datetime
from pathlib import Path
from shutil import copyfile
from typing import Dict, Iterable, List, Optional, Sequence, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

PROJECT_DIR = Path(__file__).resolve().parents[2]
LOCAL_SERVICE_TOKEN_PATH = PROJECT_DIR / "local-service" / "bridge_token.txt"
LOCAL_SERVICE_GMITM_PATH = PROJECT_DIR / "local-service" / "__gmitm.txt"
LEGACY_LOCAL_SERVICE_GMITM_PATH = PROJECT_DIR / "local-service" / "gmitm.txt"

DEFAULT_API_BASE = "http://127.0.0.1:17311"
SIM_ENDPOINT = "/sim/api/KeywordGenerator/google/suggest"
SEM_KEYWORDS_ENDPOINT = "/sem/kmtgw/v2/webapi/ideas.GetKeywords"
SEM_SUMMARY_ENDPOINT = "/sem/kmtgw/v2/webapi/ideas.GetKeywordsSummary"

SIM_RANGE_FILTER = "cpc,0.1,|difficulty,1,80"
SIM_SORT = "windowVolume"
SIM_TYPE = "Broad"
SIM_WEBSOURCE = "Total"
SIM_ROWS_PER_PAGE = 100
SIM_MAX_KEYWORDS = 300

SEM_PAGE_SIZE = 100
SEM_MAX_KEYWORDS = 300
SEM_DATABASE = "us"
SEM_CURRENCY = "USD"

REQUEST_TIMEOUT_SECONDS = 180
SNAPSHOT_RE = re.compile(r"^snapshot-(\d{8}-\d{6})\.json$")
SPACE_RE = re.compile(r"\s+")
TOP_PREVIEW_ROWS = 30

REQUIRED_SECTIONS = [
    "## 摘要",
    "## 抓取概览",
    "## 合并结果概览",
    "## Top 关键词预览",
    "## 产物路径",
    "## 备注",
]

REQUIRED_REMARKS = [
    "Excel 是完整结果，Markdown 仅做预览",
    "排序值仅基于 SEM 的 volume * cpc / kd",
    "sim_only 关键词由于缺少完整 SEM 指标，score 可能为空",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="按词根抓取 SIM/SEM 关键词并导出 Excel")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="抓取关键词 + 合并 + 快照 + 报告 + Excel")
    run_parser.add_argument("--keyword", required=True, help="词根，例如 'image to text'")
    run_parser.add_argument("--api-base", default=DEFAULT_API_BASE)
    run_parser.add_argument("--token-path", default=str(LOCAL_SERVICE_TOKEN_PATH))
    run_parser.add_argument("--gmitm-path", default=str(LOCAL_SERVICE_GMITM_PATH))

    run_parser.add_argument("--country", default="999")
    run_parser.add_argument("--latest", default="28d")
    run_parser.add_argument("--sim-rows-per-page", type=int, default=SIM_ROWS_PER_PAGE)
    run_parser.add_argument("--sim-max-keywords", type=int, default=SIM_MAX_KEYWORDS)
    run_parser.add_argument("--database", default=SEM_DATABASE)
    run_parser.add_argument("--currency", default=SEM_CURRENCY)
    run_parser.add_argument("--sem-page-size", type=int, default=SEM_PAGE_SIZE)
    run_parser.add_argument("--sem-max-keywords", type=int, default=SEM_MAX_KEYWORDS)

    run_parser.add_argument("--data-dir", default=str(PROJECT_DIR / "data"))
    run_parser.add_argument("--snapshot-dir", default=str(PROJECT_DIR / "_internal" / "snapshots"))
    run_parser.add_argument("--report-dir", default=str(PROJECT_DIR / "report" / "history"))
    run_parser.add_argument("--latest-report-path", default=str(PROJECT_DIR / "report" / "latest.md"))
    run_parser.add_argument("--latest-xlsx-path", default=str(PROJECT_DIR / "report" / "latest.xlsx"))

    rebuild_parser = subparsers.add_parser("rebuild-reports", help="根据快照重建 Markdown 和 Excel")
    rebuild_parser.add_argument("--snapshot-dir", default=str(PROJECT_DIR / "_internal" / "snapshots"))
    rebuild_parser.add_argument("--report-dir", default=str(PROJECT_DIR / "report" / "history"))
    rebuild_parser.add_argument("--latest-report-path", default=str(PROJECT_DIR / "report" / "latest.md"))
    rebuild_parser.add_argument("--latest-xlsx-path", default=str(PROJECT_DIR / "report" / "latest.xlsx"))

    validate_parser = subparsers.add_parser("validate-report", help="校验 Markdown 报告结构与 latest.xlsx")
    validate_parser.add_argument("--report", default=str(PROJECT_DIR / "report" / "latest.md"))
    validate_parser.add_argument("--xlsx", default=str(PROJECT_DIR / "report" / "latest.xlsx"))

    return parser.parse_args()


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def safe_float(value) -> float:
    try:
        if value is None or value == "":
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def safe_int(value) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def to_int_if_possible(v: float) -> str:
    if v is None:
        return "-"
    if abs(v - round(v)) < 1e-9:
        return str(int(round(v)))
    return f"{v:.2f}"


def to_display_number(value) -> str:
    if value in (None, ""):
        return "-"
    return to_int_if_possible(safe_float(value))


def read_text_required(path: Path, label: str) -> str:
    if not path.exists():
        raise RuntimeError(f"{label} 不存在: {path}")
    value = path.read_text(encoding="utf-8").strip()
    if not value:
        raise RuntimeError(f"{label} 为空: {path}")
    return value


def read_gmitm(path: Path) -> str:
    if path.exists():
        return read_text_required(path, "gmitm 文件")
    if path.name == "gmitm.txt" and LEGACY_LOCAL_SERVICE_GMITM_PATH.exists():
        return read_text_required(LEGACY_LOCAL_SERVICE_GMITM_PATH, "gmitm 文件")
    raise RuntimeError(
        f"gmitm 文件不存在: {path}。请在 word-from-root/local-service/__gmitm.txt 中写入当前会话的 __gmitm 值。"
    )


def normalize_keyword_text(text: str) -> str:
    return SPACE_RE.sub(" ", str(text or "").strip().lower())


def list_snapshot_files(snapshot_dir: Path) -> List[Path]:
    if not snapshot_dir.exists():
        return []
    files = []
    for path in snapshot_dir.iterdir():
        if path.is_file() and SNAPSHOT_RE.match(path.name):
            files.append(path)
    files.sort(key=lambda p: p.name)
    return files


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


def post_local_service(*, api_url: str, headers: dict, payload: dict, expect_jsonrpc: bool = False) -> dict:
    try:
        status_code, raw_body = _post_json(
            api_url,
            headers=headers,
            payload=payload,
            timeout_seconds=REQUEST_TIMEOUT_SECONDS,
        )
    except URLError as exc:
        raise RuntimeError(f"请求本地服务失败: {exc}") from exc

    try:
        wrapper = json.loads(raw_body)
    except json.JSONDecodeError as exc:
        raise RuntimeError("本地服务返回非 JSON") from exc

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

    try:
        upstream = json.loads(upstream_body_raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError("上游 body 非合法 JSON") from exc

    if expect_jsonrpc and not isinstance(upstream, dict):
        raise RuntimeError("上游 JSON-RPC 响应不是对象")

    return {
        "wrapper": wrapper,
        "upstream": upstream,
        "status": upstream_status,
    }


def build_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def sim_request_payload(args: argparse.Namespace, page: int) -> dict:
    return {
        "keyword": args.keyword,
        "country": args.country,
        "latest": args.latest,
        "isWindow": True,
        "websource": SIM_WEBSOURCE,
        "webSource": SIM_WEBSOURCE,
        "sort": SIM_SORT,
        "asc": False,
        "rangeFilter": SIM_RANGE_FILTER,
        "rowsPerPage": args.sim_rows_per_page,
        "type": SIM_TYPE,
        "page": page,
    }


def build_sem_filter() -> dict:
    return {
        "phrase": [],
        "competition_level": [],
        "cpc": [
            {
                "inverted": False,
                "operation": 5,
                "value": 0.1,
            }
        ],
        "difficulty": [
            {
                "inverted": False,
                "operation": 4,
                "value": 90,
            }
        ],
        "results": [],
        "serp_features": [
            {
                "inverted": False,
                "value": [],
            }
        ],
        "volume": [],
        "words_count": [],
        "phrase_include_logic": 0,
    }


def sem_request_body(args: argparse.Namespace, method: str, page_number: Optional[int] = None) -> dict:
    params = {
        "mode": 0,
        "currency": args.currency,
        "database": args.database,
        "filter": build_sem_filter(),
        "groups": [],
        "order": {
            "direction": 1,
            "field": "volume",
        },
        "groups_order": {
            "direction": 1,
            "field": "count",
        },
        "phrase": args.keyword,
        "questions_only": False,
    }
    if page_number is not None:
        params["page"] = {
            "number": page_number,
            "size": args.sem_page_size,
        }

    request_id = 15 if method == "ideas.GetKeywordsSummary" else 14 + int(page_number or 0)
    return {
        "id": request_id,
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
    }


def fetch_sim_keywords(args: argparse.Namespace, headers: dict) -> Tuple[List[dict], dict]:
    api_url = args.api_base.rstrip("/") + SIM_ENDPOINT
    first_page = post_local_service(
        api_url=api_url,
        headers=headers,
        payload=sim_request_payload(args, page=1),
    )
    upstream = first_page["upstream"]
    records = upstream.get("records")
    if not isinstance(records, list):
        raise RuntimeError("SIM 响应 records 非数组")

    total_records = safe_int(upstream.get("totalRecords"))
    effective_total = min(total_records, args.sim_max_keywords)
    total_pages = max(1, math.ceil(effective_total / max(args.sim_rows_per_page, 1)))

    page_results = [
        {
            "page": 1,
            "requestPayload": sim_request_payload(args, page=1),
            "wrapper": first_page["wrapper"],
            "upstream": upstream,
            "rowsCount": len(records),
        }
    ]

    for page in range(2, total_pages + 1):
        result = post_local_service(
            api_url=api_url,
            headers=headers,
            payload=sim_request_payload(args, page=page),
        )
        page_upstream = result["upstream"]
        page_records = page_upstream.get("records")
        if not isinstance(page_records, list):
            raise RuntimeError(f"SIM 第 {page} 页 records 非数组")
        page_results.append(
            {
                "page": page,
                "requestPayload": sim_request_payload(args, page=page),
                "wrapper": result["wrapper"],
                "upstream": page_upstream,
                "rowsCount": len(page_records),
            }
        )

    normalized = normalize_sim_records(page_results, args.sim_max_keywords)
    meta = {
        "apiUrl": api_url,
        "totalRecords": total_records,
        "effectiveTotal": effective_total,
        "rowsPerPage": args.sim_rows_per_page,
        "pagesFetched": len(page_results),
        "pagesRequested": [item["page"] for item in page_results],
        "rangeFilter": SIM_RANGE_FILTER,
        "sort": SIM_SORT,
    }
    return normalized, {
        "meta": meta,
        "pages": page_results,
    }


def normalize_sim_records(page_results: List[dict], max_keywords: int) -> List[dict]:
    normalized: List[dict] = []
    seen: set[str] = set()

    for page_result in page_results:
        page_num = safe_int(page_result.get("page"))
        records = (page_result.get("upstream") or {}).get("records") or []
        for idx, item in enumerate(records, start=1):
            if not isinstance(item, dict):
                continue
            keyword = str(item.get("keyword") or "").strip()
            if not keyword:
                continue
            normalized_key = normalize_keyword_text(keyword)
            if normalized_key in seen:
                continue
            seen.add(normalized_key)
            normalized.append(
                {
                    "keyword": keyword,
                    "keywordNormalized": normalized_key,
                    "simKeyword": keyword,
                    "simWindowVolume": safe_float(item.get("windowVolume")),
                    "simAverageVolume": safe_float(item.get("averageVolume")),
                    "simCpc": safe_float(item.get("cpc")),
                    "simKd": safe_float(item.get("difficulty")),
                    "simRank": len(normalized) + 1,
                    "simPage": page_num,
                    "simRankInPage": idx,
                }
            )
            if len(normalized) >= max_keywords:
                return normalized

    return normalized


def fetch_sem_keywords(args: argparse.Namespace, headers: dict, gmitm: str) -> Tuple[List[dict], dict]:
    summary_url = args.api_base.rstrip("/") + SEM_SUMMARY_ENDPOINT
    keywords_url = args.api_base.rstrip("/") + SEM_KEYWORDS_ENDPOINT

    summary_payload = {
        "__gmitm": gmitm,
        "requestBody": sem_request_body(args, "ideas.GetKeywordsSummary"),
    }
    summary_result = post_local_service(
        api_url=summary_url,
        headers=headers,
        payload=summary_payload,
        expect_jsonrpc=True,
    )
    summary_upstream = summary_result["upstream"]
    summary_data = (summary_upstream.get("result") or {}) if isinstance(summary_upstream, dict) else {}
    total = safe_int(summary_data.get("total"))
    effective_total = min(total, args.sem_max_keywords)
    total_pages = max(1, math.ceil(effective_total / max(args.sem_page_size, 1))) if effective_total else 1

    page_results: List[dict] = []
    normalized: List[dict] = []
    seen: set[str] = set()

    for page in range(1, total_pages + 1):
        page_request_body = sem_request_body(args, "ideas.GetKeywords", page_number=page)
        page_payload = {
            "__gmitm": gmitm,
            "requestBody": page_request_body,
        }
        page_result = post_local_service(
            api_url=keywords_url,
            headers=headers,
            payload=page_payload,
            expect_jsonrpc=True,
        )
        page_upstream = page_result["upstream"]
        keywords = (((page_upstream.get("result") or {}) if isinstance(page_upstream, dict) else {}).get("keywords") or [])
        if not isinstance(keywords, list):
            raise RuntimeError(f"SEM 第 {page} 页 keywords 非数组")

        page_results.append(
            {
                "page": page,
                "requestPayload": page_payload,
                "wrapper": page_result["wrapper"],
                "upstream": page_upstream,
                "rowsCount": len(keywords),
            }
        )

        for idx, item in enumerate(keywords, start=1):
            if not isinstance(item, dict):
                continue
            keyword = str(item.get("phrase") or "").strip()
            if not keyword:
                continue
            normalized_key = normalize_keyword_text(keyword)
            if normalized_key in seen:
                continue
            seen.add(normalized_key)
            normalized.append(
                {
                    "keyword": keyword,
                    "keywordNormalized": normalized_key,
                    "semKeyword": keyword,
                    "semVolume": safe_float(item.get("volume")),
                    "semCpc": safe_float(item.get("cpc")),
                    "semKd": safe_float(item.get("difficulty")),
                    "semCompetitionLevel": safe_float(item.get("competition_level")),
                    "semResults": safe_int(item.get("results")),
                    "semSnapshotDate": str(item.get("snapshot_date") or ""),
                    "semTrend": item.get("trend") if isinstance(item.get("trend"), list) else [],
                    "semRank": len(normalized) + 1,
                    "semPage": page,
                    "semRankInPage": idx,
                }
            )
            if len(normalized) >= args.sem_max_keywords:
                break
        if len(normalized) >= args.sem_max_keywords:
            break

    meta = {
        "summaryApiUrl": summary_url,
        "keywordsApiUrl": keywords_url,
        "totalRecords": total,
        "effectiveTotal": effective_total,
        "pageSize": args.sem_page_size,
        "pagesFetched": len(page_results),
        "pagesRequested": [item["page"] for item in page_results],
        "summary": {
            "total": total,
            "totalVolume": safe_int(summary_data.get("total_volume")),
            "totalKeywordsWithDifficulty": safe_int(summary_data.get("total_keywords_with_difficulty")),
            "totalDifficulty": safe_int(summary_data.get("total_difficulty")),
        },
    }
    return normalized, {
        "meta": meta,
        "summary": {
            "requestPayload": summary_payload,
            "wrapper": summary_result["wrapper"],
            "upstream": summary_upstream,
        },
        "pages": page_results,
    }


def merge_rows(sim_rows: List[dict], sem_rows: List[dict]) -> List[dict]:
    merged: Dict[str, dict] = {}

    for row in sim_rows:
        key = row["keywordNormalized"]
        item = merged.setdefault(
            key,
            {
                "keyword": row["keyword"],
                "keywordNormalized": key,
                "sourcePresence": "sim_only",
                "score": None,
            },
        )
        item.update({k: v for k, v in row.items() if k not in ("keyword", "keywordNormalized")})

    for row in sem_rows:
        key = row["keywordNormalized"]
        item = merged.setdefault(
            key,
            {
                "keyword": row["keyword"],
                "keywordNormalized": key,
                "sourcePresence": "sem_only",
                "score": None,
            },
        )
        if item.get("sourcePresence") == "sim_only":
            item["sourcePresence"] = "both"
        item["keyword"] = item.get("keyword") or row["keyword"]
        item.update({k: v for k, v in row.items() if k not in ("keyword", "keywordNormalized")})

    rows = list(merged.values())
    for row in rows:
        sem_volume = row.get("semVolume")
        sem_cpc = row.get("semCpc")
        sem_kd = row.get("semKd")
        if sem_volume is None or sem_cpc is None or sem_kd is None:
            row["score"] = None
        else:
            volume = safe_float(sem_volume)
            cpc = safe_float(sem_cpc)
            kd = safe_float(sem_kd)
            row["score"] = None if volume <= 0 or cpc <= 0 or kd <= 0 else round(volume * cpc / kd, 6)

    rows.sort(
        key=lambda row: (
            row.get("score") is None,
            -(safe_float(row.get("score")) if row.get("score") is not None else -1),
            -safe_float(row.get("semVolume")),
            str(row.get("keyword", "")),
        )
    )
    return rows


def build_summary_counts(sim_rows: List[dict], sem_rows: List[dict], merged_rows: List[dict]) -> dict:
    counts = {
        "simCount": len(sim_rows),
        "semCount": len(sem_rows),
        "mergedCount": len(merged_rows),
        "bothCount": 0,
        "simOnlyCount": 0,
        "semOnlyCount": 0,
        "scoredCount": 0,
    }
    for row in merged_rows:
        source_presence = row.get("sourcePresence")
        if source_presence == "both":
            counts["bothCount"] += 1
        elif source_presence == "sim_only":
            counts["simOnlyCount"] += 1
        elif source_presence == "sem_only":
            counts["semOnlyCount"] += 1
        if row.get("score") is not None:
            counts["scoredCount"] += 1
    return counts


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


def build_snapshot(*, stamp: str, args: argparse.Namespace, sim_fetch: dict, sem_fetch: dict, sim_rows: List[dict], sem_rows: List[dict], merged_rows: List[dict], summary_counts: dict, excel_history_path: Path, report_history_path: Path) -> dict:
    return {
        "meta": {
            "generatedAt": datetime.now().isoformat(timespec="seconds"),
            "stamp": stamp,
            "target": {
                "keyword": args.keyword,
                "country": args.country,
                "latest": args.latest,
                "database": args.database,
                "currency": args.currency,
            },
            "request": {
                "simRowsPerPage": args.sim_rows_per_page,
                "simMaxKeywords": args.sim_max_keywords,
                "semPageSize": args.sem_page_size,
                "semMaxKeywords": args.sem_max_keywords,
                "simRangeFilter": SIM_RANGE_FILTER,
                "simSort": SIM_SORT,
                "semScoreFormula": "semVolume * semCpc / semKd",
            },
            "api": {
                "baseUrl": args.api_base,
                "sim": sim_fetch["meta"],
                "sem": sem_fetch["meta"],
            },
            "output": {
                "reportHistoryPath": str(report_history_path),
                "excelHistoryPath": str(excel_history_path),
            },
            "summary": summary_counts,
        },
        "sim": {
            "rows": sim_rows,
            "raw": sim_fetch,
        },
        "sem": {
            "rows": sem_rows,
            "raw": sem_fetch,
        },
        "mergedRows": merged_rows,
    }


def render_report(snapshot: dict) -> str:
    meta = snapshot.get("meta") or {}
    target = meta.get("target") or {}
    api = meta.get("api") or {}
    summary = meta.get("summary") or {}
    output = meta.get("output") or {}
    merged_rows = snapshot.get("mergedRows") or []

    sim_meta = api.get("sim") or {}
    sem_meta = api.get("sem") or {}

    preview_rows = []
    for row in merged_rows[:TOP_PREVIEW_ROWS]:
        preview_rows.append(
            [
                str(row.get("keyword") or "-"),
                str(row.get("sourcePresence") or "-"),
                to_display_number(row.get("score")) if row.get("score") is not None else "-",
                to_display_number(row.get("simWindowVolume")),
                to_display_number(row.get("semVolume")),
                to_display_number(row.get("semCpc")),
                to_display_number(row.get("semKd")),
            ]
        )

    lines: List[str] = []
    lines.append(f"# 词根扩词报告（{target.get('keyword', '-')}｜{meta.get('stamp', '-')}）")
    lines.append("")
    lines.append("## 摘要")
    lines.append("")
    lines.append(f"- 词根：{target.get('keyword', '-')}")
    lines.append(f"- 合并后唯一关键词数：{summary.get('mergedCount', 0)}")
    lines.append(f"- 可计算 score 的关键词数：{summary.get('scoredCount', 0)}")
    lines.append(f"- 来源分布：both={summary.get('bothCount', 0)} / sim_only={summary.get('simOnlyCount', 0)} / sem_only={summary.get('semOnlyCount', 0)}")
    lines.append("")

    lines.append("## 抓取概览")
    lines.append("")
    lines.append(f"- SIM totalRecords：{sim_meta.get('totalRecords', 0)}")
    lines.append(f"- SIM 实际抓取：{summary.get('simCount', 0)}（pages={sim_meta.get('pagesFetched', 0)}）")
    lines.append(f"- SEM totalRecords：{sem_meta.get('totalRecords', 0)}")
    lines.append(f"- SEM 实际抓取：{summary.get('semCount', 0)}（pages={sem_meta.get('pagesFetched', 0)}）")
    lines.append("")

    lines.append("## 合并结果概览")
    lines.append("")
    lines.append(f"- both：{summary.get('bothCount', 0)}")
    lines.append(f"- sim_only：{summary.get('simOnlyCount', 0)}")
    lines.append(f"- sem_only：{summary.get('semOnlyCount', 0)}")
    lines.append(f"- 排序公式：{(meta.get('request') or {}).get('semScoreFormula', 'semVolume * semCpc / semKd')}")
    lines.append("")

    lines.append("## Top 关键词预览")
    lines.append("")
    lines.extend(
        _md_table(
            ["keyword", "sourcePresence", "score", "simWindowVolume", "semVolume", "semCpc", "semKd"],
            preview_rows,
        )
    )
    lines.append("")

    lines.append("## 产物路径")
    lines.append("")
    lines.append(f"- Markdown：{output.get('reportHistoryPath', '-')}")
    lines.append(f"- Excel：{output.get('excelHistoryPath', '-')}")
    lines.append("")

    lines.append("## 备注")
    lines.append("")
    for remark in REQUIRED_REMARKS:
        lines.append(f"- {remark}")
    lines.append("")

    return "\n".join(lines)


def _require_openpyxl():
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Font
        from openpyxl.utils import get_column_letter
    except ImportError as exc:
        raise RuntimeError(
            "缺少依赖 openpyxl。请先执行 `pip3 install -r word-from-root/requirements.txt` 再运行。"
        ) from exc
    return Workbook, Font, get_column_letter


def write_excel(snapshot: dict, output_path: Path) -> None:
    Workbook, Font, get_column_letter = _require_openpyxl()

    meta = snapshot.get("meta") or {}
    target = meta.get("target") or {}
    summary = meta.get("summary") or {}
    merged_rows = snapshot.get("mergedRows") or []

    workbook = Workbook()
    summary_sheet = workbook.active
    summary_sheet.title = "summary"
    keywords_sheet = workbook.create_sheet("keywords")

    summary_rows = [
        ("keyword", target.get("keyword", "")),
        ("generatedAt", meta.get("generatedAt", "")),
        ("simCount", summary.get("simCount", 0)),
        ("semCount", summary.get("semCount", 0)),
        ("mergedCount", summary.get("mergedCount", 0)),
        ("bothCount", summary.get("bothCount", 0)),
        ("simOnlyCount", summary.get("simOnlyCount", 0)),
        ("semOnlyCount", summary.get("semOnlyCount", 0)),
        ("scoredCount", summary.get("scoredCount", 0)),
        ("scoreFormula", "semVolume * semCpc / semKd"),
    ]
    for idx, (name, value) in enumerate(summary_rows, start=1):
        summary_sheet.cell(row=idx, column=1, value=name)
        summary_sheet.cell(row=idx, column=2, value=value)
    summary_sheet.freeze_panes = "A2"

    headers = [
        "keyword",
        "sourcePresence",
        "score",
        "simWindowVolume",
        "simAverageVolume",
        "simCpc",
        "simKd",
        "simRank",
        "semVolume",
        "semCpc",
        "semKd",
        "semCompetitionLevel",
        "semResults",
        "semSnapshotDate",
        "semRank",
    ]
    keywords_sheet.append(headers)
    for cell in keywords_sheet[1]:
        cell.font = Font(bold=True)

    for row in merged_rows:
        keywords_sheet.append(
            [
                row.get("keyword"),
                row.get("sourcePresence"),
                row.get("score"),
                row.get("simWindowVolume"),
                row.get("simAverageVolume"),
                row.get("simCpc"),
                row.get("simKd"),
                row.get("simRank"),
                row.get("semVolume"),
                row.get("semCpc"),
                row.get("semKd"),
                row.get("semCompetitionLevel"),
                row.get("semResults"),
                row.get("semSnapshotDate"),
                row.get("semRank"),
            ]
        )

    keywords_sheet.freeze_panes = "A2"
    keywords_sheet.auto_filter.ref = f"A1:{get_column_letter(len(headers))}{max(keywords_sheet.max_row, 1)}"

    numeric_columns = {
        "C": "0.00",
        "D": "0",
        "E": "0",
        "F": "0.00",
        "G": "0.00",
        "H": "0",
        "I": "0",
        "J": "0.00",
        "K": "0.00",
        "L": "0.00",
        "M": "0",
        "O": "0",
    }
    for col, fmt in numeric_columns.items():
        for cell in keywords_sheet[col][1:]:
            cell.number_format = fmt

    for sheet in (summary_sheet, keywords_sheet):
        for column_cells in sheet.columns:
            values = ["" if cell.value is None else str(cell.value) for cell in column_cells]
            width = min(max(len(v) for v in values) + 2, 40)
            sheet.column_dimensions[column_cells[0].column_letter].width = width

    ensure_dir(output_path.parent)
    workbook.save(output_path)


def write_artifacts(*, stamp: str, snapshot: dict, fetch_archive: dict, data_dir: Path, snapshot_dir: Path, report_dir: Path, latest_report_path: Path, latest_xlsx_path: Path) -> dict:
    ensure_dir(data_dir)
    ensure_dir(snapshot_dir)
    ensure_dir(report_dir)
    ensure_dir(latest_report_path.parent)
    ensure_dir(latest_xlsx_path.parent)

    fetch_archive_path = data_dir / f"fetch-{stamp}.json"
    snapshot_path = snapshot_dir / f"snapshot-{stamp}.json"
    report_history_path = report_dir / f"report-{stamp}.md"
    excel_history_path = report_dir / f"keyword-table-{stamp}.xlsx"

    snapshot_meta = snapshot.setdefault("meta", {})
    output_meta = snapshot_meta.setdefault("output", {})
    output_meta["reportHistoryPath"] = str(report_history_path)
    output_meta["excelHistoryPath"] = str(excel_history_path)
    snapshot_meta["latestReportPath"] = str(latest_report_path)
    snapshot_meta["latestExcelPath"] = str(latest_xlsx_path)

    report_text = render_report(snapshot)
    dump_json(fetch_archive_path, fetch_archive)
    dump_json(snapshot_path, snapshot)
    report_history_path.write_text(report_text, encoding="utf-8")
    latest_report_path.write_text(report_text, encoding="utf-8")
    write_excel(snapshot, excel_history_path)
    copyfile(excel_history_path, latest_xlsx_path)

    return {
        "fetchArchivePath": fetch_archive_path,
        "snapshotPath": snapshot_path,
        "reportHistoryPath": report_history_path,
        "excelHistoryPath": excel_history_path,
    }


def rebuild_history_artifacts(snapshot: dict, report_dir: Path) -> Tuple[Path, Path, str]:
    ensure_dir(report_dir)
    meta = snapshot.get("meta") or {}
    stamp = str(meta.get("stamp") or "")
    if not stamp:
        raise RuntimeError("snapshot 缺少 meta.stamp")

    report_history_path = report_dir / f"report-{stamp}.md"
    excel_history_path = report_dir / f"keyword-table-{stamp}.xlsx"
    report_text = render_report(snapshot)
    report_history_path.write_text(report_text, encoding="utf-8")
    write_excel(snapshot, excel_history_path)
    return report_history_path, excel_history_path, report_text


def run_pipeline(args: argparse.Namespace) -> int:
    data_dir = Path(args.data_dir).resolve()
    snapshot_dir = Path(args.snapshot_dir).resolve()
    report_dir = Path(args.report_dir).resolve()
    latest_report_path = Path(args.latest_report_path).resolve()
    latest_xlsx_path = Path(args.latest_xlsx_path).resolve()
    token_path = Path(args.token_path).resolve()
    gmitm_path = Path(args.gmitm_path).resolve()

    keyword = str(args.keyword or "").strip()
    if not keyword:
        raise SystemExit("--keyword 不能为空")
    args.keyword = keyword

    token = read_text_required(token_path, "token 文件")
    gmitm = read_gmitm(gmitm_path)
    headers = build_headers(token)

    stamp = now_stamp()
    sim_rows, sim_fetch = fetch_sim_keywords(args, headers)
    sem_rows, sem_fetch = fetch_sem_keywords(args, headers, gmitm)
    merged_rows = merge_rows(sim_rows, sem_rows)
    summary_counts = build_summary_counts(sim_rows, sem_rows, merged_rows)

    placeholder_report_history_path = report_dir / f"report-{stamp}.md"
    placeholder_excel_history_path = report_dir / f"keyword-table-{stamp}.xlsx"
    snapshot = build_snapshot(
        stamp=stamp,
        args=args,
        sim_fetch=sim_fetch,
        sem_fetch=sem_fetch,
        sim_rows=sim_rows,
        sem_rows=sem_rows,
        merged_rows=merged_rows,
        summary_counts=summary_counts,
        excel_history_path=placeholder_excel_history_path,
        report_history_path=placeholder_report_history_path,
    )

    fetch_archive = {
        "meta": {
            "generatedAt": datetime.now().isoformat(timespec="seconds"),
            "stamp": stamp,
            "keyword": keyword,
        },
        "sim": sim_fetch,
        "sem": sem_fetch,
    }

    artifact_paths = write_artifacts(
        stamp=stamp,
        snapshot=snapshot,
        fetch_archive=fetch_archive,
        data_dir=data_dir,
        snapshot_dir=snapshot_dir,
        report_dir=report_dir,
        latest_report_path=latest_report_path,
        latest_xlsx_path=latest_xlsx_path,
    )

    print(f"[done] fetch archive : {artifact_paths['fetchArchivePath']}")
    print(f"[done] snapshot      : {artifact_paths['snapshotPath']}")
    print(f"[done] report history: {artifact_paths['reportHistoryPath']}")
    print(f"[done] report latest : {latest_report_path}")
    print(f"[done] excel history : {artifact_paths['excelHistoryPath']}")
    print(f"[done] excel latest  : {latest_xlsx_path}")
    print(f"[done] sim rows      : {len(sim_rows)}")
    print(f"[done] sem rows      : {len(sem_rows)}")
    print(f"[done] merged rows   : {len(merged_rows)}")
    print(f"[done] scored rows   : {summary_counts['scoredCount']}")
    return 0


def rebuild_reports(args: argparse.Namespace) -> int:
    snapshot_dir = Path(args.snapshot_dir).resolve()
    report_dir = Path(args.report_dir).resolve()
    latest_report_path = Path(args.latest_report_path).resolve()
    latest_xlsx_path = Path(args.latest_xlsx_path).resolve()

    ensure_dir(snapshot_dir)
    ensure_dir(report_dir)
    ensure_dir(latest_report_path.parent)
    ensure_dir(latest_xlsx_path.parent)

    files = list_snapshot_files(snapshot_dir)
    if not files:
        raise SystemExit(f"未找到快照文件: {snapshot_dir}")

    latest_report_text = ""
    latest_excel_path: Optional[Path] = None

    for path in files:
        snapshot = load_json(path)
        report_history_path, excel_history_path, report_text = rebuild_history_artifacts(snapshot, report_dir)
        latest_report_text = report_text
        latest_excel_path = excel_history_path
        print(f"[rebuild] report: {report_history_path}")
        print(f"[rebuild] excel : {excel_history_path}")

    latest_report_path.write_text(latest_report_text, encoding="utf-8")
    if latest_excel_path is not None:
        copyfile(latest_excel_path, latest_xlsx_path)

    print(f"[done] latest report: {latest_report_path}")
    print(f"[done] latest excel : {latest_xlsx_path}")
    return 0


def validate_report(args: argparse.Namespace) -> int:
    report_path = Path(args.report).resolve()
    xlsx_path = Path(args.xlsx).resolve()
    if not report_path.exists():
        raise SystemExit(f"报告不存在: {report_path}")
    text = report_path.read_text(encoding="utf-8")

    missing_sections = [section for section in REQUIRED_SECTIONS if section not in text]
    missing_remarks = [remark for remark in REQUIRED_REMARKS if remark not in text]
    if missing_sections or missing_remarks:
        if missing_sections:
            print("缺少 section:")
            for item in missing_sections:
                print(f"- {item}")
        if missing_remarks:
            print("缺少 remark:")
            for item in missing_remarks:
                print(f"- {item}")
        raise SystemExit(1)

    if not xlsx_path.exists():
        raise SystemExit(f"Excel 不存在: {xlsx_path}")

    print(f"[ok] report validated: {report_path}")
    print(f"[ok] xlsx exists      : {xlsx_path}")
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
