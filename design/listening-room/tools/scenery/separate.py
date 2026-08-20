"""
Separate the swaying foliage out of the plate, and rebuild the candle
flame as a drawn loop.

    room2.png  ->  room-plate.png            the room, ready to move
               ->  vine-window.png           the strand by the window posters
               ->  vine-wall.png             the cluster over Ella / Dilla
               ->  plant-left.png            the left foreground mass
               ->  plant-right.png           the right foreground plant
               ->  flame-loop.png            10 frames of candle flame

FOLIAGE. Each plant is masked by greenness — in this palette foliage is
the only thing whose green channel beats its red — cleaned up by
connected components, hole-filling and a small dilation that pulls the
warm-lit leaf rims in with their leaves. The cut carries the original
pixels; only its alpha is new. The teal poster type (ELLA, NINA, PASTEL
BLUES) is also green-beats-red, but it is bright where the dark teal
leaves are not, so a value ceiling on high-hue pixels splits them.

Sway rotates each element a fraction of a degree about its own anchor,
which moves silhouette edges by a few pixels. So the plate cannot keep
the foliage baked where an edge might pull away from it: a band inside
each silhouette (deeper than the largest sway displacement) is filled
from the surrounding background by onion-peel propagation and softened.
Deeper inside, the baked copy stays — it is never exposed. Strands
thinner than two bands disappear from the plate entirely, which is
right: the thinnest things swing the most. At rest the cuts cover their
own fills and the page is unchanged.

FLAME. Painted flame is view-baked light; warping its pixels reads as
melting. Instead the flame is REDRAWN: a teardrop with a white heart
and a warm skirt, colours sampled from the painted flame itself, laid
over a patch of background from which the painted flame has been
removed. Ten frames, bend and stretch driven by closed sinusoids so the
loop has no seam. Each frame is an opaque patch whose border pixels are
the plate's own, so the sprite drops into the scene with no seam either.

Run from tools/scenery/. Needs numpy and Pillow. Prints the slot
geometry (scene px) that styles.css must carry.
"""
import numpy as np
from PIL import Image

SRC = '../../assets/room2.png'
img = np.asarray(Image.open(SRC).convert('RGB')).astype(np.float32)
H, W = img.shape[:2]
SX, SY = W / 390.0, H / 844.0

# ---------------------------------------------------------------- elements
# box: loose image-space bounds of the element.
# pivot: the point (image px) the element sways about — where it attaches.
# band: how deep (image px) behind its edges the plate must be rebuilt;
#       chosen >= the element's largest sway displacement plus margin.
ELEMENTS = {
    'vine-window': dict(box=(395, 0, 565, 725), pivot=(470, -30), band=20),
    'vine-wall': dict(box=(598, 310, 832, 845), pivot=(700, 300), band=20),
    'plant-left': dict(box=(0, 388, 238, 1844), pivot=(75, 1830), band=22),
    'plant-right': dict(box=(588, 833, 853, 1844), pivot=(760, 1800), band=22),
}


# ------------------------------------------------------------------ helpers
def blur(a, k, n=2):
    """n passes of a k-wide box blur; good enough for masks and fills."""
    for _ in range(n):
        p = np.pad(a, ((k // 2, k // 2), (k // 2, k // 2)) + ((0, 0),) * (a.ndim - 2),
                   mode='edge')
        acc = np.zeros_like(a)
        for dy in range(k):
            for dx in range(k):
                acc += p[dy:dy + a.shape[0], dx:dx + a.shape[1]]
        a = acc / (k * k)
    return a


def dilate(m, k):
    o = m.copy()
    for _ in range(k):
        p = np.pad(o, 1, constant_values=False)
        o = (p[1:-1, 1:-1] | p[:-2, 1:-1] | p[2:, 1:-1] | p[1:-1, :-2] | p[1:-1, 2:])
    return o


def erode(m, k):
    return ~dilate(~m, k)


def label_components(mask):
    """4-connected labelling into one int array — no per-component copies."""
    lab = np.zeros(mask.shape, np.int32)
    cur = 0
    ys, xs = np.nonzero(mask)
    Hm, Wm = mask.shape
    for sy, sx in zip(ys, xs):
        if lab[sy, sx]:
            continue
        cur += 1
        stack = [(sy, sx)]
        lab[sy, sx] = cur
        while stack:
            y, x = stack.pop()
            for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                ny, nx = y + dy, x + dx
                if 0 <= ny < Hm and 0 <= nx < Wm and mask[ny, nx] and not lab[ny, nx]:
                    lab[ny, nx] = cur
                    stack.append((ny, nx))
    return lab, cur


# ---------------------------------------------------------------- greenness
r, g, b = img[..., 0], img[..., 1], img[..., 2]
score = (g - r) + 0.25 * (g - b)
v = img.max(2) / 255.0
mx, mn = img.max(2), img.min(2)
d = np.maximum(mx - mn, 1e-6)
hue = np.where(mx == g, 60 * (b - r) / d + 120,
               np.where(mx == b, 60 * (r - g) / d + 240, (60 * (g - b) / d) % 360))
teal_type = (hue > 158) & (v > 0.30)
score = np.where(teal_type, -20.0, score)
score = blur(score, 3)
green = score > 6.0


def clean_mask(box):
    x0, y0, x1, y1 = box
    m = np.zeros((H, W), bool)
    m[max(y0, 0):y1, max(x0, 0):x1] = green[max(y0, 0):y1, max(x0, 0):x1]
    # drop specks
    lab, n = label_components(m)
    sizes = np.bincount(lab.ravel(), minlength=n + 1)
    m = sizes[lab] >= 150
    m &= lab > 0
    # pull the warm-lit leaf rims in with their leaves, then close
    m = dilate(m, 3)
    m = erode(dilate(m, 2), 2)
    # fill enclosed holes (lit leaf faces read warm and fall out of the score)
    sub = ~m[y0:y1, max(x0, 0):x1]
    lab, n = label_components(sub)
    sizes = np.bincount(lab.ravel(), minlength=n + 1)
    border = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    fillable = np.ones(n + 1, bool)
    fillable[border] = False
    fillable[0] = False
    fillable &= sizes < 2600
    m[y0:y1, max(x0, 0):x1] |= fillable[lab]
    return m


print('masking foliage…')
masks = {name: clean_mask(e['box']) for name, e in ELEMENTS.items()}
for name, m in masks.items():
    print(f'  {name:12s} {m.sum():6d} px')

# ------------------------------------------------------- rebuild the plate
# Fill = every element's edge band: from its silhouette boundary to `band`
# px inside it. Nothing outside the silhouette is touched — out there the
# plate is already pure background, and the mask's 3px dilation has pulled
# the painted anti-aliased fringe inside. Sources are true background only,
# never the foliage being cut away or the baked interior that stays.
claimed = np.zeros((H, W), bool)
fill = np.zeros((H, W), bool)
for name, e in ELEMENTS.items():
    m = masks[name]
    claimed |= m
    fill |= m & ~erode(m, e['band'])

plate = img.copy()
work = img.copy()
kn = ~claimed
todo = fill.copy()
for _ in range(80):
    if not todo.any():
        break
    acc = np.zeros((H, W, 3), np.float32)
    cnt = np.zeros((H, W), np.float32)
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dy == 0 and dx == 0:
                continue
            sk = np.roll(np.roll(kn, dy, 0), dx, 1)
            sc = np.roll(np.roll(work, dy, 0), dx, 1)
            acc += sc * sk[:, :, None]
            cnt += sk
    front = todo & (cnt > 0)
    if not front.any():
        break
    work[front] = acc[front] / cnt[front][:, None]
    kn |= front
    todo &= ~front
if todo.any():                      # unreachable pockets: leave baked copy
    fill &= ~todo
soft = blur(work, 5, n=2)
plate[fill] = soft[fill]


# ------------------------------------------------------------ cut the layers
def cut(name):
    m = masks[name]
    # Full coverage everywhere inside the silhouette — the painted edge
    # anti-aliasing is IN the pixels and rides with the layer — and a short
    # feather outward, so the edge stays soft against whatever it moves
    # over. Feathering inward instead would blend half-covered leaf edges
    # against the reconstructed background at rest, which shows.
    a = np.clip(blur(dilate(m, 1).astype(np.float32), 3, n=2), 0, 1)
    a = np.maximum(a, m.astype(np.float32))
    lay = np.zeros((H, W, 4), np.float32)
    lay[:, :, :3] = img
    lay[:, :, 3] = a * 255.0
    # margin bleed, as everywhere else in this pipeline: colour from fully
    # transparent pixels still enters the browser's downscale filter
    clear = lay[:, :, 3] == 0
    near = dilate(~clear, 8)
    lay[clear & near, :3] = plate[clear & near]
    lay[clear & ~near, :3] = 0
    ys, xs = np.nonzero(lay[:, :, 3] > 0)
    x0, x1 = max(xs.min() - 6, 0), min(xs.max() + 7, W)
    y0, y1 = max(ys.min() - 6, 0), min(ys.max() + 7, H)
    Image.fromarray(np.round(lay[y0:y1, x0:x1]).astype(np.uint8)).save(
        f'../../assets/{name}.png', optimize=True)

    px, py = ELEMENTS[name]['pivot']
    print(f'  .art-slot--{name} {{')
    print(f'    --x: {x0 / SX:.2f}px; --y: {y0 / SY:.2f}px; '
          f'--w: {(x1 - x0) / SX:.2f}px; --h: {(y1 - y0) / SY:.2f}px;')
    print(f'    --origin: {100 * (px - x0) / (x1 - x0):.1f}% '
          f'{100 * (py - y0) / (y1 - y0):.1f}%;')
    print('  }')
    return a


# ------------------------------------------------------------------- flame
# The painted flame, measured: core about x=246, wick at y=1249, tip near
# y=1210. Small opaque patch, plate pixels at its border: no seam, no
# plate edit, no alpha care.
FX0, FY0, FX1, FY1 = 232, 1204, 262, 1254
BASE = (246.0, 1249.0)
N_FRAMES = 10


def build_flame():
    patch = img[FY0:FY1, FX0:FX1].copy()
    ph, pw = patch.shape[:2]
    yy, xx = np.mgrid[0:ph, 0:pw].astype(np.float32)
    ax, ay = BASE[0] - FX0, BASE[1] - FY0

    # remove the painted flame: each row filled straight across from its
    # own left and right neighbours — dark jar above the wax, bright wax
    # below, which is exactly what sits behind a flame
    halfw = np.clip(9.0 * np.sin(np.clip((ay - np.arange(ph)) / (ay - 2), 0, 1)
                                 * np.pi * 0.62 + 0.30), 3.0, 9.5)
    bg = patch.copy()
    for row in range(ph):
        l_ = max(int(np.floor(ax - halfw[row])), 1)
        r_ = min(int(np.ceil(ax + halfw[row])), pw - 2)
        if r_ <= l_:
            continue
        t = (np.arange(l_, r_ + 1) - l_) / max(r_ - l_, 1)
        bg[row, l_:r_ + 1] = (patch[row, l_ - 1][None, :] * (1 - t[:, None])
                              + patch[row, r_ + 1][None, :] * t[:, None])
    bg = blur(bg, 3, n=1)
    # colours from the painting itself
    core = img[1232, 246].copy()          # near-white heart
    mid = img[1224, 243].copy()           # yellow body
    rim = img[1236, 251].copy()           # orange skirt

    # the wick survives every frame: a dark stub under the flame base
    wick = (np.clip(1.2 - np.abs(xx - ax), 0, 1)
            * np.clip(1 - np.abs(yy - (ay - 2.0)) / 4.0, 0, 1))
    wick_c = np.array((38, 24, 16), np.float32)

    # the glow the painted flame threw on its surroundings — the row fill
    # removed it along with the flame — put back statically
    gg = 0.40 * np.exp(-(((xx - ax) / 11.0) ** 2 + ((yy - (ay - 9)) / 10.0) ** 2))

    frames = []
    for k in range(N_FRAMES):
        p = 2 * np.pi * k / N_FRAMES
        bend = 2.0 * np.sin(p) + 0.9 * np.sin(2 * p + 1.1)
        stretch = 1.0 + 0.08 * np.sin(p + 2.2) + 0.04 * np.sin(3 * p + 0.4)
        glow = 1.0 + 0.05 * np.sin(2 * p + 0.5)

        h = 31.0 * stretch
        u = np.clip((ay - 3 - yy) / h, 0, 1)           # 0 at wick, 1 at tip
        cx = ax + bend * u ** 2 * 2.4
        width = 12.5 * u ** 0.45 * (1 - u) ** 1.1 + 0.3
        q = np.abs(xx - cx) / np.maximum(width, 1e-3)
        inside = (u < 1.0) & (u > 0.003) & (yy < ay - 1)

        body = (np.clip(1.0 - q, 0, 1) * inside) ** 0.6
        coreness = (np.clip(1.15 - q * 1.6, 0, 1) ** 1.2
                    * np.clip(1 - np.abs(u - 0.35) * 1.7, 0, 1))
        col = (rim[None, None, :] * (1 - body[:, :, None])
               + mid[None, None, :] * body[:, :, None])
        col = col * (1 - coreness[:, :, None]) + core[None, None, :] * coreness[:, :, None]
        alpha = np.clip(body * 2.2, 0, 1)[:, :, None]

        halo = np.clip(1.0 - q / 3.0, 0, 1) ** 1.5 * inside * 0.45
        out = bg * (1 - gg[:, :, None]) + rim[None, None, :] * gg[:, :, None] * 1.05
        out = out * (1 - halo[:, :, None]) + rim[None, None, :] * halo[:, :, None]
        out = out * (1 - wick[:, :, None] * 0.9) + wick_c[None, None, :] * wick[:, :, None] * 0.9
        out = out * (1 - alpha) + col * alpha * glow
        frames.append(np.clip(out, 0, 255))

    sheet = np.concatenate(frames, axis=1)
    Image.fromarray(np.round(sheet).astype(np.uint8)).save(
        '../../assets/flame-loop.png', optimize=True)
    print('  .art-slot--candle-flame {')
    print(f'    --x: {FX0 / SX:.2f}px; --y: {FY0 / SY:.2f}px; '
          f'--w: {(FX1 - FX0) / SX:.2f}px; --h: {(FY1 - FY0) / SY:.2f}px;')
    print(f'  }}  /* sheet: {N_FRAMES} frames, frame step {(FX1 - FX0) / SX:.2f}px */')


if __name__ == '__main__':
    print('slot geometry for styles.css:')
    alphas = {name: cut(name) for name in ELEMENTS}
    build_flame()
    Image.fromarray(np.round(plate).astype(np.uint8)).save(
        '../../assets/room-plate.png', optimize=True)

    # rest check: plate + cuts must reproduce room2 (flame patch aside —
    # the flame is a redraw, not a reproduction)
    comp = plate.copy()
    for name in ELEMENTS:
        a = alphas[name][:, :, None]
        comp = comp * (1 - a) + img * a
    err = np.abs(np.round(comp) - img).max(2)
    outside_flame = np.ones((H, W), bool)
    outside_flame[FY0:FY1, FX0:FX1] = False
    print(f'rest composite vs room2 (flame patch aside): '
          f'max {err[outside_flame].max():.0f}, mean {err[outside_flame].mean():.4f}, '
          f'>2 on {int((err[outside_flame] > 2).sum())} px')
