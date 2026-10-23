export async function onRequestGet(context) {
  return new Response(JSON.stringify({
    status: "active",
    platform: "Cloudflare Pages + Workers AI",
    model: "@cf/meta/llama-3.3-70b-instruct",
    timestamp: new Date().toISOString()
  }), {
    headers: { 'Content-Type': 'application/json' }
  });
}
