import sys
import logging

# Add the application directory to the PYTHONPATH
sys.path.insert(0, '/var/www/html')

# Import the Flask application
from flaskapp import app as application

# Optional: Set up logging
logging.basicConfig(stream=sys.stderr)
sys.stderr = open('/var/log/apache2/flaskapp_error.log', 'a')
