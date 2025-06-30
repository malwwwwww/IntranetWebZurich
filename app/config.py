import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', os.urandom(24))
    PAPERLESS_API_URL = os.getenv('PAPERLESS_API_URL', 'http://localhost:9000/api')
    WTF_CSRF_ENABLED = True