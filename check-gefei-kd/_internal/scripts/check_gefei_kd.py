#!/usr/bin/env python3
"""批量查询哥飞 KD API，并生成快照与报告。

Usage:
  python3 check-gefei-kd/_internal/scripts/check_gefei_kd.py run --keyword "image to text"
  python3 check-gefei-kd/_internal/scripts/check_gefei_kd.py run --keyword-file /tmp/keywords.txt
  python3 check-gefei-kd/_internal/scripts/check_gefei_kd.py rebuild-reports
  python3 check-gefei-kd/_internal/scripts/check_gefei_kd.py validate-report
"""

from __future__ import annotations

import argparse
import json
import os
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

PROJECT_DIR = Path(__file__).resolve().parents[2]

DEFAULT_API_BASE = "https://seo.web.cafe"
DEFAULT_ENDPOINT = "/kd/api/v1/kd"
DEFAULT_API_KEY_FILE = PROJECT_DIR / "api_key.txt"
DEFAULT_API_KEY_ENV = "GEFEI_KD_API_KEY"

SNAPSHOT_RE = re.compile(r"^snapshot-(\d{8}-\d{6})\.json$")
SPACE_RE = re.compile(r"\s+")

REQUEST_TIMEOUT_SECONDS = 60
TOP_PREVIEW_ROWS = 200

REQUIRED_SECTIONS = [
    "## 摘要",
    "## 请求参数",
    "## 关键词结果明细",
    "## 失败明细",
    "## 产物路径",
    "## 备注",
]

REQUIRED_REMARKS = [
    "API 默认使用 Header 鉴权（Authorization: Bearer <token>），可通过参数切换为 query token。",
    "MCP/API 频率限制：每分钟最多约 10 次请求，默认最小请求间隔为 6.2 秒。",
    "7 天内同词命中缓存会更快返回，但仍计入当日额度。",
]


class RequestError(RuntimeError):
    """带错误元信息的请求异常。"""

    def __init__(
        self,
        message: str,
        *,
        status: Optional[int] = None,
        code: Optional[str] = None,
        retryable: bool = False,
        fatal_global: bool = False,
        raw_body: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.retryable = retryable
        self.fatal_global = fatal_global
        self.raw_body = raw_body


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="批量查询哥飞 KD API")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="抓取 + 快照 + 报告")
    run_parser.add_argument("--keyword", action="append", default=[], help="关键词，可重复")
    run_parser.add_argument(
        "--keyword-file",
        action="append",
        default=[],
        help="关键词文件（UTF-8，每行一个关键词，支持 # 注释）",
    )
    run_parser.add_argument(
        "--keywords-csv",
        action="append",
        default=[],
        help="逗号分隔关键词列表，可重复",
    )

    run_parser.add_argument("--api-base", default=DEFAULT_API_BASE)
    run_parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    run_parser.add_argument("--api-key", default="", help="直接传入 API Key（优先级最高）")
    run_parser.add_argument("--api-key-env", default=DEFAULT_API_KEY_ENV)
    run_parser.add_argument("--api-key-file", default=str(DEFAULT_API_KEY_FILE))
    run_parser.add_argument("--auth-mode", choices=["header", "query"], default="header")

    run_parser.add_argument("--gl", default="us")
    run_parser.add_argument("--hl", default="en")
    run_parser.add_argument("--force", type=int, choices=[0, 1], default=0)
    run_parser.add_argument("--response-format", default="json", choices=["json"])

    run_parser.add_argument("--min-interval-seconds", type=float, default=6.2)
    run_parser.add_argument("--max-retries", type=int, default=2)
    run_parser.add_argument("--timeout-seconds", type=int, default=REQUEST_TIMEOUT_SECONDS)
    run_parser.add_argument("--dry-run", action="store_true")

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


def resolve_api_key(args: argparse.Namespace) -> Tuple[str, str]:
    direct = str(args.api_key or "").strip()
    if direct:
        return direct, "--api-key"

    env_name = str(args.api_key_env or "").strip()
    if env_name:
        env_val = str(os.getenv(env_name) or "").strip()
        if env_val:
            return env_val, f"env:{env_name}"

    file_path = Path(args.api_key_file).resolve()
    return read_text_required(file_path, "api_key 文件"), str(file_path)


def mask_secret(secret: str) -> str:
    text = str(secret or "")
    if len(text) <= 10:
        return "*" * len(text)
    return f"{text[:6]}****{text[-4:]}"


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
        value = str(text or "").strip()
        if value:
            raw_keywords.append(value)

    for file_arg in args.keyword_file or []:
        file_path = Path(file_arg).resolve()
        raw_keywords.extend(_read_keywords_from_file(file_path))

    for csv_arg in args.keywords_csv or []:
        text = str(csv_arg or "").strip()
        if not text:
            continue
        parts = [part.strip() for part in text.split(",")]
        raw_keywords.extend([part for part in parts if part])

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
        raise SystemExit("未获取到有效关键词。请使用 --keyword / --keyword-file / --keywords-csv 提供关键词列表。")
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


def _extract_error_payload(parsed: Optional[dict]) -> Tuple[Optional[str], str]:
    if not isinstance(parsed, dict):
        return None, ""

    if isinstance(parsed.get("error"), dict):
        err = parsed.get("error") or {}
        code = str(err.get("code") or "").strip() or None
        msg = str(err.get("message") or "").strip()
        return code, msg

    if isinstance(parsed.get("error"), str):
        # 部分上游直接把错误文本放在 error 字段，此时将其视为 message，不作为 code。
        msg = str(parsed.get("error") or "").strip()
        if not msg:
            msg = str(parsed.get("message") or "").strip()
        return None, msg

    code = str(parsed.get("code") or "").strip() or None
    msg = str(parsed.get("message") or "").strip()
    return code, msg


def _classify_http_error(*, status: Optional[int], code: Optional[str], message: str, raw_body: str) -> RequestError:
    status_code = int(status or 0) if status is not None else None
    normalized_code = str(code or "").strip().lower() or None
    message_lower = str(message or "").strip().lower()

    if status_code == 401 or normalized_code == "auth":
        return RequestError(
            message or "API 认证失败（auth）",
            status=status_code,
            code=normalized_code or "auth",
            retryable=False,
            fatal_global=True,
            raw_body=raw_body,
        )

    is_quota = normalized_code == "quota" or ("quota" in message_lower) or ("额度" in str(message or ""))
    is_rate = normalized_code == "rate" or ("rate" in message_lower) or ("频率" in str(message or ""))

    if status_code == 429 and is_quota:
        return RequestError(
            message or "当日额度耗尽（quota）",
            status=status_code,
            code="quota",
            retryable=False,
            fatal_global=True,
            raw_body=raw_body,
        )

    if status_code == 429 and is_rate:
        return RequestError(
            message or "触发频率限制（rate）",
            status=status_code,
            code="rate",
            retryable=True,
            fatal_global=False,
            raw_body=raw_body,
        )

    if status_code == 400:
        return RequestError(
            message or "参数错误（400）",
            status=status_code,
            code=normalized_code,
            retryable=False,
            fatal_global=False,
            raw_body=raw_body,
        )

    if status_code and status_code >= 500:
        return RequestError(
            message or f"上游服务错误（{status_code}）",
            status=status_code,
            code=normalized_code,
            retryable=True,
            fatal_global=False,
            raw_body=raw_body,
        )

    return RequestError(
        message or f"请求失败（status={status_code or '-'}）",
        status=status_code,
        code=normalized_code,
        retryable=False,
        fatal_global=False,
        raw_body=raw_body,
    )


def _request_once(
    *,
    api_url: str,
    keyword: str,
    gl: str,
    hl: str,
    force: int,
    response_format: str,
    api_key: str,
    auth_mode: str,
    timeout_seconds: int,
) -> Tuple[int, str, dict]:
    params = {
        "keyword": keyword,
        "gl": gl,
        "hl": hl,
        "force": int(force),
        "format": response_format,
    }
    if auth_mode == "query":
        params["token"] = api_key

    url = f"{api_url}?{urlencode(params)}"
    headers = {
        "Accept": "application/json",
        "User-Agent": "check-gefei-kd/0.1",
    }
    if auth_mode == "header":
        headers["Authorization"] = f"Bearer {api_key}"

    req = Request(url, headers=headers, method="GET")

    try:
        with urlopen(req, timeout=timeout_seconds) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            status = int(getattr(resp, "status", 0) or 0)
            parsed = json.loads(body)
            if not isinstance(parsed, dict):
                raise RequestError("返回 JSON 非对象", status=status, raw_body=body)
            return status, body, parsed
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace") if hasattr(exc, "read") else ""
        parsed: dict = {}
        try:
            maybe_parsed = json.loads(body)
            if isinstance(maybe_parsed, dict):
                parsed = maybe_parsed
        except json.JSONDecodeError:
            parsed = {}

        code, message = _extract_error_payload(parsed)
        raise _classify_http_error(
            status=int(getattr(exc, "code", 0) or 0),
            code=code,
            message=message,
            raw_body=body,
        ) from exc
    except URLError as exc:
        raise RequestError(str(exc), retryable=True) from exc
    except json.JSONDecodeError as exc:
        raise RequestError("返回非合法 JSON", retryable=False) from exc


def fetch_keyword_with_retry(
    *,
    api_url: str,
    keyword: str,
    keyword_normalized: str,
    args: argparse.Namespace,
    api_key: str,
    throttle_state: dict,
) -> dict:
    attempts: List[dict] = []

    max_retries = max(int(args.max_retries), 0)
    min_interval = max(float(args.min_interval_seconds), 0.0)
    timeout_seconds = max(int(args.timeout_seconds), 1)

    for attempt_index in range(max_retries + 1):
        waited_seconds = 0.0
        now = time.monotonic()
        last_request_at = float(throttle_state.get("lastRequestAt", 0.0))
        wait_for = min_interval - (now - last_request_at)
        if wait_for > 0:
            time.sleep(wait_for)
            waited_seconds = wait_for

        request_started = time.monotonic()
        throttle_state["lastRequestAt"] = request_started

        try:
            status, raw_body, parsed = _request_once(
                api_url=api_url,
                keyword=keyword,
                gl=args.gl,
                hl=args.hl,
                force=args.force,
                response_format=args.response_format,
                api_key=api_key,
                auth_mode=args.auth_mode,
                timeout_seconds=timeout_seconds,
            )

            attempts.append(
                {
                    "attempt": attempt_index + 1,
                    "status": "ok",
                    "httpStatus": status,
                    "waitedSeconds": round(waited_seconds, 3),
                    "response": parsed,
                }
            )

            return {
                "ok": True,
                "keyword": keyword,
                "keywordNormalized": keyword_normalized,
                "attempts": attempts,
                "response": parsed,
            }
        except RequestError as exc:
            attempts.append(
                {
                    "attempt": attempt_index + 1,
                    "status": "error",
                    "httpStatus": exc.status,
                    "errorCode": exc.code,
                    "error": str(exc),
                    "retryable": bool(exc.retryable),
                    "fatalGlobal": bool(exc.fatal_global),
                    "waitedSeconds": round(waited_seconds, 3),
                    "rawBody": exc.raw_body,
                }
            )

            if exc.fatal_global:
                return {
                    "ok": False,
                    "keyword": keyword,
                    "keywordNormalized": keyword_normalized,
                    "attempts": attempts,
                    "error": str(exc),
                    "errorCode": exc.code,
                    "httpStatus": exc.status,
                    "fatalGlobal": True,
                }

            can_retry = bool(exc.retryable and attempt_index < max_retries)
            if can_retry:
                backoff = 1.5 * (2 ** attempt_index)
                if int(exc.status or 0) == 429:
                    backoff = max(backoff, min_interval * 1.2)
                time.sleep(backoff)
                continue

            return {
                "ok": False,
                "keyword": keyword,
                "keywordNormalized": keyword_normalized,
                "attempts": attempts,
                "error": str(exc),
                "errorCode": exc.code,
                "httpStatus": exc.status,
                "fatalGlobal": False,
            }

    return {
        "ok": False,
        "keyword": keyword,
        "keywordNormalized": keyword_normalized,
        "attempts": attempts,
        "error": "未知错误",
        "errorCode": None,
        "httpStatus": None,
        "fatalGlobal": False,
    }


def _get_nested(obj: dict, *keys: str):
    current = obj
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _value_to_short_text(value, max_len: int = 80) -> str:
    if value is None:
        return "-"
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, str):
        text = value.strip()
    else:
        text = json.dumps(value, ensure_ascii=False)
    text = SPACE_RE.sub(" ", text).strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 1] + "…"


def normalize_success_row(keyword: str, response: dict) -> dict:
    row = {
        "keyword": keyword,
        "score": response.get("score"),
        "level": response.get("level"),
        "keywordType": response.get("keywordType"),
        "genericScore": response.get("genericScore"),
        "keywordVolume": response.get("keywordVolume"),
        "keywordTrend": response.get("keywordTrend"),
        "linkBudget": response.get("linkBudget"),
        "detailsCount": len(response.get("details") or []) if isinstance(response.get("details"), list) else 0,
        "cached": bool(response.get("cached")) if response.get("cached") is not None else None,
        "computedAt": response.get("computedAt"),
        "reasons": response.get("reasons") if isinstance(response.get("reasons"), list) else [],
    }
    return row


def summarize_rows(*, input_count: int, rows: List[dict], failures: List[dict]) -> dict:
    score_values = [safe_float(row.get("score")) for row in rows if row.get("score") is not None]
    cached_values = [row.get("cached") for row in rows if row.get("cached") is not None]

    level_dist: Dict[str, int] = {}
    type_dist: Dict[str, int] = {}
    for row in rows:
        level = str(row.get("level") or "未知").strip() or "未知"
        level_dist[level] = level_dist.get(level, 0) + 1

        ktype = str(row.get("keywordType") or "unknown").strip() or "unknown"
        type_dist[ktype] = type_dist.get(ktype, 0) + 1

    return {
        "inputCount": input_count,
        "successCount": len(rows),
        "failureCount": len(failures),
        "avgScore": round(sum(score_values) / len(score_values), 4) if score_values else None,
        "cachedHitRate": round(sum(1 for c in cached_values if c) / len(cached_values), 6) if cached_values else None,
        "levelDistribution": level_dist,
        "keywordTypeDistribution": type_dist,
    }


def sort_rows(rows: List[dict]) -> List[dict]:
    return sorted(
        rows,
        key=lambda row: (
            -(safe_float(row.get("score")) if row.get("score") is not None else -1),
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
    api_url: str,
    api_key_source: str,
    global_error: Optional[dict],
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
                "apiUrl": api_url,
                "gl": args.gl,
                "hl": args.hl,
                "force": int(args.force),
                "responseFormat": args.response_format,
                "authMode": args.auth_mode,
                "apiKeySource": api_key_source,
                "minIntervalSeconds": float(args.min_interval_seconds),
                "maxRetries": int(args.max_retries),
                "timeoutSeconds": int(args.timeout_seconds),
            },
            "summary": summary,
            "globalError": global_error,
            "output": {
                "reportHistoryPath": str(report_history_path),
            },
        },
        "rows": rows,
        "failures": failures,
    }


def _format_computed_at(value) -> str:
    if value is None:
        return "-"
    if isinstance(value, (int, float)):
        if value <= 0:
            return str(value)
        try:
            return datetime.fromtimestamp(float(value)).isoformat(timespec="seconds")
        except (OverflowError, OSError, ValueError):
            return str(value)
    return _value_to_short_text(value, max_len=30)


def render_report(snapshot: dict) -> str:
    meta = snapshot.get("meta") or {}
    request = meta.get("request") or {}
    summary = meta.get("summary") or {}
    output = meta.get("output") or {}

    rows = snapshot.get("rows") or []
    failures = snapshot.get("failures") or []

    result_rows: List[List[str]] = []
    for row in rows[:TOP_PREVIEW_ROWS]:
        trend_domain = _get_nested(row, "keywordTrend", "domain")
        trend_ratio = _get_nested(row, "keywordTrend", "ratio")
        trend_text = f"{_value_to_short_text(trend_domain, 20)} / {_value_to_short_text(trend_ratio, 10)}"

        target_dr = _get_nested(row, "linkBudget", "targetDr")
        link_budget_text = _value_to_short_text(target_dr, 12)

        reasons = row.get("reasons") or []
        reason_text = "；".join(_value_to_short_text(item, 40) for item in reasons[:3]) if isinstance(reasons, list) else "-"

        result_rows.append(
            [
                _value_to_short_text(row.get("keyword"), 40),
                to_display_number(row.get("score"), digits=0),
                _value_to_short_text(row.get("level"), 10),
                _value_to_short_text(row.get("keywordType"), 12),
                to_display_number(row.get("genericScore"), digits=0),
                to_display_number(row.get("keywordVolume"), digits=0),
                trend_text,
                link_budget_text,
                _value_to_short_text(row.get("cached"), 5),
                _format_computed_at(row.get("computedAt")),
                _value_to_short_text(reason_text, 100),
            ]
        )

    failure_rows: List[List[str]] = []
    for row in failures:
        failure_rows.append(
            [
                _value_to_short_text(row.get("keyword"), 40),
                str(row.get("httpStatus") or "-"),
                _value_to_short_text(row.get("errorCode"), 12),
                _value_to_short_text(row.get("error"), 80),
                str(row.get("attempts") or "-"),
            ]
        )

    lines: List[str] = []
    lines.append(f"# 哥飞KD批量查询报告（{meta.get('stamp', '-')}）")
    lines.append("")

    lines.append("## 摘要")
    lines.append("")
    lines.append(f"- 输入关键词数：{summary.get('inputCount', 0)}")
    lines.append(f"- 成功关键词数：{summary.get('successCount', 0)}")
    lines.append(f"- 失败关键词数：{summary.get('failureCount', 0)}")
    lines.append(f"- 平均 score：{to_display_number(summary.get('avgScore'))}")
    lines.append(f"- cached 命中率：{to_display_number(summary.get('cachedHitRate') * 100 if summary.get('cachedHitRate') is not None else None)}%")

    level_dist = summary.get("levelDistribution") or {}
    if isinstance(level_dist, dict) and level_dist:
        dist_text = ", ".join(f"{k}:{v}" for k, v in sorted(level_dist.items(), key=lambda x: x[0]))
        lines.append(f"- level 分布：{dist_text}")
    lines.append("")

    lines.append("## 请求参数")
    lines.append("")
    lines.append(f"- API：{request.get('apiUrl', '-')}")
    lines.append(f"- 鉴权方式：{request.get('authMode', '-')}（key 来源：{request.get('apiKeySource', '-')}）")
    lines.append(f"- gl={request.get('gl', '-')} hl={request.get('hl', '-')} force={request.get('force', '-')} format={request.get('responseFormat', '-')}")
    lines.append(f"- minIntervalSeconds={request.get('minIntervalSeconds', '-')} maxRetries={request.get('maxRetries', '-')} timeoutSeconds={request.get('timeoutSeconds', '-')}")
    lines.append("")

    lines.append("## 关键词结果明细")
    lines.append("")
    lines.extend(
        _md_table(
            [
                "keyword",
                "score",
                "level",
                "keywordType",
                "genericScore",
                "keywordVolume",
                "keywordTrend(domain/ratio)",
                "linkBudget(targetDr)",
                "cached",
                "computedAt",
                "reasons",
            ],
            result_rows,
        )
    )
    lines.append("")

    lines.append("## 失败明细")
    lines.append("")
    lines.extend(_md_table(["keyword", "status", "errorCode", "error", "attempts"], failure_rows))
    lines.append("")

    global_error = meta.get("globalError")
    if isinstance(global_error, dict) and global_error:
        lines.append("- 全局错误：")
        lines.append(f"  - status={global_error.get('httpStatus', '-')}, code={global_error.get('errorCode', '-')}, error={global_error.get('error', '-')}")
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

    api_url = args.api_base.rstrip("/") + args.endpoint

    keywords = collect_keywords(args)
    api_key, api_key_source = resolve_api_key(args)

    if args.dry_run:
        print("[dry-run] 配置检查通过，不发起网络请求。")
        print(f"[dry-run] keywords: {len(keywords)}")
        print(f"[dry-run] api: {api_url}")
        print(f"[dry-run] auth-mode: {args.auth_mode}")
        print(f"[dry-run] api-key-source: {api_key_source}")
        print(f"[dry-run] api-key(masked): {mask_secret(api_key)}")
        print(f"[dry-run] gl={args.gl} hl={args.hl} force={args.force} format={args.response_format}")
        print(f"[dry-run] min-interval={args.min_interval_seconds}s max-retries={args.max_retries}")
        return 0

    success_rows: List[dict] = []
    failures: List[dict] = []
    raw_results: List[dict] = []
    global_error: Optional[dict] = None

    throttle_state = {"lastRequestAt": 0.0}

    for item in keywords:
        keyword = item["keyword"]
        keyword_normalized = item["keywordNormalized"]

        fetch_result = fetch_keyword_with_retry(
            api_url=api_url,
            keyword=keyword,
            keyword_normalized=keyword_normalized,
            args=args,
            api_key=api_key,
            throttle_state=throttle_state,
        )
        raw_results.append(fetch_result)

        if fetch_result.get("ok"):
            success_rows.append(normalize_success_row(keyword, fetch_result.get("response") or {}))
            continue

        failure_row = {
            "keyword": keyword,
            "keywordNormalized": keyword_normalized,
            "attempts": len(fetch_result.get("attempts") or []),
            "error": str(fetch_result.get("error") or "未知错误"),
            "errorCode": fetch_result.get("errorCode"),
            "httpStatus": fetch_result.get("httpStatus"),
        }
        failures.append(failure_row)

        if fetch_result.get("fatalGlobal"):
            global_error = {
                "keyword": keyword,
                "httpStatus": fetch_result.get("httpStatus"),
                "errorCode": fetch_result.get("errorCode"),
                "error": str(fetch_result.get("error") or "未知错误"),
            }
            print(
                f"[fatal] 触发全局终止条件：keyword={keyword} status={fetch_result.get('httpStatus')} code={fetch_result.get('errorCode')}"
            )
            break

    sorted_rows = sort_rows(success_rows)
    summary = summarize_rows(input_count=len(keywords), rows=sorted_rows, failures=failures)

    stamp = now_stamp()
    placeholder_report_history_path = report_dir / f"report-{stamp}.md"
    snapshot = build_snapshot(
        stamp=stamp,
        args=args,
        keywords=keywords,
        rows=sorted_rows,
        failures=failures,
        summary=summary,
        api_url=api_url,
        api_key_source=api_key_source,
        global_error=global_error,
        report_history_path=placeholder_report_history_path,
    )

    fetch_archive = {
        "meta": {
            "generatedAt": datetime.now().isoformat(timespec="seconds"),
            "stamp": stamp,
            "summary": summary,
            "request": {
                "apiUrl": api_url,
                "gl": args.gl,
                "hl": args.hl,
                "force": int(args.force),
                "responseFormat": args.response_format,
                "authMode": args.auth_mode,
                "apiKeySource": api_key_source,
                "minIntervalSeconds": float(args.min_interval_seconds),
                "maxRetries": int(args.max_retries),
                "timeoutSeconds": int(args.timeout_seconds),
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

    if global_error:
        print(
            f"[warn] 全局错误：status={global_error.get('httpStatus')} code={global_error.get('errorCode')} error={global_error.get('error')}"
        )
        return 2

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
