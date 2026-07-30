"""
Theme Manager

Provides the active visual theme for the
HABESHAGO Mini App.
"""

from app.mini_app.static.design_tokens import BrandColors


class ThemeManager:
    LIGHT = {
        "background": BrandColors.BACKGROUND_LIGHT,
        "surface": BrandColors.SURFACE_LIGHT,
        "text_primary": BrandColors.TEXT_PRIMARY_LIGHT,
        "text_secondary": BrandColors.TEXT_SECONDARY_LIGHT,
        "primary": BrandColors.PRIMARY_GREEN,
        "accent": BrandColors.ACCENT_GOLD,
    }

    DARK = {
        "background": BrandColors.BACKGROUND_DARK,
        "surface": BrandColors.SURFACE_DARK,
        "text_primary": BrandColors.TEXT_PRIMARY_DARK,
        "text_secondary": BrandColors.TEXT_SECONDARY_DARK,
        "primary": BrandColors.PRIMARY_GREEN,
        "accent": BrandColors.ACCENT_GOLD,
    }

    @staticmethod
    def get_theme(mode="light"):
        if mode.lower() == "dark":
            return ThemeManager.DARK

        return ThemeManager.LIGHT


if __name__ == "__main__":
    print(ThemeManager.get_theme())

    print()

    print(ThemeManager.get_theme("dark"))