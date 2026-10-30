import pathlib
p = pathlib.Path("functions/api/ai-generate.js")
s = p.read_text(encoding="utf-8").replace("\r\n", "\n")
a = s.index("    return new Response(JSON.stringify({ success: true")
s = s[:a] + """    return json({ success: true, result: response.response });
  } catch (err) {
    return json({ success: false, error: err.message }, 500);
  }
}
"""
p.write_text(s, encoding="utf-8", newline="")

p = pathlib.Path("src/index.js")
s = p.read_text(encoding="utf-8").replace("\r\n", "\n")
s = s.replace("""    if (request.method === 'OPTIONS') {
      return new Response(null, {
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type, Authorization'
        }
      });
    }
""", "")
s = s.replace("""    if (url.pathname === '/api/ai-generate' && request.method === 'POST') {
      try {""", """    if (url.pathname === '/api/ai-generate' && request.method === 'POST') {
      // Admin-only: X-Admin-Token must equal env.ADMIN_TOKEN; no CORS.
      const deny = (error, status) => new Response(JSON.stringify({ success: false, error }), {
        status, headers: { 'Content-Type': 'application/json' }
      });
      if (!env.ADMIN_TOKEN) return deny('disabled', 503);
      if (request.headers.get('X-Admin-Token') !== env.ADMIN_TOKEN) return deny('unauthorized', 401);
      if (!env.AI) return deny('ai_binding_missing', 503);
      try {""")
s = s.replace(", 'Access-Control-Allow-Origin': '*'", "")
p.write_text(s, encoding="utf-8", newline="")
print("ADMIN_TOKEN" in s, "Allow-Origin" in s)
