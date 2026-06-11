# AUDIT.md — browse.html, ahead of "Baden mode"

Phase 1 of `CLAUDE_CODE_TASK_baden(2).md`. Read-only audit; **nothing in the
source has been changed yet.** Every finding below is verified against the
actual served source (`browse.html`, live `v1.08.02`) with line numbers, not
inferred from the task brief. Where the brief's assumptions did **not** hold
up against the source, that is called out explicitly.

> ⚠ **Project-rule conflict — read first.** This repo is on **LINE: NEXT**
> (`CLAUDE.md`): all browse work goes in **`next.html`**; `browse.html` is the
> frozen live tool and must not be edited except to fix a real live breakage.
> The task brief names `browse.html` throughout. `browse.html` (v1.08.02) and
> `next.html` (v1.09-test.04) are byte-near-identical (8646 vs 8659 lines — the
> 13-line delta is the timeline + curator code that's gated off on live). This
> is a **Brandon decision** and is the first open question at the bottom of this
> file. The audit findings are identical for either file.

---

## 1. Default-path findings (shared by Baden mode and ordinary visitors)

### 1.1 Viewport `maximum-scale=1` — CONFIRMED, mandatory fix
`browse.html:6` (and `next.html:6`):
```html
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
```
`maximum-scale=1` blocks iPadOS pinch-zoom and the system "Larger Text"
accommodation → **WCAG 1.4.4 (Resize Text)** failure. This is the one
default-path change the brief marks mandatory and the audit agrees: drop
`maximum-scale=1`, leaving `width=device-width,initial-scale=1`. Affects every
visitor, not just Baden — so under LINE: NEXT this is itself a reason the work
wants to be staged + promoted rather than hot-patched onto live.

### 1.2 Orientation lock — TWO separate mechanisms (brief found only the prompt)
The brief describes a "Rotate to portrait" prompt. The source actually has
**two** orientation mechanisms, and the consequential one is the JS lock, not
the prompt:

- **(a) Programmatic hard lock — the real one.** `browse.html:8638–8641`:
  ```js
  if (screen.orientation && screen.orientation.lock) {
    screen.orientation.lock('portrait').catch(() => {});
  }
  ```
  Runs unconditionally on every load. No-ops in desktop Safari (lock only works
  in installed/standalone PWA + fullscreen), but on Baden's **home-screen-icon
  iPad PWA it will genuinely force portrait** → **WCAG 1.3.4 (Orientation)**
  failure, and directly conflicts with Phase 3's "works in both orientations"
  requirement. **Baden mode must not run this.**
- **(b) CSS prompt — cosmetic, won't fire on the iPad.** Markup `#rotate-msg`
  (`browse.html:2594`), shown by `@media (orientation:landscape) and
  (max-height:500px)` (`browse.html:1981–1983`). The `max-height:500px` gate is
  a *phone-landscape* test; the iPad Mini's short side is 768pt, so this prompt
  **never appears on the iPad** in either orientation. Flag it (per brief) but
  it is not a Baden blocker.

Recommendation: gate the `screen.orientation.lock` call so it is skipped in
Baden mode (and arguably guarded generally — flagged for the maintainer per the
brief, default path otherwise left to Brandon).

### 1.3 `aria-live` on the Wikibase loading state — MISSING (valid finding)
`#load-screen` (`browse.html:2717–2720`) carries the visible "Loading Archive
Data from Wikibase…" text but has **no `role`/`aria-live`**, so a screen reader
never announces load or load-failure. (The toast helper *does* set
`role=status`/`aria-live=polite`, `browse.html:3222–3225` — so the pattern
exists in-repo to copy.) Baden mode's loading + error states must be announced;
adding `aria-live` to `#load-screen` is a cheap shared win.

---

## 2. The two "markup bugs" in the brief — VERIFIED, and they are NOT bugs

The brief asserts "an `<img>` with empty src and an `about:blank` reference …
bugs regardless of mode." Verified against source — **neither is a genuine
bug**, and "fixing" them risks a real regression. Reporting honestly rather
than making a cosmetic change the brief expects:

- **`about:blank`** = `#pdf-frame` (`browse.html:2782`), reset to `about:blank`
  on PDF close to free the renderer (`browse.html:8325`). This is the standard
  idle-iframe idiom — intentional and correct. An *empty* iframe `src` would be
  the bug; `about:blank` is the fix for that bug, not the bug. **No change.**
  (Baden mode omits PDF entirely anyway, per brief §Modals.)
- **"empty src `<img>`"** = `#mob-sheet-img` (`browse.html:2870`):
  `<img id="mob-sheet-img" class="mob-sheet-img" alt="">` — it has **no `src`
  attribute at all**, which is *not* the same as `src=""`. A missing `src`
  issues **no** network request; only a literal `src=""` re-requests the page
  URL (the actual bug pattern), and that string does not occur anywhere in
  `browse.html`. This is a valid JS-populated placeholder. **No change**
  (a marginal a11y nit — `alt=""` on a content image — but it's mobile-sheet
  only and out of Baden scope).

**Conclusion:** the source is clean on both counts. I'll note the discrepancy
and, unless you say otherwise, make no edit here. If the brief's author saw
these in a DOM inspector, they were looking at the intended idle/placeholder
states, not defects.

---

## 3. Gesture / interaction inventory on the desktop stage (all bypassed by Baden mode)

Baden's RECORD view is specified as a **native-scroll overflow container with no
custom drag handlers**, so none of the following should be wired in Baden mode —
listed so the parallel path is known to share zero gesture code with the
default stage:

| Handler | Location | Baden mode |
|---|---|---|
| `wheel` zoom on stage | `browse.html:6367` | not wired |
| `dblclick` → fit | `browse.html:6374` | not wired (double-tap is a precision/timing gesture — excluded for tremor) |
| custom pan `touchstart/move/end` on `#canvas` | `6390–6417` | replaced by native momentum scroll |
| mobile bottom-sheet swipe pipeline | `7080–7219` | not used (Baden is its own single-column layout) |
| list drag-reorder `pointerdown/move/up` | `7354–7384` | not used |
| `−/+`, FIT, 1:1, ↻, fullscreen controls | `2786–2802` | replaced by 3 fixed buttons: Fit / Bigger / Full size |

`touch-action`: global `manipulation` (`browse.html:490`); `#canvas` uses
`touch-action:none` for custom pan (`~931`). Baden's scroll container must
**not** inherit `none` — it needs `auto`/`pan-x pan-y` so native momentum +
pinch fallback work.

---

## 4. Items that require a *rendered* measurement pass (Phase 3, not source-readable)

These can't be honestly answered from source alone — they need the page rendered
at 768×1024 / 1024×768 and measured. Deferred to Phase 3 tooling (axe-core/pa11y
+ a scripted boundingRect/contrast sweep), per the brief:

- Rendered tap-target sizes of every control (brief's ≥64px Baden / the desktop
  fix-list). Source has CSS but computed px depends on the breakpoint.
- Contrast ratios. Note: the existing `#1a1816` theme is the **dark** surface;
  Baden's **default is a new light high-contrast theme (≥7:1 body)**, so Baden
  needs its own palette tokens — it can't lean on the current dark tokens. Both
  Baden themes get measured in Phase 3 (≥7:1 light, ≥4.5:1 dark).
- `pointer-up` (not -down) firing on Baden controls; focus management + inert
  scrim on Baden modals; `prefers-reduced-motion`.

---

## 5. Architecture reality check — the Notes backend (brief §Persistence)

The brief specifies "a minimal **server script in `server/`** … writing JSONL +
WAV files to disk." **This site has no server.** It is **static GitHub Pages**
(`.nojekyll`, deploy-on-push); nothing in-repo can run Python/Node or write to
disk in production. The existing *first-party* infra the brief points to is a
**Cloudflare Worker** (`cloudflare/r2-browser/`, on Brandon's personal CF
account) plus **R2** object storage — that is the discoverable pattern, and it
is a Worker, not a disk-writing server.

So the brief's `server/`-writes-to-disk design is **architecturally
incompatible with the deployment**. The faithful-to-intent equivalent is a
**Cloudflare Worker `POST /api/notes` that streams the WAV + JSON sidecar into
R2** (byte-exact, no transcode), mirroring the analytics/R2-browser Workers
already in production. This is a Brandon decision (open question B below). The
*client* half — IndexedDB-first, retry queue, Web Share "Export my notes",
mailto fallback for text — is deployment-agnostic and proceeds regardless.

---

## 6. Open decisions before Phase 2 (need Brandon)

- **A. Target file.** `browse.html` (brief) vs `next.html` (LINE: NEXT rule).
  Knock-on: the iPad home-screen icon points at a real URL now; if built in
  `next.html` the icon is `next.html?for=baden` until promotion.
- **B. Notes backend.** Worker→R2 (fits infra, recommended) vs literal local
  `server/` script (matches brief text, undeployable on Pages) vs client-only
  for now (IndexedDB + Export-my-notes, defer the endpoint).
- **C. Sequencing.** One branch landing the whole feature, vs staged
  (audit+viewport+client UI first, audio capture + backend second).

## 7. Phase 3 manual checklist (to be filled during verification)

- [ ] mode persists across reload (`?for=baden` → localStorage → bare URL restores)
- [ ] curated order respected; manifest-down + bad-ID show readable error + Retry
- [ ] Full size loads the ORIGINAL asset (not CSS-upscaled preview)
- [ ] scroll center preserved across Fit/Bigger/Full size
- [ ] text note → IndexedDB + POST (or queues) ; edit round-trips
- [ ] audio note records / plays / re-records / saves ; file is valid **PCM WAV**
      (header: RIFF/WAVE, sample rate, bit depth — NOT AAC/MP4)
- [ ] queued uploads retry on next load ; "Send now" works
- [ ] Export-my-notes share sheet includes the WAV files
- [ ] both orientations, both target sizes (768×1024 / 1024×768), no h-overflow
- [ ] axe-core/pa11y: zero serious/critical in Baden mode
- [ ] mic permission works from the home-screen standalone icon (or documented
      Safari-bookmark fallback) — **must be tested on the actual device**
