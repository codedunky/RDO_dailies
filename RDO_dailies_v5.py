

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


# Set the path to your local index.json file in a relative subfolder called 'jsonFiles'
script_dir = os.path.dirname(os.path.abspath(__file__))  # the directory where the script is
os.makedirs(os.path.join(script_dir, "jsonFiles"), exist_ok=True)  # Check folder exists

local_filename = os.path.join(script_dir, "jsonFiles", "index.json") # Creates the filepath and assign to variable
local_filename_nazar = os.path.join(script_dir, "jsonFiles", "nazar.json") # Creates the filepath for Nazar location and assign to variable
print("Initial 'local_filename':  ", local_filename)
print("Initial 'local_filename_nazar':  ", local_filename_nazar)


####################################################################################################################



    
# #### CONFIG FLAGS #### #
#####################################################
#   Override mode: "auto" or "forceX"
#   auto   = rotate based on date
#   forceX = force a specific number (e.g. "force1", "force3").
#            If the number is higher than available descriptions, 
#            it uses the highest one available.
DESCRIPTION_MODE = "auto"


# Set a variable to control if index.json will download without user prompt
autoDownload = True


# Block all API downloads (True = offline mode/testing, False = normal operation)
BLOCK_DOWNLOADS = False 


# Set to True to see [Desc #X] at the end of text
DEBUG_DESCRIPTION = True
  

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
    "ipurple":         "\033[95m",
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
CURRENT_DEBUG_LEVEL = 1

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
    Reads the index JSON file and returns start time.
    Silently defaults to current time if file is missing.
    """
    now = int(time.time())
    date_str = datetime.datetime.utcfromtimestamp(now).strftime('%Y-%m-%d')

    if not os.path.exists(local_filename):
        # File missing: return current time, no error print needed
        return now, date_str

    try:
        with open(local_filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        start_time = data.get('startTime')
        if start_time:
            dt = datetime.datetime.utcfromtimestamp(start_time)
            date_str = dt.strftime('%Y-%m-%d')
            return start_time, date_str
        else:
            return now, date_str
    except Exception as e:
        # Only print error if file exists but is corrupt
        debug_print("L1", "bred", f"Error reading existing index.json: {e}")
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
    if not os.path.exists(local_filename):
        return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
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
# Convert timestamp to readable format for debug
index_expiry_readable = datetime.datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')

if end_time < now:
    debug_print("L1", "idarkyellow", f"INDEX: File expired (Expires: {index_expiry_readable}). Downloading new file...")

    # Decide whether to prompt or just download
    if file_exists:
        if autoDownload:
            debug_print("L3", "bgreen", "INDEX: File exists locally, but autoDownload is True")
            download_now = True
            print("INDEX: download_now: ",download_now)
        else:
            user_input = input("INDEX: Do you want to download the latest index.json from rdo.gg? (y/n): ").strip().lower()
            download_now = (user_input == 'y')
    else:
        # No file exists, so download immediately
        download_now = True
else:
    # This is the new "Valid" message
    debug_print("L1", "byellow", f"INDEX: File valid (Expires: {index_expiry_readable}). Using cached json.")
    download_now = False
    
    
# --- BLOCK DOWNLOADS CHECK ---
if BLOCK_DOWNLOADS and download_now:
    debug_print("L1", "bred", "INDEX: Download skipped (BLOCK_DOWNLOADS = True).")
    download_now = False
# ----------------------------------    
    

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
        
        





    
# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# NAZAR LOCATION & IMAGE LOGIC
# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

nazar_url = "https://api.rdo.gg/nazar"
nazar_data = {}
nazar_location_text = "Location Unknown"

# Define Image Paths
placeholder_path = "HTML/images/nazar/RDO_Nazar___Placeholder.png"
nazar_final_img_src = placeholder_path 
nazar_zoom_src = ""
nazar_has_zoom = "false"
nazar_cursor_style = "default"

# 1. Check/Download Logic
download_nazar = False
valid_nazar_data = False 
now = int(time.time())

if os.path.exists(local_filename_nazar):
    try:
        with open(local_filename_nazar, 'r', encoding='utf-8') as f:
            nazar_data = json.load(f)
        nazar_end_time = nazar_data.get('endTime', 0)
        
        if nazar_end_time < now:
            debug_print("L1", "idarkyellow", f"NAZAR: Nazar file expired. Downloading...")
            download_nazar = True
            valid_nazar_data = False 
        else:
            download_nazar = False
            valid_nazar_data = True 
            nazar_expiry_readable = datetime.datetime.fromtimestamp(nazar_end_time).strftime('%Y-%m-%d %H:%M:%S')
            debug_print("L1", "byellow", f"NAZAR: File valid (Expires: {nazar_expiry_readable}). Using cached json.")

    except Exception as e:
        print(f"NAZAR: Error reading local nazar.json: {e}")
        download_nazar = True
        valid_nazar_data = False
else:
    download_nazar = True
    valid_nazar_data = False

# --- NEW: BLOCK DOWNLOADS CHECK ---
if BLOCK_DOWNLOADS and download_nazar:
    debug_print("L1", "ired", "NAZAR: Download skipped (BLOCK_DOWNLOADS = True).")
    download_nazar = False
# ----------------------------------

if download_nazar:
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(nazar_url, headers=headers)
        with urllib.request.urlopen(req) as response:
            data_bytes = response.read()
            new_nazar_data = json.loads(data_bytes.decode('utf-8'))
            with open(local_filename_nazar, 'w', encoding='utf-8') as f:
                json.dump(new_nazar_data, f, indent=2)
            nazar_data = new_nazar_data
            valid_nazar_data = True 
            print("NAZAR: downloaded new nazar.json file")
    except Exception as e:
        print(f"NAZAR: Error during Nazar download: {e}")

# 2. Process Data ONLY if valid
if valid_nazar_data:
    raw_state = nazar_data.get('state', 'unknown_state')
    raw_location = nazar_data.get('location', 'unknown_location')

    def prettify_nazar_key(key):
        if not key or not isinstance(key, str): return "Unknown"


        # 1. Parse and Strip Prefix (Standard Logic)
        # We convert to lower first to ensure consistency
        parts = key.lower().split('_')

        # Logic: If starts with "p_3_" or similar, strip the first two parts
        if len(parts) > 2 and len(parts[0]) == 1 and parts[1].isdigit():
            clean_parts = parts[2:]
        else:
            clean_parts = parts

        # 2. Reconstruct the "clean" key (e.g., "ocreaghs_run")
        clean_key = "_".join(clean_parts)
        
        # 3. Define Overrides for specific spelling/punctuation
        NAZAR_OVERRIDES = {
            "ocreaghs_run": "O'Creagh's Run",
            "macfarlanes_ranch": "MacFarlane's Ranch"
            }

        debug_print("L2", "iyellow", "NAZAR: clean_key:", clean_key)

        # 4. Check if the raw key exists in overrides (case-insensitive)
        if clean_key in NAZAR_OVERRIDES:
            debug_print("L2", "ipurple", "NAZAR: Override exists")
            return NAZAR_OVERRIDES[clean_key]

        return " ".join(word.title() for word in clean_parts)

    nazar_location_text = prettify_nazar_key(raw_location)

    nazar_img_filename = f"RDO_Nazar___{raw_state}___{raw_location}.png"
    nazar_zoom_filename = f"RDO_Nazar___{raw_state}___{raw_location}___zoom.png"

    relative_img_path = f"HTML/images/nazar/{nazar_img_filename}"
    absolute_img_path = os.path.join(script_dir, "HTML", "images", "nazar", nazar_img_filename)
    relative_zoom_path = f"HTML/images/nazar/{nazar_zoom_filename}"
    absolute_zoom_path = os.path.join(script_dir, "HTML", "images", "nazar", nazar_zoom_filename)

    if os.path.exists(absolute_img_path):
        nazar_final_img_src = relative_img_path
        debug_print("L2", "NAZAR: Found specific Nazar map image.")
    else:
        nazar_final_img_src = placeholder_path
        debug_print("L2", "NAZAR: Specific image not found, using placeholder.")

    if os.path.exists(absolute_zoom_path):
        nazar_zoom_src = relative_zoom_path
        nazar_has_zoom = "true"
        nazar_cursor_style = "pointer"
        debug_print("L2", "NAZAR: Found zoomed Nazar image.")
    else:
        nazar_zoom_src = ""
        nazar_has_zoom = "false"
        nazar_cursor_style = "default"

else:
    # Logic for when data is invalid (Expired AND Download Failed/Blocked)
    debug_print("L1", "ired", "NAZAR: Data invalid/expired/blocked. Using placeholder.")
    nazar_location_text = "Location Unknown"
    nazar_final_img_src = placeholder_path
    nazar_zoom_src = ""
    nazar_has_zoom = "false"
    nazar_cursor_style = "default"



# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# EVENTS JSON DOWNLOAD CHECKS
# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------  


local_filename_events = os.path.join(script_dir, "jsonFiles", "events.json") 
events_url = "https://api.rdo.gg/events/"
download_events = False

# Short cooldown for "Update Day" (Tuesday/Wednesday) - 3 Hours
COOLDOWN_SHORT = 10800 

# --------------------------------------------------------------------------------------
# 1. CALCULATE TIMESTAMPS
# --------------------------------------------------------------------------------------
now_utc = datetime.datetime.utcnow()
today_9am = now_utc.replace(hour=9, minute=0, second=0, microsecond=0)
days_since_tuesday = (now_utc.weekday() - 1) % 7

# Adjust to find the most recent Tuesday 9 AM
if days_since_tuesday == 0 and now_utc < today_9am:
    days_since_tuesday = 7

latest_window_start_dt = today_9am - datetime.timedelta(days=days_since_tuesday)
latest_window_start_ts = latest_window_start_dt.timestamp()

debug_print("L1", "igreen", f"EVENTS: Current Update Window started: {latest_window_start_dt}")

# --------------------------------------------------------------------------------------
# 2. CHECK LOCAL FILE STATUS
# --------------------------------------------------------------------------------------
if os.path.exists(local_filename_events):
    try:
        # Get when we LAST checked the API (Physical file modification time)
        last_api_check_ts = os.path.getmtime(local_filename_events)
        
        # Read the internal content date (When Rockstar actually updated)
        with open(local_filename_events, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
        
        local_content_ts = existing_data.get('updated', 0)
        readable_local_date = datetime.datetime.fromtimestamp(local_content_ts)
        debug_print("L1", "igreen", f"EVENTS: Local File Internal Date: {readable_local_date}")

        # ------------------------------------------------------------------
        # DECISION LOGIC
        # ------------------------------------------------------------------
        
        # 1. SUCCESS: The file contains data from the current window.
        if local_content_ts >= latest_window_start_ts:
            debug_print("L0", "bgreen", "EVENTS: Schedule is fully up to date.")
            download_events = False

        # 2. OLD DATA: The file is old. Have we checked recently?
        else:
            # Did we check the API *after* the update window opened?
            checked_this_week = last_api_check_ts > latest_window_start_ts
            
            if not checked_this_week:
                debug_print("L0", "idarkyellow", "EVENTS: New update window open. We haven't checked yet. Downloading...")
                download_events = True
            else:
                # We HAVE checked this week, but the data was still old.
                # Should we keep checking? Depends on the day.
                
                # 0=Mon, 1=Tue, 2=Wed, 3=Thu...
                current_day = now_utc.weekday()
                
                # If it's Tuesday (1) or Wednesday (2), keep checking periodically
                if current_day in [1, 2]:
                    time_since_check = int(time.time()) - last_api_check_ts
                    if time_since_check < COOLDOWN_SHORT:
                        debug_print("L0", "bgreen", f"EVENTS: Update late (Tue/Wed). Keeping cache ({int(time_since_check/60)} mins old).")
                        download_events = False
                    else:
                        debug_print("L0", "idarkyellow", "EVENTS: Update late (Tue/Wed). Cooldown expired. Checking API again...")
                        download_events = True
                
                # If it's Thursday through Monday, assume no update is coming.
                else:
                    debug_print("L0", "byellow", "EVENTS: Old data detected, but we already checked this week. Assuming no update. (Thurs-Mon Logic)")
                    download_events = False

    except Exception as e:
        print(f"EVENTS: Error reading local file ({e}). Forcing download.")
        download_events = True
else:
    debug_print("L0", "idarkyellow", "EVENTS: File not found. Downloading...")
    download_events = True

# --- BLOCK DOWNLOADS CHECK ---
if 'BLOCK_DOWNLOADS' in globals() and BLOCK_DOWNLOADS and download_events:
    debug_print("L1", "bred", "EVENTS: Download skipped (BLOCK_DOWNLOADS = True).")
    download_events = False

# --------------------------------------------------------------------------------------
# 3. PERFORM DOWNLOAD
# --------------------------------------------------------------------------------------
if download_events:
    try:
        debug_print("L2", "igreen", "EVENTS: Downloading events.json from API...")
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(events_url, headers=headers)
        
        with urllib.request.urlopen(req) as response:
            data_bytes = response.read()
            data_str = data_bytes.decode('utf-8')
            new_events_data = json.loads(data_str)
            
            # Write to file (This updates the 'mtime' used for tracking 'last_api_check_ts')
            with open(local_filename_events, 'w', encoding='utf-8') as f:
                json.dump(new_events_data, f, indent=2)
                
        print("EVENTS: Download complete.")
        
    except Exception as e:
        print(f"EVENTS: Download failed: {e}")
        
 


# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# PAUSE CONSOLE TO SHOW API DOWNLOAD LOGIC MESSAGES
# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
       
# Wait to show debug info for downloads.
time.sleep(10)



# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# EVENTS DATA EXTRACTION FOR JS
# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

def get_events_data_for_js(json_file):
    events_list = []
    
    # 1. Define a mapping dictionary for specific IDs or Variations
    #    This translates the internal code to the specific in-game title.
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
        "wild_animal_tagging": "Wild Animal Tagging"
    }

    try:
        if not os.path.exists(json_file):
            return "[]" # Return empty JSON array string

        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        target_categories = ['standard', 'themed', 'role'] # Added 'role' just in case you want those too
        
        for cat in target_categories:
            if cat not in data: continue
            schedule_dict = data[cat]
            
            for time_key, event_data in schedule_dict.items():
                
                # Extract raw data
                evt_id = event_data.get('id')
                evt_var = event_data.get('variation') # This is "hunting", "fishing", etc.
                evt_alt = event_data.get('alt')
                
                display_name = "Unknown Event"

                # LOGIC FLOW:
                # 1. If it's a "Challenge" (randomized type), look at the 'variation'
                if evt_id == "challenges" and evt_var:
                    # Check our dictionary, otherwise title case the variation (e.g. "hunting" -> "Hunting")
                    display_name = NAME_OVERRIDES.get(evt_var, evt_var.replace('_', ' ').title())
                    display_name += " Challenge" # Add "Challenge" to the end for clarity
                
                # 2. If the ID is in our override list (e.g. "hot_property" -> "Cold Dead Hands")
                elif evt_id in NAME_OVERRIDES:
                    display_name = NAME_OVERRIDES[evt_id]
                    
                # 3. Fallback: Use 'alt' or prettify the 'id'
                elif evt_alt:
                    display_name = evt_alt.replace('_', ' ').title()
                else:
                    display_name = evt_id.replace('_', ' ').title()
                
                # Append to list
                events_list.append({
                    "time": time_key,  # "09:00"
                    "name": display_name,
                    "cat": cat
                })
                
        # Return as a JSON string to be injected into JS
        return json.dumps(events_list)

    except Exception as e:
        print(f"Error preparing events for JS: {e}")
        return "[]"

# Get the JSON string data 
events_js_data = get_events_data_for_js(local_filename_events)
debug_print("L2", "Generated Events Data for JS")









def extract_challenges_with_roles(index):
    combined = []
    
    # Safety check: if index data is missing/empty, return empty list immediately
    if not index:
        return []

    # General challenges (not tied to a specific role or difficulty)
    # .get() safely returns [] if "general" key is missing
    for challenge in index.get("general", []):
        combined.append({**challenge, "role": "general", "difficulty": None})

    # Role-based challenges across easy, med, hard
    for difficulty in ["easy", "med", "hard"]:
        # Use .get() to safely retrieve the dictionary for that difficulty, 
        # defaulting to an empty dict {} if the key is missing.
        difficulty_data = index.get(difficulty, {})
        
        for role, challenges in difficulty_data.items():
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

# Build a lookup table from all sources: exact key -> All details
# We use the whole 'ch' object so we don't lose description3, description4, etc.
detail_lookup = {
    normalize_key(ch["key"]): ch
    for ch in all_challenge_definitions
}

# Extract and normalize all challenges from index.json
indexed_challenges = extract_challenges_with_roles(index_data)

# Final result list
final_list = []

for ch in indexed_challenges:
    title_upper = normalize_key(ch["title"])
    
    # Get the static details (descriptions, name, etc) from our local data files
    details = detail_lookup.get(title_upper, {})

    # Create the entry
    entry = {
        # 1. Default keys to prevent crashes if missing in details
        "name": None,
        
        # 2. Unpack local details. This brings in description3, description4, etc.
        # WARNING: This also brings in 'category' as a LIST (e.g. ['plants']), which caused the error.
        **details,
        
        # 3. Set/Overwrite with API specific data.
        # CRITICAL: This overwrites the 'category' LIST with the 'category' STRING (e.g. 'general')
        "title": ch["title"],
        "goal": ch["goal"],
        "category": ch["role"], 
        "difficulty": ch["difficulty"],
        
        # 4. Handle showgoal logic (prefer local value, default to "n")
        "showgoal": details.get("showgoal", "n")
    }
    
    final_list.append(entry)
    

# Choosing the description to use from any available ones
def get_printable_description(details):
    """
    Dynamically collects all available descriptions.
    Selects one based on deterministic rotation or dynamic "forceX" flags.
    Appends [#X] if DEBUG_DESCRIPTION is True.
    """
    
    # ---------------------------------------------------------
    # 1. DYNAMICALLY BUILD THE LIST OF OPTIONS
    # ---------------------------------------------------------
    options = []
    
    # Add the primary description (Index 0)
    if details.get("description"):
        options.append(details["description"])
        
    # Dynamic search for description2, description3, etc.
    i = 2
    while True:
        key = f"description{i}"
        val = details.get(key)
        if val:
            options.append(val)
            i += 1
        else:
            break
            
    # If no descriptions exist, return None
    if not options:
        return None
        
    count = len(options)
    selection_index = 0

    # ---------------------------------------------------------
    # 2. DETERMINE SELECTION INDEX
    # ---------------------------------------------------------
    
    # Handle "forceX" logic (force1, force2, force10, etc.)
    if DESCRIPTION_MODE.startswith("force"):
        try:
            # Extract the number part (e.g. "force5" -> "5")
            num_str = DESCRIPTION_MODE.replace("force", "")
            
            if num_str.isdigit():
                # Convert to integer and adjust for 0-based index (Force1 = Index 0)
                req_num = int(num_str)
                target_index = req_num - 1
                
                # CLAMP LOGIC:
                # If target is less than 0, use 0.
                # If target is greater than the last index, use the last index.
                # e.g. If force5 requested but only 2 items exist, use item 2 (index 1).
                selection_index = max(0, min(target_index, count - 1))
            else:
                # Fallback if someone typed just "force"
                selection_index = 0
                
        except Exception:
            selection_index = 0

    else:
        # --- AUTO MODE: DETERMINISTIC ROTATION ---
        challenge_name = details.get("name") or details.get("title") or "unknown"
        
        # Create stable integer hash
        name_hash = int(hashlib.md5(challenge_name.encode('utf-8')).hexdigest(), 16)
        
        # Day ID from start_timestamp
        day_id = int(start_timestamp / 86400) + 0
        ##########################################
        ##########################################
        ##########################################
        ##########################################
    
        # Formula: (Day + NameHash) % Count
        selection_index = (day_id + name_hash) % count

    # ---------------------------------------------------------
    # 3. RETRIEVE TEXT AND APPEND DEBUG INFO
    # ---------------------------------------------------------
    final_text = options[selection_index]
    
    if DEBUG_DESCRIPTION:
        # +1 makes it human readable (Index 0 = Desc #1, Index 1 = Desc #2)
        final_text += f" [#{selection_index + 1}]"
        
    debug_print("L3", f"Rotator: '{details.get('name')}' selected index {selection_index} ({selection_index+1}/{count})")
    
    return final_text


    

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
            debug_print("L2", "Chosen Description: ", chosen_description)
            
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

# Define fallback HTML for missing data
NO_DATA_HTML = '''
<div class="challenge">
  <label>
    <span class="challenge-text" style="color: #d00; font-style: italic;">
      Challenge Data Missing (File Not Found)
    </span>
  </label>
  <div class="challenge-desc">Could not load index.json and download was blocked/failed.</div>
</div>
'''

NO_DATA_ROLE_HTML = '''
<div class="role-challenge">
  <div class="role-challenge-text" style="color: #d00; font-style: italic;">
    Role Data Missing
  </div>
</div>
'''

if not challenges:
    # --- DATA MISSING SCENARIO ---
    debug_print("L1", "ired", "ALERT: No challenges found. Generating fallback HTML.")
    
    # Override the previously generated (and empty) html_general
    html_general = NO_DATA_HTML
    
    # Set the fallback for Role Challenges variables (just in case they are referenced)
    html_easy_roles = NO_DATA_ROLE_HTML
    html_med_roles  = NO_DATA_ROLE_HTML
    html_hard_roles = NO_DATA_ROLE_HTML
    
    # Assign the fallback to the actual variable used in the HTML output
    selected_html_roles = NO_DATA_ROLE_HTML

else:
    # --- NORMAL SCENARIO ---
    # This generates the role HTML strings based on difficulty
    html_easy_general, html_easy_roles = generate_html_for_difficulty(challenges, "easy")
    html_med_general,  html_med_roles  = generate_html_for_difficulty(challenges, "med")
    html_hard_general, html_hard_roles = generate_html_for_difficulty(challenges, "hard")
    
    # Note: We do NOT overwrite 'html_general' here because it was already 
    # correctly generated (with dividers) by 'render_general_challenges_with_dividers' earlier.

    # Select the specific role HTML based on the difficulty filter
    difficulty_roles_map = {
        "easy": html_easy_roles,
        "med": html_med_roles,
        #"hard": html_hard_roles
    }
    selected_html_roles = difficulty_roles_map.get(filter_difficulty, html_hard_roles)


# ---------------------------------------------------------------------------------------
# Debug Prints
debug_print("L2", "bblue", "Generated html_easy_roles")
debug_print("L3", "iblue", "html_easy_roles:   ", html_easy_roles)
print ("-" * 120)
debug_print("L2", "bpurple", "Generated html_med_roles")
debug_print("L3", "ipurple", "html_med_roles:   ", html_med_roles)
print ("-" * 120)
debug_print("L2", "bred", "Generated html_hard_roles")
debug_print("L3", "ired", "html_hard_roles:   ", html_hard_roles)
print ("-" * 120)
# ---------------------------------------------------------------------------------------



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
// Toggle Nazar Map Zoom                                                                  //
// ////////////////////////////////////////////////////////////////////////////////////// //

    function toggleNazarZoom(img) {{
        if (img.dataset.hasZoom !== "true") return;

        // Check if currently showing the standard image
        // We compare the end of the string to avoid absolute/relative path mismatches
        const currentSrc = img.src.split('/').pop();
        const stdSrc = img.dataset.standard.split('/').pop();

        if (currentSrc === stdSrc) {{
            // Switch to Zoom
            img.src = img.dataset.zoom;
        }} else {{
            // Switch back to Standard
            img.src = img.dataset.standard;
        }}
    }}
    // Expose to window so onclick can find it
    window.toggleNazarZoom = toggleNazarZoom;
    
    
    
    
    
// ////////////////////////////////////////////////////////////////////////////////////// //
    // JavaScript: Nazar Map 5-Second Dissolve Logic                                          //
    // ////////////////////////////////////////////////////////////////////////////////////// //
    
    setTimeout(() => {{
        const img = document.getElementById('nazar-map-img');
        if (!img) return;

        // Get the filenames to compare (ignoring full URL paths)
        const currentFilename = img.src.split('/').pop();
        const targetSrc = img.dataset.finalTarget;
        const targetFilename = targetSrc.split('/').pop();

        // If the current image is ALREADY the target (or no target exists), do nothing
        if (currentFilename === targetFilename || !targetSrc) return;

        // 1. Fade Out
        img.style.opacity = 0;

        // 2. Wait for fade out, then swap source and Fade In
        setTimeout(() => {{
            img.src = targetSrc;
            
            // Important: Update the data-standard attribute so the zoom logic 
            // knows this new image is now the "Standard" base to zoom from.
            img.dataset.standard = targetSrc; 
            
            // 3. Fade In
            img.style.opacity = 1;
        }}, 800); // Wait 800ms (matches CSS transition)

    }}, 5000); // 5000ms = 5 seconds delay    






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
        // FIX: Use LS_STREAK_COUNT (current status) instead of LS_STREAK_FOR_MULTIPLIER (start of day baseline)
        // This ensures the multiplier updates immediately visually when the streak increments (e.g. 7 -> 8).
        const currentStreak = parseInt(localStorage.getItem(LS_STREAK_COUNT) || '0', 10);
        
        if (currentStreak >= 22) return 2.5; // Days 22-28
        if (currentStreak >= 15) return 2.0; // Days 15-21
        if (currentStreak >= 8) return 1.5;  // Days 8-14
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
            "Current Streak (Live)": localStorage.getItem(LS_STREAK_COUNT) + " Days",
            "Multiplier Lock (Base)": localStorage.getItem(LS_STREAK_FOR_MULTIPLIER) + " Days",
            "Multiplier Value": getMultiplier() + "x",
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
    
    
    // --- EVENTS DATA FROM PYTHON ---
    const RAW_EVENTS_DATA = {events_js_data}; 

    // ////////////////////////////////////////////////////////////////////////////////////// //
    // JavaScript: Dynamic Upcoming Events Logic                                              //
    // ////////////////////////////////////////////////////////////////////////////////////// //

function updateUpcomingEvents() {{
        const container = document.getElementById('upcoming-events-list');
        if (!container || !RAW_EVENTS_DATA.length) return;

        const now = new Date();
        const JOIN_WINDOW_MS = 3 * 60 * 1000; // 3 minutes

        let candidates = [];
        
        function getEventDate(timeStr, dayOffset) {{
            const [h, m] = timeStr.split(':').map(Number);
            const d = new Date();
            d.setUTCHours(h, m, 0, 0);
            if (dayOffset > 0) {{
                d.setUTCDate(d.getUTCDate() + dayOffset);
            }}
            return d;
        }}

        RAW_EVENTS_DATA.forEach(evt => {{
            const t1 = getEventDate(evt.time, 0);
            candidates.push({{ ...evt, dt: t1 }});
            const t2 = getEventDate(evt.time, 1);
            candidates.push({{ ...evt, dt: t2 }});
        }});

        const activeEvents = candidates.filter(e => {{
            return (e.dt.getTime() + JOIN_WINDOW_MS) > now.getTime();
        }});

        activeEvents.sort((a, b) => a.dt - b.dt);
        const next5 = activeEvents.slice(0, 5);

        let html = '<ul style="list-style: none; padding: 0; margin: 0;">';
        
        next5.forEach(e => {{
            const diffMs = e.dt - now; 
            
            let timeDisplay = "";
            let rowBgColor = "transparent"; 
            let rowPadding = "1px 0"; 
            let textColor = "#ccc";
            let timeColor = "#bbb";   
            let textClass = "";
            
            // Define truncation limit (Default: 25 chars)
            let maxNameLength = 27; 

            if (diffMs > 0) {{
                // === FUTURE EVENT ===
                const diffMins = Math.floor(diffMs / 60000);
                if (diffMins < 60) {{
                    timeDisplay = `${{diffMins}}m`;
                }} else {{
                    const h = Math.floor(diffMins / 60);
                    const m = diffMins % 60;
                    timeDisplay = `${{h}}h ${{m}}m`;
                }}
            }} else {{
                // === ACTIVE / STARTED EVENT ===
                textClass = "active-event-glow";
                
                // NEW: Reduce name length to make room for "Join Now" text
                maxNameLength = 27; 
                
                const msPast = Math.abs(diffMs);
                rowPadding = "2px 4px"; 
                textColor = "#fff"; 
                timeColor = "#ddd"; 

                if (msPast < 60000) {{
                    rowBgColor = "#333333";
                    timeDisplay = "Now";
                }} else if (msPast < 120000) {{
                    rowBgColor = "#555500"; 
                    timeDisplay = "Now";
                }} else {{
                    rowBgColor = "#550000";
                    timeDisplay = "<1min";
                }}
            }}
            
            // Apply Dynamic Truncation
            let nameDisplay = e.name;
            if (nameDisplay.length > maxNameLength) {{
                nameDisplay = nameDisplay.substring(0, maxNameLength - 2) + "..";
            }}
            
            const eventTimeStr = e.time; 

            html += `
            <li style="display: flex; justify-content: space-between; align-items: center; padding: ${{rowPadding}}; border-bottom: 1px solid #1a1a1a; font-size: 0.85rem; color: ${{textColor}}; background-color: ${{rowBgColor}}; border-radius: 2px; margin-bottom: 1px; transition: background-color 0.5s;">
                <div style="line-height: 1;">
                    <span class="${{textClass}}" style="font-family: 'hapna', sans-serif; letter-spacing: -0.05em;">${{nameDisplay}}</span>
                    <span style="font-size: 0.7rem; color: ${{timeColor}}; margin-left: 4px; letter-spacing: -0.05em;">(${{timeDisplay}})</span>
                </div>
                <span class="${{textClass}}" style="color: #FFC107; font-family: 'RDOFont', sans-serif; font-size: 1.0rem; letter-spacing: 1px; line-height: 1;">${{eventTimeStr}}</span>
            </li>
            `;
        }});
        
        html += '</ul>';
        container.innerHTML = html;
    }}
    
    
    
    
    
    // Run immediately, then every second to keep "minutes remaining" accurate
    setInterval(updateUpcomingEvents, 1000);
    // Also run on load
    window.addEventListener('load', updateUpcomingEvents);
    
    
    
    
// UPDATED FUNCTION: Fixed calculation to prevent summing previous cycle's weeks
    function calculateLogSums(currentStreak) {{
        const goldLog = JSON.parse(localStorage.getItem(LS_GOLD_LOG)) || [];
        
        // 1. Determine the minimum streak day for the current week bracket
        let minWeekStreak = 1;
        if (currentStreak >= 22) minWeekStreak = 22;
        else if (currentStreak >= 15) minWeekStreak = 15;
        else if (currentStreak >= 8) minWeekStreak = 8;
        
        let weekTotal = 0.0;
        let runningTotal = 0.0;
        
        // Track the streak number of the previous iteration (initially -1)
        let lastStreakVal = -1;
        
        // Loop BACKWARDS through the log (newest to oldest)
        for (let i = goldLog.length - 1; i >= 0; i--) {{
            const entry = goldLog[i];
            const val = parseFloat(entry.gold || 0);
            const s = parseInt(entry.streak || 0);
            
            // If we hit a 0 streak or data is missing, stop calculations
            if (s === 0) break;
            
            // CYCLE BOUNDARY CHECK:
            // If the streak number jumps UP while going backwards (e.g., 1 -> 28),
            // we have crossed into the previous 28-day cycle. Stop the running total.
            if (lastStreakVal !== -1 && s > lastStreakVal) {{
                break;
            }}

            // Add to Running Total (Streak Gold Total)
            runningTotal += val;

            // WEEK TOTAL CHECK:
            // Only add to the week total if the streak is within the current bracket.
            // Since we break the loop above if we cross a cycle boundary, 
            // this simply filters out days 1-21 if we are in week 4 (22-28).
            if (s >= minWeekStreak) {{
                weekTotal += val;
            }}

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
                
                // --- STABLE STAR LOGIC ---
                // Default: Empty outline star, very faint
                let starChar = '☆'; 
                let starStyle = 'color: #444; opacity: 0.3; font-weight: normal;'; 

                // Gold Star Logic (Both Done: 7/7 General AND 9/9 Role)
                if (entry.general === 7 && entry.role === 9) {{
                    starChar = '★'; 
                    // "Pop" Effect: Two layers of text-shadow. 
                    // 1. Tight Gold Glow (4px)
                    // 2. Wider Orange Glow (10px) to simulate heat/radiance
                    starStyle = 'color: #FFD700; text-shadow: 0 0 4px #FFD700, 0 0 10px #FFA500;';
                }} 
                // Silver Star Logic (One Done)
                else if (entry.general === 7 || entry.role === 9) {{
                    starChar = '★'; 
                    // Subtle, single-layer cool glow
                    starStyle = 'color: #C0C0C0; text-shadow: 0 0 3px rgba(192, 192, 192, 0.5);';
                }}
                
                // Construct HTML using the new Stable Grid classes
                // Note: JS template variables are escaped as ${{variable}}
                infoDisplay.innerHTML = `
                    <div class="tooltip-top-row">
                        <span class="tooltip-date">${{humanDate}}</span>
                        <span class="tooltip-gold">${{entry.gold.toFixed(2)}} Gold</span>
                        <span class="tooltip-star" style="${{starStyle}}">${{starChar}}</span>
                    </div>
                    <div class="tooltip-bottom-row">
                        <span>Streak: ${{streakText}}</span>
                        <span>Gen: ${{entry.general}}/7 | Role: ${{entry.role}}/9</span>
                    </div>
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
        
        
        /* COLUMN 3: BONUS INFO - Base styles */
        .bonus-container {{
            padding: 7px;
            background-color: #111; /*Dark grey background*/
            display: flex;
            flex-direction: column;
            
            /* Fixed width for Desktop (3-column layout) */
            width: 250px; 
            min-width: 250px; 
            
            /* We remove max-width here to let flexbox handle it normally in row mode */
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
        
        /* 
           Scenario 1: Tablet/Intermediate Width (< 1600px)
           Layout: General and Roles side-by-side (if they fit), 
           Bonus Container wraps to the bottom line.
        */
        @media (max-width: 1600px) {{
            .bonus-container {{
                display: flex !important;
                flex-direction: column;
                order: 3;             /* Moves it to the end */
                margin-top: 15px;     /* Gap above it */
                
                width: 100% !important;
                /* CAP THE WIDTH: Keeps graphics looking good, matches sidebar width */
                max-width: 450px !important; 
                
                /* FIX SCALING: Remove min-width so it shrinks on small screens */
                min-width: 0 !important;
            }}
        }}
        
        /* 
           Scenario 2: Mobile/Narrow Width (< 1320px)
           Layout: Single column stack. 
           General -> Roles -> Bonus (all centered)
        */
        @media (max-width: 1320px) {{
          body {{
            flex-direction: column;
            align-items: center;
          }}
          
            .main-container {{
            flex-direction: column;
            align-items: center;
            width: 100%;    /* allow children to fill horizontally */
            align-items: stretch; 
            min-width: 0;   /* Prevent lock-up on tiny screens */
          }}
          
          .sidebar-container {{
            width: 100% !important; 
            max-width: 850px !important;
            margin-left: 0;    /* center below main container */
          }} 

          .bonus-container {{
            margin-left: auto !important;
            margin-right: auto !important; /* Centers the block */
            width: 100% !important;
            max-width: 450px !important;   /* Maintained width cap */
            min-width: 0 !important;       /* Ensure it scales down on mobile */
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
              margin-top: -1px;     /* <--- THIS LINE to pull it up */
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
            font-size: .95rem;
            color: #aaa;
            margin-left: 6px; /* aligns under the role challenge text */
            white-space: pre-wrap; /* allows \\n line breaks in descriptions */
            transform: scaleX(0.925); /* reduce width to 90% */
            line-height: 0.99;  /* <--- ADD THIS LINE (Lower number = tighter gap) */
            margin-top: 1px;   /* <--- OPTIONAL: Pulls description closer to the title */
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
            font-family: 'hapna', sans-serif;
            font-size: 0.8rem;
            
            /* TIGHTENING FIXES: */
            height: 30px;        /* Fixed compact height (approx 2 lines) to prevent pushing content down */
            min-height: 0;       /* Remove the large min-height from previous attempt */
            margin-top: 0px;     /* Reset top margin */
            padding-left: 5px;
            width: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center; /* Center content vertically in the 30px box */
            gap: 2px;            /* Tiny gap between the two rows */
        }}

        .tooltip-top-row {{
            display: grid;
            grid-template-columns: 1fr auto 20px; 
            align-items: center;
            width: 100%;
            
            /* TIGHTENING FIXES: */
            border-bottom: 1px solid #222;
            padding-bottom: 0px; /* Remove padding */
            margin-bottom: 0px;  /* Remove margin */
            line-height: 1.1;    /* Tight line height */
        }}

        .tooltip-date {{
            font-weight: bold;
            color: #bbb;
            white-space: nowrap;
        }}

        .tooltip-gold {{
            text-align: right;
            padding-right: 5px;
            color: #FFC107; 
            font-feature-settings: "tnum";
        }}

        .tooltip-star {{
            text-align: center;
            font-size: 0.9rem; /* Slightly smaller star to fit line height */
            line-height: 1;
            padding-top: 1px;  /* Visual alignment */
        }}

        .tooltip-bottom-row {{
            font-size: 0.75rem;
            color: #888;
            display: flex;
            justify-content: space-between;
            
            /* TIGHTENING FIXES: */
            line-height: 1.1; /* Tight line height */
            margin-top: 0px;
        }}
        
        
        
        
        
/* === UPDATED: Tighter Pulse Animation === */
        @keyframes urgentPulse {{
            0% {{ 
                /* Very tight shadow to keep text crisp */
                text-shadow: 0 0 1px #fff; 
                color: #fff;
            }}
            50% {{ 
                /* Reduced blur radius (5px/8px instead of 15px/25px) */
                text-shadow: 0 0 5px #fff, 0 0 8px #FFD700; 
                color: #fffae6;
            }}
            100% {{ 
                text-shadow: 0 0 1px #fff; 
                color: #fff;
            }}
        }}

        .active-event-glow {{
            animation: urgentPulse 1.5s infinite ease-in-out;
        }}
        
        
        /* NAZAR DISSOLVE EFFECT */
        #nazar-map-img {{
            transition: opacity 0.8s ease-in-out;
            opacity: 1;
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

    
<!-- COLUMN 3: BONUS INFO -->
        <div class="bonus-container" id="bonus-container">
            <h3 class="stats-heading" style="color: #666666; margin-bottom: 1px; padding-bottom: 0px;">Bonus Info</h3>
            
<div style="padding: 2px; border: 1px solid #000; border-radius: 8px; background-color: #151515; text-align: left; color: #E0E0E0; font-family: sans-serif;">
                
                <p class="stats-text" id="streak-container" style="margin-bottom: 0px; display: flex; justify-content: space-between; align-items: center; width: 100%;">
                    <span style="display: flex; align-items: center; white-space: nowrap;">
                        <span style="font-weight: 500;">Daily Challenge Streak:</span>
                        <span id="streak-controls">
                            <span id="streak-down">▼</span><span id="streak-up">▲</span>
                        </span>
                    </span>
                    <span id="current-streak" style="color: #FFC107; text-align: right;">0 Days</span>
                </p>

                <p class="stats-text" style="margin-bottom: 0px; display: flex; justify-content: space-between; width: 100%;">
                    <span style="font-weight: 500;">Gold Per Challenge:</span>
                    <span id="gold-per-challenge" style="color: #FFC107; text-align: right;">0.00 Gold Bars</span>
                </p>
                
                <p class="stats-text" style="margin-bottom: 0px; display: flex; justify-content: space-between; width: 100%;">
                    <span style="font-weight: 500;">Completion Reward:</span>
                    <span id="completion-bonus-reward" style="color: #FFC107; text-align: right;">0.00 Gold Bars</span>
                </p>
                
                <p class="stats-text" style="margin-bottom: 0px; display: flex; justify-content: space-between; width: 100%;">
                    <span style="font-weight: 500;">Daily Gold Total:</span>
                    <span id="daily-gold-total" style="color: #FFC107; text-align: right;">0.00 Gold Bars</span>
                </p>
                
                <p class="stats-text" style="margin-bottom: 0px; display: flex; justify-content: space-between; width: 100%;">
                    <span style="font-weight: 500;">Streak Week Gold Total:</span>
                    <span id="cycle-gold-total" style="color: #FFC107; text-align: right;">0.00 Gold Bars</span>
                </p>
                
                <p class="stats-text" style="display: flex; justify-content: space-between; width: 100%;">
                    <span style="font-weight: 500;">Streak Gold Total:</span>
                    <span id="streak-gold-total" style="color: #FFC107; text-align: right;">0.00 Gold Bars</span>
                </p>
                
            </div>
            
            
            <!-- Gold Log Chart Container -->
                
            <h3 class="stats-heading" style="color: #666666; margin-top: 15px; margin-bottom: 1px; padding-bottom: 0px;">Gold Log (Last 28 Days)</h3>

  
             <div id="gold-log-chart-container">
                <!-- Bars will be injected here by JavaScript -->
            </div>
            <div id="chart-info-display" class="chart-info-display">&nbsp;</div>


<!-- NAZAR LOCATION SECTION -->
            <h3 class="stats-heading" style="color: #666666; margin-top: 30px; margin-bottom: 1px; padding-bottom: 0px;">Where Is Madam Nazar Today?</h3>            
            <div style="padding: 2px; border: 1px solid #000; border-radius: 8px; background-color: #151515; text-align: center;">
                <div style="color: #FFC107; font-family: 'RDOFont', sans-serif; font-size: 1.4rem; letter-spacing: 0.05em; text-shadow: 1px 1px 2px rgba(0,0,0,0.8); margin-bottom: 2px; line-height: 1.1;">
                    {nazar_location_text}
                </div>
                
                    
                <!-- Image with toggle logic and 5s dissolve -->
                <img src="{placeholder_path}" 
                     id="nazar-map-img"
                     alt="Nazar Location Map" 
                     data-final-target="{nazar_final_img_src}"
                     data-standard="{nazar_final_img_src}"
                     data-zoom="{nazar_zoom_src}"
                     data-has-zoom="{nazar_has_zoom}"
                     onclick="toggleNazarZoom(this)"
                     style="width: 100%; height: auto; border-radius: 4px; border: 1px solid #333; display: block; cursor: {nazar_cursor_style};" 
                />

  
                
                <!-- Tiny hint text if zoom exists -->
                <div style="font-size: 0.7rem; color: #777; margin-top: 1px; display: {'block' if nazar_has_zoom == 'true' else 'none'};">
                    (Click map to zoom)
                </div>
            </div>
            
            
<!-- UPCOMING EVENTS SECTION (NEW) -->
            <h3 class="stats-heading" style="color: #666666; margin-top: 20px; margin-bottom: 1px; padding-bottom: 0px;">Upcoming Events</h3>
            <div style="padding: 2px; border: 1px solid #000; border-radius: 8px; background-color: #151515; min-height: 85px;">
                <div id="upcoming-events-list">
                    <div style="text-align:center; padding:10px; color:#555; font-size:0.8rem;">Loading Events...</div>
                </div>
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