import json
from pathlib import Path
from typing import Optional

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.features import shapes
from shapely.geometry import shape


EQUAL_AREA_EPSG = 6933


def _compute_flood_area_m2(flood_gdf: gpd.GeoDataFrame) -> float:
    if flood_gdf.empty:
        return 0.0
    return float(flood_gdf.to_crs(epsg=EQUAL_AREA_EPSG).geometry.area.sum())


def dem_to_flood_polygon(dem_path: str, predicted_level_m: float, out_geojson: str, crs: Optional[str] = None) -> dict:
    out_path = Path(out_geojson)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with rasterio.open(dem_path) as src:
        dem = src.read(1, masked=True)
        nodata_mask = np.ma.getmaskarray(dem)

        flood_mask = np.asarray((dem <= predicted_level_m) & (~nodata_mask), dtype=np.uint8)
        valid_mask = np.asarray(~nodata_mask, dtype=np.uint8)

        geoms = []
        for geom, value in shapes(flood_mask, mask=valid_mask, transform=src.transform):
            if value == 1:
                geoms.append(shape(geom))

        if not geoms:
            flood_gdf = gpd.GeoDataFrame({"predicted_level_m": []}, geometry=[], crs=src.crs)
        else:
            flood_gdf = gpd.GeoDataFrame(
                {"predicted_level_m": [predicted_level_m] * len(geoms)},
                geometry=geoms,
                crs=src.crs,
            )
            flood_gdf = flood_gdf.dissolve(by="predicted_level_m", as_index=False)

        if crs:
            flood_gdf = flood_gdf.to_crs(crs)

        flood_gdf.to_file(out_path, driver="GeoJSON")

        flood_pixel_count = int(np.count_nonzero(flood_mask))
        valid_pixel_count = int(np.count_nonzero(valid_mask))
        flood_ratio = float(flood_pixel_count / valid_pixel_count) if valid_pixel_count > 0 else 0.0
        flood_area_m2 = _compute_flood_area_m2(flood_gdf)

    return {
        "predicted_level_m": predicted_level_m,
        "flood_pixels": flood_pixel_count,
        "valid_pixels": valid_pixel_count,
        "flood_ratio": flood_ratio,
        "flood_area_m2": flood_area_m2,
        "out_geojson": str(out_path),
    }


def compute_exposure(flood_geojson: str, layer_path: str, layer_name: str = "layer") -> dict:
    flood = gpd.read_file(flood_geojson)
    layer = gpd.read_file(layer_path)

    if flood.empty or layer.empty:
        return {"layer": layer_name, "intersections": 0, "affected_area_m2": 0.0}

    if flood.crs != layer.crs:
        layer = layer.to_crs(flood.crs)

    intersection = gpd.overlay(layer, flood, how="intersection")
    area = float(intersection.to_crs(epsg=EQUAL_AREA_EPSG).geometry.area.sum()) if not intersection.empty else 0.0

    return {
        "layer": layer_name,
        "intersections": int(len(intersection)),
        "affected_area_m2": area,
    }


def save_summary(path: str, summary: dict) -> None:
    Path(path).write_text(json.dumps(summary, indent=2), encoding="utf-8")
