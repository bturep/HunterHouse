// ─────────────────────────────────────────────────────────────────────────
// Hunter House Foundation — read-only R2 bucket-listing Worker (S3-API edition)
//
// Powers the researcher "bucket browser" in next.html. It LISTs one folder
// level of the hunter-house-archive bucket and returns folders + files. The
// only S3 action it performs is ListObjectsV2 — no PutObject/DeleteObject/Copy
// anywhere — so the archive can never be written to or rearranged through it.
//
// WHY S3 API instead of a native R2 binding: the bucket lives in the Foundation
// Cloudflare account, but this Worker is deployed in Brandon's own account
// (which has Workers rights). Native bindings are same-account only, so instead
// the Worker calls the R2 S3 endpoint cross-account, signed with a READ-ONLY R2
// API token supplied as Worker secrets.
//
// As of 2026-06-06 this Worker also carries two tiny, cookieless analytics
// endpoints so the Foundation can see how the archive is used WITHOUT handing
// the data to a third party or needing Cloudflare-dashboard access in Floyd's
// account (everything stays in Brandon's own account, like the listing does):
//
//   GET  /dl?key=<bucket-key>   — logs a download, then 302-redirects to the
//                                 file's public URL. The browser ends up at the
//                                 same archive.hunterhousefoundation.com/<key>
//                                 it would have hit directly, so behaviour is
//                                 unchanged — we just get to count it.
//   POST /event                 — a fire-and-forget usage beacon from the SPA
//                                 (item views, searches, tool opens). text/plain
//                                 body so it stays a CORS-simple request.
//
// Both write to Workers Analytics Engine (best-effort) AND console.log a
// structured line (visible in Workers Logs / `wrangler tail`) so usage is
// observable even before the Analytics Engine SQL API is wired. No cookies, no
// identifiers, no stored IPs — only coarse country, added at the edge.
//
// Config:
//   vars    R2_ACCOUNT_ID, R2_BUCKET                (wrangler.toml [vars])
//   secrets R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY  (wrangler secret put)
//   binding AE  → Analytics Engine dataset           (wrangler.toml; optional —
//                 writes are best-effort, the endpoints work without it)
//
// Endpoints:
//   GET  /list?prefix=<key-prefix>&cursor=<continuation-token>
//        → { prefix, folders:[…], files:[…], truncated, cursor }
//   GET  /dl?key=<bucket-key>     → 302 to the public archive URL (logged)
//   POST /event   {t,id,q,n,p}    → 204 (logged)
//   POST /api/notes               → 201; Baden-mode note → R2 (env.NOTES_BUCKET).
//        JSON body = text note; multipart (meta + audio) = WAV master + sidecar.
//
// Analytics Engine column map (one dataset, flexible schema):
//   blob1 event type   blob2 item id   blob3 collection (HHC/CAA/EGC/IHC/…)
//   blob4 detail (search query | download tier)   blob5 country   blob6 page|referrer
//   double1 count (search result count, or 1 per download)   index1 collection|type
// ─────────────────────────────────────────────────────────────────────────

const ALLOW_ORIGINS = new Set([
  "https://hunterhouse.org",
  "https://www.hunterhousefoundation.com",
  "https://bturep.github.io",
  "http://localhost:8777",
  "http://127.0.0.1:8777",
]);

function corsHeaders(origin) {
  const allow = ALLOW_ORIGINS.has(origin) ? origin : "https://bturep.github.io";
  return {
    "Access-Control-Allow-Origin": allow,
    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Vary": "Origin",
  };
}

// ── Folders researchers must not see ────────────────────────────────────────
// The browser is researcher-facing; these are website assets and internal
// preservation/plumbing folders, not archive content. Hiding happens HERE
// (server side, not just in the client) so they are filtered out of every
// listing AND cannot be reached by hitting /list?prefix=… directly.
//
//   HIDDEN_PREFIXES — whole subtrees hidden from the bucket root
//   HIDDEN_SEGMENTS — folder names hidden wherever they appear (any depth)
//   HIDDEN_FILES    — individual object keys hidden (exact match)
//   plus: any path segment starting with "_" is treated as internal
//         (covers _wikibase and the _pre-deskew_… master-backup folders, and
//          any future underscore-prefixed working folder, for free).
//
// NOTE on catalogue/: the folder is intentionally VISIBLE because catalogue.csv
// is the public, human-readable finding aid. Only catalogue.json (raw SPARQL
// plumbing the app uses as an offline fallback) is hidden, via HIDDEN_FILES.
const HIDDEN_PREFIXES = ["web/", "_wikibase/"];
const HIDDEN_SEGMENTS = new Set(["metadata", "intake"]);
const HIDDEN_FILES = new Set(["catalogue/catalogue.json"]);

function isHiddenKey(key) {
  if (HIDDEN_FILES.has(key)) return true;
  if (HIDDEN_PREFIXES.some((p) => key === p || key.startsWith(p))) return true;
  return key.split("/").filter(Boolean)
    .some((seg) => HIDDEN_SEGMENTS.has(seg) || seg.startsWith("_"));
}

// ── Cookieless usage analytics (download redirect + event beacon) ───────────
const PUBLIC_BASE = "https://archive.hunterhousefoundation.com";
// Whitelisted beacon event types — anything else is dropped, so the endpoint
// can't be turned into an arbitrary data sink.
const EVENT_TYPES = new Set([
  "view", "search", "search0", "deeplink",
  "collection", "curation", "timeline", "files",
]);
// Collection code from an archive id, e.g. "HH-CAA-0018" → "CAA".
function collectionOf(id) {
  const m = /^HH-([A-Za-z]+)-/.exec(id || "");
  return m ? m[1] : "";
}
// Best-effort Analytics Engine write — a no-op (never throws) if the binding
// isn't present, so the endpoints keep working on any plan.
function writePoint(env, blobs, doubles, index) {
  try {
    if (env.AE && env.AE.writeDataPoint) {
      env.AE.writeDataPoint({ blobs, doubles, indexes: index ? [index] : [] });
    }
  } catch (_) { /* analytics must never break a request */ }
}

async function recordEvent(request, env, origin) {
  // Only accept beacons from our own pages — keeps random POSTers out.
  if (!ALLOW_ORIGINS.has(origin)) return;
  let body;
  try { body = JSON.parse((await request.text()) || "{}"); } catch (_) { return; }
  const t = String(body.t || "");
  if (!EVENT_TYPES.has(t)) return;
  const id   = String(body.id || "").slice(0, 40);
  const q    = String(body.q  || "").slice(0, 80);
  const n    = Number.isFinite(+body.n) ? +body.n : 0;
  const page = String(body.p  || "").slice(0, 60);
  const country = (request.cf && request.cf.country) || "";
  const coll = collectionOf(id);
  console.log(JSON.stringify({ ev: t, id, coll, q, n, country, page }));
  writePoint(env, [t, id, coll, q, country, page], [n], coll || t);
}

// ── Baden-mode notes (POST /api/notes) ──────────────────────────────────────
// Accession material — Mowry Baden's annotations over the Hunter record. Stored
// BYTE-EXACT in R2; never transcoded here. WAV is the preservation master;
// transcription (e.g. Whisper) happens downstream, server-side, not in the app.
//
// Storage is a native R2 binding (env.NOTES_BUCKET) — same-account, so it can
// WRITE (the listing path uses cross-account READ-ONLY S3 keys and cannot). The
// notes bucket is separate from the archive bucket, so the archive itself stays
// read-only end-to-end. Layout:
//   baden-notes/<item_id>/<file>.wav         the audio master (audio note)
//   baden-notes/<item_id>/<file>.wav.json    its sidecar metadata
//   baden-notes/<item_id>/<created>.json     a text note (full payload)
const VALID_ITEM = /^HH-[A-Za-z]+-\d+$/;
const safeName = (s) => String(s || "").replace(/[^A-Za-z0-9._-]/g, "_").slice(0, 120);

// Abuse limits on the write path. These are the REAL defence: the Origin gate in
// saveNote is browser-only and forgeable (any curl can spoof it), so a hard size
// ceiling + a WAV-shape check are what keep this from being an unbounded R2 write.
const MAX_AUDIO_BYTES = 64 * 1024 * 1024;   // ~7 min of 24-bit mono 48k WAV
const MAX_META_BYTES  = 64 * 1024;          // text note / sidecar JSON ceiling

// Constant-time string compare (Workers has no timingSafeEqual).
function ctEq(a, b) {
  a = String(a == null ? "" : a); b = String(b == null ? "" : b);
  if (a.length !== b.length) return false;
  let d = 0;
  for (let i = 0; i < a.length; i++) d |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return d === 0;
}

// RIFF....WAVE magic so the "preservation master" can't be arbitrary binary.
function isWav(buf) {
  if (!buf || buf.byteLength < 12) return false;
  const v = new Uint8Array(buf, 0, 12);
  return v[0] === 0x52 && v[1] === 0x49 && v[2] === 0x46 && v[3] === 0x46 &&  // "RIFF"
         v[8] === 0x57 && v[9] === 0x41 && v[10] === 0x56 && v[11] === 0x45;   // "WAVE"
}

async function saveNote(request, env, origin, cors) {
  const J = (obj, status) => new Response(JSON.stringify(obj), {
    status: status || 200, headers: { "Content-Type": "application/json", ...cors },
  });
  if (!ALLOW_ORIGINS.has(origin)) return new Response("Forbidden", { status: 403, headers: cors });
  if (!env.NOTES_BUCKET) return J({ error: "notes storage not configured" }, 503);

  // Optional shared-secret deterrence: enforced ONLY when the NOTES_TOKEN secret
  // is configured, so writes keep working before it's set. It ships in client JS
  // (BADEN.NOTES_TOKEN), so it raises the bar against URL-scraping bots — it is
  // not strong auth. To enable: `wrangler secret put NOTES_TOKEN` + set the same
  // value on the client. A forgeable Origin header is never authentication.
  if (env.NOTES_TOKEN && !ctEq(request.headers.get("X-Notes-Token"), env.NOTES_TOKEN))
    return new Response("Forbidden", { status: 403, headers: cors });

  // Reject oversized bodies up front (before reading/buffering them).
  if (parseInt(request.headers.get("Content-Length") || "0", 10) > MAX_AUDIO_BYTES)
    return J({ error: "too large" }, 413);

  const ct = request.headers.get("Content-Type") || "";
  try {
    if (ct.includes("application/json")) {
      const meta = await request.json();
      if (!VALID_ITEM.test(meta.item_id || "")) return J({ error: "bad item_id" }, 400);
      const body = JSON.stringify(meta);
      if (body.length > MAX_META_BYTES) return J({ error: "too large" }, 413);
      const stamp = safeName(meta.created || new Date().toISOString());
      const key = `baden-notes/${meta.item_id}/${stamp}.json`;
      await env.NOTES_BUCKET.put(key, body, {
        httpMetadata: { contentType: "application/json" },
        customMetadata: { author: safeName(meta.author), item: meta.item_id, kind: "text" },
      });
      console.log(JSON.stringify({ ev: "note", kind: "text", item: meta.item_id, key }));
      return J({ ok: true, key }, 201);
    }

    if (ct.includes("multipart/form-data")) {
      const form = await request.formData();
      let meta = {};
      try { meta = JSON.parse(form.get("meta") || "{}"); } catch (_) {}
      const audio = form.get("audio");
      if (!VALID_ITEM.test(meta.item_id || "")) return J({ error: "bad item_id" }, 400);
      if (JSON.stringify(meta).length > MAX_META_BYTES) return J({ error: "meta too large" }, 413);
      if (!audio || typeof audio.arrayBuffer !== "function") return J({ error: "no audio" }, 400);
      // safeName can empty-out an all-symbol filename; fall back so we never write a bare dir key.
      const base = safeName(meta.filename) || safeName(`MBN_${meta.item_id}_${Date.now()}.wav`);
      const wavKey = `baden-notes/${meta.item_id}/${base}`;
      const bytes = await audio.arrayBuffer();   // byte-exact, no transcode
      if (bytes.byteLength > MAX_AUDIO_BYTES) return J({ error: "audio too large" }, 413);
      if (!isWav(bytes)) return J({ error: "not a WAV" }, 415);
      await env.NOTES_BUCKET.put(wavKey, bytes, {
        httpMetadata: { contentType: "audio/wav" },
        customMetadata: { author: safeName(meta.author), item: meta.item_id, kind: "audio" },
      });
      await env.NOTES_BUCKET.put(wavKey + ".json", JSON.stringify(meta), {
        httpMetadata: { contentType: "application/json" },
      });
      console.log(JSON.stringify({ ev: "note", kind: "audio", item: meta.item_id, key: wavKey, bytes: bytes.byteLength }));
      return J({ ok: true, key: wavKey }, 201);
    }

    return J({ error: "unsupported content-type" }, 415);
  } catch (err) {
    console.error("saveNote error:", String(err));   // log server-side; don't leak internals
    return J({ error: "save failed" }, 500);
  }
}

function downloadRedirect(request, env, url, cors) {
  const key = url.searchParams.get("key") || "";
  // Bucket-relative keys only — reject absolute URLs, protocol-relative,
  // path traversal, and anything the listing hides.
  if (!key || /^https?:|^\/\/|:\/\/|\.\./.test(key) || isHiddenKey(key)) {
    return new Response("Bad key", { status: 400, headers: cors });
  }
  const coll = key.split("/")[0] || "";
  const tier = key.split("/")[1] || "";   // masters/previews/large/thumbs/pdf
  const country = (request.cf && request.cf.country) || "";
  const ref = (request.headers.get("Referer") || "").slice(0, 80);
  console.log(JSON.stringify({ ev: "download", coll, tier, key, country, ref }));
  writePoint(env, ["download", "", coll, tier, country, ref], [1], coll || "download");
  const target = PUBLIC_BASE + "/" + key.split("/").map(encodeURIComponent).join("/");
  return new Response(null, {
    status: 302,
    // no-store so every click re-hits the Worker and is counted (a cached
    // redirect would silently undercount repeat downloads).
    headers: { "Location": target, "Cache-Control": "no-store", ...cors },
  });
}

// ── AWS SigV4 (minimal, GET-only, empty body) via Web Crypto ────────────────
const enc = new TextEncoder();
function hex(buf) {
  return [...new Uint8Array(buf)].map((b) => b.toString(16).padStart(2, "0")).join("");
}
async function sha256hex(msg) {
  return hex(await crypto.subtle.digest("SHA-256", typeof msg === "string" ? enc.encode(msg) : msg));
}
async function hmac(key, msg) {
  const k = await crypto.subtle.importKey(
    "raw", typeof key === "string" ? enc.encode(key) : key,
    { name: "HMAC", hash: "SHA-256" }, false, ["sign"]
  );
  return new Uint8Array(await crypto.subtle.sign("HMAC", k, enc.encode(msg)));
}
// RFC3986 encoding for canonical query (encodeURIComponent + the chars it skips)
function enc3986(s) {
  return encodeURIComponent(s).replace(/[!*'()]/g, (c) => "%" + c.charCodeAt(0).toString(16).toUpperCase());
}
function decodeXmlEntities(s) {
  return s.replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">")
          .replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&apos;/g, "'");
}

async function signedR2List(env, prefix, cursor) {
  const region = "auto", service = "s3";
  const host = `${env.R2_ACCOUNT_ID}.r2.cloudflarestorage.com`;
  const canonUri = `/${env.R2_BUCKET}`;

  const params = { "delimiter": "/", "list-type": "2", "prefix": prefix || "" };
  if (cursor) params["continuation-token"] = cursor;
  const canonQuery = Object.keys(params).sort()
    .map((k) => `${enc3986(k)}=${enc3986(params[k])}`).join("&");

  const now = new Date();
  const amzDate = now.toISOString().replace(/[:-]|\.\d{3}/g, "");   // 20260530T162000Z
  const dateStamp = amzDate.slice(0, 8);                            // 20260530
  const payloadHash = await sha256hex("");

  const canonHeaders = `host:${host}\nx-amz-content-sha256:${payloadHash}\nx-amz-date:${amzDate}\n`;
  const signedHeaders = "host;x-amz-content-sha256;x-amz-date";
  const canonReq = `GET\n${canonUri}\n${canonQuery}\n${canonHeaders}\n${signedHeaders}\n${payloadHash}`;

  const scope = `${dateStamp}/${region}/${service}/aws4_request`;
  const stringToSign = `AWS4-HMAC-SHA256\n${amzDate}\n${scope}\n${await sha256hex(canonReq)}`;

  const kDate = await hmac("AWS4" + env.R2_SECRET_ACCESS_KEY, dateStamp);
  const kRegion = await hmac(kDate, region);
  const kService = await hmac(kRegion, service);
  const kSigning = await hmac(kService, "aws4_request");
  const signature = hex(await hmac(kSigning, stringToSign));

  const authorization =
    `AWS4-HMAC-SHA256 Credential=${env.R2_ACCESS_KEY_ID}/${scope}, ` +
    `SignedHeaders=${signedHeaders}, Signature=${signature}`;

  return fetch(`https://${host}${canonUri}?${canonQuery}`, {
    headers: {
      "x-amz-date": amzDate,
      "x-amz-content-sha256": payloadHash,
      "Authorization": authorization,
    },
  });
}

function parseListXml(xml, prefix) {
  const folders = [];
  for (const m of xml.matchAll(/<CommonPrefixes>[\s\S]*?<Prefix>([\s\S]*?)<\/Prefix>[\s\S]*?<\/CommonPrefixes>/g)) {
    const key = decodeXmlEntities(m[1]);
    folders.push({ type: "folder", key, name: key.slice(prefix.length).replace(/\/$/, "") });
  }
  const files = [];
  for (const m of xml.matchAll(/<Contents>([\s\S]*?)<\/Contents>/g)) {
    const block = m[1];
    const key = decodeXmlEntities((block.match(/<Key>([\s\S]*?)<\/Key>/) || [])[1] || "");
    const size = parseInt((block.match(/<Size>(\d+)<\/Size>/) || [])[1] || "0", 10);
    const uploaded = (block.match(/<LastModified>([\s\S]*?)<\/LastModified>/) || [])[1] || null;
    const name = key.slice(prefix.length);
    if (!name) continue;   // skip the folder-placeholder object (key === prefix)
    files.push({ type: "file", key, name, size, uploaded });
  }
  const truncated = /<IsTruncated>true<\/IsTruncated>/.test(xml);
  const cursor = truncated
    ? decodeXmlEntities((xml.match(/<NextContinuationToken>([\s\S]*?)<\/NextContinuationToken>/) || [])[1] || "")
    : null;
  folders.sort((a, b) => a.name.localeCompare(b.name));
  files.sort((a, b) => a.name.localeCompare(b.name));
  return { folders, files, truncated, cursor };
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get("Origin") || "";
    const cors = corsHeaders(origin);
    const url = new URL(request.url);

    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: cors });

    // ── Usage beacon (POST) ──────────────────────────────────────────────
    if (url.pathname === "/event") {
      if (request.method !== "POST")
        return new Response("Method Not Allowed", { status: 405, headers: cors });
      await recordEvent(request, env, origin);
      return new Response(null, { status: 204, headers: cors });
    }

    // ── Baden-mode notes → write to R2 (audio WAV + JSON sidecar, or text) ─
    if (url.pathname === "/api/notes") {
      if (request.method !== "POST")
        return new Response("Method Not Allowed", { status: 405, headers: cors });
      return saveNote(request, env, origin, cors);
    }

    // ── Tracked download → 302 to the public file ────────────────────────
    if (url.pathname === "/dl") {
      if (request.method !== "GET")
        return new Response("Method Not Allowed", { status: 405, headers: cors });
      return downloadRedirect(request, env, url, cors);
    }

    // ── Directory listing (the original purpose) ─────────────────────────
    if (request.method !== "GET") return new Response("Method Not Allowed", { status: 405, headers: cors });
    if (url.pathname !== "/list") return new Response("Not Found", { status: 404, headers: cors });

    if (!env.R2_ACCESS_KEY_ID || !env.R2_SECRET_ACCESS_KEY) {
      return new Response(
        JSON.stringify({ error: "not configured", detail: "R2_ACCESS_KEY_ID / R2_SECRET_ACCESS_KEY secrets not set" }),
        { status: 500, headers: { "Content-Type": "application/json", ...cors } }
      );
    }

    const prefix = url.searchParams.get("prefix") || "";
    const cursor = url.searchParams.get("cursor") || "";

    // Refuse to drill into a hidden folder even if asked directly.
    if (prefix && isHiddenKey(prefix)) {
      return new Response(
        JSON.stringify({ prefix, folders: [], files: [], truncated: false, cursor: null }),
        { headers: { "Content-Type": "application/json", "Cache-Control": "public, max-age=60", ...cors } }
      );
    }

    let res, xml;
    try {
      res = await signedR2List(env, prefix, cursor);
      xml = await res.text();
    } catch (err) {
      return new Response(JSON.stringify({ error: "list failed", detail: String(err) }),
        { status: 502, headers: { "Content-Type": "application/json", ...cors } });
    }
    if (!res.ok) {
      return new Response(JSON.stringify({ error: "s3 error", status: res.status, detail: xml.slice(0, 500) }),
        { status: 502, headers: { "Content-Type": "application/json", ...cors } });
    }

    const parsed = parseListXml(xml, prefix);
    // Drop hidden folders/files from the listing the researcher receives.
    parsed.folders = parsed.folders.filter((f) => !isHiddenKey(f.key));
    parsed.files = parsed.files.filter((f) => !isHiddenKey(f.key));
    return new Response(JSON.stringify({ prefix, ...parsed }), {
      headers: {
        "Content-Type": "application/json",
        "Cache-Control": "public, max-age=60",
        ...cors,
      },
    });
  },
};
