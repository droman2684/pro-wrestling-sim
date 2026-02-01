import sys
import os

# Set up path
src_path = os.path.join(os.path.dirname(__file__), "src")
sys.path.insert(0, src_path)
os.chdir(os.path.join(src_path, "ui", "desktop"))

# Run the app
exec(open("tkinter_app.py").read())
