"""Inserta Google Analytics 4 (con Consent Mode v2 y banner de cookies) en todas las páginas.
Uso: python3 tools/add_analytics.py   (desde la raíz del repo; se puede repetir sin duplicar)
"""
import glob

GA_ID = 'G-RGHMMSZ26L'
MARK = '<!-- amura-analytics -->'
SNIPPET = f"""{MARK}
<script>
window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}
gtag('consent','default',{{analytics_storage:'denied',ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied',wait_for_update:500}});
gtag('js',new Date());gtag('config','{GA_ID}');
</script>
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
<script defer src="/assets/amura-consent.js"></script>
"""

n = 0
for f in glob.glob('**/*.html', recursive=True):
    if f.startswith('tools/'):
        continue
    h = open(f, encoding='utf-8').read()
    if MARK in h:
        continue
    i = h.lower().find('<head>')
    if i < 0:
        continue
    h = h[:i + 6] + '\n' + SNIPPET + h[i + 6:]
    open(f, 'w', encoding='utf-8').write(h)
    n += 1
print('páginas con Analytics:', n)
