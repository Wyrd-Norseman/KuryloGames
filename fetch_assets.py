#!/usr/bin/env python3
"""
Copy every image (and your CV) the site uses off Squarespace and into this folder,
then switch the site to load them locally.

Run this BEFORE you cancel Squarespace or move your domain:

    Windows:      py fetch_assets.py
    Mac / Linux:  python3 fetch_assets.py

For much smaller, faster-loading images, install Pillow first:

    Windows:      py -m pip install pillow
    Mac / Linux:  python3 -m pip install pillow

With Pillow, screenshots are saved as compressed JPEGs (roughly a tenth of the size of
the PNGs). Without it, they're saved as-is. Safe to run again: finished files are skipped.
"""
import io
import json
import pathlib
import re
import sys
import time
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
INDEX = ROOT / "index.html"
WIDTH = 1600        # px; sharp on large screens without being huge
JPEG_QUALITY = 82

try:
    from PIL import Image
except ImportError:
    Image = None

BLOCK = re.compile(r'(<script id="site-data" type="application/json">)(.*?)(</script>)', re.S)


def collect_keys(data):
    keys = []

    def add(item):
        k = item if isinstance(item, str) else item.get("k")
        if k and k not in keys:
            keys.append(k)

    p = data["person"]
    add(p["heroImage"]); add(p["portrait"])
    for proj in data["projects"]:
        for f in ("hero", "thumb", "logo"):
            if proj.get(f):
                add(proj[f])
        for ch in proj.get("chapters", []):
            for g in ch.get("figs", []):
                for it in g["items"]:
                    add(it)
        for it in proj.get("gallery", []):
            add(it)
    return keys


def is_own_file(key):
    return key.startswith(("images/", "videos/", "./", "/"))


def remote_url(key, base):
    if key.startswith("http"):
        return key.replace("http:", "https:", 1)
    return base + key


def raw_rel_path(key):
    if key.startswith("http"):
        parts = [p for p in urllib.parse.urlparse(key).path.split("/") if p]
        return "images/" + "/".join(parts[-2:])
    return "images/" + key


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (portfolio asset copy)"})
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.read()


def save_image(data, rel):
    """Save bytes; with Pillow, re-encode opaque images as JPEG. Returns the path used."""
    if Image is not None:
        try:
            im = Image.open(io.BytesIO(data))
            has_alpha = im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info)
            if has_alpha and im.convert("RGBA").getextrema()[3][0] < 255:
                pass  # genuinely transparent (e.g. a logo): keep the original file
            else:
                rel = str(pathlib.PurePosixPath(rel).with_suffix(".jpg"))
                dest = ROOT / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                im.convert("RGB").save(dest, "JPEG", quality=JPEG_QUALITY, optimize=True, progressive=True)
                return rel
        except Exception:
            pass  # fall back to the original bytes
    dest = ROOT / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(data)
    return rel


def main():
    html = INDEX.read_text(encoding="utf-8")
    m = BLOCK.search(html)
    if not m:
        sys.exit("Couldn't find the site-data block in index.html")
    data = json.loads(m.group(2))
    s = data["settings"]
    local = s.get("local", {})
    keys = [k for k in collect_keys(data) if not is_own_file(k)]

    if Image is None:
        print("Pillow isn't installed, so images will be saved full-size.")
        print("For smaller images: py -m pip install pillow  (then run this again)\n")

    failed = []
    for i, k in enumerate(keys, 1):
        done = local.get(k)
        if done and (ROOT / done).exists() and (Image is None or done.endswith(".jpg") or not done.endswith(".png")):
            print(f"[{i}/{len(keys)}] have   {done}")
            continue
        try:
            rel = save_image(fetch(remote_url(k, s["cdnBase"]) + f"?format={WIDTH}w"), raw_rel_path(k))
            local[k] = rel
            print(f"[{i}/{len(keys)}] saved  {rel}")
            time.sleep(0.15)
        except Exception as e:
            failed.append((k, str(e)))
            print(f"[{i}/{len(keys)}] FAILED {k}: {e}")

    cv_dest = ROOT / s["cv"]["local"]
    if not cv_dest.exists():
        try:
            cv_dest.write_bytes(fetch(s["cv"]["cdn"]))
            print(f"saved  {cv_dest.name}")
        except Exception as e:
            failed.append(("CV", str(e)))
            print(f"FAILED CV: {e}  (copy your CV PDF into this folder as {cv_dest.name})")

    s["local"] = local
    if not failed:
        s["assets"] = "local"
    block = "\n" + json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    html = html[:m.start(2)] + block + html[m.end(2):]
    INDEX.write_text(html, encoding="utf-8")

    if failed:
        print(f"\n{len(failed)} file(s) failed. The site is still set to load from Squarespace.")
        print("Run this again to retry; files already saved are skipped.")
        sys.exit(1)
    total = sum((ROOT / p).stat().st_size for p in local.values() if (ROOT / p).exists())
    print(f"\nDone: {len(keys)} images ({total / 1e6:.0f} MB) and your CV are in this folder,")
    print("and the site now loads them locally.")


if __name__ == "__main__":
    main()
