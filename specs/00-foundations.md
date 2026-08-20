# 00 — Foundations (shared contracts)

> Every other spec builds on this file. Nothing here should be changed
> casually — a change in foundations must be checked against every other spec.
> Keep this file small and stable.
>
> Status: **stable draft** — rewritten 2026-08-19 for the v0.2 rescope
> (album-canon journey). Supersedes the v0.1 artist-map vocabulary.

## Vocabulary

| Term | Meaning |
|---|---|
| **Museum** | The user's album canon: a shared core (~1,000 albums) plus personal wings from an extended pool. Fixed size once assembled — completable. |
| **Curator** | The sequencing engine. Decides which album comes next and why. Personalization = sequencing over a finite set, never open-ended recommendation. |
| **Journey** | The user's personal path through their museum: rooms → chapters → completion. The journey is the score. |
| **Room** | One album, handed to the user by the curator, with narration. Exactly 0 or 1 albums are "in hand" at any time. |
| **Chapter** | A themed leg of ~5–8 rooms with a curator-given name. The journey's mile-marker unit. |
| **Bridge album** | An album chosen because it genuinely connects two genres/wings — the mechanism of expansion. Stretches always arrive via bridges, never jumps. |
| **Narration** | The curator's 1–2 sentence "why this, why now" attached to every handoff. |
| **Wing** | A genre/scene region of the museum. |
| **Reaction** | The user's post-listen verdict: Liked / Not for me / Already knew. |
| **Pass** | "Not today — show me a different door." Not a reaction, records no taste signal; the album returns later. |
| **Coverage** | Albums with any reaction ÷ museum size. The definitive progress number. |
| **The Board** | The user's top-albums collage (topster) assembling from Liked albums. The trophy/identity artifact. |

## Album states (contract shared by design, journey, and core-loop specs)

`Unvisited → In hand → (Liked | Not for me | Already knew)`, with
`In hand → Passed → (returns to the route later)`

- **Unvisited** — in the museum, not yet reached.
- **In hand** — the current room's album.
- **Liked** — heard + loved. Feeds the Board. Counts as coverage.
- **Not for me** — heard + rejected. Visited ground: stays visible in the
  journey history, never offered as a listen again, counts as coverage.
- **Already knew** — knew it pre-journey. Instant skip credit, counts as
  coverage.
- **Passed** — deferred without signal. Returns later via a different path.

## Taste signals (contract shared by onboarding, journey, core-loop)

| Signal | Source | Teaches |
|---|---|---|
| A/B pick | Onboarding duel | Genre affinity, coarse → fine |
| "Don't know either" | Onboarding duel | Edge of album familiarity |
| Liked | Reaction | Continue this thread; open the next door |
| Not for me | Reaction | Back off this wing; re-approach later via a different bridge |
| Already knew | Reaction | Knowledge edge — skip forward past it |
| Pass | Room action | **No taste signal.** Scheduling only. |

The curator remembers everything for the life of the user and carries an
explicit exploration bias: comfort is the means, expansion is the goal.

## Product principles (bind every spec)

1. Super simple — one core object (the journey), one core action
   (receive → listen → react → advance).
2. The journey is the score — coverage, chapters, the Board. No
   points/XP/badges/streaks.
3. Honest signals over surveillance — honor-system listening; "Already
   knew" always rewarded, never punished.
4. One album in hand — no feeds, no grids, no backlog.
5. Bridges, never jumps — every stretch is one step from something the
   user just liked.
6. A definitive end — the museum is finite and completion is visible.

## Platform decisions

- Mobile-first web app; desktop fully supported.
- No in-app audio ever in v1 — pure link-out to the user's streaming service.
- No Spotify/streaming login or history import in v1.
- No social features in v1 (exporting the Board as an image is not social).

## Cross-spec dependency map

```
00-foundations ──> everything
05-canon ──> 02-onboarding (duel pool: covers + fame tiers)
         ──> 03-journey (museum assembly pool, connection graph, narration)
         ──> 04-core-loop (album metadata, blurbs, link-out URLs)
02-onboarding ──> 03-journey (taste position + familiarity → museum + Chapter 1)
03-journey ──> 04-core-loop (the album in hand + its narration)
04-core-loop ──> 03-journey (reactions/passes steer the route)
01-design-system ──> renders states/objects defined in 00, 03, 04
```

## Open questions owned here

- Accounts: anonymous-first with local persistence, or accounts from day
  one? (The journey state must survive; losing it loses the product.)
- Product name.
