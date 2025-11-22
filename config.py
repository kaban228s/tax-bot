import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TOKEN")
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() in ("true", "1", "yes")

YOOMONEY_TOKEN = os.getenv("YOOMONEY_TOKEN", "")
YOOMONEY_WALLET = os.getenv("YOOMONEY_WALLET", "")
YOOMONEY_REDIRECT_URI = os.getenv("YOOMONEY_REDIRECT_URI", "")