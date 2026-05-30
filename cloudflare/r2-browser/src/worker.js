// ─────────────────────────────────────────────────────────────────────────
// Hunter House Foundation — read-only R2 bucket-listing Worker
//
// Powers the researcher "bucket browser" in next.html. The ONLY thing this
// Worker can do is LIST: it calls env.BUCKET.list() and returns the folders +
// files at one level. There is no put/delete/copy anywhere in this file, so
// the archive can never be written to or rearranged through it.
//
// Downloads do NOT pass through this Worker. Each file in the UI links to its
// existing public URL — https://archive.hunterhousefoundation.com/<key> — which
// the R2 custom domain already serves. This Worker is purely a directory index.
//
// Endpoint:  GET /list?prefix=<key-prefix>&cursor=<pagination-cursor>
//   prefix   "" (root) → the top-level collection folders; or e.g.
//            "hunter-house-collection/masters/" for that folder's contents.
//   cursor   opaque token from a previous truncated response (folders/files
//            with >1000 entries; rare — only deep flat folders).
//
// Response:  { prefix, folders:[{type,key,name}], files:[{type,key,name,size,
//             uploaded}], truncated, cursor }
// ─────────────────────────────────────────────────────────────────────────

// Origins allowed to read the listing. Add the staging/live site + loopback
// dev servers. (Downloads are governed by the bucket's own CORS, not this.)
const ALLOW_ORIGINS = new Set([
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

export default {
  async fetch(request, env) {
    const origin = request.headers.get("Origin") || "";
    const cors = corsHeaders(origin);

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: cors });
    }
    if (request.method !== "GET") {
      return new Response("Method Not Allowed", { status: 405, headers: cors });
    }

    const url = new URL(request.url);
    if (url.pathname !== "/list") {
      return new Response("Not Found", { status: 404, headers: cors });
    }

    const prefix = url.searchParams.get("prefix") || "";
    const cursor = url.searchParams.get("cursor") || undefined;

    let listing;
    try {
      listing = await env.BUCKET.list({
        prefix,
        delimiter: "/",   // one level at a time → lazy tree navigation
        cursor,
        limit: 1000,
      });
    } catch (err) {
      return new Response(
        JSON.stringify({ error: "list failed", detail: String(err) }),
        { status: 502, headers: { "Content-Type": "application/json", ...cors } }
      );
    }

    // delimitedPrefixes are the "subfolders"; objects are the files at this level.
    const folders = (listing.delimitedPrefixes || [])
      .map((p) => ({ type: "folder", key: p, name: p.slice(prefix.length).replace(/\/$/, "") }))
      .filter((f) => f.name.length > 0)
      .sort((a, b) => a.name.localeCompare(b.name));

    const files = (listing.objects || [])
      .map((o) => ({
        type: "file",
        key: o.key,
        name: o.key.slice(prefix.length),
        size: o.size,
        uploaded: o.uploaded,   // Date → serialized ISO string
      }))
      .filter((f) => f.name.length > 0)   // drop the folder placeholder object itself
      .sort((a, b) => a.name.localeCompare(b.name));

    const body = JSON.stringify({
      prefix,
      folders,
      files,
      truncated: listing.truncated || false,
      cursor: listing.truncated ? listing.cursor : null,
    });

    return new Response(body, {
      headers: {
        "Content-Type": "application/json",
        "Cache-Control": "public, max-age=60",   // brief CDN cache; listings change rarely
        ...cors,
      },
    });
  },
};
