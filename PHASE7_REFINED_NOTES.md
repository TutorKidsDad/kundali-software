Phase 7 refined: PDF page footers and Shadbala incremental components. Uchcha is a Sthana subcomponent; Dig uses whole-sign angular offsets, not measured quadrant cusps. Full Sthana, Kala, Cheshta, Drik and full total are not yet implemented. Never interpret partial subtotal as a full strength score. Back up before deployment.


## Critical HTTP 405 fix
`app.mount('/', StaticFiles(...))` was registered before `@app.post('/api/report/pdf')`, so the catch-all static app intercepted POST requests and returned HTTP 405. The mount has now been moved to the very end of backend.py. Deploy this backend.py and requirements.txt to Render, then redeploy the latest commit. Confirm /openapi.json lists POST /api/report/pdf.

## Shadbala next-stage groundwork
Planet data now includes `longitude_speed_deg_per_day` from Swiss Ephemeris; the Shadbala response includes `motion_diagnostics` for each classical planet. These are raw inputs for Cheshta Bala; they are NOT a calculated Cheshta Bala score. No sixfold totals are presented until all six strengths and conventions have been validated.
