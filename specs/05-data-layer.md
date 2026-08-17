# 05 — Data layer

> Status: **unspecced, highest risk.** This spec can validate or kill the
> whole approach, so it should include a hands-on prototype, not just
> decisions on paper. Every other functional spec consumes it.

## What the product needs (with no user streaming login)

1. **Artist similarity graph** — who is adjacent to whom + cluster
   structure. Powers map layout (01/03), onboarding duels (02), and frontier
   selection (03).
2. **Facet songs per artist** — the curated handful showing an artist's
   sides (04).
3. **Artist metadata** — names, images, streaming deep-links (04), plus
   enough popularity signal to build the onboarding duel pool (02).

## Candidate sources to evaluate

| Source | Likely good for | Concerns |
|---|---|---|
| Last.fm API | similar-artists, tags, popularity | rate limits, similarity quality |
| MusicBrainz / ListenBrainz | open canonical metadata, relationships | similarity coverage, effort |
| Deezer API | images, previews, metadata, no auth | catalog/deep-link mapping |
| LLM-curated | facet selection, human-readable adjacency, cluster naming | hallucination — must be grounded against real catalog data |
| Hybrid (lean) | open data for the graph + LLM for curation | pipeline complexity |

## To spec (via prototype)

1. **Source choice** — run a real test: pick 5 seed artists across genres,
   pull similar-artists from each candidate source, judge quality by hand.
2. **Graph shape** — precomputed dataset vs. live API calls vs.
   generate-on-demand-and-cache; how large a universe v1 needs.
3. **Facet-song pipeline** — can an LLM grounded in real track lists reliably
   pick 3–5 facet songs? Prototype on 10 artists you know well.
4. **Embedding/position model** — how artists get coordinates (for taste
   vectors and map layout): tag-based embedding? LLM embedding? graph layout?
5. **Deep-link resolution** — mapping an artist/track to Spotify / Apple
   Music / YouTube URLs reliably.
6. **Freshness & cost** — how often data updates; API costs at small scale;
   caching strategy.

## Contracts

- Produces (consumed by 02, 03, 04): duel pool, similarity graph + clusters,
  artist positions, facet songs, metadata + link-outs.
- This spec should end with a **data contract** section: the exact shape of
  `Artist`, `SimilarityEdge`, `Cluster`, `FacetSong` that the implementation
  agent builds against.
