import urllib.request
import datetime
import json
import inspect
import textwrap
import os
import io
import sys
import ansi2html
from ansi2html import Ansi2HTMLConverter



#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

# ANSI escape codes for different colors used by debug_print
COLORS = {
    "ireset": 			"\033[0m",     # 0
    "idarkred":			"\033[31m",    # 31
    "idarkgreen":		"\033[32m",    # 32
    "idarkyellow":		"\033[33m",    # 33
    "idarkblue": 		"\033[34m",    # 34
    "idarkpurple":		"\033[35m",    # 35
    "idarkcyan":		"\033[36m",    # 36
    "iblack":			"\033[90m",    # 90
    "ired": 			"\033[91m",    # 91
    "igreen":			"\033[92m",    # 92
    "iyellow":			"\033[93m",    # 93
    "iblue": 			"\033[94m",    # 94
    "ipurple": 			"\033[95m",    # 95
    "icyan": 			"\033[96m",    # 96
    "iwhite":			"\033[97m",    # 97


    "bblack":			"\033[40m",				# Background: Black
    "bred":				"\033[41m",				# Background: Red
    "bgreen":			"\033[42m",				# Background: Green
    "byellow":			"\033[43m",				# Background: Yellow
    "bblue":			"\033[44m",				# Background: Blue
    "bpurple":			"\033[45m",				# Background: Magenta
    "bcyan":			"\033[46m",				# Background: Cyan
    "bwhite":			"\033[47m\033[30m",		# Background: White		ink: Black
    "bRESET":			"\033[49m",				# Reset background color

    "bbrightblack":		"\033[100m",			# Background: Bright Black (Grey)
    "bbrightred":		"\033[101m",			# Background: Bright Red
    "bbrightgreen":		"\033[102m",			# Background: Bright Green
    "bbrightyellow":	"\033[103m",			# Background: Bright Yellow
    "bbrightblue":		"\033[104m",			# Background: Bright Blue
    "bbrightpurple":	"\033[105m",			# Background: Bright Magenta
    "bbrightcyan":		"\033[106m\033[30m",	# Background: Bright Cyan
    "bbrightwhite":		"\033[107m\033[30m"		# Background: Bright White
}

#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#




def debug_print(color: str, *messages: any, debug: bool = True):
    """
    Print debug messages in specified color if debug is True.
    It accepts the prefix "DEBUG:" as part of the message.

    :param color: Color string (e.g. 'cyan', 'purple', 'red', 'blue').
    :param messages: One or more messages to print.
    :param debug: Boolean to enable/disable debug printing.
    """
    

    
    if debug:
        frame = inspect.currentframe()                  # Get the current stack frame
        caller_frame = frame.f_back                     # Get the caller's frame
        line_number = caller_frame.f_lineno             # Get the line number
        
        # Print debugging information directly
        #print("DEBUG INFO:")
        #print(f"Debugging at line number: {line_number}")

        color_code = COLORS.get(color.lower(), COLORS["icyan"])  # Default to cyan if not found

        # Combine all message parts into a single string
        combined_message = " ".join(str(msg) for msg in messages)

        # Check if there are any messages to print
        if not combined_message.strip():
            print(f"LINE {line_number}: No message provided.")
            return

        # Define a wrap width
        wrap_width = 125  # Total width for wrapping
        max_indent = 12   # This value is the indent in from the left side in characters - Increase for massive programs
                          # because we can't easily pass the highest line number into the function
                          
        # Create the initial output line: "LINE <line_number>: "
        line_info = f"LINE {line_number}: "
        line_info_length = len(line_info)
        
        # Prepare the message with wrapping for the entire combined message
        wrapped_message = textwrap.fill(combined_message, width=wrap_width)
        
        # Indentation for first line
        indent_str = ' ' * (max_indent - line_info_length) # The max indent minus the Line Number Length
        
        # Print the first line, with the line prefix
        first_line = wrapped_message.splitlines()[0]
        print(f"{line_info}{indent_str}{color_code}{first_line}{COLORS['ireset']}")

        # Indentation for wrapped lines
        indent_str = ' ' * (max_indent)  # indent for wrapped lines

        # Print the wrapped lines, starting from the second line
        for line in wrapped_message.splitlines()[1:]:  # Start from the second line
            print(f"{indent_str}{color_code}{line}{COLORS['ireset']}")  # Indent additional lines



###############################################################################################################################################################################################################################################################################################################################
        
        
        
        
        
        
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
# Import the predefined_challenges dictionary data from a separate .py file called RDO_challenges_data.py
# This imports the entire RDO_challenges_data.py module, which contains the predefined_challenges list.
import RDO_challenges_data


# This assigns the list stored in RDO_challenges_data.predefined_challenges to a variable named predefined_challenges
# in this current script, so it can be used directly without the challenges_data. prefix.
predefined_challenges = RDO_challenges_data.predefined_challenges

# Step 2: Sort challenges alphabetically by 'name'
sorted_challenges = sorted(predefined_challenges, key=lambda x: x['name'])


# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# **************************************************************************************************************************************************************************************

# The next bit will create a dictionary like this:
# predefined_lookup = {'mpgc_story_mission_wins': {'key': 'mpgc_story_mission_wins', 'name': 'Story Mission Wins', 'showgoal': 'y', ...},

predefined_lookup = {c['key']: c for c in predefined_challenges}

# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Check if there's a local version of the index.json file
# Your existing local filename path
local_filename = r"C:\Users\Dunk\Documents\Thonny Bits\RDO Daily Challenges\index.json"

# URL for downloading if needed
url = "https://api.rdo.gg/challenges/index.json"

# Determine UTC now
now = datetime.datetime.utcnow()

# Function to download and save the JSON data
def download_json():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            data_bytes = response.read()
            data_str = data_bytes.decode('utf-8')
            data = json.loads(data_str)
        # Save to local file
        with open(local_filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print("Successfully downloaded and saved index.json.")
        return data
    except Exception as e:
        print("Error fetching data:", e)
        raise

# Check if local index.json exists
if os.path.exists(local_filename):
    # Check if file is empty
    if os.path.getsize(local_filename) == 0:
        print("index.json is empty. Downloading new data.")
        data = download_json()
    else:
        # Try loading JSON to verify validity
        try:
            with open(local_filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            print("Invalid JSON detected. Deleting corrupt file and re-downloading.")
            os.remove(local_filename)
            data = download_json()
        else:
            debug_print("bwhite", "JSON file passed integrity check")
            # Check if the file was last modified after 6am UTC today
            mod_time = os.path.getmtime(local_filename)
            mod_datetime = datetime.datetime.fromtimestamp(mod_time)
            today_6am = datetime.datetime.combine(now.date(), datetime.time(6, 0))
            if mod_datetime > today_6am:
                # It's recent enough; use the local version
                print("Local index.json was saved after 6am today. Using local version.")
            else:
                # It's older than 6am; ask if you want to download a new one
                choice = input("Local index.json is older than today's 6am refresh. Download new version? (Y/N): ").lower()
                if choice == 'y':
                    data = download_json()
                else:
                    print("Using existing local index.json.")
else:
    # No local file; download automatically
    print("No local index.json found. Downloading from URL...")
    data = download_json()
# -------------------------------------------------------------------------------------------------------------------------------------------


# Extract challenges list
debug_print("bbrightwhite", "Extract Challenges List From JSON") # Just to have a debug heading.

# This will extract the general challenges from the json file (id, title, goal, goalFormat)
general_challenges = data.get('general', [])
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

# Redirect stdout to buffer
sys.stdout = buffer

######################################################################################################

print("\nDAILY CHALLENGES\n")
print("-" * 120)

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

# Step 3: Loop through sorted challenges and apply your display logic
for challenge in sorted_challenges:
    name = challenge['name']
    goal_value = challenge['goal_value']
    showgoal = challenge['showgoal']

    
    
    # Decide what to print based on your conditions:
    if showgoal == 'y':
        #debug_print("icyan", "showgoal: ", showgoal)
        print(f"{goal_value} {name}")
    elif goal_value == 1 and showgoal is None or showgoal :
        #debug_print("iblue", "showgoal: ", showgoal)
        print(f"{name}")
    else:
        # For all other cases, print goal_value and name
        print(f"{goal_value} {name}")
     
    description = challenge.get('description', None) 
    if description is not None:
        print(f"\033[3;33m{challenge['description']}\033[0m")
    elif description is None:
        pass

    print("-" * 120)


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

debug_print("iblue", "Challenges data saved to challenges_export.json.")
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
print(captured_output)







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
<html>
<head>
  <style>
    body {{
      font-family: Arial, sans-serif;
      background-color: #f0f0f0;
      padding: 20px;
    }}
    h1 {{
      font-size: 60px;
      text-align: left;
      margin-bottom: 40px;
    }}
    /* Optional: style for the challenges */
    .challenge {{
      font-size: 32px;
      margin: 10px 0;
    }}
  </style>
</head>
<body>
  <h1>Daily Challenges</h1>
  {html_body}
</body>
</html>
"""

# Save to file
with open("challenges_styled.html", "w", encoding="utf-8") as f:
    f.write(html_full)

debug_print("iblue", "Styled challenges saved to 'challenges_styled.html'. Open it in your browser.")




















#print("\nDAILY CHALLENGES\n")

#print("-" * 80)