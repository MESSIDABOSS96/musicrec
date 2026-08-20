# Listening Room — Desktop

Landscape companion to the mobile page one directory up. Same
architecture throughout — read `../README.md` first; this file only
records what differs.

Authored at **1536×1024** (scene px == artwork px, no scale factor
between CSS and image space). The scene scales as one unit to fit the
viewport via `--scene-scale`, so every measured constant survives any
window size. No JavaScript, no build step.

```
index.html                 markup + the layer map
styles.css                 tokens, layer stack, components, motion
scroll.js                  the camera — scroll-driven push into the shelf
assets/roomd.original.png  the artwork as delivered — keep it
assets/roomd.png           retouched: the baked identity block painted out
assets/roomd-plate.png     prepared for motion — this is what renders
assets/vinyl-rotating.png  the record's surface, symmetrized — turns
assets/vinyl-light.png     the record's sheen and shading — never does
assets/deck-over.png       tonearm, headshell, spindle — static
assets/vine-*.png          hanging foliage (left, center, right, far-right)
assets/shelf-fern.png      the drape at the shelf's end
assets/plant-*.png         rooted foliage (left, mid, right, cabinet pot)
assets/flame-main.png      the jar candle by the turntable, 10 frames
assets/flame-shelf.png     the jar candle on the shelf, 10 frames
assets/eq-loop.png         the receiver's level meter, 16 frames
tools/retouch.py           the identity-block retouch, re-runnable
tools/fit_ellipse.py       edge-optimised rim fit (moment fit fails here)
tools/record.py            split + symmetrize in one pass
tools/scenery.py           foliage separation + both flame loops
tools/equalizer.py         the meter loop
```

## What differs from mobile

- **The disc is more foreshortened** — squash 0.282 vs 0.402 — and its
  rim ellipse was fitted by edge optimisation (`fit_ellipse.py`) because
  everything around this disc is nearly as dark as the disc, which sinks
  a moment fit. The fit targets the TOP surface rim; the visible
  front-edge thickness below it belongs to the plate and never moves.
- **`record.py` merges split + symmetrize.** The mobile pipeline's
  intermediate whole-disc `vinyl.png` isn't shipped: the rotating layer
  is ring-symmetric by construction, so the reconstruction under the
  occluders only has to feed the ring statistics and the light solve.
- **The foliage mask is a union.** This palette is darker and warmer:
  leaves sit near RGB (15,17,9) and lamp-lit leaf faces go fully warm,
  so green-beats-red alone misses half of it. `scenery.py` adds a
  yellow-green hue window gated by a relaxed score, plus per-element
  EXCLUDE boxes — the A Tribe Called Quest poster's green artwork sits
  beside the centre vine's tail, the turntable lid beside the right
  vine, the speaker cone under the right plant.
- **Nine sway elements, two flames.** Each flame is the same closed-loop
  redraw as mobile, parameterised per candle (the shelf flame is
  smaller and slower). The meter has 14 bars on a 15.6° baseline.
- **Desktop affordances**: a real CTA hover state, and the whole-scene
  scale — there is no fixed-viewport assumption anywhere.
- **The scroll shot** (see "The scroll shot" in `../README.md`) targets
  the cabinet at scene point (990, 850) at 3.3× — the spine bays plus
  the receiver, whose meter keeps dancing in the end frame. This engine
  also **clamps the camera to the artwork's bounds** so no leg of the
  move shows past the painting's edge (the mobile engine gained the same
  clamp). `body { overflow: hidden }` moved to the sticky stage, since
  the page must now scroll.

At rest, the full stack reproduces `roomd.png` exactly except the
record's two deliberate marks and the three redrawn patches (two
flames, the meter), same contract as mobile.

Serve from this directory (or the parent, under `/desktop/`):

    python3 -m http.server 8731
