#!/usr/bin/env python3
"""Exporta el menú de contenido.json a CSV (una fila por platillo) para la Google Sheet de
"10 — AM by MU / 01 — BUSINESS TRUTH / Menu & Prices" (Estándar SEO GMBH 2.0, OF 8).

Uso:  python3 tools/menu_to_csv.py > menu-am.csv
Columnas: id | seccion | platillo_es | platillo_en | descripcion_es | descripcion_en | precio | disponible | vegetariano | vegano
- `id` NO se cambia en la hoja: es la llave para regresar los cambios a contenido.json.
"""
import csv, json, os, sys
C = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "contenido.json"), encoding="utf-8"))
w = csv.writer(sys.stdout)
w.writerow(["id", "seccion", "platillo_es", "platillo_en", "descripcion_es", "descripcion_en", "precio", "disponible", "vegetariano", "vegano"])
for s in C["menu"]["secciones"]:
    for b in s["bloques"]:
        for i in b["items"]:
            t = i.get("tags") or []
            w.writerow([i["id"], b["titulo"]["es"], i["n"]["es"], i["n"]["en"], (i.get("d") or {}).get("es", ""), (i.get("d") or {}).get("en", ""),
                        i["p"], "sí" if i.get("disponible", True) else "no", "sí" if ("veg" in t or "vegan" in t) else "no", "sí" if "vegan" in t else "no"])
