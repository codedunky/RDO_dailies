import json
from datetime import datetime, timezone
from collections import defaultdict

from config import settings
from core.logger import debug_print
from core.description_picker import stable_hash, get_printable_description
from data.challenges import all_challenge_definitions


ROLE_KEYS = ["bounty_hunter", "trader", "collector", "moonshiner", "naturalist"]
ROLE_NAMES = {
    "bounty_hunter": "Bounty Hunter",
    "trader": "Trader",
    "collector": "Collector",
    "moonshiner": "Moonshiner",
    "naturalist": "Naturalist",
}

NO_DATA_HTML = """
<div class="challenge">
  <label>
    <span class="challenge-text" style="color: #d00; font-style: italic;">
      Challenge Data Missing (File Not Found)
    </span>
  </label>
  <div class="challenge-desc">Could not load index.json and download was blocked/failed.</div>
</div>
"""

NO_DATA_ROLE_HTML = """
<div class="role-challenge">
  <div class="role-challenge-text" style="color: #d00; font-style: italic;">
    Role Data Missing
  </div>
</div>
"""


def normalize_key(key: str) -> str:
    """Normalizes lookup key by uppercasing and stripping whitespace."""
    return key.strip().upper()


def extract_challenges_with_roles(index_data: dict) -> list[dict]:
    """Extracts general and role challenges across easy, med, hard from raw index.json."""
    combined = []
    if not index_data:
        return []

    # General challenges
    for challenge in index_data.get("general", []):
        combined.append({**challenge, "role": "general", "difficulty": None})

    # Role challenges across difficulty tiers
    for difficulty in ["easy", "med", "hard"]:
        difficulty_data = index_data.get(difficulty, {})
        for role, challenges in difficulty_data.items():
            for challenge in challenges:
                combined.append({**challenge, "role": role, "difficulty": difficulty})

    return combined


def build_final_challenge_list(index_data: dict, start_timestamp: int) -> list[dict]:
    """Merges dynamic index.json challenges with static descriptions and categories."""
    detail_lookup = {
        normalize_key(ch["key"]): ch
        for ch in all_challenge_definitions
    }

    indexed_challenges = extract_challenges_with_roles(index_data)
    final_list = []

    for ch in indexed_challenges:
        title_upper = normalize_key(ch["title"])
        details = detail_lookup.get(title_upper, {})

        entry = {
            "name": None,
            **details,
            "title": ch["title"],
            "goal": ch["goal"],
            "category": ch["role"],
            "difficulty": ch["difficulty"],
            "showgoal": details.get("showgoal", "n"),
        }
        final_list.append(entry)

    return final_list


def render_challenge_block(block: list[dict], prefix="challenge", role_name="", filter_difficulty="hard", start_date_str=""):
    """Renders HTML for a list of challenges, with checkboxes, descriptions, and cycle buttons."""
    html = ""

    if prefix == "role-challenge":
        role_id = "role-" + "".join(c.lower() if c.isalnum() else "-" for c in role_name).strip("-")
        html += '<div class="role-container">\n'
        html += f'  <h3 class="role-heading" id="{role_id}">{role_name}&nbsp; '
        diff_label = (
            "Rank 1–5" if filter_difficulty == "easy"
            else "Rank 6–14" if filter_difficulty == "med"
            else "Rank 15+"
        )
        html += (
            f'<span class="difficulty-toggle RDOFont" data-difficulty="{filter_difficulty}">'
            f'({filter_difficulty.capitalize()}: {diff_label})</span></h3>\n'
        )

    for c in block:
        safe_id = f"{prefix}_{start_date_str}_{stable_hash(c['text'])}"
        label_class = 'role-challenge-label' if prefix == 'role-challenge' else ''
        label_open = f'<label class="{label_class}">' if label_class else '<label>'
        difficulty = c.get("difficulty", "easy")
        desc_id = f"desc_{safe_id}"

        label_style = ' style="flex-grow: 1; margin-right: 15px;"'
        label_open_mod = label_open.replace('>', f'{label_style}>')

        html += f"""
        <div class="{prefix}" data-difficulty="{difficulty}">
          <div style="display: flex; justify-content: space-between; align-items: flex-start; width: 100%; position: relative;">
            {label_open_mod}
              <input type="checkbox" class="challenge-checkbox" id="{safe_id}" />
              <span class="{prefix}-text">{c["text"]}</span>
            </label>"""

        all_descs = c.get("all_descriptions", [])
        desc_loop = c.get("desc_loop", "yes")

        if len(all_descs) > 1 and desc_loop != "no":
            safe_json = json.dumps(all_descs).replace('"', '&quot;')
            desc_idx = c.get("desc_index", 0)
            html += (
                f'<span class="desc-cycle-btn" data-descs="{safe_json}" data-idx="{desc_idx}" '
                f'data-target="{desc_id}" onclick="cycleDesc(event, this)" title="Cycle Description">↻</span>'
            )

        html += '</div>\n'

        if c.get("description"):
            html += f'          <div id="{desc_id}" class="{prefix}-desc">{c["description"]}</div>'

        html += '</div>\n'

    if prefix == "role-challenge":
        html += '</div>\n'

    return html


def render_general_challenges_with_dividers(general_challenges: list[dict], start_date_str: str) -> str:
    """Renders general challenges with horizontal line dividers between them."""
    html = ""
    for i, challenge in enumerate(general_challenges):
        block_html = render_challenge_block([challenge], prefix="challenge", start_date_str=start_date_str)
        html += block_html
        if i < len(general_challenges) - 1:
            html += '<hr class="thin-divider">\n'
    return html


def generate_role_html_for_difficulty(challenges: list[dict], filter_difficulty: str, start_date_str: str) -> str:
    """Renders all role containers for a specified difficulty level."""
    grouped_by_role = defaultdict(list)
    for c in challenges:
        grouped_by_role[c["category"]].append(c)

    html_roles = ""
    roles_with_challenges = [role for role in ROLE_KEYS if role in grouped_by_role and grouped_by_role[role]]

    for idx, role in enumerate(roles_with_challenges):
        block = grouped_by_role[role]
        html_roles += render_challenge_block(
            block,
            prefix="role-challenge",
            role_name=ROLE_NAMES.get(role, role.title()),
            filter_difficulty=filter_difficulty,
            start_date_str=start_date_str,
        )
        if idx < len(roles_with_challenges) - 1:
            html_roles += '<hr class="thin-divider" />\n'

    return html_roles


def process_challenges(index_data: dict, start_timestamp: int) -> tuple[str, str, list[dict]]:
    """
    Main processing pipeline:
      1. Merges raw index data with static challenge descriptions.
      2. Chooses rotating descriptions.
      3. Dumps 'final_challenges_output2.json'.
      4. Returns (html_general, selected_html_roles, final_view_challenges).
    """
    start_date_str = datetime.fromtimestamp(start_timestamp, timezone.utc).strftime("%Y-%m-%d")
    raw_list = build_final_challenge_list(index_data, start_timestamp)

    if not raw_list:
        return NO_DATA_HTML, NO_DATA_ROLE_HTML, []

    category_order = ["general", "bounty_hunter", "trader", "collector", "moonshiner", "naturalist"]
    difficulty_order = [None, "easy", "med", "hard"]

    output_json = []
    grouped_json = defaultdict(lambda: defaultdict(list))
    for item in raw_list:
        grouped_json[item["category"]][item["difficulty"]].append(item)

    for category in category_order:
        for difficulty in difficulty_order:
            items = grouped_json.get(category, {}).get(difficulty, [])
            for item in sorted(items, key=lambda x: x["name"] or x["title"]):
                showgoal = str(item.get("showgoal", "")).strip().lower()

                if showgoal == "no":
                    goal_display = ""
                elif showgoal == "yes":
                    goal_display = f"{item['goal']} "
                else:
                    if isinstance(item.get("goal"), (int, float)) and item["goal"] > 1:
                        goal_display = f"{item['goal']} "
                    else:
                        goal_display = ""

                chosen_desc, all_descs, start_idx = get_printable_description(item, start_timestamp)

                output_json.append({
                    "text": f"{goal_display}{item['name'] or item['title']}",
                    "description": chosen_desc,
                    "all_descriptions": all_descs,
                    "desc_index": start_idx,
                    "desc_loop": str(item.get("desc_loop", "yes")).lower(),
                    "category": category,
                    "difficulty": difficulty,
                })

    # Save intermediate debug JSON matching original behavior
    try:
        with open(settings.DEBUG_JSON_OUTPUT_PATH, "w", encoding="utf-8") as f:
            json.dump({"final_name": output_json}, f, indent=2)
    except Exception as e:
        debug_print("L1", "bred", f"Error writing debug challenges JSON: {e}")

    # Build General HTML
    general_challenges = [c for c in output_json if c["category"] == "general"]
    html_general = render_general_challenges_with_dividers(general_challenges, start_date_str)

    # Build Role HTML
    selected_html_roles = generate_role_html_for_difficulty(
        output_json, settings.FILTER_DIFFICULTY, start_date_str
    )

    return html_general, selected_html_roles, output_json