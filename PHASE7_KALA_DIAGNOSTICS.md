# Phase 7: Kala Bala extension (partial, explicit scope)

Added birth-local-date sunrise/sunset calculation through Swiss Ephemeris, sunrise-based weekday (Vara) lord, planetary Hora lord, daytime/night-time flag and third-of-period index. Vara lord receives 45 virupas; Hora lord receives 60 virupas. The hora sequence uses the Chaldean order and advances continuously from sunrise through the night. These scores are exposed under `kala_subcomponents` and included in the existing diagnostic partial subtotal only.

**Withheld, not guessed:** Natonnatha, Tribhaga ruler scoring, Abda, Masa, Ayana and Yuddha. Tribhaga index is reported as a diagnostic only. Full Cheshta and Drik Bala are not implemented in this build. No full sixfold Shadbala total or strength verdict is exposed.

All original project files and routes are retained. `backend.py` and `shadbala_engine.py` are the only modified existing files; this note is new. Validation includes syntax checks and sunrise/hora smoke tests. Independent chart-to-chart numerical validation remains necessary.
