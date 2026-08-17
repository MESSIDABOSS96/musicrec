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
assets/vinyl.png           the record, cut out and made whole
assets/deck-over.png       what sits above the record and must not turn
tools/retouch-room2.py     the text retouch, re-runnable
tools/vinyl/               the record separation, re-runnable
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

**Keep `room2.original.png`.** It is the delivered artwork, and the only
input the retouch and the record separation can be re-derived from.

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
- **Grouped the artwork.** All scenery — the plate, the record layers, and
  the empty slots for art not yet separated — sits in one art layer, with the
  UI above it.

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
| `vinyl` | The record. Pivots on the spindle | **yes — see below** |
| `deck-over` | Tonearm, headshell, spindle, case edge, glare. Static | **yes** |
| `poster-wall` | Poster wall | needs art + geometry |
| `hanging-vines` | Hanging plants, pivot at top | needs art + geometry |
| `foreground-plants` | Foreground plants, pivot at base | needs art + geometry |

Transform origins are set per element to the pivot each one should actually
rotate about — vines swing from the top, foreground plants from their base,
the record about its spindle.

## The record is separated

`room2.png` still holds the whole room, record included. `vinyl.png` is the
disc alone and sits on top of it; `deck-over.png` holds everything that must
stay put while the disc turns.

```
room2.png  ->  vinyl.png  ->  deck-over.png  ->  the HTML/UI layers
```

The plate keeps its painted record underneath on purpose. A rotation about
the record's own axis leaves the silhouette exactly where it is, so the disc
covers its own baked copy at every angle, and the soft rim blends into
identical colour instead of against bare deck. Nothing has to be cut out of
the plate, and a seam at the rim is not possible.

Three things had to be reconstructed to make the disc whole: the surface
under the tonearm and headshell, the surface under the case's rear edge —
which crosses the far rim and is easy to miss — and the label under the
spindle. The fill copies from the same radius at a different angle, which is
the one method that keeps grooves and label edges continuous on a record.

The glare is not painted into the disc. It is a separate light layer inside
`deck-over.png`, semi-transparent, so the record still shows through it and
will pass under it rather than carrying it around. Light does not orbit.

`tools/vinyl/` regenerates both assets from `assets/room2.png`; the fitted
ellipse is a constant in `split_vinyl.py` and `fit_ellipse.py` is what
produced it. Needs numpy and Pillow.

### Before animating, know these three things

- **The rim is the axis, not the label.** The painted label sits about 3px
  off the centre of the ellipse the rim traces. Rotation has to pivot on the
  rim's centre or the silhouette walks off its baked copy — which means the
  label will wobble very slightly as it turns. The illustration, not the
  maths, is what is inconsistent here.
- **A 2D `rotate()` is wrong.** The disc is drawn in perspective. Spinning
  the ellipse in the image plane tumbles it like a flipped coin. The
  rotation has to be conjugated through the foreshortening:

  ```css
  transform-origin: 221.59px 566.94px;   /* the spindle */
  transform: rotate(-3.25deg) scaleY(0.4016) rotate(var(--spin))
             scaleY(2.49) rotate(3.25deg);
  ```

  where 0.4016 is the measured B/A and −3.25° the ellipse's tilt.
- **The spin may barely read.** Grooves are concentric and the label is
  nearly featureless, so a geometrically perfect rotation is close to
  invisible. What normally sells a spinning record is the sweeping highlight,
  and that highlight has to stay still. Consider giving the label an
  asymmetric mark before judging the result.
