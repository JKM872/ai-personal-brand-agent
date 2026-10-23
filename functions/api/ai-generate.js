/**
 * Cloudflare Pages Function: /api/ai-generate
 * Native integration with Cloudflare Workers AI for Cloudflare Pages.
 */
export async function onRequestPost(context) {
  try {
    const body = await context.request.json();
    const topic = body.topic || "Autonomiczne agenty AI w inżynierii oprogramowania";
    const format = body.format || "linkedin";

    const systemPrompt = "Jesteś pragmatycznym inżynierem AI. Tworzysz zwięzłe, merytoryczne posty bez marketingu i lania wody.";
    const userPrompt = `Napisz post na ${format} o: ${topic}. Podaj architekturę, bezpieczeństwo i wnioski inżynierskie.`;

    // Direct Cloudflare Workers AI call at edge
    const response = await context.env.AI.run('@cf/meta/llama-3.3-70b-instruct', {
      messages: [
        { role: 'system', content: systemPrompt },
        { role: 'user', content: userPrompt }
      ],
      max_tokens: 1024,
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
