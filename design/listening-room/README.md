# Listening Room

Clean implementation of the `Listening Room v2.dc.html` design, refactored out
of the `.dc.html` authoring format into plain HTML + CSS.

Authored at **390×844** (mobile is the primary target). No JavaScript, no
build step, no runtime dependency — open `index.html`.

```
index.html                 markup + the layer map
styles.css                 tokens, layer stack, components
assets/room2.png           the room illustration, retouched (853x1844)
assets/room2.original.png  the illustration as delivered — keep it
tools/retouch-room2.py     the retouch, re-runnable
```

---

## The plate was retouched

As delivered, `room2.png` had placeholder product UI **painted into the
raster**: "WELCOME TO", a MUSICREC wordmark, a tagline, a SPIN THE RECORD
pill, and a SCROLL TO EXPLORE line with its chevron — all on the wall behind
the identity block — plus a small `musicrec` wordmark on the turntable lid.

Two `.retouch` gradients used to sit in the art layer darkening those regions
so the live DOM text could be drawn over them. That is gone. The text is now
painted out of the plate itself and the wall behind it rebuilt, so the
artwork carries no product UI and needs no overlays.

`tools/retouch-room2.py` is the exact pass, with the geometry and the reasons
for each box in comments. It reads `room2.original.png`, so it can be re-run
or adjusted; it needs numpy and Pillow, which the page itself does not.

**Keep `room2.original.png`.** It is the only local copy of the delivered
artwork, and this directory is not under version control.

The copy in the DOM is left as `[PRODUCT NAME]` / `[SHORT TAGLINE]` /
`[PRIMARY ACTION]`, matching the design source. Product name is still an
open question in `specs/00-foundations.md`; the words that were baked into
the artwork were the illustrator's placeholder, not a decision.

---

## What changed, and what deliberately didn't

Nothing about the design changed. Typography, composition, colour, spacing,
and the environment are carried over value-for-value from the source. The
work was structural:

- **Dropped the `.dc.html` wrapper.** `<x-dc>`, `<helmet>`, and the
  `data-dc-script` props block only exist for the Design Components preview
  runtime (`support.js`, a generated React harness). Its only visual job is
  hoisting `<helmet>` into `<head>`, so those font links and base styles are
  written into `<head>` directly here and nothing is lost by dropping it.
  The output is plain standalone HTML.
- **Inline styles → a stylesheet.** Every literal moved into a named rule or
  a token. Colours, materials, and the z-index scale are declared once at the
  top of `styles.css`.
- **Named the layers.** The stack is explicit and documented in both files,
  with numbering gaps so layers can be inserted later without renumbering.
- **The CTA is a real `<button>`.** It was a `<div>`. It renders identically
  — the reset is in `.cta` — but it is now focusable, keyboard-operable, and
  has a visible focus ring.
- **Grouped the artwork.** The room plate and the empty turntable placeholder
  sit together in the art layer, so all scenery is in one layer and the UI
  sits above it. Since the placeholder is empty and does not overlap the
  identity block, the rendered result is unchanged.

Two additions that do not alter a screenshot: `cursor: pointer` on the CTA,
and centring the fixed-size scene on viewports larger than the artboard (a
no-op at 390×844).

---

## The structure for the motion layer

Everything intended to animate carries a **`data-actor`** attribute. Address
the motion layer against those, not against class names, so styling and
animation stay independent:

| `data-actor` | What | Ready? |
|---|---|---|
| `identity`, `eyebrow`, `product-name`, `tagline`, `cta` | Title block and its parts | **yes** |
| `glow-lamp-left`, `glow-lamp-right`, `glow-floor` | The three lamp glows | **yes** |
| `atmosphere` | Vignette | **yes** |
| `grain` | Film grain | **yes** |
| `room` | Base art plate | **yes** |
| `turntable` | Turntable group — geometry known (122, 500, 210×168) | needs art |
| `vinyl` | Platter, pivots at its own centre | needs art |
| `tonearm` | Tonearm, pivots at its mount | needs art |
| `poster-wall` | Poster wall | needs art + geometry |
| `hanging-vines` | Hanging plants, pivot at top | needs art + geometry |
| `foreground-plants` | Foreground plants, pivot at base | needs art + geometry |

Transform origins are already set per element to the pivot each one should
actually rotate about — vines swing from the top, foreground plants from
their base, the record spins about its centre.

### Artwork slicing — the real blocker

The vinyl, plants, vines, and posters are **painted into `room2.png` as a
single flat image.** No amount of DOM structure makes regions of one raster
independently animatable; they have to exist as separate images.

So the honest state is: the slots are built, positioned, and documented, but
five of them are inert until the artwork is exported in layers. What's needed:

1. `poster-wall.png`
2. `hanging-vines.png`
3. `turntable.png` (the deck body, minus platter and tonearm)
4. `vinyl.png` (the record — a square cut-out, so rotation stays centred)
5. `tonearm.png`
6. `foreground-plants.png`
7. `room-plate.png` — the room with all six of the above **removed**

Each as a transparent PNG on the same 390×844 canvas, so it drops in without
repositioning. Then, per slot in `styles.css`, set `--x/--y/--w/--h` and
`--art`, switch `display` back on, and point `.art-base` at `room-plate.png`.
Keeping the current full plate *and* adding slices renders those elements
twice — that is the one trap here.

If layered export isn't possible, the fallback is masking regions out of the
single plate with `clip-path`, which works for small motions but tears as
soon as an element moves far enough to expose the hole behind it.
