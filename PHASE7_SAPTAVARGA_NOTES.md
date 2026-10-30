# Phase 7: Saptavargaja diagnostic groundwork

This release adds seven divisional sign placements (D1, D2, D3, D7, D9, D12, D30) and marks own-sign placements for each of the seven classical planets. It reuses the existing user's workbook mapping in backend.varga_sign. No Saptavargaja Bala points are assigned, and no Shadbala totals are reported.

The report includes a Saptavargaja placement table; JSON includes `shadbala.planets[].saptavargaja_diagnostics`.

**Pending:** Validate all workbook varga mappings; calculate temporary and natural planetary relationships and compound friendships; specify dignity categories and authoritative virupa weights. Subsequently implement remaining Kala Bala, Cheshta Bala, and Drik Bala. Existing Dig/Kendradi approximations still need correction.

Deployment: update backend.py, shadbala_engine.py, report_engine.py together. Preserve all existing files. Re-deploy Render. Frontend is unchanged.
