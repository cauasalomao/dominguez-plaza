"""
Gera versoes otimizadas das fotos referenciadas em galeria/index.html.

Saida:
  Fotos/_web/thumb/<categoria>/<nome>.jpg   max 700px lado maior, q82
  Fotos/_web/medium/<categoria>/<nome>.jpg  max 1600px lado maior, q85

Idempotente: se ja existe e for mais novo que o original, pula.
"""
import os
import re
import sys
from pathlib import Path
from PIL import Image, ImageOps

ROOT = Path(__file__).parent
GAL_HTML = ROOT / "galeria" / "index.html"
OUT_THUMB = ROOT / "Fotos" / "_web" / "thumb"
OUT_MEDIUM = ROOT / "Fotos" / "_web" / "medium"

THUMB_MAX = 700
MEDIUM_MAX = 1600
THUMB_Q = 82
MEDIUM_Q = 85


def parse_gallery():
    """Extract list of (src, alt, cat) tuples from galeria/index.html."""
    html = GAL_HTML.read_text(encoding="utf-8")
    m = re.search(r"const GALLERY = \[(.*?)\];", html, re.DOTALL)
    if not m:
        sys.exit("GALLERY array not found in galeria/index.html")
    body = m.group(1)
    items = re.findall(r'\["([^"]+)",\s*"([^"]+)",\s*"([^"]+)"\]', body)
    if not items:
        sys.exit("No items parsed from GALLERY")
    return items


def resize_save(src_path: Path, dst_path: Path, max_side: int, quality: int) -> bool:
    """Resize src to max_side and save as JPEG. Returns True if written."""
    if dst_path.exists() and dst_path.stat().st_mtime >= src_path.stat().st_mtime:
        return False
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(src_path) as im:
        im = ImageOps.exif_transpose(im)
        if im.mode in ("RGBA", "LA", "P"):
            bg = Image.new("RGB", im.size, (255, 255, 255))
            if im.mode == "P":
                im = im.convert("RGBA")
            bg.paste(im, mask=im.split()[-1] if "A" in im.mode else None)
            im = bg
        elif im.mode != "RGB":
            im = im.convert("RGB")
        w, h = im.size
        if max(w, h) > max_side:
            if w >= h:
                new_w = max_side
                new_h = round(h * max_side / w)
            else:
                new_h = max_side
                new_w = round(w * max_side / h)
            im = im.resize((new_w, new_h), Image.LANCZOS)
        im.save(dst_path, "JPEG", quality=quality, optimize=True, progressive=True)
    return True


def main():
    items = parse_gallery()
    print(f"Parsed {len(items)} items from gallery")
    written = skipped = missing = 0
    total_thumb_bytes = total_medium_bytes = 0
    for rel_src, _alt, cat in items:
        # rel_src is like "../Fotos/areas-comuns/areas-comuns_0001.JPG"
        src = (ROOT / rel_src.lstrip("./")).resolve() if rel_src.startswith("../") else (ROOT / rel_src).resolve()
        # easier: strip the leading "../"
        src = (GAL_HTML.parent / rel_src).resolve()
        if not src.exists():
            print(f"  MISSING: {src}")
            missing += 1
            continue
        stem = src.stem
        thumb_dst = OUT_THUMB / cat / f"{stem}.jpg"
        medium_dst = OUT_MEDIUM / cat / f"{stem}.jpg"
        try:
            t_written = resize_save(src, thumb_dst, THUMB_MAX, THUMB_Q)
            m_written = resize_save(src, medium_dst, MEDIUM_MAX, MEDIUM_Q)
        except Exception as e:
            print(f"  ERROR {src.name}: {e}")
            continue
        if t_written or m_written:
            written += 1
        else:
            skipped += 1
        total_thumb_bytes += thumb_dst.stat().st_size
        total_medium_bytes += medium_dst.stat().st_size
    print(f"Done. written={written} skipped={skipped} missing={missing}")
    print(f"Total thumbs:  {total_thumb_bytes/1024/1024:.1f} MB")
    print(f"Total mediums: {total_medium_bytes/1024/1024:.1f} MB")


if __name__ == "__main__":
    main()
