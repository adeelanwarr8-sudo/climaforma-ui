"""User-supplied polygon AOIs for ClimaForma showcase cases.

Their coordinates have been validated, but their construction status and
parcel/property classification are not independently verified.
"""
from __future__ import annotations
import json
from pathlib import Path
from shapely.geometry import shape, Polygon, MultiPolygon
from site_mapping import BoundaryInfo, parse_boundary

SHOWCASE_FILES = {
    "Stockholm · Södermalm": "SODERMALM_SITE.geojson",
    "Barcelona · Selected construction site": "BARCELONA_SITE.geojson",
    "Vienna · Selected construction site": "VIENNA_SITE.geojson",
}
_DATA_DIR = Path(__file__).resolve().parent  # GeoJSON files stored in repository root


def showcase_boundary(city: str) -> BoundaryInfo:
    """Load one validated user-supplied AOI; preserve its original coordinates."""
    if city not in SHOWCASE_FILES:
        raise ValueError("Unknown showcase location.")
    with (_DATA_DIR / SHOWCASE_FILES[city]).open(encoding="utf-8") as fp:
        collection = json.load(fp)
    if collection.get("type") != "FeatureCollection" or len(collection.get("features", [])) != 1:
        raise ValueError("Showcase GeoJSON must contain exactly one project feature.")
    geom = shape(collection["features"][0]["geometry"])
    if isinstance(geom, MultiPolygon):
        if len(geom.geoms) != 1:
            raise ValueError("Showcase area must be a single contiguous polygon.")
        geom = geom.geoms[0]
    if not isinstance(geom, Polygon):
        raise ValueError("Showcase AOI must be a polygon.")
    return parse_boundary({"type": "Polygon", "coordinates":
                           [[list(p) for p in geom.exterior.coords]] +
                           [[list(p) for p in ring.coords] for ring in geom.interiors]})
