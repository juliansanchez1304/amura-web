// Añade el correo a la lista de Brevo. Corre en Cloudflare Pages (gratis).
// Variables secretas en Cloudflare: BREVO_API_KEY y BREVO_LIST_ID.
export async function onRequestPost({ request, env }) {
  const json = (obj, status = 200) =>
    new Response(JSON.stringify(obj), { status, headers: { "Content-Type": "application/json" } });

  let data;
  try { data = await request.json(); } catch (_) { return json({ ok: false }, 400); }

  const email = String(data.email || "").trim().toLowerCase();
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email) || email.length > 254) return json({ ok: false }, 400);
  if (!env.BREVO_API_KEY || !env.BREVO_LIST_ID) return json({ ok: false }, 500);

  const r = await fetch("https://api.brevo.com/v3/contacts", {
    method: "POST",
    headers: { "api-key": env.BREVO_API_KEY, "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify({ email, listIds: [Number(env.BREVO_LIST_ID)], updateEnabled: true }),
  });
  return json({ ok: r.ok }, r.ok ? 200 : 502);
}
