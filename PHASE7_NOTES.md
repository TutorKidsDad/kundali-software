# Phase 7 incremental upgrade

## Implemented
- Complete JSON download of the `/api/chart` response.
- Backend-generated PDF with birth metadata, planetary positions, all supported divisional chart planet tables, all Vimshottari Mahadasha/Antardasha/Pratyantardasha periods, Graha Drishti, Yoga matches, BAV/SAV, and explicit partial Shadbala status.
- Removed the obsolete duplicate Ashtakavarga placeholder.
- Added the classical natural-strength (Naisargika Bala) constants only, clearly marked as partial.

## NOT implemented yet
- Full Shadbala: Sthana, Dig, Kala, Cheshta, and Drik Bala; no full totals or comparisons are claimed. These require detailed conventions, ephemeris inputs, and cross-validation.
- 
- Hindi font rendering in PDF: current PDF is English labels; website has bilingual section headings.

## Deploy
1. Back up the currently working repository.
2. Replace frontend and backend files with the contents of this ZIP, preserving folder structure. Do not upload `__pycache__` or `js/app.js_old`.
3. Commit to GitHub. If Render is not auto-deployed, manually deploy latest commit.
4. Confirm `/api/health`, calculate a test chart, download JSON, and download PDF. The PDF endpoint is POST `/api/report/pdf` with the same request JSON as `/api/chart`.
5. Compare results with your existing production version before public release.

## Phase 7 PDF update
- The PDF now draws a North Indian style chart for D1 and each supported divisional chart, followed by its planet table.
- Birth metadata now includes name, birthplace, date, time, timezone, latitude and longitude.
- JSON also includes these birth metadata fields in the chart API response.
- Planet names in PDF chart diagrams are abbreviated in English.
