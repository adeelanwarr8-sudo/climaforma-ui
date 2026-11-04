"""ClimaForma v2.4 — Increment 3: bounded vector data acquisition.

Project selection, map navigation and single site-boundary geometry are active.
Satellite imagery analysis, science engine and intervention functions remain disabled.
"""

import html as html_std

import streamlit as st
import folium
from folium.plugins import Draw, Fullscreen, MousePosition
from streamlit_folium import st_folium
from site_mapping import (BoundaryInfo, SHOWCASE_CENTERS, DEFAULT_CENTER,
                          boundary_from_drawings, same_boundary, boundary_preview_svg)
from geo_data import fetch_osm_buildings, process_geojson_bytes

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
SHOWCASES = ("Stockholm · Södermalm", "Barcelona · Eixample", "Vienna · Neubau")


def selected_site_summary(mode: str, showcase: str, address: str) -> tuple[str, str, str]:
    """Pure presentation helper; does not resolve addresses or coordinates."""
    if mode == "Showcase site":
        return showcase, "Showcase location · site boundary is defined by your drawing", "Selected showcase"
    if mode == "Address lookup":
        return (address.strip() or "No address entered"), "Address draft only · not geocoded", "Address draft"
    return "Boundary not drawn", "Draw or edit the boundary directly on the map", "Boundary workflow"


with st.sidebar:
    html('<div class="cf-brand">◈ ClimaForma</div><div class="cf-brandline">Climate-responsive design intelligence</div>')
    html('<span class="cf-pill">V2.4.2 · INCREMENT 3</span>')
    st.divider()
    html('<div class="cf-step">01 · Project information</div>')
    st.text_input("Project name", value="Untitled climate design study", key="project_name", max_chars=100,
                  help="The name is stored only in the current Streamlit session.")
    st.caption("New design assessment · Session-local draft")
    st.divider()
    html('<div class="cf-step">02 · Site selection</div>')
    site_mode = st.selectbox("Site mode", SITE_MODES, key="site_mode")
    if site_mode == "Showcase site":
        showcase_city = st.selectbox("Showcase city", SHOWCASES, key="showcase_city")
        address_draft = ""
        st.caption("Selecting a city does not load imagery or coordinates.")
    elif site_mode == "Address lookup":
        showcase_city = SHOWCASES[0]
        address_draft = st.text_input("Address or place (draft)", key="address_draft", max_chars=180,
                                      placeholder="City, street or place")
        st.caption("Text entry only. No address search or geocoding yet.")
    else:
        showcase_city = SHOWCASES[0]
        address_draft = ""
        st.info("Go to Existing Site → draw one polygon or rectangle on the map. Use the edit/delete toolbar to adjust it.")
    st.divider()
    html('<div class="cf-step">03 · Analysis settings</div>')
    st.slider("Analysis buffer (m)", 300, 1000, 500, 100, disabled=True)
    st.number_input("Hot surface threshold (°C)", value=43.0, disabled=True)
    st.divider()
    html('<div class="cf-step">04 · Application status</div>')
    html('<div class="cf-quiet"><strong>Increment 3 active</strong><div class="cf-caption">Site drawing and optional polygon-layer acquisition are available. Satellite processing and scientific models remain disconnected.</div></div>')
    st.caption("ClimaForma v2.4.2 · Increment 3")

# A changed showcase/location mode resets the site boundary so it cannot be
# accidentally attributed to another city. Address entry is NOT geocoded.
map_context = (site_mode, showcase_city if site_mode == "Showcase site" else None)
if st.session_state.get("map_context") != map_context:
    st.session_state["map_context"] = map_context
    st.session_state["boundary_info"] = None
    st.session_state["vector_layer"] = None
    st.session_state["map_drawings_seen"] = False
    st.session_state["map_generation"] = st.session_state.get("map_generation", 0) + 1

map_center = SHOWCASE_CENTERS.get(showcase_city, DEFAULT_CENTER) if site_mode == "Showcase site" else DEFAULT_CENTER


def build_site_map(center: tuple[float, float, int], boundary: BoundaryInfo | None) -> folium.Map:
    """Make a navigation/drawing map. No basemap data are used in calculations."""
    latitude, longitude, zoom = center
    m = folium.Map(location=[latitude, longitude], zoom_start=zoom, tiles=None, control_scale=True)
    folium.TileLayer(tiles="OpenStreetMap", name="Street map", show=True).add_to(m)
    folium.TileLayer(
        tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        name="Aerial imagery", attr="Tiles © Esri and contributors", show=False,
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
html(f'<div class="cf-quiet"><strong>Project:</strong> {project_label_safe} &nbsp; · &nbsp; <strong>Site:</strong> {site_title_safe} &nbsp; · &nbsp; Interactive site mapping only · No environmental analysis</div>')

t1, t2, t3 = st.tabs(["01  Existing Site", "02  Design Options", "03  Compare Options"])

with t1:
    st.write("")
    html('<div class="cf-subheading">Existing Site</div><div class="cf-intro">Review site context, environmental layers, and baseline information before evaluating possible interventions.</div>')
    main, aside = st.columns([2.15, 1], gap="large")
    with main:
        html('<div class="cf-eyebrow">Site workspace</div>')
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
        html('<div class="cf-toolbar"><div class="cf-minihead">Map tools · active</div><span class="cf-chip">Zoom / pan</span><span class="cf-chip">Draw polygon / rectangle</span><span class="cf-chip">Edit / delete</span><span class="cf-chip">Street / aerial basemap</span><div class="cf-caption">Coordinates are WGS84 (EPSG:4326); areas are WGS84 geodesic measurements. No temperature or land-cover analysis.</div></div>')
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
        card("Surface-cover categories", '<div class="cf-legend"><i class="cf-dot" style="background:#8faba6"></i>Building</div><div class="cf-legend"><i class="cf-dot" style="background:#c6c0b2"></i>Paved surfaces</div><div class="cf-legend"><i class="cf-dot" style="background:#559a74"></i>Tree canopy</div><div class="cf-legend"><i class="cf-dot" style="background:#a8c9a2"></i>Grass / planting</div><div class="cf-legend"><i class="cf-dot" style="background:#86bfc7"></i>Water</div><div class="cf-legend"><i class="cf-dot" style="background:#cfb99c"></i>Bare soil</div><div class="cf-caption">Legend illustrates planned categories; no land-cover classification has been performed.</div>')
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
        card("Site information", f'<div class="cf-eyebrow">{site_kind_safe}</div><div class="cf-scenario-name">{site_title_safe}</div><div class="cf-caption">{site_note_safe}</div><div class="cf-divider"></div><div class="cf-metric-label">Site area</div><div class="cf-metric-value">{area_text}</div>{geometry_details}<div class="cf-divider"></div><div class="cf-metric-label">Analysis period</div><div class="cf-metric-value">—</div>')
        card("Temperature layer", '<div class="cf-muted-block"><strong>Temperature map placeholder</strong><span>Not connected to satellite observations</span></div><div class="cf-caption">Future display: temperature scale, date and source resolution.</div>')
        card("Data and quality", '<div class="cf-muted-block">Satellite sources, coverage and model status will appear here.</div>')
    html('<div class="cf-section-head"><div class="cf-subheading">Baseline indicators</div><div class="cf-caption">Proposed metric locations. No values have been calculated.</div></div>')
    m1, m2, m3, m4 = st.columns(4)
    with m1: metric("Mean surface temperature")
    with m2: metric("95th-percentile temperature")
    with m3: metric("Hot-area proportion")
    with m4: metric("Tree canopy coverage")

with t2:
    st.write("")
    html('<div class="cf-subheading">Design Options</div><div class="cf-intro">Review the future configuration workflow for landscape, surface materials and built shade. Scientific and design controls are currently disabled.</div>')
    head1,head2,head3=st.columns([1.2,1.4,1])
    with head1: st.selectbox("Option being reviewed",["Option A · Green courtyard","Option B · Cool surfaces"],disabled=True)
    with head2: st.text_input("Option name",value="Option A · Green courtyard",disabled=True)
    with head3:
        html('<div class="cf-minihead">Option actions · preview</div><span class="cf-chip">＋ New</span><span class="cf-chip">Copy</span><span class="cf-chip">Delete</span>')
    left,right=st.columns([1.02,1.58],gap="large")
    with left:
        html('<div class="cf-eyebrow">01 · Intervention presets</div>')
        st.selectbox("Design template",["Green courtyard","Cool paving","Tree-lined streets","Custom design"],disabled=True)
        html('<div class="cf-divider"></div><div class="cf-eyebrow">02 · Vegetation and landscape</div>')
        st.slider("Additional tree canopy (% of site)",0,40,20,disabled=True)
        st.slider("Grass / planting (% of site)",0,40,15,disabled=True)
        st.slider("Water feature (% of site)",0,10,0,disabled=True)
        html('<div class="cf-divider"></div><div class="cf-eyebrow">03 · Materials and surface treatments</div>')
        st.slider("Reflective / cool paving (% of site)",0,100,25,disabled=True)
        st.slider("Permeable paving (% of site)",0,80,10,disabled=True)
        html('<div class="cf-divider"></div><div class="cf-eyebrow">04 · Shade and built interventions</div>')
        st.slider("Shade structures (% of site)",0,60,10,disabled=True)
        st.slider("Cool roof treatment (% of roof)",0,100,0,disabled=True)
    with right:
        html('<div class="cf-eyebrow">Design canvas</div><div class="cf-intro">Option A · Green courtyard — conceptual layout only</div>')
        card("Selected site · shared boundary", boundary_preview_svg(st.session_state.get("boundary_info")) +
             '<div class="cf-caption">This is the selected site geometry from Existing Site. '
             'Design interventions remain illustrative and disabled.</div>')
        html(site_illustration("green"))
        card("Sketch tools · planned", '<div class="cf-viewbar"><span class="cf-view">Tree canopy</span><span class="cf-view">Planting polygon</span><span class="cf-view">Cool paving</span><span class="cf-view">Water</span><span class="cf-view">Shade</span><span class="cf-view">Erase</span></div><div class="cf-muted-block">Future map drawing and DXF / GeoJSON import workspace<br><strong>No drawing, upload or editing is enabled</strong></div>')
        card("Design summary · illustrative", '<div class="cf-bar-row"><div class="cf-bar-name">Tree canopy</div><div class="cf-bar-track"><div class="cf-bar-fill" style="width:62%"></div></div></div><div class="cf-bar-row"><div class="cf-bar-name">Vegetation</div><div class="cf-bar-track"><div class="cf-bar-fill" style="width:48%"></div></div></div><div class="cf-bar-row"><div class="cf-bar-name">Cool materials</div><div class="cf-bar-track"><div class="cf-bar-fill" style="width:35%"></div></div></div><div class="cf-caption">Decorative bars. Not intervention quantities or calculated results.</div>')
        card("Scientific status",'<div class="cf-muted-block">Predicted cooling, surface-temperature change, uncertainty and cost metrics are not available in this UI-only release.</div>')

with t3:
    st.write("")
    html('<div class="cf-subheading">Compare Options</div><div class="cf-intro">Review a consistent existing-versus-design comparison, followed by evaluation metrics and reporting controls.</div>')
    html('<div class="cf-viewbar"><span class="cf-view cf-view-active">Existing site</span><span class="cf-view">Option A · Green courtyard</span><span class="cf-view">Option B · Cool surfaces</span></div>')
    card("Project site · shared across all tabs", boundary_preview_svg(st.session_state.get("boundary_info")) +
         '<div class="cf-caption">The same active site boundary is retained here. '
         'Scenario diagrams below are conceptual placeholders, not maps of this geometry.</div>')
    p1,p2,p3=st.columns(3,gap="medium")
    with p1: card("Existing Site · Baseline",site_illustration("base")+'<div class="cf-caption">Conceptual reference — no observed thermal raster</div>')
    with p2: card("Option A · Green courtyard",site_illustration("green")+'<div class="cf-caption">Illustrative vegetation intervention</div>')
    with p3: card("Option B · Cool surfaces",site_illustration("cool")+'<div class="cf-caption">Illustrative material intervention</div>')
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

html('<div class="cf-footer">ClimaForma v2.4.2 · Increment 3 · Project and site drafts active; scientific controls disabled · Not suitable for environmental, engineering or investment decisions</div>')
