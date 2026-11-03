# ClimaForma v2.1 — Standalone UI-only Streamlit prototype

## Purpose
This is a design-review build. **No analytical functionality is connected**. It uses only Streamlit; it does not import the existing scientific engine, use satellite/GIS data, call web APIs, read files, or compute any environmental performance indicators. All input controls are disabled and the SVG site diagrams are purely illustrative.

## What's improved in v2.1
- More legible system-font hierarchy, restrained spacing, larger content workspace and consistent cards.
- Sidebar divided into Project information, Site selection, Analysis settings and Application status.
- Existing Site: stronger map prominence, map layer presentation, clearly distinguished site metadata, data quality and baseline indicators.
- Design Options: distinct categories for Landscape, Materials, and Built Shade; conceptual drawing workspace and option manager.
- Compare Options: three equal-sized panels for Existing Site, Option A and Option B, followed by indicator placeholders, chart and exports.

## Deploy to Streamlit Community Cloud
1. Create/choose a GitHub repository. Upload `app.py`, `requirements.txt`, `.streamlit/`, `tests/`, and this README to the repository root.
2. Set main branch `main` and main file path `app.py`.
3. Deploy and visually review all three tabs. No secrets or service credentials are required.

## Test
```bash
python -m pip install -r requirements.txt
streamlit run app.py
python -m pip install pytest
python -m pytest -q tests
```

## Acceptance review
- Inspect desktop and narrower browser widths.
- Check the sidebar doesn't obstruct the principal map or comparison panels.
- Check each of three tabs renders and text remains readable.
- Confirm controls are visibly disabled, charts/maps are static, and no external analytical requests are made.

## Status
Source-level tests and Python syntax checks pass. Actual Streamlit browser rendering has **not** been tested in the packaging environment. Final visual approval occurs after GitHub/Streamlit deployment.
