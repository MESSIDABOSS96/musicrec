# 03 — Expansion & pacing

> Status: **core mechanic decided, economy unspecced.** The heart of the
> product — how the map grows, and why it never explodes.

## Decided

- Expansion is **user-initiated**: "explore this direction" from an anchor
  (a liked/known artist). The app does not passively flood the map.
- Each explore reveals a **few (2–3) frontier artists** adjacent to the
  anchor: same neighborhood but deeper, or one step toward a bordering
  cluster.
- Disliked artists **blur but never disappear** — visited ground is still
  expansion, and dislikes teach the model as much as likes.
- Pacing = **effort-gated + soft daily cap** (leaning): growth requires a
  real listen-and-reaction, and even heavy engagement reveals at most ~3–5
  new artists/day. Scarcity makes each reveal an event and tomorrow worth
  returning for.
- Listening is honor-system; the reaction IS the confirmation.
- The taste model has an explicit **exploration bias**: mostly
  adjacent-but-new picks, with a regular minority of deliberate stretches
  toward bordering clusters.

## To spec

1. **Unlock economy numbers** — engagement cost per explore, exact daily
   cap, whether unused unlocks bank across days.
2. **Direction semantics** — implicit (the anchor artist IS the direction —
   current lean, simpler) vs. explicit (user picks among named directions
   like "more electronic"). Decide and kill the other.
3. **Frontier selection algorithm** — given anchor + taste model, how the
   2–3 artists are chosen; the deeper-vs-bordering mix; how the stretch
   ratio is tuned; never re-surface blurred artists.
4. **Frontier lifecycle** — do unengaged frontier nodes decay/expire, or
   wait forever? Cap on simultaneous frontier nodes?
5. **Cluster mechanics** — how clusters form/split as the map grows; whether
   the user ever jumps to a genuinely foreign cluster ("new continent"
   moment) and what triggers it.
6. **App-initiated bloom?** — is there any daily app-suggested artist
   alongside user-initiated exploration, or is v1 purely user-driven?
   (Interacts with re-engagement: what brings a user back on a day they
   don't feel like exploring?)
7. **Taste model update rules** — how each reaction shifts the model;
   recency weighting; how "Already knew" expands the knowledge frontier the
   model recommends past.
8. **Anti-degenerate cases** — the user who only explores one cluster
   forever; the user who dislikes everything; the completionist gaming the
   cap.

## Contracts

- Consumes: similarity graph + clusters from **05-data-layer**; initial
  taste vector from **02-onboarding**; reactions from **04-core-loop**.
- Produces: node state transitions per **00-foundations**; unlock/bloom
  moments rendered by **01-design-system**.
