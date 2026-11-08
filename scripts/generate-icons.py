from pathlib import Path
from PIL import Image, ImageOps
import re

print("STARTING KULZZY RADIO ICON GENERATION")

# Downloaded official logo
source_path = Path("kulzzy-logo.jpg")

if not source_path.exists():
    raise FileNotFoundError("Official Kulzzy Radio logo is missing.")

source = Image.open(source_path).convert("RGBA")

if source.width < 100 or source.height < 100:
    raise RuntimeError("The downloaded logo is too small.")

print(f"Official logo loaded: {source.width}x{source.height}")

res = Path("android/app/src/main/res")

# Standard Android launcher icons
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

    background = Image.new("RGBA", (size, size), "#06122A")

    logo = ImageOps.contain(
        source,
        (int(size * 0.82), int(size * 0.82)),
        method=Image.Resampling.LANCZOS
    )

    x = (size - logo.width) // 2
    y = (size - logo.height) // 2

    background.alpha_composite(logo, (x, y))

    background.convert("RGB").save(
        folder / "ic_launcher.png"
    )

    background.convert("RGB").save(
        folder / "ic_launcher_round.png"
    )

# Adaptive launcher icon foreground
drawable = res / "drawable"
drawable.mkdir(parents=True, exist_ok=True)

foreground = Image.new("RGBA", (432, 432), (0, 0, 0, 0))

logo = ImageOps.contain(
    source,
    (260, 260),
    method=Image.Resampling.LANCZOS
)

x = (432 - logo.width) // 2
y = (432 - logo.height) // 2

foreground.alpha_composite(logo, (x, y))

foreground.save(
    drawable / "ic_launcher_foreground.png"
)

# Background colour
values = res / "values"
values.mkdir(parents=True, exist_ok=True)

(values / "kulzzy_icon_colors.xml").write_text(
    '''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="kulzzy_icon_background">#06122A</color>
</resources>''',
    encoding="utf-8"
)

# Android adaptive icon
adaptive = res / "mipmap-anydpi-v26"
adaptive.mkdir(parents=True, exist_ok=True)

adaptive_xml = '''<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@color/kulzzy_icon_background"/>
    <foreground android:drawable="@drawable/ic_launcher_foreground"/>
</adaptive-icon>'''

(adaptive / "ic_launcher.xml").write_text(
    adaptive_xml,
    encoding="utf-8"
)

(adaptive / "ic_launcher_round.xml").write_text(
    adaptive_xml,
    encoding="utf-8"
)

# Set the launcher icons in AndroidManifest.xml
manifest = Path("android/app/src/main/AndroidManifest.xml")

if not manifest.exists():
    raise FileNotFoundError("AndroidManifest.xml is missing.")

content = manifest.read_text(encoding="utf-8")

match = re.search(r"<application\b[^>]*>", content)

if not match:
    raise RuntimeError("Android application tag was not found.")

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

# Verify generated icon files
for density, size in sizes.items():
    icon = res / f"mipmap-{density}" / "ic_launcher.png"

    if not icon.exists():
        raise RuntimeError(f"Missing icon: {icon}")

    with Image.open(icon) as check:
        if check.size != (size, size):
            raise RuntimeError(f"Incorrect icon dimensions: {icon}")

print("SUCCESS: OFFICIAL KULZZY RADIO LOGO GENERATED.")
print("SUCCESS: ANDROID LAUNCHER ICONS CONFIGURED.")
