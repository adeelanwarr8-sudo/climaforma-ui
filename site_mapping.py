"""ClimaForma Increment 2: site-boundary geometry and map configuration only.

All input geometries use GeoJSON longitude/latitude coordinates (EPSG:4326).
Areas are computed geodesically on WGS84, never from degree-squared areas.
No environmental or scientific modelling is performed.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

from pyproj import Geod
from shapely.geometry import shape
from shapely.validation import explain_validity

GEOD = Geod(ellps="WGS84")
SHOWCASE_CENTERS = {
    "Stockholm · Södermalm": (59.315, 18.075, 14),
    "Barcelona · Eixample": (41.391, 2.164, 14),
    "Vienna · Neubau": (48.202, 16.348, 14),
}
DEFAULT_CENTER = SHOWCASE_CENTERS["Stockholm · Södermalm"]
MAX_AREA_M2 = 25_000_000  # Bound the mapping pilot to reasonable sites (25 km²).
MIN_AREA_M2 = 1.0


@dataclass(frozen=True)
class BoundaryInfo:
    geometry: dict
    area_m2: float
    perimeter_m: float
    latitude: float
    longitude: float
    vertex_count: int
    bounds: tuple[float, float, float, float]


def parse_boundary(feature: dict) -> BoundaryInfo:
    """Validate a single polygon/rectangle from Folium Draw and measure geodesically."""
    if not isinstance(feature, dict):
        raise ValueError("A GeoJSON feature is required.")
    geometry = feature.get("geometry") if feature.get("type") == "Feature" else feature
    if not isinstance(geometry, dict) or geometry.get("type") != "Polygon":
        raise ValueError("Draw a polygon or rectangle, not a point or line.")
    polygon = shape(geometry)
    if polygon.is_empty or not polygon.is_valid:
        raise ValueError(f"Invalid boundary: {explain_validity(polygon)}")
    min_lon, min_lat, max_lon, max_lat = polygon.bounds
    coords = [n for ring in geometry.get("coordinates", []) for pt in ring for n in pt]
    if not coords or not all(isinstance(x, (int, float)) and math.isfinite(x) for x in coords):
        raise ValueError("Coordinates must be finite numbers.")
    if min_lon < -180 or max_lon > 180 or min_lat < -90 or max_lat > 90:
        raise ValueError("Boundary coordinates are outside WGS84 longitude/latitude limits.")
    if max_lon - min_lon > 180:
        raise ValueError("Boundaries crossing the date line are not supported in this increment.")
    area, perimeter = GEOD.geometry_area_perimeter(polygon)
    area = abs(area)
    if not math.isfinite(area) or area < MIN_AREA_M2:
        raise ValueError("Site boundary is too small or degenerate.")
    if area > MAX_AREA_M2:
        raise ValueError("Site boundary exceeds the 25 km² limit for this mapping prototype.")
    center = polygon.centroid
    return BoundaryInfo(
        geometry={"type": "Polygon", "coordinates": geometry["coordinates"]},
        area_m2=area, perimeter_m=perimeter,
        latitude=center.y, longitude=center.x,
        vertex_count=len(polygon.exterior.coords) - 1,
        bounds=(min_lon, min_lat, max_lon, max_lat),
    )


def boundary_from_drawings(drawings: object) -> BoundaryInfo | None:
    """Read the whole Draw feature-group; reject multi-boundary selections.

    None means the map has not returned a drawing event. An empty list means
    the user deleted the drawn shape via Leaflet's delete toolbar.
    """
    if drawings is None:
        return None
    if not isinstance(drawings, list):
        raise ValueError("Unexpected drawing response from map component.")
    if len(drawings) > 1:
        raise ValueError("Only one site is allowed. Delete extra polygons on the map.")
    return parse_boundary(drawings[0]) if drawings else None


def same_boundary(left: BoundaryInfo | None, right: BoundaryInfo | None) -> bool:
    if left is None or right is None:
        return left is right
    return left.geometry == right.geometry



def replacement_candidate(drawings: object, active: BoundaryInfo | None) -> BoundaryInfo | None:
    """Identify a newly drawn second boundary, without committing it.

    A separate explicit confirmation in the UI is required before replacing the
    existing site. Two shapes are only allowed transiently in the editor.
    """
    if not isinstance(drawings, list) or len(drawings) != 2 or active is None:
        return None
    candidates = [parse_boundary(item) for item in drawings]
    # Drawing toolbar appends new layers; select the shape that is different
    # from the current saved site. If both differ (concurrent edit), use last.
    differing = [item for item in candidates if not same_boundary(item, active)]
    return differing[-1] if differing else None


def boundary_preview_svg(boundary: BoundaryInfo | None) -> str:
    """Return a static SVG of the *actual selected geometry*, never a basemap.

    The map is illustrative and has no environmental layers; only geometric
    outline is projected into a local pixel viewport for tab continuity.
    """
    if boundary is None:
        return ('<div class="cf-muted-block">No active site boundary · '
                'Draw one in the Existing Site tab.</div>')
    ring = boundary.geometry['coordinates'][0]
    latitude_radians = math.radians(boundary.latitude)
    xs = [float(lon)*max(0.01, math.cos(latitude_radians)) for lon,lat in ring]
    ys = [float(lat) for lon,lat in ring]
    minx,maxx,miny,maxy = min(xs),max(xs),min(ys),max(ys)
    scale = min(420/max(maxx-minx,1e-11), 164/max(maxy-miny,1e-11))
    cx,cy = (minx+maxx)/2,(miny+maxy)/2
    pts = ' '.join(f'{260+(x-cx)*scale:.2f},{113-(y-cy)*scale:.2f}' for x,y in zip(xs,ys))
    return (f'<div class="cf-map-wrap"><svg viewBox="0 0 520 226" width="100%" '
            f'role="img" aria-label="Selected site boundary schematic">'
            f'<rect width="520" height="226" fill="#edf4f0"/>'
            f'<path d="M0 56H520 M0 113H520 M0 170H520 M130 0V226 M260 0V226 M390 0V226" '
            f'stroke="#d8e6de" stroke-width="1"/>'
            f'<polygon points="{pts}" fill="#a4d3be" fill-opacity=".55" '
            f'stroke="#087c6e" stroke-width="3"/>'
            f'<text x="18" y="25" font-size="13" fill="#336b60" '
            f'font-family="sans-serif">ACTIVE SITE BOUNDARY</text></svg>'
            f'<div class="cf-map-label">Selected geometry · {boundary.area_m2:,.1f} m² · '
            f'{boundary.perimeter_m:,.1f} m perimeter · Schematic only, not a basemap</div></div>')
