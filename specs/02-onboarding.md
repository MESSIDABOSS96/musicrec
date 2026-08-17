# 02 — Onboarding

> Status: **final** — all open items resolved in the 2026-08-16 onboarding
> spec session. States decisions an implementation agent can build against.
>
> Scope: everything from first visit to the map reveal.

## Decided shape (recap)

- **Adaptive A-or-B artist duels, running until confident** — floor 12 picks,
  hard cap 20, typically ~2–3 minutes. No two users see the same sequence.
- Coarse-to-fine: early duels span broad genre poles; later duels refine
  within the neighborhoods the user keeps choosing.
- **"I don't know either"** is a first-class answer marking the edge of
  familiarity — never force a pick between two unknowns.
- **Onboarding owns the whole screen.** Nothing else is visible until it
  ends; the map does not exist for the user until the reveal. The reveal is
  the product's emotional hook and onboarding is designed backwards from it.
- **Output:** the seeded map (10–15 artists across 2–4 clusters) + the
  initial taste state consumed by 03-expansion.

## 1. Taste state during onboarding

The model's picture of the user is three things, updated after every answer:

1. **Neighborhood affinity weights** — a weight per neighborhood/cluster of
   the artist space (space and clusters supplied by 05-data-layer),
   normalized. Starts uniform.
2. **Familiarity set** — every artist shown so far, tagged with the outcome:
   picked, passed over, or don't-know. Picked ⇒ confirmed known.
3. **Recognition level** — an estimate of how deep the user's artist
   knowledge runs, expressed in the fame tiers of the duel pool (see
   Contracts). Starts at the top tier; "don't know either" pushes it up
   toward mega-famous, confident fast picks let it relax downward.

Per-answer updates:

- **Pick A over B:** increase the affinity of A's neighborhood, decrease B's
  by a smaller amount (a pick is preference, not dislike). Add both artists
  to the familiarity set (A confirmed known; B only *shown*, not confirmed).
- **Don't know either:** no affinity change. Mark both artists don't-know,
  raise the recognition-level requirement, and immediately re-deal a more
  famous pair in the same region. Two consecutive don't-knows in the same
  region ⇒ mark the region unfamiliar and stop probing it.

## 2. Duel selection policy

Each round, choose the pair that maximizes expected information about the
affinity weights, subject to hard constraints:

- **Both artists at or above the user's current recognition level.**
- **Fame-matched:** the two artists are from the same fame tier, so the pick
  measures taste, not recognizability.
- **No artist appears twice** across a user's onboarding.

Coarse-to-fine emerges from the objective, but the policy is explicitly
phased for predictability:

- **Phase 1 (picks 1–5):** pairs spanning distant poles of the space, top
  fame tier only. Goal: locate which broad regions the user lives in.
- **Phase 2 (pick 6 onward):** pairs drawn within and between the current
  leading neighborhoods — deeper cuts, adjacent-cluster contests — refining
  weights where uncertainty is highest.

## 3. Confidence criterion (what ends onboarding)

Onboarding ends at the first pick ≥ 12 where **both** hold:

1. **Stable leaders:** the set of leading neighborhoods (top 2–4 by weight)
   has not changed over the last 3 picks.
2. **Seedable:** at least 6 confirmed-known artists sit inside those leading
   neighborhoods (enough kept picks to seed a map that is majority-confirmed).

Hard cap: pick 20. If the cap is hit without both conditions, end anyway and
seed best-effort per the edge-case rules (§6).

## 4. Presentation

- **Name + artist image only.** No genre hints, no descriptions, no sound
  clips — the no-in-app-audio rule has no onboarding exception. If the
  presentation alone can't carry recognition, that's what "don't know
  either" is for.
- Two large tappable cards (A / B) + a visually smaller third action:
  **"I don't know either."**
- Full-screen takeover. No map preview, no forming constellation, no header
  chrome. A subtle confidence-driven progress cue is allowed (adaptive
  length needs *some* signal of movement) but it must not preview the map;
  exact treatment is owned by 01-design-system.
- The reveal transition (final pick → map appears) is owned by
  01-design-system; this spec's only requirement is that it is a single
  uninterrupted moment — no intermediate summary screen, no "creating your
  map…" checklist.

## 5. Seeding the map

**Policy: familiar fills only — extrapolate familiarity, never taste
guesses.** Every orb at the reveal should land as "yes, that's me." The
reveal dies on "who is that?", so nothing unknown-to-the-user is seeded.

Build the seed set (10–15 artists, 2–4 clusters) as:

1. **Kept picks (~6–9).** Confirmed-known picked artists located inside the
   final leading neighborhoods. Coarse early picks that ended up far from
   the final estimate are dropped — *unless* the user consistently chose
   that pole, in which case it is a real leading neighborhood, not an
   outlier.
2. **Familiar fills (~4–6, hard cap 40% of the seed set).** Per leading
   cluster, add the most famous artists nearest the cluster's center of
   user-affinity that were not shown during duels — artists the user almost
   certainly already knows. Fill until each seeded cluster has ≥ 3 orbs and
   the total is within 10–15.
3. All seeds enter in node state **Seeded**, positioned by the data layer's
   space. Wrong fills are cheap: the user reacts "Not for me" and the node
   blurs — the map self-corrects; there is no confirmation step at reveal.

**Handoff to 03-expansion:** the final affinity weights + the full
familiarity set (including don't-knows and passed-over artists) persist into
the taste model. Passed-over artists are *not* treated as dislikes. No
frontier nodes exist at reveal; the first "explore this direction" creates
them.

## 6. Edge cases

- **Knows almost nothing** (don't-knows persist even at the top fame tier):
  if fewer than 6 confirmed picks by the cap, seed whatever picks exist plus
  top-fame fills biased toward them. If there are ~0 picks, seed a
  genre-spanning sampler of maximally famous artists (3 clusters, ~12
  artists) — an honest starting guess the map corrects through use.
- **Omnivore** (affinity never narrows; > 4 strong neighborhoods at the
  cap): seed the top 4 clusters by weight, 3–4 artists each. A wide map is a
  valid map; omnivory is taste, not failure.
- **Abandoned mid-onboarding:** duel state (answers, affinity, recognition
  level) persists locally after every answer; returning resumes at the next
  duel, never restarts. (Persistence mechanism follows the accounts decision
  owned by 00-foundations.)

## 7. Re-onboarding

**No.** Onboarding is one-shot per user; the map self-corrects through use,
and every post-onboarding signal outweighs a redo. There is no "retake the
quiz" surface anywhere in v1.

## Contracts

- **Consumes from 05-data-layer** — the duel pool, which must provide:
  - artist positions + cluster/neighborhood structure over one shared space;
  - a **fame tier** per artist (≥ 3 tiers; tier 1 = recognizable by name+image
    to a casual listener), with every neighborhood represented at tier 1 —
    onboarding only ever duels tier 1–2 artists;
  - name + image per artist (image quality matters: it is half the duel card).
  - Target pool size: ~200–400 duel-eligible artists covering the space at
    tier 1–2. *These requirements are inputs to 05 — confirm there.*
- **Produces for 03-expansion:** seeded nodes (state `Seeded`) + initial
  taste state = final affinity weights + full familiarity set. Signals
  conform to 00-foundations (A/B pick, "don't know either").
- **Owned by 01-design-system:** duel card layout, progress cue treatment,
  and the reveal transition.
