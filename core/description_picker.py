import hashlib
from config import settings
from core.logger import debug_print


def stable_hash(text: str) -> str:
    """Generates a stable 16-character SHA-256 hash used for unique checkbox IDs."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def get_printable_description(details: dict, start_timestamp: int) -> tuple[str | None, list[str], int]:
    """
    Dynamically collects all available descriptions for a challenge.
    Selects one based on deterministic rotation or dynamic 'forceX' flags.
    Appends [#X] if DEBUG_DESCRIPTION is True and more than one description exists.
    """
    # 1. Collect all descriptions (description, description2, description3, ...)
    options = []
    if details.get("description"):
        options.append(details["description"])

    i = 2
    while True:
        key = f"description{i}"
        val = details.get(key)
        if val:
            options.append(val)
            i += 1
        else:
            break

    if not options:
        return None, [], 0

    count = len(options)
    selection_index = 0

    # 2. Determine selection index
    mode = settings.DESCRIPTION_MODE
    if mode.startswith("force"):
        try:
            num_str = mode.replace("force", "")
            if num_str.isdigit():
                target_index = int(num_str) - 1
                selection_index = max(0, min(target_index, count - 1))
            else:
                selection_index = 0
        except Exception:
            selection_index = 0
    else:
        challenge_name = details.get("name") or details.get("title") or "unknown"
        name_hash = int(hashlib.md5(challenge_name.encode("utf-8")).hexdigest(), 16)
        day_id = int(start_timestamp / 86400)
        selection_index = (day_id + name_hash) % count

    # 3. Pre-process options (append debug [#X] tag if applicable)
    processed_options = []
    for idx, opt in enumerate(options):
        text = opt
        if settings.DEBUG_DESCRIPTION and count > 1:
            text += f" [#{idx + 1}]"
        processed_options.append(text)

    final_text = processed_options[selection_index]
    debug_print(
        "L3",
        f"Rotator: '{details.get('name')}' selected index {selection_index} ({selection_index+1}/{count})"
    )

    return final_text, processed_options, selection_index