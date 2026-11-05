"""Load user-supplied ClimaForma showcase boundaries from repository-root GeoJSON.

The three supplied showcase files contain 3D MultiPolygon coordinates. The
interactive site-drawing workflow uses 2D longitude/latitude Polygon rings,
so elevation is intentionally discarded without modifying source GeoJSON.
Construction activity and parcel status have not been independently verified.
"""
from __future__ import annotations

import json
from pathlib import Path

from shapely.geometry import MultiPolygon, Polygon, shape
from site_mapping import BoundaryInfo, parse_boundary

SHOWCASE_FILES = {
    "Stockholm · Södermalm": "SODERMALM_SITE.geojson",
    "Barcelona · Selected construction site": "BARCELONA_SITE.geojson",
    "Vienna · Selected construction site": "VIENNA_SITE.geojson",
}
_DATA_DIR = Path(__file__).resolve().parent


def showcase_boundary(city: str) -> BoundaryInfo:
    """Load one showcase AOI, converting 3D source rings to 2D WGS84."""
    if city not in SHOWCASE_FILES:
        raise ValueError("Unknown showcase location.")

    path = _DATA_DIR / SHOWCASE_FILES[city]
    with path.open(encoding="utf-8-sig") as fp:
        collection = json.load(fp)
    features = collection.get("features") if isinstance(collection, dict) else None
    if collection.get("type") != "FeatureCollection" or not isinstance(features, list) or len(features) != 1:
        raise ValueError("Showcase GeoJSON must contain exactly one project feature.")

    geom = shape(features[0]["geometry"])
    if isinstance(geom, MultiPolygon):
        if len(geom.geoms) != 1:
            raise ValueError("Showcase area must be a single contiguous polygon.")
        geom = geom.geoms[0]
    if not isinstance(geom, Polygon):
        raise ValueError("Showcase AOI must be a polygon.")

    # Each source coordinate may have Z. Leaflet rendering and the WGS84
    # boundary model require exactly [longitude, latitude]. Preserve holes.
    rings = [geom.exterior, *geom.interiors]
    coordinates = [
        [[float(point[0]), float(point[1])] for point in ring.coords]
        for ring in rings
    ]
    return parse_boundary({"type": "Polygon", "coordinates": coordinates})
