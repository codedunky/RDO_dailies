# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
import datetime
import time

import inspect
import textwrap
import os
import io
import sys
from typing import Any

# Set a variable to control if index.json will download without user prompt
autoDownload = True

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#



#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
# DEBUG_PRINT
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# ANSI escape codes for different colors used by debug_print
COLORS = {
    "ireset":          "\033[0m",
    "idarkred":        "\033[31m",
    "idarkgreen":      "\033[32m",
    "idarkyellow":     "\033[33m",
    "idarkblue":       "\033[34m",
    "idarkpurple":     "\033[35m",
    "idarkcyan":       "\033[36m",
    "iblack":          "\033[90m",
    "ired":            "\033[91m",
    "igreen":          "\033[92m",
    "iyellow":         "\033[93m",
    "iblue":           "\033[94m",
    "ipurple":        "\033[95m",
    "icyan":           "\033[96m",
    "iwhite":          "\033[97m",
    "bblack":          "\033[40m",
    "bred":            "\033[41m",
    "bgreen":          "\033[42m",
    "byellow":         "\033[43m\033[30m",
    "bblue":           "\033[44m",
    "bpurple":         "\033[45m",
    "bcyan":           "\033[46m",
    "bwhite":          "\033[47m\033[30m",
    "bRESET":          "\033[49m",
    "bbrightblack":    "\033[100m",
    "bbrightred":      "\033[101m",
    "bbrightgreen":    "\033[102m",
    "bbrightyellow":   "\033[103m",
    "bbrightblue":     "\033[104m",
    "bbrightpurple":   "\033[105m",
    "bbrightcyan":     "\033[106m\033[30m",
    "bbrightwhite":    "\033[107m\033[30m"
}

# Current debug level: 0=L0 (off), 1=L1, 2=L2, 3=L3, 4=L4
CURRENT_DEBUG_LEVEL = 2

# Map string levels to numeric levels
LEVEL_MAP = {
    'L0': 0,
    'L1': 1,
    'L2': 2,
    'L3': 3,
    'L4': 4
}

# Default colors for each level
DEFAULT_LEVEL_COLORS = {
    'L1': 'bwhite',
    'L2': 'bblue',
    'L3': 'idarkgreen',
    'L4': 'ipurple'
}

def debug_print(
    *args,
    debug: bool = True
):
    """
    Print debug messages with level filtering.
    Usage:
      debug_print(level, message parts...)
    The first argument is the level as a string ('L0', 'L1', 'L2', 'L3').
    Optionally, the second argument can be the color.
    If no color is provided, defaults are used based on level.
    """

    if not debug:
        return

    if len(args) == 0:
        return  # No arguments, do nothing

    # Extract the level
    level_str = args[0]
    if isinstance(level_str, str):
        level_upper = level_str.upper()
        level_num = LEVEL_MAP.get(level_upper, 3)
    else:
        # If first argument isn't a string, assume level 'L4'
        level_upper = 'L4'
        level_num = 4

    # Check level against current debug level
    if level_num > CURRENT_DEBUG_LEVEL:
        return

    # Determine the color:
    # If second argument exists and is a string, treat it as color
    color = None
    message_parts = []

    if len(args) > 1:
        second_arg = args[1]
        if isinstance(second_arg, str) and second_arg.lower() in COLORS:
            color = second_arg.lower()
            message_parts = args[2:]
        else:
            # No color specified, message parts start from second argument
            message_parts = args[1:]
    else:
        message_parts = []

    # If no color specified, use default for level
    if color is None:
        #Looks up the color name associated with level_upper in the DEFAULT_LEVEL_COLORS dictionary.
        #If the color name isn't found in COLORS, it defaults to 'iblue'.
        default_color_name = DEFAULT_LEVEL_COLORS.get(level_upper, 'iblue')
        color_code = COLORS.get(default_color_name, COLORS["iblue"])
    else:
        # Uses the provided color string to look up the ANSI code.
        # If the specified color isn't in COLORS, defaults to 'icyan'.
        color_code = COLORS.get(color, COLORS["icyan"])

    # Get caller line number
    frame = inspect.currentframe()
    caller_frame = frame.f_back
    line_number = caller_frame.f_lineno

    # Combine message parts
    combined_message = " ".join(str(msg) for msg in message_parts)

    if not combined_message.strip():
        print(f"LINE {line_number}: No message provided.")
        return

    # Wrap and print
    wrap_width = 125
    max_indent = 12
    line_info = f"LINE {line_number}: "
    line_info_length = len(line_info)

    wrapped_message = textwrap.fill(combined_message, width=wrap_width)
    indent_str = ' ' * (max_indent - line_info_length)

    # Print first line
    first_line = wrapped_message.splitlines()[0]
    print(f"{line_info}{indent_str}{color_code}{first_line}{COLORS['ireset']}")

    # Print wrapped remaining lines
    indent_str = ' ' * (max_indent)
    for line in wrapped_message.splitlines()[1:]:
        print(f"{indent_str}{color_code}{line}{COLORS['ireset']}")

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#





# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


def get_unix_time_from_index(local_filename):
    try:
        with open(local_filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        start_time = data.get('startTime')
        if start_time:
            return start_time  # Return the raw Unix timestamp
        else:
            # fallback to current time if startTime not present
            return int(time.time())
    except Exception as e:
        print("Error loading index.json:", e)
        return int(time.time())  # fallback to current time    

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


def get_human_readable_date(unix_timestamp):
    dt = datetime.datetime.fromtimestamp(unix_timestamp)
    day = dt.day
    month = dt.strftime('%B')  # Full month name
    year = dt.year
    weekday = dt.strftime('%A')  # Full weekday name

    # Determine ordinal suffix
    if 11 <= day <= 13:
        suffix = 'th'
    else:
        last_digit = day % 10
        if last_digit == 1:
            suffix = 'st'
        elif last_digit == 2:
            suffix = 'nd'
        elif last_digit == 3:
            suffix = 'rd'
        else:
            suffix = 'th'

    return f"{weekday}, {day}{suffix} {month} {year}"

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





import json
from collections import defaultdict
from RDO_challenges_data import (
    predefined_challenges,
    trader,
    bounty_hunter,
    collector,
    naturalist,
    moonshiner,
)

# Initialize index_data with a default empty dict
index_data = {}

# Set the path to your local index.json file
#local_filename = r"C:\Users\Dunk\Documents\Thonny Bits\RDO\RDO_dailies\jsonFiles\index.json"

# Set the path to your local index.json file in a relative subfolder called 'jsonFiles'
script_dir = os.path.dirname(os.path.abspath(__file__))  # the directory where the script is
os.makedirs(os.path.join(script_dir, "jsonFiles"), exist_ok=True)  # Check folder exists

local_filename = os.path.join(script_dir, "jsonFiles", "index.json") # Creates the filepath and assign to variable
debug_print("L1", "local_filename:  ", local_filename)




# URL for downloading if needed
url = "https://api.rdo.gg/challenges/index.json"

# Set the difficulty filter (None, "easy", "med", "hard")
filter_difficulty = "hard"  # Set to "easy", "med", or "hard" to filter role challenges

# Load the index.json challenge data
import urllib.request


file_exists = os.path.exists(local_filename)
 
if file_exists:
    try:
        with open(local_filename, 'r', encoding='utf-8') as f:
            index_data = json.load(f)  # Load JSON data from index.json file (it will all break without it as values are 0 otherwise)
            # Check if the file is outdated
            now = int(time.time())  # Gets current time in seconds since Unix epoch, and assign to 'now'
            end_time = index_data.get("endTime", 0)      # Tries to retrieve 'endTime' from the index_data dictionary, sets to 0 if can't
            start_time = index_data.get("startTime", 0)  # Tries to retrieve 'startTime' from the index_data dictionary, sets to 0 if can't
            
    except FileNotFoundError:
        print(f"{local_filename} not found. Proceeding without it.")
        # handle accordingly, e.g., initialize empty data
        now = int(time.time())
        end_time = 0
        start_time = 0

else:   #  If the index.json is not found, it will go and download it from the api website.
    print(f"{local_filename} not found. Will download new index.json.")
    now = int(time.time())
    end_time = 0
    start_time = 0


# Check if the index has expired by comparing 'endTime' in index.json to current time.
if end_time < now:
    debug_print("L2", "idarkyellow", f"The index.json has expired (endTime: {end_time}). Current time: {now}.")

    # Decide whether to prompt or just download
    if file_exists:
        if autoDownload:
            debug_print("L3", "bgreen", "autoDownload is True")
            download_now = True
        else:
            user_input = input("Do you want to download the latest index.json from rdo.gg? (y/n): ").strip().lower()
            download_now = (user_input == 'y')
    else:
        # No file exists, so download immediately
        download_now = True

    # Logic to do backup of existing index.json file before new download
    if download_now:
        # Only backup if start_time != 0
        if file_exists and start_time != 0:
            # Define the backup folder as a subfolder called 'indexJsonBackups'
            backup_folder = os.path.join(os.path.dirname(local_filename), 'indexJsonBackups')
            # Create the backup folder if it doesn't exist
            os.makedirs(backup_folder, exist_ok=True)
            
            # Construct the backup filename
            backup_filename = f"index_{datetime.datetime.fromtimestamp(start_time).strftime('%Y-%m-%d')}.json"
            # Full path for backup
            backup_path = os.path.join(backup_folder, backup_filename)
            
            try:
                os.rename(local_filename, backup_path)
                debug_print("L2", "igreen", "Backed up old index.json to:  ", backup_path)
            except Exception as e:
                debug_print("L1", "ired", f"Failed to backup old file: {e}")
        else:
            print("Skipping backup")     

        
        
        # Download new index.json
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response:
                data_bytes = response.read()
                data_str = data_bytes.decode('utf-8')
                data = json.loads(data_str)
                # Save the new data to the file
                with open(local_filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)
                    print("downloaded new index.json file")
        except Exception as e:
            print(f"Error during download: {e}")

        # Now, read the data from the saved file
        try:
            with open(local_filename, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
            # Access the data
            end_time = index_data.get("endTime", 0)
            start_time = index_data.get("startTime", 0)
            print(f"endTime: {end_time}, startTime: {start_time}")
        except Exception as e:
            print(f"Error reading {local_filename}: {e}")







def extract_challenges_with_roles(index):
    combined = []

    # General challenges (not tied to a specific role or difficulty)
    for challenge in index.get("general", []):
        combined.append({**challenge, "role": "general", "difficulty": None})

    # Role-based challenges across easy, med, hard
    for difficulty in ["easy", "med", "hard"]:
        for role, challenges in index[difficulty].items():
            for challenge in challenges:
                combined.append({**challenge, "role": role, "difficulty": difficulty})

    return combined

# Normalize keys by uppercasing and stripping whitespace (no prefix removal)
def normalize_key(key):
    return key.strip().upper()

# Combine all sources of challenge definitions that include name/key pairs
all_challenge_definitions = (
    predefined_challenges
    + trader
    + bounty_hunter
    + collector
    + naturalist
    + moonshiner
)

# Build a lookup table from all sources: exact key -> details including optional description and showgoal
detail_lookup = {
    normalize_key(ch["key"]): {
        "name": ch["name"],
        "description": ch.get("description"),
        "showgoal": ch.get("showgoal", "n")
    }
    for ch in all_challenge_definitions
}

# Extract and normalize all challenges from index.json
indexed_challenges = extract_challenges_with_roles(index_data)

# Final result list
final_list = []

for ch in indexed_challenges:
    title_upper = normalize_key(ch["title"])
    details = detail_lookup.get(title_upper, {})

    entry = {
        "title": ch["title"],
        "goal": ch["goal"],
        "category": ch["role"],
        "difficulty": ch["difficulty"],
        "name": details.get("name"),
        "description": details.get("description"),
        "showgoal": details.get("showgoal", "n")
    }
    final_list.append(entry)

# Desired print order for categories and difficulty
category_order = ["general", "bounty_hunter", "trader", "collector", "moonshiner", "naturalist"]
difficulty_order = [None, "easy", "med", "hard"]

# Group and sort challenges for JSON output
output_json = []
grouped_json = defaultdict(lambda: defaultdict(list))
for item in final_list:
    grouped_json[item["category"]][item["difficulty"]].append(item)

for category in category_order:
    for difficulty in difficulty_order:
        items = grouped_json.get(category, {}).get(difficulty, [])
        for item in sorted(items, key=lambda x: x["name"] or x["title"]):
            goal_display = ""
            if item["showgoal"].lower() == "y" or (isinstance(item["goal"], (int, float)) and item["goal"] > 1):
                goal_display = f"{item['goal']} "

            output_json.append({
                "text": f"{goal_display}{item['name'] or item['title']}",
                "description": item.get("description"),
                "category": category,
                "difficulty": difficulty
            })

# Write to file
with open("final_challenges_output2.json", "w", encoding="utf-8") as f_out:
    json.dump({"final_name": output_json}, f_out, indent=2)

# Group by category and difficulty for shell output
grouped = defaultdict(lambda: defaultdict(list))
for item in final_list:
    grouped[item["category"]][item["difficulty"]].append(item)

# Output filtered and formatted list to shell
print("\n")
for category in category_order:
    if category not in grouped:
        continue
    print(f"{category.upper()}")
    for difficulty in difficulty_order:
        if difficulty in grouped[category]:
            if difficulty is not None and filter_difficulty and difficulty != filter_difficulty:
                continue
            if not filter_difficulty:
                label = "GENERAL" if difficulty is None else difficulty.upper()
                print(f"  {label}")
            challenges = sorted(grouped[category][difficulty], key=lambda x: x["name"] or x["title"])
            for idx, challenge in enumerate(challenges):
                goal_display = ""
                if challenge["showgoal"].lower() == "y" or (isinstance(challenge["goal"], (int, float)) and challenge["goal"] > 1):
                    goal_display = f"{challenge['goal']} "

                print(f"{goal_display}{challenge['name'] or challenge['title']}")

                if challenge.get("description"):
                    print(f"\033[3;33m{challenge['description']}\033[0m")

                # Print separator between general challenges only
                if category == "general" and idx < len(challenges) - 1:
                    print("-" * 120)

            # After each difficulty group (or all general), print separator and newline
            if challenges:
                print("-" * 120)
                print()

# Summary stats
named = sum(1 for i in final_list if i["name"])
unnamed = len(final_list) - named
print(f"Total challenges: {len(final_list)}")
print(f"With names: {named}, Without names: {unnamed}")












import json
from collections import defaultdict

with open("final_challenges_output2.json", encoding="utf-8") as f:
    data = json.load(f)

challenges = data['final_name']
general_challenges = [c for c in challenges if c["category"] == "general"]
hard_role_challenges = [c for c in challenges if c["category"] != "general" and c["difficulty"] == "hard"]

role_names = {
    "bounty_hunter": "Bounty Hunter",
    "trader": "Trader",
    "collector": "Collector",
    "moonshiner": "Moonshiner",
    "naturalist": "Naturalist"
}

def render_challenge_block(block):
    html = ""
    for c in block:
        html += f'''
        <div class="challenge">
          <div class="challenge-text">{c["text"]}</div>'''
        if c.get("description"):
            html += f'''
          <div class="challenge-desc">{c["description"]}</div>'''
        html += "</div>"
    return html

html_general = render_challenge_block(general_challenges)
debug_print("L3", "ipurple", "html_general:  ", html_general)


def render_role_challenge_block(block):
    html = ""
    for c in block:
        html += f'''
        <div class="role-challenge">
          <div class="role-challenge-text">{c["text"]}</div>'''
        if c.get("description"):
            html += f'''
          <div class="role-challenge-desc">{c["description"]}</div>'''
        html += "</div>"
    return html



grouped_roles = defaultdict(list)
for c in hard_role_challenges:
    grouped_roles[c["category"]].append(c)

html_hard_roles = ""
role_keys = ["bounty_hunter", "trader", "collector", "moonshiner", "naturalist"]
for idx, role in enumerate(role_keys):
    if role in grouped_roles:
        html_hard_roles += f'<h3 class="role-heading">{role_names[role]}</h3>'
        html_hard_roles += render_role_challenge_block(grouped_roles[role])
        if idx < len(role_keys) - 1:
            html_hard_roles += '<hr class="thin-divider" />'
            debug_print("L3", "Would be printing a line here")
            
debug_print("L3", "html_hard_roles:   ", html_hard_roles)            
            

#####################################################################################################################################
##
##        HTML Generation
##
#####################################################################################################################################
# Get the appropriate date for the list of challenges and print it.
unix_time = get_unix_time_from_index(local_filename)
human_readable_date = get_human_readable_date(unix_time)
print(human_readable_date)
print("\n")


html_output = f'''
<!DOCTYPE html><html>
<head>
    <meta charset="UTF-8" />
    <link rel="icon" href="./html/images/favicon.ico" type="image/x-icon" />
    <style>
        body {{
          font-family: Arial, sans-serif;
          background-color: #000000;
          padding: 20px;
          margin: 0;
          height: 100vh;
          overflow: hidden;
        }}
        @font-face {{
          font-family: 'RDOFont';
          src: url('./Fonts/RDO_chinese_rocks_rg.otf') format('opentype');
          font-weight: normal;
          font-style: normal;
        }}
        @font-face {{
          font-family: 'hapna';
          src: url('./Fonts/hapna.woff2') format('woff2');
          font-weight: normal;
          font-style: normal;
        }}
        h1 {{
          font-size: 60px;
          text-align: left;
          margin-bottom: 40px;
        }}
        .banner-container {{
          position: relative;
          width: 100%;
          max-width: 850px;
          margin-left: 0;
        }}
        .banner-image {{
          width: 100%;
          height: auto;
          display: block;
          margin: 0;
        }}
        .banner-title {{
          font-family: 'RDOFont', sans-serif;
          position: absolute;
          top: 0%;
          left: 50%;
          transform: translateX(-50%);
          color: white;
          font-size: clamp(0.25em, 5vw, 3em);
          text-shadow: 2px 2px 4px rgba(0,0,0,0.7);
          margin: 0;
          padding: 10px;
        }}
        .date-below-title {{
          font-family: 'RDOFont', sans-serif;
          position: absolute;
          top: 37.5%;
          left: 50%;
          transform: translateX(-50%);
          color: white;
          font-size: clamp(0.15em, 1.50vw, 1.50em);
          margin: 0;
          padding: 10px;
          text-shadow: 2px 2px 4px rgba(0,0,0,0.7);
        }}
        .main-wrapper {{
          display: flex;
          align-items: flex-start;
          height: 100vh;
          padding: 0;
          margin: 0;
          position: relative;
        }}
        .challenges-wrapper {{
          max-width: 850px;
          padding: 40px 20px;
          box-sizing: border-box;
        }}
        .role-hard-wrapper {{
          width: 460px;
          max-height: 100vh;
          overflow-y: hidden;
          padding: 20px;
          box-sizing: border-box;
          position: absolute;
          top: 0;
          left: 870px;
          background: #111;
          border-left: 1px solid #333;
          font-size: 13px;
          line-height: 1;
          z-index: 1000;
        }}
        .role-hard-wrapper .challenge-text {{
          font-family: 'hapna', serif;
          font-size: 14px;
          color: #DADADA;
          white-space: pre-wrap;
          margin-bottom: 5px;
          line-height: 1;
        }}
        .role-hard-wrapper .challenge-desc {{
          font-family: 'hapna', serif;
          font-size: 12px;
          color: # #FFC300 ;
          white-space: pre-wrap;
          margin-bottom: 5px;
          line-height: 1.2;
        }}
        .thin-divider {{
          border: none;
          border-top: 1px solid #444;
          margin: 8px 0;
        }}
        .challenge {{
          margin-bottom: 10px;
          border-bottom: 1px solid #404040;
          padding-bottom: 10px;
        }}
        .challenge:last-child {{
          border-bottom: none;
        }}
        .challenge-text {{
          font-family: 'hapna', sans-serif;
          font-size: 20px;
          color: white;
        }}
        .challenge-desc {{
          font-family: 'hapna', serif;
          font-size: 16px;
          color: #999999;
          white-space: pre-wrap;
          margin-bottom: 5px;
          line-height: 1.2;
        }}
        .role-heading {{
          font-family: 'RDOFont', sans-serif;
          font-size: 24px;
          color: #eee;
          margin-top: -0px;
          margin-bottom: 8px;
          text-shadow:
            -3px -3px 0 #000,  
             3px -3px 0 #000,
            -3px 3px 0 #000,
             3px 3px 0 #000;
          letter-spacing: 1px; /* adjust as needed */
          
        }}
        .role-challenge {{
          margin-bottom: 0px;
          padding-bottom: 10px;
        }}
        .role-challenge-text {{
          font-family: 'hapna', sans-serif;
          font-size: 18px;
          color: #dadada;
          padding-bottom: 0px;
          display: inline-block; /* needed for transform to work properly */
          transform: scaleX(0.90); /* reduce width to 90% */
          transform-origin: left; /* or 'center' or 'right' based on your preference */
        }}
        .role-challenge-desc {{
          font-family: 'hapna', serif;
          font-size: 14px;
          color: #8c8080;
          white-space: pre-wrap;
          margin-bottom: 1px;
          line-height: 1.2;
          display: inline-block; /* needed for transform to work properly */
          transform: scaleX(0.925); /* reduce width to 90% */
          transform-origin: left; /* or 'center' or 'right' based on your preference */          
        }}
        .api-credit {{
          position: fixed;
          bottom: 10px;
          left: 40px;
          font-family: 'hapna', sans-serif;
          font-size: 12px;
          color: #888;
          z-index: 9999;
        }}
        .api-credit a {{
          color: #999;
          text-decoration: none;
        }}
        .api-credit a:hover {{
          text-decoration: underline;
          color: #ccc;
        }}
    </style>
</head>
<body>
  <div class="banner-container">
    <img src="HTML/images/RDO_Banner_Wide.jpg" alt="Banner" class="banner-image"/>
    <h1 class="banner-title">Daily Challenges</h1>
    <div class="date-below-title">{human_readable_date}</div>
  </div>
  <div class="main-wrapper">
    <div class="challenges-wrapper">
      {html_general}
    </div>
  </div>
  <div class="role-hard-wrapper">
      {html_hard_roles}
    </div>
  </div>
  <div class="api-credit">
  Data provided by <a href="https://rdo.gg/api" target="_blank">rdo.gg API</a>
</div>
</body>
</html>
'''

# Write to file
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_output)

print("HTML output written to index.html")

