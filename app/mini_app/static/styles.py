"""
Shared UI Styles

Reusable style definitions for HABESHAGO Mini App.
"""

from app.mini_app.static.design_tokens import (
    BorderRadius,
    Shadows,
    Spacing,
    Typography,
)
from app.mini_app.static.theme import ThemeManager


class UIStyles:
    @staticmethod
    def button(mode="light"):
        theme = ThemeManager.get_theme(mode)

        return {
            "background": theme["primary"],
            "color": theme["text_primary"] if mode == "dark" else "#FFFFFF",
            "padding": f"{Spacing.SMALL} {Spacing.LARGE}",
            "border_radius": BorderRadius.MEDIUM,
            "font_size": Typography.FONT_SIZE_BODY,
            "font_weight": Typography.FONT_WEIGHT_SEMIBOLD,
        }

    @staticmethod
    def card(mode="light"):
        theme = ThemeManager.get_theme(mode)

        return {
            "background": theme["surface"],
            "padding": Spacing.MEDIUM,
            "border_radius": BorderRadius.LARGE,
            "shadow": Shadows.CARD,
        }

    @staticmethod
    def page(mode="light"):
        theme = ThemeManager.get_theme(mode)

        return {
            "background": theme["background"],
            "text_color": theme["text_primary"],
            "padding": Spacing.LARGE,
            "font_family": Typography.FONT_FAMILY,
        }


if __name__ == "__main__":
    print("Button:")
    print(UIStyles.button())

    print()

    print("Card:")
    print(UIStyles.card())

    print()

    print("Page:")
    print(UIStyles.page())