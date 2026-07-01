import os

from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Read values from .env
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")