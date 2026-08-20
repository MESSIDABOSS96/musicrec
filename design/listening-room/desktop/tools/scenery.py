"""
Separate the desktop plate's swaying foliage, and draw its two flames.

    roomd.png  ->  roomd-plate.png          the room, ready to move
               ->  vine-left.png            hanging over the Duke poster
               ->  shelf-fern.png           the drape at the shelf's end
               ->  vine-center.png          the strand by Coltrane / Stevie
               ->  vine-right.png           the cluster around the cage lamp
               ->  plant-left.png           the big left foreground mass
               ->  plant-mid.png            the pot between chair and cabinet
               ->  plant-right.png          the right foreground plant
               ->  plant-cab.png            the little pot on the cabinet
               ->  flame-main.png           the jar candle by the turntable
               ->  flame-shelf.png          the jar candle on the shelf

Same method as the mobile tools/scenery/separate.py — greenness masks
with component cleanup and hole filling, a plate rebuilt behind every
silhouette edge to sway depth, cuts that carry the original pixels, and
flames REDRAWN as seamless sinusoid-driven loops rather than warped.
Desktop additions: per-element EXCLUDE boxes (the A Tribe Called Quest
poster's green artwork sits beside the centre vine's tail and must not
be cut), and two flames instead of one.

Scene px == image px on desktop (the page is authored at 1536x1024).

Run from desktop/tools/. Needs numpy and Pillow. Prints slot geometry
for styles.css.
"""
import numpy as np
from PIL import Image

SRC = '../assets/roomd.png'
img = np.asarray(Image.open(SRC).convert('RGB')).astype(np.float32)
H, W = img.shape[:2]

VINE_LEFT = (140, 35, 300, 265)
SHELF_FERN = (238, 240, 362, 400)
VINE_FAR_RIGHT = (1395, 60, 1536, 430)
PLANT_CAB = (1290, 498, 1360, 568)
CANDLE_SHELF = (225, 338, 266, 392)    # the shelf candle: no foliage cut here

ELEMENTS = {
    'vine-left': dict(box=VINE_LEFT, pivot=(220, 25), band=14, exclude=[]),
    'shelf-fern': dict(box=SHELF_FERN, pivot=(300, 385), band=10,
                       exclude=[CANDLE_SHELF]),
    # premerge: the strand's lower tail is sparse clusters of a few px each
    # that the size floor would drop one by one — merge neighbours before
    # filtering, because a static tail under a swaying mass tears
    'vine-center': dict(box=(455, 15, 600, 590), pivot=(527, 0), band=16,
                        exclude=[(400, 440, 506, 590)],    # ACQ poster art
                        premerge=True, minsize=80),
    'vine-right': dict(box=(1018, 88, 1272, 605), pivot=(1140, 58), band=16,
                       exclude=[(1085, 535, 1272, 605)]),  # turntable lid
    'vine-far-right': dict(box=VINE_FAR_RIGHT, pivot=(1470, 40), band=14,
                           exclude=[]),
    'plant-left': dict(box=(0, 215, 347, 1024), pivot=(150, 1002), band=24,
                       exclude=[VINE_LEFT, SHELF_FERN, CANDLE_SHELF]),
    'plant-mid': dict(box=(468, 618, 648, 938), pivot=(552, 928), band=14,
                      exclude=[]),
    'plant-right': dict(box=(1278, 298, 1536, 1024), pivot=(1428, 1002), band=24,
                        exclude=[VINE_FAR_RIGHT, PLANT_CAB,
                                 (1270, 870, 1400, 1024)]),   # speaker cone
    'plant-cab': dict(box=PLANT_CAB, pivot=(1322, 560), band=8, exclude=[]),
}


# ------------------------------------------------------------------ helpers
def blur(a, k, n=2):
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
# The desktop palette is far darker and warmer than the mobile plate:
# leaves sit at RGB values like (15,17,9) and lamp-lit leaf faces go
# fully warm (score negative). So the mask is a union: green-beats-red
# where that works, plus a yellow-green hue window for the rest, gated
# by a relaxed score so warm wood (hue < 44) stays out. Lit leaf faces
# that still escape are enclosed by leaf clusters and come back through
# hole filling.
r, g, b = img[..., 0], img[..., 1], img[..., 2]
score = (g - r) + 0.25 * (g - b)
v = img.max(2) / 255.0
mx, mn = img.max(2), img.min(2)
d = np.maximum(mx - mn, 1e-6)
hue = np.where(mx == g, 60 * (b - r) / d + 120,
               np.where(mx == b, 60 * (r - g) / d + 240, (60 * (g - b) / d) % 360))
teal_type = (hue > 158) & (v > 0.30)
score = np.where(teal_type, -20.0, score)
sscore = blur(score, 3)
green = (sscore > 1.2) | ((hue > 44) & (hue < 175) & (mx > 6) & (sscore > -4.0))


def clean_mask(e):
    x0, y0, x1, y1 = e['box']
    m = np.zeros((H, W), bool)
    m[max(y0, 0):y1, max(x0, 0):x1] = green[max(y0, 0):y1, max(x0, 0):x1]
    for ex0, ey0, ex1, ey1 in e['exclude']:
        m[ey0:ey1, ex0:ex1] = False
    if e.get('premerge'):
        m = dilate(m, 2)
    lab, n = label_components(m)
    sizes = np.bincount(lab.ravel(), minlength=n + 1)
    m = (sizes[lab] >= e.get('minsize', 120)) & (lab > 0)
    m = dilate(m, 3)
    m = erode(dilate(m, 2), 2)
    sub = ~m[y0:y1, max(x0, 0):x1]
    lab, n = label_components(sub)
    sizes = np.bincount(lab.ravel(), minlength=n + 1)
    border = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    fillable = np.ones(n + 1, bool)
    fillable[border] = False
    fillable[0] = False
    fillable &= sizes < 2600
    m[y0:y1, max(x0, 0):x1] |= fillable[lab]
    for ex0, ey0, ex1, ey1 in e['exclude']:
        m[ey0:ey1, ex0:ex1] = False
    return m


print('masking foliage…')
masks = {name: clean_mask(e) for name, e in ELEMENTS.items()}
for name, m in masks.items():
    print(f'  {name:12s} {m.sum():6d} px')

# ------------------------------------------------------- rebuild the plate
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
if todo.any():
    fill &= ~todo
soft = blur(work, 5, n=2)
plate[fill] = soft[fill]


# ------------------------------------------------------------ cut the layers
def cut(name):
    m = masks[name]
    a = np.clip(blur(dilate(m, 1).astype(np.float32), 3, n=2), 0, 1)
    a = np.maximum(a, m.astype(np.float32))
    lay = np.zeros((H, W, 4), np.float32)
    lay[:, :, :3] = img
    lay[:, :, 3] = a * 255.0
    clear = lay[:, :, 3] == 0
    near = dilate(~clear, 8)
    lay[clear & near, :3] = plate[clear & near]
    lay[clear & ~near, :3] = 0
    ys, xs = np.nonzero(lay[:, :, 3] > 0)
    x0, x1 = max(xs.min() - 6, 0), min(xs.max() + 7, W)
    y0, y1 = max(ys.min() - 6, 0), min(ys.max() + 7, H)
    Image.fromarray(np.round(lay[y0:y1, x0:x1]).astype(np.uint8)).save(
        f'../assets/{name}.png', optimize=True)
    px, py = ELEMENTS[name]['pivot']
    print(f'  .art-slot--{name} {{')
    print(f'    --x: {x0}px; --y: {y0}px; --w: {x1 - x0}px; --h: {y1 - y0}px;')
    print(f'    --origin: {100 * (px - x0) / (x1 - x0):.1f}% '
          f'{100 * (py - y0) / (y1 - y0):.1f}%;')
    print('  }')
    return a


# ------------------------------------------------------------------- flames
FLAMES = {
    'flame-main': dict(box=(893, 664, 929, 702), base=(911.0, 697.5),
                       h=15.0, hw=4.4, frames=10,
                       core=(687, 910), mid=(684, 909), rim=(691, 913)),
    'flame-shelf': dict(box=(231, 354, 261, 386), base=(246.0, 380.5),
                        h=11.0, hw=3.2, frames=10,
                        core=(371, 245), mid=(369, 244), rim=(375, 248)),
}


def build_flame(name, f):
    fx0, fy0, fx1, fy1 = f['box']
    patch = img[fy0:fy1, fx0:fx1].copy()
    ph, pw = patch.shape[:2]
    yy, xx = np.mgrid[0:ph, 0:pw].astype(np.float32)
    ax, ay = f['base'][0] - fx0, f['base'][1] - fy0

    halfw = np.clip((f['hw'] + 2.0) * np.sin(
        np.clip((ay - np.arange(ph)) / max(ay - 2, 1), 0, 1) * np.pi * 0.62 + 0.30),
        2.0, f['hw'] + 2.5)
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
    core = img[f['core']].copy()
    mid = img[f['mid']].copy()
    rim = img[f['rim']].copy()

    wick = (np.clip(1.1 - np.abs(xx - ax), 0, 1)
            * np.clip(1 - np.abs(yy - (ay - 1.5)) / 3.0, 0, 1))
    wick_c = np.array((38, 24, 16), np.float32)
    gg = 0.40 * np.exp(-(((xx - ax) / (f['hw'] * 2.6)) ** 2
                         + ((yy - (ay - f['h'] * 0.45)) / (f['h'] * 0.75)) ** 2))

    frames = []
    n = f['frames']
    for k in range(n):
        p = 2 * np.pi * k / n
        bend = (0.9 * np.sin(p) + 0.4 * np.sin(2 * p + 1.1)) * f['hw'] / 4.4
        stretch = 1.0 + 0.08 * np.sin(p + 2.2) + 0.04 * np.sin(3 * p + 0.4)
        glow = 1.0 + 0.05 * np.sin(2 * p + 0.5)

        h = f['h'] * stretch
        u = np.clip((ay - 1.5 - yy) / h, 0, 1)
        cx = ax + bend * u ** 2 * 2.4
        width = f['hw'] * 2.05 * u ** 0.45 * (1 - u) ** 1.1 + 0.3
        q = np.abs(xx - cx) / np.maximum(width, 1e-3)
        inside = (u < 1.0) & (u > 0.003) & (yy < ay - 0.5)

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
        f'../assets/{name}.png', optimize=True)
    print(f'  .art-slot--{name} {{')
    print(f'    --x: {fx0}px; --y: {fy0}px; --w: {pw}px; --h: {ph}px;')
    print(f'  }}  /* sheet: {n} frames, frame step {pw}px, total {n * pw}px */')


if __name__ == '__main__':
    print('slot geometry for styles.css:')
    alphas = {name: cut(name) for name in ELEMENTS}
    for name, f in FLAMES.items():
        build_flame(name, f)
    Image.fromarray(np.round(plate).astype(np.uint8)).save(
        '../assets/roomd-plate.png', optimize=True)

    comp = plate.copy()
    for name in ELEMENTS:
        a = alphas[name][:, :, None]
        comp = comp * (1 - a) + img * a
    err = np.abs(np.round(comp) - img).max(2)
    outside = np.ones((H, W), bool)
    for f in FLAMES.values():
        fx0, fy0, fx1, fy1 = f['box']
        outside[fy0:fy1, fx0:fx1] = False
    print(f'rest composite vs roomd (flame patches aside): '
          f'max {err[outside].max():.0f}, mean {err[outside].mean():.4f}, '
          f'>2 on {int((err[outside] > 2).sum())} px')
