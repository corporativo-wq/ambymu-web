#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genera ambymu.mx a partir de contenido.json (fuente única de verdad) + src/ (diseño).
Uso:  python3 build.py        (requiere: pip install jinja2 pillow)
Salida en la raíz del repo (lo que publica GitHub Pages): index.html, menu.html,
playa-del-carmen.html, 404.html, assets/, img/, robots.txt, sitemap.xml, favicon, og.jpg.
"""
import json, re, os, math, hashlib, html, datetime
from urllib.parse import quote
from jinja2 import Environment, BaseLoader, TemplateNotFound
from markupsafe import Markup
from PIL import Image
import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
os.chdir(ROOT)
C = json.load(open("contenido.json", encoding="utf-8"))
S, M, SEO = C["sitio"], C["marca"], C["seo"]
D = S["dominio"].rstrip("/")
BR = C["sucursales"][0]

# ------------------------------------------------------------------ colores
# Hex con los que está escrito el diseño en src/. Se reemplazan por los de contenido.json.
DEFAULT_HEX = {"verde": "#1E4029", "verde_2": "#2C5838", "matcha": "#A8C47F", "blush": "#F8D7DF",
               "rosa": "#F6B0C8", "rosa_fuerte": "#EC5A98", "crema": "#F7F0E3", "naranja": "#F29A5B"}
COL = M["colores"]
def recolor(txt):
    for k, dflt in DEFAULT_HEX.items():
        new = COL.get(k, dflt)
        if new.lower() != dflt.lower():
            txt = re.sub(re.escape(dflt), new, txt, flags=re.I)
    return txt
def rgb(h):
    h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

# ------------------------------------------------------------------ precios
P = C["precios"]; FACT = 1 + (P.get("ajuste_pct") or 0) / 100; RND = P.get("redondeo") or 1
def adj(p):
    if p is None or FACT == 1: return p
    return int(RND * round(p * FACT / RND))
def walk_prices(o):
    if isinstance(o, dict):
        for k, v in list(o.items()):
            if k in ("p", "precio") and isinstance(v, (int, float)): o[k] = adj(v)
            else: walk_prices(v)
    elif isinstance(o, list):
        for v in o: walk_prices(v)
walk_prices(C["menu"]); walk_prices(C["run_club"]); walk_prices(C["barra_libre_cafe"])
MENU, BL, RC = C["menu"], C["barra_libre_cafe"], C["run_club"]
ALL_ITEMS = [i for s in MENU["secciones"] for b in s["bloques"] for i in b["items"]]
BOTTOMLESS = next((i["p"] for i in ALL_ITEMS if "bottomless" in i["n"]["es"].lower()), None)

# ------------------------------------------------------------------ horario
DIAS = [("lun", 1, "Lunes", "Monday"), ("mar", 2, "Martes", "Tuesday"), ("mie", 3, "Miércoles", "Wednesday"),
        ("jue", 4, "Jueves", "Thursday"), ("vie", 5, "Viernes", "Friday"), ("sab", 6, "Sábado", "Saturday"),
        ("dom", 0, "Domingo", "Sunday")]
H = BR["horario"]
groups = {}
for k, n, es, en in DIAS:
    if H.get(k): groups.setdefault(tuple(H[k]), []).append((k, es, en))
closed = [(es, en) for k, n, es, en in DIAS if not H.get(k)]
main_h = max(groups.items(), key=lambda g: len(g[1]))[0] if groups else None
def hh(t): return t
HORARIO_RESUMEN = {
    "es": " · ".join(filter(None, [f"{main_h[0]}–{main_h[1]}" if main_h else "", ", ".join(e.lower() for e, _ in closed) + (" cerrado" if len(closed) == 1 else " cerrados") if closed else ""])),
    "en": " · ".join(filter(None, [f"{main_h[0]}–{main_h[1]}" if main_h else "", "closed " + ", ".join(e for _, e in closed) if closed else ""]))}
HORARIO_CHIP = {"es": f"Brunch todo el día · {main_h[0]}–{main_h[1]}", "en": f"Brunch all day · {main_h[0]}–{main_h[1]}"}
HORA_CORTA = f"{int(main_h[0][:2])}–{int(main_h[1][:2])}" if main_h else ""
CERRADO_TXT = {"es": "" if not closed else (", ".join(e for e, _ in closed) + (" cerrado" if len(closed) == 1 else " cerrados")),
               "en": "" if not closed else ("Closed " + ", ".join(e for _, e in closed))}
EN_DAY = {k: en for k, n, es, en in DIAS}
OPENING = [{"@type": "OpeningHoursSpecification", "dayOfWeek": [EN_DAY[k] for k, _, _ in days], "opens": h[0], "closes": h[1]}
           for h, days in groups.items()]

a = BR["direccion"]
DIR_TXT = f'{a["calle"]}, {a["colonia"]}, {a["cp"]} {a["ciudad"]}, Q.R.'

# ------------------------------------------------------------------ FAQ con precios vivos
FAQ = json.loads(json.dumps(C["faq"]).replace("${barra}", f"${BL['precio']}").replace("${bottomless}", f"${BOTTOMLESS}"))

# ------------------------------------------------------------------ JSON-LD
ORG = {"@type": "Organization", "@id": D + "/#org", "name": S["nombre"], "url": D + "/", "logo": D + "/favicon.png",
       "sameAs": [v for v in C["redes"].values() if v]}
SITE = {"@type": "WebSite", "@id": D + "/#website", "url": D + "/", "name": S["nombre"], "inLanguage": [S["idioma"], "en"], "publisher": {"@id": D + "/#org"}}
REST = {"@type": "Restaurant", "@id": D + "/#restaurant", "name": S["nombre"], "url": D + "/" + BR["slug"],
        "image": D + SEO["og_imagen"], "logo": D + "/favicon.png", "priceRange": "$$",
        "servesCuisine": ["Brunch", "Desayunos", "Mexicana", "Café de especialidad"],
        "address": {"@type": "PostalAddress", "streetAddress": f'{a["calle"]}, {a["colonia"]}', "addressLocality": a["ciudad"],
                    "addressRegion": a["estado"], "postalCode": a["cp"], "addressCountry": a["pais"]},
        "geo": {"@type": "GeoCoordinates", "latitude": BR["geo"]["lat"], "longitude": BR["geo"]["lng"]},
        "hasMap": BR["maps_url"], "openingHoursSpecification": OPENING,
        "menu": D + "/menu", "hasMenu": {"@id": D + "/menu#menu"},
        "acceptsReservations": bool(BR.get("reservas")),
        "sameAs": [v for v in C["redes"].values() if v], "brand": {"@id": D + "/#org"}}
if BR.get("telefono"): REST["telephone"] = BR["telefono"]
def msec(s, lg="es"):
    out = []
    for b in s["bloques"]:
        out.append({"@type": "MenuSection", "name": b["titulo"][lg], "hasMenuItem": [
            {"@type": "MenuItem", "name": i["n"][lg], **({"description": i["d"][lg]} if i.get("d") else {}),
             "offers": {"@type": "Offer", "price": str(i["p"]), "priceCurrency": P["moneda"]},
             **({"suitableForDiet": "https://schema.org/VeganDiet"} if "vegan" in (i.get("tags") or []) else {}),
             **({"suitableForDiet": "https://schema.org/GlutenFreeDiet"} if "gf" in (i.get("tags") or []) else {})}
            for i in b["items"]]})
    return out
def MENU_LD(lg):
    u = D + ("/en" if lg == "en" else "") + "/menu"
    return {"@type": "Menu", "@id": u + "#menu", "name": (f'Menú {S["nombre"]}' if lg == "es" else f'{S["nombre"]} menu'), "url": u,
            "inLanguage": "es-MX" if lg == "es" else "en", "hasMenuSection": [x for s in MENU["secciones"] for x in msec(s, lg)]}
def crumbs(*pairs):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(pairs)]}
def FAQ_LD(lg): return {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": f["q"][lg], "acceptedAnswer": {"@type": "Answer", "text": f["a"][lg]}} for f in FAQ]}
def ld(*nodes): return Markup(json.dumps({"@context": "https://schema.org", "@graph": list(nodes)}, ensure_ascii=False).replace("</", "<\\/"))

# ------------------------------------------------------------------ imágenes (webp, externas)
os.makedirs("img", exist_ok=True); os.makedirs("assets", exist_ok=True)
mask = np.array(Image.open(f"{SRC}/img/logo-mask.png").convert("RGBA"))
def logo(col, path, w=None):
    arr = mask.copy(); arr[..., :3] = rgb(col); im = Image.fromarray(arr)
    if w: im = im.resize((w, int(im.height * w / im.width)), Image.LANCZOS)
    im.save(path, quality=90, method=6); return im
logo(COL["verde"], "img/logo-green.webp", 240)
logo(COL["rosa"], "img/logo-pink.webp", 260)
am = Image.fromarray(mask).crop((0, 0, 440, 272)); arr = np.array(am); arr[..., :3] = rgb(COL["rosa"]); am = Image.fromarray(arr)
am = am.resize((400, int(am.height * 400 / am.width)), Image.LANCZOS)
fav = Image.new("RGBA", (512, 512), rgb(COL["verde"]) + (255,)); fav.alpha_composite(am, (56, (512 - am.height) // 2))
fav.resize((192, 192), Image.LANCZOS).save("favicon.png", optimize=True)
fav.resize((180, 180), Image.LANCZOS).convert("RGB").save("apple-touch-icon.png", optimize=True)
ph = Image.open(f"{SRC}/img/hero-src.jpg").convert("RGB")
hero = ph.crop((0, 700, 847, 1900)); hero.resize((600, int(1200 * 600 / 847)), Image.LANCZOS).save("img/hero.webp", quality=72, method=6)
hero.save("img/hero-2x.webp", quality=70, method=6)  # 847 px de ancho, para pantallas retina
os.makedirs("img/platos", exist_ok=True)
for i in ALL_ITEMS:  # fotos reales de platillos (campo "foto" en contenido.json); null = sin imagen
    if i.get("foto"):
        slug = re.sub(r"[^a-z0-9]+", "-", i["n"]["es"].lower().replace("ñ", "n")).strip("-")
        im = Image.open(i["foto"]).convert("RGB"); s_ = min(im.size)
        im = im.crop(((im.width - s_) // 2, (im.height - s_) // 2, (im.width + s_) // 2, (im.height + s_) // 2)).resize((600, 600), Image.LANCZOS)
        i["foto_web"] = f"img/platos/{slug}.webp"; im.save(i["foto_web"], quality=74, method=6)
Image.open(f"{SRC}/img/og-src.jpg").convert("RGB").resize((1200, 630)).save("og.jpg", quality=80, optimize=True)

# ------------------------------------------------------------------ CSS / JS
def mincss(s):
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S); s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\s*([{};:,>])\s*", r"\1", s); return s.replace(";}", "}").strip()
def minjs(s):
    return "\n".join(l.strip() for l in s.splitlines() if l.strip() and not l.strip().startswith("/*") and not l.strip().startswith("//"))
# tipografías servidas desde el propio sitio (Fontsource, licencia OFL; subconjunto latino: cubre español)
os.makedirs("assets/fonts", exist_ok=True)
FONT_FACES = [("Anton", 400, "anton-latin-400-normal.woff2"), ("Bagel Fat One", 400, "bagel-fat-one-latin-400-normal.woff2"),
              ("Caveat", 700, "caveat-latin-700-normal.woff2")] + [("Jost", w, f"jost-latin-{w}-normal.woff2") for w in (400, 500, 600, 700, 800)]
for _, _, fn in FONT_FACES: assert os.path.exists(f"assets/fonts/{fn}"), fn  # las fuentes viven en assets/fonts (fuente única)
FONT_CSS = "".join(f'@font-face{{font-family:"{fam}";font-style:normal;font-weight:{w};font-display:swap;src:url(/assets/fonts/{fn}) format("woff2")}}' for fam, w, fn in FONT_FACES)
site_css = FONT_CSS + recolor(mincss(open(f"{SRC}/css/base.css").read() + open(f"{SRC}/css/cursor.css").read()))
menu_css = recolor(mincss(open(f"{SRC}/css/menu.css").read()))
site_js = recolor(minjs(open(f"{SRC}/site.js").read())).replace("__GA4_ID__", S.get("ga4_id") or ""); menu_js = minjs(open(f"{SRC}/menu.js").read())
open("assets/site.css", "w").write(site_css); open("assets/menu.css", "w").write(menu_css)
open("assets/site.js", "w").write(site_js); open("assets/menu.js", "w").write(menu_js)
V = hashlib.md5((site_css + menu_css + site_js + menu_js).encode()).hexdigest()[:8]

# ------------------------------------------------------------------ plantillas
BI = re.compile(r"\{BI:([^|}]*)\|([^}]*)\}")
def bi_pass(t, lg):  # {BI:es|en} → solo el texto del idioma que se está generando
    return BI.sub(lambda m: m.group(1) if lg == "es" else m.group(2), t)
class Loader(BaseLoader):
    def __init__(self, lg): self.lg = lg
    def get_source(self, env, name):
        p = os.path.join(SRC, "tpl", name)
        if not os.path.exists(p): raise TemplateNotFound(name)
        return bi_pass(open(p, encoding="utf-8").read(), self.lg), p, lambda: True
def make_env(lg):
    env = Environment(loader=Loader(lg), autoescape=True, trim_blocks=False)
    env.filters["digits"] = lambda s: re.sub(r"\D", "", s or "")
    env.filters["tel"] = lambda s: "+" + re.sub(r"\D", "", s or "") if s else ""
    env.filters["urlencode"] = lambda s: quote(s or "")
    return env
f = M["tipografias"]
FONTS_URL = "https://fonts.googleapis.com/css2?family=" + f["poster"].replace(" ", "+") + "&family=" + f["groovy"].replace(" ", "+") + "&family=" + f["mano"].replace(" ", "+") + ":wght@700&family=" + f["texto"].replace(" ", "+") + ":wght@400;500;600;700;800&display=swap"
SIGNATURES = [i for i in ALL_ITEMS if i.get("signature")]
DESTACADOS = [i for i in ALL_ITEMS if i.get("destacado")]
sec = {s["id"]: s for s in MENU["secciones"]}
COUNT = {k: sum(len(b["items"]) for b in s["bloques"]) for k, s in sec.items()}
MINP = {k: min(i["p"] for b in s["bloques"] for i in b["items"]) for k, s in sec.items()}
G = dict(S=S, SEO=SEO, M=M, R=C["redes"], BR=BR, BL=BL, RC=RC, MENU=MENU, TX=C["textos"], FAQ=FAQ, DIAS=DIAS,
         TAGS={"new": {"es": "Nuevo", "en": "New"}, "vegan": {"es": "Vegano", "en": "Vegan"}, "gf": {"es": "Sin gluten", "en": "Gluten free"}},
         HORARIO_RESUMEN=HORARIO_RESUMEN, HORARIO_CHIP=HORARIO_CHIP, HORA_CORTA=HORA_CORTA, CERRADO_TXT=CERRADO_TXT,
         DIR_TXT=DIR_TXT, SIGNATURES=SIGNATURES, DESTACADOS=DESTACADOS, COUNT=COUNT, MINP=MINP, BOTTOMLESS=BOTTOMLESS, V=V, FONTS_URL=FONTS_URL,
         MAPS_EMBED="https://www.google.com/maps?q=" + quote(f'{S["nombre"]}, {a["calle"]}, {a["colonia"]}, {a["cp"]} {a["ciudad"]}') + "&z=17&output=embed",
         BURST=open(f"{SRC}/burst.txt").read().strip(), SPIKY=open(f"{SRC}/burst_spiky.txt").read().strip())
SLUG = "/" + BR["slug"]
REST_MIN = {"@id": D + "/#restaurant", "@type": "Restaurant", "name": S["nombre"]}
sizes = {}
for lg in ("es", "en"):
    env = make_env(lg); L = "" if lg == "es" else "/en"
    T = lambda o: o[lg] if isinstance(o, dict) else o
    GL = dict(G, LANG=lg, L=L)
    ptxt = env.get_template("_posters.html").render(**GL)
    POSTERS = {m.group(1): Markup(m.group(0)) for m in re.finditer(r'<div data-poster="(\w+)".*?\n</div>', ptxt, re.S)}
    HOME, MEN = ("Inicio", "Menú") if lg == "es" else ("Home", "Menu")
    PAGES = [
        ("index.html", "inicio.html", "/", dict(id="inicio", title=T(SEO["inicio"]["title"]), description=T(SEO["inicio"]["description"]), og_type="restaurant",
            ld=ld(ORG, SITE, REST) if lg == "es" else ld(REST))),
        ("menu.html", "menu.html", "/menu", dict(id="menu", title=T(SEO["menu"]["title"]), description=T(SEO["menu"]["description"]),
            ld=ld(MENU_LD(lg), crumbs((HOME, D + L + "/"), (MEN, D + L + "/menu")), dict(REST_MIN, hasMenu={"@id": D + L + "/menu#menu"})))),
        (BR["slug"] + ".html", "sucursal.html", SLUG, dict(id="sucursal", title=T(SEO["sucursal"]["title"]), description=T(SEO["sucursal"]["description"]), og_type="restaurant",
            ld=ld(REST, crumbs((HOME, D + L + "/"), (BR["ciudad"], D + L + SLUG)), FAQ_LD(lg)))),
    ]
    if lg == "es":
        PAGES.append(("404.html", "404.html", "/404", dict(id="404", title=f'Página no encontrada · {S["nombre"]}', description="Esta página no existe.", robots="noindex,follow", ld=None)))
    for out, tpl, path, page in PAGES:
        page["url"] = D + L + path
        alt = {"es": path, "en": ("/en" + path) if path != "/" else "/en/"}
        outp = out if lg == "es" else "en/" + out
        os.makedirs(os.path.dirname(outp) or ".", exist_ok=True)
        htmltxt = env.get_template(tpl).render(page=page, POSTERS=POSTERS, ALT=alt, **GL)
        htmltxt = recolor(re.sub(r">\s+<", "> <", re.sub(r"\n\s*", "\n", htmltxt)))
        open(outp, "w", encoding="utf-8").write(htmltxt); sizes[outp] = len(htmltxt.encode())

today = datetime.date.today().isoformat()
urls = [("/", "weekly", "1.0"), ("/menu", "weekly", "0.9"), (SLUG, "monthly", "0.8")]
def alts(u):
    en = "/en/" if u == "/" else "/en" + u
    return (f'<xhtml:link rel="alternate" hreflang="es-MX" href="{D}{u}"/><xhtml:link rel="alternate" hreflang="en" href="{D}{en}"/>'
            f'<xhtml:link rel="alternate" hreflang="x-default" href="{D}{u}"/>'), en
rows = []
for u, c, p in urls:
    al, en = alts(u)
    rows.append(f"<url><loc>{D}{u}</loc><lastmod>{today}</lastmod><changefreq>{c}</changefreq><priority>{p}</priority>{al}</url>")
    rows.append(f"<url><loc>{D}{en}</loc><lastmod>{today}</lastmod><changefreq>{c}</changefreq><priority>{p}</priority>{al}</url>")
open("sitemap.xml", "w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + "\n".join(rows) + "\n</urlset>\n")
open("robots.txt", "w").write(f"User-agent: *\nAllow: /\nSitemap: {D}/sitemap.xml\n")
open("CNAME", "w").write(D.split("//")[1] + "\n")
open(".nojekyll", "w").write("")
for k, v in sizes.items(): print(f"{k:28s} {v/1024:6.1f} KB")
for k in ["assets/site.css", "assets/menu.css", "assets/site.js", "assets/menu.js", "img/hero.webp", "img/hero-2x.webp", "img/logo-green.webp", "img/logo-pink.webp", "og.jpg"]:
    print(f"{k:28s} {os.path.getsize(k)/1024:6.1f} KB")
