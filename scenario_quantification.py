"""ClimaForma 6A: descriptive design-scenario geometry, not climate impact estimates.

Ground-surface coverage is a geodesic union; overhead shade is independent.
An untreated/unassigned design area is not an observed land-cover class.
"""
from __future__ import annotations
import csv
import io
import math
from shapely.geometry import shape
from shapely.ops import unary_union
from pyproj import Geod
from interventions import INTERVENTION_TYPES, EXCLUSIVE_SURFACE_TYPES

_GEOD = Geod(ellps="WGS84")
_SURFACES = tuple(kind for kind in INTERVENTION_TYPES if kind in EXCLUSIVE_SURFACE_TYPES)
_POLYGONS = tuple(kind for kind, geometry_type in INTERVENTION_TYPES.items() if geometry_type == "polygon")


def _area(geometry):
    if geometry.is_empty:
        return 0.0
    area = abs(_GEOD.geometry_area_perimeter(geometry)[0])
    if not math.isfinite(area):
        raise ValueError("Cannot calculate a finite geodesic area.")
    return area


def _union_area(geometries):
    return _area(unary_union(geometries)) if geometries else 0.0


def quantify_option(option: dict, site_geometry: dict) -> dict:
    """Recompute from coordinates; never rely on rounded cached area_m2 values."""
    site = shape(site_geometry)
    if site.is_empty or not site.is_valid or site.geom_type not in ("Polygon", "MultiPolygon"):
        raise ValueError("A valid polygon project site is required.")
    site_m2 = _area(site)
    if site_m2 <= 0:
        raise ValueError("Project site area must be positive.")
    geoms = {name: [] for name in _POLYGONS}
    tree_count = 0
    interventions = option.get("interventions", [])
    for item in interventions:
        kind = item["type"]
        if kind not in INTERVENTION_TYPES:
            raise ValueError("Unknown design intervention type.")
        geometry = shape(item["geometry"])
        if geometry.is_empty or not geometry.is_valid or not site.covers(geometry):
            raise ValueError("An intervention is invalid or outside the project site.")
        if kind == "Tree planting":
            if geometry.geom_type != "Point":
                raise ValueError("Tree locations must be points.")
            tree_count += 1
        else:
            if geometry.geom_type not in ("Polygon", "MultiPolygon"):
                raise ValueError("Surface interventions must be polygons.")
            geoms[kind].append(geometry)
    ground_polys = [geom for kind in _SURFACES for geom in geoms[kind]]
    ground_area = _union_area(ground_polys)
    shade_area = _union_area(geoms["Shade structure"])
    areas = {name: _union_area(geoms[name]) for name in _POLYGONS}
    # The source workflow prevents overlap between proposed ground surfaces.
    # Report the actual union regardless, keeping quantification robust to legacy data.
    return {
        "option_id": str(option["id"]),
        "option_name": str(option["name"]),
        "site_area_m2": round(site_m2, 2),
        "intervention_count": len(interventions),
        "tree_locations": tree_count,
        "ground_treatment_m2": round(ground_area, 2),
        "ground_coverage_pct": round(100 * ground_area / site_m2, 2),
        "unassigned_ground_m2": round(max(0, site_m2 - ground_area), 2),
        "unassigned_ground_pct": round(max(0, 100 * (site_m2-ground_area) / site_m2), 2),
        "shade_footprint_m2": round(shade_area, 2),
        "shade_footprint_pct": round(100 * shade_area / site_m2, 2),
        "areas_by_type_m2": {name: round(areas[name], 2) for name in _POLYGONS},
    }


def quantify_options(options: list[dict], site_geometry: dict) -> list[dict]:
    return [quantify_option(option, site_geometry) for option in options]


def comparison_rows(quantified: list[dict]) -> list[dict]:
    rows = []
    for item in quantified:
        row = {
            "Design option": item["option_name"],
            "Site area (m²)": item["site_area_m2"],
            "Interventions (count)": item["intervention_count"],
            "Proposed trees (locations)": item["tree_locations"],
            "Ground-treatment area (m²)": item["ground_treatment_m2"],
            "Ground-treatment coverage (%)": item["ground_coverage_pct"],
            "Unassigned design ground (m²)": item["unassigned_ground_m2"],
            "Shade footprint (m²)": item["shade_footprint_m2"],
            "Shade footprint (%)": item["shade_footprint_pct"],
        }
        for kind in _POLYGONS:
            row[f"{kind} (m²)"] = item["areas_by_type_m2"][kind]
        rows.append(row)
    return rows


def comparison_csv(rows: list[dict]) -> bytes:
    if not rows:
        return b""
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("utf-8-sig")
