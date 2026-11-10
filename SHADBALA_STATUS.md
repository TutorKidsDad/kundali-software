# Kundli Explorer — Phase 7 Shadbala status (provisional completion)

The current build now returns all six Shadbala categories for the seven classical planets and exposes component-level diagnostics in the web interface, JSON response, and PDF report.

## Implemented in this build
- Sthana Bala: Uchcha, Saptavargaja, Ojhayugma-Rasi/Amsa, Kendradi and Drekkana. The existing project Saptavargaja point schedule is retained.
- Dig Bala: directional cusp method using Ascendant, Descendant, MC and IC when supplied by Swiss Ephemeris.
- Kala Bala: Natonnata, Paksha, Tribhaga, Abda, Masa, Vara, Hora, Ayana and Yuddha candidate handling.
- Cheshta Bala: Sun uses Ayana Bala; Moon uses Paksha Bala; Mars–Saturn use a speed/retrograde approximation.
- Naisargika Bala: standard fixed natural strengths.
- Drik Bala: benefic/malefic graha-aspect weighting with orb tapering.
- Totals in Virupas and Rupas, required minimums, ratio and threshold comparison when all components are available.
- Component details are included in the UI and PDF; the complete response remains in JSON.

## Conventions and limitations that remain explicit
- Saptavargaja retains the project schedule 45 / 30 / 22.5 / 15 / 7.5 / 3.75 / 1.875. BPHS editions and software conventions vary.
- Abda and Masa use Gregorian calendar weekday proxies rather than the full traditional Ahargana computation.
- Natonnata uses sunrise/sunset segment interpolation.
- Cheshta uses a normalized daily-speed approximation for direct motion; retrograde receives 60 Virupas. It does not reconstruct the full mean-longitude/Shighrocca eight-motion table.
- Drik uses orb-weighted Parashari aspect approximations, not a full classical Drishti Pinda table.
- Yuddha Bala is set to zero when there is no close war candidate; if a candidate exists, winner/loser adjustment is withheld until apparent diameter and latitude rules are evaluated.
- Dig Bala falls back to a whole-sign angular proxy if quadrant cusps are unavailable.
- Total and strength verdicts are provisional and must be checked against independent reference charts before being treated as authoritative.

## Validation performed
- Python syntax compilation for backend, Shadbala engine, report engine and existing calculation modules.
- Sample chart calculations at 04:00, 12:00 and 20:00 local time in Bhopal, including sunrise-based weekday/Hora handling.
- PDF report generation smoke test.
- Existing API routes and frontend files retained.

## Deployment
Replace the project files using the ZIP folder structure. Do not upload `__pycache__` or `js/app.js_old`. Deploy the Python backend to Render and frontend to GitHub Pages / your webspace as currently configured. Verify `/api/health`, calculate a chart, inspect the Shadbala tables, and download both PDF and JSON.
