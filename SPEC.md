# musicrec — Initial Product Spec

> Working title. A super simple, lightweight music discovery app that gamifies
> expanding your taste. No Spotify login, no streaming integration — the app is
> a living map of your taste that grows as you explore.
>
> Status: **concept spec v0.1** — captures the vision and decided mechanics.
> No visual design, no implementation yet. Open questions are marked ❓ inline
> and collected at the end.

---

## 1. Thesis

Streaming apps have made discovery passive and stale: the algorithm feeds you
more of what you already like, and taste quietly calcifies. musicrec inverts
this. It is not a player — it's a **map of your musical identity** that only
grows when you actually go out and listen. Success after 3 months of use looks
like:

- **Deeper** — the user has found the niche corners, influences, and adjacent
  artists inside the genres they already love.
- **Wider** — they now listen to genres/scenes they'd never have touched.
- **Consistent** — discovery became a habit and a ritual, not an accident.

## 2. Principles

1. **Super simple.** One core object (the map), one core action (explore →
   listen → react). Every feature must justify itself against this.
2. **The map is the score.** No points, badges, or leaderboards in v1. The
   growing constellation *is* the progress, the reward, and the identity
   artifact.
3. **Honest signals over surveillance.** No listening-history import. The user
   tells us what they know, what they liked, what they didn't — and telling us
   is always rewarded, never punished. "Already know it" is a first-class
   answer that maps the edge of their knowledge.
4. **Intentional, not overwhelming.** Small curated sets everywhere: a few
   songs per artist, a few artists per unlock. Scarcity keeps each item worth
   acting on.
5. **Discovery-forward.** The taste model exists to *push* the user outward
   comfortably, not to feed them what they already like. Comfort is the means;
   expansion is the goal.

## 3. The Map (core object)

The home screen is the map: the user's artists floating as circular nodes on a
calm canvas — an organic constellation, not a technical graph.

**Structural reference:** Obsidian's graph — nodes, clusters, visible growth.
**Feel reference:** the "Close Friends" concept UI — warm, soft, breathing
orbs on a gradient; no drawn edges, no cockpit. (Design comes later; this is
recorded so the spec's mechanics are built for that feel.)

### Node = artist

The atomic unit of the map is the **artist**. Albums and songs live *inside*
an artist's detail view; they are not top-level map nodes.
❓ *Revisit if a scene/era grouping ever needs to be a node of its own.*

### Node states

| State | Meaning | Visual intent (directional only) |
|---|---|---|
| **Seeded** | Placed by onboarding — the starting taste | Normal orb |
| **Frontier** | Revealed by an unlock, not yet engaged with | Smaller/dimmer orb at cluster edge |
| **Explored** | User listened and reacted | Full, settled orb |
| **Known** | User marked "already know them" | Settled orb, styled as familiar territory |
| **Blurred** | User explored and disliked | Blurred out; stays on the map as visited ground |

Blurred nodes are important: they never disappear. The map records where you
went and turned back — that's still expansion, and the taste model learns as
much from a dislike as from a like.

### Clusters

Artists group into **clusters by vibe/sound/genre** — neighborhoods of the
map. Going deeper into a cluster reveals more artists within it; the space
between clusters is where cross-genre discovery happens.
❓ *Open: are clusters named/labeled for the user, or purely spatial?*

## 4. Onboarding — adaptive taste duel

**Decided: adaptive until confident.** A series of forced A-or-B choices
between two artists. No two users see the same sequence.

- Each pick narrows the model's estimate of the user's taste, like a binary
  search through music-space: early picks are broad (coarse genre poles),
  later picks are fine (within the neighborhoods the user keeps choosing).
- Runs until the model is confident enough to seed a map — typically **12–20
  picks, ~2–3 minutes** — and ends the moment confidence is reached, not at a
  fixed count.
- Needs an **"I don't know either"** escape hatch — that's a signal too
  (marks the edge of familiarity), and forcing a choice between two unknowns
  would poison the model.
- **Output:** the initial constellation — roughly 10–15 seeded artists across
  2–4 clusters, plus an initial taste vector for the recommendation engine.

The payoff moment: onboarding ends and *your map loads for the first time*.
That reveal is the hook — it must feel like being shown your own reflection.

Resolved in [02-onboarding](specs/02-onboarding.md): duels are name+image
only (no hints, no clips); confidence criterion, seeding rules ("familiar
fills only"), and edge cases are specced there.

## 5. Core loop

```
open app → see your map → tap an artist you like →
"explore this direction" → a few new frontier artists appear →
tap one → see its facet songs → link out and listen (in your own player) →
come back → react: Liked / Not for me / Already knew →
map updates (settle / blur / mark known) → taste model updates →
your engagement banks toward the next unlock
```

### 5.1 Artist detail view

Tapping any artist opens a small, intentional view:

- **A handful of songs chosen to capture different facets of the artist's
  vibe** — not their top hits. The set answers "what are the different sides
  of this artist?" so the user can find *which side* of them they connect
  with. ❓ *Exact count and how facets are chosen/curated — flesh out later;
  the constraint is: intentional, not overwhelming, interesting enough to act
  on.*
- Each song **links out** to the user's streaming app. musicrec never plays
  audio in v1. ❓ *Open: which services to deep-link (Spotify / Apple Music /
  YouTube) and whether the user sets a preferred one.*
- The reaction controls: **Liked / Not for me / Already knew** (plus
  "explore this direction" once they like the artist).

### 5.2 "Explore this direction"

Expansion is **user-initiated**, anchored on an artist they like:

1. User taps "explore this direction" on a liked/known artist.
2. A few (2–3) frontier artists appear near it — chosen by the taste model to
   be *adjacent but new*: same neighborhood but deeper, or one step toward a
   bordering cluster.
3. The user explores them and reacts. Disliked ones blur out; the user picks
   a different direction from a different anchor next time.

"Direction" is both spatial (that part of the map) and semantic (that facet
of their taste). ❓ *Open: does the user ever choose between multiple named
directions from one artist (e.g. "more electronic" vs "more acoustic"), or is
the direction implicit in which artist they anchor from? Lean: implicit —
simpler.*

## 6. Pacing — the unlock economy

The failure mode to avoid: rapid, infinite expansion that makes the map
meaningless. **Leaning (to be tuned): effort-gated + soft daily cap.**

- **Effort-gated:** frontier artists appear only after real engagement — a
  listen-and-reaction, not a tap. No engagement, no growth. The map grows
  exactly as fast as the user's actual listening.
- **Soft daily cap:** even with lots of engagement, only ~3–5 new artists can
  appear per day. Scarcity keeps each reveal an event and makes tomorrow
  worth coming back for (the habit mechanic).
- Listening is **honor-system** — the reaction is the confirmation. We can't
  verify (no streaming data, pure link-out) and shouldn't try; per Principle
  3, honest signals are the currency.

❓ *Open: exact numbers; whether unengaged frontier nodes decay/expire;
whether unlocks bank up when you skip days; whether there's any "daily bloom"
of app-initiated suggestions alongside user-initiated exploration.*

## 7. Taste model

A persistent, per-user model that every signal feeds:

| Signal | Source | What it teaches |
|---|---|---|
| A/B pick | Onboarding | Coarse-to-fine taste position |
| "Don't know either" | Onboarding | Edge of familiarity |
| Liked | Reaction | Pull — go deeper here |
| Not for me | Reaction | Boundary — redirect, don't repeat |
| Already knew | Reaction | Knowledge edge — recommend past this point |
| Explore this direction | Map action | Active appetite, and *where* |
| Which anchor artists get used | Map action | The user's true centers of gravity |

Two hard requirements:

1. **It remembers everything.** Signals accumulate for the life of the user;
   the model is the second core asset after the map (really, the map is a
   view of the model).
2. **It pushes outward.** The model uses what it knows to keep the user
   *comfortable while expanding* — an explicit exploration bias, not a
   relevance-maximizer. Rough shape: most recommendations adjacent-but-new,
   a regular minority that are deliberate stretches toward bordering
   clusters. ❓ *Ratio and mechanism TBD.*

## 8. Data & content (the hard dependency)

The app needs, without any user streaming login:

1. **An artist similarity graph** — who is adjacent to whom, and cluster
   structure (powers the map layout, onboarding duels, and recommendations).
2. **Facet songs per artist** — the curated handful showing an artist's sides.
3. **Artist metadata** — images, links out to streaming services.

Candidate sources to evaluate (not yet chosen): Last.fm API (similar-artists
+ tags), MusicBrainz/ListenBrainz (open data), Deezer API (metadata/images,
no auth), LLM-curated (strong for *facet* selection and human-readable
adjacency, needs grounding against real catalog data), or a hybrid: open
data for the graph + LLM for curation. ❓ *This is the biggest open technical
question and likely the first thing to prototype.*

## 9. Explicitly out of scope for v1

- Spotify/streaming login or listening-history import (possible later as an
  optional enhancement — never a requirement)
- In-app audio playback of any kind
- Social features: friends, sharing, compatibility, leaderboards
- Points/XP/badges/streak counters — the map is the only progress artifact
- Playlists or any library management
- Native mobile apps — **v1 is a mobile-first web app** that also works well
  on desktop (bigger canvas, same map)

## 10. Workstreams

> **New here? Read [HANDOFF.md](HANDOFF.md) first** — it maps every artifact
> in the repo, lists what is decided vs still open, and gives the recommended
> order of work.

This file is the master vision doc. The detailed speccing happens in
`specs/`, one file per workstream, designed to be worked on **in parallel**.
`specs/00-foundations.md` holds the shared contracts (vocabulary, node
states, taste signals, principles) — every other spec must stay consistent
with it; open questions from earlier drafts of this file now live in the
spec that owns them.

| Spec | Owns | Status |
|---|---|---|
| [00-foundations](specs/00-foundations.md) | Shared contracts, platform decisions, accounts, name | 🟡 stable draft |
| [01-design-system](specs/01-design-system.md) | Visual identity → DESIGN.md | 🟠 Golden Hour direction chosen; tokens pending |
| [02-onboarding](specs/02-onboarding.md) | Adaptive duels → seeded map | 🟢 final |
| [03-expansion](specs/03-expansion.md) | Explore-direction, pacing, taste model | 🟠 shape decided |
| [04-core-loop](specs/04-core-loop.md) | Artist detail, facet songs, link-out, reactions, persistence | 🟠 shape decided |
| [05-data-layer](specs/05-data-layer.md) | Artist graph, facet-song pipeline, metadata (prototype-driven) | 🔴 not started, highest risk |

Statuses: 🔴 not started · 🟠 shape decided, details open · 🟡 draft ·
🟢 final (ready for implementation)

**Definition of done per spec:** all its "To spec" items resolved, its
Contracts section confirmed against foundations, and status flipped to 🟢
in this table.

**Implementation handoff:** when all six are 🟢, the bundle
(SPEC.md + specs/ + DESIGN.md) is handed to an implementation agent as-is.
Specs should therefore state *decisions*, not discussions — each ends with
concrete contracts an agent can build against without asking questions.
