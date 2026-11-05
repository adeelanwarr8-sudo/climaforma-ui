# ClimaForma v2.4.10 — User-supplied showcase AOIs

**Builds on the v2.4.9 application.** Replaces the three artificial showcase rectangles with the three GeoJSON polygons supplied by the project owner.

## GitHub deployment

1. Replace `app.py`.
2. Replace `showcase_sites.py`.
3. Add the folder `showcase_data` and its three GeoJSON files at the repository root. **Keep folder name and filenames unchanged.**
4. Leave `site_mapping.py`, `geo_data.py`, `buffer_geometry.py`, `address_lookup.py`, and `requirements.txt` unchanged.

On switching showcase cities, the application loads the appropriate AOI, computes site measures, and centers the map on the geometry. The separate analysis buffer still uses the existing 0–300 m control. Edit, clear, and reload behaviour is retained.

The uploaded files identify polygon areas but do not establish construction status, legal ownership, or cadastral boundaries. Barcelona and Vienna have been renamed to city-level construction-site labels because the uploaded geometries do not coincide with the previous Eixample/Neubau navigation presets.

## Browser tests

- Select each showcase; map should center on its polygon and show green site border plus blue 100 m buffer.
- Check site area approximately: Stockholm 37,746 m²; Barcelona 71,545 m²; Vienna 8,947 m².
- Edit site; area and buffer recalculate. Delete it; buffer disappears. Reload AOI; original is restored.
- Confirm Address Lookup, manual drawing, OSM and GeoJSON functions continue working.

## Scope

No satellite retrieval, temperature calculation, or design scenario modelling added.
