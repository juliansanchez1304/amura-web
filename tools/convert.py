"""Convierte el mirror de amurashop.es (Shopify) en una web estática limpia.
Uso: python3 convert.py <raw_dir> <out_dir>
"""
import os, re, sys, hashlib, urllib.parse, urllib.request
from bs4 import BeautifulSoup, Comment

RAW, OUT = sys.argv[1], sys.argv[2]
ASSET_DIR = os.path.join(OUT, 'assets')
os.makedirs(ASSET_DIR, exist_ok=True)
downloaded = {}
failed = []

SHOP_HOSTS = ('amurashop.es', 'cdn.shopify.com', 'www.amurashop.es')

def is_shop_asset(url):
    if not url:
        return False
    u = url.strip()
    if u.startswith('//'):
        u = 'https:' + u
    if u.startswith('/cdn/'):
        return True
    p = urllib.parse.urlparse(u)
    if p.netloc in SHOP_HOSTS and (p.path.startswith('/cdn/') or p.path.startswith('/s/files/')):
        return True
    return False

def local_name(url):
    u = url.strip()
    if u.startswith('//'):
        u = 'https:' + u
    if u.startswith('/cdn/'):
        u = 'https://amurashop.es' + u
    p = urllib.parse.urlparse(u)
    base = os.path.basename(p.path)
    # carpeta según tipo
    if '/assets/' in p.path:
        sub = 'theme'
    elif '/fonts/' in p.path:
        sub = 'fonts'
    else:
        sub = 'img'
    return u.split('?')[0], f'{sub}/{base}'

def fetch(url):
    """Descarga un asset (sin parámetros de tamaño) y devuelve su ruta pública."""
    src, rel = local_name(url)
    if src in downloaded:
        return downloaded[src]
    dest = os.path.join(ASSET_DIR, rel)
    # evita colisiones de nombre con contenido distinto
    if os.path.exists(dest) and src not in downloaded:
        h = hashlib.md5(src.encode()).hexdigest()[:6]
        root, ext = os.path.splitext(rel)
        rel = f'{root}-{h}{ext}'
        dest = os.path.join(ASSET_DIR, rel)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    try:
        req = urllib.request.Request(src, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=60) as r:
            data = r.read()
        with open(dest, 'wb') as f:
            f.write(data)
    except Exception as e:
        failed.append((src, str(e)))
        downloaded[src] = url
        return url
    downloaded[src] = '/assets/' + rel
    return downloaded[src]

def rewrite_css(css_text):
    def rep(m):
        inner = m.group(1).strip('\'"')
        if is_shop_asset(inner):
            return f'url({fetch(inner)})'
        return m.group(0)
    return re.sub(r'url\(([^)]+)\)', rep, css_text)

SHOPIFY_SCRIPT_MARKERS = (
    'Shopify.shop', 'ShopifyAnalytics', '__TREKKIE', 'trekkie', 'wpmLoader',
    'content_for_header', 'SignInWithShop', 'featureAssets', 'PaymentButton',
    'portableWallets', 'shopify-accelerated', 'ShopifyPaypal', 'webmcp',
    'Shopify.designMode', 'StandardEvents', 'customDocumentWrite', 'loadFeatures',
    'Shopify.modules', 'form_key', 'userAgent = navigator.userAgent',
    'Function.prototype.bind.bind', 'window.shopUrl',
)
DROP_SCRIPT_IDS = {'__st', 'shopify-features', 'shop-js-analytics', 'form-persister',
                   'apple-pay-shop-capabilities', 'shopify-cfh-end', 'scb4127',
                   'shopify-origin-trials'}

NEWS_JS = """
(function () {
  var f = document.getElementById('amura-news-form');
  if (!f) return;
  f.addEventListener('submit', function (ev) {
    ev.preventDefault();
    var e = f.querySelector('input[type=email]');
    var fd = new FormData();
    fd.append('email', e.value);
    fd.append('_subject', 'Nuevo suscriptor Amura (Boletín)');
    fd.append('origen', 'Pie de pagina - suscripcion');
    var btn = f.querySelector('button[type=submit]');
    if (btn) { btn.disabled = true; btn.textContent = 'Enviando…'; }
    fetch('https://formspree.io/f/xbgldggg', {
      method: 'POST', body: fd, headers: { 'Accept': 'application/json' }
    }).then(function () { window.location.href = '/pages/gracias'; })
      .catch(function () { if (btn) { btn.disabled = false; btn.textContent = 'Suscribirme'; } alert('No se pudo enviar. Inténtalo de nuevo.'); });
  });
})();
"""

def clean(html, page_path):
    soup = BeautifulSoup(html, 'lxml')

    # 1. scripts de Shopify
    for s in soup.find_all('script'):
        src = s.get('src', '') or ''
        sid = s.get('id', '')
        attr = s.get('data-source-attribution', '') or ''
        txt = s.string or s.get_text() or ''
        if sid in DROP_SCRIPT_IDS or attr.startswith('shopify') or 'analytics' in (s.get('class') or []):
            s.decompose(); continue
        if src and ('shopifycloud' in src or 'cdn.shopify.com/storefront' in src or '/checkouts/' in src
                    or 'standard-actions' in src or 'privacy-banner' in src or 'cart-' in src
                    or 'shop-js' in src):
            s.decompose(); continue
        if not src and any(m in txt for m in SHOPIFY_SCRIPT_MARKERS):
            s.decompose(); continue
        if not src and "getElementById('amura-news-form')" in txt:
            s.string = NEWS_JS
            continue
        # scripts de Formspree de otros formularios: se quedan

    # 2. links/meta propios de Shopify
    for l in soup.find_all('link'):
        href = l.get('href', '') or ''
        rel = ' '.join(l.get('rel') or [])
        if 'storefront/policy-' in href:
            l['href'] = fetch(href); del l['integrity']; continue
        if ('.well-known' in href or 'monorail' in href or 'shopifycloud' in href
                or 'cdn.shopify.com/shopifycloud' in href or rel in ('preconnect', 'dns-prefetch') and ('shopify' in href or 'amurashop' in href)
                or 'component-cart' in href or 'feed' in rel and 'atom' in (l.get('type') or '')):
            l.decompose()
    for m in soup.find_all('meta'):
        if (m.get('name') or '') in ('shopify-digital-wallet', 'shopify-checkout-api-token', 'shopify-checkout-authorization-token') \
                or (m.get('id') or '') == 'shopify-digital-wallet':
            m.decompose()
    for c in soup.find_all(string=lambda t: isinstance(t, Comment)):
        if 'shopify' in c.lower() or 'BEGIN app' in c or 'END app' in c:
            c.extract()

    # 3. comentarios de Shopify en artículos
    for d in soup.select('.article-template__comment-wrapper, .article-template__comments, #comments, [id^="Comments-"]'):
        d.decompose()
    for f in soup.find_all('form'):
        a = f.get('action', '') or ''
        if '/comments' in a:
            f.decompose()

    # 4. formulario de newsletter: sin Shopify
    nf = soup.find('form', id='amura-news-form')
    if nf:
        nf['action'] = 'https://formspree.io/f/xbgldggg'
        for h in nf.find_all('input', attrs={'type': 'hidden'}):
            if h.get('name') in ('form_type', 'utf8', 'contact[tags]'):
                h.decompose()
        e = nf.find('input', attrs={'type': 'email'})
        if e: e['name'] = 'email'

    # 5. assets: src, href, srcset, style, data-src
    for tag in soup.find_all(True):
        for attr in ('src', 'href', 'data-src', 'poster', 'content'):
            v = tag.get(attr)
            if isinstance(v, str) and is_shop_asset(v):
                if attr == 'content' and not (tag.name == 'meta' and (tag.get('property','').startswith('og:image') or tag.get('name','').startswith('twitter:image'))):
                    continue
                newp = fetch(v)
                if attr == 'content':
                    newp = 'https://amurashop.es' + newp  # og:image absoluto
                tag[attr] = newp
        for attr in ('srcset', 'data-srcset', 'imagesrcset'):
            v = tag.get(attr)
            if isinstance(v, str) and ('cdn' in v):
                parts = []
                for item in v.split(','):
                    item = item.strip()
                    if not item: continue
                    bits = item.split()
                    if is_shop_asset(bits[0]):
                        bits[0] = fetch(bits[0])
                    parts.append(' '.join(bits))
                tag[attr] = ', '.join(parts)
        st = tag.get('style')
        if isinstance(st, str) and 'url(' in st:
            tag['style'] = rewrite_css(st)
    for st in soup.find_all('style'):
        if st.string and 'url(' in st.string:
            st.string = rewrite_css(st.string)

    # 6. enlaces internos absolutos → relativos; paginación
    for a in soup.find_all('a', href=True):
        h = a['href']
        h = re.sub(r'^https?://(www\.)?amurashop\.es', '', h)
        m = re.match(r'^(/blogs/[^/?#]+)\?page=(\d+)', h)
        if m:
            h = m.group(1) if m.group(2) == '1' else f'{m.group(1)}-page-{m.group(2)}'
        elif re.match(r'^\?page=(\d+)', h) and page_path.startswith('/blogs/'):
            n = re.match(r'^\?page=(\d+)', h).group(1)
            base = re.sub(r'-page-\d+$', '', page_path)
            h = base if n == '1' else f'{base}-page-{n}'
        a['href'] = h

    out = str(soup)
    # restos en texto plano (JSON-LD, scripts de la página)
    def rep(m):
        url = m.group(0).replace('\\/', '/')
        if url.startswith('//'):
            url = 'https:' + url
        if url.startswith('/cdn/'):
            url = 'https://amurashop.es' + url
        new = fetch(url)
        return new if new.startswith('/assets') else m.group(0)
    out = re.sub(r'(?:https?:)?(?:\\?/\\?/)(?:amurashop\.es\\?/cdn\\?/shop|cdn\.shopify\.com\\?/s\\?/files)[^"\'\s)<>,]*?\.(?:webp|jpe?g|png|gif|svg|avif)(?:\?[^"\'\s)<>]*)?',
                 rep, out)
    return out

def main():
    count = 0
    for root, _, files in os.walk(RAW):
        for fn in files:
            if not fn.endswith('.html'): continue
            src = os.path.join(root, fn)
            rel = os.path.relpath(src, RAW)
            page_path = '/' + rel[:-5]
            html = open(src, encoding='utf-8').read()
            out = clean(html, page_path)
            dest = os.path.join(OUT, rel)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            open(dest, 'w', encoding='utf-8').write(out)
            count += 1
    # CSS del tema: reescribir url() internas
    for root, _, files in os.walk(os.path.join(ASSET_DIR, 'theme')):
        for fn in files:
            if fn.endswith('.css'):
                p = os.path.join(root, fn)
                t = open(p, encoding='utf-8', errors='ignore').read()
                open(p, 'w', encoding='utf-8').write(rewrite_css(t))
    print('páginas:', count, 'assets:', len(downloaded), 'fallos:', len(failed))
    for f in failed[:20]:
        print('  FALLO', f)

if __name__ == '__main__':
    main()
