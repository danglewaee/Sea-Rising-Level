# Sea Level Risk Pipeline (Forecast + GIS + Realtime 3D Dashboard)

## Setup (Python 3.11)
```powershell
powershell -ExecutionPolicy Bypass -File Backend/setup_py311_env.ps1
Backend/.venv311/Scripts/python -m pip install -r Backend/requirements-ml.txt
```

## Train model (one-time)
```powershell
Backend/.venv311/Scripts/python -m Backend.sea_level_risk.train \
  --csv data/honolulu_hourly.csv \
  --value-col sea_level \
  --time-col timestamp \
  --model-type axial_lstm
```

## Realtime API (multi-city)
```powershell
Backend/.venv311/Scripts/python -m Backend.sea_level_risk.realtime_api \
  --model Backend/sea_level_risk/outputs/sea_level_axial_lstm.keras \
  --metadata Backend/sea_level_risk/outputs/metadata.json \
  --host 127.0.0.1 --port 8000
```

Endpoints:
- `GET /health`
- `GET /realtime/cities`
- `GET /realtime/forecast?city=honolulu&horizon=6&hours_back=96&auto_dem=1`
- `GET /realtime/forecast?station=1612340&horizon=6&hours_back=96&auto_dem=1`

Ghi chu:
- `city_registry.json` map city -> NOAA station.
- Neu city khong co DEM local, API se thu `auto_dem=1`: lay station lat/lon NOAA va tai Copernicus DEM tile vao `data/dem_cache/`.

## 3D Dashboard (interactive)
Chay API truoc, sau do chay dashboard:
```powershell
Backend/.venv311/Scripts/streamlit run Backend/sea_level_risk/dashboard_app.py
```

Dashboard cho phep:
- Chon city coastal
- Lay du lieu realtime
- Ve forecast line
- Render ban do ngap 3D theo scenario (+20/+50/+100cm)

## Files
- `Backend/sea_level_risk/realtime_api.py`: realtime API
- `Backend/sea_level_risk/dashboard_app.py`: 3D dashboard
- `Backend/sea_level_risk/city_registry.json`: danh sach city
- `Backend/sea_level_risk/dem_provider.py`: auto DEM from Copernicus
