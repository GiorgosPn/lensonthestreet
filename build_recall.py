#!/usr/bin/env python3
"""
build_recall.py — Ενημερώνει αυτόματα τη σελίδα recall.

ΧΡΗΣΗ:
  1. Ρίξε όσες φωτό θες στον φάκελο  assets/recall/       (δικές σου)
  2. Ρίξε references στον φάκελο       assets/recall-refs/  (άλλων)
  3. Τρέξε:  python3 build_recall.py
  4. git add . && git commit -m "update recall" && git push

Τι κάνει:
  - Βρίσκει ΟΛΕΣ τις εικόνες στους δύο φακέλους
  - Τις βελτιστοποιεί (max 1600px, quality 84) ώστε να φορτώνουν γρήγορα
  - Ξαναγράφει το κομμάτι gallery στο portfolio/recall.html
  - Βάζει credit αν το όνομα αρχείου περιέχει: watson / roversi / lindbergh
    (π.χ.  watson-portrait.jpg  ->  "Albert Watson")
    αλλιώς βάζει "Reference"

Οι δικές σου (assets/recall/) μπαίνουν ΠΡΩΤΕΣ ως "Recall · 01, 02...".
Απαιτεί ImageMagick (convert). Αν λείπει, τρέξε: sudo apt install imagemagick
"""

import os, re, subprocess, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
OWN_DIR  = os.path.join(ROOT, "assets", "recall")
REF_DIR  = os.path.join(ROOT, "assets", "recall-refs")
HTML     = os.path.join(ROOT, "portfolio", "recall.html")
EXTS = (".jpg", ".jpeg", ".png", ".webp")

def optimize(path):
    """Resize to max 1600px, strip metadata, quality 84 (in place)."""
    tmp = path + ".tmp.jpg"
    try:
        subprocess.run(
            ["convert", path, "-auto-orient", "-resize", "1600x1600>",
             "-strip", "-quality", "84", tmp],
            check=True, capture_output=True)
        os.replace(tmp, path)
    except Exception as e:
        if os.path.exists(tmp): os.remove(tmp)
        print(f"  ! δεν βελτιστοποιήθηκε: {os.path.basename(path)} ({e})")

def credit(fn):
    l = fn.lower()
    if "watson" in l:    return "Albert Watson"
    if "roversi" in l:   return "Paolo Roversi"
    if "lindbergh" in l: return "Peter Lindbergh"
    return None

def images_in(d):
    if not os.path.isdir(d): return []
    return sorted(f for f in os.listdir(d)
                  if f.lower().endswith(EXTS) and not f.startswith("."))

def main():
    own  = images_in(OWN_DIR)
    refs = images_in(REF_DIR)
    print(f"Βρέθηκαν {len(own)} δικές σου + {len(refs)} references.")

    print("Βελτιστοποίηση...")
    for f in own:  optimize(os.path.join(OWN_DIR, f))
    for f in refs: optimize(os.path.join(REF_DIR, f))

    # own block (numbered)
    own_html = ""
    for i, f in enumerate(own, 1):
        own_html += f'''      <figure class="p-item reveal">
        <img src="../assets/recall/{f}" alt="Recall, plate {i:02d}, portrait by Giorgos Panagou" loading="lazy">
        <figcaption><span class="cap-index">Recall &middot; {i:02d}</span></figcaption>
      </figure>
'''

    # refs: known credits grouped first, then unknown
    known = [(f, credit(f)) for f in refs if credit(f)]
    unknown = [(f, None) for f in refs if not credit(f)]
    known.sort(key=lambda x: (x[1], x[0]))
    ordered = known + unknown

    ref_html = ""
    for f, c in ordered:
        cap = c if c else "Reference"
        alt = f"Reference image by {c}" if c else "Reference image"
        ref_html += f'''      <figure class="p-item reveal">
        <img src="../assets/recall-refs/{f}" alt="{alt}" loading="lazy">
        <figcaption><span class="cap-index">{cap}</span></figcaption>
      </figure>
'''

    block = f'''    <div class="project-gallery grid-3">
      <!-- GALLERY:START:recall -->
{own_html}      <!-- GALLERY:END:recall -->
    </div>

    <section class="page-hero" style="padding-top:0">
      <span class="mono dim eyebrow-rule reveal">Visual references</span>
      <p class="project-intro reveal">The images below are not my work. They are references that set the mood and lighting I'm after, credited to their photographer where known.</p>
    </section>

    <div class="project-gallery grid-3">
{ref_html}    </div>'''

    html = open(HTML, encoding="utf-8").read()
    # remove old own-gallery
    html = re.sub(
        r'    <div class="project-gallery grid-3">\s*<!-- GALLERY:START:recall -->.*?<!-- GALLERY:END:recall -->\s*</div>',
        "___GP___", html, count=1, flags=re.DOTALL)
    # remove old refs section+grid
    html = re.sub(
        r'\s*<section class="page-hero"[^>]*>\s*<span class="mono dim eyebrow-rule reveal">Visual references</span>.*?</section>\s*<div class="project-gallery grid-3">.*?</div>',
        "", html, flags=re.DOTALL)
    if "___GP___" not in html:
        print("! ΣΦΑΛΜΑ: δεν βρέθηκε το gallery block στο recall.html. Δεν έγινε αλλαγή.")
        sys.exit(1)
    html = html.replace("___GP___", block)
    open(HTML, "w", encoding="utf-8").write(html)

    print(f"\n✓ Ενημερώθηκε το recall.html: {len(own)} δικές σου + {len(refs)} references.")
    print("  Τώρα: git add . && git commit -m 'update recall' && git push")

if __name__ == "__main__":
    main()
