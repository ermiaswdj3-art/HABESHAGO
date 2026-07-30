"""
HABESHAGO Design Tokens

Centralized visual design rules for the
HABESHAGO Telegram Mini App.
"""


class BrandColors:
    PRIMARY_GREEN = "#0A8F3D"
    PRIMARY_GREEN_DARK = "#066B2D"

    ACCENT_GOLD = "#F4B400"
    ACCENT_GOLD_DARK = "#C58E00"

    ETHIOPIAN_RED = "#D62828"

    WHITE = "#FFFFFF"
    BLACK = "#111111"

    BACKGROUND_LIGHT = "#F6F8F7"
    SURFACE_LIGHT = "#FFFFFF"
    TEXT_PRIMARY_LIGHT = "#111111"
    TEXT_SECONDARY_LIGHT = "#5F6B65"

    BACKGROUND_DARK = "#101411"
    SURFACE_DARK = "#18201B"
    TEXT_PRIMARY_DARK = "#FFFFFF"
    TEXT_SECONDARY_DARK = "#B8C2BC"

    BORDER_LIGHT = "#DDE5E0"
    BORDER_DARK = "#2C3831"

    SUCCESS = "#0A8F3D"
    WARNING = "#F4B400"
    ERROR = "#D62828"


class Typography:
    FONT_FAMILY = (
        "Inter, system-ui, -apple-system, BlinkMacSystemFont, "
        "'Segoe UI', sans-serif"
    )

    FONT_SIZE_SMALL = "12px"
    FONT_SIZE_BODY = "16px"
    FONT_SIZE_SUBTITLE = "18px"
    FONT_SIZE_TITLE = "24px"
    FONT_SIZE_HERO = "32px"

    FONT_WEIGHT_REGULAR = 400
    FONT_WEIGHT_MEDIUM = 500
    FONT_WEIGHT_SEMIBOLD = 600
    FONT_WEIGHT_BOLD = 700


class Spacing:
    EXTRA_SMALL = "4px"
    SMALL = "8px"
    MEDIUM = "16px"
    LARGE = "24px"
    EXTRA_LARGE = "32px"
    SECTION = "48px"


class BorderRadius:
    SMALL = "8px"
    MEDIUM = "14px"
    LARGE = "20px"
    PILL = "999px"


class Shadows:
    CARD = "0 6px 18px rgba(0, 0, 0, 0.08)"
    FLOATING = "0 10px 30px rgba(0, 0, 0, 0.14)"


class Motion:
    FAST = "150ms"
    NORMAL = "250ms"
    SLOW = "400ms"

    EASING = "ease-in-out"


def get_design_tokens():
    """
    Returns the design system as structured data.
    """

    return {
        "colors": {
            "primary_green": BrandColors.PRIMARY_GREEN,
            "accent_gold": BrandColors.ACCENT_GOLD,
            "ethiopian_red": BrandColors.ETHIOPIAN_RED,
            "background_light": BrandColors.BACKGROUND_LIGHT,
            "background_dark": BrandColors.BACKGROUND_DARK,
        },
        "typography": {
            "font_family": Typography.FONT_FAMILY,
            "body_size": Typography.FONT_SIZE_BODY,
            "title_size": Typography.FONT_SIZE_TITLE,
            "hero_size": Typography.FONT_SIZE_HERO,
        },
        "spacing": {
            "small": Spacing.SMALL,
            "medium": Spacing.MEDIUM,
            "large": Spacing.LARGE,
        },
        "radius": {
            "small": BorderRadius.SMALL,
            "medium": BorderRadius.MEDIUM,
            "large": BorderRadius.LARGE,
        },
        "motion": {
            "fast": Motion.FAST,
            "normal": Motion.NORMAL,
            "slow": Motion.SLOW,
        },
    }


if __name__ == "__main__":
    print(get_design_tokens())