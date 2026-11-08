from pathlib import Path
from PIL import Image, ImageOps
import xml.etree.ElementTree as ET

source = Image.open("kulzzy-icon-512.png").convert("RGBA")
res = Path("android/app/src/main/res")

sizes = {
    "mdpi": 48,
    "hdpi": 72,
    "xhdpi": 96,
    "xxhdpi": 144,
    "xxxhdpi": 192
}

for density, size in sizes.items():
    folder = res / f"mipmap-{density}"
    folder.mkdir(parents=True, exist_ok=True)

    icon = ImageOps.fit(
        source,
        (size, size),
        method=Image.Resampling.LANCZOS
    )

    icon.save(folder / "ic_launcher.png")
    icon.save(folder / "ic_launcher_round.png")

drawable = res / "drawable"
drawable.mkdir(parents=True, exist_ok=True)

foreground = Image.new("RGBA", (432, 432), (0, 0, 0, 0))
logo = ImageOps.contain(
    source,
    (264, 264),
    method=Image.Resampling.LANCZOS
)

position = (
    (432 - logo.width) // 2,
    (432 - logo.height) // 2
)

foreground.alpha_composite(logo, position)
foreground.save(drawable / "ic_launcher_foreground.png")

values = res / "values"
values.mkdir(parents=True, exist_ok=True)

(values / "kulzzy_icon_colors.xml").write_text(
    '''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="kulzzy_icon_background">#06122A</color>
</resources>'''
)

adaptive = res / "mipmap-anydpi-v26"
adaptive.mkdir(parents=True, exist_ok=True)

xml = '''<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@color/kulzzy_icon_background"/>
    <foreground android:drawable="@drawable/ic_launcher_foreground"/>
</adaptive-icon>'''

(adaptive / "ic_launcher.xml").write_text(xml)
(adaptive / "ic_launcher_round.xml").write_text(xml)

print("Kulzzy Radio launcher icons generated successfully.")
