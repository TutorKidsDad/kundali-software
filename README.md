# Kundli Explorer

A browser-only, bilingual (Hindi/English) North Indian Vedic Kundli interface prototype intended for GitHub Pages.

## Important status
This first version is a **UI prototype, not a working astronomical calculator**. The displayed planetary placements are illustrative sample data. Birth details only update the preview caption; they do not change the sample chart. Do not use this version for actual astrological analysis.

## Run locally
From this folder, run:

```bash
python3 -m http.server 8000
```

Then open http://localhost:8000 in your browser.

## Publish on GitHub Pages
1. Create a repository such as `kundli-software`.
2. Upload the contents of this folder to the repository root (so `index.html` is at the root).
3. Open **Settings → Pages**.
4. Choose **Deploy from a branch**, select `main` and `/(root)`, then save.
5. Open the URL shown by GitHub Pages.

## Planned calculation implementation
1. Select a browser-compatible astronomical engine and review its licence before bundling it.
2. Define calculation settings: sidereal zodiac, Lahiri ayanamsha, mean/true node, location coordinates and historical time zone.
3. Implement and test planetary longitude, ascendant, sign, nakshatra and pada.
4. Add D1 and D9; then dignity, aspects, yogas and Vimshottari dasha.
5. Compare known birth cases against a trusted reference program and record tolerances.

## Privacy
The prototype does not transmit entered birth details. If a geocoding service is added later, its privacy implications and data handling must be documented. Do not commit real users' birth details to the repository.

## Licence
Add a project licence after deciding how you want the source and any bundled calculation libraries to be distributed. A calculation engine may have a separate licence from this interface.
