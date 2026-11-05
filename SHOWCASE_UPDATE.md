# ClimaForma v2.4.7 — Demonstration site selection

## Purpose
"Showcase site" now shows a bounded **illustrative demonstration AOI**, rather than only moving the map to a city.

- Stockholm · Södermalm, Barcelona · Eixample, Vienna · Neubau each receive a ~120 m by 120 m editable rectangle centred on the existing showcase map location.
- These rectangles are **synthetic sample analysis areas**. They are **not verified parcels, architect-selected project boundaries, cadastral boundaries, or validated reference study sites**. Do not present their surface or thermal characteristics as validated until source data have been acquired and assessed.
- Selecting a new showcase city resets the previous boundary and its associated vector layer and loads that city's sample AOI.
- The user can edit or delete the rectangle, or clear it to draw another site. After clearing/deleting, it **does not automatically reload** at each Streamlit rerun. A manual `Reload demonstration AOI` button is available.
- A site boundary stays shared with the three tabs, and the analysis buffer is independently recomputed on rerun.
- Address lookup, OSM retrieval, GeoJSON processing and the buffer configuration are unchanged.

## GitHub update
Replace `app.py` and add `showcase_sites.py`. Keep the current v2.4.6 versions of `site_mapping.py`, `geo_data.py`, `address_lookup.py`, `buffer_geometry.py`, and `requirements.txt`.

## Live browser acceptance
1. Select Showcase site; verify an editable green AOI is present without drawing. Note the illustrative label.
2. Switch among the three city choices; verify a new AOI and map location each time.
3. Change buffer 100m -> 0m -> 300m; the blue contextual buffer changes without changing the site area.
4. Edit the sample AOI, then delete via Leaflet toolbar; verify it is not restored spontaneously.
5. Click Reload demonstration AOI and verify it returns.
6. Switch to Address lookup; verify no synthetic AOI remains and searching still works.
7. Test OSM and GeoJSON data on the showcase AOI and clear it; verify data clearing.
