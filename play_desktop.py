import threading
import webbrowser
import sys
import os
import time
import subprocess

# Standardize pathing
# 1. Get the directory where this script is located (the root)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# 2. Add both root and src to the path
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
src_path = os.path.join(BASE_DIR, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Now we can import the app
try:
    from src.ui.web.app import app
except ImportError:
    # Fallback for different environments
    from ui.web.app import app

PORT = 5000
URL = f"http://127.0.0.1:{PORT}"

def start_server():
    """Starts the Flask server."""
    # Run without debug to avoid reloader issues in thread
    app.run(port=PORT, debug=False, use_reloader=False)

def open_browser():
    """Opens the browser in app mode if possible."""
    # Give the server a moment to start
    time.sleep(1.5)
    
    print(f"Launching PWS Desktop at {URL}...")
    
    # Try to open in Chrome App Mode (looks native)
    try:
        subprocess.Popen([
            "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            f"--app={URL}",
            "--user-data-dir=C:\\tmp\\pws_profile", # Separate profile to avoid polluting main browser
            "--window-size=1280,800"
        ])
        return
    except FileNotFoundError:
        pass
        
    # Try Edge App Mode
    try:
        subprocess.Popen([
            "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
            f"--app={URL}",
            "--user-data-dir=C:\\tmp\\pws_edge_profile",
            "--window-size=1280,800"
        ])
        return
    except FileNotFoundError:
        pass

    # Fallback to standard browser tab
    webbrowser.open(URL)

if __name__ == "__main__":
    # Start server in a separate thread
    server_thread = threading.Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()

    # Launch UI
    open_browser()

    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")
