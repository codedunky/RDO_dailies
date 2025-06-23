import urllib.request
import datetime
import time
import json
import inspect
import textwrap
import os
import io
import sys
from typing import Any
from ansi2html import Ansi2HTMLConverter




#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
import inspect
import textwrap
from typing import Any

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
CURRENT_DEBUG_LEVEL = 3

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
# This is a 'decorator'
# If you put @announce in the line before your function, it will debug_print the yellow "Executing Function" message
'''
    It takes a function func as input.
    Inside, it defines wrapper, which:
        Prints a message indicating which function is running.
        Calls the original function with its arguments.

    announce returns this wrapper function.
'''
def announce(func):
    def wrapper(*args, **kwargs):
        debug_print("L1", "byellow", f"Executing function - {func.__name__}()")
        return func(*args, **kwargs)
    return wrapper



###############################################################################################################################################################################################################################################################################################################################
        
        
        
        
        
debug_print("L1", "Import RDO_Challenges_Data") # Just to have a debug heading.        
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Import the predefined_challenges dictionary data from a separate .py file called RDO_challenges_data.py
# RDO_challenges_data.py is in the same folder as this program
# This imports the entire RDO_challenges_data.py module, which contains the predefined_challenges list.
import RDO_challenges_data
debug_print("L3", "Actually imported RDO_Challenges_Data") 

# This assigns the list stored in RDO_challenges_data.predefined_challenges to a variable named predefined_challenges
# in this current script, so it can be used directly without the challenges_data. prefix.
predefined_challenges = RDO_challenges_data.predefined_challenges
debug_print("L3", "Set predefined_challenges")
debug_print("L4", predefined_challenges)

# Step 2: Sort challenges alphabetically by 'name'
sorted_challenges = sorted(predefined_challenges, key=lambda x: x['name'])
debug_print("L3", "Sort challenges alphabetically by 'name'")


# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# **************************************************************************************************************************************************************************************

# The next bit will create a dictionary like this:
# predefined_lookup = {'mpgc_story_mission_wins': {'key': 'mpgc_story_mission_wins', 'name': 'Story Mission Wins', 'showgoal': 'y', ...},

predefined_lookup = {c['key']: c for c in predefined_challenges}
debug_print("L2", "Created predefined_lookup")
debug_print("L4", predefined_lookup)
# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Check if there's a local version of the index.json file
# Your existing local filename path
local_filename = r"C:\Users\Dunk\Documents\Thonny Bits\RDO Daily Challenges\index.json"

# Extract directory
target_dir = os.path.dirname(local_filename)
debug_print("L2", "Get a target directory to save index.json files to") #
debug_print("L3", "target_dir: ", target_dir)


# URL for downloading if needed
url = "https://api.rdo.gg/challenges/index.json"

# Determine UTC now
now = datetime.datetime.utcnow()
debug_print("L2", "Get the current time") #
debug_print("L3", "now: ", now)

# Function to check if download directory exists
# --- Helper Functions ---
@announce
def ensure_directory_exists(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)
debug_print("L2", "Check download directory exists")

@announce
def get_unique_backup_name(base_name):
    debug_print("L2", "Get unique backup name for saving old index.json")
    count = 1
    new_name = base_name
    while os.path.exists(new_name):
        name, ext = os.path.splitext(base_name)
        new_name = f"{name}_{count}{ext}"
        count += 1
    debug_print("L3", "Backup name is :", new_name)
    return new_name

@announce
def should_download(existing_data):
    debug_print("L2", "Using should_download function to check if need to download")
    now = time.time()
    end_time = existing_data.get('endTime')
    #debug_print("L3", "end_time date is:",get_date_from_index(end_time))
    debug_print("L3", "Date challenges run out is ",get_human_readable_date(end_time))
    debug_print("L3", "end_time: ", end_time)
    if end_time is None:
        return True
    return now > end_time

@announce
def create_backup():
    debug_print("L3", "local_filename for backup is: ", local_filename)
    debug_print("L3", "Checking if local_filename exists:", local_filename)
    
    if os.path.exists(local_filename):
        debug_print("L2", "local_filename exists")
        # Load the existing data from index.json
        with open(local_filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Extract startTime
        start_time = data.get('startTime')
        debug_print("L3", "start_time in index.json is:", start_time)
        if start_time:
            # Convert startTime (Unix timestamp) to date string
            date_str = time.strftime('%Y-%m-%d', time.localtime(start_time))
            debug_print("L3", "start_time converted to yyyy-mm-dd:", date_str)
        else:
            # Fallback if startTime isn't present
            date_str = time.strftime('%Y-%m-%d')
            debug_print("L3", "No start_time present, so using:", date_str)
        
        # Build the backup filename using the startTime date
        base_backup_name = os.path.join(os.path.dirname(local_filename), f"index_{date_str}.json")
        debug_print("L3", "base_backup_name for backup is: ", base_backup_name)
        backup_name = get_unique_backup_name(base_backup_name)
        debug_print("L3", "backup_name for backup is: ", backup_name)
        print(f"Creating backup: {backup_name}")
        os.rename(local_filename, backup_name)
    else:
        print("File does not exist at this point.")

@announce
def download_json():
    # Check if file exists
    debug_print("L1", "download_json():")
    if os.path.exists(local_filename):
        with open(local_filename, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
        if not should_download(existing_data):
            print("Existing data is current. No need to download.")
            return None
        else:
            print("Detected that 'now' > 'endTime'.")
            response = input("Do you want to download a new version? (Y/N): ").strip().lower()
            if response != 'y':
                print("Skipping download. Keeping existing file.")
                return None
            else:
                print("Proceeding to download new data...")
    else:
        print("No existing file found. Downloading new data...")

    # Download data
    debug_print("L2", "Downloading index.json from api")
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            data_bytes = response.read()
            data_str = data_bytes.decode('utf-8')
            data = json.loads(data_str)
        return data
    except Exception as e:
        print("Error during download:", e)
        return None

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# A routine to get the actual date the index.json is for, ready to print in the output heading

@announce
def get_date_from_index(local_filename):
    #debug_print("L1", "get_date_from_index(local_filename):")
    try:
        with open(local_filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        start_time = data.get('startTime')
        if start_time:
            #debug_print("L3", "Time from index.json is: ", time.strftime('%Y-%m-%d', time.localtime(start_time)))
            return time.strftime('%Y-%m-%d', time.localtime(start_time))
        else:
            #debug_print("L3", "Fallback to current date, which is: ", time.strftime('%Y-%m-%d', time.localtime(start_time)))
            return time.strftime('%Y-%m-%d')  # fallback to current date
    except Exception as e:
        print("Error loading index.json:", e)
        return time.strftime('%Y-%m-%d')  # fallback
    
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



# --- Main process ---

# Step 1: Ensure directory exists
ensure_directory_exists(local_filename)

# Step 2: Check if need to download new data
data = download_json()
debug_print("bgreen", "local_filename for backup is: ", local_filename)

# Step 3: If new data is available, backup old file and save new
if data is not None:
    create_backup()
    with open(local_filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"New data saved to {local_filename}")
else:
    print("No update performed.")
# -------------------------------------------------------------------------------------------------------------------------------------------


# Extract challenges list
debug_print("bbrightwhite", "Extract Challenges List From JSON") # Just to have a debug heading.

# This will extract the general challenges from the json file (id, title, goal, goalFormat)
general_challenges = []  # default value

# Load existing data from index.json
if os.path.exists(local_filename):
    with open(local_filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # Now assign challenges from data if available
    if data:
        general_challenges = data.get('general', [])
    # do other stuff
else:
    print("No data available.")

debug_print("icyan", "Extracted 'general' challenges:", len(general_challenges)) # Debug message (and how many general challenges)

# Debug print the challenge object
if general_challenges: # if "general_challenges" exists then do the for loop below
    for loopnumber, challenge in enumerate(general_challenges):
        debug_print("bblue", f"General Challenge {loopnumber + 1}")
        debug_print("iblue", challenge)
        
        # "general_challenges" is the list of daily challenges extracted from the json file.
        #debug_print("ired", general_challenges)




def normalize_string(s):
    """
    Normalize a string for comparison:
    - Convert to uppercase
    - Replace underscores with spaces (optional, depending on your data)
    - Strip leading/trailing spaces
    """
    return s.upper().replace('_', ' ').strip()


def find_predefined_challenge(title):
    """
    Search for a challenge in the predefined_challenges list
    where the 'key' matches the given 'title' after normalization.
    """
    normalized_title = normalize_string(title)
    for challenge in predefined_challenges:
        challenge_key_normalized = normalize_string(challenge['key'])
        if challenge_key_normalized == normalized_title:
            return challenge
    return None


######################################################################################################
##                                                                                                  ##
## Print the list of daily challenges                                                               ##
##                                                                                                  ##
######################################################################################################

######################################################################################################
#This section is for ansi2html, to capture the output for later conversion to an html                #
######################################################################################################
# Prepare a buffer to capture output
buffer = io.StringIO()


######################################################################################################





#print("\nDAILY CHALLENGES\n")
# Get the appropriate date for the list of challenges and print it.
unix_time = get_unix_time_from_index(local_filename)
human_readable_date = get_human_readable_date(unix_time)
print("\n")
print(human_readable_date)
print("\n")



# Redirect stdout to buffer
#sys.stdout = buffer


# Step 1: Collect all challenges into a list with necessary info
all_challenges = []

for challenge in general_challenges:
    title = challenge['title']
    matched = find_predefined_challenge(title)

    if matched:
        name = matched.get('name', 'Unknown')
        goal_value = challenge['goal']
        showgoal = matched.get('showgoal')
        description = matched.get('description')
        # Store all relevant info for later display
        all_challenges.append({
            'name': name,
            'goal_value': goal_value,
            'showgoal': showgoal,
            'description': description
        })
    else:
        # No match found; still include if you want to display unmatched challenges
        # For consistency, include with a placeholder name
        all_challenges.append({
            'name': f"No match for {title}",
            'goal_value': challenge['goal'],
            'showgoal': None
        })

# Step 2: Sort alphabetically by 'name'
sorted_challenges = sorted(all_challenges, key=lambda x: x['name'].lower())

#-----------------------------------------------------------------------------
# This will be the final challenge output for the html to read in (with correct numbers)
json_file_path = 'final_challenges_output.json'

# Load existing data or initialize
if os.path.exists(json_file_path):
    with open(json_file_path, 'r') as file:
        data = json.load(file)
        # Clear previous entries to start fresh each run
        data["final_name"] = []
        
else:
    data = {"final_name": []}
#-----------------------------------------------------------------------------

# Step 3: Loop through sorted challenges, apply your display logic, and save output for html to use
for challenge in sorted_challenges:
    name = challenge['name']
    goal_value = challenge['goal_value']
    showgoal = challenge['showgoal']
    description = challenge.get('description', None) 
    
    # Initialize the dictionary for this challenge
    challenge_entry = {}


    # Decide what to print based on your conditions:
    if showgoal == 'y':
        debug_print("icyan", "showgoal: ", showgoal)
        main_text = f"{goal_value} {name}"
        
    elif goal_value == 1 and showgoal is None or showgoal :
        debug_print("L3", "showgoal: ", showgoal)
        main_text = f"{name}"
    
    else:
        # For all other cases, print goal_value and name
        main_text = f"{goal_value} {name}"
     
    
    # Save main text
    challenge_entry['text'] = main_text
    
    
    if description is not None:
        challenge_entry['description'] = description
        
    elif description is None:
        challenge_entry['description'] = None
        pass

    
    # Append this challenge's data to the list
    data["final_name"].append(challenge_entry)
    
    # Redirect stdout to buffer
    sys.stdout = buffer
    # Print the challenge and description
    print(main_text)
    if description is not None:
        print(f"\033[3;33m{challenge['description']}\033[0m")
    print("-" * 120)
    #Turn off the buffer capture
    sys.stdout = sys.__stdout__

# Save a json file out
with open(json_file_path, 'w') as file:
    json.dump(data, file, indent=4)
############################################################################

# 'with' is a context manager that handles resources automatically.
# It ensures the file closes properly even after an error.
# It opens the file, and assigns it to the vaiable f
# The open() function opens a file with the name challenges_export.json
# the w means it uses 'write mode', creating the file if it doesn't exist or overwriting it if it does

with open('challenges_export.json', 'w') as f:
    
# json.dump serializes (sorted_challenges) the alphabetically sorted list, into JSON format and writes it to the file object f
# indents=4 formats the JSON with 4 spaces of indentation for readability
    
    json.dump(sorted_challenges, f, indent=4)

#Turn off the buffer capture
sys.stdout = sys.__stdout__

debug_print("L3", "Challenges data saved to challenges_export.json.")
############################################################################


# Get the captured output
captured_output = buffer.getvalue()

# Convert ANSI to HTML
converter = Ansi2HTMLConverter()
html_output = converter.convert(captured_output)

# Save to an HTML file
with open("challenges.html", "w", encoding="utf-8") as f:
    f.write(html_output)

# Also, print to shell
print("-" * 120)
print(captured_output)





























##################################################################################################################################
##################################################################################################################################
# Parse json file to get challenges split up into nice HTML code

# Load the json data created earlier, that's sorted alphabetically, and in a neat format)
with open('challenges_export.json', 'r') as f:
    challenges = json.load(f)


@announce
def render_challenge(challenge):
    name = challenge.get('name', 'Unnamed Challenge')
    goal_value = challenge.get('goal_value', '')
    showgoal = challenge.get('showgoal', True)
    description = challenge.get('description', '')

    goal_html = ''
    if showgoal:
        goal_html = f'<p class="goal">Goal: {goal_value}</p>'

    return f'''
    <div class="challenge">
        <h3 class="challenge-name">{name}</h3>
        {goal_html}
        <p class="description">{description}</p>
    </div>
    '''
html_template2 = f"""
{"".join(render_challenge(ch) for ch in challenges)}
"""
#debug_print("L3", "html_template2: ", html_template2)









#####################################################################################################################
# Convert ANSI to HTML
converter = Ansi2HTMLConverter()
html_body = converter.convert(captured_output)

# Assume captured_output contains your output with ANSI codes
# For example, captured_output = your existing output string

# Convert ANSI to HTML
converter = Ansi2HTMLConverter()
html_body = converter.convert(captured_output)

# Wrap in full HTML with styles
html_full = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <link rel="icon" href="html/images/favicon.ico" type="image/x-icon">
  <style>
    body {{
      font-family: Arial, sans-serif;
      background-color: #f0f0f0;
      padding: 20px;
    }}
    @font-face {{
      font-family: 'RDOFont'; /* name you'll use in CSS */
      src: url('Fonts/RDO_chinese_rocks_rg.otf') format('opentype');
      font-weight: normal;
      font-style: normal;
    }}
    h1 {{
      font-size: 60px;
      text-align: left;
      margin-bottom: 40px;
    }}
    /* Style for challenges */
    .challenge {{
      font-size: 32px;
      margin: 10px 0;
    }}
    /* Banner overlay styles */
    .banner-container {{
      position: relative;
      width: 100%;
      max-width: 850px; /* match your banner width, or set to 100% for full width */
      margin: 0; /* center container in page */
    }}

    .banner-image {{
      width: 100%; /* makes image fill container width */
      height: auto;
      display: block;
    }}

    .banner-title {{
      font-family: 'RDOFont', sans-serif;
      position: absolute;
      top: 7.5%; /* adjust vertical position as needed */
      left: 50%;
      transform: translateX(-50%);
      color: white;
      margin: 0;
      padding: 10px;
      /* Responsive font size: */
      font-size: clamp(0.25em, 5vw, 3em);
      /* Drop shadow effect: */
      text-shadow: 2px 2px 4px rgba(0,0,0,0.7);
    }}
    
    .date-below-title {{
      font-family: 'RDOFont', sans-serif;
      position: absolute;
      top: 32%; /* adjust vertical position as needed */
      left: 50%;
      transform: translateX(-50%);
      color: white;
      font-size: clamp(0.15em, 1.75vw, 1.75em);
      margin: 0;
      padding: 10px;
      /* background: rgba(0, 0, 0, 0.3);
      /* Drop shadow effect: */
      text-shadow: 2px 2px 4px rgba(0,0,0,0.7);
    }}
  </style>
</head>
<body>
  <div class="banner-container">
    <img src="HTML/images/RDO_Banner.jpg" alt="Banner" class="banner-image"/>
    <h1 class="banner-title">Daily Challenges</h1>
    <div class="date-below-title">{human_readable_date}</div>
  </div>
  {html_body}
</body>
</html>
"""

# Save to file
#Open the 'challenges_styled.html' file for writing, utf-8 encoding.
#The 'with' part is the context manager which ensures the file is properly closed after the block completes, even if errors happen.
with open("challenges_styled.html", "w", encoding="utf-8") as f:
    
    #f.write('<img src="/HTML/images/RDO_Banner.jpg" alt="Banner" style="width: 200px; height: auto; display: block; margin: 0 auto;"/>\n')  # Adjust width as needed
    f.write(html_full)
debug_print("iblue", "Styled challenges saved to 'challenges_styled.html'. Open it in your browser.")











# *******************************************************************************************************************************************************************
# New version of the HTML with better control over font sizes etc.

import json

with open('final_challenges_output.json', 'r') as f:
    data = json.load(f)
    debug_print("L2", "Loaded in the final_challenges_output.json")

challenges = data['final_name']

# 2: Generate HTML for challenges
html_challenges = ""

for challenge in challenges:
    text = challenge['text']
    description = challenge['description']
    
    # Style for 'text' and 'description'
    # For example, you can set font size and font family here
    challenge_html = f"""
    <div class="challenge">
      <div class="challenge-text">{text}</div>
    """
    if description:
        challenge_html += f"""
      <div class="challenge-desc">{description}</div>
    """
    challenge_html += "</div>"
    html_challenges += challenge_html




html_full2 = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8" />
  <link rel="icon" href="html/images/favicon.ico" type="image/x-icon" />
  <style>
    /* your existing styles */
    body {{
      font-family: Arial, sans-serif;
      background-color: #000000;
      padding: 20px;
    }}
    @font-face {{
      font-family: 'RDOFont'; /* name you'll use in CSS */
      src: url('Fonts/RDO_chinese_rocks_rg.otf') format('opentype');
      font-weight: normal;
      font-style: normal;
    }}
    @font-face {{
      font-family: 'Hapna';
      src: url('Fonts/Hapna.woff2') format('woff2');
      font-weight: normal;
      font-style: normal;
    }}
    h1 {{
      font-size: 60px;
      text-align: left;
      margin-bottom: 40px;
    }}
    /* Wrapper for challenges to limit max width and center */
    .challenges-wrapper {{
    max-width: 850px;
    margin-left: 0; /* align to the left */
    /* optional: add some padding if needed */
    padding-left: 10px; /* optional padding for spacing from the edge */
    }}
    /* Style for individual challenges */
    .challenge {{
      margin-bottom: 10px;
      border-bottom: 1px solid #404040; /* separator line */
      padding-bottom: 10px; /* space after the line */
    }}
    /* Remove border from last challenge */
    .challenge:last-child {{
      border-bottom: none;
    }}
    /* Styles for text and description */
    .challenge-text {{
      font-family: 'Hapna', sans-serif;
      font-size: 20px;
      color: white;
    }}
    .challenge-desc {{
      font-family: 'Hapna', serif;
      font-size: 16px;
      color: #999999;
      white-space: pre-wrap;
      margin-bottom: 5px;
    }}
    /* Banner overlay styles */
    .banner-container {{
      position: relative;
      width: 100%;
      max-width: 850px; /* match your banner width, or set to 100% for full width */
      margin-left: 0; /* align left */
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
      top: 7.5%;
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
      top: 32%;
      left: 50%;
      transform: translateX(-50%);
      color: white;
      font-size: clamp(0.15em, 1.5vw, 1.5em);
      margin: 0;
      padding: 10px;
      text-shadow: 2px 2px 4px rgba(0,0,0,0.7);
    }}
  </style>
</head>
<body>
  <div class="banner-container">
    <img src="HTML/images/RDO_Banner.jpg" alt="Banner" class="banner-image"/>
    <h1 class="banner-title">Daily Challenges</h1>
    <div class="date-below-title">{human_readable_date}</div>
  </div>

  <!-- Challenges wrapped in container to limit width -->
  <div class="challenges-wrapper">
    {html_challenges}
  </div>
</body>
</html>
"""

# Save to file
#Open the 'challenges_styled.html' file for writing, utf-8 encoding.
#The 'with' part is the context manager which ensures the file is properly closed after the block completes, even if errors happen.
with open("challenges_styled2.html", "w", encoding="utf-8") as f:
    
    f.write(html_full2)
debug_print("iblue", "Styled challenges saved to 'challenges_styled2.html'. Open it in your browser.")




#print("\nDAILY CHALLENGES\n")

#print("-" * 80)