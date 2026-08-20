# 04 — Core loop: the room, listening, reactions & the board

> Status: **shape decided (v0.2 rescope, 2026-08-19), details unspecced.**
> Everything between the curator handing over an album and the journey
> advancing — plus persistence and the leftover product decisions that
> don't belong to onboarding or the journey. Replaces v0.1's artist-detail
> / facet-songs version of this spec (facet songs are retired: the album
> itself is the unit of listening).

## Decided

- **The room view** is the app's center: the album in hand — cover, artist,
  year, the curator's narration ("why this, why now"), a short
  what-this-is blurb, and the actions.
- **Pure link-out** — one tap opens the album in the user's streaming
  app; musicrec plays no audio.
- **Reactions: Liked / Not for me / Already knew** — honor-system,
  post-listen, the only gate to the next room.
- **Pass** — "not today, show me a different door" — available on every
  room, visually secondary to the reactions, records no taste signal.
- **The Board** — the user's topster assembles from Liked albums and is
  exportable as an image (view-only artifact, not a social feature).
- Coverage ("127 of 1,043") and chapter progress are always visible at a
  glance from the journey view.

## To spec

1. **Room view content** — exactly what earns a place beyond
   cover/narration/blurb/actions: tracklist? runtime? "part of Chapter:
   …" context? Keep minimal — one screen, no scroll (lean).
2. **Link-out targets** — which services (Spotify / Apple Music / YouTube
   Music), whether the user sets a preferred one once, album-level URL
   schemes/deep-link format, fallback when an album is missing from a
   service.
3. **Reaction timing & mutability** — react anytime or only after tapping
   out? (lean: anytime — honor system either way). Can a reaction be
   changed later? (lean: changeable — taste evolves; state transitions
   must stay consistent with 00-foundations).
4. **Partially heard** — "listened to half, want to sit with it": is
   in-hand state alone the to-listen list (lean: yes — no extra lists), or
   is there any explicit save-for-later beyond Pass?
5. **The Board mechanics** — auto-assembled (chronological? ranked?) vs.
   user-arranged; grid sizes (3×3 / 5×5 / 10×10); export format; when a
   user un-likes an album.
6. **Journey history view** — how visited rooms (including Not-for-me as
   visited ground) are browsable; per-chapter recap.
7. **Persistence & accounts** (owns foundation's open question) —
   anonymous-first localStorage vs. accounts day one; export/backup of
   journey state; multi-device.
8. **Everything-else sweep** — settings (streaming preference), about
   page, empty/loading states, the journey-complete state.

## Contracts

- Consumes: the album in hand + narration + chapter context from
  **03-journey**; album metadata, blurbs, and link-out URLs from
  **05-canon**.
- Produces: reactions and passes consumed by **03-journey**; album state
  transitions per **00-foundations**; the room view, journey view, and
  Board designed in **01-design-system**.
