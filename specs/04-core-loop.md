# 04 — Core loop: artist detail, listening & reactions

> Status: **shape decided, details unspecced.** Everything between tapping a
> node and the map updating — plus the leftover product decisions that don't
> belong to onboarding or expansion.

## Decided

- Tapping any artist opens a small, intentional **detail view**: facet songs
  + reaction controls + (for liked/known artists) "explore this direction".
- **Facet songs**: a handful of songs chosen to show the artist's different
  sides — not top hits. The point is letting the user find *which side* of
  an artist they connect with. Intentional, not overwhelming.
- **Pure link-out** — every song deep-links to the user's streaming app;
  musicrec plays no audio.
- Reactions: **Liked / Not for me / Already knew** — honor-system,
  post-listen, and the only engagement currency.

## To spec

1. **Facet definition & count** — how many songs (lean: 3–5), what a "facet"
   is (era? sound? energy?), and how facets are curated (ties to
   05-data-layer: LLM-curated vs. data-derived).
2. **Detail view content** — beyond songs + reactions: blurb? why-this-artist
   ("because you liked X")? cluster context? Keep minimal — decide what earns
   a place.
3. **Link-out targets** — which services (Spotify / Apple Music / YouTube),
   whether the user sets a preferred one once, URL schemes/deep-link format.
4. **Reaction timing** — react anytime, or only after tapping out to listen?
   Can a reaction be changed later? (Lean: changeable — taste evolves.)
5. **Partial states** — "listened to one facet, want to come back": is there
   a save-for-later, or does frontier state itself serve as the to-listen
   list? (Lean: the latter — no extra lists.)
6. **Known-artist detail view** — what does tapping an already-Known artist
   show? (They're anchors, so at minimum: explore-this-direction.)
7. **Persistence & accounts** (owns foundation's open question) —
   anonymous-first localStorage vs. accounts day one; export/backup of the
   map; multi-device.
8. **Everything-else sweep** — settings surface (streaming preference),
   about/empty states, share-a-screenshot of map (view-only, not social).

## Contracts

- Consumes: facet songs + metadata + link-out URLs from **05-data-layer**.
- Produces: reactions consumed by **03-expansion** and the taste model;
  detail-view surface designed in **01-design-system**.
