// حماية الدخول: اسم مستخدم + كلمة سر (Basic Auth) قبل تقديم أي ملف.
// المستخدمون في السر USERS بالشكل:  ali:كلمة-سر-1;sara:كلمة-سر-2
const enc = new TextEncoder();

async function sha(s) {
  return new Uint8Array(await crypto.subtle.digest('SHA-256', enc.encode(s)));
}

async function same(a, b) {
  const x = await sha(a), y = await sha(b);
  let d = 0;
  for (let i = 0; i < x.length; i++) d |= x[i] ^ y[i];
  return d === 0;
}

function deny(status, msg) {
  return new Response(msg, {
    status,
    headers: {
      'WWW-Authenticate': 'Basic realm="Libya EWS", charset="UTF-8"',
      'Content-Type': 'text/plain; charset=utf-8',
      'Cache-Control': 'no-store',
    },
  });
}

export default {
  async fetch(request, env) {
    const raw = (env.USERS || '').trim();
    if (!raw) return deny(503, 'Access is not configured.');
    const users = raw.split(';').map(s => s.trim()).filter(Boolean).map(s => {
      const i = s.indexOf(':');
      return i > 0 ? [s.slice(0, i), s.slice(i + 1)] : null;
    }).filter(Boolean);

    const h = request.headers.get('Authorization') || '';
    if (!h.startsWith('Basic ')) return deny(401, 'Sign in required.');
    let name = '', pass = '';
    try {
      const bytes = Uint8Array.from(atob(h.slice(6).trim()), c => c.charCodeAt(0));
      const t = new TextDecoder().decode(bytes);
      const i = t.indexOf(':');
      if (i < 0) return deny(401, 'Sign in required.');
      name = t.slice(0, i); pass = t.slice(i + 1);
    } catch (e) { return deny(401, 'Sign in required.'); }

    let ok = false;
    for (const [u, p] of users) {
      const a = await same(u, name), b = await same(p, pass);
      if (a && b) ok = true;
    }
    if (!ok) return deny(401, 'Invalid username or password.');

    const res = await env.ASSETS.fetch(request);
    const out = new Response(res.body, res);
    out.headers.set('Cache-Control', 'private, no-store');
    out.headers.set('X-Content-Type-Options', 'nosniff');
    out.headers.set('X-Frame-Options', 'DENY');
    out.headers.set('Referrer-Policy', 'no-referrer');
    return out;
  },
};
