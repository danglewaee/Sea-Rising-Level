import argparse
from pathlib import Path

import geopandas as gpd
import numpy as np
import rasterio
from rasterio.mask import mask


D8_CODES = np.array([1, 2, 4, 8, 16, 32, 64, 128], dtype=np.uint8)


def crop_dem_to_boundary(dem_path: str, boundary_path: str | None, out_dem: str) -> str:
    out_path = Path(out_dem)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with rasterio.open(dem_path) as src:
        if boundary_path:
            boundary = gpd.read_file(boundary_path)
            if boundary.crs != src.crs:
                boundary = boundary.to_crs(src.crs)
            geoms = [geom for geom in boundary.geometry if geom is not None]
            data, transform = mask(src, geoms, crop=True)
            meta = src.meta.copy()
            meta.update({"height": data.shape[1], "width": data.shape[2], "transform": transform})
        else:
            data = src.read()
            meta = src.meta.copy()

    with rasterio.open(out_path, "w", **meta) as dst:
        dst.write(data)

    return str(out_path)


def compute_slope(dem: np.ndarray, transform) -> np.ndarray:
    arr = dem.astype(np.float32)
    arr[arr == dem.min()] = np.nan

    xres = abs(transform.a)
    yres = abs(transform.e)
    gy, gx = np.gradient(arr, yres, xres)
    slope_rad = np.arctan(np.sqrt(gx ** 2 + gy ** 2))
    return np.degrees(slope_rad).astype(np.float32)


def compute_flow_direction_d8(dem: np.ndarray) -> np.ndarray:
    arr = dem.astype(np.float32)
    arr[arr == dem.min()] = np.nan

    center = arr

    neighbors = [
        np.roll(np.roll(arr, -1, axis=0), 0, axis=1),   # N
        np.roll(np.roll(arr, -1, axis=0), 1, axis=1),   # NE
        np.roll(np.roll(arr, 0, axis=0), 1, axis=1),    # E
        np.roll(np.roll(arr, 1, axis=0), 1, axis=1),    # SE
        np.roll(np.roll(arr, 1, axis=0), 0, axis=1),    # S
        np.roll(np.roll(arr, 1, axis=0), -1, axis=1),   # SW
        np.roll(np.roll(arr, 0, axis=0), -1, axis=1),   # W
        np.roll(np.roll(arr, -1, axis=0), -1, axis=1),  # NW
    ]

    drops = np.stack([center - n for n in neighbors], axis=0)
    drops = np.where(np.isnan(drops), -np.inf, drops)

    best_idx = np.argmax(drops, axis=0)
    best_drop = np.max(drops, axis=0)

    out = np.zeros(arr.shape, dtype=np.uint8)
    positive = best_drop > 0
    out[positive] = D8_CODES[best_idx[positive]]

    out[0, :] = 0
    out[-1, :] = 0
    out[:, 0] = 0
    out[:, -1] = 0
    return out


def run_preprocess(dem_path: str, boundary_path: str | None, out_dir: str) -> dict:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    dem_out = out / "dem_conditioned.tif"
    slope_out = out / "slope.tif"
    flow_out = out / "flow_dir_d8.tif"

    crop_dem_to_boundary(dem_path, boundary_path, str(dem_out))

    with rasterio.open(dem_out) as src:
        dem = src.read(1)
        meta = src.meta.copy()

        slope = compute_slope(dem, src.transform)
        flow = compute_flow_direction_d8(dem)

    slope_meta = meta.copy()
    slope_meta.update(dtype="float32", count=1, nodata=np.nan)
    with rasterio.open(slope_out, "w", **slope_meta) as dst:
        dst.write(slope, 1)

    flow_meta = meta.copy()
    flow_meta.update(dtype="uint8", count=1, nodata=0)
    with rasterio.open(flow_out, "w", **flow_meta) as dst:
        dst.write(flow, 1)

    return {
        "dem_conditioned": str(dem_out),
        "slope": str(slope_out),
        "flow_dir_d8": str(flow_out),
    }


def main():
    parser = argparse.ArgumentParser(description="GIS preprocessing for anti-flood workflow")
    parser.add_argument("--dem", required=True, help="Input DEM tif")
    parser.add_argument("--boundary", default=None, help="Optional boundary vector for clipping")
    parser.add_argument("--out", required=True, help="Output folder")
    args = parser.parse_args()

    result = run_preprocess(args.dem, args.boundary, args.out)
    print(result)


if __name__ == "__main__":
    main()
