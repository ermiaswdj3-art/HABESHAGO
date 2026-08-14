import os

from dotenv import load_dotenv


# Load the .env file
load_dotenv()


# Read values from .env
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

HABESHAGO_MINI_APP_URL = os.getenv(
    "HABESHAGO_MINI_APP_URL"
)

HABESHAGO_RUNTIME_BRIDGE_TOKEN = os.getenv(
    "HABESHAGO_RUNTIME_BRIDGE_TOKEN"
)
