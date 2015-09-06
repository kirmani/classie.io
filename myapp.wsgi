import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/var/www/kirmani.io/ut/public_html')

from myapp import app as application
