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
