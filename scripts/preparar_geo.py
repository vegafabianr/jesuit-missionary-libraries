"""Builds the base map (coastline, main rivers, present-day borders and a world outline) from
Natural Earth (public domain) and saves it, simplified, in datos_geo/sudamerica.json.
exportar_datos.py then embeds it in the page.

Usage: python scripts/preparar_geo.py
Needs an internet connection (it downloads about 12 MB to a temporary folder) and the shapely library.
"""
import json
import tempfile
import urllib.request
from pathlib import Path

from shapely.geometry import box, mapping, shape
from shapely.ops import unary_union

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "datos_geo" / "sudamerica.json"
BASE = "https://cdn.jsdelivr.net/gh/nvkelso/natural-earth-vector@v5.1.2/geojson/"

# Box around all the missions, with a margin (lon, lat):
RECUADRO = box(-86, -47, -32, 14)

# Rivers drawn on the map. In Natural Earth the Paraguay river is part of the Paraná line:
RIOS = {"Paraná", "Uruguay", "Amazonas", "Madeira", "Mamoré", "Guaporé", "Marañón", "Ucayali",
        "Napo", "Pilcomayo", "Bermejo", "Meta", "Orinoco", "Bío-Bío", "Beni", "Huallaga"}


def bajar(nombre, carpeta):
    destino = Path(carpeta) / f"{nombre}.geojson"
    urllib.request.urlretrieve(BASE + destino.name, destino)
    return json.loads(destino.read_text(encoding="utf-8"))


def redondear(geom, dec=2):
    """Coordinates rounded to 2 decimals (about 1 km): -58.38412 -> -58.38."""
    def r(c):
        return [round(c[0], dec), round(c[1], dec)] if isinstance(c[0], float) else [r(x) for x in c]
    g = mapping(geom)
    return {"type": g["type"], "coordinates": r(json.loads(json.dumps(g["coordinates"])))}


with tempfile.TemporaryDirectory() as tmp:
    tierra = bajar("ne_50m_land", tmp)
    rios = bajar("ne_10m_rivers_lake_centerlines", tmp)
    paises = bajar("ne_50m_admin_0_countries", tmp)
    mundo = bajar("ne_110m_land", tmp)

# Coastline of the continent:
contorno = unary_union([shape(f["geometry"]) for f in tierra["features"]]).intersection(RECUADRO)
contorno = contorno.simplify(0.03, preserve_topology=True)

# Rivers: only the chosen ones, and only main lines (scalerank <= 8), to leave out minor tributaries with the same name:
lineas = []
for f in rios["features"]:
    p = f["properties"]
    if p.get("name") in RIOS and p.get("scalerank", 99) <= 8:
        g = shape(f["geometry"]).intersection(RECUADRO)
        if not g.is_empty:
            lineas.append(g.simplify(0.02))
rios_geom = unary_union(lineas)

# Present-day borders: the lines between countries, without the coastline:
sud = [shape(f["geometry"]) for f in paises["features"]
       if f["properties"].get("CONTINENT") == "South America"]
bordes = unary_union([g.boundary for g in sud]).intersection(RECUADRO)
costa = unary_union([g for g in sud]).boundary.buffer(0.05)
fronteras = bordes.difference(costa).simplify(0.03)

# World outline for the maps of authors, from the Americas to Asia, much simplified:
MUNDO = box(-125, -58, 135, 68)
mundo_geom = unary_union([shape(f["geometry"]) for f in mundo["features"]]).intersection(MUNDO)
mundo_geom = mundo_geom.simplify(0.15, preserve_topology=True)

SALIDA.parent.mkdir(exist_ok=True)
SALIDA.write_text(json.dumps({
    "contorno": redondear(contorno),
    "rios": redondear(rios_geom),
    "fronteras": redondear(fronteras),
    "mundo": redondear(mundo_geom, 1),
}, separators=(",", ":")), encoding="utf-8")
print(f"Mapa base guardado: {SALIDA.stat().st_size / 1e3:.0f} kB")
