def hex_to_rgba(hex_color, alpha=1):
    normalized_hex = hex_color.lstrip("#")

    if len(normalized_hex) != 6:
        raise ValueError("Hex color must use 6 characters.")

    red = int(normalized_hex[0:2], 16) / 255
    green = int(normalized_hex[2:4], 16) / 255
    blue = int(normalized_hex[4:6], 16) / 255

    return red, green, blue, alpha


class Colors:
    BRAND_PRIMARY_DARK = "#062E26"
    BRAND_PRIMARY = "#0B5D4D"
    BRAND_PRIMARY_LIGHT = "#147A64"

    BRAND_ACCENT = "#D4AF37"
    BRAND_ACCENT_SOFT = "#F2DF9B"

    BACKGROUND = "#F8F6F0"
    SURFACE = "#FFFFFF"
    SURFACE_MUTED = "#EEF3EC"

    TEXT_PRIMARY = "#10201B"
    TEXT_SECONDARY = "#5E6B66"
    TEXT_MUTED = "#8A9691"
    TEXT_ON_PRIMARY = "#FFFFFF"

    BORDER = "#D8DED8"

    INCOME = "#0E7A5F"
    EXPENSE = "#B94A48"

    SUCCESS = "#0E7A5F"
    WARNING = "#B8860B"
    ERROR = "#B94A48"


class Spacing:
    XS = 4
    SM = 8
    MD = 12
    LG = 16
    XL = 24
    XXL = 32


class Radius:
    SM = 8
    MD = 14
    LG = 20
    PILL = 999


class FontSize:
    DISPLAY_AMOUNT = 32
    SCREEN_TITLE = 24
    SECTION_TITLE = 18
    CARD_TITLE = 16
    BODY = 14
    SUPPORTING = 12
    BUTTON = 14


class ComponentSize:
    TOP_BAR_HEIGHT = 56
    BUTTON_HEIGHT = 48
    SMALL_BUTTON_HEIGHT = 40
    ICON_BUTTON_SIZE = 48
    TOUCH_TARGET = 48
    CARD_MIN_HEIGHT = 72


class Elevation:
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 4