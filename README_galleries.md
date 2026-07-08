# Auto galleries — πώς προσθέτω φωτογραφίες

## Ροή (κάθε deploy)
1. Ρίξε τις εικόνες στο `assets/<series>/`
   (series: circleofashes, unfaced, penumbra, faced, saltwatercolors, muse)
2. (Προαιρετικά) φτιάξε/ενημέρωσε `assets/<series>/captions.json` για λεζάντες & σειρά
3. `git add . && git commit -m "..." && git push`
4. Το Cloudflare Pages τρέχει το build → οι galleries γεμίζουν μόνες τους.

## captions.json (προαιρετικό, ανά series)
```json
{
  "_order": ["πρώτη.jpg", "δεύτερη.jpg"],
  "πρώτη.jpg": "Λεζάντα πρώτης",
  "δεύτερη.jpg": "Λεζάντα δεύτερης"
}
```
- `_order`: ακριβής σειρά. Ό,τι λείπει → μετά, αλφαβητικά.
- Χωρίς caption → η φωτό μπαίνει χωρίς λεζάντα.
- Χωρίς captions.json → όλες αλφαβητικά, χωρίς λεζάντες.

## Cloudflare Pages settings
- Build command:       `python tools/build_galleries.py`
- Build output dir:    `/`  (το root)
- Δεν χρειάζεται τίποτα άλλο — μηδέν dependencies (μόνο stdlib).

## Τοπικό preview
```
python tools/build_galleries.py
python -m http.server 8000   →  http://localhost:8000
```
