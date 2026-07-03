#!/usr/bin/env node
// Pre-push validation for HunterHouse — runs in CI on every push to main.
// Catches the "JS syntax error / malformed VERSION → live archive offline"
// failure mode that no other guard covers (no tests, no linter, no build).
//
// Checks:
//   1. Each inline <script> block in browse.html and next.html parses as JS
//      (node --check, treated as a classic script — matches browser semantics).
//   2. The VERSION constant in each file matches the expected pattern:
//        browse.html → vMAJOR.SESSION.PATCH  e.g. v1.06.31
//        next.html   → vMAJOR.SESSION-test.NN  e.g. v1.07-test.51
//   3. manifest.json and manifest.next.json parse as JSON.
//   4. If browse.html or next.html changed since the previous push, its
//      VERSION constant must have changed too — catches "forgot to bump"
//      pushes that would otherwise leave returning visitors on a stale
//      localStorage cache. Compares against $HH_PREVIOUS_SHA (set in CI
//      from github.event.before / pull_request.base.sha) and falls back
//      to HEAD~1 locally; skips with a notice if neither is available.
//
// Failure → exits non-zero. GitHub Actions then emails the repo owner on the
// failed run, which is the audit's "alert without gating the push" model.

import { readFileSync, writeFileSync, mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { execFileSync } from "node:child_process";

const HTMLS = [
  { file: "browse.html", versionRe: /^v\d+\.\d{2}\.\d{2}$/,        kind: "live"    },
  { file: "next.html",   versionRe: /^v\d+\.\d{2}-test\.\d{2,}$/,  kind: "staging" },
];
const MANIFESTS = ["manifest.json", "manifest.next.json"];

// Inline <script> only — skip src=… loads. Greedy across newlines.
const SCRIPT_BLOCK_RE = /<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/gi;
const VERSION_RE      = /\bconst\s+VERSION\s*=\s*"([^"]+)"\s*;/;

let failures = 0;
const fail = (msg) => { console.error("✗ " + msg); failures++; };
const pass = (msg) => { console.log  ("✓ " + msg); };

const tmp = mkdtempSync(join(tmpdir(), "hh-validate-"));

for (const { file, versionRe, kind } of HTMLS) {
  let html;
  try { html = readFileSync(file, "utf8"); }
  catch (e) { fail(`${file}: cannot read (${e.message})`); continue; }

  // (1) VERSION presence + pattern
  const vm = html.match(VERSION_RE);
  if (!vm) {
    fail(`${file}: VERSION constant not found (expected: const VERSION = "...")`);
  } else if (!versionRe.test(vm[1])) {
    fail(`${file}: VERSION "${vm[1]}" does not match ${kind} pattern ${versionRe}`);
  } else {
    pass(`${file}: VERSION ${vm[1]} (${kind})`);
  }

  // (2) Each inline <script> block parses as JS.
  // Strip HTML comments first so a comment that happens to contain the
  // string "<script>" (e.g. CSP documentation prose) isn't mistaken for
  // an opening tag.
  const htmlNoComments = html.replace(/<!--[\s\S]*?-->/g, "");
  let block = 0, m;
  SCRIPT_BLOCK_RE.lastIndex = 0;
  while ((m = SCRIPT_BLOCK_RE.exec(htmlNoComments)) !== null) {
    block++;
    const code = m[1];
    if (!code.trim()) continue;
    const tmpFile = join(tmp, `${file.replace(/[^a-z0-9]/gi, "_")}.block${block}.js`);
    writeFileSync(tmpFile, code);
    try {
      execFileSync(process.execPath, ["--check", tmpFile], { stdio: "pipe" });
      pass(`${file} <script> #${block}: syntax OK (${code.length.toLocaleString()} chars)`);
    } catch (e) {
      const detail = (e.stderr?.toString() || e.message).split("\n").slice(0, 4).join("\n      ");
      fail(`${file} <script> #${block}: parse failed\n      ${detail}`);
    }
  }
}

// (3) Manifests parse as JSON
for (const file of MANIFESTS) {
  try {
    const obj = JSON.parse(readFileSync(file, "utf8"));
    if (!obj.start_url) fail(`${file}: missing required "start_url"`);
    else                pass(`${file}: parses as JSON, start_url=${obj.start_url}`);
  } catch (e) {
    fail(`${file}: ${e.message}`);
  }
}

// (4) VERSION-bump-on-substantive-change.
// If browse.html or next.html changed since the previous push, its VERSION
// must have changed too. Cheap guard against the "forgot to bump → returning
// visitors hit stale localStorage" foot-gun. Skips silently if no previous
// SHA is available (first-ever commit, or detached state with no parent).
function git(args) {
  try { return execFileSync("git", args, { stdio: ["pipe", "pipe", "pipe"] }).toString(); }
  catch { return null; }
}
const ZERO_SHA = "0000000000000000000000000000000000000000";
function previousSha() {
  const env = process.env.HH_PREVIOUS_SHA;
  if (env && env !== ZERO_SHA && /^[0-9a-f]{4,40}$/i.test(env)) return env;
  const head1 = git(["rev-parse", "--verify", "HEAD~1"]);
  return head1 ? head1.trim() : null;
}
const prevSha = previousSha();
if (!prevSha) {
  console.log("\n(VERSION-bump check skipped — no previous SHA available)");
} else {
  console.log(`\nVERSION-bump check (vs. ${prevSha.slice(0, 7)}):`);
  for (const { file } of HTMLS) {
    // Compare PREV against the working tree (no ..HEAD) so the same check
    // catches uncommitted changes when run locally before a push. In CI,
    // working tree == HEAD, so the result is identical.
    const diff = git(["diff", "--name-only", prevSha, "--", file]);
    if (diff === null) {
      // git error (likely the prev SHA isn't in the local history). Skip
      // rather than fail — the rest of the validator's coverage stands.
      console.log(`  ${file}: (skipped — couldn't compare against ${prevSha.slice(0, 7)})`);
      continue;
    }
    if (!diff.trim()) {
      pass(`${file}: unchanged since ${prevSha.slice(0, 7)}`);
      continue;
    }
    const oldContent = git(["show", `${prevSha}:${file}`]);
    if (oldContent === null) {
      // File didn't exist at that SHA (rare — net-new file). Treat as bumped.
      pass(`${file}: new since ${prevSha.slice(0, 7)} (no prior VERSION to compare)`);
      continue;
    }
    const oldVer = oldContent.match(VERSION_RE)?.[1];
    const newVer = readFileSync(file, "utf8").match(VERSION_RE)?.[1];
    if (!oldVer || !newVer) {
      console.log(`  ${file}: (couldn't read VERSION on one side — skipped)`);
      continue;
    }
    if (oldVer === newVer) {
      fail(`${file}: changed but VERSION is still "${newVer}" — bump it before pushing`);
    } else {
      pass(`${file}: VERSION bumped ${oldVer} → ${newVer}`);
    }
  }
}

// (5) Promotion invariants (audit B5) — browse.html is the LIVE file; each of
// these encodes a real, previously-shipped promotion mistake:
//   · v1.08 promotion shipped the staging manifest to live (857053d)
//   · v1.08 promotion shipped staging title/icons to live (c2a4a30)
//   · a stray "-test." VERSION on live would poison returning visitors' caches
try {
  const live = readFileSync("browse.html", "utf8");
  const liveVer = live.match(VERSION_RE)?.[1] || "";
  if (live.includes("manifest.next.json"))
    fail("browse.html: references manifest.next.json — staging manifest must not ship to live");
  else pass("browse.html: manifest reference is live (manifest.json)");
  if (liveVer.includes("-test."))
    fail(`browse.html: VERSION "${liveVer}" carries -test. — staging version must not ship to live`);
  else pass("browse.html: VERSION is a live version (no -test.)");
  if (!/<title>\s*Hunter House Archive\s*<\/title>/.test(live))
    fail("browse.html: <title> is not the live title 'Hunter House Archive' — staging title shipped?");
  else pass("browse.html: live <title> intact");
} catch (e) { fail("promotion-invariant checks: " + e.message); }

// (6) sw.js must parse, and an assets/ or sw.js change should come with a
// CACHE_NAME bump (stale-cache foot-gun; warn-level check → fails only on
// a definite miss, skips when history is unavailable).
try {
  const swFile = join(tmp, "sw.check.js");
  writeFileSync(swFile, readFileSync("sw.js", "utf8"));
  execFileSync(process.execPath, ["--check", swFile], { stdio: "pipe" });
  pass("sw.js: syntax OK");
} catch (e) { fail("sw.js: parse failed — " + (e.stderr?.toString() || e.message).split("\n")[0]); }
if (prevSha) {
  try {
    const assetDiff = git(["diff", "--name-only", prevSha, "--", "assets/", "sw.js"]);
    if (assetDiff && assetDiff.trim()) {
      const oldSw = git(["show", `${prevSha}:sw.js`]) || "";
      // sw.js declares CACHE_NAME with SINGLE quotes — accept either.
      const cacheRe = /CACHE_NAME\s*=\s*['"]([^'"]+)['"]/;
      const oldCache = oldSw.match(cacheRe)?.[1];
      const newCache = readFileSync("sw.js", "utf8").match(cacheRe)?.[1];
      if (oldCache && newCache && oldCache === newCache)
        console.log(`  ⚠ assets/ or sw.js changed but CACHE_NAME is still "${newCache}" — cached visitors may not see the change (notice only)`);
      else pass(`sw.js CACHE_NAME: ${oldCache || "?"} → ${newCache || "?"}`);
    }
  } catch (e) { console.log("  (CACHE_NAME check skipped — " + e.message.split("\n")[0] + ")"); }
}

rmSync(tmp, { recursive: true, force: true });

if (failures) {
  console.error(`\n${failures} validation failure(s) — see above`);
  process.exit(1);
}
console.log("\nall validations passed");
