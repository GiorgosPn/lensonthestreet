#!/usr/bin/env python3
"""
build_galleries.py — τρέχει σε ΚΑΘΕ deploy (Cloudflare Pages build command).

Καμία ρύθμιση, κανένα JSON. Ο ΤΙΤΛΟΣ κάθε φωτό βγαίνει από το ΟΝΟΜΑ του αρχείου:

    circle_of_ashes.jpg  ->  "Circle Of Ashes"
    ashes.jpg            ->  "Ashes"
    saltwater-colors.png ->  "Saltwater Colors"

Κανόνες ονομάτων:
  • _ και - και κενά  ->  διαχωριστικά λέξεων
  • κάθε λέξη ξεκινά με κεφαλαίο
  • προαιρετικό αριθμητικό prefix για σειρά ("01_", "02-", "3 ") κόβεται από
    τον τίτλο αλλά καθορίζει τη σειρά:  01_ashes.jpg -> "Ashes" (μπαίνει 1η)
  • χωρίς prefix -> αλφαβητική σειρά

Φάκελοι:
  assets/<series>/   -> gallery της αντίστοιχης portfolio/<series>.html
  assets/archive/    -> το "Archive" (contact sheet) στην αρχική
  assets/strip/      -> το negative strip ("Selected frames"), auto FR 01, FR 02...

Ρίχνεις εικόνες -> commit -> push. Το Cloudflare τρέχει αυτό στο build.

Cloudflare Pages:  Build command = python tools/build_galleries.py
                   Build output directory = /
"""
import pathlib
import re
import html as htmllib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

PROJECTS = ["circleofashes", "unfaced", "penumbra", "faced", "saltwatercolors", "muse"]
IMG_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif",
            ".JPG", ".JPEG", ".PNG", ".WEBP"}


# ── filename → title / σειρά ────────────────────────────────────────────────
CAMERA_PREFIXES = {"dsc", "img", "dscf", "dscn", "pict", "gopr", "pano",
                   "mvi", "vid", "photo", "image", "screenshot", "dji", "r"}


def sort_key(name):
    """Αριθμητικό prefix -> αριθμητική σειρά· αλλιώς αλφαβητικά (case-insensitive)."""
    m = re.match(r'^(\d+)\s*[-_ ]', name)
    if m:
        return (0, int(m.group(1)), name.lower())
    return (1, 0, name.lower())


def _is_camera_code(stem):
    """True αν το όνομα μοιάζει με camera/phone code (π.χ. _DSC9274, IMG_4016, UUID)."""
    s = re.sub(r'^\d+\s*[-_ ]\s*', "", stem)
    tokens = [t for t in re.split(r'[-_ ]+', s) if t]
    if not tokens:
        return True

    def tok_is_code(t):
        tl = t.lower()
        if tl in CAMERA_PREFIXES:
            return True
        if re.fullmatch(r'[A-Za-z]{0,5}\d{3,}[A-Za-z]?', t):   # IMG4016, DSC7342, R0000603
            return True
        if re.fullmatch(r'[0-9A-Fa-f]{4,}', t) and re.search(r'\d', t):  # hex UUID chunk
            return True
        if re.fullmatch(r'\d+', t):
            return True
        return False

    return all(tok_is_code(t) for t in tokens)


def title_from_filename(name):
    stem = name.rsplit(".", 1)[0]
    stem = re.sub(r'^\d+\s*[-_ ]\s*', "", stem)      # κόψε "01_", "2-", "3 "
    if _is_camera_code(name.rsplit(".", 1)[0]):      # camera code -> χωρίς τίτλο
        return ""
    words = re.split(r'[-_ ]+', stem)
    return " ".join(w[:1].upper() + w[1:] if w else "" for w in words).strip()


def list_dir(folder):
    """Ordered [(filename, title)] για έναν φάκελο μέσα στο assets/."""
    d = ASSETS / folder
    if not d.is_dir():
        return []
    files = [p.name for p in d.iterdir() if p.is_file() and p.suffix in IMG_EXTS]
    files.sort(key=sort_key)
    return [(f, title_from_filename(f)) for f in files]


# ── HTML builders ───────────────────────────────────────────────────────────
def figures_gallery(series, items):
    out = []
    for name, title in items:
        t = htmllib.escape(title, quote=True)
        out.append(
            '        <figure class="p-item reveal">\n'
            f'          <img src="../assets/{series}/{name}" alt="{t}" loading="lazy">\n'
            f'          <figcaption>{htmllib.escape(title)}</figcaption>\n'
            '        </figure>'
        )
    return "\n".join(out)


def figures_archive(items):
    out = []
    for name, title in items:
        t = htmllib.escape(title, quote=True)
        out.append(
            '        <figure class="a-item reveal">'
            f'<img src="assets/archive/{name}" alt="{t}" loading="lazy">'
            f'<figcaption>{htmllib.escape(title)}</figcaption></figure>'
        )
    return "\n".join(out)


def figures_strip(items):
    out = []
    for i, (name, title) in enumerate(items, start=1):
        t = htmllib.escape(title, quote=True)
        out.append(
            '          <figure class="frame">\n'
            f'            <img src="assets/strip/{name}" alt="{t}" loading="lazy">\n'
            f'            <figcaption><span class="mono fr-no">FR {i:02d}</span>'
            f'<span class="fr-title">{htmllib.escape(title)}</span></figcaption>\n'
            '          </figure>'
        )
    return "\n".join(out)


def replace_between(text, start, end, body_html, indent):
    if start not in text or end not in text:
        return text, False
    pre, rest = text.split(start, 1)
    _, post = rest.split(end, 1)
    body = f"\n{body_html}\n{indent}" if body_html else f"\n{indent}"
    return pre + start + body + end + post, True


def update_counter(text, series, n):
    label = f"{n:02d} frames" if n else "series"
    return re.sub(rf'(data-count="{series}"[^>]*>)[^<]*',
                  lambda m: m.group(1) + label, text)


def update_cover_preview(text, series, first_src):
    if first_src:
        text = re.sub(rf'(data-slug="{series}" data-preview=")[^"]*',
                      lambda m: m.group(1) + first_src, text)
        text = re.sub(rf'(data-cover="{series}"[^>]*\ssrc=")[^"]*',
                      lambda m: m.group(1) + first_src, text)
    return text


# ── main ────────────────────────────────────────────────────────────────────
def main():
    counts, first_frame = {}, {}

    # 1 — galleries ανά series
    for series in PROJECTS:
        items = list_dir(series)
        counts[series] = len(items)
        if items:
            first_frame[series] = f"assets/{series}/{items[0][0]}"
        page = ROOT / "portfolio" / f"{series}.html"
        if not page.exists():
            print(f"  -- λείπει portfolio/{series}.html, skip")
            continue
        text = page.read_text(encoding="utf-8")
        text, ok = replace_between(text, f"<!-- GALLERY:START:{series} -->",
                                   f"<!-- GALLERY:END:{series} -->",
                                   figures_gallery(series, items), "        ")
        text = update_counter(text, series, len(items))
        page.write_text(text, encoding="utf-8")
        print(f"{series:16s} {len(items):2d} frames  [{'✓' if ok else 'no markers'}]")

    # 2 — counters/covers/previews σε index.html & portfolio.html
    for page_name in ("index.html", "portfolio.html"):
        pf = ROOT / page_name
        if not pf.exists():
            continue
        text = pf.read_text(encoding="utf-8")
        for series in PROJECTS:
            text = update_counter(text, series, counts.get(series, 0))
            if series in first_frame:
                text = update_cover_preview(text, series, first_frame[series])
        pf.write_text(text, encoding="utf-8")
        print(f"updated counters/covers/previews -> {page_name}")

    # 3 — Archive + Strip στο index.html
    idx = ROOT / "index.html"
    if idx.exists():
        text = idx.read_text(encoding="utf-8")
        arch = list_dir("archive")
        strip = list_dir("strip")
        text, aok = replace_between(text, "<!-- ARCHIVE:START -->", "<!-- ARCHIVE:END -->",
                                    figures_archive(arch), "        ")
        text, sok = replace_between(text, "<!-- STRIP:START -->", "<!-- STRIP:END -->",
                                    figures_strip(strip), "          ")

        # 4 — hero + og:image από assets/hero/ (πρώτη εικόνα)
        hero = list_dir("hero")
        if hero:
            src = f"assets/hero/{hero[0][0]}"
            alt = hero[0][1] or "Giorgos Panagou — photograph"
            # hero <figure class="hero-image"><img ...>
            text = re.sub(r'(<figure class="hero-image reveal">\s*<img src=")[^"]*"[^>]*alt="[^"]*"',
                          lambda m: f'{m.group(1)}{src}" alt="{htmllib.escape(alt, quote=True)}"',
                          text, count=1)
            # og:image
            text = re.sub(r'(<meta property="og:image" content=")[^"]*"',
                          lambda m: f'{m.group(1)}https://www.lensonthestreet.com/{src}"',
                          text, count=1)

        idx.write_text(text, encoding="utf-8")
        print(f"archive: {len(arch):2d} frames  [{'✓' if aok else 'no markers'}]")
        print(f"strip:   {len(strip):2d} frames  [{'✓' if sok else 'no markers'}]")
        if hero:
            print(f"hero:    {hero[0][0]} -> hero + og:image")
        else:
            print("hero:     (κενό assets/hero/ — αμετάβλητο)")

    total = sum(counts.values())
    print(f"\nΈτοιμο. {total} καρέ σε {len([c for c in counts.values() if c])} series.")


if __name__ == "__main__":
    main()