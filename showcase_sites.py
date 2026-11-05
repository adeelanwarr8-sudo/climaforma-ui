"""Explicit illustrative demonstration areas (not verified land parcels).

The showcase geometries are small rectangles centred on known district navigation
coordinates. They are not cadastral/site ownership boundaries or validated study sites.
"""
from __future__ import annotations

from pyproj import Geod
from site_mapping import SHOWCASE_CENTERS, BoundaryInfo, parse_boundary

_GEOD = Geod(ellps="WGS84")
# Demonstration footprint only: 120 m x 120 m at each known city navigation point.
_HALF_WIDTH_M = 60.0
_HALF_HEIGHT_M = 60.0


def showcase_boundary(city: str) -> BoundaryInfo:
    if city not in SHOWCASE_CENTERS:
        raise ValueError("Unknown showcase location.")
    lat, lon, _zoom = SHOWCASE_CENTERS[city]
    ring = []
    for east, north in ((-_HALF_WIDTH_M, -_HALF_HEIGHT_M),
                        (_HALF_WIDTH_M, -_HALF_HEIGHT_M),
                        (_HALF_WIDTH_M, _HALF_HEIGHT_M),
                        (-_HALF_WIDTH_M, _HALF_HEIGHT_M)):
        bearing = (90 if east >= 0 else 270)
        x, y, _ = _GEOD.fwd(lon, lat, bearing, abs(east))
        bearing_ns = 0 if north >= 0 else 180
        x, y, _ = _GEOD.fwd(x, y, bearing_ns, abs(north))
        ring.append([x, y])
    ring.append(ring[0])
    return parse_boundary({"type": "Polygon", "coordinates": [ring]})
