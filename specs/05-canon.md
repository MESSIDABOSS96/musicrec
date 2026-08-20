# 05 — The Canon (dataset, connection graph & narration pipeline)

> Status: **not started — first thing to prototype.** Replaces v0.1's
> `05-data-layer.md`. The rescope transformed this workstream: v0.1 needed
> a live artist-similarity engine (flagged "can kill the concept"); v0.2
> needs a **one-time, offline curation job** over a few thousand albums.
> The risk is now editorial quality, not feasibility.

## What the product needs (all static, built once, shipped as data)

1. **Core canon** (~1,000 albums, exact size TBD) — the shared spine of
   every museum. Assembled from established canon sources so membership is
   defensible, with genre-specific lists mixed in so non-rock canons
   (hip-hop, jazz, electronic, country, global) are fairly represented.
2. **Extended pool** (~3,000–5,000 albums) — where personal wings come
   from: deeper cuts per wing + approachable entry points per wing.
3. **Per-album record** — title, artist, year, wing/genre tags, position
   in the shared space, fame tier (for onboarding duels), cover art,
   streaming links per service, a 2–3 sentence what-this-is blurb.
4. **Connection graph** — edges between albums (influence, sampling,
   lineage, scene, same-artist) with a human-readable **"why this next"
   narration line per directed edge**. This powers bridges and the
   curator's voice. Static, hand-checkable, over a few thousand nodes.

## Candidate sources

| Source | Likely good for | Concerns |
|---|---|---|
| Acclaimed Music | aggregated critic canon, ranked ~3,000 | scraping/licensing; rock-critic skew |
| RYM / AOTY charts | user-consensus canon, genre charts | no API; ToS on scraping |
| 1001 Albums book / RS500 / genre lists | membership cross-check, blurb grounding | static, editorial skew |
| MusicBrainz | canonical album/artist metadata, IDs | no canon signal itself |
| Deezer / iTunes / Spotify APIs | cover art, links, popularity signal | catalog mapping, ToS |
| WhoSampled / Wikipedia | sampling + influence edges | coverage, scraping |
| LLM curation | wing tagging, fame tiers, blurbs, edges, narration lines | hallucination — every claim must be grounded against the above and spot-checked |

Lean: **list data for membership + MusicBrainz for identity + streaming
APIs for art/links + LLM for everything editorial (tags, tiers, blurbs,
edges, narration), grounded and hand-audited.**

## To spec (via prototype — do this first)

1. **Canon assembly recipe** — which lists, how they're weighted/merged,
   inclusion threshold, target sizes, genre-balance corrections. Output: a
   reproducible script + the actual v1 album list.
2. **The shared space** — how albums get wing assignments and positions
   (tag-based embedding? LLM-assigned wings + within-wing ordering?).
   Onboarding (02) and museum assembly (03) both consume this.
3. **Fame tiers** — a defensible popularity signal per album (streaming
   popularity + list ubiquity), bucketed into ≥ 3 tiers; every wing must
   have tier-1 representatives (02's hard requirement).
4. **Connection-graph pipeline** — prototype on one wing pair (e.g.
   hip-hop ↔ soul/funk/jazz): can an LLM grounded in sampling/influence
   data produce edges + narration lines that a knowledgeable human
   endorses? Target edge density: every album reachable, every wing
   entered via ≥ 2 distinct bridges.
5. **Blurbs & narration voice** — the curator's register (warm docent,
   not encyclopedia); length limits; generation + human-spot-check
   workflow.
6. **Link resolution** — album-level deep links per service; coverage
   check (which canon albums are missing from which service); fallback
   rules.
7. **Freshness** — the canon is deliberately slow-moving; decide the
   update cadence (yearly?) and whether v1 ships fully frozen.

## Contracts

- Produces (consumed by 02, 03, 04): duel pool (covers + fame tiers +
  wings), core canon + extended pool with positions, connection graph +
  per-edge narration, per-album metadata/blurbs/links.
- This spec must end with a **data contract** section: the exact shape of
  `Album`, `Wing`, `ConnectionEdge` (with narration), and `FameTier` that
  the implementation agent builds against.
