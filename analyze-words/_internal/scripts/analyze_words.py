#!/usr/bin/env python3
"""批量分析关键词指标（SEM keywords.GetInfo）。

Usage:
  python3 analyze-words/_internal/scripts/analyze_words.py run --keyword "image to text"
  python3 analyze-words/_internal/scripts/analyze_words.py run --keyword-file /tmp/keywords.txt
  python3 analyze-words/_internal/scripts/analyze_words.py rebuild-reports
  python3 analyze-words/_internal/scripts/analyze_words.py validate-report
"""

from __future__ import annotations

import argparse
import json
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

PROJECT_DIR = Path(__file__).resolve().parents[2]
LOCAL_SERVICE_TOKEN_PATH = PROJECT_DIR / "local-service" / "bridge_token.txt"
LOCAL_SERVICE_GMITM_PATH = PROJECT_DIR / "local-service" / "__gmitm.txt"
LEGACY_LOCAL_SERVICE_GMITM_PATH = PROJECT_DIR / "local-service" / "gmitm.txt"

DEFAULT_API_BASE = "http://127.0.0.1:17311"
DEFAULT_ENDPOINT = "/sem/kwogw/v2/webapi/keywords.GetInfo"

MAX_RETRIES = 2
RETRY_BACKOFF_SECONDS = [0.8, 1.6]
REQUEST_TIMEOUT_SECONDS = 180

TOP_PREVIEW_ROWS = 30
SNAPSHOT_RE = re.compile(r"^snapshot-(\d{8}-\d{6})\.json$")
SPACE_RE = re.compile(r"\s+")

REQUIRED_SECTIONS = [
    "## 摘要",
    "## 抓取概览",
    "## 聚合结果概览",
    "## 关键词结果预览",
    "## 失败关键词",
    "## 产物路径",
    "## 备注",
]

REQUIRED_REMARKS = [
    "globalVolume = sum(volume)",
    "globalCpcAvg / globalDifficultyAvg 仅统计非 null 项",
    "任一关键词抓取失败时默认整次失败，不落任何新产物",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="批量调用 keywords.GetInfo 并聚合关键词指标")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="抓取 + 聚合 + 快照 + 报告")
    run_parser.add_argument("--keyword", action="append", default=[], help="关键词，可重复传入")
    run_parser.add_argument(
        "--keyword-file",
        action="append",
        default=[],
        help="关键词文件（UTF-8，每行一个关键词，支持 # 注释）",
    )

    run_parser.add_argument("--api-base", default=DEFAULT_API_BASE)
    run_parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    run_parser.add_argument("--token-path", default=str(LOCAL_SERVICE_TOKEN_PATH))
    run_parser.add_argument("--gmitm-path", default=str(LOCAL_SERVICE_GMITM_PATH))

    run_parser.add_argument("--device", type=int, default=0)
    run_parser.add_argument("--currency", default="USD")
    run_parser.add_argument("--database", default="us")
    run_parser.add_argument("--location", type=int, default=0)
    run_parser.add_argument("--date", default="")
    run_parser.add_argument("--timeout-ms", type=int, default=45000)
    run_parser.add_argument("--wait-timeout-ms", type=int, default=120000)

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


def now_stamp() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def safe_float(value) -> float:
    try:
        if value is None or value == "":
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def to_display_number(value, digits: int = 2) -> str:
    if value is None:
        return "-"
    number = safe_float(value)
    if abs(number - round(number)) < 1e-9:
        return str(int(round(number)))
    return f"{number:.{digits}f}"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def normalize_keyword_text(text: str) -> str:
    return SPACE_RE.sub(" ", str(text or "").strip().lower())


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
        f"gmitm 文件不存在: {path}。请在 analyze-words/local-service/__gmitm.txt 写入当前会话 __gmitm 值。"
    )


def _read_keywords_from_file(path: Path) -> List[str]:
    if not path.exists():
        raise RuntimeError(f"关键词文件不存在: {path}")
    lines = path.read_text(encoding="utf-8").splitlines()
    keywords: List[str] = []
    for raw in lines:
        text = str(raw).strip()
        if not text:
            continue
        if text.startswith("#"):
            continue
        keywords.append(text)
    return keywords


def collect_keywords(args: argparse.Namespace) -> List[dict]:
    raw_keywords: List[str] = []
    for text in args.keyword or []:
        if text is None:
            continue
        cleaned = str(text).strip()
        if cleaned:
            raw_keywords.append(cleaned)

    for file_arg in args.keyword_file or []:
        file_path = Path(file_arg).resolve()
        raw_keywords.extend(_read_keywords_from_file(file_path))

    deduped: List[dict] = []
    seen: set[str] = set()
    for keyword in raw_keywords:
        normalized = normalize_keyword_text(keyword)
        if not normalized:
            continue
        if normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(
            {
                "keyword": keyword,
                "keywordNormalized": normalized,
            }
        )

    if not deduped:
        raise SystemExit("未获取到有效关键词。请使用 --keyword 或 --keyword-file 提供关键词列表。")
    return deduped


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


def build_request_body(*, keyword: str, index: int, args: argparse.Namespace) -> dict:
    return {
        "id": 32 + index,
        "jsonrpc": "2.0",
        "method": "keywords.GetInfo",
        "params": {
            "phrase": keyword,
            "device": args.device,
            "currency": args.currency,
            "database": args.database,
            "locati0n": args.location,
            "date": args.date,
        },
    }


def build_payload(*, keyword: str, index: int, gmitm: str, args: argparse.Namespace) -> dict:
    return {
        "__gmitm": gmitm,
        "requestBody": build_request_body(keyword=keyword, index=index, args=args),
        "timeoutMs": args.timeout_ms,
        "waitTimeoutMs": args.wait_timeout_ms,
    }


def fetch_keyword_with_retry(
    *,
    api_url: str,
    headers: dict,
    gmitm: str,
    keyword: str,
    keyword_normalized: str,
    index: int,
    args: argparse.Namespace,
) -> dict:
    attempts: List[dict] = []

    for attempt in range(MAX_RETRIES + 1):
        payload = build_payload(keyword=keyword, index=index, gmitm=gmitm, args=args)
        try:
            result = post_local_service(
                api_url=api_url,
                headers=headers,
                payload=payload,
                expect_jsonrpc=True,
            )
            upstream = result["upstream"]
            if not isinstance(upstream, dict):
                raise RuntimeError("上游 JSON-RPC 响应不是对象")

            upstream_error = upstream.get("error")
            if isinstance(upstream_error, dict):
                code = upstream_error.get("code")
                message = upstream_error.get("message")
                raise RuntimeError(f"上游 JSON-RPC 错误: code={code} message={message}")

            keyword_rows = ((upstream.get("result") or {}).get("keywords") or [])
            if not isinstance(keyword_rows, list):
                raise RuntimeError("上游 result.keywords 非数组")

            attempts.append(
                {
                    "attempt": attempt + 1,
                    "status": "ok",
                    "requestPayload": payload,
                    "wrapper": result["wrapper"],
                    "upstream": upstream,
                    "rowsCount": len(keyword_rows),
                }
            )
            return {
                "ok": True,
                "keyword": keyword,
                "keywordNormalized": keyword_normalized,
                "attempts": attempts,
                "keywordsRows": keyword_rows,
            }
        except (RuntimeError, URLError, ValueError, json.JSONDecodeError) as exc:
            attempts.append(
                {
                    "attempt": attempt + 1,
                    "status": "error",
                    "requestPayload": payload,
                    "error": str(exc),
                }
            )
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_BACKOFF_SECONDS[min(attempt, len(RETRY_BACKOFF_SECONDS) - 1)])
                continue
            return {
                "ok": False,
                "keyword": keyword,
                "keywordNormalized": keyword_normalized,
                "attempts": attempts,
                "error": str(exc),
            }

    return {
        "ok": False,
        "keyword": keyword,
        "keywordNormalized": keyword_normalized,
        "attempts": attempts,
        "error": "未知错误",
    }


def aggregate_keyword_metrics(keyword_rows: List[dict]) -> dict:
    volumes: List[float] = []
    cpc_values: List[float] = []
    kd_values: List[float] = []
    databases: set[str] = set()

    for item in keyword_rows:
        if not isinstance(item, dict):
            continue

        volume = safe_float(item.get("volume"))
        volumes.append(volume)

        cpc = item.get("cpc")
        if isinstance(cpc, (int, float)):
            cpc_values.append(float(cpc))

        difficulty = item.get("difficulty")
        if isinstance(difficulty, (int, float)):
            kd_values.append(float(difficulty))

        database = str(item.get("database") or "").strip().lower()
        if database:
            databases.add(database)

    global_volume = sum(volumes)
    global_cpc_avg = (sum(cpc_values) / len(cpc_values)) if cpc_values else None
    global_difficulty_avg = (sum(kd_values) / len(kd_values)) if kd_values else None

    return {
        "globalVolume": int(round(global_volume)) if abs(global_volume - round(global_volume)) < 1e-9 else round(global_volume, 4),
        "globalCpcAvg": round(global_cpc_avg, 6) if global_cpc_avg is not None else None,
        "globalDifficultyAvg": round(global_difficulty_avg, 6) if global_difficulty_avg is not None else None,
        "databaseCount": len(databases),
        "cpcSampleCount": len(cpc_values),
        "difficultySampleCount": len(kd_values),
        "rowsCount": len(keyword_rows),
    }


def summarize_success_rows(rows: List[dict], input_count: int, failure_count: int) -> dict:
    total_global_volume = sum(safe_float(row.get("globalVolume")) for row in rows)

    cpc_values = [safe_float(row.get("globalCpcAvg")) for row in rows if row.get("globalCpcAvg") is not None]
    kd_values = [safe_float(row.get("globalDifficultyAvg")) for row in rows if row.get("globalDifficultyAvg") is not None]

    return {
        "inputCount": input_count,
        "successCount": len(rows),
        "failureCount": failure_count,
        "totalGlobalVolume": int(round(total_global_volume)) if abs(total_global_volume - round(total_global_volume)) < 1e-9 else round(total_global_volume, 4),
        "avgGlobalCpc": round(sum(cpc_values) / len(cpc_values), 6) if cpc_values else None,
        "avgGlobalDifficulty": round(sum(kd_values) / len(kd_values), 6) if kd_values else None,
    }


def sort_rows(rows: List[dict]) -> List[dict]:
    return sorted(
        rows,
        key=lambda row: (
            -safe_float(row.get("globalVolume")),
            -(safe_float(row.get("globalCpcAvg")) if row.get("globalCpcAvg") is not None else -1),
            str(row.get("keyword") or ""),
        ),
    )


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


def build_snapshot(
    *,
    stamp: str,
    args: argparse.Namespace,
    keywords: List[dict],
    rows: List[dict],
    failures: List[dict],
    summary: dict,
    report_history_path: Path,
) -> dict:
    return {
        "meta": {
            "generatedAt": datetime.now().isoformat(timespec="seconds"),
            "stamp": stamp,
            "target": {
                "keywords": [item["keyword"] for item in keywords],
                "keywordCount": len(keywords),
            },
            "request": {
                "apiBase": args.api_base,
                "endpoint": args.endpoint,
                "device": args.device,
                "currency": args.currency,
                "database": args.database,
                "locati0n": args.location,
                "date": args.date,
                "timeoutMs": args.timeout_ms,
                "waitTimeoutMs": args.wait_timeout_ms,
                "maxRetries": MAX_RETRIES,
            },
            "summary": summary,
            "output": {
                "reportHistoryPath": str(report_history_path),
            },
        },
        "rows": rows,
        "failures": failures,
    }


def render_report(snapshot: dict) -> str:
    meta = snapshot.get("meta") or {}
    request = meta.get("request") or {}
    summary = meta.get("summary") or {}
    output = meta.get("output") or {}

    rows = snapshot.get("rows") or []
    failures = snapshot.get("failures") or []

    preview_rows: List[List[str]] = []
    for row in rows[:TOP_PREVIEW_ROWS]:
        preview_rows.append(
            [
                str(row.get("keyword") or "-"),
                to_display_number(row.get("globalVolume"), digits=0),
                to_display_number(row.get("globalCpcAvg")),
                to_display_number(row.get("globalDifficultyAvg")),
                to_display_number(row.get("databaseCount"), digits=0),
            ]
        )

    failure_rows: List[List[str]] = []
    for row in failures:
        failure_rows.append(
            [
                str(row.get("keyword") or "-"),
                str(row.get("attempts") or "-"),
                str(row.get("error") or "-"),
            ]
        )

    lines: List[str] = []
    lines.append(f"# 关键词批量分析报告（{meta.get('stamp', '-')}）")
    lines.append("")

    lines.append("## 摘要")
    lines.append("")
    lines.append(f"- 输入关键词数：{summary.get('inputCount', 0)}")
    lines.append(f"- 成功关键词数：{summary.get('successCount', 0)}")
    lines.append(f"- 失败关键词数：{summary.get('failureCount', 0)}")
    lines.append("")

    lines.append("## 抓取概览")
    lines.append("")
    lines.append(f"- API：{request.get('apiBase', '-')}{request.get('endpoint', '-')}")
    lines.append(f"- 默认参数：device={request.get('device', '-')} currency={request.get('currency', '-')} database={request.get('database', '-')} locati0n={request.get('locati0n', '-')} date={request.get('date', '')!r}")
    lines.append(f"- timeoutMs={request.get('timeoutMs', '-')} / waitTimeoutMs={request.get('waitTimeoutMs', '-')} / maxRetries={request.get('maxRetries', '-')}")
    lines.append("")

    lines.append("## 聚合结果概览")
    lines.append("")
    lines.append(f"- totalGlobalVolume（所有关键词汇总）：{to_display_number(summary.get('totalGlobalVolume'), digits=0)}")
    lines.append(f"- avgGlobalCpc（关键词级均值）：{to_display_number(summary.get('avgGlobalCpc'))}")
    lines.append(f"- avgGlobalDifficulty（关键词级均值）：{to_display_number(summary.get('avgGlobalDifficulty'))}")
    lines.append("")

    lines.append("## 关键词结果预览")
    lines.append("")
    lines.extend(
        _md_table(
            ["keyword", "globalVolume", "globalCpcAvg", "globalDifficultyAvg", "databaseCount"],
            preview_rows,
        )
    )
    lines.append("")

    lines.append("## 失败关键词")
    lines.append("")
    lines.extend(_md_table(["keyword", "attempts", "error"], failure_rows))
    lines.append("")

    lines.append("## 产物路径")
    lines.append("")
    lines.append(f"- Markdown：{output.get('reportHistoryPath', '-')}")
    lines.append("")

    lines.append("## 备注")
    lines.append("")
    for remark in REQUIRED_REMARKS:
        lines.append(f"- {remark}")
    lines.append("")

    return "\n".join(lines)


def write_artifacts(
    *,
    stamp: str,
    snapshot: dict,
    fetch_archive: dict,
    data_dir: Path,
    snapshot_dir: Path,
    report_dir: Path,
    latest_report_path: Path,
) -> dict:
    ensure_dir(data_dir)
    ensure_dir(snapshot_dir)
    ensure_dir(report_dir)
    ensure_dir(latest_report_path.parent)

    fetch_archive_path = data_dir / f"fetch-{stamp}.json"
    snapshot_path = snapshot_dir / f"snapshot-{stamp}.json"
    report_history_path = report_dir / f"report-{stamp}.md"

    snapshot_meta = snapshot.setdefault("meta", {})
    output_meta = snapshot_meta.setdefault("output", {})
    output_meta["reportHistoryPath"] = str(report_history_path)
    snapshot_meta["latestReportPath"] = str(latest_report_path)

    report_text = render_report(snapshot)

    dump_json(fetch_archive_path, fetch_archive)
    dump_json(snapshot_path, snapshot)
    report_history_path.write_text(report_text, encoding="utf-8")
    latest_report_path.write_text(report_text, encoding="utf-8")

    return {
        "fetchArchivePath": fetch_archive_path,
        "snapshotPath": snapshot_path,
        "reportHistoryPath": report_history_path,
    }


def rebuild_history_artifact(snapshot: dict, report_dir: Path) -> Tuple[Path, str]:
    ensure_dir(report_dir)

    meta = snapshot.get("meta") or {}
    stamp = str(meta.get("stamp") or "")
    if not stamp:
        raise RuntimeError("snapshot 缺少 meta.stamp")

    report_history_path = report_dir / f"report-{stamp}.md"
    snapshot_meta = snapshot.setdefault("meta", {})
    output_meta = snapshot_meta.setdefault("output", {})
    output_meta["reportHistoryPath"] = str(report_history_path)

    report_text = render_report(snapshot)
    report_history_path.write_text(report_text, encoding="utf-8")
    return report_history_path, report_text


def run_pipeline(args: argparse.Namespace) -> int:
    data_dir = Path(args.data_dir).resolve()
    snapshot_dir = Path(args.snapshot_dir).resolve()
    report_dir = Path(args.report_dir).resolve()
    latest_report_path = Path(args.latest_report_path).resolve()
    token_path = Path(args.token_path).resolve()
    gmitm_path = Path(args.gmitm_path).resolve()

    token = read_text_required(token_path, "token 文件")
    gmitm = read_gmitm(gmitm_path)
    headers = build_headers(token)

    keywords = collect_keywords(args)
    api_url = args.api_base.rstrip("/") + args.endpoint

    success_rows: List[dict] = []
    failures: List[dict] = []
    raw_results: List[dict] = []

    for index, item in enumerate(keywords, start=1):
        keyword = item["keyword"]
        keyword_normalized = item["keywordNormalized"]

        fetch_result = fetch_keyword_with_retry(
            api_url=api_url,
            headers=headers,
            gmitm=gmitm,
            keyword=keyword,
            keyword_normalized=keyword_normalized,
            index=index,
            args=args,
        )
        raw_results.append(fetch_result)

        if not fetch_result.get("ok"):
            attempts = fetch_result.get("attempts") or []
            failures.append(
                {
                    "keyword": keyword,
                    "keywordNormalized": keyword_normalized,
                    "attempts": len(attempts),
                    "error": str(fetch_result.get("error") or "未知错误"),
                }
            )
            continue

        keyword_rows = fetch_result.get("keywordsRows") or []
        metrics = aggregate_keyword_metrics(keyword_rows)
        success_rows.append(
            {
                "keyword": keyword,
                "keywordNormalized": keyword_normalized,
                **metrics,
            }
        )

    sorted_rows = sort_rows(success_rows)
    summary = summarize_success_rows(sorted_rows, input_count=len(keywords), failure_count=len(failures))

    if failures:
        print("以下关键词抓取失败：")
        for item in failures:
            print(f"- {item['keyword']} (attempts={item['attempts']}): {item['error']}")
        raise SystemExit("存在失败关键词，按默认策略终止且不落任何新产物。")

    stamp = now_stamp()
    placeholder_report_history_path = report_dir / f"report-{stamp}.md"

    snapshot = build_snapshot(
        stamp=stamp,
        args=args,
        keywords=keywords,
        rows=sorted_rows,
        failures=failures,
        summary=summary,
        report_history_path=placeholder_report_history_path,
    )

    fetch_archive = {
        "meta": {
            "generatedAt": datetime.now().isoformat(timespec="seconds"),
            "stamp": stamp,
            "summary": summary,
            "request": {
                "apiUrl": api_url,
                "maxRetries": MAX_RETRIES,
            },
        },
        "requests": raw_results,
    }

    artifact_paths = write_artifacts(
        stamp=stamp,
        snapshot=snapshot,
        fetch_archive=fetch_archive,
        data_dir=data_dir,
        snapshot_dir=snapshot_dir,
        report_dir=report_dir,
        latest_report_path=latest_report_path,
    )

    print(f"[done] fetch archive : {artifact_paths['fetchArchivePath']}")
    print(f"[done] snapshot      : {artifact_paths['snapshotPath']}")
    print(f"[done] report history: {artifact_paths['reportHistoryPath']}")
    print(f"[done] report latest : {latest_report_path}")
    print(f"[done] input keywords: {summary['inputCount']}")
    print(f"[done] success count : {summary['successCount']}")
    print(f"[done] failure count : {summary['failureCount']}")
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

    latest_report_text = ""
    for path in files:
        snapshot = load_json(path)
        report_history_path, report_text = rebuild_history_artifact(snapshot, report_dir)
        latest_report_text = report_text
        print(f"[rebuild] report: {report_history_path}")

    latest_report_path.write_text(latest_report_text, encoding="utf-8")
    print(f"[done] latest report: {latest_report_path}")
    return 0


def validate_report(args: argparse.Namespace) -> int:
    report_path = Path(args.report).resolve()
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

    print(f"[ok] report validated: {report_path}")
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
