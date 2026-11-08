from pathlib import Path
from PIL import Image, ImageOps

source = Image.open("kulzzy-icon-512.png").convert("RGBA")

res = Path("android/app/src/main/res")

sizes = {
    "mdpi": 48,
    "hdpi": 72,
    "xhdpi": 96,
    "xxhdpi": 144,
    "xxxhdpi": 192
}

# Create proper launcher icons
for density, size in sizes.items():
    folder = res / f"mipmap-{density}"
    folder.mkdir(parents=True, exist_ok=True)

    background = Image.new("RGBA", (size, size), "#06122A")

    logo = ImageOps.contain(
        source,
        (int(size * 0.82), int(size * 0.82)),
        method=Image.Resampling.LANCZOS
    )

    position = (
        (size - logo.width) // 2,
        (size - logo.height) // 2
    )

    background.alpha_composite(logo, position)

    background.save(folder / "ic_launcher.png")
    background.save(folder / "ic_launcher_round.png")

# Adaptive icon foreground
drawable = res / "drawable"
drawable.mkdir(parents=True, exist_ok=True)

foreground = Image.new("RGBA", (432, 432), (0, 0, 0, 0))

logo = ImageOps.contain(
    source,
    (280, 280),
    method=Image.Resampling.LANCZOS
)

position = (
    (432 - logo.width) // 2,
    (432 - logo.height) // 2
)

foreground.alpha_composite(logo, position)
foreground.save(drawable / "ic_launcher_foreground.png")

# Background colour
values = res / "values"
values.mkdir(parents=True, exist_ok=True)

(values / "kulzzy_icon_colors.xml").write_text(
    '''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="kulzzy_icon_background">#06122A</color>
</resources>'''
)

# Android adaptive launcher icon
adaptive = res / "mipmap-anydpi-v26"
adaptive.mkdir(parents=True, exist_ok=True)

xml = '''<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@color/kulzzy_icon_background"/>
    <foreground android:drawable="@drawable/ic_launcher_foreground"/>
</adaptive-icon>'''

(adaptive / "ic_launcher.xml").write_text(xml)
(adaptive / "ic_launcher_round.xml").write_text(xml)

print("KULZZY RADIO LOGO ICON GENERATED SUCCESSFULLY")
