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
//
// Failure → exits non-zero. GitHub Actions then emails the repo owner on the
// failed run, which is the audit's "alert without gating the push" model.

import { readFileSync, writeFileSync, mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { execFileSync } from "node:child_process";

const HTMLS = [
  { file: "browse.html", versionRe: /^v\d+\.\d{2}\.\d{2}$/,        kind: "live"    },
  { file: "next.html",   versionRe: /^v\d+\.\d{2}-test\.\d{2}$/,   kind: "staging" },
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

  // (2) Each inline <script> block parses as JS
  let block = 0, m;
  SCRIPT_BLOCK_RE.lastIndex = 0;
  while ((m = SCRIPT_BLOCK_RE.exec(html)) !== null) {
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

rmSync(tmp, { recursive: true, force: true });

if (failures) {
  console.error(`\n${failures} validation failure(s) — see above`);
  process.exit(1);
}
console.log("\nall validations passed");
