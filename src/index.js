/**
 * Cloudflare Worker with native Workers AI & Static Assets
 * Provides:
 * 1. Edge AI Generation using LLaMA 3.3 / DeepSeek via env.AI
 * 2. Static Dashboard Serving via ASSETS
 * 3. /api/generate endpoint for on-demand edge generation
 */

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    // Endpoint: On-demand AI post generation using Cloudflare Workers AI
    if (url.pathname === '/api/ai-generate' && request.method === 'POST') {
      try {
        const body = await request.json();
        const topic = body.topic || "Nowości w autonomicznych agentach AI";
        const format = body.format || "linkedin";

        let systemPrompt = "Jesteś pragmatycznym inżynierem AI. Tworzysz zwięzłe, merytoryczne posty bez lania wody i taniego marketingu.";
        let userPrompt = `Napisz post na ${format} na temat: ${topic}. Skup się na architekturze, bezpieczeństwie i praktycznym kodzie.`;

        // Native Cloudflare Workers AI call (Llama 3.3 70B Instruct)
        const response = await env.AI.run('@cf/meta/llama-3.3-70b-instruct', {
          messages: [
            { role: 'system', content: systemPrompt },
            { role: 'user', content: userPrompt }
          ],
          max_tokens: 1024,
          temperature: 0.7
        });

        return new Response(JSON.stringify({ success: true, result: response.response }), {
          headers: { 'Content-Type': 'application/json' }
        });
      } catch (err) {
        return new Response(JSON.stringify({ success: false, error: err.message }), {
          status: 500,
          headers: { 'Content-Type': 'application/json' }
        });
      }
    }

    // Health / Info endpoint
    if (url.pathname === '/api/status') {
      return new Response(JSON.stringify({
        status: "online",
        service: "Cloudflare Workers AI Brand Agent",
        models_available: ["@cf/meta/llama-3.3-70b-instruct", "@cf/deepseek-ai/deepseek-r1-distill-qwen-32b"]
      }), {
        headers: { 'Content-Type': 'application/json' }
      });
    }

    // Fallback: serve static assets (dashboard)
    if (env.ASSETS) {
      return env.ASSETS.fetch(request);
    }

    return new Response("AI Personal Brand Worker is running!", { status: 200 });
  },

  // Scheduled Cron Trigger (Edge Automation)
  async scheduled(event, env, ctx) {
    console.log("[Cloudflare Cron] Edge tick triggered at", new Date().toISOString());
  }
};
