#!/usr/bin/env python3
"""Fuente única (Estándar SEO GMBH 2.0, OF 8): Google Sheet "01 — BUSINESS TRUTH / Menu & Prices" → contenido.json.
Mismo método que Mu Burgerhouse. La hoja manda en: nombre, descripción, precio, disponible, vegetariano y vegano
de los platillos que YA existen en contenido.json (por `id`). No crea platillos: un id desconocido detiene el proceso
para que una persona lo revise en el Pull Request.

Columnas (encabezados exactos, como las genera tools/menu_to_csv.py):
  id | seccion | platillo_es | platillo_en | descripcion_es | descripcion_en | precio | disponible | vegetariano | vegano
  - disponible = "no" oculta el platillo del sitio (se conserva en los datos).
  - vegetariano / vegano = "sí" o "no" (etiqueta en el menú y suitableForDiet en el JSON-LD).
Uso:  python3 tools/sheet_to_contenido.py --csv-url "$SHEET_CSV_URL"   (o --csv archivo.csv)
"""
import argparse, csv, io, json, sys, urllib.request
ap = argparse.ArgumentParser()
ap.add_argument("--csv-url"); ap.add_argument("--csv"); ap.add_argument("--contenido", default="contenido.json")
a = ap.parse_args()
raw = open(a.csv, encoding="utf-8").read() if a.csv else urllib.request.urlopen(a.csv_url, timeout=30).read().decode("utf-8")
rows = list(csv.DictReader(io.StringIO(raw.lstrip("﻿"))))
C = json.load(open(a.contenido, encoding="utf-8"))
by_id = {i["id"]: i for s in C["menu"]["secciones"] for b in s["bloques"] for i in b["items"]}
SI = ("sí", "si", "yes", "1", "true", "x")
def num(v):
    v = (v or "").strip().replace("$", "").replace(",", "")
    return int(float(v)) if v else None
def flag(tags, tag, on):
    if on and tag not in tags: tags.append(tag); return True
    if not on and tag in tags: tags.remove(tag); return True
    return False
cambios, desconocidos = [], []
for r in rows:
    rid = (r.get("id") or "").strip()
    if not rid: continue
    if rid not in by_id: desconocidos.append(rid); continue
    it = by_id[rid]
    disp = (r.get("disponible") or "sí").strip().lower() in SI
    if it.get("disponible", True) != disp:
        cambios.append(f"{rid}: disponible {it.get('disponible', True)} → {disp}")
        if disp: it.pop("disponible", None)
        else: it["disponible"] = False
    p = num(r.get("precio"))
    if p is not None and it.get("p") != p: cambios.append(f"{rid}: precio {it.get('p')} → {p}"); it["p"] = p
    for lg in ("es", "en"):
        n = (r.get(f"platillo_{lg}") or "").strip()
        if n and it["n"][lg] != n: cambios.append(f"{rid}: nombre {lg} «{it['n'][lg]}» → «{n}»"); it["n"][lg] = n
        d = (r.get(f"descripcion_{lg}") or "").strip()
        if d and (it.get("d") or {}).get(lg) != d: it.setdefault("d", {})[lg] = d; cambios.append(f"{rid}: descripción {lg}")
    tags = it.setdefault("tags", [])
    vegano = (r.get("vegano") or "").strip().lower() in SI
    vege = (r.get("vegetariano") or "").strip().lower() in SI and not vegano
    if flag(tags, "vegan", vegano): cambios.append(f"{rid}: vegano → {vegano}")
    if flag(tags, "veg", vege): cambios.append(f"{rid}: vegetariano → {vege}")
    if not tags: it.pop("tags")
if desconocidos:
    print("IDs en la hoja que no existen en contenido.json (alta manual):", ", ".join(desconocidos), file=sys.stderr); sys.exit(2)
json.dump(C, open(a.contenido, "w", encoding="utf-8"), ensure_ascii=False, indent=2); open(a.contenido, "a").write("\n")
print("\n".join(cambios) if cambios else "Sin cambios")
