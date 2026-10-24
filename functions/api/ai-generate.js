"""
Cloudflare Pages Function: /api/ai-generate
Native integration with Cloudflare Workers AI (@cf/meta/llama-3.3-70b-instruct) for Autonoma AI Studio.
Allows 0.00 PLN live generation of any of the 10 marketing channels directly at the Edge.
"""
export async function onRequestPost(context) {
  try {
    const body = await context.request.json();
    const project = body.project || {};
    const channelLabel = body.channel_label || "Post Ekspercki LinkedIn";
    const pname = project.product_name || "Autonoma AI";
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

    return new Response(JSON.stringify({ success: true, result: response.response }), {
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
    });
  } catch (err) {
    return new Response(JSON.stringify({ success: false, error: err.message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
    });
  }
}

export async function onRequestOptions() {
  return new Response(null, {
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type'
    }
  });
}
