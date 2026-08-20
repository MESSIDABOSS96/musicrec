# Cold-start: can public data bootstrap the taste graph?

**Date:** 2026-08-19
**Question:** the v0.3 direction needs `user → albums they love` to compute taste
overlap. Before we have users, can we bootstrap that from public data?
**Answer:** largely no. Nothing public is simultaneously album-level, explicitly
declared, and commercially licensed. Two workable-but-implicit paths survive.

> Status of this document: one research thread of four completed. The threads on
> scrapable sites (Bandcamp, AOTY, Musicboard), Reddit/forum ballots, and
> CF-feasibility were stopped early and are **unassessed, not ruled out**.

---

## Bottom line

The dataset matching our spec almost exactly — Yahoo's KDD Cup 2011 — is both
legally barred to commercial entities and physically gone (host is NXDOMAIN).
Everything else fails on album granularity, on licensing, or on being explicit.

The realistic bootstrap signal is **implicit playcounts thresholded into
"loves"**, not declared favorites. That is a real problem for this product,
because the pitch depends on scarcity and deliberateness — "one of someone's ten
favorite albums ever." Thresholded playcounts are closer to "albums people played
a lot," which is the ordinary signal we were trying to beat.

## Ranked options

| # | Dataset | Album? | Explicit? | Commercial? | Obtainable? | Verdict |
|---|---|---|---|---|---|---|
| 1 | Music4All-Onion + A+A | yes, via MBID bridge | no | CC-BY / CC-BY-SA | open Zenodo | best realistic option |
| 2 | ListenBrainz + MB canonical | yes, 79% mapped | no | CC0 | dumps degraded | best license, act now |
| 3 | LB `recording_feedback` | unresolvable | yes, 5.2M loves | CC0 | 70% null MSIDs | blocked but desirable |
| 4 | Amazon CDs_and_Vinyl | native | yes, 1-5 stars | non-commercial | yes | right shape, wrong license |
| 5 | MARD | yes + MBIDs | yes, 1-5 stars | MIT (contested) | yes | too small |
| 6 | Yambda-5B | opaque IDs | yes, 89M likes | Apache 2.0 | yes | unmappable to real catalog |
| 7 | MLHD+ | release_MBID | no | **prohibited** | live | no grant exists |
| 8 | LFM-2b subsets | opaque IDs | no | risky CC-BY | fragments | album IDs unnameable |
| 9 | Last.fm-360K / 1K | **none** | no | non-commercial | live | no album data at all |
| 10 | MSD + Taste Profile | corrupted | no | dead licensor | HTTP only | unlicensable, ID mess |
| 11 | Yahoo KDD Cup 2011 | 50M album ratings | 0-100 scale | **barred** | **NXDOMAIN** | perfect fit, unobtainable |
| 12 | Spotify MPD | album_uri present | no | prohibited | retired | **no user IDs at all** |
| — | RateYourMusic / AOTY | aggregate only | — | — | — | no per-user data exists |

## The two viable paths

### Music4All-Onion + Music4All A+A

Two open Zenodo records that combine into `user → album` with no email gate.

- **Onion** — `zenodo.org/records/15394646`, CC-BY-4.0. 119,140 users,
  50,016,042 (user, track, count) rows. Ships **no metadata at all** — every ID
  is opaque. Useless alone.
- **A+A** — `zenodo.org/records/17400116`, CC-BY-SA-4.0, published 2025-09-27.
  19,511 albums keyed by **MusicBrainz MBID**, each carrying a
  `music4all_onion_id` list. Across all albums these map to 71,014 distinct Onion
  track IDs. **This bridge is the whole reason the pair works.**

Cautions: ShareAlike on A+A is viral for derivative databases. Onion is LFM-2b
lineage (119,140 users vs LFM-2b's 120,322 is not a coincidence) — the same
upstream-Last.fm-terms question applies. Album release dates span 1937-2023,
weighted to 2000s-2010s, essentially nothing post-2020.

### ListenBrainz + MusicBrainz canonical dumps

The cleanest license in the whole survey. MetaBrainz states plainly that the
commercial ask is *"on a moral basis rather than a legal one"* — CC0 is an
irrevocable waiver, so no agreement is legally required. Tiers: Stealth Start-Up
$0, Bronze $100/mo at public launch, Silver $600/mo.

Measured, not quoted: 2.66B listens spanning 2005-2026, 20.7M distinct
release-groups touched. On a real 24h slice — 9.2M listens, 21,861 active users,
**max `user_id` = 168,414**, so ~168k accounts ever created. 78.7% of listens
carry a `release_mbid`.

Three cautions:
- **Dumps are broken right now.** A MetaBrainz post dated 2026-08-19 says dump
  generation crashes their servers; the JSON listens dump, public DB dump, and
  statistics dump are all missing. They lost their founder in Feb 2026 and are
  down to three people. **Grab the 191GB spark dump while it exists.**
- **Use the spark dump's integer `user_id`, not the JSON dump** — the latter
  carries real usernames attached to full listening histories, a GDPR exposure
  separate from the copyright question.
- **Population skew.** MusicBrainz-adjacent, Picard-using listeners. Good for
  training item-item album similarity; thin as a proxy for a discovery audience.
  In the sample day, 5.9M of 9.2M listens came from user_ids 160,000+ — bulk
  Last.fm backfill by new signups, not organic listening.

## Corrections to premises we started with

- **LFM-2b was not withdrawn over GDPR.** Both LFM-1b and LFM-2b carry the
  identical notice, *"not available for download anymore due to license issues,"*
  and both went down in the same Feb-Jul 2024 window. Zero matches for
  `gdpr`/`privacy`/`withdraw` in the page HTML. This reads as a single **Last.fm
  licensing action**, which taints every Last.fm-derived academic set downstream.
  A CC-BY tag applied by university researchers does not bind Last.fm.
- **LFM-1b is gone too**, not just 2b.
- **The ~717M Yahoo figure is a different dataset.** That is Webscope R2 (717M
  ratings, 136k *songs*, 1.8M users) where album is metadata and never rated.
  The one we wanted is KDD Cup Track 1: 1,000,990 users / 262.8M ratings, of
  which **~50M are album ratings across ~89k albums**, ~50 per user. Albums are
  first-class rated entities there, better than we hoped. Organizers even define
  "loved" as score ≥ 80.
- **MLHD+ is explicitly non-commercial** despite living on MetaBrainz servers.
  Chain of title is Last.fm → DDMAL McGill scrape → MetaBrainz re-match;
  MetaBrainz cleaned the MBIDs but acquired no rights.
- **Spotify MPD is structurally impossible, not just unlicensed.** The playlist
  object has no user ID field at all — only `pid`. Playlists cannot be grouped by
  owner, so `user → albums` is unreconstructable regardless of terms.
- **Yambda's album mapping is internal only.** It ships
  `album_item_mapping.parquet` and 89.3M explicit likes under Apache 2.0, but all
  user and track IDs are anonymized integers with no names or external IDs. No
  join to any real catalog.

## Also checked and rejected

- **RateYourMusic / AOTY** — no per-user data published anywhere. Every RYM
  dataset on Kaggle is aggregate top-N (rank, average rating, count). RYM has no
  API, no researcher program, and Cloudflare that broke `rymscraper`.
- **Amazon CDs_and_Vinyl** — 1.8M users, 4.8M explicit album ratings, but
  academic non-commercial only, and only **2.7 ratings/user** on average. Far too
  thin to compute overlap from.
- **Discogs** — dumps are CC0 and commercial use is fine, but they contain only
  release/artist/label metadata. User collections are Restricted Data,
  non-commercial. **Excellent catalog source, zero taste-graph value.**
- **MusicBrainz per-user ratings and collections** — both in
  `@PRIVATE_TABLE_LIST`, GPG-encrypted, never published. Only 3,105 release-group
  collections exist anyway.
- **CritiqueBrainz** — 12,815 reviews total, ~1.01 per album, so essentially zero
  co-occurrence signal. Dumps a year stale. Commercially usable subset ~3.4k.
- **MSD Taste Profile** — still downloads (HTTP only, port 443 refused) but its
  license says "same as the Echo Nest API license" and `developer.echonest.com`
  is NXDOMAIN. **There is no party from whom a commercial license can be
  obtained.** Also ~5.7k confirmed wrong song↔track matches plus ~13k
  unverifiable; the canonical artifact is krautrock band Harmonia appearing as
  the #20 artist because a song ID actually resolves to Katy Perry's *Firework*.
- **Last.fm-360K / 1K** — live, but 360K is artist-level and 1K is track-level.
  **Neither has an album column.** Both non-commercial.
- **Bandcamp 1M sales** — buyers not identifiable across purchases.

## Constraint on the fallback plan

If the answer is "collect first-party data via Spotify OAuth at signup," note
that Spotify's 2024-11-27 API change cut off Related Artists, Recommendations,
Audio Features, Audio Analysis, and 30-second previews for apps registered on or
after that date. That narrows what a Spotify-backed onboarding can do for us.

## Community sources (verified 2026-08-19, follow-up round)

- **Reddit AOTY ballots (r/indieheads, r/hiphopheads)** — best near-term
  target. Annual poll threads where users comment ranked top-10-of-the-year
  ballots. Extraction is unblocked: **Arctic Shift**
  (arctic-shift.photon-reddit.com) is alive and its download tool pulls all
  posts/comments for a subreddit over a date range — no Reddit API, no
  scraping. Watchful1's per-subreddit dump torrents on Academic Torrents are
  the bulk alternative. Yield unmeasured (guess: 1.5k-8k lists); measure by
  downloading one poll thread and counting. Caveat: **year-scoped**, not
  all-time — supplies the recency axis that favorite lists lack, not a
  substitute for them.
- **Topster images (r/Topster and similar)** — wanted future source (user
  decision): literal top-25 grids, one extraction step away. Needs a
  vision-model parse plus cover-art→album resolution. Do after text ballots.
- **AOTY.org profiles** — 403s on plain fetch; anti-bot posture. Deferred.

Algorithm note attached to this data (user, 2026-08-19): top-25 lists are
lagging indicators — recent albums rarely canonized yet — so lists should
find the *neighbors* while candidates may also come from extrapolation
(neighbors' recent loves, artist adjacency, corpus co-occurrence,
year-scoped ballot data).

## Open question, and the next move

The question that actually decides this is untouched: **do 10-album favorite
lists produce non-obvious recommendations, or does everyone's top 10 collapse
into the same ~200 canonical albums?** If it collapses, neighbour-finding
degenerates into popularity ranking and the whole mechanism fails — no amount of
data acquisition fixes that.

That is answerable offline against a few thousand real lists and needs no further
web research. It should be settled before committing to any acquisition work.
