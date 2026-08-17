# Handoff — start here

Entry point for anyone (human or agent) picking up musicrec. Read this first,
then `SPEC.md`.

**Read this before writing code: the project is not ready to implement
end-to-end.** Three of six specs are still open, and one of them
(`05-data-layer`) can invalidate the whole concept. Building the app now means
inventing those answers on the fly. The recommended order of work is at the
bottom.

---

## Where everything is

### Product specs
| File | What it holds | State |
|---|---|---|
| `SPEC.md` | Master vision, principles, core loop, workstream status board | vision settled |
| `specs/00-foundations.md` | **Shared contracts** — vocabulary, node states, taste signals, platform decisions. Everything else must stay consistent with this. | stable draft; accounts + product name still open |
| `specs/01-design-system.md` | Visual identity direction, surface inventory | direction chosen, tokens not written |
| `specs/02-onboarding.md` | Adaptive A/B duels → seeded map | **final — buildable** |
| `specs/03-expansion.md` | "Explore this direction", pacing, taste model | mechanic decided, economy open |
| `specs/04-core-loop.md` | Artist detail, facet songs, link-out, reactions, persistence | shape decided, details open |
| `specs/05-data-layer.md` | Artist graph, facet songs, metadata | **unspecced, highest risk** |

### Design research
| File | What it holds |
|---|---|
| `design/analysis/reference-teardown.md` | **The most load-bearing design document.** Measured reverse-engineering of the two lofi sunset references — value structure, depth-plane luminance shelves, hue-rotation-with-value rule, light-source bloom ratios, extracted colour ramps as hex tables. Plus a study of bruno-simon.com on how an exploratory space teaches itself. |
| `design/analysis/scripts/*.py` | The scripts that produced those measurements. Re-runnable on any new reference image. Need `pillow` + `numpy`. |
| `design/inspiration/*.png` | 9 reference images. The two `lofi-*` ones are the primary direction; `close-friends-*` are the map-structure reference. |
| `design/explorations/golden-hour-landing.html` | First landing-page attempt. **Superseded — it predates the teardown and violates most of its findings** (see "Where my first landing-page attempt went wrong" in the teardown). Keep as a reference for what not to do, or delete. |

### Not part of this project
`wb2022.html` in the repo root predates this work and is unrelated.

---

## What is decided (do not re-litigate)

From `specs/00-foundations.md` and the vision doc:

- No Spotify login, no streaming-history import, no in-app audio. Pure
  link-out to the user's own player.
- The map (artists as orbs, clustered by vibe, no drawn edges) **is** the
  score. No points, badges, XP, or streaks.
- Node states: `Seeded → Frontier → (Explored | Known | Blurred)`. Blurred
  nodes never disappear.
- "Already know it" is a first-class positive signal, never a failure.
- Expansion is user-initiated from a liked anchor artist.
- Mobile-first web app, desktop supported. No native apps in v1.
- No social features in v1.
- Onboarding is one-shot; there is no "retake the quiz" surface.

## What is still open (someone must decide)

1. **`05-data-layer` — everything.** Where the artist similarity graph, cluster
   structure, fame tiers, and facet songs come from with no user streaming
   login. Candidates: Last.fm, MusicBrainz/ListenBrainz, Deezer, LLM-curated,
   or a hybrid. **This blocks 02, 03, and 04**, all of which consume it.
2. **`03-expansion`** — unlock cost, daily cap, whether unlocks bank, frontier
   decay, how frontier artists are selected, the stretch ratio.
3. **`04-core-loop`** — facet-song count and curation, link-out targets,
   whether reactions are changeable, persistence model.
4. **`01-design-system`** — the tokens themselves. The direction and the
   measured source values exist; nobody has written `DESIGN.md` yet.
5. **`00-foundations`** — accounts (anonymous-local vs accounts day one), and
   the product name.

---

## Recommended order of work

1. **Prototype the data layer** (`05`). Pick 5 seed artists across genres,
   pull similar-artists from each candidate source, judge quality by hand; try
   getting 3–5 "facet songs" for 10 artists you know well. This is cheap and
   it either validates or kills the approach. Everything else waits on it.
2. **Write `DESIGN.md`** from `design/analysis/reference-teardown.md`. The
   measurements are already done — the ramps are extracted as hex tables and
   the rules are stated explicitly. This is now a mechanical translation job,
   not a taste job.
3. **Close `03-expansion` and `04-core-loop`** — these are product
   conversations, not research.
4. **Then build.** `02-onboarding` is already specced tightly enough to build
   against, once the data layer can supply its duel pool.

### Notes for whoever builds the UI

The teardown's findings are non-obvious and easy to lose. The short version:
depth is encoded as monotonic luminance with each plane in its own narrow
value shelf; ~80% of colour sits in one 60° warm hue wedge with a small,
always-less-saturated cool counterpoint; hue rotates toward red in shadow and
toward yellow in light, so nothing is ever grey or neutral; light sources are
flat pale-yellow cores (never white) whose bloom radius scales with
importance in roughly an 8:2:1 ratio; and the focal point is the *flattest*
area in the frame, not the most detailed. Read the document before styling
anything.

From the bruno-simon.com study, two rules for the map: **borrow a physical
mental model the user already owns** rather than teaching a new abstraction,
and **give the frontier a real affordance** — the author of the most famous
exploratory site on the web concluded, after watching real users, that he
needed more interface, not less.
