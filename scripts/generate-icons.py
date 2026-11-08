from pathlib import Path
from PIL import Image, ImageOps
import re
import shutil

print("STARTING KULZZY RADIO ICON FIX")

# Load the official logo
source_path = Path("kulzzy-logo.jpg")

if not source_path.exists():
    raise FileNotFoundError("Official Kulzzy Radio logo is missing.")

source = Image.open(source_path).convert("RGBA")

if source.width < 100 or source.height < 100:
    raise RuntimeError("Logo image is too small.")

res = Path("android/app/src/main/res")

# Remove adaptive icons so Android uses our actual PNG icons
adaptive = res / "mipmap-anydpi-v26"

if adaptive.exists():
    shutil.rmtree(adaptive)

# Official Android launcher icon sizes
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

    background = Image.new(
        "RGBA",
        (size, size),
        "#06122A"
    )

    logo = ImageOps.contain(
        source,
        (int(size * 0.88), int(size * 0.88)),
        method=Image.Resampling.LANCZOS
    )

    x = (size - logo.width) // 2
    y = (size - logo.height) // 2

    background.alpha_composite(logo, (x, y))

    icon = background.convert("RGB")

    icon.save(folder / "ic_launcher.png")
    icon.save(folder / "ic_launcher_round.png")

    with Image.open(folder / "ic_launcher.png") as check:
        if check.size != (size, size):
            raise RuntimeError(
                f"Icon verification failed: {density}"
            )

# Configure Android to use the PNG launcher icons
manifest = Path("android/app/src/main/AndroidManifest.xml")

if not manifest.exists():
    raise FileNotFoundError("Android manifest is missing.")

content = manifest.read_text(encoding="utf-8")

match = re.search(r"<application\b[^>]*>", content)

if not match:
    raise RuntimeError("Android application tag not found.")

tag = match.group(0)

for attribute, value in [
    ("icon", "@mipmap/ic_launcher"),
    ("roundIcon", "@mipmap/ic_launcher_round")
]:

    pattern = (
        rf'\s+android:{attribute}\s*=\s*["\'][^"\']*["\']'
    )

    if re.search(pattern, tag):

        tag = re.sub(
            pattern,
            f' android:{attribute}="{value}"',
            tag
        )

    else:
        tag = tag[:-1] + f' android:{attribute}="{value}">'

content = (
    content[:match.start()]
    + tag
    + content[match.end():]
)

manifest.write_text(content, encoding="utf-8")

print("SUCCESS: Official Kulzzy Radio PNG icons generated.")
print("SUCCESS: Adaptive icon configuration removed.")
print("SUCCESS: Android launcher manifest configured.")
