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
// Downloads do NOT pass through this Worker — each file links to its public URL
// https://archive.hunterhousefoundation.com/<key>, served by the R2 custom
// domain. This Worker is purely a directory index.
//
// Config:
//   vars    R2_ACCOUNT_ID, R2_BUCKET                (wrangler.toml [vars])
//   secrets R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY  (wrangler secret put)
//
// Endpoint: GET /list?prefix=<key-prefix>&cursor=<continuation-token>
//   → { prefix, folders:[{type,key,name}],
//       files:[{type,key,name,size,uploaded}], truncated, cursor }
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
    "Access-Control-Allow-Methods": "GET, OPTIONS",
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

    if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: cors });
    if (request.method !== "GET") return new Response("Method Not Allowed", { status: 405, headers: cors });

    const url = new URL(request.url);
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
