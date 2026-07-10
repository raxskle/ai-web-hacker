#!/usr/bin/env python3
"""Shared Gefei KD lookup helpers for standard-word exports."""

from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

DEFAULT_API_BASE = "https://seo.web.cafe"
DEFAULT_ENDPOINT = "/kd/api/v1/kd"
DEFAULT_API_KEY_ENV = "GEFEI_KD_API_KEY"
DEFAULT_API_KEY_FILE = Path(__file__).resolve().parent / "check-gefei-kd" / "api_key.txt"
REQUEST_TIMEOUT_SECONDS = 60
SPACE_RE = re.compile(r"\s+")


class RequestError(RuntimeError):
    """Request failure with retry and fatal metadata."""

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


def normalize_keyword_text(text: str) -> str:
    return SPACE_RE.sub(" ", str(text or "").strip().lower())


def read_text_required(path: Path, label: str) -> str:
    if not path.exists():
        raise RuntimeError(f"{label} 不存在: {path}")
    value = path.read_text(encoding="utf-8").strip()
    if not value:
        raise RuntimeError(f"{label} 为空: {path}")
    return value


def resolve_api_key(
    *,
    api_key: str = "",
    api_key_env: str = DEFAULT_API_KEY_ENV,
    api_key_file: Optional[str] = None,
) -> Tuple[str, str]:
    direct = str(api_key or "").strip()
    if direct:
        return direct, "--gefei-api-key"

    env_name = str(api_key_env or "").strip()
    if env_name:
        env_val = str(os.getenv(env_name) or "").strip()
        if env_val:
            return env_val, f"env:{env_name}"

    file_path = Path(api_key_file).resolve() if api_key_file else DEFAULT_API_KEY_FILE.resolve()
    return read_text_required(file_path, "哥飞 KD api_key 文件"), str(file_path)


def _extract_error_payload(parsed: Optional[dict]) -> Tuple[Optional[str], str]:
    if not isinstance(parsed, dict):
        return None, ""

    if isinstance(parsed.get("error"), dict):
        err = parsed.get("error") or {}
        code = str(err.get("code") or "").strip() or None
        msg = str(err.get("message") or "").strip()
        return code, msg

    if isinstance(parsed.get("error"), str):
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
            message or "哥飞 KD API 认证失败（auth）",
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
            message or "哥飞 KD 当日额度耗尽（quota）",
            status=status_code,
            code="quota",
            retryable=False,
            fatal_global=True,
            raw_body=raw_body,
        )

    if status_code == 429 and is_rate:
        return RequestError(
            message or "哥飞 KD 触发频率限制（rate）",
            status=status_code,
            code="rate",
            retryable=True,
            fatal_global=False,
            raw_body=raw_body,
        )

    if status_code == 400:
        return RequestError(
            message or "哥飞 KD 请求参数错误（400）",
            status=status_code,
            code=normalized_code,
            retryable=False,
            fatal_global=False,
            raw_body=raw_body,
        )

    if status_code and status_code >= 500:
        return RequestError(
            message or f"哥飞 KD 上游服务错误（{status_code}）",
            status=status_code,
            code=normalized_code,
            retryable=True,
            fatal_global=False,
            raw_body=raw_body,
        )

    return RequestError(
        message or f"哥飞 KD 请求失败（status={status_code or '-'}）",
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
        "User-Agent": "shared-gefei-kd/0.1",
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
                raise RequestError("哥飞 KD 返回 JSON 非对象", status=status, raw_body=body)
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
        raise RequestError("哥飞 KD 返回非合法 JSON", retryable=False) from exc


def fetch_keyword_with_retry(
    *,
    api_url: str,
    keyword: str,
    keyword_normalized: str,
    api_key: str,
    auth_mode: str,
    gl: str,
    hl: str,
    force: int,
    response_format: str,
    min_interval_seconds: float,
    max_retries: int,
    timeout_seconds: int,
    throttle_state: dict,
) -> dict:
    attempts: List[dict] = []

    max_retries = max(int(max_retries), 0)
    min_interval = max(float(min_interval_seconds), 0.0)
    timeout_seconds = max(int(timeout_seconds), 1)

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
                gl=gl,
                hl=hl,
                force=force,
                response_format=response_format,
                api_key=api_key,
                auth_mode=auth_mode,
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


def fetch_gefei_kd_rows(
    *,
    keywords: Sequence[str],
    api_base: str = DEFAULT_API_BASE,
    endpoint: str = DEFAULT_ENDPOINT,
    api_key: str = "",
    api_key_env: str = DEFAULT_API_KEY_ENV,
    api_key_file: Optional[str] = None,
    auth_mode: str = "header",
    gl: str = "us",
    hl: str = "en",
    force: int = 0,
    response_format: str = "json",
    min_interval_seconds: float = 6.2,
    max_retries: int = 2,
    timeout_seconds: int = REQUEST_TIMEOUT_SECONDS,
) -> dict:
    deduped_keywords: List[dict] = []
    seen: set[str] = set()
    for keyword in keywords:
        text = str(keyword or "").strip()
        normalized = normalize_keyword_text(text)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        deduped_keywords.append(
            {
                "keyword": text,
                "keywordNormalized": normalized,
            }
        )

    if not deduped_keywords:
        return {
            "api": {
                "apiUrl": api_base.rstrip("/") + endpoint,
                "authMode": auth_mode,
                "apiKeySource": None,
            },
            "rows": [],
            "failures": [],
            "summary": {
                "inputCount": 0,
                "requestCount": 0,
                "successCount": 0,
                "successWithScoreCount": 0,
                "missingScoreCount": 0,
                "failedCount": 0,
            },
            "scoreByKeyword": {},
        }

    resolved_api_key, api_key_source = resolve_api_key(
        api_key=api_key,
        api_key_env=api_key_env,
        api_key_file=api_key_file,
    )
    api_url = api_base.rstrip("/") + endpoint
    throttle_state: dict = {}
    rows: List[dict] = []
    failures: List[dict] = []
    score_by_keyword: Dict[str, Optional[float]] = {}

    for item in deduped_keywords:
        result = fetch_keyword_with_retry(
            api_url=api_url,
            keyword=item["keyword"],
            keyword_normalized=item["keywordNormalized"],
            api_key=resolved_api_key,
            auth_mode=auth_mode,
            gl=gl,
            hl=hl,
            force=force,
            response_format=response_format,
            min_interval_seconds=min_interval_seconds,
            max_retries=max_retries,
            timeout_seconds=timeout_seconds,
            throttle_state=throttle_state,
        )

        if result.get("ok"):
            response = result.get("response") or {}
            score = response.get("score")
            normalized_keyword = item["keywordNormalized"]
            score_by_keyword[normalized_keyword] = score
            rows.append(
                {
                    "keyword": item["keyword"],
                    "keywordNormalized": normalized_keyword,
                    "gefeiKD": score,
                    "level": response.get("level"),
                    "keywordType": response.get("keywordType"),
                    "genericScore": response.get("genericScore"),
                    "keywordVolume": response.get("keywordVolume"),
                    "keywordTrend": response.get("keywordTrend"),
                    "linkBudget": response.get("linkBudget"),
                    "cached": bool(response.get("cached")) if response.get("cached") is not None else None,
                    "computedAt": response.get("computedAt"),
                    "reasons": response.get("reasons") if isinstance(response.get("reasons"), list) else [],
                    "attempts": result.get("attempts") or [],
                }
            )
            continue

        failure = {
            "keyword": item["keyword"],
            "keywordNormalized": item["keywordNormalized"],
            "gefeiKD": None,
            "error": result.get("error"),
            "errorCode": result.get("errorCode"),
            "httpStatus": result.get("httpStatus"),
            "fatalGlobal": bool(result.get("fatalGlobal")),
            "attempts": result.get("attempts") or [],
        }
        score_by_keyword[item["keywordNormalized"]] = None
        rows.append(failure)
        failures.append(failure)

        if result.get("fatalGlobal"):
            raise RuntimeError(
                "哥飞 KD 查询失败："
                f"{failure.get('error') or '未知错误'}；"
                f"apiKeySource={api_key_source} apiUrl={api_url}"
            )

    success_count = len(rows) - len(failures)
    success_with_score_count = sum(1 for row in rows if row.get("gefeiKD") is not None)
    missing_score_count = success_count - success_with_score_count

    return {
        "api": {
            "apiUrl": api_url,
            "authMode": auth_mode,
            "apiKeySource": api_key_source,
        },
        "rows": rows,
        "failures": failures,
        "summary": {
            "inputCount": len(deduped_keywords),
            "requestCount": len(rows),
            "successCount": success_count,
            "successWithScoreCount": success_with_score_count,
            "missingScoreCount": missing_score_count,
            "failedCount": len(failures),
        },
        "scoreByKeyword": score_by_keyword,
    }
