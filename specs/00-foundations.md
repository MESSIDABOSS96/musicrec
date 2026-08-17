# 00 — Foundations (shared contracts)

> Every other spec builds on this file. Nothing here should be changed
> casually — a change in foundations must be checked against every other spec.
> Keep this file small and stable.
>
> Status: **stable draft** — reflects decisions from the 2026-08-16 interview.

## Vocabulary

| Term | Meaning |
|---|---|
| **Map** | The home screen: the user's artists as floating orbs in an organic constellation. The map is the score — there are no points/badges/streaks. |
| **Node** | An artist. The atomic unit of the map. Albums/songs live inside an artist's detail view, never as top-level nodes. |
| **Cluster** | A neighborhood of the map: artists grouped by vibe/sound/genre. |
| **Frontier** | A newly revealed artist the user hasn't engaged with yet. |
| **Anchor** | A liked/known artist the user expands from ("explore this direction"). |
| **Facet songs** | The small curated set of songs on an artist's detail view, chosen to show that artist's different sides — not their top hits. |
| **Reaction** | The user's post-listen verdict: Liked / Not for me / Already knew. |
| **Taste model** | The persistent per-user model all signals feed. The map is a view of it. |

## Node states (contract shared by design, expansion, and core-loop specs)

`Seeded → Frontier → (Explored | Known | Blurred)`

- **Seeded** — placed by onboarding.
- **Frontier** — revealed by an unlock, not yet engaged.
- **Explored** — listened + reacted Liked.
- **Known** — reacted "Already knew".
- **Blurred** — reacted "Not for me". Blurred nodes NEVER disappear —
  visited ground is still expansion.

## Taste signals (contract shared by onboarding, expansion, core-loop)

| Signal | Source |
|---|---|
| A/B pick | Onboarding |
| "Don't know either" | Onboarding |
| Liked / Not for me / Already knew | Reaction |
| "Explore this direction" (and from which anchor) | Map action |

The model remembers everything, forever, and carries an explicit
exploration bias: it uses comfort to push outward, never to feed sameness.

## Product principles (bind every spec)

1. Super simple — one core object (map), one core action (explore → listen → react).
2. The map is the score.
3. Honest signals over surveillance — honor-system, "already know it" always rewarded.
4. Intentional, not overwhelming — small curated sets everywhere.
5. Discovery-forward.

## Platform decisions

- Mobile-first web app; desktop fully supported (bigger canvas, same map).
- No in-app audio ever in v1 — pure link-out to the user's streaming service.
- No Spotify/streaming login or history import in v1.
- No social features in v1.

## Cross-spec dependency map

```
00-foundations ──> everything
05-data-layer ──> 02-onboarding (duel artist pool)
              ──> 03-expansion (similarity graph, clusters)
              ──> 04-core-loop (facet songs, metadata, link-out URLs)
01-design-system ──> renders states/objects defined in 00, 03, 04
```

## Open questions owned here

- Accounts: anonymous-first with local persistence, or accounts from day one?
  (The taste model + map must survive; losing them loses the product.)
- Product name.
