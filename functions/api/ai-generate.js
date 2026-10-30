/**
 * Cloudflare Pages Function: /api/ai-generate
 * Native integration with Cloudflare Workers AI (@cf/meta/llama-3.3-70b-instruct) for Autonoma AI Studio.
 * Allows 0.00 PLN live generation of any of the 10 marketing channels directly at the Edge.
 */
const json = (obj, status = 200) =>
  new Response(JSON.stringify(obj), { status, headers: { 'Content-Type': 'application/json' } });

// Admin-only: requires X-Admin-Token == env.ADMIN_TOKEN. No CORS (same-origin admin panel only).
export async function onRequestPost(context) {
  const env = context.env || {};
  if (!env.ADMIN_TOKEN) return json({ success: false, error: 'disabled' }, 503);
  if (context.request.headers.get('X-Admin-Token') !== env.ADMIN_TOKEN) return json({ success: false, error: 'unauthorized' }, 401);
  if (!env.AI) return json({ success: false, error: 'ai_binding_missing' }, 503);
  try {
    const body = await context.request.json();
    const project = body.project || {};
    const channelLabel = body.channel_label || body.format || "Post Ekspercki LinkedIn";
    const pname = project.product_name || body.topic || "Autonoma AI";
    const purl = project.website_url || "https://twoja-domena.pl";
    const pcat = project.category || "SaaS & Automatyzacja";
    const paud = project.target_audience || "klienci B2B";
    const pprob = project.primary_problem_solved || "optymalizacja procesów biznesowych";

    const systemPrompt =
      "Jesteś częścią 12-osobowej drużyny wirtualnych pracowników Autonoma AI. " +
      "Tworzysz w 100% polskie, profesjonalne, wysoko konwertujące materiały marketingowe i sprzedażowe B2B. " +
      "Zero lania wody, używaj konkretnych wyliczeń i czystego formatowania Markdown.";

    const userPrompt = `Przygotuj kompletny materiał dla formatu: ${channelLabel}.
Dane projektu:
- Nazwa produktu: ${pname} (${purl})
- Kategoria: ${pcat}
- Grupa docelowa: ${paud}
- Główny rozwiązywany problem: ${pprob}`;

    const response = await context.env.AI.run('@cf/meta/llama-3.3-70b-instruct', {
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userPrompt }
      ],
      max_tokens: 1800,
      temperature: 0.7
    });

    return json({ success: true, result: response.response });
  } catch (err) {
    return json({ success: false, error: err.message }, 500);
  }
}
