# Android Icons and Launch Assets

This document records the Android launcher and startup assets packaged for
Enkryon and the checks required when those assets change.

## Packaged Assets

| Purpose | File | Required characteristics |
|---|---|---|
| Legacy launcher icon | `assets/icon/enkryon.png` | 512 x 512 PNG |
| Adaptive foreground | `assets/icon/enkryon_adaptive_foreground.png` | 1024 x 1024 RGBA PNG |
| Adaptive background | `assets/icon/enkryon_adaptive_background.png` | 1024 x 1024 opaque PNG |
| Presplash artwork | `assets/splash/enkryon_splash.png` | Portrait PNG |

`buildozer.spec` points directly to these files. Android uses the adaptive
foreground and background on API 26 and later. The legacy bitmap remains
necessary for Enkryon's minimum supported API and other surfaces that use
the legacy launcher resource.

## Adaptive Icon Design

The foreground preserves the Enkryon gold emblem: the circular arc,
column-letter mark, dot, and six-leaf branch. Essential artwork stays
inside the centered safe zone so launcher masks can display circular,
rounded-square, and device-specific shapes without clipping the mark.

The adaptive background uses the theme's brand-dark color:

```text
#062E26
```

The foreground must retain transparency outside the emblem. Do not flatten
it onto a colored square, add a mask, or move essential artwork toward an
edge.

## Legacy Icon

The legacy 512 x 512 icon is a deterministic resize of the existing
Enkryon icon. It keeps the complete original composition for Android
versions and launcher surfaces that do not use adaptive layers.

Do not replace it with the adaptive foreground alone: a transparent gold
mark has insufficient contrast on arbitrary launcher backgrounds.

## Presplash

The existing portrait presplash remains the startup artwork. Its configured
background is `#FDF8F2`, matching the light upper edge of the image and
avoiding a white flash around the artwork during startup.

The presplash is not a launcher icon. Do not reuse the full portrait image
as an adaptive-icon foreground.

## Verification

### Packaging exclusions

The launcher, adaptive-icon, and presplash files are compiled separately
into Android resources. Their source copies are excluded from the Python
application archive to prevent duplicate files in the APK. Repository
screenshots are documentation assets and are also excluded.

The exclusions do not remove the compiled Android resources. A successful
artifact must still contain:

```text
res/drawable/presplash.jpg
res/mipmap-anydpi-v26/icon.xml
res/mipmap/icon.png
res/mipmap/icon_background.png
res/mipmap/icon_foreground.png
```

Run the asset checks after changing any packaged image or Buildozer path:

```bat
python -m pytest tests/test_android_assets.py -q
```

After the next Android build, inspect the launcher icon on at least one
physical device. Check the home screen, app drawer, and Android application
details screen. The complete emblem must remain visible and centered.

## References

- [Android adaptive icon design](https://developer.android.com/develop/ui/compose/system/icon_design_adaptive)
- [Buildozer application specifications](https://buildozer.readthedocs.io/en/latest/specifications/)
