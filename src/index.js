/**
 * Cloudflare Worker with native Workers AI & Static Assets for Autonoma AI (12-Agent Workforce OS)
 * Provides:
 * 1. Edge AI Generation using LLaMA 3.3 70B via env.AI (/api/ai-generate)
 * 2. Static Dashboard & Blog Serving via env.ASSETS
 * 3. Health / Telemetry status endpoint (/api/status)
 */

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        }
      });
    }

    // Endpoint: On-demand AI generation using Cloudflare Workers AI
    if (url.pathname === '/api/ai-generate' && request.method === 'POST') {
      try {
        const body = await request.json();
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

        const response = await env.AI.run('@cf/meta/llama-3.3-70b-instruct', {
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

    // Health / Info endpoint
    if (url.pathname === '/api/status') {
      return new Response(JSON.stringify({
        status: "online",
        service: "Autonoma AI — 12-Agent Workforce OS (Cloudflare Edge)",
        models_available: ["@cf/meta/llama-3.3-70b-instruct", "@cf/deepseek-ai/deepseek-r1-distill-qwen-32b"],
        timestamp: new Date().toISOString()
      }), {
        headers: { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' }
      });
    }

    // Fallback: serve static assets (dashboard & blog)
    if (env.ASSETS) {
      return env.ASSETS.fetch(request);
    }

    return new Response("Autonoma AI Worker is running!", { status: 200 });
  },

  // Scheduled Cron Trigger (Edge Automation every 6 hours)
  async scheduled(event, env, ctx) {
    console.log("[Autonoma AI Cron] Edge tick triggered at", new Date().toISOString());
  }
};
