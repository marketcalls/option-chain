import os
from dotenv import load_dotenv

load_dotenv(override=True)

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # OpenAlgo API Credentials
    OPENALGO_API_KEY = os.getenv('OPENALGO_API_KEY', 'your-api-key')
    OPENALGO_HOST = os.getenv('OPENALGO_HOST', 'http://localhost:5000')
    OPENALGO_WS_URL = os.getenv('OPENALGO_WS_URL', 'ws://localhost:8765')
    
    # App Settings
    DEBUG = True
    PORT = 5000
