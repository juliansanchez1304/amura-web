"""Crea un artículo nuevo a partir de otro artículo existente como plantilla.

Uso:
  python3 tools/new_article.py spec.json

spec.json:
{
  "template": "blogs/<blog>/<articulo-plantilla>.html",
  "blog": "marcas-modelos-chinos-2027",
  "handle": "nuevo-articulo-handle",
  "title": "Título visible (H1)",
  "seo_title": "Título para Google (opcional)",
  "description": "Meta descripción / resumen",
  "date": "2026-11-11T10:30:00+01:00",
  "author": "Equipo Amura",
  "image": "/assets/img/portada.webp",
  "image_alt": "ALT de la portada",
  "body_file": "ruta/al/cuerpo.html"
}
Después: actualizar listados con tools/update_listings.py
"""
import json, re, sys, html as H
from datetime import datetime
from bs4 import BeautifulSoup

MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto',
         'septiembre', 'octubre', 'noviembre', 'diciembre']
SITE = 'https://amurashop.es'

spec = json.load(open(sys.argv[1]))
tpl_path = spec['template']
tpl_handle = tpl_path.rsplit('/', 1)[1][:-5]
tpl_blog = tpl_path.split('/')[1]
body = open(spec['body_file'], encoding='utf-8').read()
url_path = f"/blogs/{spec['blog']}/{spec['handle']}"
full_title = (spec.get('seo_title') or spec['title'])
page_title = full_title if '|' in full_title or '–' in full_title else f"{full_title} – Amura Movilidad Eléctrica"
dt = datetime.fromisoformat(spec['date'])
fecha = f"{dt.day} de {MESES[dt.month - 1]} de {dt.year}"

raw = open(tpl_path, encoding='utf-8').read()
raw = raw.replace(f'/blogs/{tpl_blog}/{tpl_handle}', url_path).replace(tpl_handle, spec['handle'])
s = BeautifulSoup(raw, 'lxml')
s.title.string = page_title
for m in s.find_all('meta'):
    k = m.get('name') or m.get('property')
    if k in ('description', 'og:description', 'twitter:description'):
        m['content'] = spec['description']
    elif k in ('og:title', 'twitter:title'):
        m['content'] = spec['title']
    elif k == 'og:url':
        m['content'] = SITE + url_path
    elif k in ('og:image', 'og:image:secure_url'):
        m['content'] = SITE + spec['image']
can = s.find('link', rel='canonical')
if can:
    can['href'] = SITE + url_path

art = s.find('article')
img = art.find('div', class_='article-template__hero-container').find('img')
img['src'] = spec['image']
img['srcset'] = ', '.join(f"{spec['image']} {w}w" for w in (350, 750, 1100, 1200))
img['alt'] = spec['image_alt']
hdr = art.find('header')
hdr.find('h1').string = spec['title']
t = hdr.find('time')
t['datetime'] = spec['date']
t.string = fecha
au = hdr.select_one('.caption-with-letter-spacing span')
if au:
    au.string = spec.get('author', 'Equipo Amura')

content = art.find('div', class_='article-template__content')
content.clear()
content.append(BeautifulSoup(body, 'html.parser'))

for sc in s.find_all('script', type='application/ld+json'):
    try:
        d = json.loads(sc.string)
    except Exception:
        continue
    if d.get('@type') == 'Article':
        text = BeautifulSoup(body, 'html.parser').get_text('\n')
        d.update({
            '@id': url_path + '#article',
            'mainEntityOfPage': {'@type': 'WebPage', '@id': SITE + url_path},
            'articleBody': text, 'headline': spec['title'], 'description': spec['description'],
            'image': SITE + spec['image'], 'datePublished': spec['date'], 'dateModified': spec['date'],
            'author': {'@type': 'Person', 'name': spec.get('author', 'Equipo Amura')},
        })
        sc.string = json.dumps(d, ensure_ascii=False)

out = str(s)
dest = url_path.lstrip('/') + '.html'
open(dest, 'w', encoding='utf-8').write(out)
print('creado', dest)
