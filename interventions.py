"""ClimaForma Increment 5B: bounded, session-local spatial interventions.

Geometry and quantities only. No canopy radius, cooling response, cost or
surface-cover classification is inferred from a drawn design.
"""
from __future__ import annotations
from copy import deepcopy
from uuid import uuid4
import math

from shapely.geometry import shape, mapping, Polygon, MultiPolygon, Point
from shapely.ops import unary_union
from pyproj import Geod

GEOD = Geod(ellps="WGS84")
MAX_INTERVENTIONS = 100
INTERVENTION_TYPES = {
    "Tree planting": "point",
    "Grass / planting": "polygon",
    "Cool paving": "polygon",
    "Permeable paving": "polygon",
    "Water feature": "polygon",
    "Shade structure": "polygon",
}
INTERVENTION_COLORS = {
    "Tree planting": "#23784b",
    "Grass / planting": "#77b76c",
    "Cool paving": "#537fa8",
    "Permeable paving": "#bd9457",
    "Water feature": "#3a9dc0",
    "Shade structure": "#8064a2",
}


def _shape_from_drawing(drawing: dict):
    if not isinstance(drawing, dict):
        raise ValueError("Draw an intervention on the map first.")
    geometry = drawing.get("geometry") if drawing.get("type") == "Feature" else drawing
    if not isinstance(geometry, dict):
        raise ValueError("Invalid intervention drawing.")
    try:
        geom = shape(geometry)
    except (ValueError, TypeError, KeyError, IndexError, AttributeError) as exc:
        raise ValueError("Invalid drawing coordinates.") from exc
    if geom.is_empty or not geom.is_valid:
        raise ValueError("The intervention geometry is invalid.")
    if not all(math.isfinite(v) for v in geom.bounds):
        raise ValueError("Non-finite coordinates are not supported.")
    west, south, east, north = geom.bounds
    if not (-180 <= west <= east <= 180 and -90 <= south <= north <= 90):
        raise ValueError("Drawing must use WGS84 longitude/latitude coordinates.")
    return geom


def make_intervention(drawing: dict, kind: str, site_geometry: dict, *, identifier: str | None = None) -> dict:
    """Reject mismatched/outside geometry; never silently clip design areas."""
    if kind not in INTERVENTION_TYPES:
        raise ValueError("Unknown intervention type.")
    geom = _shape_from_drawing(drawing)
    expected = INTERVENTION_TYPES[kind]
    if expected == "point" and not isinstance(geom, Point):
        raise ValueError("Tree planting requires a point marker. Select the marker tool.")
    if expected == "polygon" and not isinstance(geom, Polygon):
        raise ValueError("This intervention requires a polygon or rectangle.")
    site = shape(site_geometry)
    if site.is_empty or not site.is_valid or site.geom_type not in ("Polygon", "MultiPolygon"):
        raise ValueError("A valid site boundary is required.")
    if not site.covers(geom):
        raise ValueError("Interventions must fall entirely inside the site boundary. Redraw inside the site.")
    area_m2 = 0.0
    if expected == "polygon":
        area_m2 = abs(GEOD.geometry_area_perimeter(geom)[0])
        if not math.isfinite(area_m2) or area_m2 < 1:
            raise ValueError("Draw a polygon of at least 1 m².")
    return {
        "id": identifier or uuid4().hex,
        "type": kind,
        "geometry": mapping(geom),
        "area_m2": round(area_m2, 2),
        "tree_count": 1 if expected == "point" else 0,
    }


def append_intervention(options: list[dict], option_id: str, intervention: dict) -> list[dict]:
    output = deepcopy(options)
    for option in output:
        if option["id"] == option_id:
            if len(option["interventions"]) >= MAX_INTERVENTIONS:
                raise ValueError(f"Maximum {MAX_INTERVENTIONS} interventions per option.")
            option["interventions"].append(deepcopy(intervention))
            return output
    raise ValueError("Active design option was not found.")


def remove_intervention(options: list[dict], option_id: str, intervention_id: str) -> list[dict]:
    output = deepcopy(options)
    for option in output:
        if option["id"] == option_id:
            old = len(option["interventions"])
            option["interventions"] = [x for x in option["interventions"] if x["id"] != intervention_id]
            if len(option["interventions"]) == old:
                raise ValueError("Intervention was not found.")
            return output
    raise ValueError("Active design option was not found.")


def summarize_interventions(interventions: list[dict]) -> dict:
    """Geometric quantities, including exclusive-surface union and overlaps."""
    exclusive_geoms = [shape(x["geometry"]) for x in interventions
                       if x["type"] in EXCLUSIVE_SURFACE_TYPES]
    union = unary_union(exclusive_geoms) if exclusive_geoms else None
    union_m2 = abs(GEOD.geometry_area_perimeter(union)[0]) if union is not None else 0.0
    return {
        "exclusive_surface_union_m2": round(union_m2, 2),
        "count": len(interventions),
        "trees": sum(x["tree_count"] for x in interventions),
        "total_polygon_m2": round(sum(x["area_m2"] for x in interventions), 2),
        "areas_by_type": {key: round(sum(x["area_m2"] for x in interventions if x["type"] == key), 2)
                          for key, geom_type in INTERVENTION_TYPES.items() if geom_type == "polygon"},
    }


# These are mutually exclusive proposed *ground-surface treatments*. Shade
# structures are overhead and trees are points, so may overlap ground treatments.
EXCLUSIVE_SURFACE_TYPES = frozenset({
    "Grass / planting", "Cool paving", "Permeable paving", "Water feature"
})

def find_surface_conflicts(interventions: list[dict], *, modified_id: str | None = None) -> list[tuple[str, str]]:
    """Return conflicting ID pairs; shared boundaries alone are not conflicts."""
    polygons = [(x["id"], shape(x["geometry"])) for x in interventions
                if x["type"] in EXCLUSIVE_SURFACE_TYPES]
    conflicts = []
    for idx, (left_id, left) in enumerate(polygons):
        for right_id, right in polygons[idx+1:]:
            if modified_id is not None and modified_id not in (left_id, right_id):
                continue
            if left.intersects(right) and left.intersection(right).area > 1e-14:
                conflicts.append((left_id, right_id))
    return conflicts

def replace_intervention(options: list[dict], option_id: str, intervention_id: str,
                         drawing: dict, site_geometry: dict) -> list[dict]:
    """Validate edited geometry; retain ID, type and other options unchanged."""
    output = deepcopy(options)
    for option in output:
        if option["id"] != option_id:
            continue
        for index, old in enumerate(option["interventions"]):
            if old["id"] == intervention_id:
                updated = make_intervention(drawing, old["type"], site_geometry, identifier=intervention_id)
                option["interventions"][index] = updated
                if find_surface_conflicts(option["interventions"], modified_id=intervention_id):
                    raise ValueError("Edited surface overlaps another incompatible ground treatment.")
                return output
        raise ValueError("Selected intervention was not found.")
    raise ValueError("Active design option was not found.")

def append_intervention_checked(options: list[dict], option_id: str, intervention: dict) -> list[dict]:
    """Append only if new exclusive ground-surface treatments do not overlap."""
    output = append_intervention(options, option_id, intervention)
    option = next(x for x in output if x["id"] == option_id)
    if find_surface_conflicts(option["interventions"], modified_id=intervention["id"]):
        raise ValueError("This ground-surface treatment overlaps an existing incompatible surface treatment.")
    return output
