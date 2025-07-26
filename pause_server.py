#####################################################################################################################
##  CREATE A SMALL LOCAL PYTHON SERVER TO DETECT PAUSE RDR2 PROCESS                                                ##
#####################################################################################################################


from flask import Flask
import psutil
import time
import threading
import random  # <-- Added for random sleep time

# Enable CORS so the server can receive requests from web pages (e.g., HTML button in browser)
from flask_cors import CORS

import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

PROCESS_NAME = "RDR2.exe"

@app.route('/pause', methods=['POST'])
def pause_rdr2():
    proc = next((p for p in psutil.process_iter(['name']) if p.info['name'] == PROCESS_NAME), None)
    if not proc:
        return "RDR2.exe not found", 404

    sleep_time = random.uniform(8, 12)  # generate random sleep time before thread, 8 seconds is minimum

    def do_pause():
        try:
            start_time = datetime.now()
            print(f"[{start_time}] Pausing {PROCESS_NAME} for {sleep_time:.2f} seconds...")
            proc.suspend()
            time.sleep(sleep_time)
            proc.resume()
            end_time = datetime.now()
            print(f"[{end_time}] Resumed {PROCESS_NAME}.")
        except Exception as e:
            print(f"Error: {e}")

    threading.Thread(target=do_pause).start()
    return f"RDR2 paused for {sleep_time:.2f} seconds", 200


if __name__ == '__main__':
    filepath = __file__  # current script path
    timestamp = os.path.getmtime(filepath)
    mod_time = datetime.fromtimestamp(timestamp)
    print(f"***pause_server.py last modified: {mod_time}***")
    app.run(port=6969)
