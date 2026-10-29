import os
import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
ROOT_DIR = CURRENT_DIR.parent
SERVER_DIR = ROOT_DIR / "server"

if str(SERVER_DIR) not in sys.path:
    sys.path.insert(0, str(SERVER_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoproj.settings')

from django.core.wsgi import get_wsgi_application  # noqa: E402
app = get_wsgi_application()

