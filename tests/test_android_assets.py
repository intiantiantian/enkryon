from configparser import ConfigParser
from pathlib import Path

from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BUILD_SPEC = PROJECT_ROOT / "buildozer.spec"
ICON_DIRECTORY = PROJECT_ROOT / "assets" / "icon"

LEGACY_ICON = ICON_DIRECTORY / "enkryon.png"
ADAPTIVE_FOREGROUND = (
    ICON_DIRECTORY / "enkryon_adaptive_foreground.png"
)
ADAPTIVE_BACKGROUND = (
    ICON_DIRECTORY / "enkryon_adaptive_background.png"
)
PRESPLASH = PROJECT_ROOT / "assets" / "splash" / "enkryon_splash.png"


def load_build_spec():
    parser = ConfigParser(interpolation=None)
    parser.read(BUILD_SPEC, encoding="utf-8")
    return parser["app"]


def test_build_configuration_uses_versioned_android_assets():
    app = load_build_spec()

    assert app["icon.filename"] == (
        "%(source.dir)s/assets/icon/enkryon.png"
    )
    assert app["icon.adaptive_foreground.filename"] == (
        "%(source.dir)s/assets/icon/enkryon_adaptive_foreground.png"
    )
    assert app["icon.adaptive_background.filename"] == (
        "%(source.dir)s/assets/icon/enkryon_adaptive_background.png"
    )
    assert app["presplash.filename"] == (
        "%(source.dir)s/assets/splash/enkryon_splash.png"
    )
    assert app["android.presplash_color"].upper() == "#FDF8F2"


def test_legacy_icon_has_buildozer_dimensions():
    with Image.open(LEGACY_ICON) as image:
        assert image.format == "PNG"
        assert image.size == (512, 512)


def test_adaptive_foreground_is_transparent_and_mask_safe():
    with Image.open(ADAPTIVE_FOREGROUND) as image:
        assert image.format == "PNG"
        assert image.size == (1024, 1024)
        assert image.mode == "RGBA"

        alpha = image.getchannel("A")
        alpha_minimum, alpha_maximum = alpha.getextrema()
        assert alpha_minimum == 0
        assert alpha_maximum == 255

        bounds = alpha.getbbox()
        assert bounds is not None
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]
        safe_extent = round(image.width * 0.66)

        assert width <= safe_extent
        assert height <= safe_extent


def test_adaptive_background_is_opaque_brand_dark():
    with Image.open(ADAPTIVE_BACKGROUND) as image:
        assert image.format == "PNG"
        assert image.size == (1024, 1024)

        rgb = image.convert("RGB")
        assert rgb.getextrema() == (
            (6, 6),
            (46, 46),
            (38, 38),
        )


def test_presplash_is_portrait_png():
    with Image.open(PRESPLASH) as image:
        assert image.format == "PNG"
        assert image.height > image.width
