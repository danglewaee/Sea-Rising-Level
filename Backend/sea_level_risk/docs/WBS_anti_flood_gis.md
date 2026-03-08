# WBS - Sea Level Anti-Flood GIS System

## 0. Scope and Success Criteria
- [ ] Define pilot city boundary and analysis scale (1:10,000 or 1:25,000).
- [ ] Freeze core objective: hazard + exposure + priority map (not only 3D demo).
- [ ] Define acceptance metrics:
  - [ ] Forecast quality (RMSE/MAE + q90/q95/q99).
  - [ ] GIS quality (CRS consistency, topology valid, reproducible outputs).
  - [ ] Decision quality (Top hotspot list with rationale).

Deliverable:
- `Backend/sea_level_risk/docs/project_scope.md`

---

## 1. Data Inventory and Registry
### 1.1 City registry
- [ ] Extend `Backend/sea_level_risk/city_registry.json` with:
  - `city_key`, `display_name`, `station`, `dem_path`, `admin_boundary`, `timezone`.
- [ ] Validate each city has at least one realtime station.

### 1.2 Raw data folders
- [ ] Create structure:
  - `data/raw/<city>/sea_level/`
  - `data/raw/<city>/dem/`
  - `data/raw/<city>/vector/`
  - `data/processed/<city>/`
- [ ] Add source manifest per city (`source_manifest.json`).

### 1.3 Source adapters
- [ ] NOAA adapter (done, refine limits and retries).
- [ ] UHSLC adapter (normalize schema).
- [ ] Optional: local agency adapter template.

Deliverables:
- `Backend/sea_level_risk/download_data.py` (enhanced)
- `Backend/sea_level_risk/docs/data_catalog.md`

---

## 2. GIS Preprocessing Pipeline
### 2.1 CRS and geometry QA
- [ ] Standardize projected CRS for analysis (city-specific UTM or equal-area).
- [ ] Reproject all vector layers.
- [ ] Run geometry fix/topology checks.

### 2.2 DEM conditioning
- [ ] Mosaic/crop DEM to city boundary.
- [ ] Fill sinks and remove artifacts.
- [ ] Create slope and flow-direction rasters.

### 2.3 Raster harmonization
- [ ] Align resolution/extent for all raster inputs.
- [ ] Save processing metadata (pixel size, nodata, transform).

Deliverables:
- `Backend/sea_level_risk/gis_preprocess.py`
- `data/processed/<city>/dem_conditioned.tif`
- `data/processed/<city>/flow_dir.tif`

---

## 3. Forecast Modeling (Realtime-capable)
### 3.1 Training dataset
- [ ] Build hourly sequences with strict time ordering.
- [ ] Split train/val/test chronologically.
- [ ] Outlier policy and missing-value policy documented.

### 3.2 Model training
- [ ] Baseline `lstm`.
- [ ] Compare `temporal_cnn` and `axial_lstm`.
- [ ] Keep weighted peak loss for extremes.

### 3.3 Evaluation
- [ ] Save overall metrics.
- [ ] Save peak metrics q90/q95/q99.
- [ ] Save per-horizon error profile.

Deliverables:
- `Backend/sea_level_risk/train.py` (current + improvements)
- `Backend/sea_level_risk/evaluation.py`
- `Backend/sea_level_risk/outputs/model_report_<city>.json`

---

## 4. Flood Hazard GIS Engine
### 4.1 Inundation extent
- [ ] Generate flood mask for baseline and scenarios (+20/+50/+100 cm).
- [ ] Convert to polygons with dissolve and cleanup.

### 4.2 Connectivity and drainage logic
- [ ] Add sea-connected flood filter (remove isolated pits where required).
- [ ] Add simple flow-routing support for drainage plausibility.

### 4.3 Hazard attributes
- [ ] Flood area (m2), flood ratio, polygon count.
- [ ] Optional depth proxy from surface level - DEM.

Deliverables:
- `Backend/sea_level_risk/gis.py` (current + connectivity module)
- `Backend/sea_level_risk/hazard_engine.py`

---

## 5. Exposure and Impact Analysis
### 5.1 Exposure layers
- [ ] Population grid / census blocks.
- [ ] Roads and transport nodes.
- [ ] Critical assets (hospital, school, power, water).

### 5.2 Intersections and indicators
- [ ] Affected population estimate.
- [ ] Road length affected.
- [ ] Critical facility count affected.

### 5.3 Outputs
- [ ] Scenario summary table.
- [ ] Administrative unit roll-up (district/ward stats).

Deliverables:
- `Backend/sea_level_risk/exposure.py`
- `Backend/sea_level_risk/outputs/exposure_<city>_<scenario>.csv`

---

## 6. Priority (Anti-flood Action) Scoring
### 6.1 Criteria definition
- [ ] Hazard score (flood ratio/depth/frequency).
- [ ] Exposure score (people/assets/roads).
- [ ] Vulnerability score (optional socio-economic data).

### 6.2 Weighted overlay
- [ ] Define weights file (`priority_weights.yaml`).
- [ ] Compute composite score 0-100.
- [ ] Classify Low/Moderate/High/Critical.

### 6.3 Hotspot ranking
- [ ] Produce Top-N hotspot polygons.
- [ ] Add recommended intervention type per hotspot.

Deliverables:
- `Backend/sea_level_risk/priority.py`
- `Backend/sea_level_risk/outputs/hotspots_<city>.geojson`
- `Backend/sea_level_risk/outputs/hotspot_table_<city>.csv`

---

## 7. API and Realtime Services
### 7.1 Core endpoints
- [ ] `GET /health`
- [ ] `GET /realtime/cities`
- [ ] `GET /realtime/forecast`
- [ ] `GET /realtime/hotspots?city=...`

### 7.2 Operational quality
- [ ] Add structured logging and request ids.
- [ ] Add timeout/retry policy for upstream data calls.
- [ ] Add basic cache for frequent city requests.

### 7.3 Data contracts
- [ ] Version API response (`api_version`).
- [ ] Publish JSON schema for forecast and hotspot responses.

Deliverables:
- `Backend/sea_level_risk/realtime_api.py` (current + hotspots endpoint)
- `Backend/sea_level_risk/docs/api_contract.md`

---

## 8. Dashboard (2D + 3D)
### 8.1 Core UI
- [ ] Realtime forecast chart and timeline.
- [ ] Scenario risk summary with badges.
- [ ] 3D map (single/all scenario toggle).

### 8.2 Planning-focused views
- [ ] 2D hotspot map with admin overlays.
- [ ] Asset-at-risk table with filters.
- [ ] Export button (CSV/GeoJSON report package).

### 8.3 UX hardening
- [ ] Auto-refresh interval control.
- [ ] Error banners with actionable diagnostics.
- [ ] Theme and legend consistency.

Deliverables:
- `Backend/sea_level_risk/dashboard_app.py` (current + planning views)

---

## 9. Validation and QA
### 9.1 Forecast QA
- [ ] Backtest against historical events.
- [ ] Drift monitoring (recent errors vs historical baseline).

### 9.2 GIS QA
- [ ] CRS checks and area sanity checks.
- [ ] Visual QA in QGIS for each scenario.

### 9.3 End-to-end QA
- [ ] Test script covering API + GIS output generation.
- [ ] Reproducibility test from clean environment.

Deliverables:
- `Backend/sea_level_risk/tests/test_realtime_pipeline.py`
- `Backend/sea_level_risk/docs/qa_checklist.md`

---

## 10. Deployment and Ops
### 10.1 Runtime setup
- [ ] Final `requirements-ml.txt` lock.
- [ ] `.env.example` for ports, cache, city defaults.

### 10.2 Service launch
- [ ] API start script (`run_api.ps1`).
- [ ] Dashboard start script (`run_dashboard.ps1`).

### 10.3 Monitoring
- [ ] Health check cron.
- [ ] Error log rotation.
- [ ] Daily export snapshot of key metrics.

Deliverables:
- `Backend/sea_level_risk/scripts/run_api.ps1`
- `Backend/sea_level_risk/scripts/run_dashboard.ps1`

---

## 11. Report Package (for submission)
- [ ] Methodology section (ML + GIS + scoring).
- [ ] Results section with 2D/3D maps and hotspot table.
- [ ] Limitation and uncertainty section.
- [ ] Policy/engineering recommendation section.

Deliverables:
- `Backend/sea_level_risk/docs/report_outline_vi.md`
- `Backend/sea_level_risk/docs/report_figures/`

---

## Suggested Execution Order (Practical)
1. Week 1: Sections 0-2
2. Week 2: Section 3
3. Week 3: Sections 4-5
4. Week 4: Sections 6-8
5. Week 5: Sections 9-11

---

## Immediate Next Tasks (start now)
- [ ] Add `admin_boundary` per city in `city_registry.json`.
- [ ] Build `gis_preprocess.py` skeleton.
- [ ] Add `/realtime/hotspots` endpoint placeholder.
- [ ] Add dashboard tab for 2D priority map.
