"""ClimaForma v2.4.21 — Barcelona MVP · Increment 5C: spatial intervention drawing.

Site mapping, showcase boundaries, vector context and address navigation remain.
Thermal pixel quality assessment is enabled; temperature modelling is disabled.
"""

import html as html_std

import streamlit as st
import folium
from folium.plugins import Draw, Fullscreen, MousePosition
from streamlit_folium import st_folium
from site_mapping import (BoundaryInfo, SHOWCASE_CENTERS, DEFAULT_CENTER,
                          boundary_from_drawings, same_boundary, boundary_preview_svg)
from geo_data import fetch_osm_buildings, process_geojson_bytes
from design_options import add_option, rename_option, duplicate_option, delete_option, new_option, MAX_OPTIONS
from interventions import (INTERVENTION_TYPES, INTERVENTION_COLORS, MAX_INTERVENTIONS,
                           make_intervention, append_intervention_checked, remove_intervention,
                           replace_intervention, find_surface_conflicts, summarize_interventions)
from address_lookup import search_addresses
from showcase_sites import showcase_boundary, SHOWCASE_FILES
from satellite_discovery import discover_landsat
from landsat_raster import assess_candidate
from landsat_temperature import assess_temperature_candidate
from sentinel2_analysis import discover_sentinel, assess_sentinel
from buffer_geometry import (create_analysis_buffer, BUFFER_MIN_M, BUFFER_MAX_M,
                             BUFFER_DEFAULT_M, BUFFER_STEP_M)

st.set_page_config(
    page_title="ClimaForma | Climate-Responsive Design",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
:root { --ink:#1b343a; --muted:#61757b; --sea:#14786d; --line:#e1ebe8; --sand:#f5f8f6; }
html,body,[class*="css"],.stApp {font-family:system-ui,-apple-system,'Segoe UI',sans-serif;}
.stApp {background:#f8faf9;color:var(--ink);}
[data-testid="stSidebar"] {background:#f0f6f3;border-right:1px solid #dbe8e1;}
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] {gap:.9rem;}
[data-testid="stSidebar"] label {font-size:.86rem;}
.block-container {max-width:1660px;padding-top:1.35rem;padding-bottom:3rem;}
h1,h2,h3 {font-family:system-ui,-apple-system,'Segoe UI',sans-serif;letter-spacing:-.035em;color:#193a3d;}
h2 {font-size:1.35rem !important;} h3 {font-size:1.05rem !important;}
div[data-testid="stTabs"] button {font-weight:650;letter-spacing:.01em;}
div[data-testid="stTabs"] button[aria-selected="true"] {color:#08786b;}
hr {border-color:#dce9e3;}
[data-testid="stWidgetLabel"] p {font-weight:600;color:#29474b;}
[data-testid="stMarkdownContainer"] p {line-height:1.55;}
.cf-kicker{font-size:.79rem;font-weight:800;letter-spacing:.13em;color:#138276;text-transform:uppercase;margin-bottom:.32rem;}
.cf-heading{font-family:system-ui,-apple-system,'Segoe UI',sans-serif;font-size:2.1rem;font-weight:800;color:#17393c;line-height:1.18;letter-spacing:-.045em;}
.cf-lede{font-size:1.02rem;color:#536b70;max-width:880px;margin-top:.42rem;}
.cf-pill{display:inline-block;padding:5px 10px;background:#e6f4ee;color:#176954;font-size:.72rem;border-radius:100px;font-weight:700;letter-spacing:.035em;}
.cf-section{font-weight:750;color:#234147;font-size:1.02rem;margin-bottom:4px;}
.cf-note{font-size:.83rem;color:#5e7478;line-height:1.5;}
.cf-card{border:1px solid #e2ece8;background:#fff;border-radius:14px;padding:18px 19px;box-shadow:0 3px 16px rgba(20,54,46,.03);margin-bottom:10px;}
.cf-card-title{font-weight:750;font-size:.93rem;color:#204248;margin-bottom:9px;}
.cf-metric-value{font-family:system-ui,-apple-system,'Segoe UI',sans-serif;font-size:1.55rem;font-weight:800;color:#204248;line-height:1.2;margin:.35rem 0;}
.cf-metric-label{font-size:.82rem;color:#567078;font-weight:650;}
.cf-chip{display:inline-block;border:1px solid #dde9e3;background:#f6faf8;border-radius:8px;font-size:.74rem;color:#577075;padding:5px 9px;margin-right:5px;margin-bottom:6px;}
.cf-placeholder{border:1px dashed #afc9c0;border-radius:13px;background:#f8fcfa;padding:18px;color:#738a85;font-size:.83rem;text-align:center;}
.cf-bar-row{display:flex;align-items:center;gap:10px;margin:12px 0;}
.cf-bar-name{font-size:.77rem;color:#536b6f;width:116px;flex:none;}
.cf-bar-track{background:#edf4f0;border-radius:8px;height:13px;flex:1;overflow:hidden;}
.cf-bar-fill{background:#79afa2;height:100%;border-radius:8px;}
.cf-legend{display:inline-flex;align-items:center;gap:6px;font-size:.76rem;color:#63797b;margin-right:12px;margin-bottom:8px;}
.cf-dot{width:10px;height:10px;border-radius:3px;display:inline-block;}
.cf-smallline{height:1px;background:#e4eeea;margin:12px 0;}
.cf-brand{font-family:system-ui,-apple-system,'Segoe UI',sans-serif;font-size:1.55rem;font-weight:800;letter-spacing:-.045em;color:#17695e;}
.cf-brandline{color:#657d79;font-size:.74rem;letter-spacing:.025em;margin-top:1px;}
.cf-step{color:#8da29c;font-size:.73rem;text-transform:uppercase;letter-spacing:.12em;font-weight:700;}
.cf-map-wrap{background:#f2f6f3;overflow:hidden;border:1px solid #d9e7e0;border-radius:14px;}
.cf-map-label{font-size:.78rem;color:#53726e;padding:8px 14px;background:#fff;border-top:1px solid #e2ece8;}
.cf-footer{font-size:.77rem;color:#718881;border-top:1px solid #dfebe5;padding-top:17px;margin-top:30px;}

[data-testid="stSidebar"] {min-width:276px;}
[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {font-size:.87rem;}
[data-testid="stTabs"] [data-baseweb="tab-list"] {gap:1.35rem;border-bottom:1px solid #dfe9e5;}
[data-testid="stTabs"] button {padding:13px 2px;font-size:.94rem;}
.cf-subheading{font-size:1.1rem;font-weight:760;color:#204248;letter-spacing:-.02em;}
.cf-eyebrow{font-size:.75rem;color:#237f70;letter-spacing:.1em;text-transform:uppercase;font-weight:800;}
.cf-intro{font-size:.9rem;color:#5f7778;margin:3px 0 14px;line-height:1.55;}
.cf-quiet{border:1px solid #dfece5;background:#f1f8f4;color:#437064;border-radius:11px;padding:12px 15px;font-size:.82rem;margin:12px 0 17px;}
.cf-viewbar{display:flex;gap:7px;flex-wrap:wrap;margin:6px 0 12px;}
.cf-view{font-size:.75rem;font-weight:650;background:#f1f6f4;border:1px solid #dceae4;padding:6px 10px;border-radius:7px;color:#5b746c;}
.cf-view-active{background:#dff2e9;border-color:#c1dfd3;color:#1b6e61;}
.cf-toolbar{padding:10px 13px;background:#fff;border:1px solid #e0ebe5;border-radius:11px;margin:10px 0;}
.cf-muted-block{background:#fafcfb;border:1px dashed #c4d9cd;border-radius:12px;padding:17px 14px;text-align:center;color:#67817c;min-height:80px;display:flex;align-items:center;justify-content:center;flex-direction:column;gap:5px;}
.cf-minihead{font-size:.78rem;font-weight:750;color:#3d5c5d;margin:5px 0 8px;}
.cf-caption{font-size:.78rem;color:#68817c;line-height:1.5;}
.cf-steps{color:#7b918a;font-size:.8rem;margin:10px 0 0;}
.cf-scenario-name{font-size:.93rem;font-weight:750;color:#214447;margin-bottom:10px;}
.cf-section-head{margin:22px 0 12px;}
.cf-outputrow{display:flex;gap:8px;flex-wrap:wrap;}
.cf-action{font-size:.78rem;border:1px solid #d9e6df;background:#f4f8f6;color:#71847e;border-radius:8px;padding:8px 11px;}
.cf-divider{height:1px;background:#e5ede9;margin:16px 0;}
@media (max-width:900px){.cf-heading{font-size:1.67rem}.cf-card{padding:13px 14px}.block-container{padding-top:1rem}}
</style>
""", unsafe_allow_html=True)


def html(content: str) -> None:
    """Render visual-only markup; never registers event handlers."""
    st.markdown(content, unsafe_allow_html=True)


def card(title: str, body: str) -> None:
    html(f'<div class="cf-card"><div class="cf-card-title">{title}</div>{body}</div>')


def metric(label: str, value: str = "—", note: str = "Awaiting data integration") -> None:
    html(f'<div class="cf-card"><div class="cf-metric-label">{label}</div><div class="cf-metric-value">{value}</div><div class="cf-note">{note}</div></div>')


def site_illustration(variant: str = "base") -> str:
    """A decorative, static SVG plan. It does not represent a real location or results."""
    if variant == "green":
        garden = '<rect x="280" y="165" width="192" height="118" rx="11" fill="#c0dec2"/><path d="M285 226 L466 226" stroke="#f7f8e8" stroke-width="10"/><circle cx="332" cy="193" r="20" fill="#539b75"/><circle cx="410" cy="255" r="19" fill="#539b75"/>'
    elif variant == "cool":
        garden = '<rect x="280" y="165" width="192" height="118" rx="11" fill="#d5e6e4"/><path d="M300 180 L460 260 M310 270 L457 179" stroke="#f5fbf9" stroke-width="17"/><circle cx="360" cy="209" r="20" fill="#84a8a0"/>'
    else:
        garden = '<rect x="280" y="165" width="192" height="118" rx="11" fill="#d7d2c6"/><path d="M285 223 L466 223" stroke="#eee8dc" stroke-width="12"/><circle cx="343" cy="188" r="16" fill="#90b89b"/>'
    return f'''<div class="cf-map-wrap"><svg viewBox="0 0 760 410" width="100%" style="display:block" role="img" aria-label="Illustrative architectural site plan, not geospatial data">
<rect width="760" height="410" fill="#e9efe8"/>
<path d="M0 90H760 M0 342H760" stroke="#fff" stroke-width="44"/><path d="M112 0V410 M637 0V410" stroke="#fff" stroke-width="42"/>
<path d="M0 90H760 M0 342H760" stroke="#d4ded6" stroke-dasharray="7 9" stroke-width="1.4"/><path d="M112 0V410 M637 0V410" stroke="#d4ded6" stroke-dasharray="7 9" stroke-width="1.4"/>
<rect x="172" y="125" width="410" height="193" rx="13" fill="#f8faf5" stroke="#b1c6b9" stroke-width="2" stroke-dasharray="8 5"/>
<path d="M194 142 H563 V159 H194 Z M194 286 H563 V305 H194 Z M194 159 H260 V286 H194 Z M493 159 H563 V286 H493 Z" fill="#8faba6"/>
{garden}
<g fill="#6c9d79"><circle cx="46" cy="44" r="22"/><circle cx="696" cy="55" r="27"/><circle cx="695" cy="240" r="18"/><circle cx="46" cy="287" r="20"/><circle cx="183" cy="373" r="18"/><circle cx="577" cy="375" r="17"/></g>
<g fill="#fff" opacity=".33"><circle cx="39" cy="39" r="8"/><circle cx="686" cy="47" r="9"/></g>
<rect x="199" y="128" width="356" height="172" rx="4" fill="none" stroke="#0c8173" stroke-width="2" stroke-dasharray="9 5"/>
<rect x="19" y="18" width="166" height="31" rx="8" fill="#fff" opacity=".95"/><text x="30" y="38" font-size="14" fill="#456a62" font-family="sans-serif">CONCEPT SITE PLAN</text>
<g transform="translate(707,325)"><circle r="28" fill="white" opacity=".92"/><path d="M0 -17 L7 8 L0 4 L-7 8Z" fill="#47756b"/><text x="0" y="-19" text-anchor="middle" font-size="11" fill="#47756b">N</text></g>
</svg><div class="cf-map-label">Illustrative layout only · Not a real site, map layer, or temperature result</div></div>'''


# Increment 1: session-local project identity and selection only. No geocoding/GIS.
SITE_MODES = ("Showcase site", "Address lookup", "Draw site boundary")
SHOWCASES = tuple(SHOWCASE_FILES)


def selected_site_summary(mode: str, showcase: str, address: str) -> tuple[str, str, str]:
    """Present the selected location and site information."""
    if mode == "Showcase site":
        return showcase, "User-supplied demonstration boundary · construction and parcel status unverified", "Demo AOI"
    if mode == "Address lookup":
        return (address.strip() or "No address selected"), "Address location is a navigation reference; draw the site boundary separately", "Address location"
    if address:
        return address, "Draw or edit the project boundary at the selected address", "Address-based site"
    return "Boundary not drawn", "Draw or edit the boundary directly on the map", "Boundary workflow"


with st.sidebar:
    html('<div class="cf-brand">◈ ClimaForma</div><div class="cf-brandline">Climate-responsive design intelligence</div>')
    html('<span class="cf-pill">V2.4.20 · INCREMENT 5B</span>')
    st.divider()
    html('<div class="cf-step">01 · Project information</div>')
    st.text_input("Project name", value="Untitled climate design study", key="project_name", max_chars=100,
                  help="The name is stored only in the current Streamlit session.")
    st.caption("New design assessment · Session-local draft")
    st.divider()
    html('<div class="cf-step">02 · Site selection</div>')
    site_mode = st.selectbox("Site mode", SITE_MODES, key="site_mode")
    if site_mode == "Showcase site":
        showcase_city = SHOWCASES[0]
        st.caption("Showcase: Barcelona · Selected construction site")
        address_draft = ""
        st.caption("Your supplied demonstration site polygon loads automatically. Construction and parcel status are unverified.")
    elif site_mode == "Address lookup":
        showcase_city = SHOWCASES[0]
        address_draft = st.text_input("Address or place", key="address_draft", max_chars=180,
                                      placeholder="Street, city, country")
        if st.button("Search address", key="search_address", use_container_width=True):
            try:
                with st.spinner("Looking up address…"):
                    matches = search_addresses(address_draft)
                st.session_state["address_matches"] = matches
                st.session_state["address_match_query"] = address_draft.strip()
                if not matches:
                    st.warning("No matching address found. Try a more specific location.")
            except ValueError as exc:
                st.error(str(exc))
            except Exception:
                st.error("Address service is temporarily unavailable. Please retry later or use map navigation.")
        matches = (st.session_state.get("address_matches", [])
                   if st.session_state.get("address_match_query") == address_draft.strip() else [])
        if matches:
            selected = st.selectbox("Matching locations", options=range(len(matches)),
                                    format_func=lambda i: matches[i]["label"], key="address_match_index")
            if st.button("Go to selected location", key="navigate_to_address", use_container_width=True,
                         disabled=st.session_state.get("boundary_info") is not None):
                point = matches[selected]
                st.session_state["address_location"] = point
                st.session_state["map_generation"] = st.session_state.get("map_generation", 0) + 1
                st.rerun()
            if st.session_state.get("boundary_info") is not None:
                st.caption("Clear the current site boundary before navigating to another address.")
        st.caption("Search only when clicked · © OpenStreetMap contributors · Location is not a property boundary.")
    else:
        showcase_city = SHOWCASES[0]
        address_draft = ""
        active_address = st.session_state.get("address_location")
        if active_address:
            st.success(f"Drawing location: {active_address['label']}")
            st.caption("The map remains at your searched address. Draw one polygon or rectangle to define the actual site.")
        else:
            st.info("Go to Existing Site → draw one polygon or rectangle on the map. Use the edit/delete toolbar to adjust it.")
    st.divider()
    html('<div class="cf-step">03 · Analysis settings</div>')
    analysis_buffer_m = st.slider("Analysis buffer (m)", min_value=BUFFER_MIN_M,
                                  max_value=BUFFER_MAX_M, value=BUFFER_DEFAULT_M,
                                  step=BUFFER_STEP_M, key="analysis_buffer_m",
                                  help="Automatic context buffer around the selected site; does not change site area.")
    st.caption("0 m = site only · 100 m default · 300 m maximum. Not a predicted cooling distance.")
    st.divider()
    html('<div class="cf-step">04 · Application status</div>')
    html('<div class="cf-quiet"><strong>Increment 5B active</strong><div class="cf-caption">Landsat thermal QA and Sentinel-2 optical indices are available. Integrated observed LST and Sentinel-2 index maps are available after QA; predictions remain disabled.</div></div>')
    st.caption("ClimaForma v2.4.20 · Barcelona showcase · Landsat QA + Sentinel-2 optical indices")

# Preserve the geocoded location when moving between Address lookup and
# Draw site boundary. Both modes refer to the same user-selected location.
# A showcase is a different site context and must reset its project geometry.
map_context = (site_mode, showcase_city if site_mode == "Showcase site" else None)
previous_context = st.session_state.get("map_context")
if previous_context != map_context:
    previous_mode = previous_context[0] if isinstance(previous_context, tuple) else None
    address_to_drawing = (previous_mode == "Address lookup" and site_mode == "Draw site boundary")
    drawing_to_address = (previous_mode == "Draw site boundary" and site_mode == "Address lookup")
    same_address_workflow = address_to_drawing or drawing_to_address
    st.session_state["map_context"] = map_context
    if not same_address_workflow:
        st.session_state["boundary_info"] = (showcase_boundary(showcase_city)
                                              if site_mode == "Showcase site" else None)
        st.session_state["vector_layer"] = None
        st.session_state["map_drawings_seen"] = False
        st.session_state["address_location"] = None
        st.session_state["address_matches"] = []
        st.session_state["address_match_query"] = None
    # Remount Leaflet when switching modes so the mapped address is respected.
    st.session_state["map_generation"] = st.session_state.get("map_generation", 0) + 1

# Changing the slider rebuilds the visible map while preserving the site
# boundary and any existing context dataset.
if st.session_state.get("buffer_displayed_m") != analysis_buffer_m:
    st.session_state["buffer_displayed_m"] = analysis_buffer_m
    st.session_state["map_generation"] = st.session_state.get("map_generation", 0) + 1

active_address = st.session_state.get("address_location")
map_center = ((st.session_state["boundary_info"].latitude,
               st.session_state["boundary_info"].longitude, 16)
              if site_mode == "Showcase site" and st.session_state.get("boundary_info") is not None else
              SHOWCASE_CENTERS.get(showcase_city, DEFAULT_CENTER)
              if site_mode == "Showcase site" else
              (active_address["lat"], active_address["lon"], 17)
              if active_address else DEFAULT_CENTER)
if active_address and site_mode in ("Address lookup", "Draw site boundary"):
    address_draft = active_address["label"]

# Invalidate old satellite results BEFORE Folium renders. A different
# site geometry or buffer cannot inherit the previous temperature overlay.
import json as _site_json
_site_boundary = st.session_state.get("boundary_info")
_current_satellite_signature = (_site_json.dumps(_site_boundary.geometry, sort_keys=True), analysis_buffer_m) if _site_boundary else None
if st.session_state.get("landsat_query_signature") != _current_satellite_signature:
    st.session_state.pop("landsat_temperature_result", None)


def build_site_map(center: tuple[float, float, int], boundary: BoundaryInfo | None) -> folium.Map:
    """Make a navigation/drawing map. No basemap data are used in calculations."""
    latitude, longitude, zoom = center
    m = folium.Map(location=[latitude, longitude], zoom_start=zoom, tiles=None, control_scale=True)
    folium.TileLayer(tiles="OpenStreetMap", name="Street map", show=True).add_to(m)
    if site_mode in ("Address lookup", "Draw site boundary") and st.session_state.get("address_location"):
        loc = st.session_state["address_location"]
        folium.Marker([loc["lat"], loc["lon"]],
                      tooltip="Address search result (not a site boundary)",
                      icon=folium.Icon(color="blue", icon="info-sign")).add_to(m)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        name="Aerial imagery", attr="Tiles © Esri and contributors", show=False,
    ).add_to(m)
    # Analysis buffer is a derived, read-only context layer. It must NOT be
    # placed in Leaflet Draw's editable boundary group.
    if boundary is not None and analysis_buffer_m > 0:
        context = create_analysis_buffer(boundary.geometry, analysis_buffer_m)
        if context is not None:
            folium.GeoJson(
                context.geometry, name=f"Analysis buffer · {analysis_buffer_m} m",
                style_function=lambda _: {"color": "#4787b5", "weight": 2,
                                          "fillColor": "#75b4db", "fillOpacity": 0.07,
                                          "dashArray": "6 5"},
            ).add_to(m)
    # IMPORTANT: preloaded/saved geometry MUST belong to the same editable
    # FeatureGroup used by Leaflet Draw. A separate folium.GeoJson overlay
    # is not controlled by the toolbar's Edit/Delete actions.
    editable = folium.FeatureGroup(name="Editable site boundary", show=True)
    editable.add_to(m)
    if boundary is not None:
        # Folium Polygon generates an editable L.Polygon rather than the
        # L.GeoJSON container that Leaflet Draw cannot reliably edit.
        rings = boundary.geometry["coordinates"]
        latlon_rings = [
            [(float(lat), float(lon)) for lon, lat in ring]
            for ring in rings
        ]
        locations = latlon_rings[0] if len(latlon_rings) == 1 else latlon_rings
        folium.Polygon(
            locations=locations, color="#087c6e", weight=2,
            fill=True, fill_opacity=0.12, dash_array="5 4",
        ).add_to(editable)
    # Once a site exists, disable NEW geometry creation. Editing and deleting
    # the existing editable polygon remain enabled. To redraw, clear it first.
    allow_new_boundary = boundary is None
    Draw(
        feature_group=editable,
        export=False, position="topleft", show_geometry_on_click=False,
        draw_options={"polyline": False, "circle": False, "circlemarker": False,
                      "marker": False,
                      "polygon": {"allowIntersection": False} if allow_new_boundary else False,
                      "rectangle": True if allow_new_boundary else False},
        edit_options={"edit": True, "remove": True},
    ).add_to(m)
    Fullscreen(position="topright").add_to(m)
    MousePosition(position="bottomleft", separator=" / ", prefix="Lat/Lon:", num_digits=5).add_to(m)
    thermal = st.session_state.get("landsat_temperature_result")
    if (boundary is not None and thermal is not None and thermal.overlay_png is not None
            and thermal.overlay_bounds is not None
            and st.session_state.get("landsat_query_signature") == _current_satellite_signature):
        import base64
        image_url = "data:image/png;base64," + base64.b64encode(thermal.overlay_png).decode("ascii")
        folium.raster_layers.ImageOverlay(image=image_url, bounds=thermal.overlay_bounds,
                                          name=f"Observed LST · {thermal.observed_utc[:10]}",
                                          opacity=0.78, interactive=False, show=True).add_to(m)
    optical = st.session_state.get("sentinel2_indices")
    optical_discovery = st.session_state.get("sentinel2_discovery")
    optical_candidate = optical_discovery.candidate if optical_discovery is not None else None
    if (boundary is not None and optical is not None and optical.status == "PRELIMINARY_QA_PASS"
            and optical_candidate is not None and optical.scene_id == optical_candidate.item_id
            and st.session_state.get("sentinel2_query_signature") == _current_satellite_signature
            and optical.overlay_bounds is not None):
        import base64
        for name, png in (("NDVI", optical.ndvi_overlay_png), ("NDBI", optical.ndbi_overlay_png)):
            if png:
                data_url = "data:image/png;base64," + base64.b64encode(png).decode("ascii")
                folium.raster_layers.ImageOverlay(
                    image=data_url, bounds=optical.overlay_bounds,
                    name=f"Sentinel-2 {name} · {optical.observed_utc[:10]}",
                    opacity=0.82, interactive=False, show=False,
                ).add_to(m)
    layer = st.session_state.get("vector_layer")
    if layer is not None and layer.features:
        folium.GeoJson(layer.feature_collection, name=layer.name,
                       style_function=lambda _: {"color": "#9a653c", "fillColor": "#ce9c67",
                                                  "weight": 1.4, "fillOpacity": 0.25}).add_to(m)
    folium.LayerControl(collapsed=True).add_to(m)
    return m

site_title, site_note, site_kind = selected_site_summary(site_mode, showcase_city, address_draft)
project_label = (st.session_state.project_name.strip() or "Untitled climate design study")
site_title_safe = html_std.escape(site_title)
site_note_safe = html_std.escape(site_note)
site_kind_safe = html_std.escape(site_kind)
project_label_safe = html_std.escape(project_label)

html('<div class="cf-kicker">Architecture · Landscape · Climate adaptation</div><div class="cf-heading">Design cooler places, with clarity.</div><div class="cf-lede">A visual workspace for exploring site conditions, shaping climate-responsive design alternatives, and reviewing comparative outcomes.</div>')
html(f'<div class="cf-quiet"><strong>Project:</strong> {project_label_safe} &nbsp; · &nbsp; <strong>Site:</strong> {site_title_safe} &nbsp; · &nbsp; Observed LST available after QA · No cooling predictions</div>')

t1, t2, t3 = st.tabs(["01  Existing Site", "02  Design Options", "03  Compare Options"])

with t1:
    st.write("")
    html('<div class="cf-subheading">Existing Site</div><div class="cf-intro">Review site context, environmental layers, and baseline information before evaluating possible interventions.</div>')
    main, aside = st.columns([2.15, 1], gap="large")
    with main:
        html('<div class="cf-eyebrow">Site workspace</div>')
        if site_mode == "Showcase site":
            st.info("Showcase AOI: user-provided geographic polygon for a selected construction-site case. Construction status and cadastral parcel limits have not been independently verified. You may edit, clear, or reload this boundary.")
        html('<div class="cf-quiet"><strong>Interactive mapping enabled</strong> · Draw one polygon or rectangle. Then edit or delete it; use Clear boundary before drawing a different site. Basemaps are for visual reference only.</div>')
        # Use a stable component key across ordinary Streamlit reruns so Leaflet
        # retains the user's unsaved drawing edits. A new site context resets it.
        current_boundary = st.session_state.get("boundary_info")
        map_result = st_folium(
            build_site_map(map_center, current_boundary),
            height=510, width=None,
            key=f"site_map_{st.session_state['map_generation']}",
            returned_objects=["all_drawings", "last_active_drawing"],
            use_container_width=True,
        )
        drawings = map_result.get("all_drawings") if isinstance(map_result, dict) else None
        # Single-site rule: the toolbar disables new drawing once the first
        # polygon is accepted. Editing or deleting the existing site is allowed.
        if drawings is not None:
            try:
                observed = boundary_from_drawings(drawings)
                if observed is not None:
                    st.session_state["map_drawings_seen"] = True
                    if not same_boundary(observed, st.session_state.get("boundary_info")):
                        new_site = st.session_state.get("boundary_info") is None
                        st.session_state["boundary_info"] = observed
                        st.session_state["vector_layer"] = None
                        if new_site:
                            # Remount once to remove polygon/rectangle creation
                            # controls; edit and delete remain available.
                            st.session_state["map_drawings_seen"] = False
                            st.session_state["map_generation"] += 1
                            st.rerun()
                elif drawings == [] and st.session_state.get("map_drawings_seen", False):
                    # User used the Leaflet delete toolbar and clicked Save.
                    st.session_state["boundary_info"] = None
                    st.session_state["vector_layer"] = None
                    st.session_state["map_drawings_seen"] = False
                    st.session_state["map_generation"] += 1
                    st.rerun()
            except (ValueError, TypeError, KeyError) as error:
                st.warning(f"Boundary not accepted: {error}")
        if site_mode == "Showcase site" and st.session_state.get("boundary_info") is None:
            if st.button("Reload showcase AOI", key="reload_showcase"):
                st.session_state["boundary_info"] = showcase_boundary(showcase_city)
                st.session_state["vector_layer"] = None
                st.session_state["map_drawings_seen"] = False
                st.session_state["map_generation"] += 1
                st.rerun()
        controls, status = st.columns([1, 2])
        with controls:
            if st.button("Clear boundary", key="clear_site_boundary", use_container_width=True):
                st.session_state["boundary_info"] = None
                st.session_state["vector_layer"] = None
                st.session_state["map_drawings_seen"] = False
                st.session_state["map_generation"] += 1
                st.rerun()
        with status:
            st.caption("Map layer selector: top-right. Draw: top-left. Editing uses Leaflet Draw controls. One active site boundary per project. To draw another, clear the current one first.")
        if st.session_state.get("boundary_info") is not None:
            st.caption(f"Analysis context: {analysis_buffer_m} m around the active site. "
                       "Toggle the blue dashed buffer in the map layer selector; "
                       "site area and perimeter remain unchanged.")
        html('<div class="cf-toolbar"><div class="cf-minihead">Map tools · active</div><span class="cf-chip">Zoom / pan</span><span class="cf-chip">Draw polygon / rectangle</span><span class="cf-chip">Edit / delete</span><span class="cf-chip">Street / aerial basemap</span><div class="cf-caption">Coordinates are WGS84 (EPSG:4326); areas are geodesic measurements. Satellite analyses are optional and user-initiated; no land-cover classification or cooling predictions.</div></div>')
        html('<div class="cf-section-head"><div class="cf-subheading">Vector context data · Increment 3</div><div class="cf-caption">Only explicit user requests load geospatial layers. Imported layers are not land-cover classifications.</div></div>')
        current_site = st.session_state.get("boundary_info")
        if current_site is None:
            st.info("Draw a site boundary before requesting or uploading vector data.")
        else:
            vleft, vright = st.columns([1, 1], gap="medium")
            with vleft:
                upload = st.file_uploader("Upload polygon GeoJSON (EPSG:4326)", type=["geojson", "json"],
                                          key="vector_upload", help="Up to 2 MB and 1,500 polygons; clipped to your site.")
                if st.button("Validate uploaded GeoJSON", disabled=upload is None,
                             use_container_width=True, key="validate_vector"):
                    try:
                        st.session_state["vector_layer"] = process_geojson_bytes(upload.getvalue(), current_site.geometry)
                        st.rerun()
                    except ValueError as exc:
                        st.error(str(exc))
            with vright:
                st.caption("OpenStreetMap building footprints (optional)")
                if st.button("Fetch OSM buildings for site", use_container_width=True, key="fetch_osm"):
                    try:
                        with st.spinner("Requesting OSM buildings…"):
                            st.session_state["vector_layer"] = fetch_osm_buildings(current_site.geometry, current_site.bounds)
                        st.rerun()
                    except ValueError as exc:
                        st.error(str(exc))
            layer = st.session_state.get("vector_layer")
            if layer is not None:
                st.write(f"**{layer.name}:** {layer.kept} features inside site; "
                         f"{layer.checked} checked; {layer.rejected} rejected.")
                st.caption(f"Source: {layer.source} · Retrieved/processed: {layer.acquired_utc} · "
                           + "; ".join(layer.notes))
                if st.button("Remove context layer", key="clear_vector", use_container_width=False):
                    st.session_state["vector_layer"] = None
                    st.rerun()
                st.caption("Use the layer selector to show or hide context features. "
                           "The site boundary remains independent of this context layer.")
        html('<div class="cf-section-head"><div class="cf-subheading">Landsat 8/9 · Scene discovery and quality assessment · Increment 4B</div><div class="cf-caption">Discover recent observations and explicitly assess site-level thermal/QA raster coverage. Observed LST available on demand after QA; no cooling predictions.</div></div>')
        # Record which exact site geometry and buffer generated any prior result.
        import json as _json
        signature = (_json.dumps(current_site.geometry, sort_keys=True), analysis_buffer_m) if current_site else None
        if st.session_state.get("landsat_query_signature") != signature:
            st.session_state.pop("landsat_discovery_result", None)
            st.session_state.pop("landsat_qa_result", None)
            st.session_state.pop("landsat_temperature_result", None)
            st.session_state["landsat_query_signature"] = signature
        if current_site is None:
            st.info("Select or draw a site boundary to search for Landsat observations.")
        else:
            st.caption("Search order: 3–7 days → 8–15 days → 16–30 days → 31–45 days. Maximum age: 45 days. "
                       f"Search footprint: selected site plus {analysis_buffer_m} m buffer.")
            if st.button("Find recent Landsat 8/9 scenes", key="discover_landsat", use_container_width=True):
                try:
                    with st.spinner("Searching Landsat scene metadata…"):
                        st.session_state["landsat_discovery_result"] = discover_landsat(current_site.geometry, analysis_buffer_m)
                        st.session_state.pop("landsat_qa_result", None)
                        st.session_state.pop("landsat_temperature_result", None)
                except ValueError as exc:
                    st.session_state.pop("landsat_discovery_result", None)
                    st.session_state.pop("landsat_qa_result", None)
                    st.session_state.pop("landsat_temperature_result", None)
                    st.error(str(exc))
            discovery = st.session_state.get("landsat_discovery_result")
            if discovery is not None:
                if discovery.candidate:
                    candidate = discovery.candidate
                    st.success(f"Candidate identified: {candidate.platform.upper()} · {candidate.age_days} days old · {candidate.tier} tier")
                    st.write(f"**Acquisition (UTC):** {candidate.observed_utc}  |  **Scene-wide cloud:** {candidate.scene_cloud_pct:.1f}%")
                    st.code(candidate.item_id, language=None)
                    st.caption(f"Collection: {candidate.collection} · Thermal metadata asset: {candidate.thermal_asset} · "
                               f"Search performed: {discovery.searched_at_utc}")
                    st.caption("Scene-wide cloud metadata do not indicate site-level cloud conditions.")
                    if st.button("Assess selected scene thermal/QA pixels", key="assess_thermal", use_container_width=True):
                        try:
                            with st.spinner("Reading thermal and QA raster windows for the selected site…"):
                                st.session_state["landsat_qa_result"] = assess_candidate(
                                    candidate, current_site.geometry, analysis_buffer_m)
                        except ValueError as exc:
                            st.session_state.pop("landsat_qa_result", None)
                            st.error(str(exc))
                    quality = st.session_state.get("landsat_qa_result")
                    if quality is not None and quality.scene_id == candidate.item_id:
                        if quality.status == "PRELIMINARY_QA_PASS":
                            st.success("Site-level raster screening: preliminary pass")
                        else:
                            st.warning(f"Site-level raster screening: {quality.status.replace('_', ' ').title()}")
                        q1, q2 = st.columns(2)
                        with q1:
                            st.metric("Valid site delivery pixels", f"{quality.site.valid_pixels}/{quality.site.footprint_pixels}")
                            st.caption(f"Site valid coverage: {quality.site.coverage_pct}%" if quality.site.coverage_pct is not None else "Site has no pixel centres on this raster grid.")
                        with q2:
                            st.metric("Valid context delivery pixels", f"{quality.context.valid_pixels}/{quality.context.footprint_pixels}")
                            st.caption(f"Site + buffer valid coverage: {quality.context.coverage_pct}%" if quality.context.coverage_pct is not None else "Context has no pixel centres on this raster grid.")
                        for note in quality.notes:
                            st.caption(note)
                        st.info("This evaluates the discovered candidate only. If its QA fails, alternate-scene screening remains future work.")
                        if quality.status == "PRELIMINARY_QA_PASS":
                            if st.button("Calculate and display observed Landsat LST", key="calculate_lst", use_container_width=True):
                                try:
                                    with st.spinner("Calculating observed surface temperature and georeferenced overlay…"):
                                        st.session_state["landsat_temperature_result"] = assess_temperature_candidate(
                                            candidate, current_site.geometry, analysis_buffer_m)
                                    st.session_state["map_generation"] += 1
                                    st.rerun()
                                except ValueError as exc:
                                    st.session_state.pop("landsat_temperature_result", None)
                                    st.error(str(exc))
                            thermal_result = st.session_state.get("landsat_temperature_result")
                            if thermal_result is not None and thermal_result.scene_id == candidate.item_id:
                                if thermal_result.status == "SITE_QA_PASS":
                                    st.success("Observed Landsat LST: computed from QA-masked thermal pixels")
                                    c1,c2 = st.columns(2)
                                    with c1: st.metric("Mean site LST (°C)", f"{thermal_result.mean_c:.1f}" if thermal_result.mean_c is not None else "—")
                                    with c2: st.metric("95th percentile site LST (°C)", f"{thermal_result.p95_c:.1f}" if thermal_result.p95_c is not None else "—")
                                    st.caption(f"Site valid pixels: {thermal_result.valid_site_pixels}/{thermal_result.site_pixels} ({thermal_result.site_coverage_pct:.1f}%). "
                                               f"Context coverage: {thermal_result.context_coverage_pct:.1f}%.")
                                    if thermal_result.display_range_c:
                                        st.caption(f"Map colors: {thermal_result.display_range_c[0]:.1f}–{thermal_result.display_range_c[1]:.1f} °C (2nd–98th context percentiles); "
                                                   "blue/cyan is cooler, yellow/red is warmer. Toggle observed LST in the map layer selector.")
                                    if st.button("Remove LST map", key="remove_lst_map"):
                                        st.session_state.pop("landsat_temperature_result", None)
                                        st.session_state["map_generation"] += 1
                                        st.rerun()
                                else:
                                    st.warning(f"LST withheld: {thermal_result.status}")
                                for note in thermal_result.notes:
                                    st.caption(note)
                else:
                    st.warning("No qualifying Landsat 8/9 scene metadata found within the permitted 3–45-day windows.")
                for note in discovery.notes:
                    st.caption(note)
        html('<div class="cf-section-head"><div class="cf-subheading">Sentinel-2 · Optical site characterization · Increment 4C</div><div class="cf-caption">Find one Sentinel-2 L2A scene in the 90-day window (up to 180 days fallback) and assess masked NDVI / NDBI on a 20 m analysis grid. Not a land-cover classification or temperature measurement.</div></div>')
        if st.session_state.get("sentinel2_query_signature") != signature:
            st.session_state.pop("sentinel2_discovery", None)
            st.session_state.pop("sentinel2_indices", None)
            st.session_state["sentinel2_query_signature"] = signature
        if current_site is None:
            st.info("Select a site boundary to search for Sentinel-2 observations.")
        else:
            st.caption("Sentinel-2 optical search: last 90 days first, then days 91–180 if no metadata-qualified candidate. Maximum 180 days. "
                       f"Site and {analysis_buffer_m} m context buffer used to locate candidate imagery.")
            if st.button("Find recent Sentinel-2 scenes", key="discover_sentinel", use_container_width=True):
                try:
                    with st.spinner("Searching Sentinel-2 optical scene metadata…"):
                        st.session_state["sentinel2_discovery"] = discover_sentinel(current_site.geometry, analysis_buffer_m)
                        st.session_state.pop("sentinel2_indices", None)
                except ValueError as exc:
                    st.session_state.pop("sentinel2_discovery", None)
                    st.session_state.pop("sentinel2_indices", None)
                    st.error(str(exc))
            s2 = st.session_state.get("sentinel2_discovery")
            if s2 is not None:
                if s2.candidate is None:
                    st.warning("No metadata-qualified Sentinel-2 L2A candidate found within 180 days.")
                else:
                    sc = s2.candidate
                    st.success(f"Sentinel-2 candidate: {sc.platform.upper()} · {sc.age_days} days old · {sc.tier}")
                    st.code(sc.item_id, language=None)
                    st.caption(f"Acquisition: {sc.observed_utc} · Scene-wide cloud: {sc.scene_cloud_pct:.1f}% · Processing baseline: {sc.processing_baseline}")
                    if st.button("Assess Sentinel-2 NDVI / NDBI", key="assess_sentinel", use_container_width=True):
                        try:
                            with st.spinner("Reading Sentinel-2 bands and cloud classification…"):
                                st.session_state["sentinel2_indices"] = assess_sentinel(sc, current_site.geometry, analysis_buffer_m)
                            st.session_state["map_generation"] += 1
                            st.rerun()
                        except ValueError as exc:
                            st.session_state.pop("sentinel2_indices", None)
                            st.error(str(exc))
                    indices = st.session_state.get("sentinel2_indices")
                    if indices is not None and indices.scene_id == sc.item_id:
                        if indices.status == "PRELIMINARY_QA_PASS":
                            st.success("Sentinel-2 site optical QA: preliminary pass")
                        else:
                            st.warning(f"Sentinel-2 site optical QA: {indices.status.replace('_', ' ').title()}")
                        a, b, c = st.columns(3)
                        with a:
                            st.metric("Valid site pixels (20 m grid)", f"{indices.valid_pixels}/{indices.footprint_pixels}")
                            st.caption(f"Valid site coverage: {indices.valid_coverage_pct}%" if indices.valid_coverage_pct is not None else "No pixel centres in site")
                        with b:
                            st.metric("Mean NDVI", f"{indices.ndvi_mean:.3f}" if indices.ndvi_mean is not None else "—")
                        with c:
                            st.metric("Mean NDBI", f"{indices.ndbi_mean:.3f}" if indices.ndbi_mean is not None else "—")
                        for note in indices.notes:
                            st.caption(note)
                        st.info("Single-date optical indices only; 90/180-day search does not yet create a multi-date composite. NDVI/NDBI are not land-cover percentages or thermal observations.")
        card("Environmental layer guide", '<div class="cf-caption"><strong>Observed LST</strong> — blue/cyan cooler, yellow/red warmer; scene-relative display range in °C.</div>'
             '<div class="cf-caption"><strong>NDVI</strong> — brown/cream (lower values), green (higher values); fixed −1 to +1 scale.</div>'
             '<div class="cf-caption"><strong>NDBI</strong> — teal/cream (lower values), brown (higher values); fixed −1 to +1 scale.</div>'
             '<div class="cf-caption">Toggle overlays using the map layer selector. NDVI and NDBI do not identify surface-cover classes. Displayed pixels are not intervention effects.</div>')

    with aside:
        boundary = st.session_state.get("boundary_info")
        if boundary is not None:
            area_text = f"{boundary.area_m2:,.1f} m² ({boundary.area_m2 / 10_000:,.3f} ha)"
            geometry_details = (
                f'<div class="cf-metric-label">Site perimeter</div><div class="cf-note">{boundary.perimeter_m:,.1f} m</div>'
                f'<div class="cf-metric-label">Centroid · WGS84</div><div class="cf-note">'
                f'{boundary.latitude:.6f}, {boundary.longitude:.6f}</div>'
                f'<div class="cf-metric-label">Boundary vertices</div><div class="cf-note">{boundary.vertex_count}</div>'
            )
        else:
            area_text = "—"
            geometry_details = '<div class="cf-caption">Draw one boundary in the map workspace to display area and coordinates.</div>'
        card("Site information", f'<div class="cf-eyebrow">{site_kind_safe}</div><div class="cf-scenario-name">{site_title_safe}</div><div class="cf-caption">{site_note_safe}</div><div class="cf-divider"></div><div class="cf-metric-label">Site area</div><div class="cf-metric-value">{area_text}</div>{geometry_details}<div class="cf-divider"></div><div class="cf-metric-label">Analysis buffer</div><div class="cf-note">{analysis_buffer_m} m · context only</div>')
        active_lst = st.session_state.get("landsat_temperature_result")
        if active_lst is not None and active_lst.status == "SITE_QA_PASS":
            card("Observed LST layer", f'<div class="cf-metric-label">Acquisition UTC</div><div class="cf-note">{active_lst.observed_utc}</div>'
                 f'<div class="cf-metric-label">Mean site LST</div><div class="cf-metric-value">{active_lst.mean_c:.1f} °C</div>'
                 f'<div class="cf-note">Landsat C2 L2; 30 m delivery grid, ~100 m native thermal support. Map layer is toggleable.</div>')
        else:
            card("Temperature layer", '<div class="cf-muted-block"><strong>Observed LST not computed</strong><span>Discover Landsat, assess QA, then calculate LST.</span></div>')
        current_thermal_qa = st.session_state.get("landsat_qa_result")
        current_optical = st.session_state.get("sentinel2_indices")
        current_ld = st.session_state.get("landsat_discovery_result")
        current_sd = st.session_state.get("sentinel2_discovery")
        q_parts = []
        if current_ld and current_ld.candidate:
            c = current_ld.candidate
            q_parts.append(f'<div class="cf-metric-label">Landsat observation</div><div class="cf-note">{html_std.escape(c.observed_utc[:10])} · {c.age_days} days · {c.scene_cloud_pct:.1f}% scene cloud</div>')
        if current_thermal_qa:
            q_parts.append(f'<div class="cf-metric-label">Landsat site-level QA</div><div class="cf-note">{html_std.escape(current_thermal_qa.status)} · {current_thermal_qa.site.valid_pixels}/{current_thermal_qa.site.footprint_pixels} delivery pixels · {current_thermal_qa.site.coverage_pct}% valid</div>')
        if current_sd and current_sd.candidate:
            c = current_sd.candidate
            q_parts.append(f'<div class="cf-metric-label">Sentinel-2 observation</div><div class="cf-note">{html_std.escape(c.observed_utc[:10])} · {c.age_days} days · {c.scene_cloud_pct:.1f}% scene cloud</div>')
        if current_optical:
            q_parts.append(f'<div class="cf-metric-label">Sentinel-2 site-level QA</div><div class="cf-note">{html_std.escape(current_optical.status)} · {current_optical.valid_pixels}/{current_optical.footprint_pixels} delivery pixels · {current_optical.valid_coverage_pct}% valid</div>')
        q_parts.append('<div class="cf-caption">LST: 30 m delivery grid, approximately 100 m native thermal support. Optical indices: 20 m grid. Separate acquisition dates; no predictive model or land-cover classification.</div>')
        card("Data and quality", ''.join(q_parts) if q_parts else '<div class="cf-muted-block">Run Landsat and Sentinel-2 acquisition and QA to populate this panel.</div>')
    html('<div class="cf-section-head"><div class="cf-subheading">Observed environmental indicators</div><div class="cf-caption">Values are shown only after successful satellite processing. Landsat and Sentinel-2 observations have different dates and spatial supports.</div></div>')
    m1, m2, m3, m4 = st.columns(4)
    active_lst = st.session_state.get("landsat_temperature_result")
    optical_summary = st.session_state.get("sentinel2_indices")
    observed_ok = active_lst is not None and active_lst.status == "SITE_QA_PASS"
    optical_ok = optical_summary is not None and optical_summary.status == "PRELIMINARY_QA_PASS"
    with m1: metric("Mean observed LST", f"{active_lst.mean_c:.1f} °C" if observed_ok else "—", "Landsat overpass · " + active_lst.observed_utc[:10] if observed_ok else "Awaiting LST assessment")
    with m2: metric("95th-percentile LST", f"{active_lst.p95_c:.1f} °C" if observed_ok else "—", "Delivery-grid estimate; ~100 m native thermal support" if observed_ok else "Awaiting LST assessment")
    with m3: metric("Mean NDVI", f"{optical_summary.ndvi_mean:.3f}" if optical_ok else "—", "Sentinel-2 · " + optical_summary.observed_utc[:10] if optical_ok else "Awaiting optical assessment")
    with m4: metric("Mean NDBI", f"{optical_summary.ndbi_mean:.3f}" if optical_ok else "—", "Sentinel-2 · not built-up percentage" if optical_ok else "Awaiting optical assessment")
    st.caption("Observed satellite indicators only. No hot-area threshold, tree-canopy percentage, thermal comfort, or predicted cooling has been calculated.")

# Site-specific option state: a different geographical boundary creates a fresh
# option workspace. Buffer-only changes must not affect design-option names.
_current_design_boundary = st.session_state.get("boundary_info")
_design_site_signature = (_site_json.dumps(_current_design_boundary.geometry, sort_keys=True)
                          if _current_design_boundary is not None else None)
if st.session_state.get("design_site_signature") != _design_site_signature:
    st.session_state["design_site_signature"] = _design_site_signature
    st.session_state["design_options"] = ([new_option("Option A · Untitled design")]
                                          if _design_site_signature is not None else [])
    st.session_state.pop("editing_intervention_id", None)
    st.session_state.pop("pending_design_delete", None)
    st.session_state.pop("design_option_selector", None)
    st.session_state["selected_design_id"] = (st.session_state["design_options"][0]["id"]
                                               if st.session_state["design_options"] else None)

with t2:
    st.write("")
    html('<div class="cf-subheading">Design Options</div><div class="cf-intro">Manage independent design alternatives for the selected site. Draw point trees and polygon interventions within the active site. Quantities are geometric only; cooling predictions remain disabled.</div>')
    if _design_site_signature is None:
        st.info("Define a site boundary in Existing Site before creating design options.")
    else:
        options = st.session_state["design_options"]
        option_ids = [item["id"] for item in options]
        selected_id = st.session_state.get("selected_design_id")
        if selected_id not in option_ids:
            selected_id = option_ids[0] if option_ids else None
            st.session_state["selected_design_id"] = selected_id
        if st.session_state.get("edit_option_owner") != selected_id:
            st.session_state.pop("editing_intervention_id", None)
            st.session_state["edit_option_owner"] = selected_id
        if options:
            selected_id = st.selectbox(
                "Active design option", options=option_ids,
                index=option_ids.index(selected_id),
                format_func=lambda oid: next(x["name"] for x in options if x["id"] == oid),
                key="design_option_selector",
            )
            if st.session_state.get("edit_option_owner") != selected_id:
                st.session_state.pop("editing_intervention_id", None)
                st.session_state["edit_option_owner"] = selected_id
            st.session_state["selected_design_id"] = selected_id
            active_option = next(x for x in options if x["id"] == selected_id)
        else:
            st.info("No design options yet. Create an option to begin.")
            active_option = None
        with st.expander("Create a new design option", expanded=not options):
            with st.form("design_create_form", clear_on_submit=True):
                name_new = st.text_input("New option name", value="", max_chars=64,
                                         placeholder="e.g., Green courtyard")
                create_submitted = st.form_submit_button("Create option", disabled=len(options) >= MAX_OPTIONS)
            if create_submitted:
                try:
                    updated, new_id = add_option(options, name_new)
                    st.session_state["design_options"] = updated
                    st.session_state["selected_design_id"] = new_id
                    st.session_state.pop("design_option_selector", None)
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))
        if active_option is not None:
            with st.form(f"rename_design_{selected_id}"):
                name_edited = st.text_input("Option name", value=active_option["name"], max_chars=64)
                rename_submitted = st.form_submit_button("Save name")
            if rename_submitted:
                try:
                    st.session_state["design_options"] = rename_option(options, selected_id, name_edited)
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))
            actions_left, actions_right = st.columns(2)
            with actions_left:
                if st.button("Duplicate option", key="duplicate_design", use_container_width=True,
                             disabled=len(options) >= MAX_OPTIONS):
                    try:
                        updated, new_id = duplicate_option(options, selected_id)
                        st.session_state["design_options"] = updated
                        st.session_state["selected_design_id"] = new_id
                        st.rerun()
                    except ValueError as exc:
                        st.error(str(exc))
            with actions_right:
                if st.button("Delete option", key="request_delete_design", use_container_width=True):
                    st.session_state["pending_design_delete"] = selected_id
            if st.session_state.get("pending_design_delete") == selected_id:
                st.warning(f"Delete '{active_option['name']}'? This cannot be undone within this session.")
                confirm_col, cancel_col = st.columns(2)
                with confirm_col:
                    if st.button("Confirm delete", key="confirm_design_delete", type="primary"):
                        updated, new_selected = delete_option(options, selected_id)
                        st.session_state["design_options"] = updated
                        st.session_state["selected_design_id"] = new_selected
                        st.session_state.pop("design_option_selector", None)
                        st.session_state.pop("pending_design_delete", None)
                        st.rerun()
                with cancel_col:
                    if st.button("Cancel", key="cancel_design_delete"):
                        st.session_state.pop("pending_design_delete", None)
                        st.rerun()
        st.caption(f"{len(options)} of {MAX_OPTIONS} design options · Stored in this Streamlit session only · Intervention drawing available")
    left, right = st.columns([1.02, 1.58], gap="large")
    with left:
        html('<div class="cf-eyebrow">Increment 5C · Spatial interventions</div>')
        st.caption("Select the active design option, choose the intervention type, then draw one geometry at a time on the design map. Interventions must remain entirely within the site.")
        chosen_kind = st.selectbox("Intervention type", list(INTERVENTION_TYPES), key="design_intervention_kind")
        expected_draw = INTERVENTION_TYPES[chosen_kind]
        st.caption("Use the marker tool for a tree point." if expected_draw == "point" else
                   "Use the polygon or rectangle tool to delineate the proposed intervention area.")
        if _design_site_signature and active_option is not None:
            proposed = active_option["interventions"]
            totals = summarize_interventions(proposed)
            st.metric("Proposed tree locations", totals["trees"])
            st.metric("Total drawn polygon area", f'{totals["total_polygon_m2"]:,.1f} m²')
            st.metric("Unique ground-treatment area", f'{totals["exclusive_surface_union_m2"]:,.1f} m²')
            st.caption("Ground treatments are mutually exclusive. Shade structures may overlap surfaces; tree markers do not imply canopy area. No cooling benefit estimated.")
            st.caption("Ground-treatment areas by type: " + " · ".join(
                f'{name}: {value:,.1f} m²' for name, value in totals["areas_by_type"].items() if value > 0) if any(totals["areas_by_type"].values()) else "No ground-surface polygons yet.")
            old_conflicts = find_surface_conflicts(proposed)
            if old_conflicts:
                st.warning(f"{len(old_conflicts)} pre-existing incompatible ground-surface overlaps detected. Edit or remove them before adding new overlapping treatments.")
            st.write(f'**{totals["count"]} interventions** in this option (maximum {MAX_INTERVENTIONS}).')
            editing_id = st.session_state.get("editing_intervention_id")
            if editing_id and not any(x["id"] == editing_id for x in proposed):
                st.session_state.pop("editing_intervention_id", None)
                editing_id = None
            for entry in proposed:
                label = (f'{entry["type"]} · point' if entry["tree_count"] else
                         f'{entry["type"]} · {entry["area_m2"]:,.1f} m²')
                a, b, c = st.columns([2.8, 1, 1])
                with a:
                    st.caption(label)
                with b:
                    if st.button("Edit", key=f'edit_intervention_{selected_id}_{entry["id"]}',
                                 disabled=bool(editing_id and editing_id != entry["id"])):
                        st.session_state["editing_intervention_id"] = entry["id"]
                        st.session_state["design_map_generation"] = st.session_state.get("design_map_generation",0) + 1
                        st.rerun()
                with c:
                    if st.button("Remove", key=f'remove_intervention_{selected_id}_{entry["id"]}'):
                        if st.session_state.get("editing_intervention_id") == entry["id"]:
                            st.session_state.pop("editing_intervention_id", None)
                        st.session_state["design_options"] = remove_intervention(
                            st.session_state["design_options"], selected_id, entry["id"])
                        st.session_state["design_map_generation"] = st.session_state.get("design_map_generation", 0) + 1
                        st.rerun()
        else:
            st.info("Create and select an option before drawing interventions.")
    with right:
        card("Selected site · shared boundary", boundary_preview_svg(st.session_state.get("boundary_info")) +
             '<div class="cf-caption">Intervention geometry is checked against this site boundary.</div>')
        current_name = html_std.escape(active_option["name"]) if _design_site_signature and active_option is not None else "No option selected"
        html(f'<div class="cf-quiet"><strong>Active option:</strong> {current_name} · Geometric design proposals only, no modeled cooling or cost.</div>')
        if _design_site_signature and active_option is not None:
            design_boundary = st.session_state["boundary_info"]
            editing_id = st.session_state.get("editing_intervention_id")
            editing_entry = next((x for x in active_option["interventions"] if x["id"] == editing_id), None)
            if editing_id and editing_entry is None:
                st.session_state.pop("editing_intervention_id", None)
                editing_id = None
            # The intervention Draw group is separate from the Existing Site map's
            # editable site-boundary group. Existing designs are read-only on this
            # map and can be individually removed using the list at left.
            design_map = folium.Map(
                location=[design_boundary.latitude, design_boundary.longitude],
                zoom_start=17, tiles="OpenStreetMap", control_scale=True,
            )
            west, south, east, north = design_boundary.bounds
            design_map.fit_bounds([[south, west], [north, east]])
            folium.GeoJson(design_boundary.geometry, name="Project site boundary",
                style_function=lambda _: {"color":"#087c6e","weight":3,"fillOpacity":0.04}).add_to(design_map)
            for entry in active_option["interventions"]:
                if entry["id"] == editing_id:
                    continue
                color = INTERVENTION_COLORS[entry["type"]]
                geometry = entry["geometry"]
                if entry["tree_count"]:
                    lon, lat = geometry["coordinates"][:2]
                    folium.CircleMarker([lat, lon], radius=6, color=color, fill=True,
                                        fill_opacity=0.9, tooltip=entry["type"]).add_to(design_map)
                else:
                    folium.GeoJson(geometry, name=entry["type"],
                                   style_function=lambda _, color=color: {
                                       "color":color, "weight":2, "fillColor":color, "fillOpacity":0.35},
                                   tooltip=entry["type"]).add_to(design_map)
            draw_group = folium.FeatureGroup(name="Editable intervention" if editing_entry else "New intervention drawing")
            draw_group.add_to(design_map)
            if editing_entry is not None:
                editable_geom = editing_entry["geometry"]
                edit_color = INTERVENTION_COLORS[editing_entry["type"]]
                if editing_entry["tree_count"]:
                    lon, lat = editable_geom["coordinates"][:2]
                    folium.Marker([lat, lon], tooltip="Drag this tree marker, then click Save on toolbar").add_to(draw_group)
                else:
                    rings = editable_geom["coordinates"]
                    locations = [[(float(pt[1]), float(pt[0])) for pt in ring] for ring in rings]
                    folium.Polygon(locations=locations[0] if len(locations) == 1 else locations,
                                   color=edit_color, weight=3, fill=True, fill_opacity=0.35).add_to(draw_group)
            Draw(feature_group=draw_group, position="topleft", export=False,
                 draw_options={"polyline":False, "circle":False,"circlemarker":False,
                               "marker":expected_draw == "point" if editing_entry is None else False,
                               "polygon":{"allowIntersection":False} if expected_draw == "polygon" and editing_entry is None else False,
                               "rectangle":expected_draw == "polygon" if editing_entry is None else False},
                 edit_options={"edit":True,"remove":editing_entry is None}).add_to(design_map)
            folium.LayerControl(collapsed=True).add_to(design_map)
            map_key = (f'design_map_{selected_id}_{chosen_kind}_'
                       f'{st.session_state.get("design_map_generation",0)}')
            drawn_response = st_folium(design_map, height=460, width=None,
                                     use_container_width=True, key=map_key,
                                     returned_objects=["all_drawings"])
            pending_drawings = drawn_response.get("all_drawings") if isinstance(drawn_response, dict) else None
            if editing_entry is not None:
                st.info("Editing saved intervention. Use the toolbar pencil, drag vertices or marker, then click the toolbar Save button. Finally click Apply edited geometry below.")
                apply_col, cancel_col = st.columns(2)
                with apply_col:
                    if st.button("Apply edited geometry", key="apply_intervention_edit"):
                        if not isinstance(pending_drawings, list) or len(pending_drawings) != 1:
                            st.warning("Exactly one edited shape must be present. Use the pencil and Save controls on the map first.")
                        else:
                            try:
                                st.session_state["design_options"] = replace_intervention(
                                    st.session_state["design_options"], selected_id, editing_id,
                                    pending_drawings[0], design_boundary.geometry)
                                st.session_state.pop("editing_intervention_id", None)
                                st.session_state["design_map_generation"] = st.session_state.get("design_map_generation",0) + 1
                                st.rerun()
                            except (ValueError, TypeError, KeyError) as exc:
                                st.error(f"Edited geometry not accepted: {exc}")
                with cancel_col:
                    if st.button("Cancel geometry edit", key="cancel_intervention_edit"):
                        st.session_state.pop("editing_intervention_id", None)
                        st.session_state["design_map_generation"] = st.session_state.get("design_map_generation",0) + 1
                        st.rerun()
            elif pending_drawings:
                if len(pending_drawings) > 1:
                    st.warning("Save one drawing at a time. Remove extra new shapes using the drawing toolbar.")
                else:
                    try:
                        candidate = make_intervention(pending_drawings[0], chosen_kind,
                                                       design_boundary.geometry)
                        st.session_state["design_options"] = append_intervention_checked(
                            st.session_state["design_options"], selected_id, candidate)
                        st.session_state["design_map_generation"] = st.session_state.get("design_map_generation",0) + 1
                        st.rerun()
                    except (ValueError, TypeError, KeyError) as exc:
                        st.warning(f"Intervention not accepted: {exc}")
                        st.caption("Use the map edit/delete controls or remove the drawing and redraw it.")
            st.caption("Use Edit beside a saved intervention to change its geometry. Ground-surface treatments cannot overlap one another; shade and trees may overlap them. The original site boundary is unchanged.")
        else:
            st.info("Define a site in Existing Site and create an option to activate the design map.")
        card("Scientific status", '<div class="cf-muted-block">Intervention geometry and quantities only. Cooling predictions and costs remain disabled.</div>')

with t3:
    st.write("")
    html('<div class="cf-subheading">Compare Options</div><div class="cf-intro">Review a consistent existing-versus-design comparison, followed by evaluation metrics and reporting controls.</div>')
    _comparison_names = [html_std.escape(item["name"]) for item in st.session_state.get("design_options", [])]
    html('<div class="cf-viewbar"><span class="cf-view cf-view-active">Existing site</span>' +
         ''.join(f'<span class="cf-view">{name}</span>' for name in _comparison_names) + '</div>')
    card("Project site · shared across all tabs", boundary_preview_svg(st.session_state.get("boundary_info")) +
         '<div class="cf-caption">The same active site boundary is retained here. '
         'Scenario diagrams below are conceptual placeholders, not maps of this geometry.</div>')
    p1,p2,p3=st.columns(3,gap="medium")
    with p1: card("Existing Site · Baseline",site_illustration("base")+'<div class="cf-caption">Conceptual reference — no observed thermal raster</div>')
    with p2: card("Illustrative green design",site_illustration("green")+'<div class="cf-caption">Conceptual only; not a managed option or computed result</div>')
    with p3: card("Illustrative cool-surface design",site_illustration("cool")+'<div class="cf-caption">Conceptual only; not a managed option or computed result</div>')
    html('<div class="cf-quiet">All three plans are schematic. They are not georeferenced site maps, thermal predictions, or comparative environmental findings.</div>')
    html('<div class="cf-section-head"><div class="cf-subheading">Comparative indicators</div><div class="cf-caption">Final values will only be displayed when the scientific engine is connected and validated.</div></div>')
    c1,c2,c3,c4=st.columns(4)
    with c1: metric("Mean temperature change")
    with c2: metric("Hot-area reduction")
    with c3: metric("Area improved")
    with c4: metric("Indicative cost")
    wider,smaller=st.columns([1.7,1],gap="large")
    with wider:
        card("Scenario performance · chart area",'<div class="cf-muted-block" style="min-height:200px"><strong>Comparison chart placeholder</strong><span>Existing baseline versus selected design alternatives</span><span>No numerical values generated</span></div>')
    with smaller:
        card("Reports and exports · planned",'<div class="cf-outputrow"><span class="cf-action">PDF report</span><span class="cf-action">PNG comparison</span><span class="cf-action">CSV results</span><span class="cf-action">Method note</span></div><div class="cf-divider"></div><div class="cf-caption">All export controls are visual placeholders.</div>')
        card("Scientific interpretation",'<div class="cf-caption">Future reports will distinguish observed satellite inputs, modelled temperature patterns, predicted intervention effects and associated uncertainty.</div>')

html('<div class="cf-footer">ClimaForma v2.4.21 · Increment 5C · Observed Landsat LST and Sentinel-2 indices; cooling predictions disabled · Not suitable for environmental, engineering or investment decisions</div>')
