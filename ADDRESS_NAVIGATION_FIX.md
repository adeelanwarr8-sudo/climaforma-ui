# ClimaForma v2.4.8 — Address → Drawing continuity fix

## Bug
After searching for an address in **Address lookup**, switching the sidebar **Site mode** to **Draw site boundary** reset the map to its default Stockholm location.

## Cause
The sidebar mode-change block cleared `st.session_state['address_location']` on **every** mode change, and `map_center` only honored the saved geocoded location when the current mode was **Address lookup**.

## Correction
- Preserve the resolved address during transitions between **Address lookup** and **Draw site boundary**.
- Center the map on the saved address, at zoom 17, in **both** modes.
- Retain the blue address reference marker in drawing mode.
- Display the selected address in the sidebar and project site summary while drawing.
- Avoid silently clearing an existing site geometry or vector layer during a transition between these two modes.
- Continue resetting site, address and context layers when switching to a **Showcase site**, to avoid geographic misattribution.
- Leave site boundary drawing, deletion, buffer generation, OSM and GeoJSON processing unchanged.

## GitHub deployment
This is a **one-file hotfix** to ClimaForma v2.4.7:
1. Replace only `app.py` in the same GitHub repository.
2. Commit, allow Streamlit to redeploy, and test.
3. Retain `site_mapping.py`, `geo_data.py`, `address_lookup.py`, `buffer_geometry.py`, `showcase_sites.py`, and your `requirements.txt` unchanged.

## Browser acceptance tests
1. Select **Address lookup**, search `Medborgarplatsen, Stockholm`, choose a result, click **Go to selected location**.
2. Confirm the map centers on the address and shows its blue reference marker.
3. Change **Site mode** to **Draw site boundary**. Confirm the **same location and marker** remain visible.
4. Draw a polygon/rectangle. Confirm area and 100 m buffer update correctly.
5. Switch back to **Address lookup** and then to **Draw site boundary**: the existing site should be retained for the same location.
6. Switch to **Showcase site**: the demonstration AOI should load and the previous geocoded address must not carry over.

## Verification
39 automated local tests passed; Python source compilation passed. Live Streamlit behaviour remains for user verification.
