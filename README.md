# ClimaForma v2.3 — Increment 2: Interactive Mapping and Site Boundaries

This release builds on the approved Streamlit v2.2 interface and activates **only** site mapping and geometry, retaining the three-tab layout.

## Active features

- Project name and site-mode selection from v2.2.
- OpenStreetMap street layer and Esri aerial imagery layer with a Leaflet layer selector.
- Showcase navigation to Södermalm (Stockholm), Eixample (Barcelona), and Neubau (Vienna).
- Zoom/pan and fullscreen map controls, live coordinate readout.
- Single polygon or rectangle drawing, Leaflet edit/delete toolbar, **Clear boundary** button.
- WGS84 geodesic site area (m² and ha), perimeter, centroid and vertex count.
- Boundary validation: valid polygons only, 1 m²–25 km², one boundary at a time.
- Site boundaries kept in the Streamlit session; switching site mode or showcase clears them.

## Not implemented yet

- Address lookup/geocoding: typed addresses remain drafts; in Address mode the map starts in Stockholm and can be panned manually.
- Satellite imagery analysis, land cover, temperature predictions, design interventions, exports and scientific engine.
- Drawn shape editing is provided by Leaflet Draw. Drawn boundaries are **not** editable through the Design Options tab. The stored reference polygon is displayed in green dashed styling; use the drawing tool to adjust the live drawing or **Clear boundary** to reset. If an edit leaves multiple shapes, delete extras until one remains.
- Aerial tiles may be subject to provider availability and usage conditions; map tiles are for orientation, not analysis.

## Deploy to existing GitHub/Streamlit app

1. Extract ZIP. Upload or replace **app.py**, **site_mapping.py**, **requirements.txt**, and **README.md** in the repository root. Also upload `.streamlit/config.toml` if not present.
2. Keep the Streamlit entrypoint as `app.py` and branch `main`. No need for a new repository/app.
3. Streamlit Cloud installs the requirements and redeploys automatically.
4. Observe dependency logs and the app. If it fails, send the error message rather than replacing the repository.

## Browser acceptance test

1. Confirm the three existing tabs and sidebar remain intact.
2. Select each of the three showcase cities and confirm the map moves to that location.
3. Change between street and aerial basemaps via the map's top-right layer selector.
4. Zoom, pan and use fullscreen; hover/click to read coordinates.
5. Draw a single rectangle in Existing Site. The site-information card should show an area greater than zero in **m² and ha**, perimeter and coordinates.
6. Edit the drawing using the Leaflet edit toolbar and check the area changes. Test a polygon too.
7. Try drawing two polygons: only one is accepted. Delete extras on the map.
8. Click **Clear boundary**: the saved site, map drawing and area must reset.
9. Enter address mode, type an address, and verify **no automatic geocoding** occurs.
10. Check that Design Options and Compare Options still have no analytical functionality.

## Verification performed in build environment

- `python -m pytest -q` → 26 tests passed.
- `python -m py_compile app.py site_mapping.py` → success.
- ZIP integrity check → success.
- **Not verified here:** Actual Streamlit runtime, web browser drawing/editing persistence, remote basemap tiles, and Streamlit Community Cloud deployment. Streamlit could not be installed because the build environment cannot access the package index. Browser acceptance is mandatory.

### Safety and scope

Mapping is for early design **site delineation** only. Area and perimeter values come from geodesic WGS84 geometry, not from satellite imagery or environmental modelling. No site geometry is saved to a server database or uploaded to an external analysis service by this application. Remote basemap providers do receive ordinary tile requests from a user's browser.
