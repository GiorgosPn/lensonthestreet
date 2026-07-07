#!/usr/bin/env python3
"""
fetch_assets.py — τρέξε το ΤΟΠΙΚΑ, όσο το lensonthestreet.com είναι live.

1. Σκανάρει τις live σελίδες σου (home, about, prints, portfolio + 6 series)
   και μαζεύει όλα τα image URLs (images.squarespace-cdn.com) + captions/alt.
2. Κατεβάζει τα originals σε assets/img/<page>/ (κάνει skip όσα υπάρχουν ήδη —
   αν έχεις ήδη τρέξει την προηγούμενη έκδοση, τα αρχεία επαναχρησιμοποιούνται).
3. Ξαναγράφει κάθε CDN URL στα τοπικά .html σε τοπικό path.
4. Γεμίζει τα κενά galleries (unfaced, penumbra, faced, saltwatercolors, muse)
   ανάμεσα στα GALLERY:START/END markers, με captions.
5. Ενημερώνει τα "NN frames" counters, τα covers (data-cover) και τα
   previews των series (data-preview) με το πρώτο καρέ κάθε series.

Χρήση (από το root του project):
  pip install requests beautifulsoup4
  python tools/fetch_assets.py

Τρέξε το ΠΡΙΝ την ακύρωση του Squarespace — μετά, τα CDN links πεθαίνουν.
"""
import re
import sys
import pathlib
import urllib.parse

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    sys.exit("pip install requests beautifulsoup4")

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = "https://www.lensonthestreet.com"
CDN_RE = re.compile(r"https://images\.squarespace-cdn\.com/[^\s\"')]+")
PROJECTS = ["circleofashes", "unfaced", "penumbra", "faced", "saltwatercolors", "muse"]
PAGES = {"home": "/", "about": "/about", "prints": "/prints", "portfolio": "/portfolio",
         **{s: f"/portfolio/{s}" for s in PROJECTS}}
HEADERS = {"User-Agent": "Mozilla/5.0 (site-owner archive script)"}


def clean_url(url):
    return url.split("?")[0] + "?format=2500w"


def fname(url):
    path = urllib.parse.urlparse(url).path
    name = urllib.parse.unquote(path.rsplit("/", 1)[-1])
    return re.sub(r"[^A-Za-z0-9._-]+", "_", name)


def scrape(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    out, seen = [], set()
    for img in soup.find_all("img"):
        src = img.get("data-src") or img.get("src") or ""
        if src.startswith("//"):
            src = "https:" + src
        if "squarespace-cdn.com" not in src:
            continue
        src = clean_url(src)
        if src in seen:
            continue
        seen.add(src)
        cap = ""
        fig = img.find_parent("figure")
        if fig and fig.find("figcaption"):
            cap = fig.find("figcaption").get_text(strip=True)
        out.append((src, cap or (img.get("alt") or "").strip()))
    return out


def download(url, dest):
    if dest.exists():
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    r = requests.get(url, headers=HEADERS, timeout=60)
    r.raise_for_status()
    dest.write_bytes(r.content)
    print(f"  ↓ {dest.relative_to(ROOT)} ({len(r.content)//1024} KB)")


def main():
    url_map, page_images = {}, {}
    for key, path in PAGES.items():
        full = SITE + path
        print(f"scraping {full}")
        try:
            imgs = scrape(full)
        except Exception as exc:
            print(f"  !! failed: {exc}")
            continue
        page_images[key] = []
        for src, cap in imgs:
            local = ROOT / "assets" / "img" / key / fname(src)
            download(src, local)
            rel = f"assets/img/{key}/{local.name}"
            url_map[src.split("?")[0]] = rel
            page_images[key].append((rel, cap))

    # 3 — rewrite CDN urls -> local paths σε όλα τα html
    html_files = list(ROOT.glob("*.html")) + list((ROOT / "portfolio").glob("*.html"))
    for hf in html_files:
        text = hf.read_text(encoding="utf-8")
        prefix = "../" if hf.parent.name == "portfolio" else ""

        def repl(m):
            local = url_map.get(m.group(0).split("?")[0])
            return prefix + local if local else m.group(0)

        new = CDN_RE.sub(repl, text)
        if new != text:
            hf.write_text(new, encoding="utf-8")
            print(f"rewrote {hf.relative_to(ROOT)}")

    # 4+5 — galleries, counters, covers, previews
    for slug in PROJECTS:
        imgs = page_images.get(slug) or []
        if not imgs:
            continue
        hf = ROOT / "portfolio" / f"{slug}.html"
        if hf.exists():
            text = hf.read_text(encoding="utf-8")
            start, end = f"<!-- GALLERY:START:{slug} -->", f"<!-- GALLERY:END:{slug} -->"
            if start in text and "fetch_assets.py" in text.split(start)[1].split(end)[0]:
                figs = "\n".join(f'''        <figure class="p-item reveal">
          <img src="../{rel}" alt="{cap}" loading="lazy">
          <figcaption>{cap}</figcaption>
        </figure>''' for rel, cap in imgs)
                text = text.split(start)[0] + start + "\n" + figs + "\n        " + end + text.split(end)[1]
            text = re.sub(rf'(data-count="{slug}"[^>]*>)[^<]*', rf"\g<1>{len(imgs):02d} frames", text)
            hf.write_text(text, encoding="utf-8")
            print(f"filled gallery: portfolio/{slug}.html ({len(imgs)} frames)")

    for page_name in ("index.html", "portfolio.html"):
        pf = ROOT / page_name
        if not pf.exists():
            continue
        text = pf.read_text(encoding="utf-8")
        for slug in PROJECTS:
            imgs = page_images.get(slug) or []
            if not imgs:
                continue
            first = imgs[0][0]
            text = re.sub(rf'(data-slug="{slug}" data-preview=")[^"]*', rf"\g<1>{first}", text)
            text = re.sub(rf'(data-cover="{slug}" src=")[^"]*', rf"\g<1>{first}", text)
            text = re.sub(rf'(data-count="{slug}"[^>]*>)[^<]*', rf"\g<1>{len(imgs):02d} frames", text)
        pf.write_text(text, encoding="utf-8")
        print(f"updated previews/covers/counters in {page_name}")

    print("\nΈτοιμο. Έλεγχος:  python -m http.server 8000  →  http://localhost:8000")


if __name__ == "__main__":
    main()
