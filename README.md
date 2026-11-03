# ClimaForma v2.2 — Increment 1: Project information and site selection

UI-only Streamlit application based on the approved ClimaForma v2.1 layout.

## Activated in Increment 1
- Editable project name (up to 100 characters), held in Streamlit session state.
- Site-selection modes: showcase site, address draft, and future boundary-drawing selection.
- Three available showcase *labels*: Stockholm / Södermalm, Barcelona / Eixample, Vienna / Neubau.
- Address entry is a text draft only; it is not geocoded or searched.
- Existing Site information panel reflects the selected label, with HTML escaping for safe rendering.

## Explicitly NOT active
No maps, geocoding, boundary drawing, file upload, satellite retrieval, land-cover processing,
thermal prediction, scientific model, design interventions, comparison calculation, or export.
All remaining analytical controls stay disabled and the three original tabs are retained.
Project and site selections are session-local and are not saved across browser sessions.

## Deployment to the existing repository
Replace `app.py` and `README.md` at the repository root. `requirements.txt` remains
`streamlit>=1.38,<2`. Keep `.streamlit/config.toml` as supplied. Commit to `main`.
Streamlit Cloud should redeploy automatically; verify the new version label in the sidebar.

## Smoke test
1. Load app. Confirm all three tabs render.
2. Change project name; confirm header project summary updates.
3. Change showcase city; confirm site information changes but map remains static.
4. Select Address lookup; type a location; confirm it is labelled a draft and no lookup occurs.
5. Select Draw site boundary; verify informative placeholder and no geometry.
6. Navigate tabs; confirm all analysis, drawing, cost and export functions remain disabled.

Run source tests with `python -m pytest -q tests` (pytest not required on Streamlit Cloud).
