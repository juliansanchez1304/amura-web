"""Servidor local que imita Cloudflare Pages (/ruta -> ruta.html)."""
import http.server, os, sys
ROOT = sys.argv[1]
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=ROOT, **k)
    def translate_path(self, path):
        p = super().translate_path(path.split('?')[0])
        if os.path.isdir(p) and os.path.exists(os.path.join(p, 'index.html')):
            return os.path.join(p, 'index.html')
        if (not os.path.exists(p) or os.path.isdir(p)) and os.path.exists(p.rstrip('/') + '.html'):
            return p.rstrip('/') + '.html'
        if not os.path.exists(p) and os.path.exists(p + '.html'):
            return p + '.html'
        return p
    def log_message(self, *a):
        pass
http.server.ThreadingHTTPServer(('127.0.0.1', 8080), H).serve_forever()
