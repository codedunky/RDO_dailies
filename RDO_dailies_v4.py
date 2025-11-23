

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
import datetime
import time

import inspect
import textwrap
import os
import io
import sys
from typing import Any
import hashlib  # For the checkbox id's

# Set a variable to control if index.json will download without user prompt
autoDownload = True

# Set the path to your local index.json file in a relative subfolder called 'jsonFiles'
script_dir = os.path.dirname(os.path.abspath(__file__))  # the directory where the script is
os.makedirs(os.path.join(script_dir, "jsonFiles"), exist_ok=True)  # Check folder exists

local_filename = os.path.join(script_dir, "jsonFiles", "index.json") # Creates the filepath and assign to variable
local_filename_nazar = os.path.join(script_dir, "jsonFiles", "nazar.json") # Creates the filepath for Nazar location and assign to variable
print("Initial 'local_filename':  ", local_filename)
print("Initial 'local_filename_nazar':  ", local_filename_nazar)


####################################################################################################################
# Set whether using description2 (for testing)
USE_DESCRIPTION2 = True

# #### CONFIG FLAGS #### #
#####################################################
#   Override mode: "auto", "force1", or "force2"
#   auto   = pick based on even/odd calendar day
#   force1 = always use description (description1)
#   force2 = always use description2
DESCRIPTION_MODE = "auto"

manual_streak = -1		# Set the number of days for the daily streak
                        # -1 will set it to use the current stored value
                        
                        
#   Toggle browser console debugging for Gold Totals
ENABLE_JS_DEBUG = True                        


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
    "bbrightyellow":   "\033[103m\033[30m",
    "bbrightblue":     "\033[104m",
    "bbrightpurple":   "\033[105m",
    "bbrightcyan":     "\033[106m\033[30m",
    "bbrightwhite":    "\033[107m\033[30m"
}

# Current debug level: 0=L0 (off), 1=L1, 2=L2, 3=L3, 4=L4
CURRENT_DEBUG_LEVEL = 0

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


import json
import datetime
import time

def get_index_start_date(local_filename):
    """
    Reads the index JSON file and returns:
    - The raw Unix timestamp for startTime (or current time fallback)
    - The formatted start date string "YYYY-MM-DD" (UTC)
    """
    #debug_print("L1", "local_filename", local_filename)
    #print(f"[DEBUG] Looking for index.json at: {os.path.abspath(local_filename)}")

    try:
        with open(local_filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        start_time = data.get('startTime')
        if start_time:
            dt = datetime.datetime.utcfromtimestamp(start_time)
            date_str = dt.strftime('%Y-%m-%d')
            return start_time, date_str
        else:
            now = int(time.time())
            date_str = datetime.datetime.utcfromtimestamp(now).strftime('%Y-%m-%d')
            return now, date_str
    except Exception as e:
        debug_print("L1", "bred", "Error loading index.json file")
        print("Error loading index.json:", e)
        now = int(time.time())
        date_str = datetime.datetime.utcfromtimestamp(now).strftime('%Y-%m-%d')
        return now, date_str

# Usage
start_timestamp, human_readable_date = get_index_start_date(local_filename)
  

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


def get_human_readable_date(unix_timestamp):
    unix_timestamp, _ = get_index_start_date(local_filename)  # if your function returns a tuple
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





# Returns a human readbale date from a unix timestamp
def timestamp_to_date(timestamp):
    return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------




#need this to get the unique build time so tickbox logic works with local storage caching

def get_index_mod_date_str(local_filename):
    try:
        mod_timestamp = os.path.getmtime(local_filename)
        dt = datetime.datetime.fromtimestamp(mod_timestamp)
        return dt.strftime("%Y-%m-%d_%H-%M-%S")
    except Exception as e:
        print(f"Error getting modification time: {e}")
        return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

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


#############################################################################################
##  DEBUG FOR GITHUB
#############################################################################################
print(f"[DEBUG] index.json path: {local_filename}")                                         
print(f"[DEBUG] Does index.json exist? {os.path.exists(local_filename)}")

if os.path.exists(local_filename):
    with open(local_filename, 'r') as f:
        data = json.load(f)
    print(f"[DEBUG] ***** index.json endTime: {data.get('endTime')} ({timestamp_to_date(data.get('endTime'))})")

    

#############################################################################################

# Generating a unique id for tickboxes using todays date
import datetime
start_time_unix, human_readable_date = get_index_start_date(local_filename)
start_date_str = datetime.datetime.utcfromtimestamp(start_time_unix).strftime("%Y-%m-%d")




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
    print

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
                
            # !!! INSERT THESE 3 LINES HERE !!!
            # Refresh the start_timestamp so the HTML and IDs get the NEW date, not the old one
            start_timestamp, human_readable_date = get_index_start_date(local_filename)
            start_date_str = datetime.datetime.utcfromtimestamp(start_timestamp).strftime("%Y-%m-%d")
            # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            
            # Access the data
            end_time = index_data.get("endTime", 0)
            start_time = index_data.get("startTime", 0)
            print(f"startTime: {timestamp_to_date(start_time)}, endTime: {timestamp_to_date(end_time)}")
        except Exception as e:
            print(f"Error reading {local_filename}: {e}")
            
        time.sleep(10)        







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
        "description2": ch.get("description2"),
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
        "description2": details.get("description2"),
        "showgoal": details.get("showgoal", "n")
    }
    final_list.append(entry)
    

#Choosing either description or description2
def get_printable_description(details):
    """
    Return the appropriate description text based on the flag (or random logic)
    """
    desc1 = details.get("description")
    desc2 = details.get("description2")

    # Fallback if no alternate description
    if not desc2:
        return desc1
    
    
    # --- Manual override modes ---
    if DESCRIPTION_MODE == "force1":
        debug_print("L2", "Force1 is set, so forcing description")
        return desc1
    elif DESCRIPTION_MODE == "force2":
        debug_print("L2", "Force2 is set, so forcing description2")
        return desc2

    # --- Auto mode: alternate by calendar day ---
    today = datetime.date.today()
    if today.day % 2 == 0:
        # even-numbered day
        debug_print("L2", "Even Numbered Day, using description2")
        return desc2
    else:
        # odd-numbered day
        debug_print("L2", "Odd Numbered Day, using description")
        return desc1
    
    
    

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

            # Safely get and normalize the showgoal value
            showgoal = str(item.get("showgoal", "")).strip().lower()
            debug_print("L3", "bpurple", "showgoal before processing: ", showgoal)

            if showgoal == "no":
                # Explicitly do not show the goal
                goal_display = ""
            elif showgoal == "yes":
                # Always show the goal
                goal_display = f"{item['goal']} "
            else:
                # Default fallback: show goal if > 1
                if isinstance(item.get("goal"), (int, float)) and item["goal"] > 1:
                    goal_display = f"{item['goal']} "
                    
            debug_print("L3", "showgoal: ", showgoal)
            debugtext = f"{goal_display}{item['name'] or item['title']}",
            debug_print("L3", "iblue", "text: ", debugtext),
                        
            chosen_description = get_printable_description(item)
            debug_print("L1", "Chosen Description: ", chosen_description)
            
            output_json.append({
                "text": f"{goal_display}{item['name'] or item['title']}",
                "description": chosen_description,
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

role_keys = ["bounty_hunter", "trader", "collector", "moonshiner", "naturalist"]

role_names = {
    "bounty_hunter": "Bounty Hunter",
    "trader": "Trader",
    "collector": "Collector",
    "moonshiner": "Moonshiner",
    "naturalist": "Naturalist"
}

###########################################
###### Generate a stable tickbox hash #####
###########################################
def stable_hash(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()[:16]  # First 16 chars of hash
#-----------------------------------------#

import datetime


###########################################################################################################################################################

def render_challenge_block_old(block, prefix="challenge"):
    html = ""
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")  # Current date for debug purposes
    debug_print("L3", "today_str:   ", today_str)
    start_time_unix, human_readable_date = get_index_start_date(local_filename)  # Date of challenges from index.json
    start_date_str = datetime.datetime.utcfromtimestamp(start_time_unix).strftime("%Y-%m-%d")  # Creating a unique id for the index.json date
    debug_print("L3", "bblue", "'start_date_str' for use in tickbox id:   ", start_date_str)

    for c in block:
        # Combine date + text hash to avoid persistence across different days
        safe_id = f"{prefix}_{start_date_str}_{stable_hash(c['text'])}"
        debug_print("L3", "safe_id:   ", safe_id)  #  Print the unique id for a challenge

        html += f'''
        <div class="{prefix}">
          <label>
            <input type="checkbox" class="challenge-checkbox" id="{safe_id}" />
            <span class="{prefix}-text">{c["text"]}</span>
          </label>'''

        # Optional description
        if c.get("description"):
            html += f'''
          <div class="{prefix}-desc">{c["description"]}</div>'''

        html += '</div>\n'

    return html

###########################################################################################################################################################


## New render_general_challenge_block function adds in line dividers
###########################################################################################################################################################

def render_general_challenges_with_dividers(general_challenges):
    html = ""
    for i, challenge in enumerate(general_challenges):
        # render single challenge as a block
        block_html = render_challenge_block([challenge])  # pass a list of one challenge
        html += block_html
        
        # Add divider except after last challenge
        if i < len(general_challenges) - 1:
            html += '<hr class="thin-divider">\n'
    return html





def render_challenge_block(block, prefix="challenge", role_name="", filter_difficulty="hard"):
    html = ""

    # Current date for debug purposes (not used in ID generation)
    today_str = datetime.datetime.now().strftime("%Y-%m-%d")
    debug_print("L3", "today_str:   ", today_str)

    # Get the date of challenges from index.json
    start_time_unix, human_readable_date = get_index_start_date(local_filename)

    # Create a unique date string to ensure checkbox IDs change daily
    start_date_str = datetime.datetime.utcfromtimestamp(start_time_unix).strftime("%Y-%m-%d")
    debug_print("L3", "bblue", "'start_date_str' for use in tickbox id:   ", start_date_str)

    # If this is a role challenge, add a heading and wrapper container
    if prefix == "role-challenge":
        # Create a role ID from the role name (lowercase, no spaces)
        role_id = "role-" + "".join(c.lower() if c.isalnum() else "-" for c in role_name).strip("-")

        # Start a role block container
        html += f'<div class="role-container">\n'  # << NEW: wrapper for the role + its challenges

        # Add role heading and difficulty toggle button
        html += f'  <h3 class="role-heading" id="{role_id}">{role_name}&nbsp; '
        html += f'<span class="difficulty-toggle RDOFont" data-difficulty="{filter_difficulty}">({filter_difficulty.capitalize()}: ' \
        f'{ "Rank 1–5" if filter_difficulty == "easy" else "Rank 6–14" if filter_difficulty == "med" else "Rank 15+" })</span>'

        html += '</h3>\n'

    # Loop through the challenge block. Use enumerate to track index for divider logic.
    for i, c in enumerate(block):
        # Combine date + text hash to create a unique and stable ID for each challenge
        safe_id = f"{prefix}_{start_date_str}_{stable_hash(c['text'])}"
        debug_print("L3", "safe_id:   ", safe_id)  # Print the unique id for a challenge

        # Add the class to the label only for role challenges
        label_class = 'role-challenge-label' if prefix == 'role-challenge' else ''
        label_open = f'<label class="{label_class}">' if label_class else '<label>'

        # Get the difficulty of the challenge, defaulting to 'easy' if not present
        difficulty = c.get("difficulty", "easy")  # << NEW: Add this to support filtering

        # Start the challenge container with a label, checkbox, and difficulty attribute
        html += f'''
        <div class="{prefix}" data-difficulty="{difficulty}">
          {label_open}
            <input type="checkbox" class="challenge-checkbox" id="{safe_id}" />
            <span class="{prefix}-text">{c["text"]}</span>
          </label>'''

        # Add optional description block if it exists
        if c.get("description"):
            html += f'''
          <div class="{prefix}-desc">{c["description"]}</div>'''

        # Close the challenge container
        html += '</div>\n'

    # If this was a role challenge, close the wrapper container
    if prefix == "role-challenge":
        html += '</div>\n'  # Close the role-container div

    return html











html_general = render_general_challenges_with_dividers(general_challenges)
debug_print("L3", "ipurple", "html_general:  ", html_general)

############################################################
# Generate html for role challenges with difficulty levels #
############################################################

def generate_html_for_difficulty(challenges, filter_difficulty):
    from collections import defaultdict

    # Group all challenges by their 'category' (e.g., role categories or 'general')
    grouped_by_role = defaultdict(list)
    for c in challenges:
        grouped_by_role[c['category']].append(c)

    # Separate general challenges and role-specific challenges
    general_challenges = grouped_by_role.get("general", [])

    # Render the general challenges HTML block
    html_general = '<h2 class="general-heading">General Challenges <span id="general-counter">(0/0)</span></h2>\n'
    # Render general challenges without role/difficulty filtering
    html_general += render_challenge_block(general_challenges)

    # Render role challenges — don't pre-filter by difficulty anymore
    html_roles = ''   # <h2>Role Challenges <span id="role-counter">(0/0)</span></h2>\n'

    # Loop through roles that actually have challenges
    roles_with_challenges = [role for role in role_keys if role in grouped_by_role and grouped_by_role[role]]

    for idx, role in enumerate(roles_with_challenges):
        block = grouped_by_role[role]

        # Pass the filter_difficulty to set the initial difficulty shown
        html_roles += render_challenge_block(
            block,
            prefix="role-challenge",
            role_name=role_names.get(role, role.title()),
            filter_difficulty=filter_difficulty  # Pass down difficulty
        )

        # Add a thin divider line between role sections, except after the last one
        if idx < len(roles_with_challenges) - 1:
            html_roles += '<hr class="thin-divider" />\n'

        debug_print("L2", "byellow", f"Adding role block: {role_names[role]}")

    return html_general, html_roles






def render_role_challenge_block_old(block):
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

##########################################################################
# Generate html for role challenges with difficulty levels and tickboxes #
##########################################################################
def render_role_challenge_block(block):
    debug_print("L1", "bbyellow", "render_role_challenge_block")
    html = ""

    # Get the start date string to use in generating stable IDs
    start_time_unix, _ = get_index_start_date(local_filename)
    start_date_str = datetime.datetime.utcfromtimestamp(start_time_unix).strftime("%Y-%m-%d")

    for c in block:
        # Create a stable unique ID based on date and challenge text
        safe_id = f"role-challenge_{start_date_str}_{stable_hash(c['text'])}"
        
        debug_print("L1", "bbyellow", "label class")
        html += f'''
        <div class="role-challenge">
          <label class="role-challenge-label">
            <input type="checkbox" class="challenge-checkbox" id="{safe_id}" />
            <span class="text-scale"><span class="role-challenge-text">{c["text"]}</span></span>
          </label>'''

        # Optional description
        if c.get("description"):
            html += f'''
          <div class="role-challenge-desc">{c["description"]}</div>'''

        html += "</div>\n"

        # Removed: Divider between each challenge to avoid clutter
        # You should add divider between roles externally after rendering each block

    return html




#-------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------
########################  This was the old hard coded role challenges (for hard difficulty) ########################

# grouped_roles = defaultdict(list)
# for c in hard_role_challenges:
#     grouped_roles[c["category"]].append(c)
# 
# html_hard_roles = ""
# role_keys = ["bounty_hunter", "trader", "collector", "moonshiner", "naturalist"]
# for idx, role in enumerate(role_keys):
#     if role in grouped_roles:
#         html_hard_roles += f'<h3 class="role-heading">{role_names[role]}</h3>'
#         html_hard_roles += render_role_challenge_block(grouped_roles[role])
#         if idx < len(role_keys) - 1:
#             html_hard_roles += '<hr class="thin-divider" />'
#             debug_print("L3", "Would be printing a line here")
#             
# debug_print("L3", "html_hard_roles:   ", html_hard_roles)

#-------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------




####################################
# Generate HTML for each difficulty#
####################################
html_easy_general, html_easy_roles = generate_html_for_difficulty(challenges, "easy")
html_med_general,  html_med_roles  = generate_html_for_difficulty(challenges, "med")
html_hard_general, html_hard_roles = generate_html_for_difficulty(challenges, "hard")



debug_print("L2", "bblue", "Generated html_easy_roles")
debug_print("L3", "iblue", "html_easy_roles:   ", html_easy_roles)
print ("-" * 120)
debug_print("L2", "bpurple", "Generated html_med_roles")
debug_print("L3", "ipurple", "html_med_roles:   ", html_med_roles)
print ("-" * 120)
debug_print("L2", "bred", "Generated html_hard_roles")
debug_print("L3", "ired", "html_hard_roles:   ", html_hard_roles)
print ("-" * 120)

#---------------------------------------------------------------------------------------
difficulty_roles_map = {
    "easy": html_easy_roles,
    "med": html_med_roles,
    #"hard": html_hard_roles
}

selected_html_roles = difficulty_roles_map.get(filter_difficulty, html_hard_roles)
#---------------------------------------------------------------------------------------




#############################################################################################
##  DEBUG FOR GITHUB
#############################################################################################
unix_time = get_index_start_date(local_filename)
print("#################### unix_time from index.json", unix_time, "####################")    


#############################################################################################






####################################################################################################################################
##                                                                                                                                ##
##                                                        HTML VERSION 2                                                          ##
##                                                                                                                                ##
####################################################################################################################################
# Get the appropriate date for the list of challenges and print it.
unix_time = get_index_start_date(local_filename)
human_readable_date = get_human_readable_date(unix_time)
print(human_readable_date)
index_mod_date_str = get_index_mod_date_str(local_filename)
print("index_mod_date_str:  ",index_mod_date_str)
print("\n")









# ... (all of your existing Python code before this point) ...

####################################################################################################################################
##                                                                                                                                ##
##                                    JAVASCRIPT BLOCK (DEFINED SEPARATELY)                                                       ##
##                                                                                                                                ##
####################################################################################################################################

# Define the JavaScript as a separate f-string to correctly inject Python variables
# without conflicting with JavaScript's own syntax.


javascript_code = f'''







<script>
// ////////////////////////////////////////////////////////////////////////////////////// //
// JavaScript: Check if flask server is running and show or hide button accordingly       //
// ////////////////////////////////////////////////////////////////////////////////////// //

fetch('http://127.0.0.1:6969/status')
    .then(response => {{
      if (response.ok) {{
        document.getElementById('pauseBtn').style.display = 'inline';
      }} else {{
        document.getElementById('pauseBtn').style.display = 'none';
      }}
    }})
    .catch(error => {{
      document.getElementById('pauseBtn').style.display = 'none';
    }});

// ////////////////////////////////////////////////////////////////////////////////////// //
// JavaScript: Banner and Clock Logic                                                     //
// ////////////////////////////////////////////////////////////////////////////////////// //

function resizeBannerText() {{
    const container = document.querySelector('.banner-container');
    const title = document.querySelector('.banner-title');
    const date = document.querySelector('.banner-date');
    const counters = document.querySelector('.challenge-counters');
    const clock = document.getElementById('rdo-clock');

    if (!container) return;

    const containerWidth = container.offsetWidth;
    const minWidth = 400;
    const maxWidth = 850;
    const scale = Math.max(minWidth, Math.min(containerWidth, maxWidth)) / maxWidth;

    title.style.fontSize = (2.5 * scale) + 'rem';
    date.style.fontSize = (1.4 * scale) + 'rem';
    counters.style.fontSize = (1.25 * scale) + 'rem';
    
    if (clock) {{
        clock.style.fontSize = (2 * scale) + 'rem';
    }}
}}

window.addEventListener('resize', resizeBannerText);
window.addEventListener('load', resizeBannerText);

const offsetSeconds = -600; // -10 minutes offset for game clock

function getInGameHour() {{
    const now = new Date();
    const utcSeconds = now.getUTCHours() * 3600 + now.getUTCMinutes() * 60 + now.getUTCSeconds();
    const gameSeconds = (utcSeconds * 30 + offsetSeconds) % 86400;
    return Math.floor(gameSeconds / 3600) + Math.floor((gameSeconds % 3600) / 60) / 60;
}}

function updateAllTimeFunctions() {{
    const hourFloat = getInGameHour();
    const gameHours = Math.floor(hourFloat).toString().padStart(2, '0');
    const gameMinutes = Math.floor((hourFloat % 1) * 60).toString().padStart(2, '0');
    document.getElementById("rdo-clock").textContent = `${{gameHours}}:${{gameMinutes}}`;

    const banner = document.querySelector('.banner-image');
    const clock = document.querySelector('.rdo-clock');
    
    if (hourFloat >= 22 || hourFloat < 5) {{
        if (!banner.src.endsWith("RDO_Banner_Wide_Night.jpg")) banner.src = "HTML/images/RDO_Banner_Wide_Night.jpg";
        clock.classList.add('night-glow');
    }} else {{
        if (!banner.src.endsWith("RDO_Banner_Wide.jpg")) banner.src = "HTML/images/RDO_Banner_Wide.jpg";
        clock.classList.remove('night-glow');
    }}
}}

setInterval(updateAllTimeFunctions, 1000);
updateAllTimeFunctions();

// ////////////////////////////////////////////////////////////////////////////////////// //
// JavaScript: Main Logic                                                                 //
// ////////////////////////////////////////////////////////////////////////////////////// //

document.addEventListener("DOMContentLoaded", function() {{

    // --- CONSTANTS INJECTED FROM PYTHON ---
    const PYTHON_STREAK_OVERRIDE = {manual_streak};
    const PYTHON_CHALLENGE_TIMESTAMP = {start_timestamp}; 
    const PYTHON_ENABLE_DEBUG = {str(ENABLE_JS_DEBUG).lower()};

    // --- LOCAL STORAGE KEYS ---
    const LS_STREAK_COUNT = 'rdoStreakCount';
    const LS_LAST_COMPLETION_DATE = 'rdoLastCompletionDate';
    const LS_CHALLENGE_STATUS = 'rdoChallengeStatus';
    const LS_STREAK_FOR_MULTIPLIER = 'rdoStreakForMultiplier'; 
    const MAX_RDO_STREAK = 28;
    const LS_GOLD_LOG = 'rdoGoldLog';
    const LS_LAST_KNOWN_TIMESTAMP = 'rdoLastKnownTimestamp';
    
    // --- ELEMENT SELECTORS ---
    const allCheckboxes = document.querySelectorAll('.challenge-checkbox');
    const generalCheckboxes = document.querySelectorAll('.challenge-checkbox[id^="challenge_"]');
    const roleCheckboxes = document.querySelectorAll('.challenge-checkbox[id^="role-challenge_"]');
    
    // --- UTILITY FUNCTIONS ---
    
    function getRDODayKey() {{
        const now = new Date();
        const resetTimeHours = 6; 
        const date = new Date(now.getTime());
        if (date.getUTCHours() < resetTimeHours) {{
            date.setUTCDate(date.getUTCDate() - 1);
        }}
        return date.toISOString().split('T')[0];
    }}

    function getChallengeDateKey() {{
        const date = new Date(PYTHON_CHALLENGE_TIMESTAMP * 1000);
        return date.toISOString().split('T')[0];
    }}

    function getDateDifferenceInDays(dateStr1, dateStr2) {{
        const date1 = new Date(`${{dateStr1}}T12:00:00Z`);
        const date2 = new Date(`${{dateStr2}}T12:00:00Z`);
        return Math.round(Math.abs(date2 - date1) / (1000 * 60 * 60 * 24));
    }}
    
    function setStreakCount(newCount, setCompleted) {{
        const count = Math.min(Math.max(0, newCount), MAX_RDO_STREAK); 
        localStorage.setItem(LS_STREAK_COUNT, count);
        if (setCompleted) {{
            localStorage.setItem(LS_LAST_COMPLETION_DATE, getRDODayKey());
            localStorage.setItem(LS_CHALLENGE_STATUS, 'completed');
        }} else {{
            localStorage.removeItem(LS_LAST_COMPLETION_DATE);
            localStorage.removeItem(LS_CHALLENGE_STATUS);
        }}
    }}

    function getMultiplier() {{ 
        const lockedStreak = parseInt(localStorage.getItem(LS_STREAK_FOR_MULTIPLIER) || '0', 10);
        if (lockedStreak >= 22) return 2.5; // Days 22-28
        if (lockedStreak >= 15) return 2.0; // Days 15-21
        if (lockedStreak >= 8) return 1.5;  // Days 8-14
        return 1.0;                         // Days 1-7
    }}

    function formatGoldForDisplay(goldValue) {{
        const fixedValue = goldValue.toFixed(2);
        const parts = fixedValue.split('.');
        return `<span>${{parts[0]}}</span><span class="gold-decimal">.${{parts[1]}}</span> Gold Bars`;
    }}

    // --- DEBUGGING FUNCTION ---
    function debugGoldStats(daily, week, running, goldLog) {{
        if (!PYTHON_ENABLE_DEBUG) return;

        console.group(`%cRDO GOLD STATS`, 'color: #000; background: #FFC107; padding: 4px; border-radius: 4px; font-weight: bold;');
        
        console.table({{
            "Current Streak": localStorage.getItem(LS_STREAK_COUNT) + " Days",
            "Multiplier Lock": localStorage.getItem(LS_STREAK_FOR_MULTIPLIER) + " Days",
            "Daily Total": daily.toFixed(2),
            "Streak Week Total": week.toFixed(2),
            "Streak Running Total": running.toFixed(2)
        }});

        console.groupCollapsed("Full Gold Log History");
        console.table(goldLog);
        console.groupEnd();
        
        console.groupEnd();
    }}

    function calculateDailyGoldTotal(completedGeneral, completedRole) {{
        const BASE_REWARD = 0.10; 
        const COMPLETION_BONUS_BASE = 0.30; 
        const multiplier = getMultiplier();
        const completionBonusAmount = COMPLETION_BONUS_BASE * multiplier;
        const generalGold = (completedGeneral * BASE_REWARD) * multiplier;
        const generalBonus = (completedGeneral === 7) ? completionBonusAmount : 0;
        const roleGold = (completedRole * BASE_REWARD) * multiplier;
        const roleBonus = (completedRole === 9) ? completionBonusAmount : 0;
        
        document.getElementById('gold-per-challenge').innerHTML = formatGoldForDisplay(BASE_REWARD * multiplier);
        document.getElementById('completion-bonus-reward').innerHTML = formatGoldForDisplay(completionBonusAmount);
        
        return Math.round((generalGold + generalBonus + roleGold + roleBonus) * 100) / 100;
    }}

    function logDailyGold(goldAmount, streakCount, generalCount, roleCount) {{
        const today = getRDODayKey();
        if (getChallengeDateKey() !== today) return;

        let goldLog = JSON.parse(localStorage.getItem(LS_GOLD_LOG)) || [];
        const todayEntryIndex = goldLog.findIndex(entry => entry.date === today);
        const newEntry = {{ date: today, gold: goldAmount, streak: streakCount, general: generalCount, role: roleCount }};

        if (todayEntryIndex > -1) {{
            goldLog[todayEntryIndex] = newEntry;
        }} else {{
            goldLog.push(newEntry);
        }}
        while (goldLog.length > 28) goldLog.shift();
        localStorage.setItem(LS_GOLD_LOG, JSON.stringify(goldLog));
    }}
    
    // UPDATED FUNCTION: Smarter "Current Streak" Calculation
    function calculateLogSums(currentStreak) {{
        const goldLog = JSON.parse(localStorage.getItem(LS_GOLD_LOG)) || [];
        
        // 1. Calculate Week Total (Range based)
        let minWeekStreak = 1;
        if (currentStreak >= 22) minWeekStreak = 22;
        else if (currentStreak >= 15) minWeekStreak = 15;
        else if (currentStreak >= 8) minWeekStreak = 8;
        else minWeekStreak = 1;
        
        const maxWeekStreak = minWeekStreak + 6;

        let weekTotal = 0.0;
        let runningTotal = 0.0;
        
        // Loop forward for Week Total (simple range check)
        goldLog.forEach(entry => {{
            const val = parseFloat(entry.gold || 0);
            const s = parseInt(entry.streak || 0);
            if (s >= minWeekStreak && s <= maxWeekStreak && s > 0) {{
                weekTotal += val;
            }}
        }});
        
        // 2. Calculate Running Total (Backwards contiguous check)
        let lastStreakVal = -1;
        
        for (let i = goldLog.length - 1; i >= 0; i--) {{
            const entry = goldLog[i];
            const s = parseInt(entry.streak || 0);
            
            if (s === 0) break;
            
            // Discontinuity Check: If streak jumps UP going backwards (e.g. 1 -> 28), it's a new cycle.
            if (lastStreakVal !== -1 && s >= lastStreakVal) {{
                break;
            }}

            runningTotal += parseFloat(entry.gold || 0);

            if (s === 1) break;

            lastStreakVal = s;
        }}
        
        return {{ week: weekTotal, running: runningTotal }};
    }}
    
    function renderGoldLogChart() {{
        const GOLD_CHART_MULTIPLIER = 12; 
        const container = document.getElementById('gold-log-chart-container');
        const infoDisplay = document.getElementById('chart-info-display');
        if (!container || !infoDisplay) return;

        // Audio Context Setup
        if (!window.rdoAudioCtx) {{
            const AudioContext = window.AudioContext || window.webkitAudioContext;
            window.rdoAudioCtx = new AudioContext();
            const unlockAudio = () => {{
                if (window.rdoAudioCtx.state === 'suspended') window.rdoAudioCtx.resume();
                document.removeEventListener('click', unlockAudio);
            }};
            document.addEventListener('click', unlockAudio);
        }}
        
        function playHoverTick() {{
            const ctx = window.rdoAudioCtx;
            if (!ctx || ctx.state === 'suspended') return;
            const osc = ctx.createOscillator();
            const gain = ctx.createGain();
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.type = 'triangle'; 
            osc.frequency.setValueAtTime(1200, ctx.currentTime);
            gain.gain.setValueAtTime(0.2, ctx.currentTime); 
            gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.05);
            osc.start();
            osc.stop(ctx.currentTime + 0.05);
        }}

        infoDisplay.innerHTML = '&nbsp;';
        const goldLog = JSON.parse(localStorage.getItem(LS_GOLD_LOG)) || [];
        container.innerHTML = '';

        if (goldLog.length === 0) {{
            container.innerHTML = '<p style="color: #666; font-size: 0.8rem; text-align: center; width: 100%;">No gold data logged yet.</p>';
            return;
        }}

        function getBarColorForStreak(streak) {{
            if (!streak) return '#555555';
            if (streak >= 22) return '#FFD200'; 
            if (streak >= 15) return '#E4B800'; 
            if (streak >= 8)  return '#C59A00'; 
            return '#A57C00';                   
        }}
        
        const availableWidth = container.clientWidth - 4; 
        const barWidth = Math.max(Math.floor(availableWidth / 28) - 2, 2);
        let tooltipLeaveTimer;

        goldLog.forEach(entry => {{
            const barHeight = Math.max((entry.gold * GOLD_CHART_MULTIPLIER), 0);
            const wrapper = document.createElement('div');
            wrapper.className = 'chart-bar-wrapper';
            wrapper.style.width = `${{barWidth}}px`;
            
            const bar = document.createElement('div');
            bar.className = 'chart-bar';
            bar.style.height = `${{barHeight}}px`;
            bar.style.backgroundColor = getBarColorForStreak(entry.streak);

            wrapper.appendChild(bar);
            container.appendChild(wrapper);

            const date = new Date(entry.date); 

            wrapper.addEventListener('mouseenter', () => {{
                if (tooltipLeaveTimer) clearTimeout(tooltipLeaveTimer);
                bar.style.backgroundColor = '#FFFFFF';
                bar.style.boxShadow = '0 0 8px rgba(255, 255, 255, 0.9)';
                playHoverTick();

                const humanDate = date.toLocaleDateString('en-GB', {{ weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' }});
                const streakText = entry.streak ? `Day ${{entry.streak}} (Week ${{Math.floor((entry.streak - 1) / 7) + 1}})` : 'No Streak';
                
                let star = '';
                if (entry.general === 7 && entry.role === 9) {{
                    star = ' <span style="color: #FFD700;">⭐</span>';
                }} else if (entry.general === 7 || entry.role === 9) {{
                    star = ' <span style="filter: grayscale(100%) brightness(1.3);">⭐</span>';
                }}
                
                infoDisplay.innerHTML = `
                    <div style="display: flex; justify-content: space-between; align-items: baseline; width: 100%; font-size: 0.9rem;">
                        <span style="font-weight: bold;">${{humanDate}}</span>
                        <span>${{entry.gold.toFixed(2)}} Gold${{star}}</span>
                    </div>
                    <div style="font-size: 0.8rem; color: #999;">Streak: ${{streakText}} | Gen: ${{entry.general}}/7, Role: ${{entry.role}}/9</div>
                `;
                infoDisplay.style.color = '#aaa';
            }});

            wrapper.addEventListener('mouseleave', () => {{
                bar.style.backgroundColor = getBarColorForStreak(entry.streak);
                bar.style.boxShadow = 'none';
                tooltipLeaveTimer = setTimeout(() => {{
                    infoDisplay.innerHTML = '&nbsp;';
                }}, 200);
            }});
        }});
    }}

    // --- CORE UPDATE LOGIC ---
    
    function loadStreak() {{
        let currentStreak = parseInt(localStorage.getItem(LS_STREAK_COUNT) || '0', 10);
        if (PYTHON_STREAK_OVERRIDE > -1) {{
            currentStreak = PYTHON_STREAK_OVERRIDE; 
            setStreakCount(currentStreak, true);
        }}
        
        const lastCompletionDateStr = localStorage.getItem(LS_LAST_COMPLETION_DATE);
        if (lastCompletionDateStr) {{
            const diff = getDateDifferenceInDays(getRDODayKey(), lastCompletionDateStr);
            if (diff > 1 || (diff === 1 && currentStreak >= MAX_RDO_STREAK)) {{
                currentStreak = 0;
                setStreakCount(0, false);
            }}
            if (diff >= 1) {{
                localStorage.removeItem(LS_CHALLENGE_STATUS);
                localStorage.removeItem(LS_LAST_COMPLETION_DATE); 
            }}
        }}
        
        localStorage.setItem(LS_STREAK_FOR_MULTIPLIER, currentStreak);
        document.getElementById('current-streak').textContent = `${{currentStreak}} Days`;
    }}

    function updateCounters() {{
        const generalDone = Array.from(generalCheckboxes).filter(cb => cb.checked).length;
        const roleDone = Math.min(
            Array.from(roleCheckboxes).filter(cb => cb.checked && cb.closest('.role-challenge')?.style.display !== 'none').length,
            9
        );

        document.getElementById('general-counter').textContent = `${{generalDone}}/7`;
        document.getElementById('general-counter').classList.toggle('counter-glow', generalDone === 7);
        document.getElementById('role-counter').textContent = `${{roleDone}}/9`;
        document.getElementById('role-counter').classList.toggle('counter-glow', roleDone === 9);
        
        const dailyGoldTotal = calculateDailyGoldTotal(generalDone, roleDone);
        const currentStreak = parseInt(localStorage.getItem(LS_STREAK_COUNT) || '0', 10);
        
        document.getElementById('current-streak').textContent = `${{currentStreak}} Days`; 
        
        const goldDisplay = document.getElementById('daily-gold-total');
        const isDataCurrent = (getChallengeDateKey() === getRDODayKey());
        
        if (isDataCurrent) {{
            // 1. Log today's calculated gold (and streak) to localStorage
            logDailyGold(dailyGoldTotal, currentStreak, generalDone, roleDone);
            goldDisplay.innerHTML = formatGoldForDisplay(dailyGoldTotal);
        }} else {{
            goldDisplay.innerHTML = '<span style="color: #888; font-size: 0.8em;">PREVIOUS DAY DATA</span>';
        }}

        // 2. Calculate Week/Running totals by summing the Log
        const sums = calculateLogSums(currentStreak);
        
        // 3. Update DOM with flash effect if values changed
        const newCycleHTML = formatGoldForDisplay(sums.week);
        const cycleEl = document.getElementById('cycle-gold-total');
        if (cycleEl.innerHTML !== newCycleHTML) {{
             cycleEl.innerHTML = newCycleHTML;
             cycleEl.classList.remove('gold-exciting-flash');
             void cycleEl.offsetWidth; 
             cycleEl.classList.add('gold-exciting-flash');
             setTimeout(() => cycleEl.classList.remove('gold-exciting-flash'), 1000);
        }}
        
        const newStreakHTML = formatGoldForDisplay(sums.running);
        const streakEl = document.getElementById('streak-gold-total');
        if (streakEl.innerHTML !== newStreakHTML) {{
             streakEl.innerHTML = newStreakHTML;
             streakEl.classList.remove('gold-exciting-flash');
             void streakEl.offsetWidth; 
             streakEl.classList.add('gold-exciting-flash');
             setTimeout(() => streakEl.classList.remove('gold-exciting-flash'), 1000);
        }}

        const rolesContainer = document.getElementById('roles-container') || document.body;
        rolesContainer.classList.toggle('all-roles-completed', roleDone === 9);
        document.querySelectorAll('.difficulty-toggle').forEach(toggle => toggle.classList.toggle('dimmed-text', roleDone === 9));
        
        document.querySelectorAll('.role-container').forEach(roleContainer => {{
            const visible = Array.from(roleContainer.querySelectorAll('.role-challenge')).filter(ch => ch.style.display !== 'none');
            const allComp = visible.length > 0 && visible.every(ch => ch.querySelector('.challenge-checkbox')?.checked);
            roleContainer.querySelector('.role-heading')?.classList.toggle('dimmed', allComp);
        }});
        
        renderGoldLogChart();
        // --- DEBUG LOG ---
        const goldLog = JSON.parse(localStorage.getItem(LS_GOLD_LOG)) || [];
        debugGoldStats(dailyGoldTotal, sums.week, sums.running, goldLog);
    }}
    
    function handleStreakUpdate(isTicked) {{
        const checkedCount = Array.from(allCheckboxes).filter(cb => cb.checked).length;
        const currentStatus = localStorage.getItem(LS_CHALLENGE_STATUS);
        const lockedStreak = parseInt(localStorage.getItem(LS_STREAK_FOR_MULTIPLIER) || '0', 10);
        
        if (isTicked && checkedCount > 0 && currentStatus !== 'completed') {{
            const newStreak = lockedStreak + 1;
            setStreakCount(newStreak, true);
        }} else if (!isTicked && checkedCount === 0 && currentStatus === 'completed') {{
            setStreakCount(lockedStreak, false);
        }}
        updateCounters();
    }}

    // --- INIT ---
    
    const dailyKeyCheck = localStorage.getItem(LS_LAST_KNOWN_TIMESTAMP);
    if (dailyKeyCheck != PYTHON_CHALLENGE_TIMESTAMP) {{
        Object.keys(localStorage).forEach(k => {{ if(k.includes('_challenge_')) localStorage.removeItem(k); }});
    }}
    
    localStorage.setItem(LS_LAST_KNOWN_TIMESTAMP, PYTHON_CHALLENGE_TIMESTAMP);
    
    allCheckboxes.forEach(cb => {{
        const key = `${{PYTHON_CHALLENGE_TIMESTAMP}}_${{cb.id}}`;
        cb.checked = localStorage.getItem(key) === "true";
        if(cb.checked) cb.closest('div').classList.add('completed');
        
        cb.addEventListener('change', () => {{
            cb.closest('div').classList.toggle('completed', cb.checked);
            localStorage.setItem(key, cb.checked);
            handleStreakUpdate(cb.checked);
        }});
    }});

    document.getElementById('streak-up').addEventListener('click', () => {{ 
        localStorage.setItem(LS_STREAK_COUNT, Math.min(28, parseInt(localStorage.getItem(LS_STREAK_COUNT)||0)+1)); 
        localStorage.setItem(LS_STREAK_FOR_MULTIPLIER, localStorage.getItem(LS_STREAK_COUNT));
        updateCounters(); 
    }});
    document.getElementById('streak-down').addEventListener('click', () => {{ 
        localStorage.setItem(LS_STREAK_COUNT, Math.max(0, parseInt(localStorage.getItem(LS_STREAK_COUNT)||0)-1)); 
        localStorage.setItem(LS_STREAK_FOR_MULTIPLIER, localStorage.getItem(LS_STREAK_COUNT));
        updateCounters(); 
    }});

    document.querySelectorAll('.difficulty-toggle').forEach(toggle => {{
        const roleContainer = toggle.closest('.role-container');
        const roleName = roleContainer.querySelector('.role-heading').textContent.split('(')[0].trim().toLowerCase().replace(/[^a-z0-9]/g, '');
        const lsKey = `difficulty_${{roleName}}`;
        
        function setView(diff) {{
            roleContainer.querySelectorAll('.role-challenge').forEach(ch => ch.style.display = (ch.dataset.difficulty === diff) ? '' : 'none');
            toggle.dataset.difficulty = diff;
            const desc = diff === 'easy' ? 'Rank 1–5' : diff === 'med' ? 'Rank 6–14' : 'Rank 15+';
            toggle.textContent = `(${{diff.charAt(0).toUpperCase() + diff.slice(1)}}: ${{desc}})`;
        }}
        
        setView(localStorage.getItem(lsKey) || 'hard');
        
        toggle.addEventListener('click', () => {{
            if (toggle.classList.contains('dimmed-text')) return;
            const next = toggle.dataset.difficulty === 'easy' ? 'med' : toggle.dataset.difficulty === 'med' ? 'hard' : 'easy';
            localStorage.setItem(lsKey, next);
            setView(next);
            roleContainer.querySelectorAll('.role-challenge[style*="display: none"] .challenge-checkbox:checked').forEach(cb => {{
                cb.checked = false;
                localStorage.setItem(`${{PYTHON_CHALLENGE_TIMESTAMP}}_${{cb.id}}`, false);
            }});
            handleStreakUpdate(false);
        }});
    }});

    loadStreak();
    updateCounters();
    
    window.addEventListener('load', renderGoldLogChart);
    window.addEventListener('resize', renderGoldLogChart);
}});

document.addEventListener('DOMContentLoaded', () => {{
    document.getElementById('pauseBtn').addEventListener('click', () => {{
      fetch('http://127.0.0.1:6969/pause', {{ method: 'POST' }})
      .then(r => r.text()).then(d => alert(d)).catch(e => alert(e));
    }});
}});
</script>









'''





####################################################################################################################################
##                                                                                                                                ##
##                                                        HTML VERSION 2                                                          ##
##                                                                                                                                ##
####################################################################################################################################
# Get the appropriate date for the list of challenges and print it.
unix_time, _ = get_index_start_date(local_filename)
human_readable_date = get_human_readable_date(unix_time)
print(human_readable_date)
index_mod_date_str = get_index_mod_date_str(local_filename)
print("index_mod_date_str:  ",index_mod_date_str)
print("\n")

# Use a global start_timestamp from the get_index_start_date function call
start_timestamp, _ = get_index_start_date(local_filename)

html_output = f'''
<!DOCTYPE html><html>
<head>
    <meta charset="UTF-8" />
    <link rel="icon" href="./html/images/favicon.ico" type="image/x-icon" />
    <style>
        /* === Global styles === */
        body {{
          margin: 0;
          padding: 0;
          background-color: #000;
          display: flex;
          flex-direction: row;
          justify-content: flex-start;
          align-items: flex-start;
          font-family: Arial, sans-serif;
          gap: 10px;
          flex-wrap: wrap;
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

        /* === Layout containers === */
        .page-container {{
          display: flex;
          flex-direction: column;
          min-height: 100vh;
        }}
        .main-container {{
          display: flex;
          flex-wrap: wrap;
          justify-content: flex-start;
          align-items: flex-start;
          gap: 10px;
          margin: 0;
          padding: 0;
        }}

        .left-column {{
          display: flex;
          flex-direction: column;
          max-width: 850px;
          width: 100%;
        }}

        .sidebar-container {{
          display: block;
          width: 450px;
          background-color: #111;
          color: #eee;
          /*border: 2px solid orange;*/
          padding: 15px;
          box-sizing: border-box;
          font-family: Arial, sans-serif;
          overflow: visible; /* allow images to stick outside */
          /* margin-left: -10px;shift left */
        }}
        
        
        /* COLUMN 3: BONUS INFO - Fixed to 250px wide */
        .bonus-container {{
            padding: 7px;
            background-color: #111; /*Dark grey background*/
            display: flex;
            flex-direction: column;
            /* --- FIXED WIDTH CHANGES --- */
            width: 250px; 
            min-width: 250px; 
            max-width: 850px;
            /*flex-shrink: 0; Ensures this column does not shrink, prioritizing the fixed width */
            /* --------------------------- */
        }}
        

        .stats-heading {{
            font-family: 'RDOFont', sans-serif;
            font-size: 1.3rem;
            margin-top: 0;
            margin-bottom: 5px;
            border-bottom: 2px solid #555;
            padding-bottom: 5px;
            color: #666666; /* PRESERVED: Keeping the original color */
            text-shadow: 2px 2px 4px rgba(0,0,0,0.7);
            
        }}
        
        .stats-text {{
            font-family: 'hapna', sans-serif; /* Example font */
            font-size: .9rem;
            color: #aaa;
            white-space: pre-wrap; /* allows \\n line breaks in descriptions */
            letter-spacing: -0.05em; 
            margin-top: 0;
            margin: 0;
        }}

        /* *** FIX: Styling for non-shifting streak adjustment controls *** */
        #streak-controls {{
            opacity: 0;
            visibility: hidden;
            color: #999;
            cursor: pointer;
            user-select: none;
            font-size: 0.8rem;
            margin-left: 10px;
            transition: opacity 0.2s ease-in-out, visibility 0.2s ease-in-out;
        }}
        #streak-container:hover #streak-controls {{
            opacity: 1;
            visibility: visible;
        }}
        #streak-up, #streak-down {{
            padding: 0 4px;
        }}
        #streak-up:hover, #streak-down:hover {{
            color: #fff;
        }}
        
     
        
        
        /* Ensure the animation class uses the 1000ms duration */
        .gold-exciting-flash {{
            animation: simpleGoldGlow 1000ms ease-out forwards;
        }}

        /* Define the simple glow keyframes */
        /* Ensure the animation class uses the 1ms duration for an instant state change */
        .gold-exciting-flash {{
            animation: instantWhiteGlow 1ms forwards;
        }}

        @keyframes instantWhiteGlow {{
            /* 0% Start: Text and glow go instantly white */
            0% {{
                color: white !important; 
                text-shadow: 
                    0 0 2px white,
                    0 0 4px #eeeeee; /* Strong white/silver glow */
                opacity: 1;
            }}
            
            /* 100% End: We keep it at the flash state so the JavaScript timeout controls the duration */
            100% {{
                color: white !important;
                text-shadow: 
                    0 0 3px white,
                    0 0 6px #eeeeee;
                opacity: 1;
            }}
        }}
        
        /* Set the animation class to use the correct keyframes and the JS duration */
        .gold-exciting-flash {{
            /* The 1000ms duration is crucial, matching your JavaScript setTimeout */
            animation: instantWhiteGlow 1000ms forwards;
        }}

            


        .banner-container {{
          position: sticky;
          top: 0;
          z-index: 10; /* stays above other content */
          
          
          width: 100%;
          max-width: 850px;
          min-width: 400px;
          background-color: #000;
          /*border: 2px solid blue;*/
          box-sizing: border-box;
          padding: 10px;
          color: #eee;
        }}

        .banner-image-wrapper {{
          position: relative;
          width: 100%;
        }}

        .banner-image {{
          width: 100%;
          height: auto;
          display: block;
        }}

        .banner-text-overlay {{
          position: absolute;
          top: -3%;
          left: 50%;
          transform: translateX(-50%);
          color: white;
          text-align: center;
          width: 90%;
          text-shadow: 2px 2px 4px rgba(0,0,0,0.7);
          pointer-events: none;
          font-family: 'RDOFont', sans-serif;
        }}

        .banner-title {{
          font-size: 2.5rem;
          margin: 10px 0;
          text-shadow:
            -2px -2px 0 #000,
             2px -2px 0 #000,
            -2px  2px 0 #000,
             2px  2px 0 #000;
        }}

        .banner-date {{
          font-size: 1.4rem;
          margin-bottom: 10px;
          margin-top: -15px;
          text-shadow:
           -1px -1px 2px #000,
            1px -1px 2px #000,
           -1px  1px 2px #000,
            1px  1px 2px #000;
        }}

        .challenge-counters {{
          position: absolute;
          bottom: 10px;
          left: 0;
          right: 0;
          display: flex;
          justify-content: space-between;
          padding: 0 15px;
          font-size: 1.25rem;
          color: white;
          text-shadow: 3px 3px 2px rgba(0,0,0,0.6);
          pointer-events: none;
          font-family: 'RDOFont', sans-serif;
          transform: scaleY(1.15); /* Increase font height */
          
        }}

        .challenge-counters > div {{
          white-space: nowrap;
        }}

        .challenge-counters span {{
          display: inline-block;
          width: 4ch;
          text-align: right;
        }}
        
        .counter-glow {{
          color: white;
          text-shadow:
            0 0 5px rgba(255, 255, 160, 0.75),  /* yellow glow with an opacity (0.75) */
            0 0 10px rgba(255, 255, 160, 0.75),
            0 0 15px rgba(255, 255, 160, 0.75);
          transition: text-shadow 0.3s ease;
        }}
        
        @keyframes counterPop {{
          0% {{
            transform: scale(1);
          }}
          50% {{
            transform: scale(1.3);
          }}
          100% {{
            transform: scale(1);
          }}
        }}

        .counter-pop {{
          animation: counterPop 0.4s ease forwards;
        }}
        
        

        .general-challenges-container {{
          width: 100%;
          max-width: 850px;
          margin: 0 auto;
          background-color: #111;
          padding: 15px;
          box-sizing: border-box;
          color: white;
          font-family: 'hapna', sans-serif;
          font-size: 1.25rem;
          text-shadow: 1px 1px 2px rgba(0,0,0,0.6);
          /*border: 2px solid green;*/
        }}



/* ############################################################# */
/*  Role challenges switching logic as browser viewport narrows  */
/* ############################################################# */
        
        /* NEW: Rule to hide the bonus container when screen is 1600px or less (The Requirement) */
        @media (max-width: 1600px) {{
            .bonus-container {{
                display: none; 
          }}
        }}
        
        
        
        /* Narrow screens: column layout, sidebar below main */
        @media (max-width: 1320px) {{
          body {{
            flex-direction: column;
            align-items: center;
          }}
          
            .main-container {{
            flex-direction: column;
            align-items: center;
            width: 100%;    /* allow children to fill horizontally */
            align-items: stretch; /* <— THIS is the key */
            min-width: 420px;
          }}
          
          .sidebar-container {{
            width: 100% !important; 
            max-width: 850px !important;
            margin-left: 0;    /* center below main container */
          }}      
        }}

        /* === Challenge checkboxes with wrapped text aligned properly === */
        .challenge label {{
          display: flex; /* container */
          align-items: flex-start;  /* Align to the top of the checkbox */
          gap: 8px;                 /* Space between checkbox and text */
          position: relative; /* for absolute checkbox */
          padding-left: 0px; /* reserve space for checkbox */
          cursor: pointer;
          white-space: normal;
          line-height: 1.3;
        }}
        
        .challenge:first-of-type label {{
          margin-top: -8px; /* adjust as needed */
        }}

        /* Position the checkbox at the left of label */
        .challenge-checkbox {{
          width: 14px;
          height: 14px;
          margin: 0;
          margin-top: 6px;  /* Optional: better vertical alignment */
          appearance: none; /* Remove default styling */
          -webkit-appearance: none;
          background-color: #888; /* Default background */
          /* background-color: orange; /* TEST */*/
          border: 2px solid #333;
          border-radius: 3px;
          cursor: pointer;
        }}
        
        .challenge-checkbox:checked {{
          background-color: #222;
          background-color: #b00000;  /* Dark Red Colour */
          border: 2px solid #333;
          border-radius: 3px;
        }}
        
        /* add a checkmark */
        .challenge-checkbox:checked::before {{
          content: "✔";
          display: block;
          text-align: top;
          color: white;
          font-size: 12px;
          line-height: 10px;
        }}
        

        /* Text span with hanging indent:
           first line starts after checkbox,
           wrapped lines align under text, NOT under checkbox */
           
        .challenge-text {{
          display: block;
          display: block;
          word-wrap: break-word;
          max-width: 100%;
          user-select: none;
        }}


        /* Optional: styling for challenge description */
        .challenge-desc {{
          margin-left: 22px; /* indent to align with text */
          font-size: 1rem;
          color: #999999;
          padding-bottom: 7px;
          white-space: pre-wrap;  /* Preserve \\n line breaks and wrap long lines */
          line-height: 1.2;  /* smaller numbers = tighter spacing */
        }}
        
        .thin-divider {{
          border: none;
          border-top: 1px solid #444;
          /*width: 825px;    Allowing this will kill the word-wrap and dynamic resizing of the general challenges*/
          max-width: 100%;
          margin: 8px auto;
        }}


    
        .role-heading {{
            font-family: 'RDOFont', sans-serif;  /* Example font, change as needed */
            font-size: 1.5rem;
            color: #eee;
            margin: -4px 0 0 0;
            
            text-shadow:
            -3px -3px 0 #000,  
             3px -3px 0 #000,
            -3px 3px 0 #000,
             3px 3px 0 #000;
             text-shadow: 1px 1px 2px rgba(0,0,0,0.6);
            letter-spacing: 0.05em; /* Adjust this value to your liking */
            padding-left: 20px; /* Increase this to move the text right */
            background-color: transparent;
            overflow: visible;
            /*Adding picture behind the heading text*/
            z-index: 0; /* Create a stacking context */
            background-image: url('HTML/images/RDO_Role_Challenges_Header3.png');
            background-repeat: no-repeat;
            background-position: 2px center;
            background-size: 410px 35px;
            
            display: flex;
            justify-content: space-between;
            align-items: center;
    
        }}
            /* Space between different role challenges */
            .role-challenge {{
              margin-bottom: .6rem; /* adjust as needed */
            }}

        .role-challenge-text {{
            font-family: 'hapna', sans-serif; /* Example font */
            font-size: 1.05rem;
            color: #eee;
            display: inline-block; /* keeps it inline for natural text flow */
            line-height: 1.1;
            display: inline;
            transform: scaleY(1.1); /* Increase font height */


        }}
        .role-challenge-desc {{
            font-family: 'hapna', sans-serif; /* Example font */
            font-size: 1rem;
            color: #aaa;
            margin-left: 6px; /* aligns under the role challenge text */
            white-space: pre-wrap; /* allows \\n line breaks in descriptions */
            transform: scaleX(0.925); /* reduce width to 90% */
        }}
        
        /*  ##### Role Challenges Tickboxes ##### */
        
        /* Unchecked state */
        .role-challenge input[type="checkbox"] {{
            width: 14px;
            height: 14px;
            margin: 0;
            margin-top: 0px;  /* Optional: better vertical alignment */
            appearance: none; /* Remove default styling */
            -webkit-appearance: none;
            background-color: #888; /* Default background */
            border: 2px solid #333;
            border-radius: 3px;
            cursor: pointer;
        }}
        
        /* Checked state */
        .role-challenge input[type="checkbox"]:checked {{
            background-color: #222;
            background-color: #b00000;  /* Dark Red Colour */
            border: 2px solid #333;
            border-radius: 3px;
        }}
        .role-challenge input[type="checkbox"]:checked::before {{
            content: "✔";
            display: block;
            text-align: center;
            color: white;
            font-size: 12px;
            line-height: 14px;
            vertical-align: middle;
            position: relative;
            top: -2px; /* Adjust this value to fine-tune the vertical alignment */
        }}
        
        
        .role-challenge-label {{
          display: flex;
          align-items: baseline; /* aligns checkbox with first line of text */
          gap: 0.5em;               /* space between checkbox and text */
          cursor: pointer;
          user-select: none;
          -webkit-user-select: none; /* Safari */
          -moz-user-select: none; /* Firefox */
          -ms-user-select: none; /* IE/Edge */
          
        }}
        
        /* Using this to scale role challenge text */
        .text-scale {{
            display: inline-block;
            transform: scaleX(0.9);
            transform-origin: left;
        }}
        
        /* Makes it clickable */
        .difficulty-toggle {{
            cursor: pointer;
            user-select: none;
            font-size: 0.6em;  /* adjust if needed */
            margin-right: 10px; /* adjust px as you like */
            color: #dd0000;  /* Dark Red Colour */
            transform: scaleY(1.2); 
            /* Mid-grey outline effect */
            text-shadow:
              -1px -1px 0 #111111,
               1px -1px 0 #111111,
              -1px  1px 0 #111111,
               1px  1px 0 #111111;
            }}
        
        /* Dimming the difficulty-toggle */
        .dimmed-text {{
            opacity: 0.5;
            pointer-events: none;
            user-select: none;
        }}


        
        

/* ==== Checkbox Challenge Completion Styling ==== */


        /* When checkbox is checked, style the following sibling text */
        .challenge-checkbox:checked + .challenge-text,
        .challenge-checkbox:checked + .role-challenge-text {{
          color: #555;
          text-decoration: line-through;
          opacity: 0.5;
        }}


        /* This dims both the challenge text and the description when the challenge is completed */
        .challenge.completed .challenge-text,
        .challenge.completed .challenge-desc,
        .role-challenge.completed .role-challenge-text,
        .role-challenge.completed .role-challenge-desc {{
          color: #555 !important;
          /* Uncomment if you want strikethrough and opacity effect */
          text-decoration: line-through;
          opacity: 0.85;
        }}
        
        
        .role-completed {{
          color: #555;
          font-weight: bold;
        }}


        /* Dim role challenges and headings when all 9 role challenges are completed */
        .role-completed .role-challenge-text,
        .role-completed .role-heading {{
          opacity: 0.5; /* dim text and headings */
          color: #666;  /* optional dim color */
          transition: opacity 0.3s ease;
          background: orange;
        }}

        /* Keep checkboxes fully visible and interactive */
        .role-completed .challenge-checkbox {{
          opacity: 1 !important;
          pointer-events: auto;
        }}


        .role-challenge-desc.dimmed {{
          opacity: 0.5;
          color: #666666;
          transition: opacity 0.3s ease, color 0.3s ease;
        }}



/* ==== Global Checkbox Role Challenge Completion Styling (9 out of 9)==== */


        /* Global dimming for all text elements when all roles are complete */
        .all-roles-completed .role-heading,
        .all-roles-completed .role-challenge-label span, /* Targets the Challenge Name */
        .all-roles-completed .role-challenge-desc, /* ✅ NEW: Targets the Description Element */
        .all-roles-completed .role-challenge p /* General Paragraph Fallback */
        {{
          color: #888 !important; 
          opacity: 0.5 !important; /* Forces dimming, overriding competing rules */
          transition: color 0.3s, opacity 0.3s;
        }}

        /* When 9/9 roles are complete, make the entire DIV of any unticked challenge non-interactive */
        .all-roles-completed .role-challenge:not(.completed) {{
            pointer-events: none;
            cursor: default;
        }}

        /* Then, specifically dim the checkbox inside that disabled DIV for visual feedback */
        .all-roles-completed .role-challenge:not(.completed) input[type="checkbox"] {{
            opacity: 0.35 !important;
        }}
        
        
    /*############ RDO-CLOCK SECTION ############*/        
        .rdo-clock {{
            position: absolute;
            bottom: 5px;  /* Position near the bottom of the banner */
            left: 47.5%;
            transform: translateX(-50%);
            transform: translateY(-2px);  /* Negative value moves it up */
            font-family: 'RDOFont', sans-serif;
            font-size: calc(1.5vw + 0.8rem);
            color: #white;
            text-shadow:
             -4px -4px 4px #cf0202,
              4px -4px 4px #cf0202,
             -4px  4px 4px #cf0202,
              4px  4px 4px #cf0202;
        }}
        
        .rdo-clock.night-glow {{
            text-shadow:
            -4px -4px 4px #0d2542,
             4px -4px 4px #0d2542,
            -4px  4px 4px #0d2542,
             4px  4px 4px #0d2542;
            /*color: #white;               Optional: change text color too */
}}



    /*############ API CREDIT SECTION ############*/
        .api-credit-separator {{
            border: none;
            height: 15px;               /* Thickness of the line */
            background-color: black;
            margin: 10px -15px;         /* Vertical spacing, and negative horizontal to counter the container padding so it stretches all the way across */
        }}


        /* API credit styling */
        .api-credit {{
          margin-top: auto;
          margin-bottom: 0px;
          padding: 0px 0 0px 5px;
          font-size: 0.75rem;
          color: #5b5b5b;
          font-family: Arial, sans-serif;
          text-align: right;
          line-height: 1
        }}
        .api-credit a {{
          color: #5b5b5b;
          text-decoration: none;
        }}
        .api-credit a:hover {{
          text-decoration: underline;
          color: #8e7878;
        }}
        
        
     /*############ PAUSE RDR BUTTON SECTION ############*/       
        .pause-rdr2-button {{
            position: absolute;
            top: 12px;
            left: 12px;
            z-index: 9999;
            padding: 6px 10px;
            background-color: #b00000;
            color: white;
            border: none;
            border-radius: 4px;
            font-size: 0.9rem;
            cursor: pointer;
            font-family: 'hapna', sans-serif;
            box-shadow: 1px 1px 3px rgba(0,0,0,0.4);
            transition: background-color 0.3s ease;
        }}
        .pause-rdr2-button:hover {{
            background-color: #900000;
        }}
        
        #pauseBtn {{
          position: absolute;
          top: 5px;
          right: 10px;
          width: 100px;
          cursor: pointer;
          display: none;    /* hidden by default */
          filter: drop-shadow(2px 2px 4px rgba(0, 0, 0, 0.6));
        }}
        
        #pauseBtn:hover {{
          filter: drop-shadow(0 0 8px rgba(255, 255, 255, 0.8));
          transform: scale(1.05);
        }}

    /*############ GOLD LOG CHART ############*/
        #gold-log-chart-container {{
            display: flex;
            justify-content: flex-start; /* Aligns bars to the left */
            align-items: flex-end;
            height: 75px;
            width: 100%;
            background-color: #151515;
            border: 1px solid #000;
            border-radius: 8px;
            padding: 2px;
            box-sizing: border-box;
            gap: 2px;
            overflow: hidden; /* Prevents scrollbar */
        }}

        .chart-bar-wrapper {{
            display: flex;
            justify-content: center;
            align-items: flex-end;
            height: 100%;
        }}

        .chart-bar {{
            width: 100%;
            background-color: #B8860B; /* Darker Gold */
            border-radius: 2px 2px 0 0;
            transition: background-color 0.2s ease;
            min-height: 1px;
        }}
        
        .chart-bar-wrapper:hover .chart-bar {{
            background-color: #FFE957; /* Brighter gold for highlight */
        }}
        
        .chart-info-display {{
            color: #5b5b5b;
            font-family: 'hapna', sans-serif; /* Use hapna font */
            font-size: 0.8rem;
            text-align: left; /* Justify left */
            padding-left: 5px; /* Add some padding */
            height: 1.2em;
            margin-top: -3px; /* reduce or increase to move graph's 'tooltip' text up or down */
            transition: color 0.2s;
            letter-spacing: -0.05em; /* Add this line for narrower text */
        }}
        
    </style>
</head>
<body>
    <div class="main-container">
        <div class="left-column">
            <div class="banner-container">
                <div class="banner-image-wrapper">
                    <img src="HTML/images/RDO_Banner_Wide.jpg" alt="Banner" class="banner-image"/>
                    <img id="pauseBtn" src="HTML/images/RDO_PauseStopwatch.png" alt="Pause RDO" title="Pause RDO"
                         style="position:absolute; top:0px; left:10px; width:50px; cursor:pointer;" />                    
                    <div class="banner-text-overlay">
                        <h1 class="banner-title">Daily Challenges</h1>
                        <div class="banner-date">{human_readable_date}</div>
                    </div>
                    <div class="challenge-counters">
                        <div>General Challenges <span id="general-counter">(0/7)</span></div>
                        <div>Role Challenges <span id="role-counter">(0/9)</span></div>
                    </div>
                    <div class="rdo-clock" id="rdo-clock">
                        --:--
                    </div>
                </div>
            </div>

            <div class="general-challenges-container">
                {html_general}
            </div>
        </div>

<!-- COLUMN 2: ROLE CHALLENGES -->
        <div class="sidebar-container" id="roles-container">
            {selected_html_roles}
            
            <hr class="api-credit-separator" />
            
            <div class="api-credit">
                <span class="api-label">Data provided by:&nbsp;</span>
                <a href="https://rdo.gg/api" target="_blank" class="api-link">rdo.gg API</a>
            </div>
        </div>

<!-- COLUMN 3: BONUS INFO (Now the final column, cleared of content) -->
        <div class="bonus-container" id="bonus-container">
            <h3 class="stats-heading" style="color: #666666;">Bonus Info</h3>
            
            <div style="padding: 2px; border: 1px solid #000; border-radius: 8px; background-color: #151515; text-align: left; color: #E0E0E0; font-family: sans-serif;">
                
                <!-- *** FIX: Restructured Streak HTML for proper alignment *** -->
                <p class="stats-text" id="streak-container" style="margin-bottom: 2px; display: flex; justify-content: space-between; align-items: center; width: 100%;">
                    <span style="display: flex; align-items: center; white-space: nowrap;">
                        <span style="font-weight: 500;">Daily Challenge Streak:</span>
                        <span id="streak-controls">
                            <span id="streak-down">▼</span><span id="streak-up">▲</span>
                        </span>
                    </span>
                    <span id="current-streak" style="color: #FFC107; text-align: right;">0 Days</span>
                </p>

                <p class="stats-text" style="margin-bottom: 2px; display: flex; justify-content: space-between; width: 100%;">
                    <span style="font-weight: 500;">Gold Per Challenge:</span>
                    <span id="gold-per-challenge" style="color: #FFC107; text-align: right;">0.00 Gold Bars</span>
                </p>
                
                <p class="stats-text" style="margin-bottom: 2px; display: flex; justify-content: space-between; width: 100%;">
                    <span style="font-weight: 500;">Completion Reward:</span>
                    <span id="completion-bonus-reward" style="color: #FFC107; text-align: right;">0.00 Gold Bars</span>
                </p>
                
                <p class="stats-text" style="margin-bottom: 2px; display: flex; justify-content: space-between; width: 100%;">
                    <span style="font-weight: 500;">Daily Gold Total:</span>
                    <span id="daily-gold-total" style="color: #FFC107; text-align: right;">0.00 Gold Bars</span>
                </p>
                
                <p class="stats-text" style="margin-bottom: 2px; display: flex; justify-content: space-between; width: 100%;">
                    <span style="font-weight: 500;">Streak Week Gold Total:</span>
                    <span id="cycle-gold-total" style="color: #FFC107; text-align: right;">0.00 Gold Bars</span>
                </p>
                
                <p class="stats-text" style="display: flex; justify-content: space-between; width: 100%;">
                    <span style="font-weight: 500;">Streak Gold Total:</span>
                    <span id="streak-gold-total" style="color: #FFC107; text-align: right;">0.00 Gold Bars</span>
                </p>
                
            </div>

            <!-- Gold Log Chart Container -->
            <h3 class="stats-heading" style="color: #666666; margin-top: 15px;">Gold Log (Last 28 Days)</h3>
            <div id="gold-log-chart-container">
                <!-- Bars will be injected here by JavaScript -->
            </div>
            <div id="chart-info-display" class="chart-info-display">&nbsp;</div>


        <!-- END COLUMN 3 -->
    </div> 
  
  
<!-- Default Statcounter code for RDO_dailies - codedunky
https://codedunky.github.io/RDO_dailies/ -->
<script type="text/javascript">
var sc_project=13147326; 
var sc_invisible=1; 
var sc_security="51162dbd"; 
</script>
<script type="text/javascript"
src="https://www.statcounter.com/counter/counter.js"
async></script>
<noscript><div class="statcounter"><a title="Web Analytics"
href="https://statcounter.com/" target="_blank"><img
class="statcounter"
src="https://c.statcounter.com/13147326/0/51162dbd/1/"
alt="Web Analytics"
referrerPolicy="no-referrer-when-downgrade"></a></div></noscript>
<!-- End of Statcounter Code -->  
  
  
{javascript_code}
  
</body>
</html>
'''

# Write to file
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_output)

print("HTML output written to index.html")