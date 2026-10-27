// POST /api/lead — lead form endpoint (Cloudflare Pages Function).
// Stores leads in Supabase (anon key, RLS insert-only). Without config answers 503 + mailto fallback.
import { validateLead } from "./_lead_validate.js";

const MAX_BODY = 8192;
const json = (obj, status = 200) =>
  new Response(JSON.stringify(obj), { status, headers: { "Content-Type": "application/json; charset=utf-8" } });

export async function onRequest(context) {
  if (context.request.method !== "POST") {
    return new Response(JSON.stringify({ ok: false, error: "method_not_allowed" }), {
      status: 405, headers: { "Content-Type": "application/json", Allow: "POST" },
    });
  }
  return onRequestPost(context);
}

export async function onRequestPost({ request, env }) {
  // Same-origin only (no CORS *). Missing Origin is allowed; validation + honeypot still apply.
  const origin = request.headers.get("Origin");
  if (origin) {
    try {
      if (new URL(origin).host !== new URL(request.url).host) return json({ ok: false, error: "forbidden" }, 403);
    } catch (_) {
      return json({ ok: false, error: "forbidden" }, 403);
    }
  }

  const len = Number(request.headers.get("Content-Length") || 0);
  if (len > MAX_BODY) return json({ ok: false, error: "too_large" }, 413);
  const raw = await request.text();
  if (raw.length > MAX_BODY) return json({ ok: false, error: "too_large" }, 413);

  let body;
  try { body = JSON.parse(raw); } catch (_) { return json({ ok: false, errors: { _: "invalid_json" } }, 400); }

  const res = validateLead(body, Date.now());
  if (res.spam) { console.log("lead_spam", res.spam); return json({ ok: true }); }
  if (res.errors) return json({ ok: false, errors: res.errors }, 400);

  if (!env.SUPABASE_URL || !env.SUPABASE_ANON_KEY) return json({ ok: false, fallback: "mailto" }, 503);

  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), 5000);
  try {
    const r = await fetch(`${env.SUPABASE_URL.replace(/\/$/, "")}/rest/v1/leads`, {
      method: "POST",
      signal: ctrl.signal,
      headers: {
        apikey: env.SUPABASE_ANON_KEY,
        Authorization: `Bearer ${env.SUPABASE_ANON_KEY}`,
        "Content-Type": "application/json",
        Prefer: "return=minimal",
      },
      body: JSON.stringify({ tenant_id: env.TENANT_ID || "default", ...res.lead }),
    });
    if (!r.ok) { console.error("lead_store_failed", r.status); return json({ ok: false, fallback: "mailto" }, 502); }
  } catch (e) {
    console.error("lead_store_failed", "network_or_timeout");
    return json({ ok: false, fallback: "mailto" }, 502);
  } finally {
    clearTimeout(timer);
  }

  // Optional owner notification (no e-mail address in the message).
  if (env.TELEGRAM_BOT_TOKEN && env.TELEGRAM_CHAT_ID) {
    try {
      await fetch(`https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/sendMessage`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ chat_id: env.TELEGRAM_CHAT_ID, text: `Nowy lead: ${res.lead.name}, ${res.lead.service_interest || "-"}` }),
      });
    } catch (_) { console.error("lead_notify_failed"); }
  }
  return json({ ok: true });
}
