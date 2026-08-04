"""
Mini App Configuration

This module stores configuration values used by the
HABESHAGO Telegram Mini App.
"""

import os

from dotenv import load_dotenv


load_dotenv()


class MiniAppSettings:
    APP_NAME = "HABESHAGO Mini App"
    PLATFORM_NAME = "HABESHAGO"
    VERSION = "1.0.0"

    THEME = "light"

    DEFAULT_LANGUAGE = "en"

    ENABLE_MAP = True
    ENABLE_RIDE = True
    ENABLE_TRANSIT = False
    ENABLE_LOGISTICS = False

    DEVELOPMENT_DRIVER_ID = os.getenv(
        "HABESHAGO_MINI_APP_DRIVER_ID"
    )