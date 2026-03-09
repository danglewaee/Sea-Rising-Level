from pathlib import Path


def create_project(package_dir: str, out_project: str | None = None):
    try:
        from qgis.core import (
            QgsCoordinateReferenceSystem,
            QgsProject,
            QgsRasterLayer,
            QgsVectorLayer,
        )
    except ImportError as exc:
        raise RuntimeError("Run this script inside QGIS Python Console (PyQGIS required).") from exc

    pkg = Path(package_dir).resolve()
    if not pkg.exists():
        raise FileNotFoundError(str(pkg))

    layers_dir = pkg / "layers"
    styles_dir = pkg / "styles"

    project = QgsProject.instance()
    project.clear()
    project.setCrs(QgsCoordinateReferenceSystem("EPSG:4326"))

    # 1) DEM
    dem_candidates = list(layers_dir.glob("*.tif"))
    if not dem_candidates:
        raise FileNotFoundError("No DEM .tif found in package layers folder")
    dem_path = dem_candidates[0]
    dem_layer = QgsRasterLayer(str(dem_path), "dem")
    if not dem_layer.isValid():
        raise RuntimeError(f"Invalid DEM layer: {dem_path}")
    project.addMapLayer(dem_layer, True)

    # 2) Vector layers in recommended order
    layer_specs = [
        ("flood_plus_20cm", "flood_plus_20cm.geojson", "flood_plus_20cm.qml"),
        ("flood_plus_50cm", "flood_plus_50cm.geojson", "flood_plus_50cm.qml"),
        ("flood_plus_100cm", "flood_plus_100cm.geojson", "flood_plus_100cm.qml"),
        ("hotspots", "hotspots.geojson", "hotspots.qml"),
    ]

    created = [dem_layer]

    for name, file_name, style_name in layer_specs:
        p = layers_dir / file_name
        if not p.exists():
            continue

        lyr = QgsVectorLayer(str(p), name, "ogr")
        if not lyr.isValid():
            continue

        style = styles_dir / style_name
        if style.exists():
            lyr.loadNamedStyle(str(style))
            lyr.triggerRepaint()

        project.addMapLayer(lyr, True)
        created.append(lyr)

    # 3) Layer order (bottom -> top)
    root = project.layerTreeRoot()
    order_ids = [l.id() for l in created]
    root.setCustomLayerOrderByIds(order_ids)
    root.setHasCustomLayerOrder(True)

    # 4) Save project
    if out_project is None:
        out_project = str(pkg / "anti_flood_template.qgz")
    out_path = Path(out_project)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    ok = project.write(str(out_path))
    if not ok:
        raise RuntimeError(f"Failed to write QGIS project: {out_path}")

    return str(out_path)


# Example usage in QGIS Python Console:
# from Backend.sea_level_risk.qgis.create_qgis_template import create_project
# create_project(r"D:\CODE\Projects\Sea_Level_Rise - New ver\Backend\sea_level_risk\outputs\qgis_packages\honolulu_20260308_184339")
