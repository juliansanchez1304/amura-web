"""Añade un artículo nuevo (creado con new_article.py) a los listados:
- primera página de su blog (y desplaza la última tarjeta a la página siguiente)
- página /pages/revista
- sitemap.xml

Uso: python3 tools/update_listings.py spec.json "Etiqueta revista"
Ej. etiqueta revista: "Marcas y modelos"
"""
import json, sys, copy, os, re, glob
from datetime import datetime
from bs4 import BeautifulSoup

MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto',
         'septiembre', 'octubre', 'noviembre', 'diciembre']
spec = json.load(open(sys.argv[1]))
etiqueta = sys.argv[2] if len(sys.argv) > 2 else ''
blog, handle = spec['blog'], spec['handle']
url = f'/blogs/{blog}/{handle}'
dt = datetime.fromisoformat(spec['date'])
fecha = f"{dt.day} de {MESES[dt.month - 1]} de {dt.year}"

def trunc(t, n):
    return t if len(t) <= n else t[:n - 3] + '...'

def set_card(card):
    for a in card.find_all('a', href=True):
        a['href'] = url
        a.string = '\n                ' + trunc(spec['title'], 50) + '\n              '
    for img in card.find_all('img'):
        img['src'] = spec['image']
        img['alt'] = spec['image_alt']
        if img.get('srcset'):
            img['srcset'] = ', '.join(f"{spec['image']} {p.split()[-1]}" for p in img['srcset'].split(','))
    for t in card.find_all('time'):
        t['datetime'] = spec['date']
        t.string = fecha
    for p in card.find_all('p', class_='article-card__excerpt'):
        p.string = trunc(spec['description'], 150) + '\n'

# 1. listado del blog
pages = [f'blogs/{blog}.html'] + sorted(glob.glob(f'blogs/{blog}-page-*.html'))
soups = [BeautifulSoup(open(p, encoding='utf-8').read(), 'lxml') for p in pages]
if url in str(soups[0]):
    print('ya estaba en el listado')
else:
    first = soups[0].find(class_='blog-articles__article')
    new = copy.copy(first)
    set_card(new)
    first.insert_before(new)
    # cascada: la última de cada página pasa a la siguiente
    for i in range(len(soups) - 1):
        cards = soups[i].find_all(class_='blog-articles__article')
        last = cards[-1].extract()
        nxt = soups[i + 1].find(class_='blog-articles__article')
        nxt.insert_before(last)
    for p, s in zip(pages, soups):
        open(p, 'w', encoding='utf-8').write(str(s))
    print('listado del blog actualizado')

# 2. revista
rp = 'pages/revista.html'
if os.path.exists(rp):
    s = BeautifulSoup(open(rp, encoding='utf-8').read(), 'lxml')
    if url not in str(s):
        items = s.find_all('li', class_='amura-rev__item')
        tpl = next((i for i in items if i.get('data-blog') == blog), items[0])
        new = copy.copy(tpl)
        new['data-blog'] = blog
        new['data-ts'] = str(int(dt.timestamp()))
        a = new.find('a'); a['href'] = url
        img = new.find('img'); img['src'] = spec['image']; img['alt'] = spec['image_alt']
        meta = new.find(class_='amura-art__meta')
        lab = etiqueta or meta.get_text().split('·')[0].strip()
        meta.string = f"{lab} · {dt.strftime('%d/%m/%Y')}"
        new.find(class_='amura-art__t').string = spec['title']
        new.find(class_='amura-art__x').string = trunc(spec['description'], 120)
        items[0].insert_before(new)
        open(rp, 'w', encoding='utf-8').write(str(s))
        print('revista actualizada')

# 3. sitemap
sm = open('sitemap.xml', encoding='utf-8').read()
if url not in sm:
    line = f'  <url><loc>https://amurashop.es{url}</loc><lastmod>{dt.date().isoformat()}</lastmod></url>\n'
    sm = sm.replace('</urlset>', line + '</urlset>')
    open('sitemap.xml', 'w', encoding='utf-8').write(sm)
    print('sitemap actualizado')
