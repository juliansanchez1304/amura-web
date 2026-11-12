# Cómo publicar un artículo nuevo en la web de Amura

La web es HTML estático. Cada `git push` a la rama `main` se publica solo en Cloudflare Pages en un minuto aproximadamente (amurashop.es).

## 1. Cuerpo del artículo
- El formato del cuerpo es **el mismo HTML que se usaba en Shopify**: todo va dentro de `<div class="amura-article">…</div>`, con las mismas clases (`amura-meta`, `amura-lead`, `amura-resumen`, `amura-tabla-wrap`/`amura-tabla`, `amura-callout`, `amura-fig`, `amura-faq`, `amura-cta`, `amura-fuentes`).
- Ejemplo completo: `blogs/marcas-modelos-chinos-2027/leapmotor-b03x-espana-precio-versiones-autonomia-carga.html` (el cuerpo es el contenido de `<div class="article-template__content …">`).
- Enlaces internos relativos: `/blogs/<blog>/<handle>` y `/pages/<handle>`.
- Imágenes: `/assets/img/<nombre>.webp` (no URLs de Shopify). Portada 1200×630 o 1200×675; resto 1200×675.

Guarda el cuerpo en un archivo, por ejemplo `/tmp/atto2/body.html`.

## 2. Imágenes
Copia los WebP a `assets/img/` con el nombre exacto usado en el HTML (portada incluida).

## 3. Ficha del artículo (spec.json)
```json
{
  "template": "blogs/marcas-modelos-chinos-2027/leapmotor-b03x-espana-precio-versiones-autonomia-carga.html",
  "blog": "marcas-modelos-chinos-2027",
  "handle": "byd-atto-2-espana-precio-versiones-autonomia-carga",
  "title": "Título visible (H1)",
  "seo_title": "Título para Google (opcional)",
  "description": "Meta descripción / resumen (≈150-160 caracteres)",
  "date": "2026-11-12T09:00:00+01:00",
  "author": "Equipo Amura",
  "image": "/assets/img/amura-byd-atto-2-espana-portada.webp",
  "image_alt": "ALT de la portada",
  "body_file": "/tmp/atto2/body.html"
}
```
Como `template` usa cualquier artículo ya publicado (mejor uno del mismo blog). Blogs disponibles (`blog`):
- `marcas-modelos-chinos-2027` (etiqueta revista: "Marcas y modelos")
- `comparativas-coches-electricos-chinos`
- `carga-baterias-infraestructura-coches-electricos`
- `comprar-primer-electrico`
- `lanzamientos-coches-electricos-chinos-2027`

## 4. Generar y publicar
Desde la raíz del repo:
```bash
python3 tools/new_article.py /tmp/atto2/spec.json
python3 tools/update_listings.py /tmp/atto2/spec.json "Marcas y modelos"
[ -f tools/add_analytics.py ] && python3 tools/add_analytics.py   # añade Analytics a la página nueva si falta (no duplica)
git add -A && git commit -m "Publica artículo …" && git push origin main
```
`update_listings.py` pone el artículo el primero en su blog (desplaza la última tarjeta a la página siguiente), lo añade a /pages/revista y al sitemap.

## 5. Comprobar
Abre `https://amurashop.es/blogs/<blog>/<handle>` (o `https://amura-movilidad.pages.dev/...`) y revisa portada, imágenes y enlaces.

## Programar un artículo
No hay programación automática: se deja preparado y se hace el `git push` el día y la hora que se quiera publicar.
