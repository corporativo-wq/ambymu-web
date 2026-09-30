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
- Fotos de platillos: campo `foto` del platillo en `contenido.json` (solo fotos reales; null = sin imagen). Destacados de la home: `destacado: true`.
- Tipografías en `assets/fonts/` (Fontsource, OFL, subconjunto latino); no se generan, se editan ahí.
- `src/css/` estilos (se escriben con los hex por defecto; el build los sustituye por los de `contenido.json`).
- `src/site.js` (idioma, eventos, cursor) y `src/menu.js` (pestañas). `src/img/` originales → `img/*.webp`.

## Medición
Cada CTA lleva `data-ev` (`como_llegar`, `whatsapp`, `phone`, `order_*`, `menu_nav`, `branch_page`, `home_nav`, `review`, `social_*`)
y `data-branch`. Un clic = `dataLayer.push({event:'cta_click',…})` + `gtag('event', ev, {branch})`. Sin GTM (evita hits duplicados).

## Reglas
- No cambiar nombre, horarios ni datos del Perfil de Google sin aprobación de Fernando.
- Teléfono/WhatsApp actual: número de la capitana (temporal hasta tener Wati de AM). No usar números de otras marcas.
- No mencionar otras marcas del grupo en el sitio.
- GA4: eventos clave = como_llegar, whatsapp, phone, menu_nav (sin valor monetario).
