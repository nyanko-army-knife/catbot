import sys
from pathlib import Path
from PIL import Image

src = Path("./data/img/Unit")
dst = src.with_name(src.name)
dst.mkdir(exist_ok=True)

for f in src.iterdir():
    if f.suffix.lower() not in {".png"}:
        continue
    img = Image.open(f).convert("RGBA")
    w, h = img.size
    if w >= 128 or h >= 128:
        print(f"Skipping {f.name}: too large")
        continue
    canvas = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    canvas.paste(img, ((128 - w) // 2, (128 - h) // 2), img)
    canvas.save(dst / f"{f.stem}.png")
