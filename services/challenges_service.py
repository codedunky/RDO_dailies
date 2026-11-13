import os
import json
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from config import settings
from core.logger import debug_print, BG_GREEN, BG_YELLOW, BG_RED, BG_RESET
from services.time_utils import get_current_rdo_window, timestamp_to_date


def convert_rdodailies_to_index_format(raw_json: dict) -> dict:
    """Converts rdo-dailies.com API structure into the rdo.gg index.json format."""
    data_root = raw_json.get("data", {})
    general_root = data_root.get("general", {})

    start_time = general_root.get("startTime", 0)
    end_time = general_root.get("endTime", 0)
    if not start_time:
        start_time, end_time = get_current_rdo_window()

    output = {
        "updated": int(time.time()),
        "startTime": start_time,
        "endTime": end_time,
        "general": [],
        "easy": {"bounty_hunter": [], "trader": [], "collector": [], "moonshiner": [], "naturalist": []},
        "med": {"bounty_hunter": [], "trader": [], "collector": [], "moonshiner": [], "naturalist": []},
        "hard": {"bounty_hunter": [], "trader": [], "collector": [], "moonshiner": [], "naturalist": []},
        "meta": {
            "documentation": "https://rdo-dailies.com",
            "provider": "rdo-dailies.com",
            "special_thanks": [],
        },
    }

    def format_challenge(ch):
        desc = ch.get("description", {})
        disp_type = ch.get("displayType", "")
        disp_format = desc.get("formatLabel", "ACMP_DC_PLAYER_MENU")
        desired = ch.get("desiredGoal", 1)

        # 1. Timed objectives / booleans
        if disp_type in ["DISPLAY_AS_BOOL", "DISPLAY_MS_TO_MINUTES"] or disp_format in [
            "ACMP_DC_PLAYER_MENU_BOOL",
            "ACMP_DC_PLAYER_MENU_TIMED",
        ]:
            goal = 1
        # 2. Distance in meters to feet
        elif disp_type == "DISPLAY_FEET" or disp_format == "ACMP_DC_PLAYER_MENU_FEET":
            goal = int(round(desired / 0.3048))
            if goal == 5281:
                goal = 5280
        # 3. Cash
        elif disp_type == "DISPLAY_CASH":
            goal = f"${desired / 100:.2f}"
        # 4. Standard counts
        else:
            goal = int(desired) if isinstance(desired, (int, float)) else desired

        return {
            "id": ch.get("id", ""),
            "title": desc.get("label", ch.get("id", "")),
            "goal": goal,
            "goalFormat": "ACMP_DC_PLAYER_MENU",
        }

    for ch in general_root.get("challenges", []):
        output["general"].append(format_challenge(ch))

    role_map = {
        "CHARACTER_RANK_BOUNTY_HUNTER": "bounty_hunter",
        "CHARACTER_RANK_TRADER": "trader",
        "CHARACTER_RANK_COLLECTOR": "collector",
        "CHARACTER_RANK_MOONSHINER": "moonshiner",
        "CHARACTER_RANK_NATURALIST": "naturalist",
    }

    for tier in ["easy", "med", "hard"]:
        tier_groups = data_root.get(tier, [])
        for group in tier_groups:
            role_key = role_map.get(group.get("role"))
            if role_key:
                for ch in group.get("challenges", []):
                    output[tier][role_key].append(format_challenge(ch))

    return output


def sync_challenges() -> tuple[dict, str]:
    """
    Checks local index.json cache. Downloads from primary (rdo.gg) or backup (rdo-dailies.com)
    if expired. Returns (index_data, status_string).
    """
    settings.JSON_DIR.mkdir(parents=True, exist_ok=True)
    local_file = settings.INDEX_JSON_PATH
    file_exists = local_file.exists()

    index_data = {}
    now = int(time.time())
    start_time = 0
    end_time = 0

    if file_exists:
        try:
            with open(local_file, "r", encoding="utf-8") as f:
                index_data = json.load(f)
            end_time = index_data.get("endTime", 0)
            start_time = index_data.get("startTime", 0)
        except Exception:
            pass

    expiry_readable = timestamp_to_date(end_time)
    status_index = f"{BG_YELLOW}INDEX:  File valid (Expires: {expiry_readable}). Using cached json.{BG_RESET}"

    if end_time < now:
        debug_print("L1", "idarkyellow", f"INDEX: File expired (Expires: {expiry_readable}). Downloading new file...")
        status_index = f"{BG_GREEN}INDEX:  New json file downloaded successfully.{BG_RESET}"
        if file_exists and not settings.AUTO_DOWNLOAD:
            user_input = input("INDEX: Do you want to download the latest index.json? (y/n): ").strip().lower()
            download_now = user_input == "y"
        else:
            download_now = True
    else:
        debug_print("L1", "byellow", f"INDEX: File valid (Expires: {expiry_readable}). Using cached json.")
        download_now = False

    if settings.BLOCK_DOWNLOADS and download_now:
        debug_print("L1", "bred", "INDEX: Download skipped (BLOCK_DOWNLOADS = True).")
        download_now = False

    if download_now:
        # Backup existing file if valid start_time
        if file_exists and start_time != 0:
            settings.BACKUP_INDEX_DIR.mkdir(parents=True, exist_ok=True)
            backup_date = datetime.fromtimestamp(start_time, timezone.utc).strftime("%Y-%m-%d")
            backup_path = settings.BACKUP_INDEX_DIR / f"index_{backup_date}.json"
            try:
                os.replace(local_file, backup_path)
                debug_print("L2", "igreen", f"Backed up old index.json to: {backup_path}")
            except Exception as e:
                debug_print("L1", "ired", f"Failed to backup old file: {e}")

        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        downloaded_data = None
        stale_backup_data = None

        # Step 1: Primary provider (rdo.gg)
        try:
            print("Attempting to download from rdo.gg...")
            url = f"{settings.PRIMARY_CHALLENGES_URL}?nocache={today_str}"
            req = urllib.request.Request(url, headers=settings.DEFAULT_HEADERS)
            with urllib.request.urlopen(req, timeout=10) as resp:
                candidate = json.loads(resp.read().decode("utf-8"))
                if candidate.get("endTime", 0) > now:
                    downloaded_data = candidate
                    print("SUCCESS: Retrieved up-to-date data from rdo.gg!")
                else:
                    stale_backup_data = candidate
                    print(f"rdo.gg returned outdated data (endTime: {timestamp_to_date(candidate.get('endTime', 0))}).")
        except Exception as e:
            print(f"rdo.gg failed: {e}")

        # Step 2: Fallback provider (rdo-dailies.com)
        if not downloaded_data:
            try:
                print("Falling back to rdo-dailies.com...")
                url = f"{settings.FALLBACK_CHALLENGES_URL}?nocache={today_str}"
                req = urllib.request.Request(url, headers=settings.DEFAULT_HEADERS)
                with urllib.request.urlopen(req, timeout=10) as resp:
                    raw = json.loads(resp.read().decode("utf-8"))
                    candidate = convert_rdodailies_to_index_format(raw)
                    if candidate.get("endTime", 0) > now:
                        downloaded_data = candidate
                        print("SUCCESS: Retrieved and converted up-to-date data from rdo-dailies.com!")
                    else:
                        stale_backup_data = stale_backup_data or candidate
            except Exception as e:
                print(f"rdo-dailies.com fallback failed: {e}")

        # Step 3: Best available fallback
        if not downloaded_data and stale_backup_data:
            print("WARNING: Both sources returned outdated data; using best available fallback.")
            downloaded_data = stale_backup_data

        # Step 4: Save
        if downloaded_data:
            try:
                with open(local_file, "w", encoding="utf-8") as f:
                    json.dump(downloaded_data, f, indent=2)
                index_data = downloaded_data
                print(f"Saved new index.json to {local_file}")
            except Exception as e:
                print(f"Error saving to {local_file}: {e}")
        else:
            print("CRITICAL: Failed to get daily challenges from all providers.")

    end_time = index_data.get("endTime", 0)
    status_index += f" - (endTime: {timestamp_to_date(end_time)})"
    return index_data, status_index