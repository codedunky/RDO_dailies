import os
import json
import time
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

from config import settings
from core.logger import debug_print, BG_GREEN, BG_YELLOW, BG_RED, BG_RESET


NAME_OVERRIDES = {
    # --- Generic Challenges (id: "challenges", variation: "...") ---
    "hunting": "Wild Animal Kills",
    "headshot_kills": "Headshot Kills",
    "longarm_kills": "Longarm Kills",
    "sidearm_kills": "Sidearm Kills",
    "horseback_kills": "Horseback Kills",
    "melee_kills": "Melee Kills",
    "bow_kills": "Bow Kills",
    "fishing": "Lake Fishing Challenge",
    # --- Specific Events (id: "...") ---
    "hot_property": "Cold Dead Hands",
    "dispatch_rider": "Dispatch Rider",
    "king_of_the_castle": "King of the Castle",
    "railroad_baron": "Railroad Baron",
    "master_archer": "Master Archer",
    "wildlife_photographer": "Wildlife Photographer",
    "fool_gold": "Fool's Gold",
    # --- Role Events ---
    "legendary_bounties": "Legendary Bounty",
    "condor_egg": "Condor Egg",
    "salvage": "Salvage",
    "trade_route": "Trade Route",
    "manhunt": "Manhunt",
    "day_of_reckoning": "Day of Reckoning",
    "wild_animal_tagging": "Wild Animal Tagging",
}


def parse_events_for_js(json_file_path: Path | str) -> list[dict]:
    """Extracts and normalizes raw schedule events into the list expected by the JavaScript ticker."""
    events_list = []
    path_obj = Path(json_file_path)
    if not path_obj.exists():
        return []

    try:
        with open(path_obj, "r", encoding="utf-8") as f:
            data = json.load(f)

        target_categories = ["standard", "themed", "role"]

        for cat in target_categories:
            if cat not in data:
                continue
            schedule_dict = data[cat]

            for time_key, event_data in schedule_dict.items():
                evt_id = event_data.get("id")
                evt_var = event_data.get("variation")
                evt_alt = event_data.get("alt")

                # 1. Challenge variation
                if evt_id == "challenges" and evt_var:
                    display_name = NAME_OVERRIDES.get(evt_var, evt_var.replace("_", " ").title())
                    display_name += " Challenge"
                # 2. Known override
                elif evt_id in NAME_OVERRIDES:
                    display_name = NAME_OVERRIDES[evt_id]
                # 3. Fallbacks
                elif evt_alt:
                    display_name = evt_alt.replace("_", " ").title()
                else:
                    display_name = (evt_id or "Unknown").replace("_", " ").title()

                events_list.append({
                    "time": time_key,
                    "name": display_name,
                    "cat": cat,
                })

        return events_list
    except Exception as e:
        print(f"Error parsing events: {e}")
        return []


def sync_events() -> tuple[list[dict], str]:
    """
    Checks local events.json with Tuesday 9 AM window logic & cooldowns.
    Returns (events_list, status_events).
    """
    local_file = settings.EVENTS_JSON_PATH
    download_events = False
    status_events = f"{BG_YELLOW}EVENTS: Unknown{BG_RESET}"

    # 1. Calculate Tuesday 9am window
    now_utc = datetime.now(timezone.utc)
    today_9am = now_utc.replace(
        hour=settings.EVENTS_WINDOW_HOUR_UTC, minute=0, second=0, microsecond=0
    )
    days_since_tuesday = (now_utc.weekday() - 1) % 7
    if days_since_tuesday == 0 and now_utc < today_9am:
        days_since_tuesday = 7

    latest_window_start_dt = today_9am - timedelta(days=days_since_tuesday)
    latest_window_start_ts = latest_window_start_dt.timestamp()

    debug_print("L1", "igreen", f"EVENTS: Current Update Window started: {latest_window_start_dt}")

    # 2. Check local file
    if local_file.exists():
        try:
            last_api_check_ts = os.path.getmtime(local_file)
            with open(local_file, "r", encoding="utf-8") as f:
                existing_data = json.load(f)

            local_content_ts = existing_data.get("updated", 0)
            readable_local_date = datetime.fromtimestamp(local_content_ts)
            debug_print("L1", "igreen", f"EVENTS: Local File Internal Date: {readable_local_date}")

            if local_content_ts >= latest_window_start_ts:
                debug_print("L0", "bgreen", "EVENTS: Schedule is fully up to date.")
                status_events = f"{BG_YELLOW}EVENTS: File valid (Begins:  {readable_local_date}). Using cached json.{BG_RESET}"
                download_events = False
            else:
                checked_this_week = last_api_check_ts > latest_window_start_ts
                if not checked_this_week:
                    debug_print("L0", "idarkyellow", "EVENTS: New update window open. Downloading...")
                    download_events = True
                else:
                    current_day = now_utc.weekday()
                    # 1=Tue, 2=Wed
                    if current_day in [1, 2]:
                        time_since_check = int(time.time()) - last_api_check_ts
                        if time_since_check < settings.EVENTS_COOLDOWN_SHORT:
                            debug_print("L0", "bgreen", f"EVENTS: Update late (Tue/Wed). Keeping cache ({int(time_since_check/60)} mins old).")
                            download_events = False
                        else:
                            debug_print("L0", "idarkyellow", "EVENTS: Update late. Cooldown expired. Checking API...")
                            download_events = True
                    else:
                        debug_print("L0", "byellow", "EVENTS: Old data detected, but checked this week. (Thurs-Mon Logic)")
                        status_events = f"{BG_YELLOW}EVENTS: File valid (Begins:  {readable_local_date}). Using cached json.{BG_RESET}"
                        download_events = False
        except Exception as e:
            print(f"EVENTS: Error reading local file ({e}). Forcing download.")
            download_events = True
    else:
        debug_print("L0", "idarkyellow", "EVENTS: File not found. Downloading...")
        download_events = True

    if settings.BLOCK_DOWNLOADS and download_events:
        debug_print("L1", "bred", "EVENTS: Download skipped (BLOCK_DOWNLOADS = True).")
        download_events = False

    # 3. Perform download if needed
    if download_events:
        try:
            debug_print("L2", "igreen", "EVENTS: Downloading events.json from API...")
            req = urllib.request.Request(settings.EVENTS_URL, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                new_data = json.loads(resp.read().decode("utf-8"))

            with open(local_file, "w", encoding="utf-8") as f:
                json.dump(new_data, f, indent=2)

            print("EVENTS: Download complete.")
            status_events = f"{BG_GREEN}EVENTS: New json file downloaded successfully.{BG_RESET}"
        except Exception as e:
            print(f"EVENTS: Download failed: {e}")
            status_events = f"{BG_RED}EVENTS: New json file failed to download.{BG_RESET}"

    events_data = parse_events_for_js(local_file)
    return events_data, status_events