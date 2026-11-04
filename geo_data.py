"""ClimaForma Increment 3: bounded acquisition and validation of VECTOR context only.

EPSG:4326 throughout. No land-cover classification, remote sensing, thermal analysis,
or other scientific predictions. External OSM data require a user-initiated request.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

import requests
from shapely.geometry import shape, mapping, Polygon, MultiPolygon
from shapely.ops import unary_union
from shapely.validation import explain_validity

MAX_UPLOAD_BYTES = 2_000_000
MAX_UPLOAD_FEATURES = 1500
MAX_OSM_BBOX_KM2 = 2.5
MAX_OSM_FEATURES = 2500
# Public endpoints can return 429/502/503 or time out; use documented alternatives.
# Private.coffee is the current endpoint of the former overpass.kumi.systems service.
OVERPASS_ENDPOINTS = (
    'https://overpass.private.coffee/api/interpreter',
    'https://ovp.dresel.systems/api/interpreter',  # Europe coverage; daily updates
    'https://overpass-api.de/api/interpreter',
)
OVERPASS_URL = OVERPASS_ENDPOINTS[0]  # Compatibility alias



@dataclass(frozen=True)
class VectorData:
    name: str
    features: list[dict]
    source: str
    acquired_utc: str
    checked: int
    kept: int
    rejected: int
    notes: tuple[str, ...]

    @property
    def feature_collection(self) -> dict:
        return {'type': 'FeatureCollection', 'features': self.features}


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def _valid_polygon(geom: Any):
    if not isinstance(geom, dict) or geom.get('type') not in ('Polygon', 'MultiPolygon'):
        return None
    try:
        polygon = shape(geom)
    except (TypeError, ValueError, KeyError, IndexError):
        return None
    if polygon.is_empty or not polygon.is_valid:
        return None
    bounds = polygon.bounds
    if any(not math.isfinite(v) for v in bounds):
        return None
    if not (-180 <= bounds[0] <= bounds[2] <= 180 and -90 <= bounds[1] <= bounds[3] <= 90):
        return None
    return polygon if polygon.area > 0 else None


def process_geojson_bytes(data: bytes, boundary_geom: dict) -> VectorData:
    """Validate and clip polygons to the active site, without inferring their class."""
    if not data or len(data) > MAX_UPLOAD_BYTES:
        raise ValueError('Upload a GeoJSON file between 1 byte and 2 MB.')
    try:
        collection = json.loads(data.decode('utf-8-sig'))
    except (ValueError, UnicodeDecodeError) as exc:
        raise ValueError('File must contain valid UTF-8 GeoJSON.') from exc
    if not isinstance(collection, dict):
        raise ValueError('Expected a GeoJSON FeatureCollection.')
    if collection.get('crs') is not None:
        raise ValueError('GeoJSON CRS declaration is not supported; supply WGS84 (EPSG:4326).')
    if collection.get('type') != 'FeatureCollection' or not isinstance(collection.get('features'), list):
        raise ValueError('Only GeoJSON FeatureCollection is supported.')
    incoming = collection['features']
    if len(incoming) > MAX_UPLOAD_FEATURES:
        raise ValueError('Upload exceeds 1,500 features; select a smaller site dataset.')
    site = _valid_polygon(boundary_geom)
    if site is None:
        raise ValueError('Select a valid site boundary first.')
    result = []
    rejected = 0
    for item in incoming:
        geom = item.get('geometry') if isinstance(item, dict) and item.get('type') == 'Feature' else None
        poly = _valid_polygon(geom)
        if poly is None:
            rejected += 1
            continue
        inter = poly.intersection(site)
        if inter.is_empty:
            continue
        if not inter.is_valid:
            rejected += 1
            continue
        # Only polygonal components are admitted; strips/point touching excluded.
        if inter.geom_type == 'GeometryCollection':
            poly_parts = [g for g in inter.geoms if isinstance(g, (Polygon, MultiPolygon)) and g.area > 0]
            if not poly_parts:
                continue
            inter = unary_union(poly_parts)
        if not isinstance(inter, (Polygon, MultiPolygon)) or inter.area <= 0:
            continue
        result.append({'type': 'Feature', 'geometry': mapping(inter), 'properties': {'source': 'user_geojson'}})
    return VectorData('Uploaded GeoJSON', result, 'User-provided (unverified class)', _utc(),
                      len(incoming), len(result), rejected,
                      ('Polygon geometries only', 'Clipped to selected boundary',
                       'Feature classes are not inferred or verified'))


def bbox_km2_approx(bounds: tuple[float, float, float, float]) -> float:
    minx, miny, maxx, maxy = bounds
    if not all(math.isfinite(v) for v in bounds):
        raise ValueError('Invalid coordinates.')
    if minx >= maxx or miny >= maxy or maxx-minx > 180:
        raise ValueError('Unsupported bounding box.')
    mid_lat = math.radians((miny + maxy) / 2)
    return (maxx-minx)*111.32*max(0.0, math.cos(mid_lat))*(maxy-miny)*111.32


def overpass_query(bounds: tuple[float, float, float, float]) -> str:
    if bbox_km2_approx(bounds) > MAX_OSM_BBOX_KM2:
        raise ValueError('OSM request extent is too large (max 2.5 km² bounding box). Draw a smaller site.')
    west, south, east, north = bounds
    return f'[out:json][timeout:20];way["building"]({south:.7f},{west:.7f},{north:.7f},{east:.7f});out geom;'


def process_overpass_result(data: dict, boundary_geom: dict) -> VectorData:
    if not isinstance(data, dict) or not isinstance(data.get('elements'), list):
        raise ValueError('Invalid Overpass JSON response.')
    elements = data['elements']
    if len(elements) > MAX_OSM_FEATURES:
        raise ValueError('OSM response exceeds the 2,500-building safety limit.')
    site = _valid_polygon(boundary_geom)
    if site is None:
        raise ValueError('A valid site boundary is required.')
    found = []
    rejected = 0
    for item in elements:
        if not isinstance(item, dict) or item.get('type') != 'way' or not isinstance(item.get('geometry'), list):
            rejected += 1
            continue
        coords = []
        for node in item['geometry']:
            if not isinstance(node, dict):
                coords = []
                break
            coords.append([node.get('lon'), node.get('lat')])
        if len(coords) < 4 or coords[0] != coords[-1]:
            rejected += 1
            continue
        poly = _valid_polygon({'type': 'Polygon', 'coordinates': [coords]})
        if poly is None:
            rejected += 1
            continue
        inter = poly.intersection(site)
        if not isinstance(inter, (Polygon, MultiPolygon)) or inter.is_empty or not inter.is_valid or inter.area <= 0:
            continue
        found.append({'type': 'Feature', 'geometry': mapping(inter),
                      'properties': {'osm_id': str(item.get('id', '')), 'source': 'OpenStreetMap building tag'}})
    return VectorData('OSM buildings', found, 'OpenStreetMap via Overpass API', _utc(),
                      len(elements), len(found), rejected,
                      ('Building-tagged OSM ways only', 'OSM completeness not guaranteed',
                       'Relation-only buildings may be missing', 'Clipped to selected boundary'))


def fetch_osm_buildings(boundary_geom: dict, bounds: tuple[float, float, float, float]) -> VectorData:
    """Fetch on demand; try independent Overpass instances, without losing site state.

    No external request is made if the bounding box or geometry is invalid.
    An HTTP 200 response must also contain a valid Overpass JSON object.
    """
    query = overpass_query(bounds)
    if _valid_polygon(boundary_geom) is None:
        raise ValueError('Select a valid site boundary first.')
    failures: list[str] = []
    for url in OVERPASS_ENDPOINTS:
        host = url.split('/')[2]
        try:
            response = requests.post(
                url, data={'data': query}, timeout=(6, 18),
                headers={'User-Agent': 'ClimaFormaPrototype/0.4 (geospatial research demo)',
                         'Accept': 'application/json'},
            )
            response.raise_for_status()
            if 'json' not in response.headers.get('Content-Type', '').lower():
                # Some Overpass configurations may omit content-type for JSON.
                if not response.text.lstrip().startswith('{'):
                    raise ValueError('non-JSON response')
            payload = response.json()
            result = process_overpass_result(payload, boundary_geom)
            return VectorData(
                name=result.name, features=result.features,
                source=f'OpenStreetMap via {host}', acquired_utc=result.acquired_utc,
                checked=result.checked, kept=result.kept, rejected=result.rejected,
                notes=result.notes + (f'Endpoint: {host}',),
            )
        except requests.Timeout:
            failures.append(f'{host}: timeout')
        except requests.HTTPError as exc:
            status = exc.response.status_code if exc.response is not None else 'unknown'
            failures.append(f'{host}: HTTP {status}')
        except requests.RequestException:
            failures.append(f'{host}: connection error')
        except (ValueError, TypeError, KeyError):
            failures.append(f'{host}: invalid response')
    raise ValueError(
        'OSM building retrieval failed across available public services. '
        + ' | '.join(failures)
        + '. You can retry later or upload building polygons as EPSG:4326 GeoJSON.'
    )
