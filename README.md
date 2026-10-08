# Las bibliotecas de las misiones jesuíticas de la Sudamérica hispánica (1767–1768)

Visualización interactiva de los inventarios de las bibliotecas de 74 misiones jesuíticas de Sudamérica, levantados después de la expulsión de la Compañía de Jesús (1767–1768): dónde estaban, cuánto tenían, qué temas, títulos y autores reunían. Incluye la transcripción completa de los inventarios.

*Interactive visualization of the library inventories of 74 Jesuit missions in Spanish South America, drawn up after the expulsion of the Society of Jesus (1767–1768). The site is in Spanish; the data files use English column names.*

Sitio: https://vegafabianr.github.io/jesuit-missionary-libraries/

## Contenido

- `index.html`: el sitio completo, en un solo archivo, con los datos incrustados. Se puede abrir sin conexión.
- `datos/`: los datos en CSV.
  - `books.csv`: un asiento de inventario por fila (misión, documento, folio, volúmenes, formato, autor, título y tópico identificados).
  - `authors.csv`: autores identificados, con nacimiento, muerte e institución.
  - `institutions.csv`: cada institución y su pertenencia (jesuitas, otras órdenes, clero secular…).
  - `missions.csv` y `mission_groups.csv`: misiones y conjuntos misionales, con fundación y coordenadas.
  - En todas las columnas, `-` significa que el dato no puede saberse y la celda vacía, que todavía no se trabajó.
- `datos_geo/sudamerica.json`: mapa base, a partir de [Natural Earth](https://www.naturalearthdata.com/).
- `scripts/exportar_datos.py`: incrusta los CSV en `index.html` (`python scripts/exportar_datos.py`; necesita pandas).
- `scripts/preparar_geo.py`: regenera el mapa base (necesita shapely e internet).

## Cómo citar

Vega, Fabián R. (2026). *Las bibliotecas de las misiones jesuíticas de la Sudamérica hispánica (1767–1768)* [sitio web, versión 1.0]. GitHub. https://github.com/vegafabianr/jesuit-missionary-libraries. DOI: pendiente.

## Licencias

- Código: MIT (`LICENSE`).
- Datos (`datos/`): CC BY 4.0 (`LICENSE-DATA`).
- La imagen del inventario de Itapúa (Archivo General de la Nación, Argentina, Sala IX) se reproduce con permiso del AGN y no está cubierta por estas licencias.
- Los logos de la Unión Europea y de la Universidad Complutense de Madrid pertenecen a sus titulares.
- D3 (https://d3js.org) va incrustado en `index.html` bajo su propia licencia ISC.

## Financiación

Este proyecto ha recibido financiación del programa de investigación e innovación Horizonte Europa de la Unión Europea en virtud del acuerdo de subvención Marie Skłodowska-Curie n.º 101200600, JesLibSouth: *Books in the Borderlands of the Iberian Worlds: Jesuit Libraries and Cultural Transformation in South America (17th and 18th Centuries)*.
