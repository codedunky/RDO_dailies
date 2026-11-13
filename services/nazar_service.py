import json
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from config import settings
from core.logger import debug_print, BG_GREEN, BG_YELLOW, BG_RED, BG_RESET
from services.time_utils import get_current_rdo_window, timestamp_to_date


def prettify_nazar_key(key: str) -> str:
    """Formats location key for display (e.g., 'macfarlanes_ranch' -> 'MacFarlane\'s Ranch')."""
    if not key or not isinstance(key, str):
        return "Unknown"
    parts = key.lower().split("_")
    if len(parts) > 2 and len(parts[0]) == 1 and parts[1].isdigit():
        clean_parts = parts[2:]
    else:
        clean_parts = parts
    clean_key = "_".join(clean_parts)

    NAZAR_OVERRIDES = {
        "ocreaghs_run": "O'Creagh's Run",
        "macfarlanes_ranch": "MacFarlane's Ranch",
    }
    if clean_key in NAZAR_OVERRIDES:
        return NAZAR_OVERRIDES[clean_key]
    return " ".join(word.title() for word in clean_parts)


def normalize_nazar_payload(raw: dict) -> dict | None:
    """Ensures consistent schema regardless of data provider."""
    if not isinstance(raw, dict):
        return None
    data_block = raw.get("data", raw)

    start_time = data_block.get("startTime", raw.get("startTime", 0))
    end_time = data_block.get("endTime", raw.get("endTime", 0))
    if not end_time:
        start_time, end_time = get_current_rdo_window()

    return {
        "updated": raw.get("updated", int(time.time())),
        "startTime": start_time,
        "endTime": end_time,
        "state": data_block.get("state", raw.get("state", "unknown_state")),
        "location": data_block.get("location", raw.get("location", "unknown_location")),
        "near": data_block.get("near", raw.get("near", "")),
    }


def sync_nazar() -> tuple[dict, str]:
    """
    Checks local nazar.json cache, downloads update if expired,
    verifies map, zoom, and photo images on disk, and returns view model dictionary.
    """
    local_file = settings.NAZAR_JSON_PATH
    now = int(time.time())
    nazar_data = {}
    download_nazar = False
    valid_data = False

    if local_file.exists():
        try:
            with open(local_file, "r", encoding="utf-8") as f:
                nazar_data = json.load(f)
            end_time = nazar_data.get("endTime", 0)
            if end_time < now:
                debug_print("L1", "idarkyellow", "NAZAR: Nazar file expired. Downloading...")
                download_nazar = True
            else:
                valid_data = True
                readable = timestamp_to_date(end_time)
                debug_print("L1", "byellow", f"NAZAR: File valid (Expires: {readable}). Using cached json.")
                status_nazar = f"{BG_YELLOW}NAZAR:  File valid (Expires: {readable}). Using cached json.{BG_RESET}"
        except Exception:
            download_nazar = True
    else:
        download_nazar = True

    if settings.BLOCK_DOWNLOADS and download_nazar:
        debug_print("L1", "ired", "NAZAR: Download skipped (BLOCK_DOWNLOADS = True).")
        download_nazar = False

    if download_nazar:
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        downloaded = None
        stale_backup = None

        # 1. Primary rdo.gg
        try:
            print("NAZAR: Attempting download from api.rdo.gg...")
            url = f"{settings.PRIMARY_NAZAR_URL}?nocache={today_str}"
            req = urllib.request.Request(url, headers=settings.DEFAULT_HEADERS)
            with urllib.request.urlopen(req, timeout=10) as resp:
                candidate = normalize_nazar_payload(json.loads(resp.read().decode("utf-8")))
                if candidate and candidate.get("endTime", 0) > now:
                    downloaded = candidate
                    print("NAZAR: SUCCESS: Retrieved up-to-date data from api.rdo.gg!")
                else:
                    stale_backup = candidate
        except Exception as e:
            print(f"NAZAR: api.rdo.gg download failed: {e}")

        # 2. Fallbacks
        if not downloaded:
            for fb_url in settings.FALLBACK_NAZAR_URLS:
                try:
                    print(f"NAZAR: Falling back to {fb_url}...")
                    url = f"{fb_url}?nocache={today_str}"
                    req = urllib.request.Request(url, headers=settings.DEFAULT_HEADERS)
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        raw = json.loads(resp.read().decode("utf-8"))
                        candidate = normalize_nazar_payload(raw)
                        if candidate and candidate.get("location") != "unknown_location":
                            if candidate.get("endTime", 0) > now:
                                downloaded = candidate
                                print("NAZAR: SUCCESS from rdo-dailies.com!")
                                break
                            else:
                                stale_backup = stale_backup or candidate
                except Exception as e:
                    print(f"NAZAR: Fallback failed: {e}")

        if not downloaded and stale_backup:
            downloaded = stale_backup

        if downloaded:
            try:
                with open(local_file, "w", encoding="utf-8") as f:
                    json.dump(downloaded, f, indent=2)
                nazar_data = downloaded
                valid_data = True
                status_nazar = f"{BG_GREEN}NAZAR:  New json file downloaded successfully.{BG_RESET}"
            except Exception as e:
                status_nazar = f"{BG_RED}NAZAR:  Error Saving.{BG_RESET}"
        else:
            status_nazar = f"{BG_RED}NAZAR:  Error Downloading.{BG_RESET}"

    # Build view attributes
    placeholder = settings.NAZAR_PLACEHOLDER_REL
    if valid_data:
        raw_state = nazar_data.get("state", "unknown_state")
        raw_location = nazar_data.get("location", "unknown_location")
        location_text = prettify_nazar_key(raw_location)

        img_filename = f"RDO_Nazar___{raw_state}___{raw_location}.png"
        zoom_filename = f"RDO_Nazar___{raw_state}___{raw_location}___zoom.png"
        photo_filename = f"RDO_Nazar___{raw_state}___{raw_location}___photo1.png"

        abs_img = settings.NAZAR_IMAGES_DIR / img_filename
        abs_zoom = settings.NAZAR_IMAGES_DIR / zoom_filename
        abs_photo = settings.NAZAR_IMAGES_DIR / photo_filename

        final_img_src = f"HTML/images/nazar/{img_filename}" if abs_img.exists() else placeholder
        zoom_src = f"HTML/images/nazar/{zoom_filename}" if abs_zoom.exists() else ""
        photo_src = f"HTML/images/nazar/{photo_filename}" if abs_photo.exists() else ""

        has_zoom = "true" if (abs_zoom.exists() or abs_photo.exists()) else "false"
        cursor_style = "pointer" if has_zoom == "true" else "default"
    else:
        location_text = "Location Unknown"
        final_img_src = placeholder
        zoom_src = ""
        photo_src = ""
        has_zoom = "false"
        cursor_style = "default"

    view_model = {
        "location_text": location_text,
        "final_img_src": final_img_src,
        "zoom_src": zoom_src,
        "photo_src": photo_src,
        "has_zoom": has_zoom,
        "cursor_style": cursor_style,
        "placeholder_path": placeholder,
    }
    return view_model, status_nazar