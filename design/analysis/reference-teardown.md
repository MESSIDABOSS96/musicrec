# Reference teardown

Reverse-engineering of the two lofi sunset references, from measured pixel
data rather than impression. Source images:
`design/inspiration/lofi-window-city-sunset.png` (**Image A** — window onto a
city street) and `design/inspiration/lofi-beach-sunset-street.png`
(**Image B** — café doorway onto a beach).

All luminance (`L`) values are perceptual (0.2126R + 0.7152G + 0.0722B),
normalized 0–1. Positions are fractions of the frame.

---

## Part 1 — The visual system of the reference images

### 1. The armature is an aperture punched through a dark near-plane

Neither image is "a sunset." Both are **a bright opening surrounded by a dark
interior** — a window frame and table in A, a door jamb and café table in B.

| | Image A | Image B |
|---|---|---|
| pixels below L 0.15 | **53.2%** | ~34% |
| pixels above L 0.55 | **10.2%** | ~12% |
| border 12% vs center mean L | 0.19 border / 0.33 center | 1.76× brighter center |

More than half of Image A is essentially dark. The sky it frames is only
L 0.58 — nowhere near white — but it *reads* as blinding because the eye
judges brightness relatively. **The dark surround is not decoration; it is a
value clamp that buys luminosity without needing bright pixels.**

Practical consequence: you get a glowing interface by making most of it dark,
not by making the bright part brighter.

### 2. Depth is encoded as luminance, monotonically, with the light at infinity

Measured median L per depth plane, near → far:

**Image A:** frame/lintel `0.053` → table `0.053` → street floor `0.169` →
left buildings `0.202` → sky `0.581` → sun `0.91`

**Image B:** door jambs `0.085` → table + cups `0.159` → buses `0.166` →
street/people `0.231` → sea `0.344` → sky at horizon `0.431` → sun `0.93`

Monotonic in both. The nearest plane is the darkest; the light source sits at
the farthest. Critically, **each plane occupies a narrow, largely
non-overlapping value band** (interquartile ranges of 0.05–0.22). Planes do
not blend into each other — they stack as discrete value shelves.

This is why the images read as crisply layered despite having almost no
outlines.

### 3. There are no outlines. Shapes separate by value mass.

Test: of the dark pixels (L < 0.10), what share sit within 4px of something
brighter than L 0.30? A real ink-outline style scores >35%.

- **Image A: 5.3%**
- **Image B: 12.3%**

Both far below the threshold. Linework exists as *interior texture* — wood
grain, bus panelling, window mullions — but never as a contour drawn around
shapes. Objects are legible because their value band differs from their
neighbour's, not because a line separates them.

Implication: borders on everything is the wrong instinct. Separation comes
from putting adjacent surfaces in different value bands.

### 4. Hue is nearly monolithic; value does all the work

Distribution of saturated pixels (sat > 0.35) across 30° hue bins:

- **Image A: 76% inside a single 60° wedge** (0–60°, centred ≈25°, orange)
- **Image B: 87% inside a single 60° wedge** (330–30°, centred ≈0°, red)

Everything outside that wedge is a small, deliberately **desaturated** cool
minority — A has ~11% at 150–210° (teal-grey buildings, sat 0.34); B has ~4%
at 210–240° (blue-grey buses, sat 0.23).

The rule: **one narrow warm wedge carries ~80% of the image; a small cool
wedge carries ~10–15%, and the cool is always less saturated than the warm.**
A's warm average sat is 0.52–0.75 against the cool's 0.34–0.45.

### 5. Hue rotates with value — the temperature ramp

This is what separates these from a flat orange gradient. Mean hue per
luminance decile:

**Image A** — D3–D7 (shadows through midtones) sit at hue 24–33°; D8 dips to
19.8° (redder at the strong midtone); D9 climbs to 32° (yellower at the
highlight).

**Image B** — D0–D4 (darks) at hue **342–360°** (crimson/maroon); D5–D7 at
350–0°; D8–D9 at **11–18°** (orange).

So: **darks rotate toward red/magenta; lights rotate toward yellow.** A
shadow is never a darker, greyer version of the midtone — it is a
*hue-shifted* version.

And the shadows stay saturated. Image A's dark mass (L 0.08–0.18) averages
`#311D14` at **sat 0.57**; Image B's darkest decile is `#18080C` at
**sat 0.65**. There are no greys, no neutral shadows, and no black anywhere in
either image.

### 6. Light sources: flat core, colored bloom, radius proportional to importance

Every measured emissive core, across both images:

`#FDF7B6` `#FDF0AA` `#FCE668` `#FBD568` `#FED24E` `#FAD246` `#F6F63A`
`#FAB45C` `#F4B557` `#E6A72D`

All pale warm yellow, L 0.71–0.95 — **never white.**

Radial falloff, measured as mean L on rings out from each core:

| Source | r=0.008 | 0.02 | 0.04 | 0.07 | 0.11 | 0.16 |
|---|---|---|---|---|---|---|
| Sun (A) | 0.91 | 0.90 | 0.62 | 0.41 | 0.32 | 0.28 |
| Hanging bulb (A) | 0.55 | 0.52 | 0.50 | 0.43 | 0.37 | 0.30 |
| String bulb (B) | 0.63 | 0.51 | 0.26 | 0.19 | 0.18 | — |
| Cup highlight (B) | 0.43 | 0.32 | 0.22 | 0.21 | 0.18 | — |

Three findings:

1. **The sun's core is flat.** L 0.91 at r0.008 *and* at r0.02 — no internal
   gradient at all — then a hard edge falling to 0.62 by r0.04. It is a disc
   of solid color with bloom outside it, not a radial-gradient blob.
2. **Bloom radius scales with narrative importance**, roughly **8 : 2 : 1** —
   the sun glows out to ~16% of the frame, hanging bulbs to ~4%, small object
   highlights to ~2%. Small distant lights are nearly hard points.
3. **The bloom ramps hue as it falls**, following the same rule as §5. The
   sun's halo runs `#FDF0AA` → `#FBBF78` → `#FDA55F` → `#F98D48` → `#E45C2F`
   → `#C15037` → `#873B34`: yellow → orange → red → maroon.

### 7. Composition: the vanishing point, the light source, and the focal point are the same pixel

Sun position, measured: **Image A x=0.57, y=0.38. Image B x=0.57, y=0.40.**

Near-identical placement across two different scenes — right of centre, at
about 40% height. In both, the perspective lines (street edges, power lines,
the sea horizon, the sunpath on the water) converge on that point. One
location does three jobs at once.

### 8. Vertical rhythm: alternating bands

Image A's row-luminance profile is a five-band alternation:

```
y 0.00–0.10  dark lintel      L ≈ 0.05–0.10   ██
y 0.12–0.40  bright aperture  L ≈ 0.33–0.40   ████████████
y 0.44–0.72  dark trough      L ≈ 0.13–0.17   ████
y 0.76–0.84  warm lift (lit table) L ≈ 0.20   █████
y 0.88–1.00  near-black       L ≈ 0.03–0.05   █
```

Dark → light → dark → light → dark. The eye is pushed through the frame
rather than allowed to settle. Image B is simpler: a bright upper half and a
dark foreground shelf, with a horizontal vignette (column L peaks at x≈0.55
and falls to ~0.10 at both edges — true in A as well).

### 9. Detail density is inverted from importance

The measured edge-density maps put detail in the **foreground** (wood grain,
bottles, cups) and the **midground clutter** (signage, wires, bus panels).
The sky and the sun — the actual focal point — are the **flattest, least
detailed regions in the frame**.

The eye lands on the sun not because it is elaborate but because it is bright
and *quiet* amid busyness. Detail is used to make surroundings recede, and
emptiness marks the subject.

### 10. Grain

High-frequency residual measured in the flattest 20% of each image: **0.0051
(A)** and **0.0045 (B)**, both above the ~0.004 threshold for visible
grain. Present but subtle. It is what stops the large flat colour fields from
reading as vector art.

---

### The system in one paragraph

A large dark near-plane frames a small bright aperture; depth is encoded as a
monotonic luminance ramp with the light source at the far end; each depth
plane sits in its own narrow, non-overlapping value band, and shapes are
separated by those bands rather than by outlines; ~80% of the colour lives in
a single 60° warm hue wedge, with a small, always-less-saturated cool wedge
for the unlit architecture; hue rotates with value — toward red in the darks,
toward yellow in the lights — so nothing is ever grey or neutral; light
sources are flat pale-yellow cores (never white) with hue-ramping bloom whose
radius is proportional to their importance; the vanishing point, the light
source, and the focal point are the same location; detail clusters away from
the subject, leaving the focal point the flattest area in the frame; and a
faint grain sits over everything.

### 11. The extracted ramps

Averaging the dominant hue wedge within each value shelf yields the actual
working ramps. These are measurements, not picks.

**Image A — warm ramp** (58% of frame). Note the hue column: it holds at
15–20° through the whole shadow-to-midtone body, then rotates hard toward
yellow in the top three shelves. Saturation stays high *everywhere* — it never
drops below 0.59.

| L band | hex | hue | sat | area |
|---|---|---|---|---|
| 0.00–0.05 | `#0D0804` | 34° | 0.65 | 6.5% |
| 0.05–0.09 | `#1B100A` | 25° | 0.59 | 10.3% |
| 0.09–0.14 | `#32190E` | 20° | 0.67 | 8.1% |
| 0.14–0.20 | `#452416` | 20° | 0.64 | 7.9% |
| 0.20–0.28 | `#6C321D` | 17° | 0.67 | 6.1% |
| 0.28–0.38 | `#904425` | 18° | 0.69 | 4.6% |
| 0.38–0.50 | `#D4592D` | 16° | 0.76 | 3.2% |
| 0.50–0.62 | `#DE8536` | 30° | 0.75 | 10.7% |
| 0.62–0.78 | `#E6A842` | 38° | 0.71 | 0.2% |
| 0.78–1.01 | `#F6EE3A` | 59° | 0.76 | 0.6% |

**Image A — cool counterpoint** (19%), hue 150–177° (teal):
`#050A0A` → `#182321` → `#283935` → `#354942` → `#556868`, with saturation
**falling** 0.55 → 0.31 → 0.29 → 0.28 → 0.19 as it lightens.

**Image B — warm ramp** (78%), anchored redder:

| L band | hex | hue | sat |
|---|---|---|---|
| 0.00–0.05 | `#1B0506` | 338° | 0.81 |
| 0.05–0.09 | `#250E11` | 346° | 0.62 |
| 0.09–0.14 | `#371615` | 19° | 0.61 |
| 0.14–0.20 | `#4D231C` | 21° | 0.63 |
| 0.20–0.28 | `#7B2E25` | 12° | 0.69 |
| 0.28–0.38 | `#A1423F` | 334° | 0.61 |
| 0.38–0.50 | `#D15840` | 12° | 0.67 |
| 0.50–0.62 | `#E4734D` | 15° | 0.65 |
| 0.62–0.78 | `#F19F62` | 26° | 0.59 |
| 0.78–1.01 | `#F4CBA4` | 30° | 0.32 |

**Image B — cool counterpoint** (12%), hue 214–231° (blue):
`#0D0F19` → `#1E222D` → `#2A3240` → `#454F5F` → `#555F6E`, saturation again
**falling** 0.51 → 0.23 as it lightens.

The asymmetry between the two ramps is the most useful single finding here:

> **The warm ramp holds its saturation as it brightens; the cool ramp bleeds
> saturation as it brightens.**

That is the difference between *coloured light* and *unlit material catching
ambient*. It is why the warm feels like a source and the cool feels like a
surface, and it is a rule you can encode directly in tokens.

### Where my first landing-page attempt went wrong

Measured against the above, the failures were structural, not stylistic:

1. **No aperture.** I made the sunset the whole canvas. The references make
   it a minority of the frame seen through a dark surround — which is the
   entire source of their luminosity.
2. **No near-plane.** There was nothing between the viewer and the sky, so
   there was no depth ramp, only a gradient.
3. **Continuous gradients instead of value shelves.** I blended sky into sea
   into land; the references keep planes in discrete, separated value bands.
4. **A soft radial-gradient sun** rather than a flat disc with bloom outside
   it.
5. **Uniform glow on every light** instead of importance-scaled bloom.
6. **No cool counterpoint** — everything was warm, so nothing read as unlit
   material, and the warmth had nothing to be warm *against*.
7. **Detail in the wrong place** — nothing textured in the foreground, so no
   sense of a place the viewer occupies.

---

## Part 2 — bruno-simon.com: what makes an exploratory space work

Studied for how it makes a page feel alive and inhabited. The most valuable
findings were not about rendering — they were about **how an exploratory
space teaches itself and where it fails**, which is exactly musicrec's
problem, since our map is also a space the user must learn to move through
without a tutorial.

### 1. It borrows a mental model instead of teaching one

The reason driving a car around a portfolio works is not that it is clever.
It is that **nearly everyone has already played a game where you steer a
car**, so the controls arrive pre-learned. The interface only has to
*activate* existing knowledge, never install new knowledge.

This is the single most transferable principle here, and it costs nothing in
2D. An interface feels intuitive when it maps onto a physical metaphor the
user already owns — weight, momentum, stacks, drawers, distance, proximity —
rather than a novel abstraction that must be explained.

**For musicrec:** the map should behave like a physical place with
distance and inertia, not like a diagram. "Things far away are unfamiliar,
things near you are yours" is a model every person already has.

### 2. The author himself concluded he needed *more* interface

The most credible criticism of the original build came from Bruno. After beta
testing a later version, users could not tell where to go; he had known the
answer and resisted it, then added a map, a menu, and a visible "unstuck"
button. He attributed the original omission to his own gamer habits.

This is the exact failure mode waiting for a free-exploration taste map: a
beautiful space with no indication of where to go next. The lesson from the
most famous exploratory site on the web is that **ambient beauty does not
substitute for affordances**, and its author shipped more chrome, not less,
once he watched real users.

**For musicrec:** the frontier must visibly *call*. "Curiosity / pull" is one
of the two feelings we committed to, and it needs a designed affordance —
not just dimmer orbs at the edge and hope.

### 3. Instructions are a smell

A repeated critique, and hard to argue with: needing a controls modal to
explain your interface means the interface is not carrying its own weight.

**For musicrec:** the map should teach exploration through its own behaviour
— what glows, what drifts, what responds to a hover — not through a
first-run tooltip tour.

### 4. The escape hatch that was built and never linked

Verified directly: a complete plain-HTML CV exists at
`bruno-simon.com/html/` and returns 200. **Zero pages link to it.** No
`robots.txt`, no `sitemap.xml`, no `h1` structure, no ARIA, no `alt` text.
The fallback links forward into the 3D site; the 3D site never links back.

The most common complaint about the site — "just show me the content" — was
already solved, and the fix was one anchor tag that never shipped.

**For musicrec:** whatever the low-effort path is (someone who wants
recommendations without exploring the map), it has to be *reachable from the
main surface*, not merely to exist.

### 5. Where the analogy stops

Two honest limits worth recording before we borrow anything:

- The backlash around this style is aimed at **imitators**, not at Bruno.
  His site works partly because he sells the Three.js course it demonstrates
  — the experience *is* the product demo. musicrec has no such alibi, so
  spectacle has to earn its place functionally.
- Accessibility was the jury's lowest score both times it was awarded, and it
  got *worse* over six years. Ambient motion, glow, and a spatial-only
  navigation model all carry real accessibility cost. `prefers-reduced-motion`
  and a non-spatial route to the same content are not optional for us.

### 6. What to actually take

| Take | Leave |
|---|---|
| Borrowed physical mental model (weight, momentum, distance) | Literal 3D / a game engine |
| Damping and inertia so the space feels physical | Controls that must be explained |
| Ambient motion that signals a living, persistent world | Motion with no reduced-motion fallback |
| Visible affordances pointing at where to go next | Free exploration with no guidance |
| A reachable low-effort path through the same content | An orphaned fallback nobody can find |
