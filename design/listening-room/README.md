# Listening Room

Clean implementation of the `Listening Room v2.dc.html` design, refactored out
of the `.dc.html` authoring format into plain HTML + CSS.

**Desktop:** `desktop/` holds the landscape companion page — same
architecture applied to a 1536×1024 artwork, documented in
`desktop/README.md` against this file.

Authored at **390×844** (mobile is the primary target). No build step, no
runtime dependency — open `index.html`. The one script is `scroll.js`,
dependency-free vanilla JS.

```
index.html                 markup + the layer map
styles.css                 tokens, layer stack, components, motion
scroll.js                  the camera — scroll-driven push into the shelf
assets/room2.png           the room illustration, retouched (853x1844)
assets/room2.original.png  the illustration as delivered — keep it
assets/room-plate.png      room2 prepared for motion — this is what renders
assets/vinyl.png           the record, cut out and made whole
assets/vinyl-rotating.png  the record's surface, symmetrized — this turns
assets/vinyl-light.png     the record's sheen and shading — this never does
assets/deck-over.png       what sits above the record and must not turn
assets/vine-window.png     the strand by the window posters — sways
assets/vine-wall.png       the cluster over Ella / Dilla — sways
assets/plant-left.png      the left foreground mass — sways
assets/plant-right.png     the right foreground plant — sways
assets/flame-loop.png      the candle flame, 10 drawn frames
assets/eq-loop.png         the stereo's level meter, 16 drawn frames
tools/retouch-room2.py     the text retouch, re-runnable
tools/vinyl/               the record separation + light split, re-runnable
tools/scenery/             foliage separation, flame + meter loops, re-runnable
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
| `vinyl` | The record's turning surface. Pivots on the spindle | **spinning — see below** |
| `vinyl-light` | The record's sheen and shading. Static | **yes** |
| `deck-over` | Tonearm, headshell, spindle, case edge, glare. Static | **yes** |
| `vine-window`, `vine-wall` | Hanging plants, pivot at their attach point | **swaying** |
| `plant-left`, `plant-right` | Foreground plants, pivot at their base | **swaying** |
| `candle-flame` | The flame, a 10-frame drawn loop | **burning** |
| `eq-meter` | The stereo's level meter, a 16-frame drawn loop | **dancing** |
| `poster-wall` | Poster wall | needs art + geometry |
| `story-line-1`, `story-line-2` | The scroll copy (placeholder lines) | **scroll-driven** |
| `shelf-dark`, `finale`, `finale-cta` | The shot's ending | **scroll-driven** |
| `scroll-cue` | The invitation to scroll | **yes** |

## The scroll shot

The page is one continuous camera move — a slow push from the full room
into the record shelf — with the scrollbar as the playhead. `scroll.js`
owns it entirely:

- The **track** (`.scroll-track`, 560dvh) is the page's only height; the
  stage inside it is sticky, so the scene never leaves the screen.
- The **camera** is one transform applied identically to the art and
  lighting layers (the world). Identity, story lines, finale, and cue are
  UI and stay in screen space; the vignette and grain are the lens and
  never move. The shot targets the shelf at scene point (178, 705) —
  spine rows plus the receiver's display — at 3.2× zoom.
- The **playhead is smoothed** (exponential chase, ~7/s), which is what
  gives the camera its mass. Scroll up and the shot reverses exactly.
- The idle loops (spin, sway, flame, EQ, flicker) stay on their own clocks
  and keep running through the move, so the end frame is still alive.
- Under `prefers-reduced-motion` the camera never moves; the copy still
  surfaces by opacity alone.

The story lines in the DOM are **placeholder copy** written against
SPEC v0.2's finite-canon idea; swap them freely.

Transform origins are set per element to the pivot each one should actually
rotate about — vines swing from the top, foreground plants from their base,
the record about its spindle.

## The record is separated

`room2.png` still holds the whole room, record included. `vinyl.png` is the
disc alone and sits on top of it; `deck-over.png` holds everything that must
stay put while the disc turns.

```
room2.png  ->  vinyl-rotating.png  ->  vinyl-light.png  ->  deck-over.png  ->  the HTML/UI layers
```

(`vinyl.png` itself no longer renders on the page — it is the input the
two layers above it are derived from; see the next section.)

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

## The light is separated from the surface

Rotating `vinyl.png` directly fails, even with exact geometry, and it fails
perceptually: the disc carries view-dependent paint — the sheen across its
surface, the glints along the rim, the visible thickness of its front edge.
Turn the disc and that light orbits it. Light belongs to the room, not to
the record, so the eye instantly reads the whole disc as a separate object
pasted on top of the scene. This was verified frame-by-frame before the
split was built.

`tools/vinyl/symmetrize.py` splits the disc one more time:

```
vinyl.png  ->  vinyl-rotating.png  ->  vinyl-light.png
```

- **`vinyl-rotating.png`** is the surface that turns: every pixel replaced
  by the median of its ring in record space, so the layer is rotationally
  symmetric and spins with no artifact at all. Its alpha fades out just
  inside the rim (r 0.94 → 0.985), so the painted rim, its glints, and the
  edge thickness stay in the plate and never move. Because a symmetric disc
  spins invisibly, it carries two deliberate asymmetric marks — a warm
  smudge on the label and a dust fleck out on the grooves — sized to read
  in motion, not in a still.
- **`vinyl-light.png`** is everything the surface lost: the signed residual
  between the real disc and its symmetric version, solved per pixel into
  the most transparent normal-composite layer that lands back on the
  original. The sheen and shading live here and hold still. The marks pass
  underneath it and dim where the light is strong, which is what a real
  reflection does to detail.

At rest the chain `plate → vinyl-rotating → vinyl-light → deck-over`
reproduces the old `plate → vinyl → deck-over` composite to ≤2 levels
everywhere outside the marks.

## The foliage is separated

`tools/scenery/separate.py` cuts four plants out of the plate: the vine
strand by the window posters, the leaf cluster over the Ella and Dilla
posters, and the two foreground masses left and right. Foliage is masked
by greenness — in this palette it is the only thing whose green channel
beats its red — with a value ceiling that keeps the teal poster type
(ELLA, NINA, PASTEL BLUES) out of the cut, hole-filling for warm-lit leaf
faces, and a small dilation that pulls the lit leaf rims in with their
leaves.

Sway rotates each element a fraction of a degree about the point where it
actually attaches — vines from above the frame edge, plants from their
pots — so the plate had to be rebuilt behind every silhouette edge: a
band deeper than the largest sway displacement, filled from the
surrounding background and softened. Deeper inside each silhouette the
baked copy stays, because it is never exposed. That rebuilt plate is
`room-plate.png`, which is what the page renders; `room2.png` is
untouched and remains the tool's input. At rest the cuts cover their own
fills and the composite equals `room2.png` exactly, to the pixel.

The two vines render behind the record layers; the two plants and the
flame render in front of `deck-over`, because that is their depth in the
painting.

## The flame is drawn, not warped

The candle flame is baked light, and warping painted light reads as
melting. `tools/scenery/separate.py` instead REDRAWS it: ten frames of a
teardrop — white heart, yellow body, orange skirt, colours sampled from
the painted flame itself — over a small patch from which the painted
flame was removed. Bend and stretch are driven by closed sinusoids, so
frame 10 hands back to frame 1 with no seam. Each frame is opaque and its
border pixels are the plate's own, so the sprite needs no seam care and
no plate edit. The page plays it with `steps(10)` at ~11fps, like film.

The stereo's level meter gets the same treatment in
`tools/scenery/equalizer.py`, which measures the painted display rather
than assuming it: the lit segments are found by colour, grouped into
columns, and the sloped shelf line they stand on is fitted from their
bases — the receiver leans about 28 degrees in this view and the bars
must keep standing on that line. Sixteen frames redraw every column as a
stack of ember-to-hot segments with a faint glow on the glass, each
bar's height riding its own closed sinusoid; frame 1 reproduces the
painting's levels. Played with `steps(16)` at ~9fps — meters snap, they
do not glide.

### The spin geometry, for whoever touches it

- **The rim is the axis, not the label.** The painted label sits about 3px
  off the centre of the ellipse the rim traces. Rotation pivots on the
  rim's centre or the silhouette walks off its baked copy — which means the
  label wobbles very slightly as it turns. The illustration, not the maths,
  is what is inconsistent here.
- **A 2D `rotate()` is wrong.** The disc is drawn in perspective. Spinning
  the ellipse in the image plane tumbles it like a flipped coin. The
  rotation is conjugated through the foreshortening — see the transform on
  `.art-plate--vinyl` in `styles.css`, which un-squashes the ellipse to the
  circle it really is, turns it, and puts the perspective back.
