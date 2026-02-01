import sys, os

# DREAMHOST SPECIFIC: Force the use of the virtual environment
# This replaces the current process with the venv python interpreter
cwd = os.getcwd()
INTERP = os.path.join(cwd, 'venv', 'bin', 'python3')
if sys.executable != INTERP:
    os.execl(INTERP, INTERP, *sys.argv)

# Add the src folder to the python path
src_path = os.path.join(cwd, 'src')
sys.path.insert(0, src_path)

# Import the flask app as 'application' (required by Passenger)
from ui.web.app import app as application