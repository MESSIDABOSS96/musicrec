# 02 — Onboarding

> Status: **stable draft** — the v0.1 artist-duel spec (final, 2026-08-16)
> ported to album duels in the 2026-08-19 v0.2 rescope. The duel mechanics
> carried over intact; the *output contract* changed (no map seeding — the
> curator now consumes onboarding's taste state to assemble the museum and
> build Chapter 1). Re-flip to 🟢 once 03-journey confirms the handoff.
>
> Scope: everything from first visit to the first album being handed over.

## Decided shape (recap)

- **Adaptive A-or-B album duels, running until confident** — floor 12
  picks, hard cap 20, typically ~2–3 minutes. No two users see the same
  sequence.
- Coarse-to-fine: early duels span broad genre poles; later duels refine
  within the wings the user keeps choosing.
- **"I don't know either"** is a first-class answer marking the edge of
  familiarity — never force a pick between two unknowns.
- **Onboarding owns the whole screen.** Nothing else exists for the user
  until it ends. The ending — the curator introducing itself, naming
  Chapter 1, and handing over the first album — is the product's first
  emotional beat, and onboarding is designed backwards from it.
- **Output:** taste position (wing affinity weights) + familiarity set +
  recognition level, consumed by 03-journey.

## 1. Taste state during onboarding

The model's picture of the user is three things, updated after every answer:

1. **Wing affinity weights** — a weight per wing/genre-region of the album
   space (space supplied by 05-canon), normalized. Starts uniform.
2. **Familiarity set** — every album shown so far, tagged with the outcome:
   picked, passed over, or don't-know. Picked ⇒ confirmed known.
3. **Recognition level** — how deep the user's album knowledge runs,
   expressed in the fame tiers of the duel pool (see Contracts). Starts at
   the top tier; "don't know either" pushes it toward mega-famous,
   confident fast picks let it relax downward.

Per-answer updates:

- **Pick A over B:** increase the affinity of A's wing, decrease B's by a
  smaller amount (a pick is preference, not dislike). Add both albums to
  the familiarity set (A confirmed known; B only *shown*, not confirmed).
- **Don't know either:** no affinity change. Mark both albums don't-know,
  raise the recognition-level requirement, and immediately re-deal a more
  famous pair in the same region. Two consecutive don't-knows in the same
  region ⇒ mark the region unfamiliar and stop probing it. (Unfamiliar
  regions are prime targets for entry-point curation later — see 03.)

## 2. Duel selection policy

Each round, choose the pair that maximizes expected information about the
affinity weights, subject to hard constraints:

- **Both albums at or above the user's current recognition level.**
- **Fame-matched:** the two albums are from the same fame tier, so the pick
  measures taste, not recognizability.
- **No album appears twice** across a user's onboarding.

Phased for predictability:

- **Phase 1 (picks 1–5):** pairs spanning distant poles of the space, top
  fame tier only. Goal: locate which broad wings the user lives in.
- **Phase 2 (pick 6 onward):** pairs drawn within and between the current
  leading wings — deeper cuts, adjacent-wing contests — refining weights
  where uncertainty is highest.

## 3. Confidence criterion (what ends onboarding)

Onboarding ends at the first pick ≥ 12 where **both** hold:

1. **Stable leaders:** the set of leading wings (top 2–4 by weight) has not
   changed over the last 3 picks.
2. **Anchored:** at least 6 confirmed-known albums sit inside those leading
   wings — enough confirmed ground for the curator to start the journey
   from genuinely familiar territory.

Hard cap: pick 20. If the cap is hit without both conditions, end anyway
and hand off best-effort per the edge-case rules (§6).

## 4. Presentation

- **Cover + album title + artist name only.** No genre labels, no
  descriptions, no sound clips — the no-in-app-audio rule has no
  onboarding exception. Album covers are the strongest recognition
  artifact in music; the card is mostly cover.
- Two large tappable cards (A / B) + a visually smaller third action:
  **"I don't know either."**
- Full-screen takeover. No journey preview, no header chrome. A subtle
  confidence-driven progress cue is allowed (adaptive length needs *some*
  signal of movement); exact treatment owned by 01-design-system.
- The ending transition (final pick → the curator's introduction → Chapter
  1 named → first album in hand) is owned by 01-design-system; this spec's
  only requirement is that it is a single uninterrupted moment — no
  summary screen, no "building your museum…" checklist.
  ❓ *Whether a brief museum-overview beat (the "world map" glimpse)
  belongs inside this moment → 01-design-system.*

## 5. Handoff to the curator

**No seeding, no reveal-of-a-map.** Onboarding's entire output is taste
state; 03-journey turns it into a museum and a route:

1. **Final wing affinity weights** — which wings are home, which border
   home, which are unfamiliar.
2. **Full familiarity set** — confirmed-known albums (already-heard
   territory the curator routes *around*), shown-but-unconfirmed albums
   (not treated as dislikes), and don't-know albums/regions (the knowledge
   edge).
3. **Recognition level** — calibrates how deep Chapter 1's picks can go.

The curator uses these to (a) assemble the user's museum (core canon +
personal wings, per 03-journey) and (b) build Chapter 1 in the user's home
wing: canon pillars they *don't* already know. Confirmed-known albums are
pre-credited as **Already knew** where they're in the museum — onboarding
knowledge counts toward coverage from minute one.

## 6. Edge cases

- **Knows almost nothing** (don't-knows persist even at the top fame
  tier): hand off with low confidence flagged; the curator opens with the
  genre-spanning "front hall" chapter — maximally famous, maximally
  approachable albums across 3–4 wings — and lets reactions do the work
  onboarding couldn't. An honest cold start the journey corrects quickly.
- **Omnivore** (affinity never narrows; > 4 strong wings at the cap): a
  wide home is a valid home; the curator alternates early chapters across
  the leading wings. Omnivory is taste, not failure.
- **Abandoned mid-onboarding:** duel state (answers, affinity, recognition
  level) persists locally after every answer; returning resumes at the
  next duel, never restarts. (Persistence mechanism follows the accounts
  decision owned by 00-foundations.)

## 7. Re-onboarding

**No.** Onboarding is one-shot per user; the journey self-corrects through
reactions, and every post-onboarding signal outweighs a redo. There is no
"retake the quiz" surface anywhere in v1.

## Contracts

- **Consumes from 05-canon** — the duel pool, which must provide:
  - album positions + wing structure over one shared space;
  - a **fame tier** per album (≥ 3 tiers; tier 1 = recognizable by
    cover+title to a casual listener), with every wing represented at
    tier 1 — onboarding only ever duels tier 1–2 albums;
  - cover art + title + artist per album (cover quality matters: it is
    most of the duel card).
  - Target pool size: ~200–400 duel-eligible albums covering the space at
    tier 1–2. *These requirements are inputs to 05 — confirm there.*
- **Produces for 03-journey:** final wing affinity weights + full
  familiarity set + recognition level. Signals conform to 00-foundations.
- **Owned by 01-design-system:** duel card layout, progress cue, and the
  ending transition into Chapter 1.
