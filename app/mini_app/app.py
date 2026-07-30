"""
HABESHAGO Telegram Mini App

Application entry point.
"""

from app.mini_app.config.settings import MiniAppSettings


def get_application_info():
    """
    Returns basic information about the Mini App.
    """

    return {
        "application": MiniAppSettings.APP_NAME,
        "platform": MiniAppSettings.PLATFORM_NAME,
        "version": MiniAppSettings.VERSION,
        "theme": MiniAppSettings.THEME,
    }


if __name__ == "__main__":
    print(get_application_info())