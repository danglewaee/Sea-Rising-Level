import argparse
from pathlib import Path

import geopandas as gpd
import numpy as np
import plotly.graph_objects as go
import rasterio
from rasterio.features import rasterize


SCENARIO_STYLE = {
    "plus_20cm": {"color": "rgba(255,215,0,0.65)", "opacity": 0.45, "label": "+20cm"},
    "plus_50cm": {"color": "rgba(255,140,0,0.75)", "opacity": 0.50, "label": "+50cm"},
    "plus_100cm": {"color": "rgba(220,20,60,0.85)", "opacity": 0.55, "label": "+100cm"},
}

CAMERA_PRESETS = {
    "oblique": dict(eye=dict(x=1.8, y=1.6, z=1.1)),
    "top": dict(eye=dict(x=0.01, y=0.01, z=2.8)),
    "coastal": dict(eye=dict(x=2.2, y=0.8, z=0.9)),
}


def _infer_water_level(flood_gdf: gpd.GeoDataFrame, fallback: float) -> float:
    if "predicted_level_m" in flood_gdf.columns and not flood_gdf["predicted_level_m"].isna().all():
        return float(flood_gdf["predicted_level_m"].iloc[0])
    return fallback


def _make_xy_grid(transform, shape: tuple[int, int]) -> tuple[np.ndarray, np.ndarray]:
    height, width = shape
    rows, cols = np.indices((height, width), dtype=np.float32)
    x = transform.c + (cols + 0.5) * transform.a + (rows + 0.5) * transform.b
    y = transform.f + (cols + 0.5) * transform.d + (rows + 0.5) * transform.e
    return x.astype(np.float32), y.astype(np.float32)


def _load_dem(dem_path: str):
    with rasterio.open(dem_path) as src:
        dem = src.read(1, masked=True)
        dem_arr = np.asarray(dem.filled(np.nan), dtype=np.float32)
        x, y = _make_xy_grid(src.transform, dem_arr.shape)
        return dem_arr, x, y, src.transform, src.crs


def _flood_mask_from_geojson(flood_geojson: str, out_shape, transform, crs) -> tuple[np.ndarray, float]:
    flood = gpd.read_file(flood_geojson)
    if flood.empty:
        return np.zeros(out_shape, dtype=bool), float("nan")
    if flood.crs != crs:
        flood = flood.to_crs(crs)

    mask = rasterize(
        [(geom, 1) for geom in flood.geometry if geom is not None],
        out_shape=out_shape,
        transform=transform,
        fill=0,
        dtype=np.uint8,
    ).astype(bool)

    return mask, _infer_water_level(flood, fallback=float("nan"))


def render_3d_flood_map_multi(
    dem_path: str,
    scenario_items: list[dict],
    out_html: str,
    downsample: int = 4,
    vertical_exaggeration: float = 1.5,
    terrain_colorscale: str = "Earth",
    camera_preset: str = "oblique",
):
    out_path = Path(out_html)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    dem_arr, x, y, transform, crs = _load_dem(dem_path)

    step = max(1, int(downsample))
    x_ds = x[::step, ::step]
    y_ds = y[::step, ::step]
    z_ds = dem_arr[::step, ::step] * float(vertical_exaggeration)

    finite_dem = np.isfinite(z_ds)
    if not np.any(finite_dem):
        raise ValueError("DEM contains no finite values after masking.")

    traces = [
        go.Surface(
            x=x_ds,
            y=y_ds,
            z=z_ds,
            colorscale=terrain_colorscale,
            colorbar=dict(title="Elevation (m)"),
            name="Terrain",
            showscale=True,
            showlegend=False,
        )
    ]

    for item in scenario_items:
        scenario = item.get("scenario", "unknown")
        flood_geojson = item.get("flood_geojson") or item.get("geojson")
        if not flood_geojson:
            continue

        mask, inferred_level = _flood_mask_from_geojson(flood_geojson, dem_arr.shape, transform, crs)
        level = item.get("water_level_m")
        if level is None or (isinstance(level, float) and np.isnan(level)):
            if np.isnan(inferred_level):
                continue
            level = float(inferred_level)

        style = SCENARIO_STYLE.get(scenario, {"color": "rgba(65,105,225,0.7)", "opacity": 0.45, "label": scenario})
        m_ds = mask[::step, ::step]
        water_z = np.where(m_ds & finite_dem, float(level) * float(vertical_exaggeration), np.nan)

        traces.append(
            go.Surface(
                x=x_ds,
                y=y_ds,
                z=water_z,
                colorscale=[[0, style["color"]], [1, style["color"]]],
                showscale=False,
                opacity=float(style["opacity"]),
                name=style.get("label", scenario),
                showlegend=True,
            )
        )

    camera = CAMERA_PRESETS.get(camera_preset, CAMERA_PRESETS["oblique"])

    fig = go.Figure(data=traces)
    fig.update_layout(
        title="3D Flood Inundation Map",
        scene=dict(
            xaxis_title="Longitude",
            yaxis_title="Latitude",
            zaxis_title="Elevation (m)",
            camera=camera,
        ),
        margin=dict(l=0, r=0, t=48, b=0),
        legend=dict(yanchor="top", y=0.98, xanchor="left", x=0.01),
    )

    fig.write_html(str(out_path), include_plotlyjs="cdn")
    return {"out_html": str(out_path), "downsample": step, "vertical_exaggeration": vertical_exaggeration, "camera": camera_preset}


def render_3d_flood_map(
    dem_path: str,
    flood_geojson: str,
    out_html: str,
    downsample: int = 4,
    vertical_exaggeration: float = 1.5,
    water_alpha: float = 0.65,
    terrain_colorscale: str = "Earth",
    camera_preset: str = "oblique",
):
    _ = water_alpha
    return render_3d_flood_map_multi(
        dem_path=dem_path,
        scenario_items=[{"scenario": "plus_50cm", "flood_geojson": flood_geojson}],
        out_html=out_html,
        downsample=downsample,
        vertical_exaggeration=vertical_exaggeration,
        terrain_colorscale=terrain_colorscale,
        camera_preset=camera_preset,
    )


def main():
    parser = argparse.ArgumentParser(description="Render interactive 3D flood map from DEM + flood polygon")
    parser.add_argument("--dem", required=True, help="DEM raster (.tif)")
    parser.add_argument("--flood", required=True, help="Flood polygon GeoJSON")
    parser.add_argument("--out", required=True, help="Output HTML path")
    parser.add_argument("--downsample", type=int, default=4)
    parser.add_argument("--zex", type=float, default=1.5, help="Vertical exaggeration")
    parser.add_argument("--camera", default="oblique", choices=["oblique", "top", "coastal"])
    args = parser.parse_args()

    result = render_3d_flood_map(
        dem_path=args.dem,
        flood_geojson=args.flood,
        out_html=args.out,
        downsample=args.downsample,
        vertical_exaggeration=args.zex,
        camera_preset=args.camera,
    )
    print(result)


if __name__ == "__main__":
    main()
