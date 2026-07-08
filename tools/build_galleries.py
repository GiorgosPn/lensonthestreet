#!/usr/bin/env python3
"""
build_galleries.py — τρέχει σε ΚΑΘΕ deploy (Cloudflare Pages build command).

Τι κάνει:
  1. Για κάθε series, σκανάρει το assets/<series>/ για εικόνες.
  2. Ξαναγράφει τα <figure> blocks ανάμεσα στα GALLERY:START/END markers
     της αντίστοιχης portfolio/<series>.html.
  3. Ενημερώνει counters ("NN frames"), covers (data-cover) και
     previews (data-preview) σε index.html + portfolio.html με το 1ο καρέ.

Captions & σειρά — τα ελέγχεις ΕΣΥ, μέσω ενός προαιρετικού
assets/<series>/captions.json:

  {
    "_order": ["R0000603.jpg", "_DSC7328.jpeg", "1.jpg"],
    "R0000603.jpg": "Ο τίτλος της φωτογραφίας",
    "_DSC7328.jpeg": "Άλλος τίτλος"
  }

  - "_order" (προαιρετικό): η ακριβής σειρά εμφάνισης. Ό,τι δεν αναφέρεται
    εκεί μπαίνει μετά, αλφαβητικά. Αν λείπει εντελώς, όλα αλφαβητικά.
  - Τα υπόλοιπα κλειδιά: filename -> caption. Ό,τι δεν έχει caption
    εμφανίζεται χωρίς λεζάντα (κενό figcaption).

Ρίχνεις εικόνες στο folder -> commit -> push. Το Cloudflare τρέχει αυτό
το script στο build και το site ενημερώνεται. Μηδέν άγγιγμα HTML.

Build command στο Cloudflare Pages:  python tools/build_galleries.py
(Build output directory:  /   — δηλαδή το root)
"""
import json
import pathlib
import re
import html as htmllib

ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

# Σειρά = σειρά εμφάνισης / αρίθμηση (I, II, ...). Κράτα την ίδια με το site.
PROJECTS = ["circleofashes", "unfaced", "penumbra", "faced", "saltwatercolors", "muse"]

IMG_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif", ".JPG", ".JPEG", ".PNG"}


def load_captions(series_dir):
    """Επιστρέφει (order_list, caption_map) από captions.json αν υπάρχει."""
    cfile = series_dir / "captions.json"
    if not cfile.exists():
        return [], {}
    try:
        data = json.loads(cfile.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"  !! {cfile.name}: άκυρο JSON ({exc}) — αγνοείται")
        return [], {}
    order = data.pop("_order", []) or []
    # ό,τι απομένει = filename -> caption
    caption_map = {k: (v or "") for k, v in data.items()}
    return order, caption_map


def list_images(series):
    """Λίστα ονομάτων εικόνων του series, με σειρά βάσει captions.json/_order."""
    series_dir = ASSETS / series
    if not series_dir.is_dir():
        return series_dir, [], {}
    files = [p.name for p in series_dir.iterdir()
             if p.is_file() and p.suffix in IMG_EXTS]
    order, caption_map = load_captions(series_dir)

    # ταξινόμηση: πρώτα ό,τι είναι στο _order (με τη σειρά του),
    # μετά τα υπόλοιπα αλφαβητικά (case-insensitive)
    in_order = [f for f in order if f in files]
    rest = sorted((f for f in files if f not in in_order), key=str.lower)
    ordered = in_order + rest
    return series_dir, ordered, caption_map


def build_figures(series, images, caption_map):
    parts = []
    for name in images:
        cap = caption_map.get(name, "")
        cap_attr = htmllib.escape(cap, quote=True)
        cap_html = htmllib.escape(cap)
        parts.append(
            '        <figure class="p-item reveal">\n'
            f'          <img src="../assets/{series}/{name}" alt="{cap_attr}" loading="lazy">\n'
            f'          <figcaption>{cap_html}</figcaption>\n'
            '        </figure>'
        )
    return "\n".join(parts)


def replace_gallery(text, series, figures_html):
    start = f"<!-- GALLERY:START:{series} -->"
    end = f"<!-- GALLERY:END:{series} -->"
    if start not in text or end not in text:
        return text, False
    pre, rest = text.split(start, 1)
    _, post = rest.split(end, 1)
    body = f"\n{figures_html}\n        " if figures_html else "\n        "
    return pre + start + body + end + post, True


def update_counter(text, series, n):
    # <... data-count="series" ...>ΟΤΙΔΗΠΟΤΕ</  ->  NN frames
    label = f"{n:02d} frames" if n else "series"
    return re.sub(
        rf'(data-count="{series}"[^>]*>)[^<]*',
        lambda m: m.group(1) + label,
        text,
    )


def update_cover_preview(text, series, first_src):
    if first_src:
        text = re.sub(rf'(data-slug="{series}" data-preview=")[^"]*',
                      lambda m: m.group(1) + first_src, text)
        text = re.sub(rf'(data-cover="{series}"[^>]*\ssrc=")[^"]*',
                      lambda m: m.group(1) + first_src, text)
    return text


def main():
    # 1+2 — galleries ανά series
    counts = {}
    first_frame = {}
    for series in PROJECTS:
        series_dir, images, caption_map = list_images(series)
        counts[series] = len(images)
        if images:
            # preview/cover path σχετικά με το ROOT (index/portfolio ζουν στο root)
            first_frame[series] = f"assets/{series}/{images[0]}"

        page = ROOT / "portfolio" / f"{series}.html"
        if not page.exists():
            print(f"  -- λείπει {page.relative_to(ROOT)}, skip")
            continue
        text = page.read_text(encoding="utf-8")
        figs = build_figures(series, images, caption_map)
        text, ok = replace_gallery(text, series, figs)
        text = update_counter(text, series, len(images))
        page.write_text(text, encoding="utf-8")
        status = "✓" if ok else "χωρίς markers"
        print(f"{series:16s} {len(images):2d} frames  [{status}]  portfolio/{series}.html")

    # 3 — counters + covers + previews σε index.html & portfolio.html
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

    total = sum(counts.values())
    print(f"\nΈτοιμο. Σύνολο {total} καρέ σε {len([c for c in counts.values() if c])} series.")


if __name__ == "__main__":
    main()
