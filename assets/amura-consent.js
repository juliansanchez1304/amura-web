/* Amura: banner de cookies + Google Analytics 4 con Consent Mode v2.
   Analytics solo guarda cookies si el visitante pulsa "Aceptar". */
(function () {
  var KEY = 'amura_cookies_v1';
  var choice = null;
  try { choice = localStorage.getItem(KEY); } catch (e) {}

  function grant() {
    if (window.gtag) gtag('consent', 'update', { analytics_storage: 'granted' });
  }
  function save(v) {
    try { localStorage.setItem(KEY, v); } catch (e) {}
  }

  if (choice === 'granted') { grant(); return; }
  if (choice === 'denied') return;

  function show() {
    var css = document.createElement('style');
    css.textContent =
      '#amura-cookies{position:fixed;left:16px;right:16px;bottom:16px;z-index:99999;max-width:560px;margin:0 auto;' +
      'background:#0d1b2a;color:#fff;border-radius:16px;padding:18px 20px;box-shadow:0 10px 30px rgba(0,0,0,.25);' +
      'font:15px/1.5 "DM Sans",system-ui,-apple-system,sans-serif}' +
      '#amura-cookies p{margin:0 0 14px}#amura-cookies a{color:#86efac;text-decoration:underline}' +
      '#amura-cookies .b{display:flex;gap:10px;flex-wrap:wrap}' +
      '#amura-cookies button{flex:1 1 140px;border:0;border-radius:999px;padding:11px 18px;font:700 15px/1 inherit;cursor:pointer}' +
      '#amura-cookies .ok{background:#15803d;color:#fff}#amura-cookies .no{background:transparent;color:#fff;border:2px solid #fff}';
    document.head.appendChild(css);
    var box = document.createElement('div');
    box.id = 'amura-cookies';
    box.setAttribute('role', 'dialog');
    box.setAttribute('aria-label', 'Aviso de cookies');
    box.innerHTML =
      '<p>Usamos cookies de analítica (Google Analytics) para saber qué contenidos te resultan útiles y mejorar la web. ' +
      'Solo se activan si las aceptas. <a href="/pages/politica-de-cookies">Política de cookies</a></p>' +
      '<div class="b"><button type="button" class="no">Rechazar</button><button type="button" class="ok">Aceptar</button></div>';
    document.body.appendChild(box);
    box.querySelector('.ok').onclick = function () { save('granted'); grant(); box.remove(); };
    box.querySelector('.no').onclick = function () { save('denied'); box.remove(); };
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', show); else show();
})();
