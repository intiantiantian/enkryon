import pytest

from theme.tokens import Colors, Spacing, hex_to_rgba


def test_hex_to_rgba_converts_hex_color_to_kivy_rgba():
    assert hex_to_rgba("#FFFFFF") == (1, 1, 1, 1)


def test_hex_to_rgba_accepts_hex_without_hash():
    assert hex_to_rgba("000000") == (0, 0, 0, 1)


def test_hex_to_rgba_accepts_alpha():
    assert hex_to_rgba("#000000", alpha=0.5) == (0, 0, 0, 0.5)


def test_hex_to_rgba_rejects_invalid_hex_length():
    with pytest.raises(ValueError):
        hex_to_rgba("#FFF")


def test_brand_primary_is_defined():
    assert Colors.BRAND_PRIMARY.startswith("#")


def test_spacing_scale_increases():
    assert Spacing.XS < Spacing.SM < Spacing.MD < Spacing.LG < Spacing.XL