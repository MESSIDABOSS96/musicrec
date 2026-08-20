# 03 — The Journey (curator, sequencing & pacing)

> Status: **shape decided (v0.2 rescope, 2026-08-19), details unspecced.**
> The heart of the product — how the curator turns a fixed canon into a
> personal, definitive journey. Replaces v0.1's `03-expansion.md`
> (explore-this-direction / unlock economy), which is retired.

## Decided

- **The museum is (mostly) shared; the tour is personal.** Personalization
  is sequencing + pacing over a finite set, plus bounded variance in museum
  membership. There is no live recommendation engine; the curator routes
  over the static connection graph from 05-canon.
- **Museum assembly** happens once, at the end of onboarding: the shared
  core canon (~1,000) + personal wings from the extended pool — deeper
  cuts in the user's home wings, curated entry points (not the full deep
  canon) in unfamiliar wings. Museum size is then fixed and shown to the
  user; completion is real.
- **One album in hand.** The curator hands over exactly one album with
  narration ("why this, why now"). Reacting to it is the only gate to the
  next room. No calendar, no daily cap.
- **Chapters** of ~5–8 rooms, themed and named by the curator, are the
  journey's structure and mile-markers.
- **Route shape:** start in the home wing with unheard canon pillars
  (early wins build trust in the curator) → expand via **bridge albums**
  only (influence/sampling/lineage/scene edges from the connection
  graph) — never jumps.
- **Reactions steer:** Liked → continue the thread, open the next door.
  Not for me → back off the wing, re-approach later via a different
  bridge. Already knew → skip-forward credit.
- **Pass ("not today — show me a different door")** is a first-class
  scheduling action, records no taste signal, and the passed album returns
  later on a different path.
- Visual structure (recorded for 01): room-to-room / level-to-level
  progression à la Super Mario world maps — a drawn path, completed rooms
  behind you, the current room lit, the road ahead visible but closed.

## To spec

1. **Museum assembly recipe** — core:personal ratio, per-wing depth as a
   function of affinity, entry-point counts for unfamiliar wings, total
   size bounds; whether wings can grow mid-journey (lean: no — fixed size
   is the point) or only at defined milestones.
2. **Chapter construction** — how themes are chosen and ordered; chapter
   length variance; what the chapter-complete moment is; how far ahead the
   route is planned (whole journey vs. rolling next-chapter — lean:
   rolling, so reactions can reroute cheaply).
3. **Sequencing policy** — the actual algorithm: scoring the next room
   given affinity, recent reactions, bridge availability, and variety
   (never three similar albums in a row?); the stretch cadence (how often
   a chapter reaches toward a new wing).
4. **Pass mechanics** — how many alternative doors per sitting; when a
   passed album resurfaces; anti-abuse (pass-spamming as taste signal
   laundering — does a 5th consecutive pass mean something?).
5. **"Not for me" recovery** — how long the curator waits before
   re-approaching a rejected wing, and via which alternate bridge; when it
   concludes a wing is genuinely closed (and whether the museum then
   shrinks or the rooms just sit unvisited).
6. **Binge behavior** — completionists reacting without listening are
   honor-system-tolerated (per principles), but decide whether any soft
   friction exists (lean: none — the journey being finite already caps the
   damage).
7. **Journey completion** — what 100% coverage looks like; whether an
   "extended museum" or new-releases mode follows (post-v1, but the ending
   must not be a dead wall).
8. **Anti-degenerate cases** — the user who dislikes everything early; the
   omnivore whose chapters ping-pong; unfamiliar-everything users (see
   02 §6 front-hall chapter).

## Contracts

- Consumes: taste position + familiarity set + recognition level from
  **02-onboarding**; canon pools, connection graph, and per-edge narration
  lines from **05-canon**; reactions and passes from **04-core-loop**.
- Produces: the museum (fixed membership + coverage accounting), the
  route (current chapter, current room, album-in-hand + narration handed
  to **04-core-loop**), album state transitions per **00-foundations**;
  chapter/journey structure rendered by **01-design-system**.
