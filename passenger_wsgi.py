import sys
import os

# Add the src folder to the python path
# This assumes passenger_wsgi.py is in the project root
project_root = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

# Import the flask app
from ui.web.app import app as application