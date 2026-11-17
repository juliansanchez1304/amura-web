/* Envía a Brevo (vía /api/subscribe) los datos de cada formulario de la web.
   Se ejecuta antes que el envío a Formspree y nunca bloquea ni rompe el formulario. */
(function () {
  var ORIGENES = {
    'form-contacto': 'Formulario de contacto',
    'form-soporte-ve': 'Soporte coches electricos',
    'form-planificador-ruta': 'Planificador de rutas',
    'form-plan-compra-amura': 'Estudio de compra (asesoramiento)',
    'amc-lead-form': 'Comparador - formulario de interes'
  };
  document.addEventListener('submit', function (ev) {
    var f = ev.target;
    if (!f || !ORIGENES[f.id]) return;
    try {
      var fd = new FormData(f);
      var body = {
        email: fd.get('email') || '',
        contacto: fd.get('contacto') || '',
        name: fd.get('name') || '',
        phone: fd.get('phone') || '',
        origen: ORIGENES[f.id]
      };
      fetch('/api/subscribe', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        keepalive: true, body: JSON.stringify(body)
      }).catch(function () {});
    } catch (e) {}
  }, true);
})();
