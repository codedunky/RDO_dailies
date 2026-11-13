import os
import json
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from config import settings
from core.logger import debug_print


def get_current_rdo_window() -> tuple[int, int]:
    """
    Returns (start_timestamp, end_timestamp) for the 06:00 UTC daily reset cycle.
    """
    now = datetime.now(timezone.utc)
    today_reset = now.replace(
        hour=settings.RDO_RESET_HOUR_UTC,
        minute=0,
        second=0,
        microsecond=0
    )
    if now < today_reset:
        start_dt = today_reset - timedelta(days=1)
    else:
        start_dt = today_reset

    start_time = int(start_dt.timestamp())
    end_time = start_time + 86399  # 23 hours, 59 minutes, 59 seconds
    return start_time, end_time


def timestamp_to_date(timestamp: int | float) -> str:
    """Converts a unix timestamp to 'YYYY-MM-DD HH:MM:SS' format."""
    if not timestamp:
        return "Unknown"
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


def get_index_start_date(file_path: Path | str = settings.INDEX_JSON_PATH) -> tuple[int, str]:
    """
    Reads the index JSON file and returns (startTime, 'YYYY-MM-DD').
    Defaults to current time if missing.
    """
    now = int(time.time())
    date_str = datetime.fromtimestamp(now, timezone.utc).strftime("%Y-%m-%d")

    path_obj = Path(file_path)
    if not path_obj.exists():
        return now, date_str

    try:
        with open(path_obj, "r", encoding="utf-8") as f:
            data = json.load(f)
        start_time = data.get("startTime")
        if start_time:
            dt = datetime.fromtimestamp(start_time, timezone.utc)
            return start_time, dt.strftime("%Y-%m-%d")
        return now, date_str
    except Exception as e:
        debug_print("L1", "bred", f"Error reading existing index.json: {e}")
        return now, date_str


def get_human_readable_date(unix_timestamp: int | float | None = None) -> str:
    """
    Produces formatted banner date with correct English ordinal suffix:
    e.g., 'Friday, 13th November 2026'
    """
    if unix_timestamp is None:
        unix_timestamp, _ = get_index_start_date(settings.INDEX_JSON_PATH)

    dt = datetime.fromtimestamp(unix_timestamp)
    day = dt.day
    month = dt.strftime("%B")
    year = dt.year
    weekday = dt.strftime("%A")

    if 11 <= day <= 13:
        suffix = "th"
    else:
        last_digit = day % 10
        if last_digit == 1:
            suffix = "st"
        elif last_digit == 2:
            suffix = "nd"
        elif last_digit == 3:
            suffix = "rd"
        else:
            suffix = "th"

    return f"{weekday}, {day}{suffix} {month} {year}"


def get_index_mod_date_str(file_path: Path | str = settings.INDEX_JSON_PATH) -> str:
    """Returns local file modification date string for cache validation."""
    path_obj = Path(file_path)
    if not path_obj.exists():
        return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    try:
        mod_timestamp = os.path.getmtime(path_obj)
        dt = datetime.fromtimestamp(mod_timestamp)
        return dt.strftime("%Y-%m-%d_%H-%M-%S")
    except Exception as e:
        debug_print("L1", "bred", f"Error getting modification time: {e}")
        return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")