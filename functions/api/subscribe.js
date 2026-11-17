// Registra el contacto en la lista de Brevo. Corre en Cloudflare Pages (gratis).
// Variables en Cloudflare: BREVO_API_KEY (secreto) y BREVO_LIST_ID.
// Admite correo o, si el usuario solo dejó un móvil/WhatsApp, el teléfono.
export async function onRequestPost({ request, env }) {
  const json = (obj, status = 200) =>
    new Response(JSON.stringify(obj), { status, headers: { "Content-Type": "application/json" } });

  let data;
  try { data = await request.json(); } catch (_) { return json({ ok: false }, 400); }

  const clean = (v, n = 200) => String(v == null ? "" : v).trim().slice(0, n);
  const raw = clean(data.email || data.contacto, 254).toLowerCase();
  const isEmail = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(raw);

  // Teléfono: el del campo "phone" o, si el contacto no es un correo, lo que escribió ahí
  let phone = clean(data.phone || (isEmail ? "" : raw), 40).replace(/[^\d+]/g, "");
  if (/^[6789]\d{8}$/.test(phone)) phone = "+34" + phone;          // móvil/fijo español
  else if (/^34[6789]\d{8}$/.test(phone)) phone = "+" + phone;
  const validPhone = /^\+\d{9,15}$/.test(phone);

  if (!isEmail && !validPhone) return json({ ok: false }, 400);
  if (!env.BREVO_API_KEY || !env.BREVO_LIST_ID) return json({ ok: false }, 500);

  const base = {};
  const name = clean(data.name, 100);
  if (name) base.NOMBRE = name;   // en esta cuenta de Brevo el nombre se llama NOMBRE
  if (validPhone) base.SMS = phone;
  const origen = clean(data.origen || "Pie de pagina - suscripcion", 120);

  const send = (attributes) =>
    fetch("https://api.brevo.com/v3/contacts", {
      method: "POST",
      headers: { "api-key": env.BREVO_API_KEY, "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify({
        ...(isEmail ? { email: raw } : {}),
        attributes,
        listIds: [Number(env.BREVO_LIST_ID)],
        updateEnabled: true,
      }),
    });

  // Intentos de más a menos datos: así no se pierde nunca el contacto aunque un atributo falle
  const intentos = [{ ...base, ORIGEN: origen }, { ORIGEN: origen, ...(validPhone ? { SMS: phone } : {}) }, validPhone ? { SMS: phone } : {}];
  let r;
  for (const attrs of intentos) {
    r = await send(attrs);
    if (r.ok) break;
  }
  return json({ ok: r.ok }, r.ok ? 200 : 502);
}
