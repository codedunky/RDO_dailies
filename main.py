import json
import time
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

from config import settings
from core.logger import debug_print
from services.time_utils import get_index_start_date, get_human_readable_date
from services.challenges_service import sync_challenges
from services.nazar_service import sync_nazar
from services.events_service import sync_events
from core.processor import process_challenges


def main():
    start_time_bench = time.time()

    print(f"Initial 'local_filename':       {settings.INDEX_JSON_PATH}")
    print(f"Initial 'local_filename_nazar': {settings.NAZAR_JSON_PATH}\n")

    # 1. Ingestion: Sync API data caches
    index_data, status_index = sync_challenges()
    nazar_view, status_nazar = sync_nazar()
    events_data, status_events = sync_events()

    # Small pause matching original console flow to show download messages
    time.sleep(1)

    # 2. Time & Date resolution
    start_timestamp, _ = get_index_start_date(settings.INDEX_JSON_PATH)
    human_readable_date = get_human_readable_date(start_timestamp)
    print(f"\nTarget Date: {human_readable_date}")

    # 3. Processing: Merge API data, apply description rotation, format HTML
    html_general, selected_html_roles, _ = process_challenges(index_data, start_timestamp)

    # 4. Rendering: Populate Jinja2 template
    env = Environment(loader=FileSystemLoader(str(settings.TEMPLATES_DIR)))
    template = env.get_template("index.html.jinja")

    rendered_html = template.render(
        human_readable_date=human_readable_date,
        html_general=html_general,
        selected_html_roles=selected_html_roles,
        nazar=nazar_view,
        manual_streak=settings.MANUAL_STREAK,
        start_timestamp=start_timestamp,
        enable_js_debug=settings.ENABLE_JS_DEBUG,
        events_json=json.dumps(events_data),
    )

    # 5. Output: Write the final index.html
    with open(settings.HTML_OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(rendered_html)

    print(f"\nHTML output written to {settings.HTML_OUTPUT_PATH.name}")
    print(status_index)
    print(status_nazar)
    print(status_events)

    elapsed = time.time() - start_time_bench
    debug_print("L1", "bgreen", f"Build finished in {elapsed:.2f}s")


if __name__ == "__main__":
    main()