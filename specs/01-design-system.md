# 01 — Design system & visual identity

> Status: **direction chosen — Golden Hour.** Tokens/DESIGN.md not yet
> written; a first landing-page exploration exists at
> `design/explorations/golden-hour-landing.html`.
>
> **v0.2 rescope note (2026-08-19):** the aesthetic direction and all
> teardown findings survive the rescope untouched. What changed is the
> *structural* metaphor — the constellation map is retired; the journey now
> reads as **room-to-room / level-to-level progression à la Super Mario
> world maps**: a drawn path through named regions (chapters/wings),
> completed rooms behind you, the current room lit, the road ahead visible
> but not yet open. The surface inventory below is updated accordingly.
>
> Final deliverable: a `DESIGN.md` design system (tokens, type, color,
> motion, components) in Google's DESIGN.md format.

## Direction: Golden Hour (chosen 2026-08-16)

The palette and mood come from the user's reference images in
`design/inspiration/`: vinyl on a wood table in low sun, a sunset café
turntable, an amber phosphor car-stereo display ("TRACK 06"), lofi-anime
sunset street scenes. The world is dusk:

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
  hour for arrival/landing, deep night for the journey map.
- **First-second feeling (decided):** "this is mine" + curiosity/pull —
  intimacy first, with the road ahead visibly calling.
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

## What the design system must cover (inventory from other specs, v0.2)

Surfaces:
- [ ] The journey view (home) — the Mario-style path: chapters as regions,
      rooms as stops, current room lit; desktop's wider canvas
- [ ] The room view — album in hand: cover, curator narration, blurb,
      link-out, reactions, the secondary "different door" pass
- [ ] Onboarding duel screens + the ending transition (curator introduces
      itself → Chapter 1 named → first album handed over — the emotional hook)
- [ ] The Board (topster) + its image export
- [ ] Journey history / chapter recap
- [ ] Empty/loading states, journey-complete state

States & moments needing distinct visual treatment (contract: 00-foundations):
- [ ] Album states: Unvisited / In hand / Liked / Not for me / Already knew / Passed
- [ ] Chapter identity — how a themed leg reads as a region of the world
- [ ] The handoff moment — the curator giving you the next album (paced, an event)
- [ ] Chapter-complete moment
- [ ] "Not for me" settling into visited ground (must not feel like punishment)
- [ ] Coverage — how "127 of 1,043" is always felt but never gamey

## To figure out in the design session

- The full visual identity: palette, type, texture, motion language
- The journey-map grammar: how far ahead is visible, how closed rooms look,
  how wings/regions read at a glance
- The curator's visual presence/voice (a character? a typographic voice only?)
- Desktop layout philosophy (same journey, wider — how?)
- Name + wordmark (shared with 00)

## Session plan

Run the design interview (the `design-md-planner` skill fits this exactly:
it interviews for taste, commits to a referenced aesthetic, and produces a
lint-clean DESIGN.md). Bring the lofi references and a couple of Super Mario
world-map screenshots for the journey structure.
