#!/usr/bin/env python3
"""Daily attendance check-in script for the student portal."""

from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from urllib import error, request
from zoneinfo import ZoneInfo


DEFAULT_BASE_URL = "http://121.40.111.236:3033/api"
DEFAULT_TIMEZONE = "Asia/Shanghai"
DEFAULT_TIMEOUT = 30
DEFAULT_STUDENT_NO = "202337057"
DEFAULT_PASSWORD = "殷祥凯"


class CheckinError(RuntimeError):
    """Raised when the check-in flow cannot be completed safely."""


@dataclass
class Config:
    base_url: str
    student_no: str
    password: str
    timezone: str
    timeout: int = DEFAULT_TIMEOUT


def env_or_default(name: str, default: str) -> str:
    value = os.getenv(name)
    if value is None:
        return default
    value = value.strip()
    return value or default


def load_config() -> Config:
    base_url = env_or_default("CHECKIN_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    student_no = env_or_default("CHECKIN_STUDENT_NO", DEFAULT_STUDENT_NO)
    password = env_or_default("CHECKIN_PASSWORD", DEFAULT_PASSWORD)
    timezone = env_or_default("CHECKIN_TIMEZONE", DEFAULT_TIMEZONE)

    return Config(
        base_url=base_url,
        student_no=student_no,
        password=password,
        timezone=timezone,
    )


def now_in_timezone(timezone_name: str) -> datetime:
    try:
        tz = ZoneInfo(timezone_name)
    except Exception as exc:
        raise CheckinError(f"Invalid timezone: {timezone_name}") from exc
    return datetime.now(tz)


def api_request(
    config: Config,
    method: str,
    path: str,
    payload: dict[str, Any] | None = None,
    token: str | None = None,
) -> dict[str, Any]:
    url = f"{config.base_url}{path}"
    body = None
    headers = {
        "Accept": "application/json",
    }
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = request.Request(url=url, data=body, method=method.upper(), headers=headers)
    try:
        with request.urlopen(req, timeout=config.timeout) as resp:
            raw = resp.read().decode("utf-8")
    except error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace").strip()
        raise CheckinError(f"HTTP {exc.code} for {path}: {details or exc.reason}") from exc
    except error.URLError as exc:
        raise CheckinError(f"Network error for {path}: {exc.reason}") from exc

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise CheckinError(f"Non-JSON response from {path}: {raw[:200]}") from exc

    if not isinstance(data, dict):
        raise CheckinError(f"Unexpected response shape from {path}: {type(data).__name__}")

    code = data.get("code")
    if code != 200:
        raise CheckinError(f"API error for {path}: {data.get('message', 'unknown error')}")
    return data


def login(config: Config) -> str:
    response = api_request(
        config,
        "POST",
        "/auth/login",
        payload={
            "student_no": config.student_no,
            "password": config.password,
        },
    )
    payload = response.get("data")
    if not isinstance(payload, dict):
        raise CheckinError("Login response is missing data")

    token = payload.get("token")
    if not token or not isinstance(token, str):
        raise CheckinError("Login response did not include a valid token")

    print("登录成功")
    return token


def is_checked_in_today(status_data: Any) -> bool:
    if not status_data:
        return False
    if not isinstance(status_data, dict):
        return False
    return bool(status_data.get("status") or status_data.get("attendance_time"))


def get_today_status(config: Config, token: str) -> dict[str, Any] | None:
    response = api_request(config, "GET", "/attendance/today-status", token=token)
    payload = response.get("data")
    if payload is None:
        return None
    if not isinstance(payload, dict):
        raise CheckinError("Today status response had unexpected data")
    return payload


def submit_checkin(config: Config, token: str) -> dict[str, Any]:
    response = api_request(
        config,
        "POST",
        "/attendance/check-in",
        payload={"status": "在校"},
        token=token,
    )
    payload = response.get("data")
    if payload is not None and not isinstance(payload, dict):
        raise CheckinError("Check-in response had unexpected data")
    return payload or {}


def main() -> int:
    try:
        config = load_config()
        now = now_in_timezone(config.timezone)
        print(f"开始执行打卡: {now.strftime('%Y-%m-%d %H:%M:%S %Z')}")

        token = login(config)
        today_status = get_today_status(config, token)

        if is_checked_in_today(today_status):
            status = today_status.get("status", "未知状态")
            time_text = today_status.get("attendance_time", "未知时间")
            print(f"今日已存在记录: {status} @ {time_text}")
            return 0

        result = submit_checkin(config, token)
        status = result.get("status", "在校")
        time_text = result.get("attendance_time", "时间未返回")
        print(f"已打卡: {status} @ {time_text}")
        return 0
    except CheckinError as exc:
        print(f"打卡失败: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
