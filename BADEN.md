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
The plan is to add it to Mowry's iPad **home screen**; because the mode persists,
the icon opens straight into the viewing room with zero input.

After promotion the live URL is `https://hunterhouse.org/browse.html?for=baden`.

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

### 1. Stand up the notes backend (one-time)
The Worker that receives notes is the existing `cloudflare/r2-browser/` Worker,
extended with `POST /api/notes`. It writes to a **new** R2 bucket in **your own**
Cloudflare account (native binding = write-capable; the archive bucket stays
read-only).

```bash
cd cloudflare/r2-browser
npx wrangler r2 bucket create hhf-baden-notes   # one-time
npx wrangler deploy                              # ships /api/notes + the binding
```
Until this is deployed, notes still save on the iPad and queue (they POST as soon
as the Worker is live — no data lost). Notes land in R2 under
`baden-notes/<item-id>/…` (`.wav` + `.wav.json`, or `<timestamp>.json` for text).

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
