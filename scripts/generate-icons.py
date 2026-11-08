from pathlib import Path
from PIL import Image, ImageOps
import re

# Official Kulzzy Radio logo
source_path = Path("kulzzy-icon-512.png")

if not source_path.exists():
    raise FileNotFoundError("Kulzzy Radio logo was not downloaded.")

source = Image.open(source_path).convert("RGBA")

# Android resources folder
res = Path("android/app/src/main/res")

# Generate standard Android launcher icons
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

    icon = Image.new("RGBA", (size, size), "#06122A")

    logo = ImageOps.contain(
        source,
        (int(size * 0.80), int(size * 0.80)),
        method=Image.Resampling.LANCZOS
    )

    x = (size - logo.width) // 2
    y = (size - logo.height) // 2

    icon.alpha_composite(logo, (x, y))

    icon.save(folder / "ic_launcher.png")
    icon.save(folder / "ic_launcher_round.png")

# Generate adaptive icon foreground
drawable = res / "drawable"
drawable.mkdir(parents=True, exist_ok=True)

foreground = Image.new("RGBA", (432, 432), (0, 0, 0, 0))

logo = ImageOps.contain(
    source,
    (250, 250),
    method=Image.Resampling.LANCZOS
)

x = (432 - logo.width) // 2
y = (432 - logo.height) // 2

foreground.alpha_composite(logo, (x, y))
foreground.save(drawable / "ic_launcher_foreground.png")

# Adaptive icon background
values = res / "values"
values.mkdir(parents=True, exist_ok=True)

(values / "kulzzy_icon_colors.xml").write_text(
    '''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="kulzzy_icon_background">#06122A</color>
</resources>'''
)

# Adaptive icon configuration
adaptive = res / "mipmap-anydpi-v26"
adaptive.mkdir(parents=True, exist_ok=True)

adaptive_xml = '''<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@color/kulzzy_icon_background"/>
    <foreground android:drawable="@drawable/ic_launcher_foreground"/>
</adaptive-icon>'''

(adaptive / "ic_launcher.xml").write_text(adaptive_xml)
(adaptive / "ic_launcher_round.xml").write_text(adaptive_xml)

# FORCE Android to use the Kulzzy Radio icons
manifest = Path("android/app/src/main/AndroidManifest.xml")

if not manifest.exists():
    raise FileNotFoundError("AndroidManifest.xml was not found.")

content = manifest.read_text(encoding="utf-8")

match = re.search(r"<application\b[^>]*>", content)

if not match:
    raise RuntimeError("Android application declaration was not found.")

tag = match.group(0)

for attribute, value in [
    ("icon", "@mipmap/ic_launcher"),
    ("roundIcon", "@mipmap/ic_launcher_round")
]:
    pattern = rf'\s+android:{attribute}\s*=\s*["\'][^"\']*["\']'

    if re.search(pattern, tag):
        tag = re.sub(
            pattern,
            f' android:{attribute}="{value}"',
            tag
        )
    else:
        tag = tag[:-1] + f' android:{attribute}="{value}">'

content = content[:match.start()] + tag + content[match.end():]
manifest.write_text(content, encoding="utf-8")

# Verify the generated icons
for density in sizes:
    icon = res / f"mipmap-{density}" / "ic_launcher.png"

    if not icon.exists() or icon.stat().st_size == 0:
        raise RuntimeError(f"Icon generation failed: {icon}")

print("SUCCESS: KULZZY RADIO LOGO GENERATED AND CONNECTED TO ANDROID.")
