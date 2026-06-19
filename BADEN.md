# Baden mode — "Selected for Mowry Baden"

A private viewing room inside the archive viewer, built for **Mowry Baden**
(sculptor, 92, hand tremor, browsing on an iPad Mini, touch only). He can walk a
curated set of items, view drawings at full resolution, and **leave notes — by
voice or by typing** — which are captured as archival material.

It is a **parallel rendering path** inside `next.html` (and `browse.html` once
promoted), gated by a URL parameter. Ordinary visitors and the desktop research
tool are completely unaffected — Baden mode is invisible unless switched on.

> Status: built + verified in **`next.html` (v1.09-test.05)** on branch
> `feature/baden-mode`. Rides the next promotion to `browse.html`. Two things
> remain for Brandon before handover — see **Before handover** below.

---

## Turning it on / off

| URL | Effect |
|---|---|
| `…/next.html?for=baden` | Enter Baden mode; **remembered** on this device (localStorage) |
| `…/next.html` (bare) | If this device entered Baden mode before, it stays in it |
| `…/next.html?for=off` | Leave Baden mode on this device |

It is a **courtesy-private** URL, not security — nothing secret is behind it.

After promotion the live URL is `https://hunterhouse.org/browse.html?for=baden`.

### Home-screen install (built 2026-06-18)
The viewing room is meant to live as a **home-screen icon** on Mowry's iPad — because
the mode persists, the icon opens straight in with zero input. iPadOS Safari can't
auto-install (no install API; nothing can add itself), so two things make it work:

- **An accessible first-open guide** (`#bd-install` sheet, Baden-only). The first time
  the room opens *and it isn't already a home-screen app*, a large, plain card shows the
  three iPad-Safari steps (Share → Add to Home Screen → Add) with the Share glyph. Tapping
  **Got it** dismisses it for good (`localStorage hhf_baden_install_seen`). It never shows
  when launched from the installed icon (`navigator.standalone`).
- **A Baden manifest** (`manifest.baden.next.json`, `start_url: ./next.html?for=baden`).
  The head IIFE repoints `<link rel=manifest>` to it **only when Baden mode is on**, and
  sets the icon label to "Hunter House". So an installed icon launches into `?for=baden`
  (lands in the standalone storage with the flag set) — and an ordinary visitor's install
  is completely unaffected (they keep `manifest.next.json` / "HH Next").

> **No auto-install is possible on iPad** — confirmed. If Brandon isn't there to do the
> Share→Add taps, just send the `?for=baden` link: it works fully in Safari with no install
> (the room *is* the page), and the icon is pure convenience added later.

> **⚠ Promotion to `browse.html`:** the IIFE reference `manifest.baden.next.json` and the
> `start_url` are NEXT-specific. When Baden mode promotes to live, create
> **`manifest.baden.json`** (`start_url: ./browse.html?for=baden`) and update the
> browse.html IIFE to point at it — mirrors the existing `manifest.next.json` →
> `manifest.json` swap. Also add it to `sw.js` PRECACHE + bump CACHE_NAME.

---

## What's in it

- **List → Record**, one view at a time, single column. Large tap targets
  (≥64px), 22px serif (a one-tap **A+** raises to 26px), **light high-contrast**
  default with a one-tap **dark** toggle. Both choices are remembered.
- **Image stage**: *Fit* / *Bigger* / *Full size*. Pan by dragging (native
  scroll — no precision gesture). *Full size* loads the real 3840px asset.
  Pinch-zoom also works (the `maximum-scale` lock was removed).
- **Notes** — a full-width *Add a note* on every record opens two equal choices,
  **Speak a note** and **Type a note**:
  - *Type*: a big autofocused box; the keyboard's microphone key dictates too.
  - *Speak*: tap to start, tap to stop (never press-and-hold). Then Play /
    Re-record / Save. Audio is captured as an **uncompressed 24-bit mono WAV**
    (a preservation master — not Safari's lossy default).
- Saved notes appear under the record. Text notes are editable; audio notes are
  never overwritten (a correction is a new recording).
- **Export my notes** (in Help) shares everything — including the WAV files —
  via the iPad share sheet (AirDrop / Files / Mail). Text also has a Mail
  fallback to `archive@hunterhousefoundation.com`.

### Where notes go
1. **On the iPad immediately** (IndexedDB) — survives reloads.
2. **Sent to the server** (`POST /api/notes` → Cloudflare Worker → R2 bucket
   `hhf-baden-notes`, stored byte-exact). Audio = WAV + a JSON sidecar; text =
   JSON. **The server is the real custody**; the iPad copy is only a cache
   (Safari can evict it). Transcription (e.g. Whisper) happens **downstream on
   the server**, never in the app.
3. If a send fails it **queues and retries** on next open; a small "saved on this
   iPad, not yet sent" line with a **Send now** button shows while anything is
   pending.

---

## Editing the curated set

Edit **`curation/baden.json`** — an ordered list; the order is the walk:

```json
[
  { "id": "HH-CAA-0007", "address": "A line from you to Mowry about why it's here." },
  { "id": "HH-IHC-0003", "address": "" }
]
```

- `id` — the archive identifier exactly as catalogued.
- `address` — optional, 1–2 sentences, shown under the item. Omit or `""` for none.
- `//` and `/* */` comments are allowed (don't put comment markers *inside* an
  address). Unknown IDs are skipped; if none resolve the room shows a Retry error.

The 10 seeded entries are real items with **placeholder** address lines — replace
the words with real ones to Mowry.

---

## Before handover (Brandon)

### 1. Stand up the notes backend (one-time) — ✅ DONE & VERIFIED 2026-06-18
The Worker that receives notes is the existing `cloudflare/r2-browser/` Worker,
extended with `POST /api/notes`. It writes to a **new** R2 bucket in **your own**
Cloudflare account (native binding = write-capable; the archive bucket stays
read-only).

**This backend is now live.** Verified end-to-end 2026-06-18:
- bucket `hhf-baden-notes` exists (628a account);
- the Worker has `/api/notes` deployed (GET→405, valid POST→201);
- the `NOTES_TOKEN` shared secret is set on the Worker AND matches
  `BADEN.NOTES_TOKEN` in `next.html` (set 2026-06-12) — no token → 403, correct
  token → 201;
- a real POST landed at `baden-notes/HH-TEST-0000/…json` in R2 and was deleted.

So a note left from the iPad reaches the bucket. Notes land under
`baden-notes/<item-id>/…` (`.wav` + `.wav.json`, or `<timestamp>.json` for text).

For reference, the original one-time stand-up was:

```bash
cd cloudflare/r2-browser
npx wrangler r2 bucket create hhf-baden-notes   # one-time
npx wrangler deploy                              # ships /api/notes + the binding
npx wrangler secret put NOTES_TOKEN             # shared secret; match BADEN.NOTES_TOKEN
```

⚠ **Reading notes back has no listing path yet.** The notes bucket is in the
personal 628a account; the `hh-r2` rclone remote points at the *Foundation*
account, so it can't see it, and the Worker's `/list` reads the archive bucket
only. To check "are there new notes from Mowry," use the Cloudflare dashboard, or
stand up a read path (an `hh-baden:` rclone remote with 628a S3 keys, or a
researcher-gated read endpoint on the Worker). Not built yet.

### 2. Test the microphone ON THE ACTUAL iPad — do not skip
`getUserMedia` has a **history of failing inside home-screen standalone webapps
on iPadOS** (the site sets `apple-mobile-web-app-capable`). So:
1. Add the page to the home screen, open it, and **grant the microphone** when
   prompted.
2. Record a **test note** and confirm it plays back and saves.
3. **If the mic fails from the home-screen icon**, install it instead as a plain
   **Safari bookmark** (or we override the standalone meta for this page) — the
   mic is reliable in normal Safari. Typed notes work either way.

This must be confirmed on Mowry's device before handover; it cannot be verified
headless (and wasn't — see AUDIT.md §Phase 3).

---

## Known limits (first pass)
- **Desktop-only entry today** is *not* a limit here — Baden mode is built for the
  iPad and works at 768×1024 and 1024×768.
- Live microphone capture is unverified in CI (headless `getUserMedia` never
  settles); the WAV encoder itself is verified to emit valid PCM WAV.
- 90/270° display-rotation items (P144) are rotated via CSS transform; the seeded
  set is all upright, so this is untested in anger.
