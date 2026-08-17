# 01 — Design system & visual identity

> Status: **direction chosen — Golden Hour.** Tokens/DESIGN.md not yet
> written; a first landing-page exploration exists at
> `design/explorations/golden-hour-landing.html`.
>
> Final deliverable: a `DESIGN.md` design system (tokens, type, color,
> motion, components) in Google's DESIGN.md format.

## Direction: Golden Hour (chosen 2026-08-16)

The palette and mood come from the user's reference images in
`design/inspiration/`: vinyl on a wood table in low sun, a sunset café
turntable, an amber phosphor car-stereo display ("TRACK 06"), lofi-anime
sunset street scenes. NOT the daytime-cream Close Friends look — the
*structure* of that reference survives (floating orbs, organic
constellation, no drawn edges), but the world is dusk:

- **Ground:** warm-dark ramp — deep plum-brown through burnt sienna to
  amber; silhouettes in warm near-black (never pure black), sky/sun glow as
  the light source.
- **Accent:** phosphor amber (≈#FFB000) — the car-stereo display. It is the
  one glowing interaction color.
- **Type pairing (the identity):** warm old-style serif for display/voice
  (record-sleeve, liner-note register) + monospace uppercase with wide
  tracking for labels/UI chrome (dashboard-phosphor register). Working
  stacks: Iowan Old Style/Palatino/Georgia + SF Mono/Menlo; real webfont
  choices TBD in the tokens pass.
- **Texture/motion:** film grain, glow, slow breathing/drift; flicker used
  sparingly (string-light bulbs). Sunset→night as a narrative axis: golden
  hour for arrival/landing, deep night for the constellation map.
- **First-second feeling (decided):** "this is mine" + curiosity/pull —
  intimacy first, with the frontier visibly calling.
- **Color modes:** single-world, dark-warm by nature. No light/dark
  toggle — the app lives at dusk. (Revisit only if legibility testing
  demands it.)

## Existing artifacts

- **`design/analysis/reference-teardown.md` — read this before writing any
  tokens.** Measured reverse-engineering of the two lofi references: value
  structure, depth-plane luminance shelves, the hue-rotation-with-value rule,
  light-source bloom ratios, and the warm/cool ramps extracted as hex tables.
  The tokens pass is now a translation of this document, not a taste
  exercise. Its Part 2 covers bruno-simon.com — how an exploratory space
  teaches itself, and the affordance trap waiting for a free-exploration map.
- `design/analysis/scripts/` — the measurement scripts, re-runnable on any
  new reference image (needs `pillow` + `numpy`).
- `design/inspiration/` — 9 reference images (named descriptively).
- `design/explorations/golden-hour-landing.html` — first landing-page
  attempt. **Superseded.** It predates the teardown and violates most of its
  findings: no aperture, no dark near-plane, continuous gradients instead of
  discrete value shelves, a soft radial sun instead of a flat disc with
  bloom, uniform glow on every light, and no cool counterpoint. Kept only as
  a record of what not to do. The one salvageable part is the copy voice:
  "Your taste is a place." and the TRACK 01 / TRACK 02 tracklist labels.

## What the design system must cover (inventory from other specs)

Surfaces:
- [ ] The map (home) — including desktop's wider canvas
- [ ] Artist detail view (facet songs, reactions, explore-this-direction)
- [ ] Onboarding duel screens + the map-reveal moment (the emotional hook)
- [ ] Empty/loading/limit states (daily cap reached, frontier decay if adopted)

States & moments needing distinct visual treatment (contract: 00-foundations):
- [ ] Node states: Seeded / Frontier / Explored / Known / Blurred
- [ ] Cluster identity — how neighborhoods read as neighborhoods
- [ ] Unlock moment — new frontier artists appearing (paced, scarce, an event)
- [ ] Blur-out moment — a dislike settling into visited ground (must not feel
      like punishment)

## To figure out in the design session

- The full visual identity: palette, type, texture, motion language
- How "known territory" reads vs "explored" vs "frontier" at a glance
- Whether clusters get labels or stay purely spatial (shared with 03)
- Desktop layout philosophy (same map, wider — how?)
- Name + wordmark (shared with 00)

## Session plan

Run the design interview (the `design-md-planner` skill fits this exactly:
it interviews for taste, commits to a referenced aesthetic, and produces a
lint-clean DESIGN.md). Bring the Close Friends screenshots.
