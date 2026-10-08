"""Reads the CSV files in datos/ and embeds them in the site's HTML page.

The data go between the markers /*DATOS:INICIO*/ and /*DATOS:FIN*/.
CSV convention: "-" = cannot be known; empty cell = not worked on yet.
Run it again whenever the CSV files change:  python scripts/exportar_datos.py
"""
import json
import re
from collections import Counter
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parent.parent
DATOS = RAIZ / "datos"
# Pages that carry the embedded data (the ones that do not exist are skipped):
PAGINAS = [RAIZ / "web" / "index.html", RAIZ / "index.html"]


def valor(s):
    """CSV text -> None (empty), integer, decimal, boolean or text: "1612" -> 1612, "" -> None."""
    if s == "":
        return None
    if re.fullmatch(r"-?\d+", s):
        return int(s)
    if re.fullmatch(r"-?\d+\.\d+", s):
        return float(s)
    if s in ("True", "False"):
        return s == "True"
    return s


def leer(nombre):
    df = pd.read_csv(DATOS / f"{nombre}.csv", dtype=str, keep_default_na=False)
    return {c: [valor(s) for s in df[c]] for c in df.columns}


TABLAS = ["books", "authors", "missions", "mission_groups", "institutions"]
FUENTES = {t: leer(t) for t in TABLAS}


def columna(valores):
    """A text column with few distinct values becomes a dictionary plus indices:
    ["Folio", "Quarto", "Folio"] -> {"v": ["Folio", "Quarto"], "i": [0, 1, 0]}."""
    distintos = list(dict.fromkeys(valores))
    if len(valores) < 50 or len(distintos) > len(valores) / 4 or not all(v is None or isinstance(v, str) for v in distintos):
        return valores
    pos = {v: k for k, v in enumerate(distintos)}
    return {"v": distintos, "i": [pos[v] for v in valores]}


def tabla(t, columnas):
    """One list per column, {internal name: [values]}, instead of one object per row."""
    return {interno: columna(FUENTES[t][c]) for c, interno in columnas.items()}


# Columns of each CSV -> internal name (the one the JavaScript reads):
INTERNOS = {
    "books": {
        "id": "id", "mission": "mision", "entry_text": "registro",  # the mission group comes from the mission
        "document": "archivo", "folio": "folio", "volumes": "vols", "format": "formato",
        "author": "autor", "title": "titulo", "topic": "topico", "about_americas": "america",
        # Topic according to the inventory itself (Guarani missions only) and production in the Americas:
        "inventory_topic": "topicoInv", "local_production": "local",
        # Heading of the inventory where the entry appears (section titles in the reading of the documents):
        "inventory_heading": "categoria",
    },
    "authors": {
        "author": "autor", "birth_year": "anioNac", "birth_year_certainty": "anioNacCerteza",
        "birth_city": "ciudadNac", "birth_country": "paisNac",
        "death_year": "anioMuerte", "death_year_certainty": "anioMuerteCerteza",
        "death_city": "ciudadMuerte", "death_country": "paisMuerte",
        "institution": "institucion", "been_in_americas": "americaAutor",
    },
    "missions": {
        "mission": "mision", "mission_group": "conjunto", "foundation_year": "fundacion",
        "latitude": "lat", "longitude": "lon",
    },
    "mission_groups": {
        "mission_group": "conjunto", "foundation_year": "fundacion", "province": "provincia",
        "general_language": "lenguaGeneral", "consolidation": "consolidacion",
        "printed_indigenous_books": "impresosIndigenas",
        # Centroid of each mission group (where the map places it in the view by group):
        "centroid_latitude": "lat", "centroid_longitude": "lon",
    },
}

DESCRIPCION = {"books": "libros (asientos)", "authors": "autores", "missions": "misiones",
               "mission_groups": "conjuntos misionales", "institutions": "instituciones"}
# Relations: citing table and column (many rows) -> cited table and column (one row).
# Institutions are a table of their own (third normal form): the affiliation depends on the
# institution, not on the author.
RELACIONES = [("books", "mission", "missions", "mission"), ("missions", "mission_group", "mission_groups", "mission_group"),
              ("books", "author", "authors", "author"), ("authors", "institution", "institutions", "institution")]
# Primary key of each table (unique and never empty):
PK = {"books": "id", "authors": "author", "missions": "mission", "mission_groups": "mission_group", "institutions": "institution"}
vacio = lambda x: x is None or x == "-"


def tipo(valores):
    """Type of a column from its values, leaving out "-" and empty cells."""
    v = [x for x in valores if not vacio(x)]
    if v and all(isinstance(x, bool) for x in v):
        return "boolean"
    if v and all(isinstance(x, int) and not isinstance(x, bool) for x in v):
        return "integer"
    if v and all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in v):
        return "decimal"
    return "text"


# Checks that every primary key is unique and complete:
for t, c in PK.items():
    v = FUENTES[t][c]
    repetidas = [x for x, n in Counter(v).items() if n > 1]
    falta = sum(x is None for x in v)  # "-" is a valid key: the row for the authors that cannot be known
    if repetidas or falta:
        print(f"Revisar clave primaria {t}.{c}: {len(repetidas)} repetidas {repetidas[:5]}, {falta} vacías")


def cardinalidad(t, c, u, d):
    """Minimum on each side of a relation, from the data, and values with no row in the cited table."""
    hijo = FUENTES[t][c]
    padres = set(FUENTES[u][d])
    usados = set(x for x in hijo if not vacio(x))
    huerfanos = sorted(map(str, usados - padres))
    if huerfanos:
        print(f"Revisar {t}.{c} -> {u}.{d}: {len(huerfanos)} valores sin fila en {u}: {huerfanos[:6]}")
    return {"minHijo": 0 if any(map(vacio, hijo)) else 1,   # does every row of t cite a row of u?
            "minPadre": 1 if padres <= usados else 0}       # is every row of u cited by some row of t?


esquema = {
    "tablas": [{"id": t, "nombre": t, "desc": DESCRIPCION[t], "filas": len(FUENTES[t][PK[t]]),
                "columnas": list(FUENTES[t]), "tipos": [tipo(v) for v in FUENTES[t].values()],
                "pk": PK[t]} for t in TABLAS],
    "relaciones": [{"de": t, "col": c, "a": u, "colA": d, **cardinalidad(t, c, u, d)} for t, c, u, d in RELACIONES],
}

datos = {
    "libros": tabla("books", INTERNOS["books"]),
    "autores": tabla("authors", INTERNOS["authors"]),
    "misiones": tabla("missions", INTERNOS["missions"]),
    "conjuntos": tabla("mission_groups", INTERNOS["mission_groups"]),
    "pertenencias": dict(zip(FUENTES["institutions"]["institution"], FUENTES["institutions"]["affiliation"])),
    # Schema of the CSV files, drawn on the page about how the data are organized:
    "esquema": esquema,
    # Base map, made by scripts/preparar_geo.py:
    "geo": json.loads((RAIZ / "datos_geo" / "sudamerica.json").read_text(encoding="utf-8")),
}

js = json.dumps(datos, ensure_ascii=False, separators=(",", ":"))
for pagina in PAGINAS:
    if not pagina.exists():
        continue
    html = pagina.read_text(encoding="utf-8")
    html, n = re.subn(r"/\*DATOS:INICIO\*/.*?/\*DATOS:FIN\*/",
                      lambda _: f"/*DATOS:INICIO*/{js}/*DATOS:FIN*/", html, flags=re.S)
    assert n == 1, f"No encontré los marcadores de datos en {pagina}"
    pagina.write_text(html, encoding="utf-8")

print(f"Datos incrustados: {len(js) / 1e6:.2f} MB")
