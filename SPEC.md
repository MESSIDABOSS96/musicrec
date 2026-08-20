# musicrec — Product Spec

> Working title. An album discovery app: a personal, curated **journey through
> the album canon** — the ~1,000-odd records that show up on every
> greatest-albums list — paced like a museum tour, one album at a time.
>
> Status: **concept spec v0.2 (2026-08-19)** — supersedes the v0.1 taste-map
> concept. v0.1's constellation-of-artists map is retired as the core object
> (its mechanics were built for navigating an infinite artist space; v0.2's
> space is finite and curated). What survives from v0.1 is noted inline.
> Open questions are marked ❓ and owned by the workstream specs.

---

## 1. Origin & thesis

The founding question: *"How much classic music is out there, and how do I
find it?"* — the feeling of seeing someone's top-albums board (Dark Side of
the Moon and forty covers you don't recognize) and having no good way in.

The answer turns out to be the product insight: **the album canon is
finite.** All recorded music is bottomless, but the set of albums that
actually populate those boards — critics' lists, RYM charts, the "1001
Albums" book — is on the order of 1,000–5,000 records. That's a space you
can *complete*. Yet every existing tool for it (RYM, Acclaimed Music,
1001-albums generators) is either a mute database or a random shuffle.

musicrec is the missing experience: **a curator, not a catalog.** Like a
museum docent who sizes you up and then walks you through the collection in
an order built for *you* — starting where you're comfortable, spending time
where you're curious, and routing you toward rooms you'd never have entered
alone — the app takes a fixed canon and turns it into a personal journey
with a definitive end.

Success after 3 months: the user has heard albums they'd always meant to
hear, discovered genres they'd never have touched, can *see* their coverage
of the canon growing, and has a top-albums board of their own emerging from
their likes.

## 2. The three core objects

| Object | What it is | Analogy |
|---|---|---|
| **The Museum** | The album canon — mostly shared by all users, finite, completable | The collection |
| **The Curator** | The sequencing engine: picks *which album next, and why* | The docent |
| **The Journey** | The user's personal path: rooms → chapters → the whole museum | The tour |

**The museum is (mostly) the same for everyone. The tour is personal.**
Personalization is a *sequencing* problem over a finite set, not a
recommendation problem over an infinite one. That is the central
simplification of v0.2.

## 3. Principles

1. **Super simple.** One core object (the journey), one core action
   (receive album → listen → react → advance). Every feature must justify
   itself against this.
2. **The journey is the score.** Coverage of your museum, chapters
   completed, and the board of your likes are the only progress artifacts.
   No points, XP, badges, streaks. *(Carried from v0.1: "the map is the
   score", re-aimed.)*
3. **Honest signals over surveillance.** No streaming login, no
   listening-history import, ever, in v1. Listening is honor-system; the
   reaction is the confirmation. "Already knew it" is a first-class answer
   that skips you forward — knowing things is never punished. *(Carried
   from v0.1 verbatim.)*
4. **One album in hand.** The curator hands you exactly one album at a
   time. No feeds, no grids of suggestions, no backlog anxiety. The only
   pressure valve is "not today — show me a different door."
5. **Expansion through bridges, never jumps.** The curator never teleports
   you across the museum. Every stretch toward a new genre arrives via an
   album that genuinely connects it to something you just liked. Curiosity
   is manufactured by *ordering*, not by exhortation.
6. **A definitive end.** The journey is completable. The user is always
   working toward something visible and finite.

## 4. The Museum (the canon)

- **Core canon (shared):** ~1,000 albums every user's museum contains — the
  undisputed spine, assembled from the established canon sources
  (Acclaimed Music aggregate, RYM all-time charts, the 1001 Albums book,
  Rolling Stone 500, plus genre-specific lists so non-rock canons are
  fairly represented). ❓ *Exact size and assembly recipe → 05-canon.*
- **Personal wings (variance):** each user's museum flexes from a larger
  extended pool (~3,000–5,000 albums): **deeper cuts in the wings they
  love** (a hip-hop head's museum goes deeper into hip-hop than the core
  canon does) and **curated entry points into wings they've never
  explored** (the 3 most-approachable jazz records, not the 40 most
  canonical). Two users' museums heavily overlap but are not identical.
  ❓ *How much flex; whether wings grow during the journey → 03-journey.*
- Every user's museum is a **fixed, knowable size** once assembled —
  that's what makes coverage and completion meaningful.

### Album states (the shared contract)

| State | Meaning |
|---|---|
| **Unvisited** | In your museum, not yet reached |
| **In hand** | The album the curator has currently given you (exactly 0 or 1) |
| **Liked** | Heard it, loved it — feeds the board |
| **Not for me** | Heard it, not your thing — visited ground, never resurfaces as a listen, still counts as coverage |
| **Already knew** | Knew it before the journey — instant skip-forward credit, counts as coverage |
| **Passed** | "Not today" — no signal recorded, returns later on a different path |

*(v0.1's "blurred nodes never disappear" survives as: Not-for-me albums
stay visible in your history/museum as visited ground.)*

## 5. Onboarding — the curator sizes you up

**Adaptive A-or-B album-cover duels, running until confident** — the v0.1
onboarding mechanic (specced final in [02-onboarding](specs/02-onboarding.md))
carried over with albums instead of artists:

- Forced choice between two album covers; "I don't know either" as a
  first-class escape hatch; fame-matched pairs; coarse-to-fine (broad genre
  poles first, refinement after); floor 12 picks, cap 20, ~2–3 minutes.
- **Output:** the user's taste position (genre affinities) + knowledge edge
  (how deep their album familiarity runs) → the curator assembles their
  museum and builds Chapter 1.
- The payoff moment: onboarding ends and **the journey begins** — the
  curator introduces itself, names your first chapter, and hands you your
  first album. ❓ *Whether a museum-overview reveal precedes the first
  album → 01-design-system.*

## 6. The Journey

### 6.1 Rooms — one album at a time

The core unit is a **room**: one album, given to you by the curator with a
line or two of *why this, why now* — connective narration tying it to what
you just heard ("You loved the drums on the last one; this is the record
they were sampled from"). You listen in your own streaming app (pure
link-out, no in-app audio), come back, and react:

- **Liked / Not for me / Already knew** — advances you to the next room.
- **"Not today — show me a different door"** — a pass, not a dislike. The
  curator offers a different next album; the passed album returns later.
  ❓ *Pass limits / anti-abuse → 03-journey.*

### 6.2 Chapters — the manageable bits

Rooms group into **chapters**: short themed legs of ~5–8 albums the curator
names for you ("Where your indie rock came from"). Chapters are the
mile-markers — small enough to finish in a week or two of normal listening,
narrative enough to feel like a guided tour rather than a queue.
❓ *Chapter construction, themes, and what a chapter-complete moment looks
like → 03-journey / 01-design-system.*

### 6.3 The route — how the curator sequences

- **Start in the home wing:** the first chapters are canon pillars in
  genres the user already loves but hasn't heard. Early wins build trust.
- **Expand via bridge albums:** genre stretches arrive through albums that
  genuinely connect two worlds (hip-hop → the soul it sampled → funk →
  jazz-fusion → jazz). Each album is chosen so the previous ones have made
  the user ready for it.
- **Reactions steer:** Liked → thread continues, next door opens. Not for
  me → curator backs off, approaches that wing later via a different
  bridge. Already knew → skip forward. ❓ *Full sequencing policy →
  03-journey.*

### 6.4 Pacing — self-paced, reaction-gated

**No calendar.** The gate is reacting to the album in hand, not waiting for
midnight. Move at listening speed: a chapter in a weekend or a month, both
fine. *(v0.1's "effort-gated" principle survives; the daily cap does not —
one-album-in-hand makes it unnecessary.)* ❓ *Whether any soft ceiling is
needed for binge-completionists → 03-journey.*

## 7. Core loop

```
open app → see your journey (current chapter, current room) →
the album in hand: cover + the curator's "why this, why now" →
link out and listen (your own player) → come back →
react: Liked / Not for me / Already knew   (or pass: "different door") →
coverage ticks up, board grows if Liked → curator hands you the next room →
chapter completes → next chapter begins
```

## 8. Progress & the trophy

- **Coverage:** "127 of 1,043" — heard (any reaction) over museum size.
  The definitive thing being worked toward.
- **Chapters completed** — the journey's visible mile-markers.
- **The board:** the user's top-albums collage (topster) assembling itself
  from their Liked albums — shareable as an image, the identity artifact
  the whole idea came from. ❓ *Board mechanics (auto vs. user-arranged,
  sizes) → 04-core-loop.*

## 9. Visual direction (recorded, not designed)

Design is deliberately deferred, but the spec's mechanics are built for:

- **Structure: room-to-room / level-to-level progression** — the journey
  reads like a world you move through (reference: Super Mario world maps —
  a drawn path through named regions, completed rooms behind you, the
  current room lit, future rooms present but not yet open). This replaces
  v0.1's constellation as the structural metaphor.
- **Feel: Golden Hour** — the dusk-warm direction already chosen and
  measured in [01-design-system](specs/01-design-system.md) and
  `design/analysis/reference-teardown.md`. The aesthetic survives the
  rescope untouched; only the surface inventory changes.

## 10. Data & content

What the product needs (all buildable **offline, once** — no live
recommendation engine in v1):

1. **The canon dataset** — core canon + extended pool: album, artist, year,
   genres, cover art, streaming links, a short what-this-is blurb.
2. **The connection graph** — which albums bridge which (influence,
   sampling, lineage, scene), with a human-readable "why this next" line
   per edge. Static, over a few thousand nodes; LLM-curated and grounded
   against the list/metadata sources, checkable by hand.
3. **Duel pool metadata** — fame tiers + covers for onboarding.

Sources: Acclaimed Music / RYM charts / 1001 Albums / RS500 for canon
membership; MusicBrainz for canonical metadata; Deezer/streaming APIs for
covers and link-outs; LLM curation for narration and bridges.
❓ *Assembly pipeline and data contracts → 05-canon. This was v0.1's
highest-risk workstream; the rescope reduces it to a one-time curation
job — the risk is now editorial quality, not feasibility.*

## 11. Explicitly out of scope for v1

- Spotify/streaming login or listening-history import *(unchanged)*
- In-app audio playback of any kind *(unchanged)*
- Social features: friends, sharing-to-feed, compatibility *(unchanged;
  exporting your board as an image is not social)*
- Points/XP/badges/streaks *(unchanged)*
- Playlists or library management *(unchanged)*
- Native mobile apps — v1 is a **mobile-first web app**, desktop supported
  *(unchanged)*
- **The v0.1 constellation map** — retired as the core object. Its feel
  may inform the museum-overview visual; its mechanics (frontier nodes,
  explore-this-direction, unlock economy, live taste model) are not built.
- Free-browse of the whole canon — v1 is the guided journey only.
  ❓ *Revisit post-v1; a "browse the museum" view is the natural add-on.*

## 12. Workstreams

> **New here? Read [HANDOFF.md](HANDOFF.md) first** — it maps every
> artifact in the repo and gives the recommended order of work.

`specs/00-foundations.md` holds the shared contracts; every other spec must
stay consistent with it. Statuses: 🔴 not started · 🟠 shape decided ·
🟡 stable draft · 🟢 final (buildable).

| Spec | Owns | Status |
|---|---|---|
| [00-foundations](specs/00-foundations.md) | Shared contracts, platform decisions, accounts, name | 🟡 rewritten for v0.2 |
| [01-design-system](specs/01-design-system.md) | Golden Hour identity → DESIGN.md; journey/room surfaces | 🟠 direction chosen; inventory updated for v0.2; tokens pending |
| [02-onboarding](specs/02-onboarding.md) | Adaptive album duels → taste position + museum assembly | 🟡 v0.1 final mechanic ported to albums; outputs re-contracted |
| [03-journey](specs/03-journey.md) | The curator: museum assembly, sequencing, chapters, bridges, passes, pacing | 🟠 shape decided in v0.2 rescope |
| [04-core-loop](specs/04-core-loop.md) | The room: album view, narration, link-out, reactions, board, persistence | 🟠 shape decided in v0.2 rescope |
| [05-canon](specs/05-canon.md) | Canon dataset, connection graph, narration pipeline | 🔴 not started — first thing to prototype |

**Definition of done per spec:** all "To spec" items resolved, Contracts
confirmed against foundations, status flipped to 🟢.

**Implementation handoff:** when all six are 🟢, the bundle
(SPEC.md + specs/ + DESIGN.md) goes to an implementation agent as-is.
Specs state *decisions*, not discussions.
