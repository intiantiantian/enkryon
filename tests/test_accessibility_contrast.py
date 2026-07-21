from pathlib import Path

import pytest

from theme.tokens import Colors


def _relative_luminance(hex_color):
    channels = [
        int(hex_color[index:index + 2], 16) / 255
        for index in (1, 3, 5)
    ]

    linear_channels = [
        channel / 12.92
        if channel <= 0.04045
        else ((channel + 0.055) / 1.055) ** 2.4
        for channel in channels
    ]

    return (
        0.2126 * linear_channels[0]
        + 0.7152 * linear_channels[1]
        + 0.0722 * linear_channels[2]
    )


def _contrast_ratio(foreground, background):
    luminances = sorted(
        (
            _relative_luminance(foreground),
            _relative_luminance(background),
        ),
        reverse=True,
    )
    return (luminances[0] + 0.05) / (luminances[1] + 0.05)


@pytest.mark.parametrize(
    ("foreground", "background"),
    [
        (Colors.TEXT_PRIMARY, Colors.SURFACE),
        (Colors.TEXT_PRIMARY, Colors.BACKGROUND),
        (Colors.TEXT_SECONDARY, Colors.SURFACE),
        (Colors.TEXT_SECONDARY, Colors.BACKGROUND),
        (Colors.TEXT_MUTED, Colors.SURFACE),
        (Colors.TEXT_MUTED, Colors.BACKGROUND),
        (Colors.TEXT_ON_PRIMARY, Colors.BRAND_PRIMARY),
        (Colors.TEXT_ON_PRIMARY, Colors.BRAND_PRIMARY_LIGHT),
        (Colors.BRAND_PRIMARY, Colors.BRAND_ACCENT_SOFT),
        (Colors.INCOME, Colors.SURFACE),
        (Colors.EXPENSE, Colors.SURFACE),
    ],
)
def test_text_color_pairs_meet_wcag_aa_contrast(
    foreground,
    background,
):
    assert _contrast_ratio(foreground, background) >= 4.5


def test_notes_placeholder_uses_readable_text_token():
    project_root = Path(__file__).resolve().parents[1]
    layout = (
        project_root / "kv" / "add_transaction.kv"
    ).read_text(encoding="utf-8")

    notes_label = layout.split(
        "id: notes_label",
        maxsplit=1,
    )[1]
    screen_source = (
        project_root / "screens" / "add_transaction.py"
    ).read_text(encoding="utf-8")

    assert "theme_text_color: 'Custom'" in notes_label
    assert (
        "text_color: get_color_from_hex(Colors.TEXT_SECONDARY)"
        in notes_label
    )
    assert "theme_text_color: 'Hint'" not in notes_label
    assert (
        "self.ids.notes_label.theme_text_color = 'Custom'"
        in screen_source
    )
    assert (
        "self.ids.notes_label.theme_text_color = 'Hint'"
        not in screen_source
    )
