# Kundli Explorer — Phase 5

Extends Phase 4 (Swiss Ephemeris, D1 and workbook-derived Varga charts, Vimshottari Dasha) with **real computed, transparent preliminary D1 analysis**:

- Classical whole-sign Graha Drishti for the seven visible Grahas (7th for all; Mars 4th/8th, Jupiter 5th/9th, Saturn 3rd/10th). Rahu/Ketu are excluded because schools differ.
- Selected basic sign/house yoga checks: own-sign, exaltation-sign, Pancha Mahapurusha, Gaja Kesari.
- Ashtakavarga and Shadbala are explicitly **not implemented**; do not treat the placeholders as computed results.

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m uvicorn backend:app --host 127.0.0.1 --port 8000 --reload
```

Open http://127.0.0.1:8000 and calculate a Kundli. The analysis appears below the Dasha panel. Health check: http://127.0.0.1:8000/api/health.

## Limitations

Preliminary rules are not comprehensive predictive yogas. Strength, combustion, cancellation, aspects with orbs, and multiple traditions are not modeled. Validate against reference charts before use in professional reports. Existing workbook-derived divisional mappings are carried forward without new independent validation. Review Swiss Ephemeris licensing before deployment.


## Phase 6 additions
- Classical unadjusted seven-graha BAV and SAV, total 337 bindus, with seven tables and a sign-by-sign SAV grid.
- Repositioned the twelve house labels to separate hotspots inside North Indian chart sectors; compact overflow handling.
- Fixed dasha UTC timestamp parsing (API timestamps lacked `Z`, so browsers incorrectly parsed them as local time), and preserved dropdown selection when re-rendering.
- Ashtakavarga source rule lists: https://vedicreader.com/j/learn/shadbala-ashtakavarga and https://mokshology.com/learn/ashtakavarga . Verify against a trusted reference chart before production use.
- Restart the backend and hard-refresh browser (Ctrl+Shift+R) to avoid cached JavaScript/CSS.
