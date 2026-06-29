// ── Gated letters delivery — researcher-only (model B, real auth) ───────────
// Serves the Frances Hunter correspondence ONLY to an authenticated researcher.
// Content lives in a PRIVATE R2 bucket (env.GATED_BUCKET, native binding) that is
// NOT mapped to any public domain — so transcripts + scans are reachable ONLY
// through these token-checked endpoints, never by guessing a public URL.
//
// Wire into worker.js fetch() (near the top, before /list):
//     import { handleGated } from "./gated-letters.js";
//     if (url.pathname.startsWith("/gated/")) return handleGated(request, env);
//
// wrangler.toml:  [[r2_buckets]] binding="GATED_BUCKET"  bucket_name="hhf-gated"
// secret:         npx wrangler secret put GATED_TOKEN        (the researcher password)
//
// Endpoints (all require the token via X-Researcher-Token header or ?t=):
//   GET /gated/letters           → letters-dataset.json (metadata + transcripts)
//   GET /gated/img?key=gated/<handle>/<file>  → a private scan/tier or access PDF

const GATED_ALLOW = new Set([
  "https://hunterhouse.org",
  "https://www.hunterhousefoundation.com",
  "http://localhost",
  "http://127.0.0.1",
]);

function cors(origin) {
  const o = GATED_ALLOW.has(origin) ? origin : "https://hunterhouse.org";
  return {
    "Access-Control-Allow-Origin": o,
    "Access-Control-Allow-Headers": "X-Researcher-Token",
    "Access-Control-Allow-Methods": "GET,OPTIONS",
    "Vary": "Origin",
  };
}

// constant-time string compare (same intent as worker.js ctEq)
function ctEq(a, b) {
  if (typeof a !== "string" || typeof b !== "string" || a.length !== b.length) return false;
  let r = 0;
  for (let i = 0; i < a.length; i++) r |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return r === 0;
}

export async function handleGated(request, env) {
  const url = new URL(request.url);
  const H = cors(request.headers.get("Origin") || "");
  if (request.method === "OPTIONS") return new Response(null, { headers: H });
  if (!env.GATED_BUCKET)
    return new Response(JSON.stringify({ error: "gated storage not configured" }),
      { status: 503, headers: { ...H, "Content-Type": "application/json" } });

  // ── auth: shared researcher token ────────────────────────────────────────
  const tok = request.headers.get("X-Researcher-Token") || url.searchParams.get("t") || "";
  if (!env.GATED_TOKEN || !ctEq(tok, env.GATED_TOKEN))
    return new Response("Unauthorized", { status: 401, headers: H });

  // ── the dataset (metadata + transcripts) ─────────────────────────────────
  if (url.pathname === "/gated/letters") {
    const obj = await env.GATED_BUCKET.get("letters-dataset.json");
    if (!obj) return new Response(JSON.stringify({ error: "dataset not found" }),
      { status: 404, headers: { ...H, "Content-Type": "application/json" } });
    return new Response(obj.body, {
      headers: { ...H, "Content-Type": "application/json", "Cache-Control": "no-store" },
    });
  }

  // ── a private scan / tier / access PDF ───────────────────────────────────
  if (url.pathname === "/gated/img") {
    const key = url.searchParams.get("key") || "";
    if (!key.startsWith("gated/") || key.includes("..")) return new Response("Bad key", { status: 400, headers: H });
    const obj = await env.GATED_BUCKET.get(key);
    if (!obj) return new Response("Not found", { status: 404, headers: H });
    const ct = (obj.httpMetadata && obj.httpMetadata.contentType) ||
      (key.endsWith(".pdf") ? "application/pdf" : "image/jpeg");
    return new Response(obj.body, { headers: { ...H, "Content-Type": ct, "Cache-Control": "private, max-age=600" } });
  }

  return new Response("Not found", { status: 404, headers: H });
}
