# LENS ON THE STREET — static rebuild v2 (high design)

Πλήρης ανακατασκευή του site σε καθαρό static HTML/CSS/JS (δικός μας κώδικας,
zero dependencies, zero build step). Μοναδικό επαναλαμβανόμενο κόστος: το domain.

## Τι περιλαμβάνει η v2

- Animated wordmark στο load (letter-by-letter stagger)
- Parallax σε hero/full-bleed φωτογραφίες
- Staggered scroll reveals (IntersectionObserver)
- Header που κρύβεται στο scroll down, επιστρέφει στο scroll up
- Marquee strip κάτω από το hero
- Portfolio cards με index numbers, hover zoom, underline sweep
- Project pages με panel hero, mono intro, "NN photographs" counter,
  editorial gallery (full-width κάθε 3η, ζεύγη ενδιάμεσα), prev/next
- Lightbox: βέλη, πληκτρολόγιο (←/→/Esc), counter "04 / 12", captions
- Τεράστιο τυπογραφικό footer wordmark + meta γραμμή
- SEO: canonical, Open Graph, sitemap.xml, robots.txt, 404.html
- Accessibility: focus states, aria labels, prefers-reduced-motion

## Πού «τρέχει» το καθένα

| Κομμάτι | Πού τρέχει | Πότε |
|---|---|---|
| Το site (HTML/CSS/JS) | Στον browser του επισκέπτη — σερβίρεται ως στατικά αρχεία | Πάντα |
| `tools/fetch_assets.py` | Στο laptop σου (Python 3) | ΜΙΑ φορά, πριν την ακύρωση |
| Local preview | `python -m http.server` στο laptop σου | Όποτε θες |
| Hosting | GitHub Pages ή Cloudflare Pages (δωρεάν) | Μετά το push |

Δεν υπάρχει server-side κώδικας — τίποτα δεν χρειάζεται να «τρέχει» σε server.

## Βήμα 1 — Κατέβασμα φωτογραφιών (ΠΡΙΝ ακυρώσεις το Squarespace!)

Οι σελίδες τώρα δείχνουν στο `images.squarespace-cdn.com`. Μόλις λήξει η
συνδρομή, τα links πεθαίνουν. Στο laptop σου:

```bash
pip install requests beautifulsoup4
python tools/fetch_assets.py
```

Το script κατεβάζει τα originals σε `assets/img/`, ξαναγράφει όλα τα `src`
σε τοπικά paths, γεμίζει τα galleries των Unfaced / Penumbra / Faced /
Saltwater Colors / Muse (με captions), ενημερώνει τα photo counters και
βάζει covers στα project cards.

Έλεγχος:

```bash
python -m http.server 8000    # http://localhost:8000
```

## Βήμα 2 — Newsletter

Export τους subscribers από Squarespace (Marketing → Email lists → CSV),
μετά σύνδεσε τη φόρμα του footer:
- **Buttondown** (free ≤100): `action="https://buttondown.com/api/emails/embed-subscribe/USERNAME"`
- ή **MailerLite** (free ≤1.000).

## Βήμα 3 — Hosting (δωρεάν)

**GitHub Pages:**
```bash
git init && git add -A && git commit -m "lens on the street v2"
git remote add origin git@github.com:USERNAME/lensonthestreet.git
git push -u origin main
# GitHub → Settings → Pages → Deploy from branch → main / root
```
Custom domain: Settings → Pages → `www.lensonthestreet.com` + Enforce HTTPS.

**Ή Cloudflare Pages:** connect repo → deploy (καλύτερο CDN + analytics).

## Βήμα 4 — Domain & DNS

1. Μεταφορά domain από Squarespace σε Cloudflare Registrar (~10€/χρόνο):
   Squarespace → Domains → Transfer → auth code (θέλει έως ~5 μέρες).
2. DNS για GitHub Pages:
   - `CNAME  www → USERNAME.github.io`
   - apex A records: 185.199.108.153 / 109 / 110 / 111
3. Περίμενε ενεργό HTTPS.

## Βήμα 5 — Ακύρωση Squarespace, ΜΟΝΟ όταν:

- [ ] `fetch_assets.py` έτρεξε — όλα δουλεύουν με τοπικές εικόνες
- [ ] Subscribers CSV κατέβηκε και έγινε import στο νέο εργαλείο
- [ ] Domain μεταφέρθηκε, DNS δείχνει στο νέο hosting
- [ ] Το site σερβίρεται με HTTPS στο lensonthestreet.com

## Μετά (προαιρετικά)

- Contact form: Formspree / Web3Forms (free) αντί για mailto
- Analytics: Cloudflare Web Analytics ή GoatCounter (χωρίς cookies)
- Image optimization: `npx @squoosh/cli` ή `cwebp` για WebP εκδόσεις
- Google Search Console: υπέβαλε το sitemap.xml
