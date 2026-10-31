# ambymu.mx — sitio oficial de AM by Mu (brunch & coffee bar, Calle 38, Playa del Carmen)

Publica con **GitHub Pages** desde `main` (raíz). Los HTML de la raíz se GENERAN: no los edites a mano.

## Cómo cambiar algo
1. Edita **`contenido.json`** (fuente única de verdad): nombre, colores, tipografías, menú y precios, horarios,
   teléfono/WhatsApp, redes, pedidos, textos, SEO y FAQ. Campos `null` no se muestran (nunca se inventa relleno).
   - Todos los precios +15 %: `"precios": {"ajuste_pct": 15}` (redondea al múltiplo de `redondeo`).
   - Cambiar un color en todo el sitio (CSS, SVG, logo, favicon): `marca.colores.<clave>`.
   - GA4: `sitio.ga4_id` (p. ej. `G-XXXX`). Search Console por meta: `sitio.search_console_meta`.
2. `./build.sh` (python3 + `pip install jinja2 pillow numpy`).
3. `git add -A && git commit -m "…" && git push`. Pages publica en ~1 min.

## Estructura
- `src/tpl/` plantillas Jinja (`inicio`, `menu`, `sucursal`, `404`, `_base`, `_macros`, `_posters`). `{BI:es|en}` = texto bilingüe.
- Idiomas: el build genera español en la raíz (`/`, `/menu`, `/playa-del-carmen`) e inglés en `/en/` con hreflang y sitemap con alternates. El selector ES/EN son enlaces (sin redirección automática).
- Videos de platillos: campo `video` del platillo (`mp4`, `webm` opcional, `poster`; H.264 basta para Safari, Chrome y Firefox) con archivos ya optimizados en `video/` (540×960, ~9 s, sin audio, ~1 MB; no se generan). Salen en la sección «Nuevos» del inicio y en la tira de videos de su sección del menú; se cargan solo al verse.
- Fotos de platillos: campo `foto` del platillo en `contenido.json` (solo fotos reales; null = sin imagen). Destacados de la home: `destacado: true`.
- Tipografías en `assets/fonts/` (Fontsource, OFL, subconjunto latino); no se generan, se editan ahí.
- `src/css/` estilos (se escriben con los hex por defecto; el build los sustituye por los de `contenido.json`).
- `src/site.js` (idioma, eventos, cursor) y `src/menu.js` (pestañas). `src/img/` originales → `img/*.webp`.

## Estándar SEO GMBH 2.0 (aprobado 29 oct 2026)
- Títulos, description y H1 por página: `contenido.json → seo.<pagina>.title / description / h1` (≤60 / ≤155). El H1 es texto visible; los títulos de póster ("Buenas mañanas", "Calle 38") son `<p aria-hidden>`.
- Texto de desayunos (portada y sucursal): `textos.desayunos`. Variables que el build reemplaza: `${horario_texto_es|en}`, `${barra}`, `${express}`, `${bottomless}`, `${whatsapp}`, `${delivery_es|en}`, `${horario_faq_es|en}`.
- FAQ visibles + FAQPage: `faq` (mismas preguntas en las dos).
- Sucursal: `reservas.activo` (→ acceptsReservations), `delivery.activo` (false = "Por ahora no…"; true + `pedidos` = botones), `desde`, `estacionamiento`, `pet_friendly`, `factura`.
- Dietas: etiquetas `veg` / `vegan` en el platillo (→ suitableForDiet). Si un vegetariano ofrece extras con carne, la etiqueta dice "sin extras de carne".
- Mapa: tarjeta estática (`map_card`); el iframe de Google solo se carga al tocar "Ver el mapa".
- GA4: snippet estándar asíncrono en el `<head>` (`_base.html`), ID en `sitio.ga4_id`. site.js solo manda los eventos de los CTA.
- robots.txt (política del punto 13), sitemap con lastmod, llms.txt y `/menu/` → `/menu` (carpeta `menu/` con meta refresh + canonical) los genera el build.
- Fuente única del menú: Google Sheet "2026-10-31 — Menú y precios — AM" (Drive › 10 — AM by MU › 01 — BUSINESS TRUTH › Menu & Prices). `tools/menu_to_csv.py` exporta; `tools/sheet_to_contenido.py` + `.github/workflows/menu-from-sheet.yml` traen los cambios de la hoja y abren un PR (requiere el secret `SHEET_CSV_URL`). Cada platillo tiene `id` fijo: no cambiarlo.

## Medición
Cada CTA lleva `data-ev` (`como_llegar`, `whatsapp`, `phone`, `order_*`, `menu_nav`, `branch_page`, `home_nav`, `review`, `social_*`)
y `data-branch`. Un clic = `dataLayer.push({event:'cta_click',…})` + `gtag('event', ev, {branch})`. Sin GTM (evita hits duplicados).

## Reglas
- No cambiar nombre, horarios ni datos del Perfil de Google sin aprobación de Fernando.
- Teléfono/WhatsApp actual: número de la capitana (temporal hasta tener Wati de AM). No usar números de otras marcas.
- No mencionar otras marcas del grupo en el sitio.
- GA4: eventos clave = como_llegar, whatsapp, phone, menu_nav (sin valor monetario).
