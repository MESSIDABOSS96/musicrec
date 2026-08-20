# Handoff — start here

Entry point for anyone (human or agent) picking up musicrec. Read this first,
then `SPEC.md`.

**The project was rescoped on 2026-08-19 (spec v0.2).** v0.1 was a
constellation-map of artists with an unlock economy; v0.2 is an **album
discovery journey**: a fixed, completable album canon (the Museum) that a
sequencing engine (the Curator) walks each user through room-by-room,
chapter-by-chapter, Mario-world-map style. If you find artifacts talking
about artist nodes, frontier unlocks, or facet songs, they predate the
rescope.

**Read this before writing code: the project is not ready to implement
end-to-end.** Three of six specs are shape-only, and `05-canon` — the canon
dataset and connection graph — is unstarted and everything consumes it. The
recommended order of work is at the bottom.

---

## Where everything is

### Product specs
| File | What it holds | State |
|---|---|---|
| `SPEC.md` | Master vision (v0.2), principles, core loop, workstream board | vision settled |
| `specs/00-foundations.md` | **Shared contracts** — vocabulary (Museum/Curator/Journey/Room/Chapter), album states, signals, platform decisions. Everything else must stay consistent with this. | stable draft; accounts + name still open |
| `specs/01-design-system.md` | Golden Hour identity, surface inventory (updated for v0.2) | direction chosen, tokens not written |
| `specs/02-onboarding.md` | Adaptive A/B **album** duels → taste state for the curator | stable draft — v0.1's final artist-duel mechanic ported to albums; re-finalize once 03 confirms the handoff |
| `specs/03-journey.md` | The curator: museum assembly, sequencing, chapters, bridges, passes, pacing | shape decided, details open |
| `specs/04-core-loop.md` | The room: album view, narration, link-out, reactions, the Board, persistence | shape decided, details open |
| `specs/05-canon.md` | Canon dataset, connection graph, narration pipeline | **unspecced — first thing to prototype** |

### Design research
| File | What it holds |
|---|---|
| `design/analysis/reference-teardown.md` | **The most load-bearing design document.** Measured reverse-engineering of the two lofi sunset references — value structure, depth-plane luminance shelves, hue-rotation-with-value rule, light-source bloom ratios, extracted colour ramps as hex tables. Plus a study of bruno-simon.com on how an exploratory space teaches itself. All of it survives the rescope — the aesthetic is unchanged. |
| `design/analysis/scripts/*.py` | The scripts that produced those measurements. Re-runnable on any new reference image. Need `pillow` + `numpy`. |
| `design/inspiration/*.png` | 9 reference images. The two `lofi-*` ones are the primary direction; `close-friends-*` were the v0.1 map-structure reference (retired — v0.2's structural reference is Super Mario world maps, not yet collected). |
| `design/listening-room/` | The user's in-progress experiential design work (the design window). Separate track from the spec work. |
| `design/explorations/golden-hour-landing.html` | First landing-page attempt. **Superseded — it predates the teardown and violates most of its findings.** Keep as a record of what not to do. |

### Not part of this project
`wb2022.html` in the repo root predates this work and is unrelated.

---

## What is decided (do not re-litigate)

From `specs/00-foundations.md` and SPEC.md v0.2:

- The product is a **guided journey through a finite album canon** — not a
  browsable database, not a daily-drop feed, not the v0.1 map.
- The museum is (mostly) shared; the tour is personal. Personalization is
  **sequencing over a finite set** plus bounded museum variance (deeper
  cuts in loved wings, entry points in unexplored ones).
- **One album in hand** at a time; reacting is the only gate. No calendar
  pacing, no daily cap.
- Reactions: Liked / Not for me / Already knew. **Pass ("not today — show
  me a different door")** is scheduling, not a taste signal.
- Chapters of ~5–8 themed rooms; expansion via **bridge albums only**.
- The curator **narrates** every handoff ("why this, why now").
- Progress = coverage + chapters + the Board (topster of likes). No
  points/XP/badges/streaks.
- No streaming login, no history import, no in-app audio. Pure link-out.
  Honor-system listening. "Already knew" always rewarded.
- Mobile-first web app; no native apps; no social features in v1.
- Onboarding: adaptive album-cover duels, one-shot, no retake.
- Visual: Golden Hour aesthetic + Mario-world-map journey structure
  (design itself deliberately deferred).

## What is still open (someone must decide)

1. **`05-canon` — everything.** Canon assembly recipe, the shared space +
   wings, fame tiers, the connection graph + narration pipeline, link
   resolution. **This blocks 02, 03, and 04**, all of which consume it.
2. **`03-journey`** — museum assembly numbers, chapter construction,
   sequencing policy, pass mechanics, not-for-me recovery, completion.
3. **`04-core-loop`** — room view content, link-out targets, reaction
   mutability, Board mechanics, persistence/accounts.
4. **`01-design-system`** — the tokens themselves; the journey-map grammar;
   the curator's visual presence.
5. **`00-foundations`** — accounts, and the product name.

---

## Recommended order of work

1. **Prototype the canon** (`05`). Assemble a draft core canon from the
   list sources (Acclaimed Music, RYM, 1001, RS500 + genre lists), then
   prototype the connection graph + narration on one wing pair (hip-hop ↔
   soul/jazz). This is cheap, it's the whole product's substrate, and its
   editorial quality decides whether the curator feels magical or generic.
2. **Close `03-journey`** — with real canon data in hand, the sequencing
   and chapter questions become concrete product conversations.
3. **Write `DESIGN.md`** from the teardown + a Mario-world-map structural
   pass. The Golden Hour measurements are already done.
4. **Close `04-core-loop`**, revalidate `02-onboarding`'s handoff, then
   **build**.

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

From the bruno-simon.com study, two rules that apply even better to the
journey map than they did to the constellation: **borrow a physical mental
model the user already owns** (the Mario world map IS that move) and **give
the road ahead a real affordance** — the author of the most famous
exploratory site on the web concluded, after watching real users, that he
needed more interface, not less.
