import os, datetime
SITE='site'; today=datetime.date.today().isoformat()
urls=[]
for r,_,fs in os.walk(SITE):
    for f in fs:
        if not f.endswith('.html') or f=='404.html': continue
        p='/'+os.path.relpath(os.path.join(r,f),SITE)[:-5]
        if p=='/index': p='/'
        if '-page-' in p or p=='/pages/gracias': continue
        urls.append(p)
urls.sort()
with open(f'{SITE}/sitemap.xml','w') as s:
    s.write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
    for u in urls: s.write(f'  <url><loc>https://amurashop.es{u}</loc><lastmod>{today}</lastmod></url>\n')
    s.write('</urlset>\n')
open(f'{SITE}/robots.txt','w').write('User-agent: *\nAllow: /\nDisallow: /pages/gracias\n\nSitemap: https://amurashop.es/sitemap.xml\n')
open(f'{SITE}/_redirects','w').write("""# URLs antiguas de Shopify
/collections/*   /   301
/collections     /   301
/products/*      /   301
/cart            /   301
/account/*       /   301
/account         /   301
/search          /   301
/blogs/*/tagged/*  /blogs/:splat  301
/sitemap_*       /sitemap.xml  301
""")
open(f'{SITE}/_headers','w').write("""https://:project.pages.dev/*
  X-Robots-Tag: noindex

/assets/*
  Cache-Control: public, max-age=31536000, immutable
""")
print(len(urls),'URLs en el sitemap')
