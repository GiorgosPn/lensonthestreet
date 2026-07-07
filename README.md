# LENS ON THE STREET — final edition (light + negative strip)

Το brand σου (λευκό, καθαρό, οι σελίδες σου) με την καρδιά του αρνητικού φιλμ:
σκούρα strip-μπάντα με διατρήσεις που «προχωράει» στο scroll, loader
«developing», reveals, lightbox-contact-sheet, νέο aperture logo.
Καθαρό HTML/CSS/JS — μηδέν dependencies, μηδέν build.

## Δομή
```
index.html                αρχική: hero, marquee, negative strip, series, archive
portfolio.html            οι 6 σειρές: λίστα + σταθερό preview + grid
portfolio/*.html          6 σελίδες series (Circle of Ashes πλήρης)
about / faqs / contact / prints / 404
assets/brand/             logo: mark.svg, logo-lockup.svg, favicon.svg
css/style.css · js/main.js
tools/fetch_assets.py     τοπικό script: εικόνες + galleries + covers
sitemap.xml · robots.txt
```

## Βήματα (με τη σειρά)
1. **Τώρα, όσο το Squarespace είναι live:**
   `pip install requests beautifulsoup4 && python tools/fetch_assets.py`
   → κατεβάζει ΟΛΕΣ τις φωτογραφίες (κάνει skip όσες έχεις ήδη από την
   προηγούμενη εκτέλεση), γεμίζει τα galleries των 5 series, διορθώνει
   counters, covers και previews με τα πραγματικά πρώτα καρέ.
2. Προεπισκόπηση: `python -m http.server 8000`
3. Newsletter: export subscribers CSV από Squarespace → Buttondown/MailerLite →
   βάλε το action στη φόρμα του footer (TODO comment).
4. Hosting: GitHub Pages ή Cloudflare Pages (δωρεάν). Push → Pages → main/root.
5. Domain: transfer από Squarespace σε Cloudflare Registrar (~10€/χρόνο),
   DNS: CNAME www → USERNAME.github.io + τα 4 A records του GitHub.
6. Ακύρωση Squarespace ΜΟΝΟ όταν: εικόνες τοπικά ✓ subscribers ✓ DNS ✓ HTTPS ✓

## Logo
`assets/brand/` — aperture iris (6 blades), σε 3 μορφές:
- `mark.svg` — σκέτο σήμα (currentColor, βάψ' το όπως θες)
- `logo-lockup.svg` — σήμα + wordmark + υπότιτλος (για export/print)
- `favicon.svg` — favicon (δηλωμένο ήδη σε όλες τις σελίδες)
